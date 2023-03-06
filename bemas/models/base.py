from django.contrib.gis.db.models import Model
from django.db.models.fields import BigAutoField, DateTimeField


class Basemodel(Model):
  """
  default abstract model class
  """

  id = BigAutoField(
    primary_key=True,
    editable=False
  )
  created_at = DateTimeField(
    auto_now_add=True,
    editable=False
  )
  updated_at = DateTimeField(
    auto_now=True,
    editable=False
  )

  class Meta:
    abstract = True
    get_latest_by = 'updated_at'

  class BasemodelMeta:
    description = None

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super().delete(*args, **kwargs)


class Codelist(Basemodel):
  """
  abstract model class for codelists
  """

  class Meta(Basemodel.Meta):
    abstract = True
