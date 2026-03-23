import json

from django.conf import settings
from django.contrib.gis.geos import Point
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.forms import ChoiceField, ModelForm, ModelMultipleChoiceField, ValidationError, widgets
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ..constants_vars import ADMIN_GROUP, USERS_GROUP
from ..utils import (
  authorized_to_edit,
  get_user_provider,
  is_angebotsdb_admin,
  is_angebotsdb_user,
)
from .functions import add_permission_context_elements


def _set_geometry_from_request(request, instance):
  """
  Liest die Geometrie aus dem Hidden-Field 'geometry' im POST-Request
  und setzt sie auf die Service-Instanz (EPSG:4326 GeoJSON → EPSG:25833 Point).
  """
  geometry_json = request.POST.get('geometry', '')
  if geometry_json:
    try:
      geojson = json.loads(geometry_json)
      coords = geojson.get('coordinates', [])
      if coords and len(coords) >= 2 and coords[0] != 0 and coords[1] != 0:
        point = Point(coords[0], coords[1], srid=4326)
        point.transform(25833)
        instance.geometry = point
    except (json.JSONDecodeError, TypeError, KeyError):
      pass


class CreatableMultipleChoiceField(ModelMultipleChoiceField):
  """
  A custom ModelMultipleChoiceField that accepts both existing object IDs and new names. When
  processing the input, it first tries to resolve any numeric values as existing IDs. Any values
  that cannot be resolved as IDs are treated as new names, for which new objects are created via
  get_or_create. The target model must be passed as the `model` keyword argument.
  """

  def __init__(self, *args, model=None, **kwargs):
    self._model_class = model
    super().__init__(*args, **kwargs)

  def _check_values(self, value):
    """
    Accepts a list of IDs or names. IDs are resolved first, with any missing IDs interpreted
    as names. Returns all found or newly created objects.
    """
    model_class = self._model_class
    key = self.to_field_name or 'pk'
    value = list(set(value))
    pks = []
    names = []

    for item in value:
      if str(item).isdigit():
        pks.append(str(item))
      else:
        names.append(item)

    qs = self.queryset.filter(**{'%s__in' % key: pks})
    found_map = {str(getattr(t, key)): t for t in qs}
    found = list(found_map.values())

    for pk in pks:
      if pk not in found_map:
        names.append(pk)

    for name in names:
      if str(name).strip():
        obj, _ = model_class.objects.get_or_create(name=name)
        if obj not in found:
          found.append(obj)

    return found

  def to_python(self, value):
    if not value:
      return []
    return list(self._check_values(value))


class DynamicStyledModelForm(ModelForm):
  """
  Eine ModelForm, die automatisch CSS-Klassen zu allen Feldern hinzufügt
  basierend auf ihrem Widget-Typ.
  """

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    # Mapping: Widget-Typ → CSS-Klassen und zusätzliche HTML-Attribute
    widget_config = {
      widgets.TextInput: {
        'class': 'form-control text-input',
        'autocomplete': 'off',
        'spellcheck': 'false',
      },
      widgets.NumberInput: {
        'class': 'form-control number-input',
        'step': 'any',
        'autocomplete': 'off',
      },
      widgets.EmailInput: {
        'class': 'form-control email-input',
        'autocomplete': 'email',
        'spellcheck': 'false',
      },
      widgets.URLInput: {
        'class': 'form-control url-input',
        'autocomplete': 'url',
        'spellcheck': 'false',
      },
      widgets.PasswordInput: {
        'class': 'form-control password-input',
        'autocomplete': 'current-password',
      },
      widgets.Select: {'class': 'form-control form-select select-input'},
      widgets.SelectMultiple: {'class': 'form-select select2-multiple'},
      widgets.Textarea: {
        'class': 'form-control textarea-input',
        'rows': '4',
        'spellcheck': 'true',
      },
      widgets.CheckboxInput: {'class': 'form-check-input checkbox-input'},
      widgets.DateInput: {'class': 'form-control date-input', 'autocomplete': 'off'},
      widgets.TimeInput: {'class': 'form-control time-input', 'autocomplete': 'off'},
      widgets.DateTimeInput: {'class': 'form-control datetime-input', 'autocomplete': 'off'},
      widgets.FileInput: {'class': 'form-control'},
      widgets.ClearableFileInput: {'class': 'form-control'},
    }

    # Durch alle Felder iterieren
    for field_name, field in self.fields.items():
      widget_type = type(field.widget)

      # Passende Konfiguration für diesen Widget-Typ finden
      if widget_type in widget_config:
        config = widget_config[widget_type]

        # CSS-Klassen behandeln (bestehende erhalten)
        if 'class' in config:
          existing_classes = field.widget.attrs.get('class', '')
          new_classes = config['class']

          if existing_classes:
            field.widget.attrs['class'] = f'{existing_classes} {new_classes}'
          else:
            field.widget.attrs['class'] = new_classes

        # Alle anderen Attribute aus der Konfiguration hinzufügen
        for attr_name, attr_value in config.items():
          if attr_name != 'class':  # CSS-Klassen wurden bereits behandelt
            field.widget.attrs[attr_name] = attr_value

      # Zusätzliche Attribute für bessere UX (nur wenn kein Placeholder bereits gesetzt)
      if (
        not isinstance(field.widget, widgets.CheckboxInput)
        and 'placeholder' not in field.widget.attrs
      ):
        field.widget.attrs.update(
          {'placeholder': field.label or field_name.replace('_', ' ').title()}
        )

      # HTML5-Validierung unterstützen
      if field.required:
        field.widget.attrs['required'] = 'required'


