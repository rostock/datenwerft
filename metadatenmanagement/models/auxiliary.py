from django.db import models
from django.utils.translation import gettext_lazy as _

from .abstract import Base

# Importiere Codelisten über String-Referenz oder direkt,
# da sie über models/__init__.py verfügbar sind.
# Direkter Import ist hier sicher, da keine Zirkelbezüge zu erwarten sind.
from .codelists import (
  Access,
  Crs,
  Format,
  License,
  MimeType,
  PoliticalGeocoding,
  PoliticalGeocodingLevel,
)

# ------------- Weitere Modelle -------------


class CrsSet(Base):
  """Modell für Sets von Koordinatenreferenzsystemen."""

  title = models.TextField(unique=True, verbose_name=_('Titel'))
  # ManyToManyField zur Codeliste Crs
  crs = models.ManyToManyField(Crs, verbose_name=_('Koordinatenreferenzsysteme'))

  def __str__(self):
    return self.title


class DataType(models.Model):
  """Modell für Datentypen."""

  title = models.TextField(unique=True, verbose_name=_('Titel'))
  # ForeignKey-Beziehungen zu Codelisten
  format = models.ForeignKey(
    Format, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Format')
  )
  mime_type = models.ForeignKey(
    MimeType, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('MIME-Typ')
  )

  def __str__(self):
    return self.title


class Legal(models.Model):
  """Modell für rechtliche Informationen."""

  title = models.TextField(unique=True, verbose_name=_('Titel'))
  # ForeignKey-Beziehungen zu Codelisten
  access = models.ForeignKey(
    Access, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Zugriffsrecht')
  )
  license = models.ForeignKey(
    License, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Lizenz')
  )
  constraints = models.TextField(blank=True, null=True, verbose_name=_('Nutzungsbedingungen'))

  def __str__(self):
    return self.title


class SpatialReference(models.Model):
  """Modell für räumliche Referenzen."""

  title = models.TextField(unique=True, verbose_name=_('Titel'))
  extent_spatial_south = models.DecimalField(
    max_digits=10, decimal_places=7, verbose_name=_('Ausdehnung Süd')
  )
  extent_spatial_east = models.DecimalField(
    max_digits=10, decimal_places=7, verbose_name=_('Ausdehnung Ost')
  )
  extent_spatial_north = models.DecimalField(
    max_digits=10, decimal_places=7, verbose_name=_('Ausdehnung Nord')
  )
  extent_spatial_west = models.DecimalField(
    max_digits=10, decimal_places=7, verbose_name=_('Ausdehnung West')
  )
  # ForeignKey-Beziehungen zu Codelisten
  political_geocoding_level = models.ForeignKey(
    PoliticalGeocodingLevel,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    verbose_name=_('Ebene der politischen Geokodierung'),
  )
  political_geocoding = models.ForeignKey(
    PoliticalGeocoding,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    verbose_name=_('Politische Geokodierung'),
  )

  def __str__(self):
    return self.title


class Organization(Base):
  """Modell für Organisationen."""

  name = models.TextField(unique=True, verbose_name=_('Name (intern)'))
  title = models.TextField(verbose_name=_('Titel (öffentlich)'))
  image = models.URLField(blank=True, null=True, verbose_name=_('Bild-URL'))

  def __str__(self):
    return self.title


class Contact(Base):
  """Modell für Kontakte."""

  first_name = models.TextField(blank=True, null=True, verbose_name=_('Vorname'))
  last_name = models.TextField(blank=True, null=True, verbose_name=_('Nachname'))
  email = models.EmailField(verbose_name=_('E-Mail'))
  # ForeignKey zu Organization
  organization = models.ForeignKey(
    Organization, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Organisation')
  )

  def __str__(self):
    name = f'{self.first_name or ""} {self.last_name or ""}'.strip()
    return name or self.email
