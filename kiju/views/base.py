from json import loads

from django.http import JsonResponse
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView

from ..models.services import HolidayService, PreventionService, Service


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
  # GeoJSON-serialize object
  from django.core.serializers import serialize

  object_geojson_serialized = loads(serialize('geojson', [curr_object]))
  model = curr_object.__class__.__name__.lower()
  pk = curr_object.pk

  # define GeoJSON feature:
  # get geometry from GeoJSON-serialized object,
  # get (meta) properties directly from object
  geojson_feature = {
    'type': 'Feature',
    'geometry': object_geojson_serialized['features'][0]['geometry'],
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
  if isinstance(curr_object, HolidayService):
    for field in ['time', 'maximum_participants', 'costs', 'meeting_point']:
      if getattr(curr_object, field):
        geojson_feature['properties'][
          getattr(curr_object.__class__._meta.get_field(field), 'verbose_name', field)
        ] = str(getattr(curr_object, field))
  elif isinstance(curr_object, PreventionService):
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
        # only include objects with valid geometry
        if hasattr(curr_object, 'geometrie') and curr_object.geometrie:
          # create GeoJSON feature
          feature = create_geojson_feature(curr_object)
          # add GeoJSON feature to GeoJSON feature collection
          feature_collection['features'].append(feature)

    return feature_collection

  def get(self, request, *args, **kwargs):
    context = self.get_context_data(**kwargs)
    return self.render_to_response(context)


class MapView(TemplateView):
  """
  view for map page
  """

  template_name = 'kiju/map.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)

    # add map related information to context
    from django.conf import settings

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

    # add map data URLs for each service type
    context['services_mapdata_url'] = reverse('kiju:service_mapdata')
    context['holiday_services_mapdata_url'] = reverse('kiju:holidayservice_mapdata')
    context['prevention_services_mapdata_url'] = reverse('kiju:preventionservice_mapdata')

    # add filter related information to context
    context['topics'] = list(
      Service.objects.order_by('topic').values_list('topic__name', flat=True).distinct()
    )
    context['target_groups'] = list(
      Service.objects.order_by('target_group')
      .values_list('target_group__name', flat=True)
      .distinct()
    )
    context['hosts'] = list(
      Service.objects.order_by('host').values_list('host__name', flat=True).distinct()
    )

    # add miscellaneous information to context
    services_count = get_model_objects(Service, True)
    holiday_services_count = get_model_objects(HolidayService, True)
    prevention_services_count = get_model_objects(PreventionService, True)
    context['objects_count'] = services_count + holiday_services_count + prevention_services_count

    # define colors for different service types
    context['services_color'] = '#007bff'  # blue
    context['holiday_services_color'] = '#28a745'  # green
    context['prevention_services_color'] = '#ffc107'  # yellow

    return context
