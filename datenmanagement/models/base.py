from uuid import uuid4
from django.contrib.gis.db.models import Model
from django.db.models.fields import BooleanField, CharField, UUIDField

from .constants_vars import standard_validators


#
# Basisklassen für Datenmodelle
#

class Basemodel(Model):
  """
  Basisdatenmodell (abstrakt)
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


class Metamodel(Basemodel):
  """
  Meta-Datenmodell (abstrakt)
  """

  class Meta(Basemodel.Meta):
    abstract = True
    metamodel = True
    editable = False


class Codelist(Basemodel):
  """
  Codeliste (abstrakt)
  """

  class Meta(Basemodel.Meta):
    abstract = True
    codelist = True


#
# Klassen für Codelisten
#

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


#
# Klassen für normale Datenmodelle
#

class SimpleModel(Basemodel):
  """
  einfaches Datenmodell (abstrakt)
  """

  aktiv = BooleanField(
    ' aktiv?',
    default=True
  )

  class Meta(Basemodel.Meta):
    abstract = True


class ComplexModel(SimpleModel):
  """
  komplexes Datenmodell (abstrakt)
  """

  class Meta(SimpleModel.Meta):
    abstract = True
    complex = True
