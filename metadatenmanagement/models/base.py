from django.db.models import Model
from django.db.models.fields import CharField, DateTimeField, URLField, UUIDField
from uuid import uuid4

from toolbox.constants_vars import standard_validators


class Base(Model):
  """
  default abstract model class
  """

  id = UUIDField(
    verbose_name='ID',
    primary_key=True,
    default=uuid4,
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

  namespace = URLField(
    verbose_name='Namensraum',
    blank=True,
    null=True,
    validators=standard_validators
  )
  code = CharField(
    verbose_name='Code',
    unique=True,
    validators=standard_validators
  )
  title = CharField(
    verbose_name='Bezeichnung',
    validators=standard_validators
  )
  description = CharField(
    verbose_name='Beschreibung',
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(Base.Meta):
    abstract = True
    ordering = ['title']

  def __str__(self):
    return self.title
