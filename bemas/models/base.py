from django.contrib.gis.db.models import Model
from django.db.models.fields import BigAutoField, CharField, DateTimeField


class Basemodel(Model):
  """
  default abstract model class
  """

  id = BigAutoField(verbose_name='ID', primary_key=True, editable=False)
  created_at = DateTimeField(verbose_name='Erstellung', auto_now_add=True, editable=False)
  updated_at = DateTimeField(verbose_name='letzte Änderung', auto_now=True, editable=False)

  class Meta:
    abstract = True
    get_latest_by = 'updated_at'

  class BasemodelMeta:
    table_exclusion_fields = ['created_at', 'updated_at']
    geometry_field = None
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

  search_content = CharField(max_length=255, blank=True, null=True, editable=False)

  class Meta(Basemodel.Meta):
    abstract = True

  class BasemodelMeta(Basemodel.BasemodelMeta):
    table_exclusion_fields = Basemodel.BasemodelMeta.table_exclusion_fields
    table_exclusion_fields.append('search_content')


class GeometryObjectclass(Objectclass):
  """
  abstract model class for object classes with geometry related fields
  """

  class Meta(Objectclass.Meta):
    abstract = True
