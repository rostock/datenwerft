from django.utils.translation import gettext_lazy as _

from .abstract import Codelist


class Access(Codelist):
  """
  access (Zugriff)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Zugriff')
    verbose_name_plural = _('Codeliste → Zugriffe')


class AssetType(Codelist):
  """
  asset type (Typ eines Assets)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Typ eines Assets')
    verbose_name_plural = _('Codeliste → Typen von Assets')


class Charset(Codelist):
  """
  charset (Zeichensatz)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Zeichensatz')
    verbose_name_plural = _('Codeliste → Zeichensätze')


class Crs(Codelist):
  """
  coordinate reference system (Koordinatenreferenzsystem)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Koordinatenreferenzsystem')
    verbose_name_plural = _('Codeliste → Koordinatenreferenzsysteme')


class DatathemeCategory(Codelist):
  """
  data theme category (Datenthemenkategorie)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Datenthemenkategorie')
    verbose_name_plural = _('Codeliste → Datenthemenkategorien')


class Format(Codelist):
  """
  format (Format)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Format')
    verbose_name_plural = _('Codeliste → Formate')


class Frequency(Codelist):
  """
  frequency (Häufigkeit)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Häufigkeit')
    verbose_name_plural = _('Codeliste → Häufigkeiten')


class HashType(Codelist):
  """
  hash type (Typ eines Hashes)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Typ eines Hashes')
    verbose_name_plural = _('Codeliste → Typen von Hashes')


class HvdCategory(Codelist):
  """
  high-value dataset category (HVD-Kategorie)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → HVD-Kategorie')
    verbose_name_plural = _('Codeliste → HVD-Kategorien')


class InspireServiceType(Codelist):
  """
  INSPIRE service type (Typ eines INSPIRE-Services)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Typ eines INSPIRE-Services')
    verbose_name_plural = _('Codeliste → Typen von INSPIRE-Services')


class InspireSpatialScope(Codelist):
  """
  INSPIRE spatial scope (räumlicher INSPIRE-Bezugsbereich)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → INSPIRE-Raumbezug')
    verbose_name_plural = _('Codeliste → INSPIRE-Raumbezüge')


class InspireTheme(Codelist):
  """
  INSPIRE theme (INSPIRE-Thema)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → INSPIRE-Thema')
    verbose_name_plural = _('Codeliste → INSPIRE-Themen')


class Language(Codelist):
  """
  language (Sprache)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Sprache')
    verbose_name_plural = _('Codeliste → Sprachen')


class License(Codelist):
  """
  license (Lizenz)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Lizenz')
    verbose_name_plural = _('Codeliste → Lizenzen')


class MimeType(Codelist):
  """
  MIME type (MIME-Typ)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → MIME-Typ')
    verbose_name_plural = _('Codeliste → MIME-Typen')


class PoliticalGeocoding(Codelist):
  """
  political geocoding (geopolitische Verwaltungscodierung)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Geopolitische Verwaltungscodierungen')
    verbose_name_plural = _('Codeliste → Geopolitische Verwaltungscodierung')


class PoliticalGeocodingLevel(Codelist):
  """
  political geocoding level (Ebene der geopolitischen Verwaltungscodierung)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Ebene der geopolitischen Verwaltungscodierung')
    verbose_name_plural = _('Codeliste → Ebenen der geopolitischen Verwaltungscodierung')


class SpatialRepresentationType(Codelist):
  """
  spatial representation type (Typ der räumlichen Repräsentation)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Typ der räumlichen Repräsentation')
    verbose_name_plural = _('Codeliste → Typen der räumlichen Repräsentation')


class Tag(Codelist):
  """
  tag (Schlagwort)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Codelistenelement → Schlagwort')
    verbose_name_plural = _('Codeliste → Schlagwörter')
