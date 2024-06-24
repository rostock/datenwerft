from django.db.models.fields import CharField

from .base import Codelist
from toolbox.constants_vars import standard_validators


#
# general codelists
#

class CodelistRequestStatus(Codelist):
  """
  model class for general codelist:
  request status (Antragsstatus)
  """

  icon = CharField(
    verbose_name='Icon',
    unique=True,
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelist_requeststatus'
    verbose_name = 'Antragsstatus'
    verbose_name_plural = 'Antragsstatus'

  class BaseMeta(Codelist.BaseMeta):
    description = 'Codeliste: Status von Anträgen'

  def __str__(self):
    return self.name

  @staticmethod
  def get_status_new(as_queryset=False):
    if CodelistRequestStatus.objects.filter(ordinal=0).exists():
      return CodelistRequestStatus.objects.filter(ordinal=0) if as_queryset else (
        CodelistRequestStatus.objects.get(ordinal=0))
    else:
      return None

  @staticmethod
  def get_status_in_process(as_queryset=False):
    if CodelistRequestStatus.objects.filter(ordinal=1).exists():
      return CodelistRequestStatus.objects.filter(ordinal=1) if as_queryset else (
        CodelistRequestStatus.objects.get(ordinal=1))
    else:
      return None

  @staticmethod
  def get_status_processed(as_queryset=False):
    if CodelistRequestStatus.objects.filter(ordinal=2).exists():
      return CodelistRequestStatus.objects.filter(ordinal=2) if as_queryset else (
        CodelistRequestStatus.objects.get(ordinal=2))
    else:
      return None

  @staticmethod
  def get_status_rejected(as_queryset=False):
    if CodelistRequestStatus.objects.filter(ordinal=3).exists():
      return CodelistRequestStatus.objects.filter(ordinal=3) if as_queryset else (
        CodelistRequestStatus.objects.get(ordinal=3))
    else:
      return None


#
# codelists for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventCodelistWasteQuantity(Codelist):
  """
  model class for codelist for request type clean-up events (Müllsammelaktionen):
  waste quantity (Abfallmenge)
  """

  class Meta(Codelist.Meta):
    db_table = 'cleanupevent_codelist_wastequantity'
    verbose_name = 'Müllsammelaktion: Abfallmenge'
    verbose_name_plural = 'Müllsammelaktionen: Abfallmengen'

  class BaseMeta(Codelist.BaseMeta):
    description = 'Codeliste für Müllsammelaktionen: Abfallmengen'


class CleanupEventCodelistWasteType(Codelist):
  """
  model class for codelist for request type clean-up events (Müllsammelaktionen):
  waste type (Abfallart)
  """

  class Meta(Codelist.Meta):
    db_table = 'cleanupevent_codelist_wastetype'
    verbose_name = 'Müllsammelaktion: Abfallart'
    verbose_name_plural = 'Müllsammelaktionen: Abfallarten'

  class BaseMeta(Codelist.BaseMeta):
    description = 'Codeliste für Müllsammelaktionen: Abfallarten'


class CleanupEventCodelistEquipment(Codelist):
  """
  model class for codelist for request type clean-up events (Müllsammelaktionen):
  equipment (Austattung)
  """

  class Meta(Codelist.Meta):
    db_table = 'cleanupevent_codelist_equipment'
    verbose_name = 'Müllsammelaktion: Austattung'
    verbose_name_plural = 'Müllsammelaktionen: Austattungen'

  class BaseMeta(Codelist.BaseMeta):
    description = 'Codeliste für Müllsammelaktionen: Austattungen'
