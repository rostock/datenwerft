from datenwerft.secrets import FME_GEOJSON_URL, FME_GEOJSON_TOKEN, FME_GPX_URL, FME_GPX_TOKEN
from django.apps import apps
from django.db import connections
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View
from django.views.generic.base import TemplateView
from json import dumps
from jsonview.views import JsonView
from requests import post as requests_post

from datenmanagement.models.base import Codelist, ComplexModel, Metamodel
from datenmanagement.utils import user_has_model_permissions_any, \
  user_has_model_permissions_change_delete_view
from .functions import add_basic_model_context_elements, get_uuids_geometries_from_sql


class GeometryView(JsonView):
  """
  view for querying the geometries of the passed model

  the following parameters can be provided for filtering:
  * lat, lng, (rad): coordinates of a point (EPSG:4326) and radius
  * pk: primary key of a database object

  :param model: model
  """

  model = None

  def __init__(self, model=None):
    self.model = model
    super().__init__()

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    context['model_name'] = self.model.__name__
    # if the primary key of a database object was passed as a parameter...
    if self.request.GET.get('pk'):
      pk = self.request.GET.get('pk')
      with connections['datenmanagement'].cursor() as cursor:
        cursor.execute(
          'SELECT uuid, ST_AsText(ST_Transform(geometrie, 4326)) FROM ' +
          self.model._meta.db_table.replace('"', '') + ' WHERE uuid = %s;',
          [pk]
        )
        uuid, geom = cursor.fetchone()  # tuple
        context['uuid'] = uuid
        context['geometry'] = geom
    # if the coordinates of a point (EPSG:4326) were passed as parameters...
    elif self.request.GET.get('lat') and self.request.GET.get('lng'):
      lat, lng = float(self.request.GET.get('lat')), float(self.request.GET.get('lng'))
      # radius defaults to zero unless passed as a parameter
      rad = float(self.request.GET.get('rad')) if self.request.GET.get('rad') else 0
      with connections['datenmanagement'].cursor() as cursor:
        cursor.execute(
          'SELECT uuid, ST_AsText(ST_Transform(geometrie, 4326)) FROM ' +
          self.model._meta.db_table.replace('"', '') +
          ' WHERE ST_Buffer(ST_Transform(ST_SetSRID(' +
          'ST_MakePoint(%s, %s),4326)::geometry,25833),%s) && geometrie;',
          [lng, lat, rad]
        )
        uuids_geometries = get_uuids_geometries_from_sql(cursor.fetchall())
        context['uuids'] = uuids_geometries[0]
        context['object_list'] = uuids_geometries[1]
    else:
      with connections['datenmanagement'].cursor() as cursor:
        cursor.execute(
          'SELECT uuid, ST_AsText(ST_Transform(geometrie, 4326)) FROM ' +
          self.model._meta.db_table.replace('"', '') + ';',
          []
        )
        uuids_geometries = get_uuids_geometries_from_sql(cursor.fetchall())
        context['uuids'] = uuids_geometries[0]
        context['object_list'] = uuids_geometries[1]
    return context


class GISFiletoGeoJSON(View):
  """
  view for passing a file to FME Server and returning the generated GeoJSON
  """
  http_method_names = ['post']

  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    """
    ``dispatch()`` is called via ``GISFiletoGeoJSON.as_view()`` in ``urls.py``;
    ``dispatch()`` forwards to ``post()`` since a POST request has been executed

    :param request: request
    :param args:
    :param kwargs:
    :return:
    """
    return super().dispatch(request, *args, **kwargs)

  @csrf_exempt
  def post(self, request, *args, **kwargs):
    """
    ``post()`` is called automatically by ``dispatch()``

    :param request: request
    :param args:
    :param kwargs:
    :return: GeoJSON response or FME Server error response
    """
    file, url, token, content_type = None, '', '', ''
    if 'geojson' in request.FILES.keys():
      file = request.FILES['geojson']
      url = FME_GEOJSON_URL
      token = FME_GEOJSON_TOKEN
      content_type = 'application/geo+json'
    elif 'gpx' in request.FILES.keys():
      file = request.FILES['gpx']
      url = FME_GPX_URL
      token = FME_GPX_TOKEN
      content_type = 'application/gpx+xml'
    post = requests_post(
        url=url,
        headers={
          'Authorization': token,
          'Content-Type': content_type,
          'Accept': 'application/geo+json'
        },
        data=file
    )
    if post.status_code != 200:
      response = {
        'status_code': str(post.status_code),
        'error_log': str(post.text)
      }
      return JsonResponse(status=post.status_code, data=dumps(response), safe=False)
    else:
      return JsonResponse(data=post.json())


class IndexView(TemplateView):
  """
  view for main page
  """

  template_name = 'datenmanagement/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    models_meta, models_codelist, models_complex, models_simple = [], [], [], []
    models = apps.get_app_config('datenmanagement').get_models()
    for model in models:
      if user_has_model_permissions_any(self.request.user, model):
        model_name = model.__name__
        model_dict = {
          'name': model_name,
          'verbose_name_plural': model._meta.verbose_name_plural,
          'description': model.BasemodelMeta.description,
          'url_start': reverse('datenmanagement:' + model_name + '_start')
        }
        if issubclass(model, Metamodel):
          models_meta.append(model_dict)
        elif issubclass(model, Codelist):
          models_codelist.append(model_dict)
        elif issubclass(model, ComplexModel):
          models_complex.append(model_dict)
        else:
          models_simple.append(model_dict)
    context = super().get_context_data(**kwargs)
    context['models_meta'] = models_meta
    context['models_codelist'] = models_codelist
    context['models_complex'] = models_complex
    context['models_simple'] = models_simple
    return context


class StartView(TemplateView):
  """
  view for entry page of a model

  :param model: model
  """

  model = None
  template_name = 'datenmanagement/start.html'

  def __init__(self, model=None):
    self.model = model
    super().__init__()

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    model_name = self.model.__name__
    model_name_lower = model_name.lower()
    context = super().get_context_data(**kwargs)
    # add basic model related elements to context
    context = add_basic_model_context_elements(context, self.model)
    if (
        self.model.BasemodelMeta.editable
        and self.request.user.has_perm('datenmanagement.add_' + model_name_lower)
    ):
      context['url_model_add'] = reverse('datenmanagement:' + model_name + '_add')
    if user_has_model_permissions_change_delete_view(self.request.user, self.model):
      context['url_model_list'] = reverse('datenmanagement:' + model_name + '_list')
      if self.model.BasemodelMeta.geometry_type:
        context['url_model_map'] = reverse('datenmanagement:' + model_name + '_map')
    context['url_back'] = reverse('datenmanagement:index')
    return context


class AddAnotherView(TemplateView):
  """
  view for page for creating another object of a model, based on the object just created

  :param model: model
  """

  model = None
  template_name = 'datenmanagement/add_another.html'

  def __init__(self, model=None):
    self.model = model
    super().__init__()

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add basic model related elements to context
    context = add_basic_model_context_elements(context, self.model)
    context['object'] = self.request.session.get('object_just_created', None)
    pk = self.request.session.get('object_just_created_pk', None)
    context['url_yes'] = reverse('datenmanagement:' + self.model.__name__ + '_change', args=[pk])
    context['url_no'] = self.request.session.get('original_url_back', None)
    return context
