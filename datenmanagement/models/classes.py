from uuid import uuid4
from django.contrib.gis.db.models import Model
from django.db.models.fields import BooleanField, CharField, UUIDField

from .constants_vars import standard_validators


class DefaultModel(Model):
  """
  Datenmodell (abstrakt)
  """

  uuid = UUIDField(
    primary_key=True,
    default=uuid4,
    editable=False
  )

  class Meta:
    abstract = True
    managed = False

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super().delete(*args, **kwargs)


class Metamodel(DefaultModel):
  """
  Meta-Datenmodell (abstrakt)
  """

  class Meta(DefaultModel.Meta):
    abstract = True
    metamodel = True
    editable = False


class Codelist(DefaultModel):
  """
  Codeliste (abstrakt)
  """

  class Meta(DefaultModel.Meta):
    abstract = True
    codelist = True


class Art(Codelist):
  """
  Art (abstrakt)
  """

  art = CharField(
    'Art',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract = True
    list_fields = {
      'art': 'Art'
    }
    ordering = ['art']

  def __str__(self):
    return self.art


class Befestigungsart(Codelist):
  """
  Befestigungsart (abstrakt)
  """

  befestigungsart = CharField(
    'Befestigungsart',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract = True
    list_fields = {
      'befestigungsart': 'Befestigungsart'
    }
    ordering = ['befestigungsart']

  def __str__(self):
    return self.befestigungsart


class Material(Codelist):
  """
  Material (abstrakt)
  """

  material = CharField(
    'Material',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract = True
    list_fields = {
      'material': 'Material'
    }
    ordering = ['material']

  def __str__(self):
    return self.material


class Schlagwort(Codelist):
  """
  Schlagwort (abstrakt)
  """

  schlagwort = CharField(
    'Schlagwort',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract = True
    list_fields = {
      'schlagwort': 'Schlagwort'
    }
    ordering = ['schlagwort']

  def __str__(self):
    return self.schlagwort


class Status(Codelist):
  """
  Status (abstrakt)
  """

  status = CharField(
    'Status',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract = True
    list_fields = {
      'status': 'Status'
    }
    ordering = ['status']

  def __str__(self):
    return self.status


class Typ(Codelist):
  """
  Typ (abstrakt)
  """

  typ = CharField(
    'Typ',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    abstract = True
    list_fields = {
      'typ': 'Typ'
    }
    ordering = ['typ']

  def __str__(self):
    return self.typ


class Model(DefaultModel):
  """
  Standard-Datenmodell (abstrakt)
  """

  aktiv = BooleanField(
    ' aktiv?',
    default=True
  )

  class Meta(DefaultModel.Meta):
    abstract = True