class GenericCreateView(CreateView):
  template_name = 'kiju/form.html'
  # model = None
  success_url = None

  def __init__(self, model, *args, **kwargs):
    self.model = model
    self.success_url = reverse_lazy(viewname=f'kiju:{self.model.__name__.lower()}_list')

  def dispatch(self, request, *args, **kwargs):
    self.fields = '__all__'
    return super().dispatch(request, *args, **kwargs)

  def get_form_class(self):
    """
    Dynamically creates a ModelForm class for the given model, applying specific customizations
    based on the model type:
    - For UserProfile: Excludes the user_id field from Meta and adds it as a ChoiceField
      in __init__.
    - For Service models: Excludes the host field from Meta, as it will be automatically
      populated from the user's profile.
    - For all other models: Includes all fields by default.
    """
    # Check permissions
    if not (
      is_angebotsdb_user(self.request.user)
      or self.request.user.is_superuser
      or self.request.user.is_staff
    ):
      raise PermissionDenied("You don't have permission to access this resource")

    used_model = self.model

    from ..models.base import UserProfile
    from ..models.services import Service

    # Prüfen ob das Modell ein Service-Modell ist
    is_service_model = not used_model._meta.abstract and issubclass(used_model, Service)

    # Meta-Klasse dynamisch erstellen, um fields/exclude-Konflikt zu vermeiden.
    # Django erlaubt NICHT fields='__all__' und exclude gleichzeitig in Meta.
    if used_model == UserProfile:
      # user_id wird manuell als ChoiceField in __init__ hinzugefügt
      _meta_attrs = {'model': used_model, 'exclude': ['user_id']}
    elif is_service_model:
      # host- und status-Feld werden automatisch verwaltet → aus dem Formular ausschließen
      _meta_attrs = {'model': used_model, 'exclude': ['host', 'status', 'published_version', 'geometry']}
    else:
      _meta_attrs = {'model': used_model, 'fields': '__all__'}
    _FormMeta = type('Meta', (), _meta_attrs)

    class StyledForm(DynamicStyledModelForm):
      Meta = _FormMeta

      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if used_model == UserProfile:
          from django.contrib.auth.models import User

          users = (
            User.objects.using('default')
            .filter(groups__name__in=[ADMIN_GROUP, USERS_GROUP])
            .distinct()
            .order_by('username')
          )

          user_choices = [('', '----------')]
          for user in users:
            full_name = user.get_full_name()
            display = f'{user.username} ({full_name})' if full_name else user.username
            user_choices.append((user.id, display))

          self.fields['user_id'] = ChoiceField(
            choices=user_choices,
            label='Benutzer',
            required=True,
            help_text='Wählen Sie einen Benutzer aus der AngebotsDB-Gruppe',
          )
          # CSS-Klassen und Attribute manuell setzen, da das Feld nach
          # super().__init__() hinzugefügt wird und DynamicStyledModelForm
          # es deshalb nicht automatisch stylen kann.
          self.fields['user_id'].widget.attrs.update(
            {
              'class': 'form-control form-select select-input',
              'placeholder': 'Benutzer auswählen',
              'required': 'required',
            }
          )
          # user_id als erstes Feld anzeigen
          field_order = ['user_id'] + [f for f in self.fields if f != 'user_id']
          self.order_fields(field_order)

        if 'tags' in self.fields:
          from ..models.base import Tag

          current_field = self.fields['tags']
          self.fields['tags'] = CreatableMultipleChoiceField(
            model=Tag,
            queryset=Tag.objects.all(),
            label=current_field.label,
            required=current_field.required,
            widget=widgets.SelectMultiple(
              attrs={'class': 'form-select select2-multiple', 'data-tags': 'true'}
            ),
          )

        if 'target_group' in self.fields:
          from ..models.base import TargetGroup

          current_field = self.fields['target_group']
          self.fields['target_group'] = CreatableMultipleChoiceField(
            model=TargetGroup,
            queryset=TargetGroup.objects.all(),
            label=current_field.label,
            required=current_field.required,
            widget=widgets.SelectMultiple(
              attrs={'class': 'form-select select2-multiple', 'data-tags': 'true'}
            ),
          )

        for field_name, config in getattr(used_model, 'PYGEOAPI_FIELDS', {}).items():
          if field_name in self.fields:
            from ..fields import PyGeoAPIMultipleChoiceField

            current_field = self.fields[field_name]
            self.fields[field_name] = PyGeoAPIMultipleChoiceField(
              endpoint=config['endpoint'],
              params=config.get('params', {}),
              label_property=config['label_property'],
              initial_values=None,
              label=current_field.label,
              required=current_field.required,
              help_text=current_field.help_text,
            )

        # Adressfeld-Placeholder anpassen
        if is_service_model:
          if 'street' in self.fields:
            self.fields['street'].widget.attrs['placeholder'] = 'Straße & Hausnr.'
          if 'zip' in self.fields:
            self.fields['zip'].widget.attrs['placeholder'] = 'PLZ'
          if 'city' in self.fields:
            self.fields['city'].widget.attrs['placeholder'] = 'Gemeinde'

    return StyledForm

  def form_valid(self, form):
    # Spezielle Behandlung für UserProfile: Setze automatisch den aktuellen Benutzer
    if self.model.__name__ == 'UserProfile':
      if 'user_id' in form.cleaned_data:
        form.instance.user_id = int(form.cleaned_data['user_id'])

    # Spezielle Behandlung für Service-Modelle: host automatisch aus UserProfile befüllen
    from ..models.services import Service

    is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)
    if is_service_model:
      provider = get_user_provider(self.request.user)
      if provider:
        form.instance.host = provider
      else:
        form.add_error(
          None,
          ValidationError(
            'Ihrem Benutzerprofil ist kein Träger zugeordnet. '
            'Bitte wenden Sie sich an einen Administrator.'
          ),
        )
        return self.form_invalid(form)
      # Geometrie aus Hidden-Field übernehmen
      _set_geometry_from_request(self.request, form.instance)

    # IntegrityError abfangen, die z.B. bei unique_together-Verletzungen entsteht
    try:
      response = super().form_valid(form)
    except IntegrityError:
      form.add_error(
        None,
        ValidationError(
          'Dieser Eintrag existiert bereits. '
          'Die Kombination aus den gewählten Werten muss eindeutig sein.'
        ),
      )
      return self.form_invalid(form)

    # Hochgeladene Bilder als ServiceImage-Objekte speichern
    if is_service_model:
      _save_uploaded_images(
        self.request,
        self.model.__name__.lower(),
        self.object.pk,
      )

    return response

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # Berechtigungs-Informationen hinzufügen
    context = add_permission_context_elements(context, self.request.user)

    # Model-Informationen hinzufügen
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_name'] = self.model.__name__
    context['model_lower'] = self.model.__name__.lower()
    context['model_icon'] = getattr(self.model, 'icon', None)

    context['LEAFLET_CONFIG'] = getattr(
      settings,
      'LEAFLET_CONFIG',
      {
        'DEFAULT_CENTER': (51.0, 10.0),
        'DEFAULT_ZOOM': 6,
        'MIN_ZOOM': 3,
        'MAX_ZOOM': 18,
      },
    )

    # user_can_save: Speicher-Button im Template anzeigen?
    # Admins und Superuser dürfen immer speichern.
    # Normale Nutzer nur, wenn ihnen im UserProfile ein Provider zugeordnet ist.
    from ..models.services import Service

    is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)
    if is_service_model:
      context['user_can_save'] = authorized_to_edit(self.request.user)
      context['service_images'] = []
      context['is_service_model'] = True
      context['addresssearch_url'] = reverse_lazy('toolbox:addresssearch')
    else:
      context['user_can_save'] = True

    return context


