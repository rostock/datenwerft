from django.db import models
from django.utils.translation import gettext_lazy as _


class GeometryType(models.TextChoices):
  """
  geometry type (Geometrietyp)
  """

  POINT = 'Point', _('Point')
  MULTIPOINT = 'MultiPoint', _('MultiPoint')
  LINESTRING = 'LineString', _('LineString')
  MULTILINESTRING = 'MultiLineString', _('MultiLineString')
  POLYGON = 'Polygon', _('Polygon')
  MULTIPOLYGON = 'MultiPolygon', _('MultiPolygon')
  GEOMETRYCOLLECTION = 'GeometryCollection', _('GeometryCollection')


class ProcessingType(models.TextChoices):
  """
  processing type (Verarbeitungstyp)
  """

  DIRECTLY = 'directly', _('direkt (z.B. mittels einer API)')
  AUTOMATICALLY = 'automatically', _('automatisch (z.B. mittels Shell-Skript)')
  MANUALLY = 'manually', _('manuell')


class RepositoryType(models.TextChoices):
  """
  repository type (Typ eines Speicherorts)
  """

  INTERFACE = 'interface', _('Schnittstelle (z.B. eine API)')
  DATABASE = 'database', _('Datenbank')
  FILE = 'file', _('Datei(en)')


class ServiceType(models.TextChoices):
  """
  service type (Typ eines Services)
  """

  GEORSS = 'OGC:GeoRSS 1.0', _('GeoRSS')
  API_FEATURES = 'OGC:OGC API - Features', _('OGC API – Features')
  SOS = 'OGC:SOS 2.0.0', _('SOS')
  TMS = 'OGC:TMS 1.0.0', _('TMS')
  WCS = 'OGC:WCS 2.0', _('WCS')
  WFS = 'OGC:WFS 2.0', _('WFS')
  WMS = 'OGC:WMS 1.3.0', _('WMS')
  WMTS = 'OGC:WMTS 1.0.0', _('WMTS')


class UnitOfMeasurement(models.TextChoices):
  """
  unit of measurement (Maßeinheit)
  """

  METERS = 'm', _('Meter')
