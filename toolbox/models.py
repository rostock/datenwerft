from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db import models


class Subsets(models.Model):
  id = models.AutoField(
    primary_key=True
  )
  created_at = models.DateTimeField(
    auto_now=True
  )
  model = models.ForeignKey(
    ContentType,
    on_delete=models.CASCADE
  )
  pk_field = models.CharField(
    max_length=255
  )
  pk_values = ArrayField(
    models.CharField(
      # normally model primary keys are UUIDs (36 chars in length)
      max_length=36
    )
  )

  class Meta:
    verbose_name = 'Subset'
    verbose_name_plural = 'Subsets'

  def __str__(self):
    return str(self.id)

  def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super().delete(*args, **kwargs)
