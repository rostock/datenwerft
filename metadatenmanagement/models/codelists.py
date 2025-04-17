from .abstract import Codelist  # Importiere die abstrakte Basisklasse

# ------------- Codelisten-Modelle -------------
# Alle erben von der abstrakten Klasse Codelist


class Access(Codelist):
  """Modell für Zugriffsrechte."""

  # Erbt alle Felder von Codelist


class AssetType(Codelist):
  """Modell für Asset-Typen."""


class Charset(Codelist):
  """Modell für Zeichensätze."""


class Crs(Codelist):
  """Modell für Koordinatenreferenzsysteme (CRS)."""


class DatathemeCategory(Codelist):
  """Modell für Datenthema-Kategorien."""


class Format(Codelist):
  """Modell für Datenformate."""


class Frequency(Codelist):
  """Modell für Aktualisierungshäufigkeiten."""


class HashType(Codelist):
  """Modell für Hash-Typen."""


class HvdCategory(Codelist):
  """Modell für Hochwertige Daten (HVD) Kategorien."""


class InspireServiceType(Codelist):
  """Modell für INSPIRE Diensttypen."""


class InspireSpatialScope(Codelist):
  """Modell für INSPIRE räumliche Geltungsbereiche."""


class InspireTheme(Codelist):
  """Modell für INSPIRE Themen."""


class Language(Codelist):
  """Modell für Sprachen."""


class License(Codelist):
  """Modell für Lizenzen."""


class MimeType(Codelist):
  """Modell für MIME-Typen."""


class PoliticalGeocoding(Codelist):
  """Modell für politische Geokodierungen."""


class PoliticalGeocodingLevel(Codelist):
  """Modell für Ebenen der politischen Geokodierung."""


class SpatialRepresentationType(Codelist):
  """Modell für räumliche Repräsentationstypen."""


class Tag(Codelist):
  """Modell für Schlagwörter (Tags)."""
