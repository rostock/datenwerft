from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet

from d3.api import D3AuthenticationApi, D3Api
from d3.models import AktenOrdner, Akte, Vorgang
from d3.api import D3AuthenticationApi, D3Api, DmsObject
from d3.models import AktenOrdner, Akte, Metadaten, Vorgang, VorgangMetadaten
from datenwerft.settings import D3_REPOSITORY


def lade_d3_api():
  """
  Initialisiert eine D3Api-Instanz mit einem geladenen Access-Token.

  Zum Initialisieren wird ein access token von der Authentifizierungssystem API geladen.

  Returns:
      D3Api: D3Api Client mit geladenen Access-Token
  """
  access_token = D3AuthenticationApi.lade_access_token()

  return D3Api(access_token)


def lade_akten_ordner(content_type_id: int) -> AktenOrdner | None:
  """
  Lädt den d3 akten ordner für den content type mit der übergebenen id oder None, falls nicht gefunden.

  Parameters:
      content_type_id (int): Identifier des content types.

  Returns:
      AktenOrdner | None: Der Aktenordner für den übergebenem content_type oder None, falls nicht gefunden.
  """
  akte = AktenOrdner.objects.filter(model=content_type_id)

  if akte.count() == 0:
    return None
  else:
    return akte[0]

def lade_oder_erstelle_akte(content_type_id: int, object_id: str, akten_ordner: AktenOrdner) -> Akte:
  """
  Lädt die d3 akte des objekts oder erstellt eine neue falls keine gefunden wurde.

  Parameters:
      content_type_id (int): Identifier des content types.
      object_id (int): Identifier des content Objekts.
      akten_ordner (AktenOrdner): Aktenordner des Content Types.

  Returns:
      Akten: Die Akte für den content type
  """
  geladene_akten = Akte.objects.filter(model=content_type_id, object_id=object_id)
  content_object = ContentType.objects.get_for_id(content_type_id).get_object_for_this_type(uuid=object_id)

  if geladene_akten.count() == 0:

    api = lade_d3_api()
    d3_akte = api.erstelle_akte(D3_REPOSITORY, akten_ordner.d3_id, content_object.__str__())

    akte = Akte()
    akte.d3_id = d3_akte.id,
    akte.object_id = object_id
    akte.model = content_type_id
    akte.save()
    return akte
  else:
    return geladene_akten[0]


def fetch_processes(content_type_id: int, object_id: str) -> list[Vorgang]|None:

  file = load_file(content_type_id, object_id)

  if file:

    processes = load_processes(file.id)
    if processes:

      return processes

  return None


def load_file(content_type_id: int, object_id: str) -> Akte | None:
  """
  Lädt die d3 akte des objekts oder None, falls keine gefunden wurde.

  Parameters:
      content_type_id (int): Identifier des content types.
      object_id (int): Identifier des content Objekts.

  Returns:
      Akte | None: Die Akte für den content type oder None, falls nicht gefunden.
  """
  files = Akte.objects.filter(model=content_type_id, object_id=object_id)

  if files.count() == 0:
    return None
  else:
    return files[0]


def load_processes(akten_id:int) -> QuerySet[Vorgang]|None:
    """
    Lädt alle Vorgänge für die übergebene Akten ID.

    Parameters:
        akten_id (int): Identifier der Akte.

    Returns:
        list[Vorgang]: Liste der Vorgänge für die Akte.
    """

    processes = Vorgang.objects.filter(akten_id=akten_id)

    if processes.count() == 0:
      return None
    else:
      return processes


def lade_d3_properties() -> list[tuple[str, str]]:
  """
  lade alle d3 properties und gebe sie als list von tuple zurück, wobei der erste Wert der Key des properties
  in d3 entspricht und der zweite Wert der Anzeigenamen des properties.

  Returns:
      list[tuple[str, str]]: liste von properties als tuple
  """
  api = lade_d3_api()
  source = api.lade_default_mapping(D3_REPOSITORY)

  source_properties = []

  for source_property in source.properties:

    source_properties.append((source_property.key, source_property.displayName))

  return source_properties

def erstelle_vorgang(vorgang: Vorgang, vorgang_metadaten: list[VorgangMetadaten], metadaten: QuerySet[Metadaten]) -> DmsObject:
  """
  Erstellt einen neuen Vorgang im D3 DMS mit den Daten aus dem Vorgang und deren Metadaten.

  Args:
      vorgang (Vorgang): Vorgang für welchen ein neues DMS-Objekt erstellt werden soll.
      vorgang_metadaten (list[VorgangMetadaten]): Liste der Metadaten des Vorgangs
      metadaten (QuerySet[Metadaten]): Liste alle Metadaten aus der Datenbank

  Returns:
      DmsObject: The newly created document management system object for the process.
  """
  properties = {}

  for metadaten_feld in metadaten:

    wert = None

    for metadaten_wert in vorgang_metadaten:

      if metadaten_wert.metadaten == metadaten_feld:
        wert = metadaten_wert.wert
        break

    if metadaten_feld.d3_id and wert:
      properties[metadaten_feld.d3_id] = wert

  api = lade_d3_api()
  return api.erstelle_vorgang(D3_REPOSITORY, vorgang.akten.d3_id, vorgang.titel, properties)

def lade_alle_metadaten():
  """
  lade alle metadaten felder aus der Datenbank für Vorgänge

  Returns:
      QuerySet[Metadaten]: Ein QuerySet welches alle Daten aus der Metadaten Tabelle enthält
  """
  return Metadaten.objects.all()
