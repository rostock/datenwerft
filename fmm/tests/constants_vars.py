from django.contrib.gis.geos import (
  LinearRing,
  MultiPolygon,
  Polygon,
)

DATABASES = {'default', 'fmm'}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'

VALID_MULTIPOLYGON_DB_A = MultiPolygon(
  Polygon(
    LinearRing(
      (307845, 6005103), (307845, 6005105), (307847, 6005105), (307847, 6005103), (307845, 6005103)
    )
  )
)
VALID_MULTIPOLYGON_DB_B = MultiPolygon(
  Polygon(
    LinearRing(
      (308745, 6001503), (308745, 6001505), (308747, 6001505), (308747, 6001503), (308745, 6001503)
    )
  )
)
VALID_STRING_A = 'NJssBauTxVNk'
VALID_STRING_B = 'RdwcOYXoHvZs'
