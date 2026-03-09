from datenwerft.settings import PYGEOAPI_HOST
from pygeoapi.api.apis import PygeoapiApi


def reload_pygeoapi() -> None:
  """
  Veranlasse das neuladen der Konfiguration des Pygeoapi-Webservers.
  """
  if not PYGEOAPI_HOST:
    return None

  api = PygeoapiApi()
  api.reload_configuration()

  return None
