from django.contrib.gis.db.models import Model
from django.db.models.fields import BigAutoField, CharField, DateTimeField, \
  PositiveSmallIntegerField

from toolbox.constants_vars import standard_validators


class Base(Model):
  """
  default abstract model class
  """

  id = BigAutoField(
    verbose_name='ID',
    primary_key=True,
    editable=False
  )
  created = DateTimeField(
    verbose_name='Erstellung',
    auto_now_add=True,
    editable=False
  )
  modified = DateTimeField(
    verbose_name='letzte Änderung',
    auto_now=True,
    editable=False
  )

  class Meta:
    abstract = True
    get_latest_by = 'modified'

  class BaseMeta:
    description = None


class Codelist(Base):
  """
  abstract model class for codelists
  """

  ordinal = PositiveSmallIntegerField(
    verbose_name='Ordinalzahl',
    unique=True,
    blank=True,
    null=True
  )
  name = CharField(
    verbose_name='Bezeichnung',
    unique=True,
    validators=standard_validators
  )
  description = CharField(
    verbose_name='Beschreibung',
    blank=True,
    null=True,
    validators=standard_validators
  )
  icon = CharField(
    verbose_name='Icon',
    unique=True,
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(Base.Meta):
    abstract = True
    ordering = ['ordinal', 'name']

  def __str__(self):
    return self.name


class Object(Base):
  """
  abstract model class for objects
  """

  class Meta(Base.Meta):
    abstract = True


class GeometryObject(Object):
  """
  abstract model class for objects with geometry related fields
  """

  class Meta(Object.Meta):
    abstract = True
