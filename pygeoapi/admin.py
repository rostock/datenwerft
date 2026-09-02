import json

from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Prefetch
from django.forms import (
  BaseInlineFormSet,
  BooleanField,
  CharField,
  HiddenInput,
  ModelChoiceField,
  ModelForm,
  ModelMultipleChoiceField,
  Select,
  SelectMultiple,
)
from django.utils.functional import cached_property
from django.utils.html import format_html_join
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from gdihrometadata.models import Service, ServiceType
from pygeoapi.constants_vars import max_columns
from pygeoapi.models import (
  AttributeReadPermission,
  Collection,
  CollectionAttribute,
  DatabaseConnection,
  Role,
)
from pygeoapi.services import reconcile_collection_inventory
from pygeoapi.utils import reload_pygeoapi


# a longer message no longer fits into the message cookie of 2048 bytes and falls
# back to the session, which costs one query more
MESSAGE_ATTRIBUTE_LIMIT = 10

# the two hidden fields that carry a reconcile through the POST
RECONCILE_FIELDS = ('reconcile', 'reconcile_columns')

# from the model, so that a value too long is rejected in the form instead of
# surfacing as a database error behind the reconcile
NAME_MAX_LENGTH = CollectionAttribute._meta.get_field('name').max_length
DATA_TYPE_MAX_LENGTH = CollectionAttribute._meta.get_field('data_type').max_length


def attributes_without_role_message(names):
  """
  names the attributes no role may read, at most MESSAGE_ATTRIBUTE_LIMIT of them;
  the total number is always given
  """
  shown = names[:MESSAGE_ATTRIBUTE_LIMIT]
  listing = ', '.join(shown)
  remaining = len(names) - len(shown)
  if remaining:
    listing += ngettext(
      ' … und %(count)d weiteres (siehe Spalte „Hinweis“)',
      ' … und %(count)d weitere (siehe Spalte „Hinweis“)',
      remaining,
    ) % {'count': remaining}
  # fixed prose in first place: admin/base.html renders '{{ message|capfirst }}'
  # and would capitalise an attribute name into one that does not exist
  headline = ngettext(
    'Ein Attribut dieser Kollektion kann von keiner Rolle gelesen werden: %(names)s.',
    '%(count)d Attribute dieser Kollektion können von keiner Rolle gelesen werden: %(names)s.',
    len(names),
  ) % {'count': len(names), 'names': listing}
  # a plain str and no mark_safe(): the template escapes the names, a SafeString
  # would survive cookie or session into the page
  return f'{headline} {gettext("Gespeichert wurde trotzdem alles.")}'


def reconcile_result_message(result):
  """
  names the four numbers of a reconcile, deliberately without the attribute names:
  those stand in the attribute overview, which the reconcile returns to
  """
  parts = [
    ngettext(
      '%(count)d Attribut neu aufgenommen',
      '%(count)d Attribute neu aufgenommen',
      len(result.added),
    )
    % {'count': len(result.added)},
    # the participles carry no number in German, hence no ngettext for the middle two
    gettext('%(count)d als „nicht mehr vorhanden“ gekennzeichnet')
    % {'count': len(result.vanished)},
    gettext('%(count)d wieder aufgetaucht') % {'count': len(result.reappeared)},
    ngettext(
      '%(count)d Datentyp aktualisiert',
      '%(count)d Datentypen aktualisiert',
      len(result.retyped),
    )
    % {'count': len(result.retyped)},
  ]
  return '{}.'.format(', '.join(parts))


class ServiceChoiceField(ModelChoiceField):
  def label_from_instance(self, obj):
    return f'({obj.name}) {obj.title}'


