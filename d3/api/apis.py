import base64
from typing import List
from urllib.parse import urlencode
import logging

import requests
from django.core.files.uploadedfile import UploadedFile
from requests import Response

from d3.api import SourceMapping, SourceCategory, ObjectDefinition, ObjectDefinitionPropertyField, SourcePropertyValue, \
  DateiInhalt
from d3.api.responses import Repository, DmsObject, SourceProperty
from datenwerft.secrets import D3_DATEI_CATEGORY
from datenwerft.settings import APPLICATION_HTTP_USER_AGENT, D3_USERNAME, D3_PASSWORD, D3_HOST, D3_AKTEN_CATEGORY, D3_VORGANG_CATEGORY, \
  D3_VORGANGS_TITEL_ID, D3_VORGANGS_TYP_ID

class D3AuthenticationApi:

  logger = logging.getLogger(__name__)

  def lade_access_token(self) -> str | None:
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

    self.logger.debug("Sending request to " + D3_HOST + "/dms/r/ with Headers: " + request_headers.__str__())
    response = requests.get(D3_HOST + "/dms/r/", headers = request_headers)

    if response.status_code >= 400:
      self.logger.error("Authentication failed with status code " + str(response.status_code) + " and message " + response.text)
      raise Exception("Authentication failed with status code " + str(response.status_code) + " and message " + response.text)

    return response.cookies.get("AuthSessionId")

