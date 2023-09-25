from django.apps import apps
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models.fields import DateField, DateTimeField, TimeField
from django.forms import CheckboxSelectMultiple, Select, TextInput, Textarea
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_user_agents.utils import get_user_agent
from leaflet.forms.widgets import LeafletWidget
from re import sub

from datenmanagement.models.fields import ChoiceArrayField
from datenmanagement.utils import is_geometry_field
from toolbox.models import Subsets
from .fields import ArrayDateField


def add_model_context_elements(context, model, kwargs=None):
  """
  adds general model related elements to the passed context and returns the context

  :param context: context
  :param model: model
  :param kwargs: kwargs of the view calling this function
  :return: context with general model related elements added
  """
  model_name = model.__name__
  context['model_name'] = model_name
  context['model_name_lower'] = model_name.lower()
  context['model_pk_field'] = model._meta.pk.name
  context['model_verbose_name'] = model._meta.verbose_name
  context['model_verbose_name_plural'] = model._meta.verbose_name_plural
  context['model_description'] = model.BasemodelMeta.description
  context['editable'] = model.BasemodelMeta.editable
  context['geometry_type'] = model.BasemodelMeta.geometry_type
  context['subset_id'] = None
  if kwargs and kwargs['subset_id']:
    subset_id = int(kwargs['subset_id'])
    context['subset_id'] = subset_id
    context['objects_count'] = get_model_objects(model, subset_id, True)
  else:
    context['objects_count'] = get_model_objects(model, None, True)
  return context


def add_model_form_context_elements(context, model):
  """
  adds model form related elements to the passed context and returns the context

  :param context: context
  :param model: model
  :return: context with model form related elements added
  """
  context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
  context['REVERSE_SEARCH_RADIUS'] = settings.REVERSE_SEARCH_RADIUS
  context['forms_in_mobile_mode'] = model.BasemodelMeta.forms_in_mobile_mode
  context['readonly_fields'] = model.BasemodelMeta.readonly_fields
  context['choices_models_for_choices_fields'] = (
    model.BasemodelMeta.choices_models_for_choices_fields)
  context['group_with_users_for_choice_field'] = (
    model.BasemodelMeta.group_with_users_for_choice_field)
  context['fields_with_foreign_key_to_linkify'] = (
    model.BasemodelMeta.fields_with_foreign_key_to_linkify)
  context['catalog_link_fields'] = model.BasemodelMeta.catalog_link_fields
  if model.BasemodelMeta.catalog_link_fields:
    context['catalog_link_fields_names'] = list(model.BasemodelMeta.catalog_link_fields.keys())
  context['address_type'] = model.BasemodelMeta.address_type
  context['address_mandatory'] = model.BasemodelMeta.address_mandatory
  context['geojson_input'] = model.BasemodelMeta.geojson_input
  context['gpx_input'] = model.BasemodelMeta.gpx_input
  context['postcode_assigner'] = model.BasemodelMeta.postcode_assigner
  context['additional_wms_layers'] = model.BasemodelMeta.additional_wms_layers
  context['additional_wfs_featuretypes'] = model.BasemodelMeta.additional_wfs_featuretypes
  # list of all models
  # which shall be selectable as additional overlay layers in the maps of all form views
  model_list = {}
  app_models = apps.get_app_config('datenmanagement').get_models()
  for app_model in app_models:
    if app_model.BasemodelMeta.as_overlay:
      model_list[app_model.__name__] = app_model._meta.verbose_name_plural
  context['model_list'] = dict(sorted(model_list.items()))
  return context


def add_user_agent_context_elements(context, request):
  """
  adds user agent related elements to the passed context and returns the context

  :param context: context
  :param request: request
  :return: context with user agent related elements added
  """
  user_agent = get_user_agent(request)
  if user_agent.is_mobile or user_agent.is_tablet:
    context['is_mobile'] = True
  else:
    context['is_mobile'] = False
  return context


def assign_widgets(field):
  """
  creates corresponding form field (widget) to passed model field and returns it

  :param field: model field
  :return: corresponding form field (widget) to passed model field
  """
  is_array_field = False
  # field is array field?
  if field.__class__.__name__ == 'ArrayField':
    # override the class of the field by the class of its base field
    field = field.base_field
    is_array_field = True
  form_field = field.formfield()
  # handle array fields with multiple choices
  if issubclass(field.__class__, ChoiceArrayField):
    form_field = field.formfield(empty_value=None, widget=CheckboxSelectMultiple())
  # handle ordinary (single) selects
  elif issubclass(form_field.widget.__class__, Select):
    form_field.widget.attrs['class'] = 'form-select'
  # handle text areas
  elif issubclass(form_field.widget.__class__, Textarea):
    form_field.widget.attrs['class'] = 'form-control'
    form_field.widget.attrs['rows'] = 5
  # handle geometry fields/widgets
  elif is_geometry_field(field.__class__):
    form_field = field.formfield(widget=LeafletWidget())
  elif issubclass(form_field.widget.__class__, TextInput) and field.name == 'farbe':
    form_field = field.formfield(widget=TextInput(attrs={
      'type': 'color',
      'class': 'form-control-color'
    }))
  # handle datetime fields/widgets
  elif issubclass(field.__class__, DateTimeField):
    form_field = field.formfield(widget=TextInput(attrs={
      'type': 'datetime-local',
      'class': 'form-control',
      'step': '1'
    }))
  # handle time fields/widgets
  elif issubclass(field.__class__, TimeField):
    form_field = field.formfield(widget=TextInput(attrs={
      'type': 'time',
      'class': 'form-control',
      'step': '1'
    }))
  # handle date fields/widgets
  elif issubclass(field.__class__, DateField):
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
  # handle other inputs
  else:
    if hasattr(form_field.widget, 'input_type'):
      if form_field.widget.input_type == 'checkbox':
        form_field.widget.attrs['class'] = 'form-check-input'
      else:
        form_field.widget.attrs['class'] = 'form-control'
  # field is array field?
  if is_array_field:
    # highlight corresponding form field as array field via custom HTML attribute
    form_field.widget.attrs['is_array_field'] = 'true'
  return form_field


def delete_object_immediately(request, pk):
  """
  deletes the data object with the passed primary key directly from the database
  and throws a corresponding exception if permissions are missing

  :param request: WSGI request
  :param pk: primary key of the database object to be deleted
  :return: HTTP code 204 (No Content)
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


def get_model_objects(model, subset_id=None, count_only=False):
  """
  either returns all data objects of the passed model or a subset of it

  :param model: model
  :param subset_id: subset ID
  :param count_only: only return the count and not the data objects themselves?
  :return: either all data objects of the passed model or a subset of it
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


def get_uuids_geometries_from_sql(rows):
  """
  returns all UUID (as a list) and all geometries (as a list)
  from the passed result of an SQL query

  :param rows: result of an SQL query
  :return: all UUID (as a list) and all geometries (as a list)
  from the passed result of an SQL query
  """
  uuid_list = []
  geometry_list = []
  for i in range(len(rows)):
    uuid_list.append(rows[i][0])
    geometry_list.append(str(rows[i][1]))
  return uuid_list, geometry_list


def set_form_attributes(form):
  """
  sets attributes in the passed form and returns it

  :param form: form
  :return: passed form with attributes set
  """
  form.fields_with_foreign_key_to_linkify = (
    form.model.BasemodelMeta.fields_with_foreign_key_to_linkify)
  form.choices_models_for_choices_fields = (
    form.model.BasemodelMeta.choices_models_for_choices_fields)
  form.group_with_users_for_choice_field = (
    form.model.BasemodelMeta.group_with_users_for_choice_field)
  return form