class CollectionForm(ModelForm):
  required_css_class = 'required'

  service = ServiceChoiceField(
    queryset=Service.objects.filter(type=ServiceType.API_FEATURES),
    widget=Select(attrs={'class': 'select2'}),
    label=_('Service-Metadatensatz aus GDI.HRO Metadata'),
  )

  schema_select = CharField(
    label=_('Auswahlmöglichkeit für Schema'),
    required=False,
    widget=Select(),
  )

  table_select = CharField(
    label=_('Auswahlmöglichkeit für Tabelle/View'),
    required=False,
    widget=Select(),
  )

  id_field_select = CharField(
    label=_('Auswahlmöglichkeit für ID-Attribut'),
    required=False,
    widget=Select(),
  )

  title_field_select = CharField(
    label=_('Auswahlmöglichkeit für Attribut mit (möglichst eindeutiger) Bezeichnung'),
    required=False,
    widget=Select(),
  )

  geom_field_select = CharField(
    label=_('Auswahlmöglichkeit für Geometrie-Attribut'),
    required=False,
    widget=Select(),
  )

  # filled in the browser by the button of the attribute overview; hidden and
  # outside every fieldset (see change_form.html)
  reconcile = BooleanField(
    label=_('Abgleich des Attributinventars anstoßen'),
    required=False,
    widget=HiddenInput(),
  )

  reconcile_columns = CharField(
    label=_('Spaltenliste für den Abgleich'),
    required=False,
    widget=HiddenInput(),
  )

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    used_ids = set(
      Collection.objects.exclude(service_id__isnull=True).values_list('service_id', flat=True)
    )

    qs = Service.objects.filter(type=ServiceType.API_FEATURES)

    # Ensure current instance value is not excluded (edit mode)
    if self.instance and self.instance.service_id:
      used_ids.discard(self.instance.service_id)

    # Apply filtering
    qs = qs.exclude(pk__in=used_ids)

    self.fields['service'].queryset = qs

    # Ensure preselection in edit mode (safe fallback)
    if self.instance and self.instance.service_id:
      self.fields['service'].initial = self.instance.service_id

  def clean_reconcile_columns(self):
    """
    the column list of a reconcile as validated dicts of name and data type

    The list comes from the browser and is therefore checked here in full; every
    rejection makes the whole form invalid. See docs/pygeoapi/rechtesystem.md for
    the data path and the risk deliberately accepted with it.
    """
    raw = self.cleaned_data['reconcile_columns']
    if not raw:
      return []
    try:
      columns = json.loads(raw)
    except json.JSONDecodeError as error:
      raise ValidationError(
        _('Die Spaltenliste des Abgleichs ist nicht lesbar (kein gültiges JSON).')
      ) from error
    if not isinstance(columns, list):
      raise ValidationError(_('Die Spaltenliste des Abgleichs muss eine Liste sein.'))
    # read per call and not at import, so that a deployment can raise the limit
    limit = max_columns()
    if len(columns) > limit:
      raise ValidationError(
        _(
          'Die Spaltenliste des Abgleichs umfasst %(count)d Einträge und damit mehr '
          'als die zugelassenen %(limit)d.'
        )
        % {'count': len(columns), 'limit': limit}
      )
    result, seen = [], set()
    for column in columns:
      if not isinstance(column, dict):
        raise ValidationError(
          _('Ein Eintrag der Spaltenliste des Abgleichs ist kein Objekt mit „name“ und „type“.')
        )
      name = column.get('name')
      if not isinstance(name, str) or not name:
        raise ValidationError(_('Ein Eintrag der Spaltenliste des Abgleichs hat keinen Namen.'))
      if len(name) > NAME_MAX_LENGTH:
        raise ValidationError(
          _('Der Attributname „%(name)s“ ist länger als die zugelassenen %(limit)d Zeichen.')
          % {'name': name, 'limit': NAME_MAX_LENGTH}
        )
      if name in seen:
        raise ValidationError(
          # rejected here and not left to the unique constraint of the model
          _('Der Attributname „%(name)s“ kommt in der Spaltenliste des Abgleichs mehrfach vor.')
          % {'name': name}
        )
      seen.add(name)
      data_type = column.get('type')
      if not isinstance(data_type, str) or len(data_type) > DATA_TYPE_MAX_LENGTH:
        # not shortened: a cut value would pretend a type the source does not state
        data_type = ''
      result.append({'name': name, 'type': data_type})
    return result

  def clean(self):
    cleaned_data = super().clean()
    # the admin renders errors of fields outside a fieldset nowhere; without this
    # move a rejected column list would name no reason
    for name in RECONCILE_FIELDS:
      for error in self.errors.pop(name, []):
        self.add_error(None, error)
    return cleaned_data

  def save(self, commit=True):
    instance = super().save(commit=False)
    service = self.cleaned_data.get('service')
    instance.service_id = service.pk if service else None
    if commit:
      instance.save()
    return instance


