from uuid import uuid4

from django.db import models
from django.utils.translation import gettext_lazy as _


class Base(models.Model):
  """
  default abstract model class
  """

  id = models.BigAutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  created = models.DateTimeField(verbose_name=_('Erstellung'), auto_now_add=True, editable=False)
  modified = models.DateTimeField(verbose_name=_('letzte Änderung'), auto_now=True, editable=False)

  class Meta:
    abstract = True
    ordering = ['-created']
    get_latest_by = 'modified'


class Codelist(Base):
  """
  abstract model class for codelists
  """

  code = models.URLField(unique=True, verbose_name=_('Code (URL)'))
  title = models.TextField(verbose_name=_('Titel'))
  description = models.TextField(blank=True, null=True, verbose_name=_('Beschreibung'))

  class Meta:
    abstract = True
    ordering = ['title']

  def __str__(self):
    return self.title


class BaseMetadata(models.Model):
  """
  abstract model class for base metadata
  """

  uuid = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name=_('UUID'))
  description = models.TextField(blank=True, null=True, verbose_name=_('Beschreibung'))
  external = models.URLField(blank=True, null=True, verbose_name=_('externe URL'))
  # ManyToManyField for tags is included in the concrete models that inherit from this base model

  class Meta:
    abstract = True


class CreationalMetadata(models.Model):
  """
  abstract model class for creational metadata
  """

  creation = models.DateField(verbose_name=_('Erstellungsdatum'))
  last_update = models.DateField(verbose_name=_('Datum der letzten Aktualisierung'))
  # ForeignKey for update frequency is included in the concrete models
  # that inherit from this base model

  class Meta:
    abstract = True


class SpatioTemporalMetadata(models.Model):
  """
  abstract model class for spatio-temporal metadata
  """

  # ForeignKeys for native CRS and spatial reference,
  # along with ManyToManyField for additional CRS,
  # are included in the concrete models that inherit from this base model
  extent_temporal_start = models.DateTimeField(
    blank=True, null=True, verbose_name=_('Beginn der zeitlichen Ausdehnung')
  )
  extent_temporal_end = models.DateTimeField(
    blank=True, null=True, verbose_name=_('Ende der zeitlichen Ausdehnung')
  )

  class Meta:
    abstract = True
