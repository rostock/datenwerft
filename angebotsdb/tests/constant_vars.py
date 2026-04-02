from datetime import date

from django.contrib.gis.geos import Point

DATABASES = {'default', 'angebotsdb'}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'
USERNAME_PROVIDER = 'provider_user'
USERNAME_REVIEWER = 'reviewer_user'
USERNAME_NO_ROLE = 'norole_user'

VALID_STRING_A = 'TestEintragAlpha'
VALID_STRING_B = 'TestEintragBeta'
VALID_DATE_A = date(2027, 12, 31)
VALID_DATE_B = date(2028, 6, 30)
VALID_ZIP = 18055
VALID_POINT_DB = Point(307845, 6005103, srid=25833)
