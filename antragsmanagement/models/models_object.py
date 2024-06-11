from django.db.models import ForeignKey, PROTECT
from django.db.models.fields import CharField, EmailField, TextField

from toolbox.constants_vars import standard_validators
from .base import Object, GeometryObject
from .models_codelist import CodelistRequestStatus, CleanupEventCodelistWasteQuantity, \
  CleanupEventCodelistWasteType, CleanupEventCodelistEquipment


#
# general objects
#

class Authority(Object):
  """
  model class for general object:
  authority (Behörde)
  """

  group = CharField(
    verbose_name='Gruppe',
    editable=False
  )
  name = CharField(
    verbose_name='Bezeichnung',
    unique=True,
    editable=False
  )
  email = EmailField(
    verbose_name='E-Mail-Adresse'
  )

  class Meta(Object.Meta):
    db_table = 'authority'
    ordering = ['name']
    verbose_name = 'Behörde'
    verbose_name_plural = 'Behörden'

  class BaseMeta(Object.BaseMeta):
    description = 'Behörden'

  def __str__(self):
    return self.name


class Email(Object):
  """
  model class for general object:
  email (E-Mail)
  """

  key = CharField(
    verbose_name='Identifikator',
    unique=True,
    editable=False
  )
  body = TextField(
    verbose_name='Inhalt',
    validators=standard_validators
  )

  class Meta(Object.Meta):
    db_table = 'email'
    ordering = ['key']
    verbose_name = 'E-Mail'
    verbose_name_plural = 'E-Mails'

  class BaseMeta(Object.BaseMeta):
    description = 'E-Mails'

  def __str__(self):
    return self.key


class Request(Object):
  """
  abstract model class for general object:
  request (Antrag)
  """

  status = ForeignKey(
    to=CodelistRequestStatus,
    verbose_name='Status',
    on_delete=PROTECT
  )

  class Meta(Object.Meta):
    abstract = True


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventRequest(Request):
  """
  model class for object for request type clean-up events (Müllsammelaktionen):
  request (Antrag)
  """

  class Meta(Request.Meta):
    db_table = 'cleanupevent_request'
    ordering = ['-id']
    verbose_name = 'Antrag'
    verbose_name_plural = 'Anträge'

  class BaseMeta(Request.BaseMeta):
    description = 'Müllsammelaktionen: Anträge'

  def __str__(self):
    return '#' + str(self.id) + ' vom ' + self.created.strftime('%d.%m.%Y') + \
           ' (' + str(self.status) + ')'
