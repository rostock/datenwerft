import base64
from typing import List
from urllib.parse import urlencode

import requests
from requests import Response

from d3.api import SourceMapping, SourceCategory
from d3.api.responses import Repository, DmsObject, SourceProperty
from datenwerft.settings import APPLICATION_HTTP_USER_AGENT, D3_USERNAME, D3_PASSWORD, D3_HOST, D3_AKTEN_CATEGORY, D3_VORGANG_CATEGORY

class D3AuthenticationApi:

  @staticmethod
  def lade_access_token() -> str | None:
    """
    Methode zum Laden eines Access tokens zur Authentifizierung gegenüber des D3 Backends.

    Rückgabe:
        str | None: AccessToken der Authentifizierung.
    """
    basic_header = base64.b64encode(f"{D3_USERNAME}:{D3_PASSWORD}".encode('ascii'))

    request_headers = {
      "User-Agent": APPLICATION_HTTP_USER_AGENT,
      "Accept": "application/json",
      "Authorization": "Basic " + basic_header.decode('utf-8')
    }

    response = requests.get(D3_HOST + "/dms/r/", headers = request_headers)

    if response.status_code >= 400:
      raise Exception("Authentication failed with status code " + str(response.status_code) + " and message " + response.text)

    return response.cookies.get("AuthSessionId")

