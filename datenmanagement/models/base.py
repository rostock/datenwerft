from uuid import uuid4
from django.contrib.gis.db.models import Model
from django.db.models.fields import BooleanField, CharField, UUIDField

from toolbox.constants_vars import standard_validators


#
# base abstract model classes
#

class Basemodel(Model):
  """
  default abstract model class
  """

  uuid = UUIDField(
    primary_key=True,
    default=uuid4,
    editable=False
  )

  class Meta:
    abstract = True
    managed = False


class Metamodel(Basemodel):
  """
  abstract model class for meta models
  """

  class Meta(Basemodel.Meta):
    abstract = True
    metamodel = True
    editable = False


class Codelist(Basemodel):
  """
  abstract model class for codelists
  """

  class Meta(Basemodel.Meta):
    abstract = True
    codelist = True


#
# abstract model classes for specific codelists
#

class Art(Codelist):
  """
  abstract model class for 'Art' codelists
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
  abstract model class for 'Befestigungsart' codelists
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
  abstract model class for 'Material' codelists
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
  abstract model class for 'Schlagwort' codelists
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
  abstract model class for 'Status' codelists
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
  abstract model class for 'Typ' codelists
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


#
# abstract model classes for data models
#

class SimpleModel(Basemodel):
  """
  abstract model class for simple data models
  """

  aktiv = BooleanField(
    ' aktiv?',
    default=True
  )

  class Meta(Basemodel.Meta):
    abstract = True


class ComplexModel(SimpleModel):
  """
  abstract model class for complex data models
  """

  class Meta(SimpleModel.Meta):
    abstract = True
    complex = True
