import logging
import redis
from datetime import date, datetime, timezone
from django.conf import settings
from django.contrib.gis.db.models.fields import LineStringField as ModelLineStringField
from django.contrib.gis.db.models.fields import MultiLineStringField as ModelMultiLineStringField
from django.contrib.gis.db.models.fields import MultiPolygonField as ModelMultiPolygonField
from django.contrib.gis.db.models.fields import PointField as ModelPointField
from django.contrib.gis.db.models.fields import PolygonField as ModelPolygonField
from django.contrib.gis.forms.fields import LineStringField as FormLineStringField
from django.contrib.gis.forms.fields import MultiLineStringField as FormMultiLineStringField
from django.contrib.gis.forms.fields import MultiPolygonField as FormMultiPolygonField
from django.contrib.gis.forms.fields import PointField as FormPointField
from django.contrib.gis.forms.fields import PolygonField as FormPolygonField
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.geos import Point, Polygon
from django.db.models import Q
from itertools import groupby
from lxml import etree
from operator import itemgetter
from re import match, search, sub
from requests import post
from zoneinfo import ZoneInfo


logger = logging.getLogger(__name__)


def concat_address(street=None, house_number=None, postal_code=None, place=None):
  """
  concats passed address string parts and returns address string

  :param street: street name
  :param house_number: house number
  :param postal_code: postal code
  :param place: place
  :return: address string
  """
  first_part = (street + ' ' if street else '') + (house_number if house_number else '')
  second_part = (postal_code + ' ' if postal_code else '') + (place if place else '')
  if first_part and second_part:
    return first_part.strip() + ', ' + second_part.strip()
  elif first_part:
    return first_part.strip()
  elif second_part:
    return second_part.strip()
  else:
    return None


def find_in_wfs_features(string, search_element, wfs_features):
  """
  returns true if passed search string is found in passed search element of passed WFS features

  :param string: search string
  :param search_element: WFS feature search element
  :param wfs_features: WFS features
  :return: true if passed search string is found in passed search element of passed WFS features
  """
  for wfs_feature in wfs_features:
    properties = wfs_feature.get('properties', {})
    if properties.get(search_element) == string:
      return True
  return False


def format_date_datetime(value, time_string_only=False):
  """
  formats date or datetime and returns appropriate date, datetime or time only string

  :param value: date or datetime
  :param time_string_only: time string only?
  :return: appropriate date, datetime or time only string
  """
  # format datetimes
  if isinstance(value, datetime):
    value_tz = value.replace(tzinfo=timezone.utc).astimezone(ZoneInfo(settings.TIME_ZONE))
    if time_string_only:
      return value_tz.strftime('heute, %H:%M Uhr')
    else:
      return value_tz.strftime('%d.%m.%Y, %H:%M Uhr')
  # format dates
  elif isinstance(value, date):
    return value.strftime('%d.%m.%Y')
  else:
    return value


def format_filesize(size_in_bytes: int) -> str:
  """
  formats filesize in bytes (int) to the right format with unit.

  :param size_in_bytes: filesize in bytes
  :type size_in_bytes: int
  :return: filesize in the right format with unit
  :rtype: str
  """
  units = ["Bytes", "KB", "MB", "GB", "TB"]
  size = size_in_bytes
  unit_index = 0

  while size >= 1024 and unit_index < len(units) - 1:
    size /= 1024.0
    unit_index += 1

  return f"{size:.2f} {units[unit_index]}"


def get_array_first_element(curr_array):
  """
  returns first element of passed array

  :param curr_array: array
  :return: first element of passed array
  """
  if curr_array is not None and len(curr_array) > 0 and curr_array[0] is not None:
    return curr_array[0]
  else:
    return curr_array


def get_overlapping_area(area_a, area_b, entity_value):
  """
  intersects passed areas a and b and returns overlapping area (as a dictionary)

  :param area_a: area a
  :param area_b: area b
  :param entity_value: value for 'entity' key of return overlapping area dictionary
  :return: overlapping area (as a dictionary) of intersected passed areas a and b
  """
  # make sure that SRID of area a equals SRID of area b
  area_a = transform_geometry(geometry=area_a, target_srid=area_b.srid)
  return {
    'entity': entity_value,
    'area': area_a.intersection(area_b).area
  }


def group_dict_by_key_and_sum_values(curr_dict, group_key, sum_value):
  """
  groups passed dictionary by passed key, sums up passed sum values for each key,
  and returns summed values

  :param curr_dict: dictionary
  :param group_key: key to group by
  :param sum_value: value to sum up for key
  :return: summed values for each group-by-key of passed dictionary, grouped by passed key
  """
  # sort passed dictionary by passed key to ensure groupby works correctly
  sorted_data = sorted(curr_dict, key=itemgetter(group_key))
  # use groupby to group data by passed key
  grouped_data = groupby(sorted_data, key=itemgetter(group_key))
  summed_values = {}
  for key, group in grouped_data:
    # sum passed sum values for each group
    summed = sum(item[sum_value] for item in group)
    summed_values[key] = summed
  return summed_values


