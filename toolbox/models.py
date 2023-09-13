from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db.models import CASCADE, ForeignKey, Model
from django.db.models.fields import AutoField, CharField, DateTimeField


class Subsets(Model):
  id = AutoField(
    primary_key=True
  )
  created_at = DateTimeField(
    auto_now=True
  )
  model = ForeignKey(
    ContentType,
    on_delete=CASCADE
  )
  pk_field = CharField(
    max_length=255
  )
  pk_values = ArrayField(
    CharField(
      # data model primary keys are UUIDs (36 chars in length)
      max_length=36
    )
  )

  class Meta:
    verbose_name = 'Subset'
    verbose_name_plural = 'Subsets'

  def __str__(self):
    return str(self.id)
