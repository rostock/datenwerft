from django.conf import settings

ADMIN_GROUP = getattr(settings, 'ANGEBOTSDB_ADMIN_GROUP_NAME', 'angebotsdb_admin')
USERS_GROUP = getattr(settings, 'ANGEBOTSDB_USERS_GROUP_NAME', 'angebotsdb_user')
