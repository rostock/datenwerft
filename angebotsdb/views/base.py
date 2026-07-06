import logging
from json import loads

from django.apps import apps
from django.http import JsonResponse
from django.template.defaultfilters import date as date_filter
from django.urls import reverse
from django.views import View

from ..models.services import Service

logger = logging.getLogger(__name__)


class JsonView(View):
  """
  Base view for JSON responses
  """

  def render_to_response(self, context, **response_kwargs):
    return JsonResponse(context, **response_kwargs)


def get_model_objects(model, count_only=False):
  """
  returns objects of passed model (or their count)

  For Service models only published objects (status='published') are returned,
  so that drafts and services under review are not visible on the map.

  :param model: model
  :param count_only: count only?
  :return: objects of passed model (or their count)
  """

  is_service_model = not model._meta.abstract and issubclass(model, Service)

  if is_service_model:
    qs = model.objects.filter(status='published')
  else:
    qs = model.objects.all()

  if count_only:
    return qs.count()
  else:
    return qs


def resolve_list_field_value(obj, field_name):
  """
  resolves a ``list_fields`` key to a display string, mirroring the list view
  table rendering (``list.html`` / the ``get_attribute`` template filter) so that
  the map pop-up shows the same values as the list table

  :param obj: object
  :param field_name: ``list_fields`` key (field name, ``__str__`` or special key)
  :return: display string or None for empty values
  """
  if field_name == '__str__':
    return str(obj)

  # choice fields (e.g. status) -> human-readable display value
  display_method = f'get_{field_name}_display'
  try:
    field = obj._meta.get_field(field_name)
  except Exception:
    field = None
  if field is not None and getattr(field, 'choices', None) and hasattr(obj, display_method):
    return getattr(obj, display_method)()

  value = getattr(obj, field_name, None)
  if value in (None, ''):
    return None

  # date fields -> same format as the list table ({{ ...|date:"d.m.Y H:i" }})
  if field_name in ('created_at', 'updated_at'):
    return date_filter(value, 'd.m.Y H:i')

  # ManyToMany / reverse FK -> comma-separated list of items
  if field is not None and (field.many_to_many or field.one_to_many):
    return ', '.join(str(item) for item in value.all())

  return str(value)


def create_geojson_feature(curr_object):
  """
  creates a GeoJSON feature based on passed object and returns it

  :param curr_object: object
  :return: GeoJSON feature based on passed object
  """
  model = curr_object.__class__.__name__.lower()
  pk = curr_object.pk

  # Transform geometry from source SRID to WGS84 (4326) for GeoJSON
  geometry = curr_object.geometry
  if geometry.srid != 4326:
    geometry = geometry.transform(4326, clone=True)

  # Convert geometry to GeoJSON format
  geometry_json = loads(geometry.geojson)

  # define GeoJSON feature:
  # get geometry transformed to WGS84,
  # get (meta) properties directly from object
  geojson_feature = {
    'type': 'Feature',
    'geometry': geometry_json,
    'properties': {
      '_model': model,
      '_pk': pk,
      '_tooltip': str(curr_object),
      '_title': curr_object.__class__._meta.verbose_name,
      '_link_detail': reverse('angebotsdb:' + model + '_detail', args=[pk]),
      '_link_delete': reverse('angebotsdb:' + model + '_delete', args=[pk]),
    },
  }

  # add properties for map pop-up to GeoJSON feature:
  # exactly the fields shown in the list view (list_fields), so that the pop-up
  # and the list table stay in sync (labels = list_fields column headers)
  list_fields = getattr(curr_object, 'list_fields', {})
  for field_name, label in list_fields.items():
    value = resolve_list_field_value(curr_object, field_name)
    if value:
      geojson_feature['properties'][label] = value

  return geojson_feature


class GenericMapDataView(JsonView):
  """
  map data composition view

  :param model: model
  """

  model = None

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    super().__init__(*args, **kwargs)

  def get_context_data(self, **kwargs):
    """
    returns GeoJSON feature collection

    :param kwargs:
    :return: GeoJSON feature collection
    """

    # Always initialize with empty feature collection
    feature_collection = {'type': 'FeatureCollection', 'features': []}
    objects = get_model_objects(self.model, False)

    # handle objects
    if objects:
      for curr_object in objects:
        # only include objects with valid geometry (not default POINT(0 0))
        if hasattr(curr_object, 'geometry') and curr_object.geometry:
          geom = curr_object.geometry
          if geom.x == 0 and geom.y == 0:
            continue
          try:
            feature = create_geojson_feature(curr_object)
            feature_collection['features'].append(feature)
          except Exception as e:
            logger.error(
              'GeoJSON-Feature-Erstellung fehlgeschlagen für %s pk=%s: %s',
              curr_object.__class__.__name__,
              curr_object.pk,
              e,
            )

    return feature_collection

  def get(self, request, *args, **kwargs):
    context = self.get_context_data(**kwargs)
    return self.render_to_response(context)


class CombinedMapDataView(JsonView):
  """
  Kombinierter Map-Endpoint: liefert alle veröffentlichten Services
  mit gültiger Geometrie aus allen konkreten Service-Modellen.
  Neue Service-Modelle werden automatisch eingebunden.
  """

  def get_context_data(self, **kwargs):
    feature_collection = {'type': 'FeatureCollection', 'features': []}
    service_models = [
      m
      for m in apps.get_app_config('angebotsdb').get_models()
      if not m._meta.abstract and issubclass(m, Service)
    ]
    for model in service_models:
      for obj in get_model_objects(model, count_only=False):
        if hasattr(obj, 'geometry') and obj.geometry:
          if obj.geometry.x == 0 and obj.geometry.y == 0:
            continue
          try:
            feature_collection['features'].append(create_geojson_feature(obj))
          except Exception as e:
            logger.error(
              'GeoJSON-Feature-Erstellung fehlgeschlagen für %s pk=%s: %s',
              model.__name__,
              obj.pk,
              e,
            )
    return feature_collection

  def get(self, request, *args, **kwargs):
    return self.render_to_response(self.get_context_data(**kwargs))
