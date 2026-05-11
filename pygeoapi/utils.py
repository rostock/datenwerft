from django.core.exceptions import ObjectDoesNotExist
from django.db import OperationalError
from django.db.backends.base.base import BaseDatabaseWrapper
from django.db.utils import ConnectionHandler

from datenwerft.settings import PYGEOAPI_HOST
from pygeoapi.api.apis import PygeoapiApi
from pygeoapi.models import DatabaseConnection


def create_database_connection(database_connection_id) -> BaseDatabaseWrapper | None:
  """
  creates and returns a new database connection by means of the passed database connection ID

  :param database_connection_id: database connection ID
  :return: new database connection by means of the passed database connection ID
  :raises ObjectDoesNotExist: if database connection object does not exist
  :raises OperationalError: if database connection fails
  """
  try:
    db = DatabaseConnection.objects.get(id=database_connection_id)
    db_settings = {
      'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db.dbname,
        'USER': db.user,
        'PASSWORD': db.password,
        'HOST': db.host,
        'PORT': str(db.port),
        'CONN_MAX_AGE': 0,  # disable persistent connections
      }
    }
    # create temporary connection handler
    handler = ConnectionHandler(db_settings)
    # get connection
    connection = handler['default']
    # explicitly establish connection now
    connection.ensure_connection()
    return connection
  except (ObjectDoesNotExist, OperationalError):
    return None


def reload_pygeoapi() -> None:
  """
  triggers a reload of the pygeoapi web server configuration
  """
  if not PYGEOAPI_HOST:
    return None
  api = PygeoapiApi()
  api.reload_configuration()
  return None
