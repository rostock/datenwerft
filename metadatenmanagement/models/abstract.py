import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

# ------------- Abstrakte Basismodelle -------------


class Base(models.Model):
  """Abstraktes Basismodell mit Zeitstempeln."""

  # Django fügt automatisch ein 'id'-Feld hinzu (AutoField)
  created = models.DateTimeField(auto_now_add=True, verbose_name=_('Erstellt am'))
  modified = models.DateTimeField(auto_now=True, verbose_name=_('Geändert am'))

  class Meta:
    abstract = True
    ordering = ['-created']  # Standard-Sortierung


class Codelist(Base):
  """Abstraktes Modell für Codelisten."""

  code = models.URLField(unique=True, verbose_name=_('Code (URL)'))
  title = models.TextField(verbose_name=_('Titel'))
  description = models.TextField(blank=True, null=True, verbose_name=_('Beschreibung'))

  class Meta:
    abstract = True
    ordering = ['title']

  def __str__(self):
    return self.title


class BaseMetadata(models.Model):
  """Abstraktes Modell für Basis-Metadaten."""

  uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name=_('UUID'))
  description = models.TextField(blank=True, null=True, verbose_name=_('Beschreibung'))
  external = models.URLField(blank=True, null=True, verbose_name=_('Externe URL'))
  # ManyToManyField für 'tags' wird in den konkreten Modellen hinzugefügt
  # die dieses Modell erben

  class Meta:
    abstract = True


class CreationalMetadata(models.Model):
  """Abstraktes Modell für Erstellungs-Metadaten."""

  creation = models.DateField(verbose_name=_('Erstellungsdatum'))
  last_update = models.DateField(verbose_name=_('Letzte Aktualisierung'))
  # ForeignKey für 'update_frequency' wird in den konkreten Modellen hinzugefügt
  # die dieses Modell erben

  class Meta:
    abstract = True


class SpatioTemporalMetadata(models.Model):
  """Abstraktes Modell für räumlich-zeitliche Metadaten."""

  extent_temporal_start = models.DateTimeField(
    blank=True, null=True, verbose_name=_('Zeitliche Ausdehnung Start')
  )
  extent_temporal_end = models.DateTimeField(
    blank=True, null=True, verbose_name=_('Zeitliche Ausdehnung Ende')
  )
  # ForeignKeys für 'native_crs', 'spatial_reference' und ManyToManyField für 'additional_crs'
  # werden in den konkreten Modellen hinzugefügt, die dieses Modell erben

  class Meta:
    abstract = True
