from django.db.models.fields import CharField, SmallIntegerField

from toolbox.constants_vars import standard_validators
from .base import Codelist


class Status(Codelist):
  """
  model class for codelist status (Bearbeitungsstatus)
  """

  ordinal = SmallIntegerField(
    verbose_name='Ordinalzahl',
    unique=True
  )
  title = CharField(
    verbose_name='Titel',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  icon = CharField(
    verbose_name='Icon',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelist_status'
    ordering = ['ordinal']
    verbose_name = 'Bearbeitungsstatus'
    verbose_name_plural = 'Bearbeitungsstatus'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Bearbeitungsstatus von Beschwerden'

  class CustomMeta:
    min_numbers = {
      'ordinal': 1
    }

  def __str__(self):
    return self.title

  @staticmethod
  def get_default_status():
    return Status.objects.get(ordinal=1) if Status.objects.filter(ordinal=1).exists() else None

  @staticmethod
  def get_closed_status():
    return Status.objects.get(ordinal=2) if Status.objects.filter(ordinal=2).exists() else None


class Sector(Codelist):
  """
  model class for codelist sector (Branche)
  """

  title = CharField(
    verbose_name='Titel',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  examples = CharField(
    verbose_name='Beispiele',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelist_sector'
    ordering = ['title']
    verbose_name = 'Branche'
    verbose_name_plural = 'Branchen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'definiert Verursacher näher'

  def __str__(self):
    return self.title


class TypeOfEvent(Codelist):
  """
  model class for codelist type of event (Ereignisart)
  """

  title = CharField(
    verbose_name='Titel',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  icon = CharField(
    verbose_name='Icon',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelist_typeofevent'
    ordering = ['title']
    verbose_name = 'Ereignisart'
    verbose_name_plural = 'Ereignisarten'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'definiert Journalereignisse näher'

  def __str__(self):
    return self.title


class TypeOfImmission(Codelist):
  """
  model class for codelist type of immission (Immissionsart)
  """

  title = CharField(
    verbose_name='Titel',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  icon = CharField(
    verbose_name='Icon',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelist_typeofimmission'
    ordering = ['title']
    verbose_name = 'Immissionsart'
    verbose_name_plural = 'Immissionsarten'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'definiert Immissionen näher'

  def __str__(self):
    return self.title
