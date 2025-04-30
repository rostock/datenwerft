from django.utils.translation import gettext_lazy as _

from .abstract import Codelist


class Access(Codelist):
  """
  access (Zugriff)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Zugriff')
    verbose_name_plural = _('Zugriffe')


class AssetType(Codelist):
  """
  asset type (Typ eines Assets)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Typ eines Assets')
    verbose_name_plural = _('Typen von Assets')


class Charset(Codelist):
  """
  charset (Zeichensatz)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Zeichensatz')
    verbose_name_plural = _('Zeichensätze')


class Crs(Codelist):
  """
  coordinate reference system (Koordinatenreferenzsystem)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Koordinatenreferenzsystem')
    verbose_name_plural = _('Koordinatenreferenzsysteme')


class DatathemeCategory(Codelist):
  """
  data theme category (Datenthemenkategorie)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Datenthemenkategorie')
    verbose_name_plural = _('Datenthemenkategorien')


class Format(Codelist):
  """
  format (Format)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Format')
    verbose_name_plural = _('Formate')


class Frequency(Codelist):
  """
  frequency (Häufigkeit)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Häufigkeit')
    verbose_name_plural = _('Häufigkeiten')


class HashType(Codelist):
  """
  hash type (Typ eines Hashes)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Typ eines Hashes')
    verbose_name_plural = _('Typen von Hashes')


class HvdCategory(Codelist):
  """
  high-value dataset category (HVD-Kategorie)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('HVD-Kategorie')
    verbose_name_plural = _('HVD-Kategorien')


class InspireServiceType(Codelist):
  """
  INSPIRE service type (Typ eines INSPIRE-Services)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Typ eines INSPIRE-Services')
    verbose_name_plural = _('Typen von INSPIRE-Services')


class InspireSpatialScope(Codelist):
  """
  INSPIRE spatial scope (räumlicher INSPIRE-Bezugsbereich)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('INSPIRE-Raumbezug')
    verbose_name_plural = _('INSPIRE-Raumbezüge')


class InspireTheme(Codelist):
  """
  INSPIRE theme (INSPIRE-Thema)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('INSPIRE-Thema')
    verbose_name_plural = _('INSPIRE-Themen')


class Language(Codelist):
  """
  language (Sprache)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Sprache')
    verbose_name_plural = _('Sprachen')


class License(Codelist):
  """
  license (Lizenz)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Lizenz')
    verbose_name_plural = _('Lizenzen')


class MimeType(Codelist):
  """
  MIME type (MIME-Typ)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('MIME-Typ')
    verbose_name_plural = _('MIME-Typen')


class PoliticalGeocoding(Codelist):
  """
  political geocoding (geopolitische Verwaltungscodierung)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Geopolitische Verwaltungscodierungen')
    verbose_name_plural = _('Geopolitische Verwaltungscodierung')


class PoliticalGeocodingLevel(Codelist):
  """
  political geocoding level (Ebene der geopolitischen Verwaltungscodierung)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Ebene der geopolitischen Verwaltungscodierung')
    verbose_name_plural = _('Ebenen der geopolitischen Verwaltungscodierung')


class SpatialRepresentationType(Codelist):
  """
  spatial representation type (Typ der räumlichen Repräsentation)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Typ der räumlichen Repräsentation')
    verbose_name_plural = _('Typen der räumlichen Repräsentation')


class Tag(Codelist):
  """
  tag (Schlagwort)
  """

  class Meta(Codelist.Meta):
    verbose_name = _('Schlagwort')
    verbose_name_plural = _('Schlagwörter')