@admin.register(DatabaseConnection)
class DatabaseConnectionAdmin(admin.ModelAdmin):
  ordering = ('host', 'dbname', 'user')
  list_display = ('id', 'host', 'dbname', 'user')
  empty_value_display = ''


class RoleField(ModelMultipleChoiceField):
  """
  role picker of a single attribute row, resolved against a catalog that
  `CollectionAttributeFormSet` loads once per request
  """

  # the queryset stays empty on purpose: both the options and the validation of
  # the posted keys come from `roles_by_pk`, which the formset fills in. Going
  # through the queryset instead would cost one query per row when rendering and
  # another one per row when saving.
  def __init__(self, *args, **kwargs):
    super().__init__(*args, queryset=Role.objects.none(), **kwargs)
    self.roles_by_pk = {}

  def _check_values(self, value):
    # keys arrive as strings from a POST and as integers from `initial` of a
    # disabled row, hence the lookup by str()
    roles = []
    for key in frozenset(value):
      role = self.roles_by_pk.get(str(key))
      if role is None:
        raise ValidationError(
          self.error_messages['invalid_choice'],
          code='invalid_choice',
          params={'value': key},
        )
      roles.append(role)
    return roles


class CollectionAttributeInlineForm(ModelForm):
  """
  one row of the attribute overview; only the role assignment is editable
  """

  roles = RoleField(
    required=False,
    label=_('zugewiesene Rollen'),
    widget=SelectMultiple(
      attrs={
        'class': 'select2',
        # select2 reads its options from data attributes; without a placeholder
        # a row without any assignment looks like a broken field
        'data-placeholder': _('Rolle zuweisen …'),
        # select2 resolves its width from the inline style of the element;
        # without it the field stays as narrow as its longest role name
        'style': 'width: 100%',
      }
    ),
  )

  class Meta:
    model = CollectionAttribute
    # no model field of the inventory is edited here: the inventory mirrors the
    # source table and is written by the reconciliation
    fields = []

  def __init__(self, *args, role_choices=(), roles_by_pk=None, **kwargs):
    super().__init__(*args, **kwargs)
    field = self.fields['roles']
    field.roles_by_pk = roles_by_pk or {}
    # a finished list instead of a ModelChoiceIterator: str(role) is then
    # computed once per role and not once per role and row
    field.choices = role_choices
    # the empty form exists only to supply the column headers and carries no
    # attribute; its reverse relation is not usable without a primary key
    if self.instance.pk is None:
      return
    # reads the prefetch of the inline, on GET as well as on POST, and therefore
    # costs no query; role_id avoids touching the related object
    self.initial['roles'] = [
      permission.role_id for permission in self.instance.read_permissions.all()
    ]
    field.widget.attrs['data-attribute'] = self.instance.name
    collection = self.instance.collection
    if self.instance.name in (collection.id_field, collection.geom_field):
      # Django's disabled is the server-side safeguard, no check of our own is
      # needed: a disabled field is cleaned from its initial value and never
      # reports itself as changed, so a forged POST is structurally without
      # effect rather than rejected
      field.disabled = True


