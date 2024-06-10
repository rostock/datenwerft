from .base import Codelist


#
# general codelists
#

class CodelistRequestStatus(Codelist):
  """
  model class for general codelist request status (Antragsstatus)
  """

  class Meta(Codelist.Meta):
    db_table = 'codelist_requeststatus'
    verbose_name = 'Antragsstatus'
    verbose_name_plural = 'Antragsstatus'

  class BaseMeta(Codelist.BaseMeta):
    description = 'Status von Anträgen'

  @staticmethod
  def get_status_new():
    if CodelistRequestStatus.objects.filter(ordinal=0).exists():
      return CodelistRequestStatus.objects.get(ordinal=0)
    else:
      return None

  @staticmethod
  def get_status_in_process():
    if CodelistRequestStatus.objects.filter(ordinal=1).exists():
      return CodelistRequestStatus.objects.get(ordinal=1)
    else:
      return None

  @staticmethod
  def get_status_processed():
    if CodelistRequestStatus.objects.filter(ordinal=2).exists():
      return CodelistRequestStatus.objects.get(ordinal=2)
    else:
      return None

  @staticmethod
  def get_status_rejected():
    if CodelistRequestStatus.objects.filter(ordinal=3).exists():
      return CodelistRequestStatus.objects.get(ordinal=3)
    else:
      return None
