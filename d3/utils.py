from django.contrib.contenttypes.models import ContentType

from d3.api import D3AuthenticationApi, D3Api
from d3.models import AktenOrdner, Akte
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

def lade_akte(content_type_id: int, object_id: str, akten_ordner: AktenOrdner) -> Akte:
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
