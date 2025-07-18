from django.db import models


class Topic(models.Model):
  name = models.CharField(max_length=255, verbose_name='Bezeichnung')

  def __str__(self):
    return self.name
