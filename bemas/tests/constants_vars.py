from datetime import date

from django.contrib.gis.geos import Point

DATABASES = {'default', 'bemas'}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'

VALID_DATE = date.today()
VALID_POINT_DB = Point(12.057, 54.158)
VALID_POINT_VIEW = 'SRID=4326;POINT (12.057 54.158)'

INVALID_STRING = 'Worsch´d  supp'

TABLEDATA_VIEW_PARAMS = {'order[0][column]': 0}
