from .base import Codelist


class CodelistUpdateFrequency(Codelist):
  """
  model class for codelist update frequency (Aktualisierungshäufigkeiten)
  """

  class Meta(Codelist.Meta):
    db_table = 'codelist_updatefrequency'
    verbose_name = 'Aktualisierungshäufigkeit'
    verbose_name_plural = 'Aktualisierungshäufigkeiten'

  class BaseMeta(Codelist.BaseMeta):
    description = 'Häufigkeiten von Aktualisierungen'
