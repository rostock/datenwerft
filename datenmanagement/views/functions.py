from decimal import Decimal
from django.apps import apps
from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.db.models.fields import DateField, DateTimeField, DecimalField, TimeField
from django.forms import CheckboxSelectMultiple, Select, TextInput, Textarea
from django.http import HttpResponse, Http404, StreamingHttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django_user_agents.utils import get_user_agent
from json import JSONEncoder
from leaflet.forms.widgets import LeafletWidget
from pathlib import Path
from re import sub
from wsgiref.util import FileWrapper

from .fields import ArrayDateField, ArrayDecimalField
from toolbox.models import Subsets
from toolbox.utils import is_geometry_field
from toolbox.vcpub.DataBucket import DataBucket
from datenmanagement.models.fields import ChoiceArrayField
from datenmanagement.models.base import Basemodel


class DecimalEncoder(JSONEncoder):
  def default(self, obj):
    if isinstance(obj, Decimal):
      return str(obj)
    return super().default(obj)


def add_basic_model_context_elements(context, model):
  """
  adds basic model related elements to the passed context and returns the context

  :param context: context
  :param model: model
  :return: context with basic model related elements added
  """
  model_name = model.__name__
  context['model_name'] = model_name
  context['model_name_lower'] = model_name.lower()
  context['model_verbose_name_plural'] = model._meta.verbose_name_plural
  context['model_description'] = model.BasemodelMeta.description
  context['model_is_editable'] = model.BasemodelMeta.editable
  context['model_geometry_type'] = model.BasemodelMeta.geometry_type
  context['model_pk_field_name'] = model._meta.pk.name
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
  context['forms_in_high_zoom_mode'] = model.BasemodelMeta.forms_in_high_zoom_mode
  context['forms_in_high_zoom_mode_default_aerial'] = (
    model.BasemodelMeta.forms_in_high_zoom_mode_default_aerial)
  if model.BasemodelMeta.forms_in_high_zoom_mode:
    context['leaflet_config_overrides'] = {
      'MAX_ZOOM': 21
    }
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
  context['address_search_class'] = model.BasemodelMeta.address_search_class
  context['address_search_long_results'] = model.BasemodelMeta.address_search_long_results
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
  context['default_overlays'] = model.BasemodelMeta.default_overlays
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


def assign_object_value(request, pk):
  """
  assigns passed value to passed field of the database object with the passed primary key
  and throws a corresponding exception if permissions are missing

  :param request: WSGI request
  :param pk: primary key of the affected database object
  :return: HTTP code 204 (No Content)
  """
  model_name = sub('^.*/', '', sub('/assign.*$', '', request.path_info))
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  obj = get_object_or_404(model, pk=pk)
  if request.user.has_perm('datenmanagement.change_' + model_name.lower()):
    if request.GET.get('field'):
      field, value = request.GET.get('field'), request.GET.get('value')
      if value:
        if model._meta.get_field(field).remote_field:
          value = model._meta.get_field(field).remote_field.model.objects.get(pk=value)
        setattr(obj, field, value)
      else:
        setattr(obj, field, None)
      obj.save()
  else:
    raise PermissionDenied()
  return HttpResponse(status=204)


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
  # handle decimal array fields/widgets
  elif issubclass(field.__class__, DecimalField) and is_array_field:
    label = form_field.label
    step = 10 ** -field.decimal_places
    form_field = ArrayDecimalField(
      label=label,
      widget=TextInput(
        attrs={
          'type': 'number',
          'class': 'form-control',
          'step': step
        }
      )
    )
    form_field.required = False
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
    '^.*/', '', sub('/deleteimmediately.*$', '', request.path_info)
  )
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  obj = get_object_or_404(model, pk=pk)
  if request.user.has_perm('datenmanagement.delete_' + model_name.lower()):
    obj.delete()
  else:
    raise PermissionDenied()
  return HttpResponse(status=204)


