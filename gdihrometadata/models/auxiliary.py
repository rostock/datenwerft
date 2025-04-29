from django.db import models
from django.utils.translation import gettext_lazy as _

from .abstract import Base
from .codelists import (
  Access,
  Crs,
  Format,
  License,
  MimeType,
  PoliticalGeocoding,
  PoliticalGeocodingLevel,
)


class CrsSet(Base):
  """
  set of coordinate reference systems (Set aus einem oder mehreren Koordinatenreferenzsystem(en))
  """

  title = models.TextField(unique=True, verbose_name=_('Titel'))
  crs = models.ManyToManyField(Crs, verbose_name=_('Koordinatenreferenzsystem(e)'))

  class Meta:
    ordering = ['title']

  def __str__(self):
    return self.title


class DataType(Base):
  """
  data type (Datentyp)
  """

  title = models.TextField(unique=True, verbose_name=_('Titel'))
  format = models.ForeignKey(
    Format, on_delete=models.PROTECT, blank=True, null=True, verbose_name=_('Format')
  )
  mime_type = models.ForeignKey(
    MimeType, on_delete=models.PROTECT, blank=True, null=True, verbose_name=_('MIME-Typ')
  )

  class Meta:
    ordering = ['title']

  def __str__(self):
    return self.title


class Legal(Base):
  """
  legal (rechtliche Informationen)
  """

  title = models.TextField(unique=True, verbose_name=_('Titel'))
  access = models.ForeignKey(Access, on_delete=models.PROTECT, verbose_name=_('Zugriff'))
  license = models.ForeignKey(License, on_delete=models.PROTECT, verbose_name=_('Lizenz'))
  constraints = models.TextField(blank=True, null=True, verbose_name=_('Nutzungsbedingungen'))

  class Meta:
    ordering = ['title']

  def __str__(self):
    return self.title


class SpatialReference(models.Model):
  """
  spatial reference (räumlicher Bezug)
  """

  title = models.TextField(unique=True, verbose_name=_('Titel'))
  extent_spatial_south = models.DecimalField(
    max_digits=8, decimal_places=5, verbose_name=_('räumliche Ausdehnung Süden')
  )
  extent_spatial_east = models.DecimalField(
    max_digits=8, decimal_places=5, verbose_name=_('räumliche Ausdehnung Osten')
  )
  extent_spatial_north = models.DecimalField(
    max_digits=8, decimal_places=5, verbose_name=_('räumliche Ausdehnung Norden')
  )
  extent_spatial_west = models.DecimalField(
    max_digits=8, decimal_places=5, verbose_name=_('räumliche Ausdehnung Westen')
  )
  political_geocoding_level = models.ForeignKey(
    PoliticalGeocodingLevel,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    verbose_name=_('Ebene der geopolitischen Verwaltungscodierung)'),
  )
  political_geocoding = models.ForeignKey(
    PoliticalGeocoding,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    verbose_name=_('geopolitische Verwaltungscodierung'),
  )

  class Meta:
    ordering = ['title']

  def __str__(self):
    return self.title


class Organization(Base):
  """
  organization (Organisation)
  """

  name = models.TextField(unique=True, verbose_name=_('Name'))
  title = models.TextField(verbose_name=_('Titel'))
  image = models.URLField(blank=True, null=True, verbose_name=_('Bild (URL)'))

  class Meta:
    ordering = ['title']

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
