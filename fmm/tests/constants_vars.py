from django.contrib.gis.geos import (
  LinearRing,
  Polygon,
)

DATABASES = {'default', 'fmm'}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'

VALID_POLYGON_DB_A = Polygon(
  LinearRing(
    (307845, 6005103), (307845, 6005105), (307847, 6005105), (307847, 6005103), (307845, 6005103)
  )
)
VALID_POLYGON_DB_B = Polygon(
  LinearRing(
    (308745, 6001503), (308745, 6001505), (308747, 6001505), (308747, 6001503), (308745, 6001503)
  )
)
VALID_STRING_A = 'NJssBauTxVNk'
VALID_STRING_B = 'RdwcOYXoHvZs'
