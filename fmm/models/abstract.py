from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class Base(models.Model):
  """
  default abstract model class
  """

  id = models.BigAutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  created = models.DateTimeField(verbose_name=_('Erstellung'), auto_now_add=True, editable=False)
  modified = models.DateTimeField(verbose_name=_('Änderung'), auto_now=True, editable=False)
  uuid = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name=_('UUID'))

  class Meta:
    abstract = True
    ordering = ['-created']
    get_latest_by = 'modified'

  class BaseMeta:
    icon = 'paket'
    geometry_field = None
    geometry_type = None
