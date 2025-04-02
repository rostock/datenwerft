from datetime import date

from django.contrib.gis.geos import LinearRing, Point, Polygon
from django.utils import timezone

DATABASES = {'default', 'antragsmanagement'}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'

VALID_DATE = date.today()
VALID_DATETIME = timezone.now()
VALID_EMAIL = 'deborah.feinman@gov.il'
VALID_FIRST_NAME = 'Deborah'
VALID_LAST_NAME = 'Feinman'
VALID_POINT_DB = Point(12.057, 54.158)
VALID_POINT_VIEW = 'SRID=4326;POINT (12.057 54.158)'
VALID_POLYGON_DB = Polygon(
  LinearRing(
    (307845, 6005103), (307845, 6005105), (307847, 6005105), (307847, 6005103), (307845, 6005103)
  )
)
VALID_POLYGON_VIEW = (
  'POLYGON((12.057 54.158, 12.057 54.159, 12.058 54.159, 12.058 54.158, 12.057 54.158))'
)
VALID_STRING = 'Consetetur'
VALID_TELEPHONE = '+1 206 555 0199'
VALID_TEXT = 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam.'