class D3Api:

  logger = logging.getLogger(__name__)

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
      self.logger.error("Repositories konnten nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")
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
      self.logger.error("Default Mappings konnten nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")
      raise Exception("Default Mappings konnten nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    json_response = response.json()
    properties = []
    categories = []

    for json_object in json_response["properties"]:
      properties.append(SourceProperty(json_object["key"], json_object["type"], json_object["displayName"]))

    for json_object in json_response["categories"]:
      categories.append(SourceCategory(json_object["key"], json_object["displayName"]))

    return SourceMapping(json_response["id"], json_response["displayName"], properties, categories)

  def lade_objekt_definitionen(self, repository_id: str, category_id: str) -> ObjectDefinition:
    """
    lade die Objektdefinition von der Kategorie mit der übergebenen id im d3 repositories

    Args:
        repository_id (str): id des repositories
        category_id (str): id der Kategorie

    Returns:
        ObjectDefinition: Objektdefinition der Kategorie
    """
    response = self.__get(f"/dms/r/{repository_id}/objdef", {})

    if response.status_code >= 400:
      self.logger.error("Objekt Definition konnten nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text)
      raise Exception("Objekt Definition konnten nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text)

    json_response = response.json()

    for object_definition_json in json_response["objectDefinitions"]:

      if "uniqueId" not in object_definition_json or object_definition_json["uniqueId"] != category_id:
        continue

      property_fields = []

      for property_json_object in object_definition_json["propertyFields"]:

        propertyDefinition = ObjectDefinitionPropertyField()
        propertyDefinition.id = property_json_object["id"]
        propertyDefinition.uniqueId = property_json_object["uniqueId"]
        propertyDefinition.displayName = property_json_object["displayName"]
        propertyDefinition.isMandatory = property_json_object["isMandatory"]
        propertyDefinition.dataType = property_json_object["dataType"]
        property_fields.append(propertyDefinition)

      object_definition = ObjectDefinition()
      object_definition.id = object_definition_json["id"]
      object_definition.uniqueId = object_definition_json["uniqueId"]
      object_definition.displayName = object_definition_json["displayName"]
      object_definition.writeAccess = object_definition_json["writeAccess"]
      object_definition.objectType = object_definition_json["objectType"]
      object_definition.propertyFields = property_fields

      return object_definition

    raise Exception(f"Objekt Definition für Kategorie {category_id} konnten nicht geladen werden.")

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
      self.logger.error("Akte konnte nicht erstellt werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")
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
      self.logger.error("Akte konnte nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")
      raise Exception("Akte konnte nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    return self.__map_dms_object(response.json())

  def erstelle_vorgang(self, repository_id: str, parent_id: str, name: str | None, vorgangs_typ: str, properties: dict[str, str | List[str]]) -> str:
    """
    erstellt einen neue Vorgang im d3 System

    Args:
      repository_id (str): id des repositories
      parent_id (str | None): id des Elternelements des neuen Vorgangs
      name (str | None): Anzeigename des Vorgangs in d3
      vorgangs_typ (str): Vorgangs type des Vorgangs
      properties (dict[str, str | List[str]): properties des Vorgangs

    Returns:
        DmsObject: neu erstellter Vorgang
    """

    mapped_properties = [
      {"key": D3_VORGANGS_TITEL_ID, "values": [name]}
    ]

    if None != D3_VORGANGS_TYP_ID:
      mapped_properties.append({
        "key": D3_VORGANGS_TYP_ID,
        "values": [vorgangs_typ]
      })

    for key, value in properties.items():

      if isinstance(value, list):
        mapped_properties.append({
          "key": key,
          "values": value,
        })
      else:
        mapped_properties.append({
          "key": key,
          "values": [value],
        })

    json_body = {
      "sourceCategory": D3_VORGANG_CATEGORY,
      "sourceId": f"/dms/r/{repository_id}/source",
      "parentId": parent_id,
      "sourceProperties": {
        "properties": mapped_properties,
      },
    }

    response = self.__post(f"/dms/r/{repository_id}/o2m", json_body)

    if response.status_code >= 400:
      self.logger.error("Vorgang konnte nicht erstellt werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")
      raise Exception("Vorgang konnte nicht erstellt werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    location_header = response.headers.get("Location")

    d3_id_with_query = location_header.replace(f"/dms/r/{repository_id}/o2m/", "")
    query_start = d3_id_with_query.find("?")
    return d3_id_with_query[:query_start]

  def lade_dokument(self, repository_id: str, dokumenten_id: str):
    """
    lädt ein existierendes Dokument aus dem d3 System

    Args:
      repository_id (str): id des repositories
      dokumenten_id (str): id des Dokuments

    Returns:
        DmsObject: Vorgang aus dem d3 System
    """
    response = self.__get(f"/dms/r/{repository_id}/o2m/{dokumenten_id}", {"sourceId": f"/dms/r/{repository_id}/source"})

    if response.status_code >= 400:
      self.logger.error("Dokument konnte nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text)
      raise Exception("Dokument konnte nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text)

    return self.__map_dms_object(response.json())

  def suche_dokumente(self, repository_id: str, vorgangs_id: str) -> list[DmsObject]:
    """
    Suche alle Dateien, die zu dem übergebenen Vorgang gehören

    Args:
      repository_id (str): id des repositories
      vorgangs_id (str): id des Vorgangs

    Returns:
        DmsObject: Vorgang aus dem d3 System
    """

    params = {
      "children_of": vorgangs_id,
      "sourceId": f"/dms/r/{repository_id}/source",
    }

    response = self.__get(f"/dms/r/{repository_id}/srm", params)

    if response.status_code >= 400:
      self.logger.error("Dateien konnten nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text)
      raise Exception("Dateien konnten nicht geladen werden. Status code: " + str(response.status_code) + " Message: " + response.text)

    dateien = []
    for item_json in response.json()["items"]:
      dateien.append(self.__map_dms_object(item_json))

    return dateien

  def lade_datei_hoch(self, repository_id: str, file: UploadedFile) -> str | None:
    """
    Lädt eine Datei in den d3 Repository hoch und gibt anschließend die content uri zurück, damit diese verwendet werden
    kann, um neue DmsObjects anlegen zu können.

    Parameters:
      repository_id (str): id des d3 repositories
      file (UploadedFile): Die Datei die hochgeladen werden soll

    Returns:
      str | None: content_uri der hochgeladenen Datei
    """
    if not file.multiple_chunks():
      response = self.__post_file(f"/dms/r/{repository_id}/blob/chunk/", file)
      return response.headers.get('Location')
    else:
      content_location = None

      for chunk in file.chunks():

        if None == content_location:
          response = self.__post_file(f"/dms/r/{repository_id}/blob/chunk/", chunk)

          if response.status_code >= 400:
            raise Exception("Datei konnte nicht hochgeladen werden. Status code: " + str(response.status_code) + " Message: " + response.text)

          content_location = response.headers.get('Location')
        else:
          response = self.__post_file(content_location, chunk)

          if response.status_code >= 400:
            raise Exception("Datei konnte nicht hochgeladen werden. Status code: " + str(response.status_code) + " Message: " + response.text)

      return content_location

  def erstelle_dokument(self, repository_id: str, parent_id: str, name: str, temp_file_uri: str, properties: dict[str, str | List[str]]) -> str:
    """
    erstellt eine neue Datei im d3 System

    Args:
      repository_id (str): id des repositories
      parent_id (str | None): id des Elternelements der neuen Datei
      name (str): Anzeigename der Datei in d3
      temp_file_uri (str | None): Uri der temp file, für die die Datei erstellt werden soll
      properties (dict[str, str | List[str]): properties der Datei

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
          "values": [value],
        })

    json_body = {
      "sourceId": f"/dms/r/{repository_id}/source",
      "sourceCategory": D3_DATEI_CATEGORY,
      "contentLocationUri": temp_file_uri,
      "filename": name,
      "parentId": parent_id,
      "sourceProperties": {
        "properties": mapped_properties,
      },
    }

    print(json_body)
    response = self.__post(f"/dms/r/{repository_id}/o2m", json_body)

    if response.status_code >= 400:
      self.logger.error("Datei konnte nicht erstellt werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")
      raise Exception("Datei konnte nicht erstellt werden. Status code: " + str(response.status_code) + " Message: " + response.text + "")

    location_header = response.headers.get("Location")

    d3_id_with_query = location_header.replace(f"/dms/r/{repository_id}/o2m/", "")
    query_start = d3_id_with_query.find("?")
    return d3_id_with_query[:query_start]

  def bearbeite_dokument(self, repository_id: str, parent_id: str, d3_id: str | None, name: str | None, temp_file_uri: str | None, properties: dict[str, str | List[str]]) -> str:
    """
    erstellt eine neue Datei im d3 System

    Args:
      repository_id (str): id des repositories
      parent_id (str | None): id des Elternelements der neuen Datei
      d3_id (str | None): Id des Objekts, welches aktualisiert werden soll
      name (str): Anzeigename der Datei in d3
      temp_file_uri (str | None): Uri der temp file, für die die Datei erstellt werden soll
      properties (dict[str, str | List[str]): properties der Datei

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
          "values": [value],
        })

    json_body = {
      "dmsObjectId": d3_id,
      "sourceId": f"/dms/r/{repository_id}/source",
      "sourceCategory": D3_DATEI_CATEGORY,
      "contentLocationUri": temp_file_uri,
      "filename": name,
      "parentId": parent_id,
      "sourceProperties": {
        "properties": mapped_properties,
      },
    }

    if temp_file_uri:
      json_body["alterationText"] = "updated file"

    response = self.__put(f"/dms/r/{repository_id}/o2m/{d3_id}", json_body)

    if response.status_code >= 400:
      self.logger.error("Datei konnte nicht bearbeitet werden. Status code: " + str(response.status_code) + " Message: " + response.text)
      raise Exception("Datei konnte nicht bearbeitet werden. Status code: " + str(response.status_code) + " Message: " + response.text)

    return d3_id

  def lade_datei_inhalt(self, repository_id: str, file_id: str) -> DateiInhalt:
    """
    Lade die Datei mit Inhalt aus dem d3 System.

    Args:
      repository_id (str): id des repositories
      file_id (str): id der Datei deren Inhalt geladen werden soll

    Returns:
        DateiInhalt: geladene Datei aus d3
    """

    file_response = self.__get(f"/dms/r/{repository_id}/o2m/{file_id}", {
      "sourceId": f"/dms/r/{repository_id}/source",
    })

    if file_response.status_code >= 400:
      self.logger.error("Datei konnte nicht geladen werden. Status code: " + str(file_response.status_code) + " Message: " + file_response.text + "")
      raise Exception("Datei konnte nicht geladen werden. Status code: " + str(file_response.status_code) + " Message: " + file_response.text + "")

    content_url = file_response.json()["_links"]["mainblobcontent"]["href"]
    file_name = None
    mime_type = None

    for source_property in file_response.json()["sourceProperties"]:

      if "property_filename" == source_property["key"]:
        file_name = source_property["value"]
      if "property_filemimetype" == source_property["key"]:
        mime_type = source_property["value"]

    content_response = self.__get(content_url, {})

    if content_response.status_code >= 400:
      self.logger.error("Datei Content konnte nicht geladen werden. Status code: " + str(content_response.status_code) + " Message: " + content_response.text + "")
      raise Exception("Datei Content konnte nicht geladen werden. Status code: " + str(content_response.status_code) + " Message: " + content_response.text + "")

    return DateiInhalt(file_name, mime_type, content_response.content)

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

    full_url = self.baseUrl + url + "?" + urlencode(params)

    self.logger.debug("Sending request to " + full_url + " with Headers: " + request_headers.__str__())
    return requests.get(full_url, headers = request_headers, cookies={"AuthSessionId": self.accessToken})

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

    self.logger.debug("Sending request to " + self.baseUrl + url + " with Headers: " + request_headers.__str__() + " and JSON: " + json.__str__())
    return requests.post(self.baseUrl + url, headers = request_headers, json = json, cookies={"AuthSessionId": self.accessToken})

  def __put(self, url: str, json: any) -> Response:
    """
    Methode zum Senden einer HTTP PUT Anfrage an den D3 Webserver.

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

    self.logger.debug("Sending request to " + self.baseUrl + url + " with Headers: " + request_headers.__str__() + " and JSON: " + json.__str__())
    return requests.put(self.baseUrl + url, headers = request_headers, json = json, cookies={"AuthSessionId": self.accessToken})

  def __post_file(self, url: str, file_content) -> Response:
    """
    Methode zum Senden einer HTTP POST Anfrage an den D3 Webserver.

    Args:
      url (str): Relative URL der Anfrage mit führendem /
      file_content (any): Datei-Content der hochgeladen werden soll

    Returns:
      Response: Das HTTP response Objekt, welches die Antwort auf die POST Anfrage des Servers beinhaltet

    Raises:
      RequestException: Raised for underlying errors in obtaining the response.
    """

    request_headers = {
      "User-Agent": APPLICATION_HTTP_USER_AGENT,
      "Accept": "application/json",
      "Content-Type": "application/octet-stream",
    }

    return requests.post(self.baseUrl + url, headers = request_headers, data = file_content, cookies={"AuthSessionId": self.accessToken})

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
      properties.append(SourcePropertyValue(property_json["key"], property_json["value"]))

    return DmsObject(json_object["id"], properties, json_object["sourceCategories"], None, None, None)
