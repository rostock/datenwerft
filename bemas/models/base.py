from django.contrib.gis.db.models import Model
from django.db.models.fields import BigAutoField, DateTimeField


class Basemodel(Model):
  """
  default abstract model class
  """

  id = BigAutoField(
    'ID',
    primary_key=True,
    editable=False
  )
  created_at = DateTimeField(
    'Erstellung',
    auto_now_add=True,
    editable=False
  )
  updated_at = DateTimeField(
    'letzte Änderung',
    auto_now=True,
    editable=False
  )

  class Meta:
    abstract = True
    get_latest_by = 'updated_at'

  class BasemodelMeta:
    gis_field = None
    description = None
    definite_article = None
    indefinite_article = None
    personal_pronoun = None
    new = None


class Codelist(Basemodel):
  """
  abstract model class for codelists
  """

  class Meta(Basemodel.Meta):
    abstract = True


class Objectclass(Basemodel):
  """
  abstract model class for object classes
  """

  class Meta(Basemodel.Meta):
    abstract = True


class GISObjectclass(Basemodel):
  """
  abstract model class for object classes containing GIS data
  """

  class Meta(Basemodel.Meta):
    abstract = True
