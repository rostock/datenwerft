class SourceProperty:

  key: str
  propertyType: str
  displayName: str

  def __init__(self, key: str, property_type: str, display_name: str):

    self.key = key
    self.propertyType = property_type
    self.displayName = display_name

class SourceCategory:

  key: str
  displayName: str

  def __init__(self, key: str, display_name: str):

    self.key = key
    self.displayName = display_name

class SourcePropertyValue:

  key: str
  value: str
  values: dict[str, str]

  def __init__(self, key: str, value: str, values: dict[str, str] | None):

    self.key = key
    self.value = value
    self.values = values

class Repository:

  id: str
  name: str

  def __init__(self, id: str, name: str):

    self.id = id
    self.name = name

class SourceMapping:

  id: str
  displayName: str
  properties: list[SourceProperty]
  categories: list[SourceCategory]

  def __init__(self, id: str, display_name: str, properties: list[SourceProperty], categories: list[SourceCategory]):

    self.id = id
    self.displayName = display_name
    self.properties = properties
    self.categories = categories

class DmsObject:

  id: str
  sourceProperties: list[SourcePropertyValue]
  sourceCategories: list[str]
  mainBlobUrl: str | None
  pdfBlobUrl: str | None
  notes: str | None

  def __init__(self, id: str, source_properties: list[SourcePropertyValue], source_categories: list[str], main_blob_url: str | None, pdf_blob_url: str | None, notes: str = None):

    self.id = id
    self.sourceProperties = source_properties
    self.sourceCategories = source_categories
    self.mainBlobUrl = main_blob_url
    self.pdfBlobUrl = pdf_blob_url
    self.notes = notes
