import ldap

from django_auth_ldap.config import GroupOfNamesType, LDAPSearch
from pathlib import Path

BASE_DIR_CUSTOM = Path(__file__).resolve().parent.parent


# Datenwerft.HRO:
# global application definition

DEBUG = True
INSTANCE_STATUS = 'DEVEL'  # PRODUCTION | TESTING | DEVEL
SECRET_KEY = 'abcdefghijklmnopqrstuvwxyz0123456789-#(!$&%abcdefg'
ALLOWED_HOSTS = [
  'datenwerft.hro.localhost',
  'localhost',
  '127.0.0.1',
  '::1'
]
CSRF_TRUSTED_ORIGINS = [
  'http://datenwerft.hro.localhost'
]

LOGIN_REDIRECT_URL = '/'
LOGIN_URL = '/datenwerft/accounts/login/'


# Datenwerft.HRO:
# reverse proxy settings

# USE_X_FORWARDED_HOST = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


# Datenwerft.HRO:
# logging configuration
# log levels available: DEBUG, INFO, WARNING, ERROR, CRITICAL

LOGGING = {
  'version': 1,
  'disable_existing_loggers': False,
  'handlers': {
    'console': {
      'class': 'logging.StreamHandler',
      'level': 'WARNING'
    },
    'datenmanagement-file': {
      'class': 'logging.FileHandler',
      'filename': 'logs/datenmanagement.log',
      'level': 'WARNING'
    },
    'celery-file': {
      'class': 'logging.FileHandler',
      'filename': 'logs/celery.log',
      'level': 'WARNING'
    },
    'VCPub-file': {
      'class': 'logging.FileHandler',
      'filename': 'logs/VCPub.log',
      'level': 'WARNING'
    },
    'error-file': {
      'class': 'logging.FileHandler',
      'filename': 'logs/error.log',
      'level': 'ERROR'
    }
  },
  'loggers': {
    '': {
      'handlers': ['console', 'error-file'],
      'level': 'WARNING'
    },
    'datenmanagement': {
      'handlers': ['console', 'datenmanagement-file'],
      'level': 'WARNING'
    },
    'celery': {
      'handlers': ['console', 'celery-file'],
      'level': 'WARNING'
    },
    'VCPub': {
      'handlers': ['console', 'VCPub-file'],
      'level': 'WARNING'
    }
  }
}


# Datenwerft.HRO:
# databases

DATABASES = {
  'default': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'datenwerft',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'db',
    'PORT': '5432'
  },
  'antragsmanagement': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'NAME': 'antragsmanagement',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'db',
    'PORT': '5432'
  },
  'bemas': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'NAME': 'bemas',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'db',
    'PORT': '5432'
  },
  'datenmanagement': {
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'NAME': 'datenmanagement',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'db',
    'PORT': '5432'
  },
  'gdihrometadata': {
    'ENGINE': 'django.db.backends.postgresql',
    'NAME': 'gdihrometadata',
    'USER': 'postgres',
    'PASSWORD': 'postgres',
    'HOST': 'db',
    'PORT': '5432'
  }
}
POSTGIS_VERSION = (3, 5, 0)


# Accounts app:
# authentication

AUTH_LDAP_EXTENSION_INTERNAL_IP_ADDRESSES = [
  '10.0.0.0/8',
  '172.16.0.0/12',
  '192.168.0.0/16'
]

AUTH_LDAP_EXTENSION_ACCESS_TOKEN_LIFETIME = 300
AUTH_LDAP_GLOBAL_OPTIONS = {
  ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER
}
AUTH_LDAP_SERVER_URI = 'ldap://localhost:1389'
AUTH_LDAP_BIND_DN = 'cn=admin,dc=example,dc=org'
AUTH_LDAP_BIND_PASSWORD = 'password'
AUTH_LDAP_ALWAYS_UPDATE_USER = True
AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
  'ou=Abteilung,ou=Amt,o=Stadt',
  ldap.SCOPE_SUBTREE,
  '(objectClass=groupOfNames)'
)
AUTH_LDAP_GROUP_TYPE = GroupOfNamesType()
AUTH_LDAP_REQUIRE_GROUP = None
AUTH_LDAP_USER_SEARCH = LDAPSearch(
  'o=Stadt',
  ldap.SCOPE_SUBTREE,
  '(uid=%(user)s)'
)
AUTH_LDAP_USER_ATTR_MAP = {
  'first_name': 'givenName',
  'last_name': 'sn',
  'email': 'mail'
}