def intersection_with_wfs(geometry, wfs_config, only_presence=False):
  """
  intersects passed feature geometry with passed WFS config and returns (presence of) hits

  :param geometry: feature geometry
  :param wfs_config: WFS config (including URL, namespace, namespace URL, feature type, and SRID)
  :param only_presence: presence of intersection hits instead of intersection hits?
  :return: (presence of) intersection hits of passed feature geometry with passed WFS config
  """
  # unpack WFS config into variables using dictionary unpacking
  url, namespace, namespace_url, featuretype, srid = wfs_config.values()
  # transform feature geometry to WFS SRID
  geometry = transform_geometry(geometry, srid)
  # build geometry part for WFS Intersection filter
  if isinstance(geometry, Point):
    coords = f"{geometry.x} {geometry.y}"
    geometry_filter = f'''
      <gml:Point srsName="EPSG:{srid}">
        <gml:pos>{coords}</gml:pos>
      </gml:Point>
    '''
  elif isinstance(geometry, Polygon):
    coords = ' '.join(f"{coord[0]} {coord[1]}" for coord in geometry.coords[0])
    geometry_filter = f'''
      <gml:Polygon srsName="EPSG:{srid}">
        <gml:exterior>
          <gml:LinearRing>
            <gml:posList>{coords}</gml:posList>
          </gml:LinearRing>
        </gml:exterior>
      </gml:Polygon>
    '''
  else:
    geometry_filter = ''
  # build WFS Intersection filter
  filter_string = f'''
  <wfs:GetFeature service="WFS" version="2.0.0" outputFormat="application/geo+json"
                  xmlns:wfs="http://www.opengis.net/wfs/2.0"
                  xmlns:ogc="http://www.opengis.net/ogc"
                  xmlns:gml="http://www.opengis.net/gml/3.2"
                  xmlns:{namespace}="{namespace_url}">
    <wfs:Query typeNames="{namespace}:{featuretype}">
      <ogc:Filter>
        <ogc:Intersects>
          <ogc:PropertyName>geometry</ogc:PropertyName>
          {geometry_filter}
        </ogc:Intersects>
      </ogc:Filter>
    </wfs:Query>
  </wfs:GetFeature>
  '''
  # parse the WFS Intersection filter string to an XML element
  # and then convert it back to a string to ensure it's well-formed
  filter_element = etree.fromstring(filter_string)
  filter_xml = etree.tostring(filter_element).decode('utf-8')
  # get WFS response
  response = post(
    url=url,
    data=filter_xml,
    headers={'Content-Type': 'text/xml'}
  )
  geojson_data = response.json()
  features = geojson_data.get('features', [])
  return len(features) > 0 if only_presence else features


def is_geometry_field(field):
  """
  checks if passed field is a geometry related field

  :param field: field
  :return: passed field is a geometry related field?
  """
  if (
      issubclass(field, FormLineStringField)
      or issubclass(field, ModelLineStringField)
      or issubclass(field, FormMultiLineStringField)
      or issubclass(field, ModelMultiLineStringField)
      or issubclass(field, FormMultiPolygonField)
      or issubclass(field, ModelMultiPolygonField)
      or issubclass(field, FormPointField)
      or issubclass(field, ModelPointField)
      or issubclass(field, FormPolygonField)
      or issubclass(field, ModelPolygonField)
  ):
    return True
  else:
    return False


def optimize_datatable_filter(search_element, search_column, qs_params_inner):
  """
  optimizes datatables queryset filter based on passed parameters

  :param search_element: search element
  :param search_column: search column
  :param qs_params_inner: queryset parameters
  :return: optimized datatables queryset filter based on passed parameters
  """
  case_a = search('^[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}$', search_element)
  case_b = search('^[0-9]{2}\\.[0-9]{4}$', search_element)
  case_c = search('^[0-9]{2}\\.[0-9]{2}$', search_element)
  if case_a or case_b or case_c:
    search_element_splitted = search_element.split('.')
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): (search_element_splitted[
            2] + '-' if case_a else '') +
        search_element_splitted[1] + '-' +
        search_element_splitted[0]
    }
  elif search_element == 'ja':
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): 'true'
    }
  elif search_element == 'nein' or search_element == 'nei':
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): 'false'
    }
  elif match(r"^[0-9]+,[0-9]+$", search_element):
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): sub(',', '.', search_element)
    }
  else:
    kwargs = {
        '{0}__{1}'.format(search_column, 'icontains'): search_element
    }
  q = Q(**kwargs)
  return qs_params_inner | q if qs_params_inner else q


def transform_geometry(geometry, target_srid):
  """
  transform passed feature geometry to passed target SRID and return it
  or return passed feature geometry untransformed

  :param geometry: feature geometry
  :param target_srid: target SRID
  :return: passed feature geometry either transformed to passed target SRID or untransformed
  """
  source_srid = geometry.srid
  if source_srid != target_srid:
    source_srs = SpatialReference(source_srid)
    target_srs = SpatialReference(target_srid)
    transform = CoordTransform(source_srs, target_srs)
    geometry.transform(transform)
  return geometry


def is_broker_available():
  """
  checks if the broker is available
  :return: True if the broker is available, False otherwise
  :rtype: bool
  """
  try:
    # Erstelle eine Redis-Verbindung
    r = redis.Redis.from_url(url=f'redis://{settings.RQ_QUEUES["default"]["HOST"]}')
    # Versuche, einen Ping an Redis zu senden
    r.ping()
    return True
  except redis.ConnectionError as e:
    logger.critical(f'Redis is not available: {e}')
    return False
