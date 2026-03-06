import logging
import threading

import requests
from requests import Response

from datenwerft.settings import (
  APPLICATION_HTTP_USER_AGENT,
  PYGEOAPI_KEY,
  PYGEOAPI_HOST,
  PYGEOAPI_RESOURCE
)

class PygeoapiApi:
  logger = logging.getLogger(__name__)

  baseUrl: str

  def __init__(self):
    self.baseUrl = PYGEOAPI_HOST

  def reload_configuration(self) -> None:
    """
    Veranlasse das Senden eines POST Request zur PyGeoApi um das neugenerieren der Konfiguration
    zu veranlassen.
    """

    # Der Request and die pygeoapi muss asynchron gesendet werden, da Datenbankänderungen erst
    # mit Abschluss des Requests in gespeichert werden.
    threading.Thread(target=self.send_reload_request, args=()).start()

  def send_reload_request(self) -> None:
    """
    Sende einen POST Request zur PyGeoApi um das neugenerieren der Konfiguration zu veranlassen.

    Request: /processes/{PYGEOAPI_RESOURCE}/execution

    Response: 200
    {
      "inputs": {
          "key": "TestMe"
      },
    }
    """
    request_body = {
      "inputs": {
        "key": PYGEOAPI_KEY
      }
    }
    self.__post(f'/processes/{PYGEOAPI_RESOURCE}/execution', request_body)

  def __post(self, url: str, json: any) -> Response:
    """
    Methode zum Senden einer HTTP POST Anfrage an den Pygeoapi-Webserver.

    Args:
      url (str): Relative URL der Anfrage mit führendem /
      json (any): JSON objekt, welches an den Server gesendet werden soll

    Returns:
      Response: HTTP-Response-Objekt, das die Antwort auf die POST-Anfrage des Servers beinhaltet

    Raises:
      RequestException: Raised for underlying errors in obtaining the response.
    """

    request_headers = {
      'User-Agent': APPLICATION_HTTP_USER_AGENT,
      'Accept': 'application/json',
      'Content-Type': 'application/json',
    }

    self.logger.debug(
      'Sending request to '
      + self.baseUrl
      + url
      + ' with Headers: '
      + request_headers.__str__()
      + ' and JSON: '
      + json.__str__()
    )
    return requests.post(
      self.baseUrl + url,
      headers=request_headers,
      json=json,
    )
