from django.conf import settings

GROUP = getattr(settings, 'PYGEOAPI_GROUP_NAME', 'pygeoapi')

# default upper bound of the column list a reconcile accepts, raisable per
# deployment via PYGEOAPI_MAX_COLUMNS; see docs/pygeoapi/rechtesystem.md
MAX_COLUMNS_DEFAULT = 100


def max_columns():
  return getattr(settings, 'PYGEOAPI_MAX_COLUMNS', MAX_COLUMNS_DEFAULT)