class GenericUpdateView(UpdateView):
  template_name = 'kiju/form.html'
  # model = None
  success_url = None

  readonly = False

  def __init__(self, model, readonly=False, *args, **kwargs):
    self.model = model
    self.readonly = readonly
    self.success_url = reverse_lazy(viewname=f'kiju:{self.model.__name__.lower()}_list')

  def dispatch(self, request, *args, **kwargs):
    if not (
      is_angebotsdb_user(request.user) or request.user.is_superuser or request.user.is_staff
    ):
      return HttpResponseForbidden("You don't have permission to access this resource")
    self.fields = '__all__'
    self._editing_published = False

    # ── Readonly-Modus (Detail-Ansicht) ────────────────────────────────────
    if self.readonly:
      self._service_locked = True
      return super().dispatch(request, *args, **kwargs)

    from django.shortcuts import redirect
    from django.urls import reverse

    from ..models.services import Service
    from ..utils import get_draft_copy_for_user, get_user_provider

    obj = self.get_object()  # nutzt Cache ab jetzt
    is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)

    if is_service_model:
      status = getattr(obj, 'status', None)

      # ── Sperre bei in_review ───────────────────────────────────────────────
      if status == 'in_review':
        self._service_locked = True

      # ── Published: Draft suchen oder Formular normal öffnen ─────────────
      elif status == 'published':
        provider = get_user_provider(request.user)

        if provider is not None:
          draft = get_draft_copy_for_user(obj, request.user)
        else:
          draft = obj.__class__.objects.filter(
            published_version=obj,
            status__in=['draft', 'in_review', 'revision_needed'],
          ).first()

        if draft is not None:
          # Draft existiert → zum Draft weiterleiten
          draft_url = reverse(
            f'kiju:{self.model.__name__.lower()}_update',
            args=[draft.pk],
          )
          return redirect(draft_url)
        else:
          # Kein Draft → Formular normal öffnen, Draft erst beim Speichern
          self._editing_published = True
          self._service_locked = False

      else:
        self._service_locked = False
    else:
      self._service_locked = False

    return super().dispatch(request, *args, **kwargs)

  def get_object(self, queryset=None):
    """
    Gibt das angeforderte Objekt zurück. Cached das Ergebnis in self._cached_object
    um mehrfache DB-Abfragen innerhalb desselben Requests zu vermeiden.
    """
    if hasattr(self, '_cached_object') and self._cached_object is not None:
      return self._cached_object
    self._cached_object = super().get_object(queryset)
    return self._cached_object

  def get_form_class(self):
    # Check permissions
    if not (
      is_angebotsdb_user(self.request.user)
      or self.request.user.is_superuser
      or self.request.user.is_staff
    ):
      raise PermissionDenied("You don't have permission to access this resource")

    used_model = self.model
    service_locked = getattr(self, '_service_locked', False)

    from ..models.services import Service

    is_service_model = not used_model._meta.abstract and issubclass(used_model, Service)

    if is_service_model:
      _meta_attrs = {'model': used_model, 'exclude': ['host', 'status', 'published_version', 'geometry']}
    else:
      _meta_attrs = {'model': used_model, 'fields': '__all__'}
    _FormMeta = type('Meta', (), _meta_attrs)

    class StyledForm(DynamicStyledModelForm):
      Meta = _FormMeta

      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'tags' in self.fields:
          from ..models.base import Tag

          current_field = self.fields['tags']
          self.fields['tags'] = CreatableMultipleChoiceField(
            model=Tag,
            queryset=Tag.objects.all(),
            label=current_field.label,
            required=current_field.required,
            widget=widgets.SelectMultiple(
              attrs={'class': 'form-select select2-multiple', 'data-tags': 'true'}
            ),
          )

        if 'target_group' in self.fields:
          from ..models.base import TargetGroup

          current_field = self.fields['target_group']
          self.fields['target_group'] = CreatableMultipleChoiceField(
            model=TargetGroup,
            queryset=TargetGroup.objects.all(),
            label=current_field.label,
            required=current_field.required,
            widget=widgets.SelectMultiple(
              attrs={'class': 'form-select select2-multiple', 'data-tags': 'true'}
            ),
          )

        for field_name, config in getattr(used_model, 'PYGEOAPI_FIELDS', {}).items():
          if field_name in self.fields:
            from ..fields import PyGeoAPIMultipleChoiceField

            current_field = self.fields[field_name]
            existing = getattr(self.instance, field_name, None) or [] if self.instance and self.instance.pk else []
            self.fields[field_name] = PyGeoAPIMultipleChoiceField(
              endpoint=config['endpoint'],
              params=config.get('params', {}),
              label_property=config['label_property'],
              initial_values=existing,
              label=current_field.label,
              required=current_field.required,
              help_text=current_field.help_text,
            )
            if existing:
              self.initial[field_name] = existing

        # Adressfeld-Placeholder anpassen
        if is_service_model:
          if 'street' in self.fields:
            self.fields['street'].widget.attrs['placeholder'] = 'Straße & Hausnr.'
          if 'zip' in self.fields:
            self.fields['zip'].widget.attrs['placeholder'] = 'PLZ'
          if 'city' in self.fields:
            self.fields['city'].widget.attrs['placeholder'] = 'Gemeinde'

        # Bei gesperrtem Service alle Felder deaktivieren
        if service_locked:
          for field in self.fields.values():
            field.widget.attrs['disabled'] = 'disabled'

    return StyledForm

  def form_valid(self, form):
    # POST-Absicherung: Gesperrte Services (in_review/readonly) dürfen nicht gespeichert werden
    if getattr(self, '_service_locked', False):
      raise PermissionDenied(
        'Dieser Service befindet sich in Prüfung und kann nicht bearbeitet werden.'
      )

    # POST-Absicherung: Normale Nutzer dürfen nur Services ihres eigenen Providers speichern
    from ..models.services import Service

    is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)
    if is_service_model and not authorized_to_edit(self.request.user, self.object):
      raise PermissionDenied('Sie haben keine Berechtigung, dieses Angebot zu bearbeiten.')

    # Geometrie aus Hidden-Field übernehmen
    if is_service_model:
      _set_geometry_from_request(self.request, form.instance)

    # Lazy Draft-Erstellung: Bei published Services wird nicht direkt gespeichert,
    # sondern ein Draft-Copy mit den Änderungen erstellt.
    if getattr(self, '_editing_published', False):
      from django.shortcuts import redirect

      from ..utils import create_draft_copy

      published = self.object
      draft = create_draft_copy(published, self.request.user)

      # Formular-Änderungen auf den Draft anwenden
      for field_name, value in form.cleaned_data.items():
        try:
          field_obj = draft._meta.get_field(field_name)
          if field_obj.many_to_many:
            getattr(draft, field_name).set(value)
          else:
            setattr(draft, field_name, value)
        except Exception:
          pass
      # Geometrie auch auf den Draft übertragen
      _set_geometry_from_request(self.request, draft)
      draft.save()

      # Hochgeladene Bilder auf den Draft speichern
      if is_service_model:
        _save_uploaded_images(
          self.request,
          self.model.__name__.lower(),
          draft.pk,
        )

      return redirect(self.success_url)

    response = super().form_valid(form)

    # Hochgeladene Bilder speichern
    if is_service_model:
      _save_uploaded_images(
        self.request,
        self.model.__name__.lower(),
        self.object.pk,
      )

    return response

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # Berechtigungs-Informationen hinzufügen
    context = add_permission_context_elements(context, self.request.user)

    # Model-Informationen hinzufügen
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_name'] = self.model.__name__
    context['model_lower'] = self.model.__name__.lower()
    context['model_icon'] = getattr(self.model, 'icon', None)
    context['is_update'] = True  # Kennzeichnung für Update-Operation
    context['readonly'] = self.readonly

    context['LEAFLET_CONFIG'] = getattr(
      settings,
      'LEAFLET_CONFIG',
      {
        'DEFAULT_CENTER': (51.0, 10.0),
        'DEFAULT_ZOOM': 6,
        'MIN_ZOOM': 3,
        'MAX_ZOOM': 18,
      },
    )

    # user_can_save: Speicher-Button im Template anzeigen?
    # Admins und Superuser dürfen immer speichern.
    # Normale Nutzer nur, wenn ihr Provider mit dem host des Service-Objekts übereinstimmt.
    # Bei gesperrten Services (in_review) darf niemand speichern.
    from ..models.services import Service

    is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)
    service_locked = getattr(self, '_service_locked', False)
    if service_locked:
      context['user_can_save'] = False
      context['service_locked'] = True
    elif is_service_model:
      context['user_can_save'] = authorized_to_edit(self.request.user, self.object)
      context['service_locked'] = False
    else:
      context['user_can_save'] = True
      context['service_locked'] = False

    if is_service_model:
      context['is_service_model'] = True
      context['addresssearch_url'] = reverse_lazy('toolbox:addresssearch')

    # Service-Bilder für das Template laden
    if is_service_model:
      from ..models.services import ServiceImage

      context['service_images'] = ServiceImage.objects.filter(
        service_type=self.model.__name__.lower(),
        service_id=self.object.pk,
      )

    # Service-Status und Kommentare für Workflow-Buttons im Template
    if is_service_model:
      context['service_status'] = getattr(self.object, 'status', None)
      # Kommentare des letzten abgelehnten ReviewTask für die Überarbeitungsansicht laden
      from ..models.base import ReviewTask

      latest_rejected = (
        ReviewTask.objects.filter(
          service_type=self.model.__name__.lower(),
          service_id=self.object.pk,
          task_status='rejected',
        )
        .order_by('-created_at')
        .first()
      )
      context['revision_comments'] = latest_rejected.comments if latest_rejected else {}
      context['is_draft_copy'] = getattr(self.object, 'published_version_id', None) is not None
      context['published_version'] = getattr(self.object, 'published_version', None)
    else:
      context['service_status'] = None
      context['revision_comments'] = {}
      context['is_draft_copy'] = False
      context['published_version'] = None

    # Geometrie zu GeoJSON konvertieren, falls vorhanden
    if hasattr(self.object, 'geometry') and self.object.geometry:
      try:
        geom = self.object.geometry
        # Transformiere von EPSG:25833 zu EPSG:4326
        geom_transformed = geom.transform(4326, clone=True)
        # Konvertiere zu GeoJSON
        geojson = json.loads(geom_transformed.geojson)
        context['geometry'] = json.dumps(geojson)
        context['model_geometry_type'] = geom.geom_type
      except Exception:
        context['geometry'] = None
    else:
      context['geometry'] = None

    return context


