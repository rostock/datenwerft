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
    description = None


class Codelist(Basemodel):
  """
  abstract model class for codelists
  """

  class Meta(Basemodel.Meta):
    abstract = True
