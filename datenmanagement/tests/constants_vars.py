from datetime import date
from django.contrib.gis.geos import LinearRing, LineString, MultiLineString, \
  MultiPolygon, Point, Polygon
from django.utils import timezone
from pathlib import Path


TEST_DIR = Path(__file__).resolve().parent
TEST_MEDIA_DIR = TEST_DIR / 'temp'

DATABASES = {
  'default',
  'datenmanagement'
}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'

VALID_GPX_FILE = TEST_DIR / 'data' / 'gpx_valid.gpx'
VALID_IMAGE_FILE = TEST_DIR / 'data' / 'image_valid.jpg'
VALID_PDF_FILE = TEST_DIR / 'data' / 'pdf_valid.pdf'
INVALID_GPX_FILE = TEST_DIR / 'data' / 'gpx_invalid.gpx'

VALID_POINT_DB = Point(307845, 6005103)
VALID_POINT_VIEW = 'POINT(12.057 54.158)'
VALID_LINE_DB = LineString((307845, 6005103), (307847, 6005105))
VALID_LINE_VIEW = 'LINESTRING(12.057 54.158, 12.058 54.159)'
VALID_MULTILINE_DB = MultiLineString(VALID_LINE_DB)
VALID_MULTILINE_VIEW = \
  'MULTILINESTRING(' + VALID_LINE_VIEW.replace('LINESTRING', '') + ')'
VALID_POLYGON_DB = Polygon(
  LinearRing(
    (307845, 6005103), (307845, 6005105), (307847, 6005105), (307847, 6005103), (307845, 6005103)
  )
)
VALID_POLYGON_VIEW = 'POLYGON((12.057 54.158, 12.057 54.159, ' \
                     '12.058 54.159, 12.058 54.158, 12.057 54.158))'
VALID_MULTIPOLYGON_DB = MultiPolygon(VALID_POLYGON_DB)
VALID_MULTIPOLYGON_VIEW = 'MULTIPOLYGON(' + VALID_POLYGON_VIEW.replace('POLYGON', '') + ')'

VALID_DATE = date.today()
VALID_DATETIME = timezone.now().replace(second=0, microsecond=0)
INVALID_DECIMAL = -0.01
INVALID_INTEGER = -1
INVALID_EMAIL = 'worsch@supp'
INVALID_STRING = 'Worsch´d  supp'

DATA_VIEW_PARAMS = {
  'order[0][column]': 0
}
GEOMETRY_VIEW_PARAMS = {
  'lat': 54.158,
  'lng': 12.057,
  'rad': 10
}

LIST_VIEW_STRING = 'Liste aller'
MAP_VIEW_STRING = 'Karte aller'
START_VIEW_STRING = 'in Tabelle auflisten'