def download_pointcloud(pk):
  """
  view, which routes the download request to the right file.

  :param pk: primary key of the requested pointcloud
  :return:
  """
  # get pointcloud model instance of given pk
  pc_model = apps.get_model(app_label='datenmanagement', model_name='Punktwolken')
  pc_instance = pc_model.objects.get(pk=pk)

  # check if pointcloud is stored at VCPub
  if pc_instance.vcp_object_key:
    # get project instance of pointcloud instance for bucket information
    pcprj_model = apps.get_model(app_label='datenmanagement', model_name='Punktwolken_Projekte')
    pcprj_instance = pcprj_model.objects.get(pk=pc_instance.projekt.uuid)

    # get dataset bucket
    bucket = DataBucket(_id=pcprj_instance.vcp_dataset_bucket_id)
    print(f'Object Key: {pc_instance.vcp_object_key}')
    ok, response = bucket.download_file(object_key=str(pc_instance.vcp_object_key), stream=True)
    if ok:
      print(f"Content Type: {response.headers.get('Content-Type')}")
      file_response = StreamingHttpResponse(
        response.raw,
        content_type='application/octet-stream',
        as_attachment=True,
        filename=pc_instance.dateiname
      )
      file_response['Content-Length'] = pc_instance.file_size
      print(f'Response: {file_response.__dict__}')
      return file_response
    elif response.status_code == 404:
      raise Http404("No Point Cloud.")
    else:
      return HttpResponse(response)
  else:
    file_path = Path(f'{settings.MEDIA_ROOT}/{pc_instance.punktwolke}')
    f = open(file_path, 'rb')
    file_response = StreamingHttpResponse(
      FileWrapper(f), content_type='application/octet-stream')
    file_response['Content-Disposition'] = f'attachment; filename={pc_instance.dateiname}'
    file_response['Content-Length'] = file_path.stat().st_size
    print(f'Response: {file_response.__dict__}')
    return file_response


def get_model_objects(model, subset_id=None, count_only=False):
  """
  either returns all data objects of the passed model or a subset of it

  :param model: model
  :param subset_id: subset ID
  :param count_only: only return the count and not the data objects themselves?
  :return: either all data objects of the passed model or a subset of it
  """
  if subset_id is not None:
    subset_id = subset_id if isinstance(subset_id, int) else int(subset_id)
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


def get_url_back(referer, fallback, lazy=False):
  """
  returns URL used for buttons leading "back" (to somewehere)
  and/or used in case of successfully submitted forms

  :param referer: referer
  :param fallback: fallback
  :param lazy: lazy?
  :return: URL used for buttons leading "back" (to somewehere)
  and/or used in case of successfully submitted forms
  """
  if referer and '/add_another' not in referer and '/delete' not in referer:
    return referer
  return reverse_lazy(fallback) if lazy else reverse(fallback)


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


def handle_multi_file_upload(form, multi_field_name):
  """
  handles multi file upload for the passed form

  :param form: form
  :param multi_field_name: name of multi file upload field
  """
  # only carry out any further operations if all mandatory fields have been filled in,
  # otherwise the transfer will not work for the other objects
  if all(
      field.name == form.model._meta.pk.name
      or field.name == multi_field_name
      or not form.fields[field.name].required
      or form.data[field.name]
      for field in form.model._meta.get_fields()
  ):
    files = form.multi_files.getlist(multi_field_name)
    if len(files) > 1:
      for file in files[:-1]:  # exclude the last file from this loop
        m = form.model()
        for field in form.model._meta.get_fields():
          if field.name == 'dateiname_original':
            setattr(m, field.name, file.name)
          elif field.name == multi_field_name:
            setattr(m, field.name, file)
          elif field.name != m._meta.pk.name:
            setattr(m, field.name, form.cleaned_data[field.name])
        m.save()


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


def set_form_template(model: Basemodel):
  """
  sets adequate form template for passed model and returns it

  :param model: model
  :return: adequate form template for passed model
  """
  if (
    model.__module__ == 'datenmanagement.models.models_codelist'
    or model.BasemodelMeta.geometry_type is None
  ):
    return 'datenmanagement/form-list.html'
  elif model.__name__ == 'Punktwolken_Projekte':
    return 'datenmanagement/form-pcmanagement.html'
  else:
    return 'datenmanagement/form-map.html'
