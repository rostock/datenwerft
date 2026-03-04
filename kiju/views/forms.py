import json

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.forms import ChoiceField, ModelForm, ModelMultipleChoiceField, ValidationError, widgets
from django.http import HttpResponseForbidden, JsonResponse
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from ..constants_vars import ADMIN_GROUP, USERS_GROUP
from ..utils import (
  authorized_to_edit,
  get_user_provider,
  is_angebotsdb_admin,
  is_angebotsdb_user,
)
from .functions import add_permission_context_elements


class TagMultipleChoiceField(ModelMultipleChoiceField):
  """
  A custom ModelMultipleChoiceField that accepts both existing tag IDs and new tag names. When
  processing the input, it first tries to resolve any numeric values as existing tag IDs. Any
  values that cannot resolved as IDs are treated as new tag names, for which new Tag objects are
  created. The final result is a list of Tag objects corresponding to the provided IDs and names.
  """

  def _check_values(self, value):
    """
    Accepts a list of IDs or names. IDs are resolved first, with any missing IDs interpreted
    as names. Returns all found or newly created tag objects.
    """
    from ..models.base import Tag

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
    found_tags_map = {str(getattr(t, key)): t for t in qs}
    found_tags = list(found_tags_map.values())

    for pk in pks:
      if pk not in found_tags_map:
        names.append(pk)

    for name in names:
      if str(name).strip():
        tag, created = Tag.objects.get_or_create(name=name)
        if tag not in found_tags:
          found_tags.append(tag)

    return found_tags

  def to_python(self, value):
    """
    Override to_python to handle both existing tag IDs and new tag names. If the value is empty,
    return an empty list. Otherwise, resolve IDs to tag objects and create new tags for any names.
    """
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
      _meta_attrs = {'model': used_model, 'exclude': ['host', 'status']}
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

        # Wenn das Modell ein Geometrie-Feld hat, verwende LeafletWidget
        if 'geometry' in self.fields:
          from leaflet.forms.widgets import LeafletWidget

          self.fields['geometry'].widget = LeafletWidget()

        if 'tags' in self.fields:
          from ..models.base import Tag

          current_field = self.fields['tags']
          self.fields['tags'] = TagMultipleChoiceField(
            queryset=Tag.objects.all(),
            label=current_field.label,
            required=current_field.required,
            widget=widgets.SelectMultiple(
              attrs={'class': 'form-select select2-multiple', 'data-tags': 'true'}
            ),
          )

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

    # IntegrityError abfangen, die z.B. bei unique_together-Verletzungen entsteht
    # (z.B. doppelter Eintrag bei OrgUnitServicePermission).
    # Ohne diesen Handler würde Django mit einem 500-Fehler abstürzen, da die
    # Datenbankeinschränkung erst beim INSERT greift — also nach der Formularvalidierung.
    # Stattdessen wird der Fehler als lesbarer Formularfehler zurückgegeben.
    try:
      return super().form_valid(form)
    except IntegrityError:
      form.add_error(
        None,
        ValidationError(
          'Dieser Eintrag existiert bereits. '
          'Die Kombination aus den gewählten Werten muss eindeutig sein.'
        ),
      )
      return self.form_invalid(form)

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
    else:
      context['user_can_save'] = True

    return context


class GenericUpdateView(UpdateView):
  template_name = 'kiju/form.html'
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
    self.fields = '__all__'

    from django.shortcuts import redirect
    from django.urls import reverse

    from ..models.services import Service
    from ..utils import create_draft_copy, get_draft_copy_for_user, get_user_provider

    obj = self.get_object()  # nutzt Cache ab jetzt
    is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)

    if is_service_model:
      status = getattr(obj, 'status', None)

      # ── Sperre bei in_review ───────────────────────────────────────────────
      if status == 'in_review':
        self._service_locked = True

      # ── Redirect bei published → Draft-Copy ──────────────────────────────
      elif status == 'published':
        # Gilt für ALLE Nutzer (auch Admins) — niemand darf published
        # Services direkt bearbeiten.
        provider = get_user_provider(request.user)

        if provider is not None:
          # Provider-Nutzer: Draft-Copy unter eigenem Provider suchen/anlegen
          draft = get_draft_copy_for_user(obj, request.user)
          if draft is None:
            draft = create_draft_copy(obj, request.user)
        else:
          # Admin/Superuser ohne Provider: Draft-Copy unter host des Originals
          # suchen oder neu anlegen (host bleibt der Original-Provider)
          draft = obj.__class__.objects.filter(
            published_version=obj,
            status__in=['draft', 'in_review', 'revision_needed'],
          ).first()
          if draft is None:
            draft = create_draft_copy(obj, request.user)

        draft_url = reverse(
          f'kiju:{self.model.__name__.lower()}_update',
          args=[draft.pk],
        )
        return redirect(draft_url)

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
      _meta_attrs = {'model': used_model, 'exclude': ['host', 'status']}
    else:
      _meta_attrs = {'model': used_model, 'fields': '__all__'}
    _FormMeta = type('Meta', (), _meta_attrs)

    class StyledForm(DynamicStyledModelForm):
      Meta = _FormMeta

      def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Wenn das Modell ein Geometrie-Feld hat, verwende LeafletWidget
        if 'geometry' in self.fields:
          from leaflet.forms.widgets import LeafletWidget

          self.fields['geometry'].widget = LeafletWidget()

        if 'tags' in self.fields:
          from ..models.base import Tag

          current_field = self.fields['tags']
          self.fields['tags'] = TagMultipleChoiceField(
            queryset=Tag.objects.all(),
            label=current_field.label,
            required=current_field.required,
            widget=widgets.SelectMultiple(
              attrs={'class': 'form-select select2-multiple', 'data-tags': 'true'}
            ),
          )

        # Bei gesperrtem Service alle Felder deaktivieren
        if service_locked:
          for field in self.fields.values():
            field.widget.attrs['disabled'] = 'disabled'

    return StyledForm

  def form_valid(self, form):
    # POST-Absicherung: Gesperrte Services (in_review) dürfen nicht gespeichert werden
    if getattr(self, '_service_locked', False):
      raise PermissionDenied(
        'Dieser Service befindet sich in Prüfung und kann nicht bearbeitet werden.'
      )

    # POST-Absicherung: Normale Nutzer dürfen nur Services ihres eigenen Providers speichern
    from ..models.services import Service

    is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)
    if is_service_model and not authorized_to_edit(self.request.user, self.object):
      raise PermissionDenied('Sie haben keine Berechtigung, dieses Angebot zu bearbeiten.')

    return super().form_valid(form)

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
        print(f'Geometrietyp: {geom.geom_type}')
      except Exception as e:
        print(f'Error converting geometry: {e}')
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

  def delete(self, request, *args, **kwargs):
    """
    Überschreibt die delete-Methode, um AJAX-Anfragen zu unterstützen.
    Die Provider-Berechtigung wird bereits in get_object geprüft.
    """
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
      try:
        self.object = self.get_object()
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
      return super().delete(request, *args, **kwargs)