class D3Api:

  accessToken: str
  baseUrl: str

  def __init__(self, access_token: str):

    self.accessToken = access_token
    self.baseUrl = D3_HOST

  def suche_repositories(self) -> List[Repository]:
    """
    sucht alle verfügbaren repositories im d3 System

    Returns:
        List[Repository]: Liste der repositories im d3 System
    """
    response = self.__get("/dms/r", {})

    if response.status_code >= 400:
      raise Exception("Repositories konnten nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    json_responses = response.json()
    responses = []

    for json_object in json_responses["repositories"]:
      responses.append(Repository(json_object["id"], json_object["name"]))

    return responses

  def lade_default_mapping(self, repository_id: str) -> SourceMapping:
    """
    lade das standard mapping des d3 repositories

    Returns:
        Source: Source des d3 repositories
    """
    response = self.__get(f"/dms/r/{repository_id}/source", {})

    if response.status_code >= 400:
      raise Exception("Default Mappings konnten nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    json_response = response.json()
    properties = []
    categories = []

    for json_object in json_response["properties"]:
      properties.append(SourceProperty(json_object["key"], json_object["type"], json_object["displayName"]))

    for json_object in json_response["categories"]:
      categories.append(SourceCategory(json_object["key"], json_object["displayName"]))

    return SourceMapping(json_response["id"], json_response["displayName"], properties, categories)

  def erstelle_akte(self, repository_id: str, parent_id: str | None, name: str | None) -> DmsObject:
    """
    erstellt eine neue Akte im d3 System

    Args:
      repository_id (str): id des repositories
      parent_id (str | None): id des Elternelements der neuen Akte
      name (str | None): Anzeigename der akte in d3

    Returns:
        DmsObject: neu erstellt akte
    """

    json_body = {
      "displayValue": name,
      "sourceCategory": D3_AKTEN_CATEGORY,
      "source": f"/dms/r/{repository_id}/source",
      "parentId": parent_id,
    }

    response = self.__post(f"/dms/r/{repository_id}/o2m", json_body)

    if response.status_code >= 400:
      raise Exception("Akte konnte nicht erstellt werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    return self.__map_dms_object(response.json())

  def lade_akte(self, repository_id: str, akten_id: str) -> DmsObject:
    """
    lädt eine existierende Akte aus dem d3 System

    Args:
      repository_id (str): id des repositories
      akten_id (str): id der Akte

    Returns:
        DmsObject: Akte aus dem d3 System
    """

    response = self.__get(f"/dms/r/{repository_id}/o2m/{akten_id}", {})

    if response.status_code >= 400:
      raise Exception("Akte konnte nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    return self.__map_dms_object(response.json())

  def erstelle_vorgang(self, repository_id: str, parent_id: str, name: str | None, properties: dict[str, str | List[str]]) -> DmsObject:
    """
    erstellt einen neue Vorgang im d3 System

    Args:
      repository_id (str): id des repositories
      parent_id (str | None): id des Elternelements des neuen Vorgangs
      name (str | None): Anzeigename des Vorgangs in d3
      properties (dict[str, str | List[str]): properties des Vorgangs

    Returns:
        DmsObject: neu erstellter Vorgang
    """

    mapped_properties = []

    for key, value in properties.items():

      if isinstance(value, list):
        mapped_properties.append({
          "key": key,
          "values": value,
        })
      else:
        mapped_properties.append({
          "key": key,
          "value": value,
        })

    json_body = {
      "displayValue": name,
      "sourceCategory": D3_VORGANG_CATEGORY,
      "source": f"/dms/r/{repository_id}/source",
      "parentId": parent_id,
      "sourceProperties": mapped_properties,
    }

    response = self.__post(f"/dms/r/{repository_id}/o2m", json_body)

    if response.status_code >= 400:

      raise Exception("Vorgang konnte nicht erstellt werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    return self.__map_dms_object(response.json())

  def lade_vorgang(self, repository_id: str, vorgangs_id: str):
    """
    lädt einen existierenden Vorgang aus dem d3 System

    Args:
      repository_id (str): id des repositories
      vorgangs_id (str): id des Vorgangs

    Returns:
        DmsObject: Vorgang aus dem d3 System
    """

    response = self.__get(f"/dms/r/{repository_id}/o2m/{vorgangs_id}", {})

    if response.status_code >= 400:

      raise Exception("Vorgang konnte nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    return self.__map_dms_object(response.json())

  def __get(self, url: str, params: dict[str, str]) -> Response:
    """
    Methode zum Senden einer HTTP GET Anfrage an den D3 Webserver.

    Args:
      url (str): Relative URL der Anfrage mit führendem /

    Returns:
      Response: Das HTTP response Objekt, welches die Antwort auf die GET Anfrage des Servers beinhaltet

    Raises:
      RequestException: Raised for underlying errors in obtaining the response.
    """
    request_headers = {
      "User-Agent": APPLICATION_HTTP_USER_AGENT,
      "Accept": "application/json",
    }

    return requests.get(self.baseUrl + url + "?" + urlencode(params), headers = request_headers, cookies={"AuthSessionId": self.accessToken})

  def __post(self, url: str, json: any) -> Response:
    """
    Methode zum Senden einer HTTP POST Anfrage an den D3 Webserver.

    Args:
      url (str): Relative URL der Anfrage mit führendem /
      json (any): JSON objekt, welches an den Server gesendet werden soll

    Returns:
      Response: Das HTTP response Objekt, welches die Antwort auf die POST Anfrage des Servers beinhaltet

    Raises:
      RequestException: Raised for underlying errors in obtaining the response.
    """

    request_headers = {
      "User-Agent": APPLICATION_HTTP_USER_AGENT,
      "Accept": "application/json",
      "Content-Type": "application/json",
    }

    return requests.post(self.baseUrl + url, headers = request_headers, json = json, cookies={"AuthSessionId": self.accessToken})

  @staticmethod
  def __map_dms_object(json_object: any) -> DmsObject:
    """
    Map ein DmsObject JSON aus der API in ein DmsObject Objekt.

    Args:
      json_object: JSON objekt aus der API

    Returns:
      DmsObject: Das gemappte DmsObject Objekt
    """

    properties = []

    for property_json in json_object["sourceProperties"]:
      properties.append(SourceProperty(property_json["key"], property_json["value"], property_json["values"]))

    return DmsObject(json_object["id"], properties, json_object["sourceCategories"], None, None)
