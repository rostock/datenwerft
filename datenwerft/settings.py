from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


# Datenwerft.HRO:
# global application definition

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
DJANGO_APPS = [
  'django.contrib.admin',
  'django.contrib.auth',
  'django.contrib.contenttypes',
  'django.contrib.sessions',
  'django.contrib.messages',
  'django.contrib.staticfiles',
  'django.contrib.gis',
]
THIRD_PARTY_APPS = [
  'django_user_agents',
  'leaflet',
  'requests',
  'rest_framework',
  'jsonview',
]
LOCAL_APPS = [
  'accounts',
  'toolbox',
  'datenmanagement',
  'antragsmanagement',
  'bemas',
  'metadatenmanagement'
]
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS
LOGIN_REDIRECT_URL = '/'
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
]
ROOT_URLCONF = 'datenwerft.urls'
WSGI_APPLICATION = 'datenwerft.wsgi.application'
TEMPLATES = [
  {
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [
      BASE_DIR / 'datenwerft/templates',
      BASE_DIR / 'accounts/templates',
      BASE_DIR / 'datenmanagement/templates',
      BASE_DIR / 'antragsmanagement/templates',
      BASE_DIR / 'bemas/templates'
    ],
    'APP_DIRS': True,
    'OPTIONS': {
      'context_processors': [
        'django.template.context_processors.debug',
        'django.template.context_processors.request',
        'django.contrib.auth.context_processors.auth',
        'django.contrib.messages.context_processors.messages',
        'datenwerft.context_processors.include_login_form',
      ],
      'libraries': {
        'toolbox_tags': 'toolbox.tags',
        'datenmanagement_tags': 'datenmanagement.tags',
        'antragsmanagement_tags': 'antragsmanagement.tags',
        'bemas_tags': 'bemas.tags'
      },
    },
  },
]


# Datenwerft.HRO:
# databases

DATABASE_ROUTERS = [
  'datenwerft.db_routers.DatabaseRouter'
]


# Datenwerft.HRO:
# authentication

AUTHENTICATION_BACKENDS = (
  'accounts.backend.DatenwerftAuthBackend',
  'django.contrib.auth.backends.ModelBackend',
)


# Datenwerft.HRO:
# security

CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'


# Datenwerft.HRO:
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


# Datenwerft.HRO:
# REST framework

REST_FRAMEWORK = {
  'DEFAULT_PERMISSION_CLASSES': [
    'rest_framework.permissions.IsAuthenticated'
  ],
  'DATETIME_FORMAT': 'iso-8601',
  'DATE_FORMAT': 'iso-8601',
  'TIME_FORMAT': 'iso-8601',
  'DEFAULT_RENDERER_CLASSES': (
    'rest_framework.renderers.JSONRenderer',
    'rest_framework.renderers.BrowsableAPIRenderer'
  )
}


# Datenwerft.HRO:
# global static files, static files of external libraries
# and static help files

STATICFILES_DIRS = (
  BASE_DIR / 'vendor/',
  ('bootstrap', BASE_DIR / 'node_modules/bootstrap/dist/css'),
  ('bootstrap', BASE_DIR / 'node_modules/bootstrap/dist/js'),
  ('fontawesome', BASE_DIR / 'node_modules/@fortawesome/fontawesome-free/css'),
  ('fontawesome', BASE_DIR / 'node_modules/@fortawesome/fontawesome-free/js'),
  ('webfonts', BASE_DIR / 'node_modules/@fortawesome/fontawesome-free/webfonts'),
  ('jquery', BASE_DIR / 'node_modules/jquery/dist'),
  ('leaflet-geoman', BASE_DIR / 'node_modules/@geoman-io/leaflet-geoman-free/dist'),
  ('leaflet-locatecontrol', BASE_DIR / 'node_modules/leaflet.locatecontrol/dist'),
  ('leaflet-markercluster', BASE_DIR / 'node_modules/leaflet.markercluster/dist'),
  ('martinez-polygon-clipping', BASE_DIR / 'node_modules/martinez-polygon-clipping/dist'),
  ('popperjs', BASE_DIR / 'node_modules/@popperjs/core/dist/umd'),
  ('proj4', BASE_DIR / 'node_modules/proj4/dist'),
  ('proj4leaflet', BASE_DIR / 'node_modules/proj4leaflet/src'),
  ('select2', BASE_DIR / 'node_modules/select2/dist/css'),
  ('select2', BASE_DIR / 'node_modules/select2/dist/js'),
  ('select2-bootstrap-5-theme', BASE_DIR / 'node_modules/select2-bootstrap-5-theme/dist'),
  ('wicket', BASE_DIR / 'node_modules/wicket'),
  ('hilfe', BASE_DIR / 'hilfe/build/html'),
  ('css', BASE_DIR / 'datenwerft/static/css'),
  ('img', BASE_DIR / 'datenwerft/static/img')
)


# Datenwerft.HRO:
# internationalization (i18n) and localization (l10n)

LANGUAGE_CODE = 'de'
TIME_ZONE = 'Europe/Berlin'
USE_I18N = True
USE_TZ = True


# Antragsmanagement app:
# icons

ANTRAGSMANAGEMENT_ICONS = {
  'authority': 'landmark',
  'back': 'backward-step',
  'cancel': 'hand',
  'email': 'envelope',
  'error': 'circle-exclamation',
  'next': 'forward-step',
  'ok': 'circle-check',
  'save': 'floppy-disk',
  'update': 'pen',
  'warning': 'triangle-exclamation'
}


# BEMAS app:
# icons

BEMAS_ICONS = {
  'activity': 'bell',
  'address': 'house',
  'address_to_map': 'location-dot',
  'anonymous_complaint': 'link-slash',
  'back': 'backward-step',
  'cancel': 'hand',
  'clone': 'clone',
  'codelist': 'list',
  'complaint': 'folder-open',
  'contact': 'address-card',
  'create': 'circle-plus',
  'created': 'plus',
  'delete': 'trash',
  'deleted': 'minus',
  'error': 'circle-exclamation',
  'event': 'paperclip',
  'filter_off': 'filter-circle-xmark',
  'filter_on': 'filter',
  'index': 'backward-fast',
  'info': 'circle-info',
  'logentry': 'clock-rotate-left',
  'map': 'map-location-dot',
  'map_with_filter': 'map-location',
  'ok': 'circle-check',
  'organization': 'building',
  'originator': 'industry',
  'originator_without_operator': 'question',
  'orphaned_data': 'ghost',
  'person': 'user',
  'save': 'floppy-disk',
  'show_on_map': 'map',
  'statistics': 'chart-simple',
  'table': 'table',
  'update': 'pen',
  'updated': 'pen',
  'warning': 'triangle-exclamation'
}


# BEMAS app:
# colors

BEMAS_COLORS = {
  'complaint': '#b85814',
  'originator': '#3d8f8f'
}


# Toolbox app:
# PDF export

PDF_ESCAPE = [
  ('&', r'\&'),
  (chr(8211), '--')
]
PDF_JINJASTRINGS = {
  'block_start': r'\JINJA{',
  'block_end': '}',
  'variable_start': r'\VAR{',
  'variable_end': '}',
  'comment_start': r'\JCMNT{',
  'comment_end': '}'
}


# configuration file with additional parameters
# which must not fall under Git version control

try:
  from datenwerft.secrets import *
except ImportError:
  pass
