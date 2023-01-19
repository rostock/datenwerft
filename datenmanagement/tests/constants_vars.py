from django.contrib.gis.geos import LinearRing, LineString, MultiPolygon, Point, Polygon
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent

DATABASES = {
  'default',
  'datenmanagement'
}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'

VALID_GPX_FILE = TEST_DIR / 'data' / 'gpx_valid.gpx'
VALID_PDF_FILE = TEST_DIR / 'data' / 'pdf_valid.pdf'
INVALID_GPX_FILE = TEST_DIR / 'data' / 'gpx_invalid.gpx'

VALID_POINT_DB = Point(307845, 6005103)
VALID_POINT_VIEW = 'POINT(12.057 54.158)'
VALID_LINESTRING_DB = LineString((307845, 6005103), (307847, 6005105))
VALID_LINESTRING_VIEW = 'LINESTRING(12.057 54.158, 12.058 54.159)'
VALID_POLYGON_DB = Polygon(
  LinearRing(
    (307845, 6005103), (307845, 6005105), (307847, 6005105), (307847, 6005103), (307845, 6005103)
  )
)
VALID_POLYGON_VIEW = 'POLYGON((12.057 54.158, 12.057 54.159, ' \
                     '12.058 54.159, 12.058 54.158, 12.057 54.158))'
VALID_MULTIPOLYGON_DB = MultiPolygon(VALID_POLYGON_DB)
VALID_MULTIPOLYGON_VIEW = 'MULTIPOLYGON(' + VALID_POLYGON_VIEW + ')'

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