class GenericDeleteView(DeleteView):
  template_name = 'kiju/delete.html'
  # model = None
  success_url = None

  def __init__(self, model, *args, **kwargs):
    self.model = model
    self.success_url = reverse_lazy(viewname=f'kiju:{self.model.__name__.lower()}_list')

  def dispatch(self, request, *args, **kwargs):
    if not (
      is_angebotsdb_user(request.user) or request.user.is_superuser or request.user.is_staff
    ):
      return HttpResponseForbidden("You don't have permission to access this resource")
    return super().dispatch(request, *args, **kwargs)

  def get_object(self, queryset=None):
    """
    Gibt das angeforderte Objekt zurück. Bei Service-Modellen wird geprüft, ob der
    Nutzer berechtigt ist, dieses Objekt zu löschen (Provider-Vergleich).
    Admins und Superuser dürfen alle Objekte löschen.
    """
    obj = super().get_object(queryset)

    from ..models.services import Service

    is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)
    if is_service_model and not authorized_to_edit(self.request.user, obj):
      raise PermissionDenied('Sie haben keine Berechtigung, dieses Angebot zu löschen.')

    return obj

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    # Berechtigungs-Informationen hinzufügen
    context = add_permission_context_elements(context, self.request.user)

    # Model-Informationen hinzufügen
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_name'] = self.model.__name__
    context['model_lower'] = self.model.__name__.lower()

    # Benutzerberechtigungen hinzufügen
    context['is_angebotsdb_user'] = is_angebotsdb_user(self.request.user)
    context['is_angebotsdb_admin'] = is_angebotsdb_admin(self.request.user)

    return context

  def _delete_related_review_tasks(self, obj):
    """Löscht alle ReviewTasks (inkl. InboxMessages via CASCADE) für einen Service."""
    from ..models.services import Service
    from ..models.base import ReviewTask

    if not self.model._meta.abstract and issubclass(self.model, Service):
      ReviewTask.objects.filter(
        service_type=self.model.__name__.lower(),
        service_id=obj.pk,
      ).delete()

  def delete(self, request, *args, **kwargs):
    """
    Überschreibt die delete-Methode, um AJAX-Anfragen zu unterstützen.
    Die Provider-Berechtigung wird bereits in get_object geprüft.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
      try:
        self.object = self.get_object()
        self._delete_related_review_tasks(self.object)
        self.object.delete()

        # Erfolgsmeldung zurückgeben
        return JsonResponse(
          {
            'success': True,
            'message': f'{self.model._meta.verbose_name} wurde erfolgreich gelöscht.',
          }
        )
      except PermissionDenied as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=403)
      except Exception as e:
        # Fehlermeldung zurückgeben
        return JsonResponse(
          {'success': False, 'message': f'Fehler beim Löschen: {str(e)}'}, status=400
        )
    else:
      # Normale Behandlung für nicht-AJAX-Anfragen
      self.object = self.get_object()
      self._delete_related_review_tasks(self.object)
      return super().delete(request, *args, **kwargs)


def _save_uploaded_images(request, service_type, service_id):
  """
  Speichert alle hochgeladenen Bilder aus request.FILES als ServiceImage-Objekte.
  """
  from ..models.services import ServiceImage

  files = request.FILES.getlist('images')
  for file in files:
    ServiceImage.objects.create(
      service_type=service_type,
      service_id=service_id,
      image=file,
    )


class ServiceImageDeleteView(View):
  """
  AJAX-Endpoint zum Löschen eines ServiceImage.
  """

  def post(self, request, pk):
    from ..models.services import ServiceImage

    if not (
      is_angebotsdb_user(request.user) or request.user.is_superuser or request.user.is_staff
    ):
      return JsonResponse({'success': False, 'message': 'Keine Berechtigung.'}, status=403)

    try:
      image = ServiceImage.objects.get(pk=pk)
    except ServiceImage.DoesNotExist:
      return JsonResponse({'success': False, 'message': 'Bild nicht gefunden.'}, status=404)

    # Berechtigungsprüfung: Nur Provider des zugehörigen Service oder Admin
    if not (request.user.is_superuser or is_angebotsdb_admin(request.user)):
      from ..utils import get_service_instance

      service = get_service_instance(image.service_type, image.service_id)
      if service and not authorized_to_edit(request.user, service):
        return JsonResponse({'success': False, 'message': 'Keine Berechtigung.'}, status=403)

    image.delete()
    return JsonResponse({'success': True, 'message': 'Bild wurde gelöscht.'})
