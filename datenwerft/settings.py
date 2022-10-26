import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Application definition

DATENMANAGEMENT_VERSION = '5.6.0'

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DJANGO_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django.contrib.gis',
]

LOCAL_APPS = [
  'datenmanagement',
]

THIRD_PARTY_APPS = [
  'django_user_agents',
  'guardian',
  'leaflet',
  'requests',
  'rest_framework',
  'jsonview',
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS + THIRD_PARTY_APPS

LOGIN_URL = '/datenwerft/accounts/login'

MIDDLEWARE = [
  'django.middleware.security.SecurityMiddleware',
  'django.contrib.sessions.middleware.SessionMiddleware',
  'django.middleware.common.CommonMiddleware',
  'django.middleware.csrf.CsrfViewMiddleware',
  'django.contrib.auth.middleware.AuthenticationMiddleware',
  'django.contrib.messages.middleware.MessageMiddleware',
  'django.middleware.clickjacking.XFrameOptionsMiddleware',
  'django.middleware.gzip.GZipMiddleware',
  'django_user_agents.middleware.UserAgentMiddleware',
  'django_currentuser.middleware.ThreadLocalUserMiddleware',
]

ROOT_URLCONF = 'datenwerft.urls'

WSGI_APPLICATION = 'datenwerft.wsgi.application'

# Security

CSRF_COOKIE_SECURE = False

SECURE_BROWSER_XSS_FILTER = True

SECURE_CONTENT_TYPE_NOSNIFF = True

X_FRAME_OPTIONS = 'DENY'

# Leaflet

LEAFLET_CONFIG = {
  'SPATIAL_EXTENT': (10.53001, 52.98541, 14.68873, 54.82175),
  'DEFAULT_CENTER': (54.14775, 12.14945),
  'DEFAULT_ZOOM': 11,
  'MIN_ZOOM': 11,
  'MAX_ZOOM': 19,
  'TILES': [],
  'SRID': 3857,
  'ATTRIBUTION_PREFIX': '',
  'RESET_VIEW': False,
  'PLUGINS': {
    'forms': {
      'auto_include': True
    },
    'geoman': {
      'css': 'leaflet-geoman/leaflet-geoman.css',
      'js': 'leaflet-geoman/leaflet-geoman.min.js',
      'auto_include': True
    },
    'locatecontrol': {
      'css': 'leaflet-locatecontrol/L.Control.Locate.min.css',
      'js': 'leaflet-locatecontrol/L.Control.Locate.min.js',
      'auto_include': True
    },
    'markercluster': {
      'css': [
        'leaflet-markercluster/MarkerCluster.css',
        'leaflet-markercluster/MarkerCluster.Default.css'
      ],
      'js': 'leaflet-markercluster/leaflet.markercluster.js',
      'auto_include': True
    }
  }
}

# REST framework

REST_FRAMEWORK = {
  'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAdminUser',
  ],
  'DATETIME_FORMAT': 'iso-8601',
  'DATE_FORMAT': 'iso-8601',
  'TIME_FORMAT': 'iso-8601',
  'DEFAULT_RENDERER_CLASSES': (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer',
  ),
}

# Static files (CSS, JavaScript, Images)

STATICFILES_DIRS = (
  os.path.join(BASE_DIR, 'vendor/'),
  ('bootstrap', os.path.join(BASE_DIR, 'node_modules/bootstrap/dist/css')),
  ('bootstrap', os.path.join(BASE_DIR, 'node_modules/bootstrap/dist/js')),
  ('fontawesome', os.path.join(
    BASE_DIR,
    'node_modules/@fortawesome/fontawesome-free/css'
  )),
  ('fontawesome', os.path.join(
    BASE_DIR,
    'node_modules/@fortawesome/fontawesome-free/js'
  )),
  ('webfonts', os.path.join(
    BASE_DIR,
    'node_modules/@fortawesome/fontawesome-free/webfonts'
  )),
  ('jquery', os.path.join(BASE_DIR, 'node_modules/jquery/dist')),
  ('leaflet-geoman', os.path.join(
    BASE_DIR,
    'node_modules/@geoman-io/leaflet-geoman-free/dist'
  )),
  ('leaflet-locatecontrol', os.path.join(
    BASE_DIR,
    'node_modules/leaflet.locatecontrol/dist'
  )),
  ('leaflet-markercluster', os.path.join(
    BASE_DIR,
    'node_modules/leaflet.markercluster/dist'
  )),
  ('martinez-polygon-clipping', os.path.join(
    BASE_DIR,
    'node_modules/martinez-polygon-clipping/dist'
  )),
  ('popperjs', os.path.join(BASE_DIR, 'node_modules/@popperjs/core/dist/umd')),
  ('proj4', os.path.join(BASE_DIR, 'node_modules/proj4/dist')),
  ('proj4leaflet', os.path.join(BASE_DIR, 'node_modules/proj4leaflet/src')),
  ('wicket', os.path.join(BASE_DIR, 'node_modules/wicket')),
  ('hilfe', os.path.join(BASE_DIR, 'hilfe/build/html')),
)

# Internationalization

LANGUAGE_CODE = 'de'

TIME_ZONE = 'Europe/Berlin'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Link auf Konfigurationsdatei mit weiteren Parametern,
# die nicht unter Git-Versionskontrolle fallen sollen

try:
  from datenwerft.secrets import *
except ImportError:
  pass
