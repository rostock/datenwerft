from json import loads

from django.http import JsonResponse
from django.urls import reverse
from django.views import View

from ..models.services import PreventionService


class JsonView(View):
  """
  Base view for JSON responses
  """

  def render_to_response(self, context, **response_kwargs):
    return JsonResponse(context, **response_kwargs)


def get_model_objects(model, count_only=False):
  """
  returns objects of passed model (or their count)

  :param model: model
  :param count_only: count only?
  :return: objects of passed model (or their count)
  """
  if count_only:
    return model.objects.all().count()
  else:
    return model.objects.all()


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
      '_link_update': reverse('kiju:' + model + '_update', args=[pk]),
      '_link_delete': reverse('kiju:' + model + '_delete', args=[pk]),
    },
  }

  # add properties for map pop-up to GeoJSON feature
  for field in curr_object.__class__._meta.concrete_fields:
    if getattr(curr_object, field.name) and field.name in (
      'id',
      'created_at',
      'updated_at',
      'name',
      'description',
      'email',
      'host',
      'topic',
      'target_group',
    ):
      value = getattr(curr_object, field.name)
      if hasattr(value, '__iter__') and not isinstance(value, str):
        # Handle ManyToMany fields
        geojson_feature['properties'][field.verbose_name] = ', '.join(
          str(item) for item in value.all()
        )
      elif hasattr(value, '__str__'):
        geojson_feature['properties'][field.verbose_name] = str(value)
      else:
        geojson_feature['properties'][field.verbose_name] = value

  # Handle specific fields for different service types
  if isinstance(curr_object, PreventionService):
    for field in ['setting', 'phone', 'costs', 'application_needed']:
      if getattr(curr_object, field):
        geojson_feature['properties'][
          getattr(curr_object.__class__._meta.get_field(field), 'verbose_name', field)
        ] = str(getattr(curr_object, field))

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
    feature_collection, objects = None, None
    objects = get_model_objects(self.model, False)

    # handle objects
    if objects:
      # declare empty GeoJSON feature collection
      feature_collection = {'type': 'FeatureCollection', 'features': []}
      for curr_object in objects:
        # only include objects with valid geometry (not default POINT(0 0))
        if hasattr(curr_object, 'geometry') and curr_object.geometry:
          # skip default/empty geometry
          if curr_object.geometry.wkt == 'POINT (0 0)':
            continue
          # create GeoJSON feature
          feature = create_geojson_feature(curr_object)
          # add GeoJSON feature to GeoJSON feature collection
          feature_collection['features'].append(feature)

    return feature_collection

  def get(self, request, *args, **kwargs):
    context = self.get_context_data(**kwargs)
    return self.render_to_response(context)
