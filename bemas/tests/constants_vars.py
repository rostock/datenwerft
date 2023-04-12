from django.contrib.gis.geos import Point


DATABASES = {
  'default',
  'bemas'
}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'

VALID_POINT_DB = Point(307845, 6005103)
VALID_POINT_VIEW = 'POINT(12.057 54.158)'

INVALID_STRING = 'Worsch´d  supp'

TABLEDATA_VIEW_PARAMS = {
  'order[0][column]': 0
}
