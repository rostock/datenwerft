from django.db import models
from django.utils.translation import gettext_lazy as _


class GeometryType(models.TextChoices):
  """Enum für Geometrietypen."""

  POINT = 'Point', _('Point')
  LINESTRING = 'LineString', _('LineString')
  POLYGON = 'Polygon', _('Polygon')
  MULTIPOINT = 'MultiPoint', _('MultiPoint')
  MULTILINESTRING = 'MultiLineString', _('MultiLineString')
  MULTIPOLYGON = 'MultiPolygon', _('MultiPolygon')
  GEOMETRYCOLLECTION = 'GeometryCollection', _('GeometryCollection')


class ProcessingType(models.TextChoices):
  """Enum für Verarbeitungstypen."""

  DIRECTLY = 'directly', _('directly')
  AUTOMATICALLY = 'automatically', _('automatically')
  MANUALLY = 'manually', _('manually')


class RepositoryType(models.TextChoices):
  """Enum für Repository-Typen."""

  INTERFACE = 'interface', _('interface')
  DATABASE = 'database', _('database')
  FILE = 'file', _('file')


class ServiceType(models.TextChoices):
  """Enum für Diensttypen."""

  GEORSS_1_0 = 'OGC:GeoRSS 1.0', _('OGC:GeoRSS 1.0')
  API_FEATURES = 'OGC:OGC API - Features', _('OGC:OGC API - Features')
  SOS_2_0_0 = 'OGC:SOS 2.0.0', _('OGC:SOS 2.0.0')
  TMS_1_0_0 = 'OGC:TMS 1.0.0', _('OGC:TMS 1.0.0')
  WCS_2_0 = 'OGC:WCS 2.0', _('OGC:WCS 2.0')
  WFS_2_0 = 'OGC:WFS 2.0', _('OGC:WFS 2.0')
  WMS_1_3_0 = 'OGC:WMS 1.3.0', _('OGC:WMS 1.3.0')
  WMTS_1_0_0 = 'OGC:WMTS 1.0.0', _('OGC:WMTS 1.0.0')


class UnitOfMeasurement(models.TextChoices):
  """Enum für Maßeinheiten."""

  METERS = 'm', _('m')
