from django.db.models import CheckConstraint, Q
from django.db.models.fields import CharField, SmallIntegerField

from datenmanagement.models.constants_vars import standard_validators
from .base import Codelist


class Status(Codelist):
  """
  model class for codelist status (Bearbeitungsstatus)
  """

  ordinal = SmallIntegerField(
    unique=True
  )
  title = CharField(
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  icon = CharField(
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta:
    codelist = True
    constraints = [
      CheckConstraint(
        check=Q(ordinal__gte=1),
        name='status_ordinal_gte_1'
      )
    ]
    db_table = 'codelist_status'
    ordering = ['ordinal']
    verbose_name = 'Bearbeitungsstatus'
    verbose_name_plural = 'Bearbeitungsstatus'

  def __str__(self):
    return self.title


class Sector(Codelist):
  """
  model class for codelist sector (Branche)
  """

  title = CharField(
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta:
    codelist = True
    db_table = 'codelist_sector'
    ordering = ['title']
    verbose_name = 'Branche'
    verbose_name_plural = 'Branchen'

  def __str__(self):
    return self.title


class TypeOfEvent(Codelist):
  """
  model class for codelist type of event (Ereignisart)
  """

  title = CharField(
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  icon = CharField(
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta:
    codelist = True
    db_table = 'codelist_typeofevent'
    ordering = ['title']
    verbose_name = 'Ereignisart'
    verbose_name_plural = 'Ereignisarten'

  def __str__(self):
    return self.title


class TypeOfImmission(Codelist):
  """
  model class for codelist type of immission (Immissionsart)
  """

  title = CharField(
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  icon = CharField(
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta:
    codelist = True
    db_table = 'codelist_typeofimmission'
    ordering = ['title']
    verbose_name = 'Immissionsart'
    verbose_name_plural = 'Immissionsarten'

  def __str__(self):
    return self.title