# Antragsmanagement app:
# authentication

ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME = 'antragsmanagement_requester'
ANTRAGSMANAGEMENT_AUTHORITY_GROUPS_NAMES = [
  'antragsmanagement_authority_1',
  'antragsmanagement_authority_2'
]
ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME = 'antragsmanagement_admin'


# BEMAS app:
# authentication

BEMAS_ADMIN_GROUP_NAME = 'bemas_admins'
BEMAS_USERS_GROUP_NAME = 'bemas_users'


# BEMAS app:
# data privacy

BEMAS_STATUS_CHANGE_DEADLINE_DAYS = 365


# GDI.HRO Metadata app:
# authentication

GDIHROMETADATA_GROUP_NAME = 'gdihrometadata'


# Datenwerft.HRO:
# email

DEFAULT_FROM_EMAIL = 'webmaster@localhost'
EMAIL_HOST = 'smtp'


# Datenwerft.HRO:
# static files (CSS, JavaScript, images)

STATIC_URL = '/datenwerft/static/'
STATIC_ROOT = BASE_DIR_CUSTOM / 'static'


# Datenwerft.HRO:
# upload files

MEDIA_URL = '/datenwerft/uploads/'
MEDIA_ROOT = BASE_DIR_CUSTOM / 'uploads'
PC_MEDIA_URL = '/datenwerft/uploads/punktwolken'
PC_MEDIA_ROOT = BASE_DIR_CUSTOM / 'uploads/punktwolken'


# Datenmanagement app:
# upload files

PDF_PATH_PREFIX_PUBLIC = 'public/pdf/'
PDF_PATH_PREFIX_PRIVATE = 'private/pdf/'
PHOTO_PATH_PREFIX_PUBLIC = 'public/photos/'
PHOTO_PATH_PREFIX_PRIVATE = 'private/photos/'
PC_PATH_PREFIX_PUBLIC = ''
PC_PATH_PREFIX_PRIVATE = ''


# Toolbox app:
# address search

ADDRESS_SEARCH_URL = 'https://geo.sv.rostock.de/geocodr/query?'
ADDRESS_SEARCH_KEY = '00000000000000000000000000000000'  # this key is valid!
REVERSE_SEARCH_RADIUS = 200  # m


# Toolbox app:
# OWS proxy

OWS_PROXY_PROXIES = {
  'http': 'http://1.2.3.4:8080',
  'https': 'http://1.2.3.4:8090'
}


# Datenmanagement app:
# FME Server

FME_GEOJSON_URL = 'https://geo.sv.rostock.de/fmedatastreaming/converters/geojson2geojson.fmw'
FME_GEOJSON_TOKEN = 'fmetoken token=abcdefghijklmnopqrstuvwxyz0123456789-#(!'
FME_GPX_URL = 'https://geo.sv.rostock.de/fmedatastreaming/converters/gpx2geojson.fmw'
FME_GPX_TOKEN = 'fmetoken token=abcdefghijklmnopqrstuvwxyz0123456789-#(!'


# Datenmanagement app:
# VC Publisher

PYBLISHER = {
  'host': 'https://vcpublisher.your-domain.tld',
  'api_version': 'v1',
  'user': 'username',
  'password': 'password',
  'project_id': '<project id>',
}


# Datenwerft.HRO:
# Django-RQ configuration

RQ_QUEUES = {
  'default': {
    'HOST': 'localhost',
    'PORT': 6379,
    'DB': 0,
    'DEFAULT_TIMEOUT': 360,
  }
}


# Datenwerft.HRO:
# relevant only for development environments under Microsoft Windows

#GDAL_LIBRARY_PATH = ''
"""
example:

GDAL_LIBRARY_PATH = 'C:\\Program Files\\QGIS 3.28.2\\bin\\gdal306.dll'
"""
#GEOS_LIBRARY_PATH = ''
"""
example:

GEOS_LIBRARY_PATH = 'C:\\Program Files\\QGIS 3.28.2\\bin\\geos_c.dll'
"""