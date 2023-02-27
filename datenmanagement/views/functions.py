import os

from datetime import date, datetime
from django.apps import apps
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.forms import CheckboxSelectMultiple, TextInput
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from leaflet.forms.widgets import LeafletWidget
from locale import LC_ALL, format_string, setlocale
from re import sub
from toolbox.models import Subsets

from .fields import ArrayDateField


def assign_widgets(field):
  """
  liefert passendes Formularelement (Widget) zu übergebenem Feld

  :param field: Feld
  :return: Formularelement (Widget) zu übergebenem Feld
  """
  # Array-Felder als solche markieren,
  # ihre Klasse jedoch mit jener ihres Basisfeldes überschreiben
  is_array_field = False
  if field.__class__.__name__ == 'ArrayField':
    field = field.base_field
    is_array_field = True
  form_field = field.formfield()
  if (
      form_field.widget.__class__.__name__ == 'Select'
      or form_field.widget.__class__.__name__ == 'NullBooleanSelect'
  ):
    form_field.widget.attrs['class'] = 'form-select'
  elif form_field.widget.__class__.__name__ == 'Textarea':
    form_field.widget.attrs['class'] = 'form-control'
  elif field.name == 'geometrie':
    form_field = field.formfield(widget=LeafletWidget())
  elif field.__class__.__name__ == 'CharField' and field.name == 'farbe':
    form_field = field.formfield(widget=TextInput(attrs={
      'type': 'color',
      'class': 'form-control-color'
    }))
  elif field.__class__.__name__ == 'ChoiceArrayField':
    form_field = field.formfield(empty_value=None, widget=CheckboxSelectMultiple())
  elif field.__class__.__name__ == 'DateField':
    if is_array_field:
      label = form_field.label
      form_field = ArrayDateField(
        label=label,
        widget=TextInput(
          attrs={
            'type': 'date',
            'class': 'form-control'
          }
        )
      )
      form_field.required = False
    else:
      form_field = field.formfield(widget=TextInput(attrs={
        'type': 'date',
        'class': 'form-control'
      }))
  elif field.__class__.__name__ == 'DateTimeField':
    form_field = field.formfield(widget=TextInput(attrs={
      'type': 'datetime-local',
      'class': 'form-control',
      'step': '1'
    }))
  elif field.__class__.__name__ == 'TimeField':
    form_field = field.formfield(widget=TextInput(attrs={
      'type': 'time',
      'class': 'form-control',
      'step': '1'
    }))
  else:
    if hasattr(form_field.widget, 'input_type'):
      if form_field.widget.input_type == 'checkbox':
        form_field.widget.attrs['class'] = 'form-check-input'
      else:
        form_field.widget.attrs['class'] = 'form-control'
  # Markierung als Array-Feld als HTML-Attribut in Formularfeld übertragen, falls vorhanden
  if is_array_field:
    form_field.widget.attrs['is_array_field'] = 'true'
  return form_field


def delete_object_immediately(request, pk):
  """
  löscht das Datenobjekt mit dem übergebenen Primärschlüssel aus der Datenbank;
  wirft eine entsprechende Exception bei fehlenden Berechtigungen

  :param request: WSGI-Request
  :param pk: Primärschlüssel des zu löschenden Datenbankobjekts
  :return: HTTP-Code 204 (No Content)
  """
  model_name = sub(
    pattern='^.*\\/',
    repl='',
    string=sub(
      pattern='\\/deleteimmediately.*$',
      repl='',
      string=request.path_info
    )
  )
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  obj = get_object_or_404(model, pk=pk)
  if request.user.has_perm('datenmanagement.delete_' + model_name.lower()):
    obj.delete()
  else:
    raise PermissionDenied()
  return HttpResponse(status=204)


def get_data(curr_object, field):
  """
  gibt die Daten des übergebenen Feldes für das übergebene Datenobjekt zurück

  :param curr_object: Datenobjekt
  :param field: Feld
  :return: Daten des übergebenen Feldes für das übergebene Datenobjekt
  """
  data = getattr(curr_object, field)
  if isinstance(data, date):
    data = data.strftime('%Y-%m-%d')
  elif isinstance(data, datetime):
    data = data.strftime('%Y-%m-%d %H:%M:%S')
  return data


def get_model_objects(model, subset_id=None, count_only=False):
  """
  gibt entweder alle Datenobjekte des übergebenen Datenmodells
  oder aber eine Untermenge davon zurück

  :param model: Datenmodell
  :param subset_id: ID der Untermenge
  :param count_only: nur die Anzahl und nicht die Datenobjekte selbst zurückgeben?
  :return: entweder alle Datenobjekte des übergebenen Datenmodells
  oder aber eine Untermenge davon
  """
  if subset_id is not None and isinstance(subset_id, int):
    subset = Subsets.objects.filter(id=subset_id)[0]
    if (
        subset is not None
        and isinstance(subset, Subsets)
        and subset.model.model == model.__name__.lower()
    ):
      objects = model.objects.filter(pk__in=subset.pk_values)
    else:
      objects = model.objects.all()
  else:
    objects = model.objects.all()
  return objects.count() if count_only else objects


def get_thumb_url(url):
  """
  gibt die zugehörige Thumbnail-URL für die übergebene URL eines Fotos zurück

  :param url: URL eines Fotos
  :return: zugehörige Thumbnail-URL für die übergebene URL eines Fotos
  """
  head, tail = os.path.split(url)
  return head + '/thumbs/' + tail


def get_uuids_geometries_from_sql(rows):
  """
  gibt alle UUID (als Liste) und alle Geometrien (als Liste)
  aus dem Resultat einer SQL-Abfrage zurück

  :param rows: Resultat einer SQL-Abfrage
  :return: alle UUID (als Liste) und alle Geometrien (als Liste) aus dem Resultat einer SQL-Abfrage
  """
  uuid_list = []
  geometry_list = []
  for i in range(len(rows)):
    uuid_list.append(rows[i][0])
    geometry_list.append(str(rows[i][1]))
  return uuid_list, geometry_list