class CollectionAttributeFormSet(BaseInlineFormSet):
  """
  loads the role catalog once per request and writes the difference of the role
  assignments with a number of queries independent of the amount of data
  """

  @cached_property
  def roles(self):
    return list(Role.objects.all())

  @cached_property
  def role_choices(self):
    # str(role) is 'Label (identifier)': only identifier is unique, two roles may
    # share a label
    return [(role.pk, str(role)) for role in self.roles]

  @cached_property
  def roles_by_pk(self):
    return {str(role.pk): role for role in self.roles}

  def get_form_kwargs(self, index):
    kwargs = super().get_form_kwargs(index)
    kwargs['role_choices'] = self.role_choices
    kwargs['roles_by_pk'] = self.roles_by_pk
    return kwargs

  def save_existing(self, form, obj, commit=True):
    # the inline has no editable model field; form.save() would cost a
    # full_clean() and an identical UPDATE per changed row. The row is already
    # noted in changed_objects at this point, so the log entry loses nothing.
    return obj

  def save_permissions(self):
    """
    writes the difference between the assigned and the selected roles and records
    it for the object history
    """
    to_create, to_delete = [], []
    self.permission_changes = {}
    for form in self.initial_forms:
      if 'roles' not in form.changed_data:
        continue
      attribute = form.instance
      # both sides come from memory: the prefetch of the inline and the catalog
      assigned = {
        permission.role_id: permission for permission in attribute.read_permissions.all()
      }
      selected = {role.pk: role for role in form.cleaned_data['roles']}
      changes = self.permission_changes.setdefault(attribute.name, [])
      for role_id, role in selected.items():
        if role_id not in assigned:
          to_create.append(AttributeReadPermission(role=role, attribute=attribute))
          changes.append(_('Rolle „%(role)s“ zugewiesen') % {'role': role})
      for role_id, permission in assigned.items():
        if role_id not in selected:
          to_delete.append(permission.pk)
          changes.append(_('Rolle „%(role)s“ entzogen') % {'role': permission.role})
    if to_create:
      # bulk_create() skips save() and thus full_clean(), the limit documented in
      # docs/pygeoapi/rechtesystem.md. Its three checks are guaranteed here
      # beforehand: the role comes from the loaded catalog, the attribute from the
      # queryset of the formset, and only combinations that are not stored yet are
      # inserted. ignore_conflicts because the existence of the row IS the right:
      # a row inserted by a concurrent save is the desired end state, not an error.
      AttributeReadPermission.objects.bulk_create(to_create, ignore_conflicts=True)
    if to_delete:
      AttributeReadPermission.objects.filter(pk__in=to_delete).delete()

  def attributes_without_role(self):
    """
    the names of the attributes no role may read after this save, in the order of
    the overview
    """
    names = []
    for form in self.initial_forms:
      attribute = form.instance
      # a forged INITIAL_FORMS count produces initial forms without an attribute
      if attribute.pk is None:
        continue
      # a disappeared attribute delivers nothing anyway, and a structural one is
      # not subject to the assignment
      if not attribute.is_present:
        continue
      collection = attribute.collection
      if attribute.name in (collection.id_field, collection.geom_field):
        continue
      # the target state of this POST and not the prefetch, which save_permissions()
      # leaves untouched: whoever revokes the last role right here has to be named.
      # Truthiness only — the value holds Role objects, ints or an empty queryset.
      if not form.cleaned_data.get('roles'):
        names.append(attribute.name)
    return names