def localize_number(value):
  """
  gibt den übergebenen numerischen Wert lokalisiert zurück

  :param value: numerischer Wert
  :return: lokalisierter numerischer Wert
  """
  setlocale(LC_ALL, 'de_DE.UTF-8')
  return format_string('%.2f', value, grouping=True)


def set_form_attributes(form):
  """
  setzt Attribute im übergebenen Forumular und gibt dieses Forumular anschließend wieder zurück

  :param form: Forumular
  :return: Forumular mit gesetzten Attributen
  """
  form.fields_with_foreign_key_to_linkify = (
      form.model._meta.fields_with_foreign_key_to_linkify if hasattr(
          form.model._meta, 'fields_with_foreign_key_to_linkify') else None)
  form.choices_models_for_choices_fields = (
      form.model._meta.choices_models_for_choices_fields if hasattr(
          form.model._meta, 'choices_models_for_choices_fields') else None)
  form.group_with_users_for_choice_field = (
      form.model._meta.group_with_users_for_choice_field if hasattr(
          form.model._meta, 'group_with_users_for_choice_field') else None)
  return form


def set_form_context_elements(context, model):
  """
  setzt auf das Formular für das übergebene Datenmodell bezogene Elemente im übergebenen Kontext
  und gibt diesen Kontext anschließend wieder zurück

  :param context: Kontext
  :param model: Datenmodell
  :return: Kontext mit gesetzten,
  auf das Formular für das übergebene Datenmodell bezogenen Elementen
  """
  context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
  context['REVERSE_SEARCH_RADIUS'] = settings.REVERSE_SEARCH_RADIUS
  context['catalog_link_fields'] = (
      model._meta.catalog_link_fields if hasattr(model._meta, 'catalog_link_fields') else None)
  context['catalog_link_fields_names'] = (
      list(model._meta.catalog_link_fields.keys()) if hasattr(
          model._meta, 'catalog_link_fields') else None)
  context['fields_with_foreign_key_to_linkify'] = (
      model._meta.fields_with_foreign_key_to_linkify if hasattr(
          model._meta, 'fields_with_foreign_key_to_linkify') else None)
  context['choices_models_for_choices_fields'] = (
      model._meta.choices_models_for_choices_fields if hasattr(
          model._meta, 'choices_models_for_choices_fields') else None)
  context['address_type'] = (
      model._meta.address_type if hasattr(model._meta, 'address_type') else None)
  context['address_mandatory'] = (
      model._meta.address_mandatory if hasattr(model._meta, 'address_mandatory') else None)
  context['readonly_fields'] = (
      model._meta.readonly_fields if hasattr(model._meta, 'readonly_fields') else None)
  context['group_with_users_for_choice_field'] = (
      model._meta.group_with_users_for_choice_field if hasattr(
          model._meta, 'group_with_users_for_choice_field') else None)
  # GPX-Upload-Feld
  context['gpx_input'] = (
      model._meta.gpx_input if hasattr(model._meta, 'gpx_input') else None)
  # Postleitzahl-Auto-Zuweisung
  context['postcode_assigner'] = (
      model._meta.postcode_assigner if hasattr(model._meta, 'postcode_assigner') else None)
  # zusätzliche WMS-Layer
  context['additional_wms_layers'] = (
    model._meta.additional_wms_layers if hasattr(
      model._meta, 'additional_wms_layers') else None)
  # zusätzliche WFS-Feature-Types
  context['additional_wfs_featuretypes'] = (
    model._meta.additional_wfs_featuretypes if hasattr(
      model._meta, 'additional_wfs_featuretypes') else None)
  # Liste aller Datensätze für die Overlay-Daten-Liste
  model_list = {}
  app_models = apps.get_app_config('datenmanagement').get_models()
  for app_model in app_models:
    if hasattr(app_model._meta, 'as_overlay') and app_model._meta.as_overlay is True:
      model_list[app_model.__name__] = app_model._meta.verbose_name_plural
  context['model_list'] = dict(sorted(model_list.items()))
  context['forms_in_mobile_mode'] = (
      model._meta.forms_in_mobile_mode if hasattr(model._meta, 'forms_in_mobile_mode') else False)
  return context


def set_model_related_context_elements(context, model, kwargs=None):
  """
  setzt allgemeine, auf das übergebene Datenmodell bezogene Elemente im übergebenen Kontext
  und gibt diesen Kontext anschließend wieder zurück

  :param context: Kontext
  :param model: Datenmodell
  :param kwargs: kwargs des Views, der diese Funktion aufruft
  :return: Kontext mit gesetzten allgemeinen, auf das übergebene Datenmodell bezogenen Elementen
  """
  context['model_name'] = model.__name__
  context['model_name_lower'] = model.__name__.lower()
  context['model_pk_field'] = model._meta.pk.name
  context['model_verbose_name'] = model._meta.verbose_name
  context['model_verbose_name_plural'] = model._meta.verbose_name_plural
  context['model_description'] = model._meta.description
  context['editable'] = (
      model._meta.editable if hasattr(model._meta, 'editable') else True)
  context['geometry_type'] = (
      model._meta.geometry_type if hasattr(model._meta, 'geometry_type') else None)
  context['subset_id'] = None
  if kwargs and kwargs['subset_id']:
    subset_id = int(kwargs['subset_id'])
    context['subset_id'] = subset_id
    context['objects_count'] = get_model_objects(model, subset_id, True)
  else:
    context['objects_count'] = get_model_objects(model, None, True)
  return context