class CollectionAttributeInline(admin.TabularInline):
  """
  overview of a collection's attribute inventory; the roles allowed to read an
  attribute are assigned and revoked here
  """

  model = CollectionAttribute
  form = CollectionAttributeInlineForm
  formset = CollectionAttributeFormSet
  template = 'admin/pygeoapi/edit_inline/collection_attributes.html'
  fields = ['name', 'data_type', 'hint', 'roles']
  readonly_fields = ['name', 'data_type', 'hint']
  extra = 0
  can_delete = False
  # the admin site would otherwise put a dash into the roles column of an
  # attribute without any assignment, which reads like a role of that name
  empty_value_display = ''

  def has_add_permission(self, request, obj):
    # the inventory mirrors the source table; entries are not created by hand
    return False

  def has_delete_permission(self, request, obj=None):
    return False

  def get_queryset(self, request):
    # keeps the number of queries independent of the number of attributes and
    # of assigned roles; the ordering is a promised behaviour and therefore set
    # here explicitly instead of relying on Meta.ordering. It is unambiguous
    # because (collection, name) is unique.
    return (
      super()
      .get_queryset(request)
      .select_related('collection')
      .prefetch_related(
        Prefetch(
          'read_permissions',
          queryset=AttributeReadPermission.objects.select_related('role').order_by(
            'role__identifier'
          ),
        )
      )
      .order_by('name')
    )

  def roles(self, obj):
    # display fallback: a user without pygeoapi.change_collectionattribute gets
    # every field rendered read-only, the form field above is then not reached
    return format_html_join(
      ', ', '{}', ((permission.role.label,) for permission in obj.read_permissions.all())
    )

  roles.short_description = _('zugewiesene Rollen')

  def hint(self, obj):
    hints = []
    if not obj.is_present:
      hints.append(_('nicht mehr vorhanden'))
    # id_field and geom_field sit at root level of the GeoJSON response and are
    # therefore delivered regardless of any read permission (see
    # docs/pygeoapi/rechtesystem.md); title_field is an ordinary attribute
    if obj.name in (obj.collection.id_field, obj.collection.geom_field):
      hints.append(_('immer ausgeliefert'))
      # arises when id_field or geom_field is renamed afterwards and a right
      # granted regularly before thereby falls onto a structural row: the right
      # is without effect, but should not lie around unseen
      if obj.read_permissions.all():
        hints.append(_('wirkungsloses Recht'))
    # elif: a structurally delivered row must never carry this hint
    elif not obj.read_permissions.all():
      hints.append(_('von keiner Rolle lesbar'))
    return format_html_join(', ', '{}', ((hint,) for hint in hints))

  hint.short_description = _('Hinweis')


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
  form = CollectionForm
  inlines = [CollectionAttributeInline]
  list_display = ('id', 'service_display', 'database_connection', 'schema', 'table', 'deactivated')
  empty_value_display = ''
  fieldsets = [
    (
      'Sichtbarkeit und Verknüpfung',
      {
        'description': 'Konfiguration der Sichtbarkeit und der Verknüpfung mit GDI.HRO Metadata',
        'fields': ['deactivated', 'service'],
      },
    ),
    (
      'Datenbankquelle',
      {
        'description': 'Konfiguration der Datenbankquelle, aus der die Daten bezogen werden',
        'fields': [
          'database_connection',
          'schema_select',
          'schema',
          'table_select',
          'table',
          'id_field_select',
          'id_field',
          'title_field_select',
          'title_field',
          'geom_field_select',
          'geom_field',
          'storage_crs',
        ],
      },
    ),
  ]

  def get_inlines(self, request, obj=None):
    # an unsaved collection has no inventory, and no rights may be assigned to a
    # collection that does not exist yet
    return [] if obj is None else super().get_inlines(request, obj)

  def get_fieldsets(self, request, obj=None):
    fieldsets = super().get_fieldsets(request, obj)
    if obj is None:
      fieldsets = [
        *fieldsets,
        (
          'Attribute einer Kollektion',
          {
            'description': 'Attribute erst nach dem Speichern.',
            'fields': [],
          },
        ),
      ]
    return fieldsets

  def get_queryset(self, request):
    qs = super().get_queryset(request)

    # Collect all service_ids from the queryset
    service_ids = set(qs.exclude(service_id__isnull=True).values_list('service_id', flat=True))

    # Cache related services in one query (avoid N+1)
    self._service_cache = {s.id: s for s in Service.objects.filter(id__in=service_ids)}

    return qs

  def service_display(self, obj):
    service = getattr(self, '_service_cache', {}).get(obj.service_id)
    if not service:
      return '-' if not obj.service_id else f'Unknown ({obj.service_id})'
    return f'({service.name}) {service.title}'

  service_display.short_description = 'Service-Metadatensatz aus GDI.HRO Metadata'
  service_display.admin_order_field = 'service_id'

  def save_formset(self, request, form, formset, change):
    super().save_formset(request, form, formset, change)
    if isinstance(formset, CollectionAttributeFormSet):
      formset.save_permissions()

  def save_related(self, request, form, formsets, change):
    super().save_related(request, form, formsets, change)
    # after super() and before the reload, which happens once per save and after
    # every write of this POST
    if form.cleaned_data.get('reconcile'):
      self.reconcile_inventory(request, form)
    # a warning and not an error: nothing failed. Saving deliberately goes through —
    # a block would stop the very reconciliation that enters attributes without a role.
    for formset in formsets or []:
      if isinstance(formset, CollectionAttributeFormSet):
        names = formset.attributes_without_role()
        if names:
          self.message_user(request, attributes_without_role_message(names), messages.WARNING)
    # here and not in save_model(): that one runs first and would trigger the
    # reload before the permissions of the inline are written. save_related() is
    # reached exactly once per valid POST, for adding as well as for changing and
    # regardless of which save button was used.
    self.reload_after_commit()

  def reconcile_inventory(self, request, form):
    """
    reconciles the attribute inventory of the saved collection against the column
    list of this POST and reports the outcome
    """
    columns = form.cleaned_data.get('reconcile_columns')
    if not columns:
      # safeguard: the browser-side path names the cause and stops before
      # submitting, so this text is deliberately the terse one
      self.message_user(
        request,
        gettext('Der Abgleich kam ohne Spaltenliste an; das Attributinventar bleibt unverändert.'),
        messages.WARNING,
      )
      return
    result = reconcile_collection_inventory(form.instance, columns)
    # on the form and not on self: a ModelAdmin is a process-wide singleton, so a
    # value on self would leak into the next request
    form.reconcile_result = result
    if not result.has_changes:
      self.message_user(request, gettext('Der Abgleich hat keine Änderung ergeben.'))
      return
    self.message_user(request, reconcile_result_message(result))

  def delete_model(self, request, obj):
    super().delete_model(request, obj)
    self.reload_after_commit()

  def delete_queryset(self, request, queryset):
    super().delete_queryset(request, queryset)
    self.reload_after_commit()

  def reload_after_commit(self):
    # reload_pygeoapi() starts a thread; without on_commit() it would race the
    # still open transaction of the admin view and could read a state that is not
    # written yet. Note for tests: TestCase never commits, so a test counting the
    # reload needs self.captureOnCommitCallbacks(execute=True).
    transaction.on_commit(reload_pygeoapi)

  def construct_change_message(self, request, form, formsets, add):
    # without this the two carrier fields would stand in the object history as
    # changed fields of the collection on every reconcile
    form.changed_data = [name for name in form.changed_data if name not in RECONCILE_FIELDS]
    # Django's own message would only name the attribute, not the role, and would
    # therefore not carry what the object history has to show
    changes, remaining = {}, []
    for formset in formsets or []:
      permission_changes = getattr(formset, 'permission_changes', None)
      if permission_changes is None:
        remaining.append(formset)
      else:
        changes.update(permission_changes)
    message = super().construct_change_message(request, form, remaining, add)
    for attribute_name, entries in changes.items():
      if not entries:
        continue
      # a structured entry and not a plain text message: LogEntry returns a string
      # that does not start with '[' unchanged, which would drop the entries of
      # the parent form
      message.append(
        {
          'changed': {
            'name': str(_('Attribut')),
            'object': attribute_name,
            'fields': [str(entry) for entry in entries],
          }
        }
      )
    result = getattr(form, 'reconcile_result', None)
    if result and result.has_changes:
      # in full and not capped like the message band: the object history is the
      # record of what happened
      categories = [
        (_('aufgenommen'), result.added),
        (_('nicht mehr vorhanden'), result.vanished),
        (_('wieder aufgetaucht'), result.reappeared),
        (_('Datentyp aktualisiert'), result.retyped),
      ]
      message.append(
        {
          'changed': {
            'name': str(_('Attributinventar')),
            'object': str(form.instance),
            'fields': [f'{label}: {", ".join(names)}' for label, names in categories if names],
          }
        }
      )
    return message
