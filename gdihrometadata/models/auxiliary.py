from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from toolbox.constants_vars import (
  kleinbuchstaben_bindestrich_message,
  kleinbuchstaben_bindestrich_regex,
  personennamen_validators,
  standard_validators,
)
from toolbox.fields import NullTextField

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

  title = models.CharField(unique=True, validators=standard_validators, verbose_name=_('Titel'))
  crs = models.ManyToManyField(
    Crs, related_name='crs_sets', verbose_name=_('Koordinatenreferenzsystem(e)')
  )

  class Meta(Base.Meta):
    ordering = ['title']
    verbose_name = _('Set aus einem oder mehreren Koordinatenreferenzsystem(en)')
    verbose_name_plural = _('Sets aus einem oder mehreren Koordinatenreferenzsystem(en)')

  def __str__(self):
    return self.title


class DataType(Base):
  """
  data type (Datentyp)
  """

  title = models.CharField(unique=True, validators=standard_validators, verbose_name=_('Titel'))
  format = models.ForeignKey(
    Format,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='datatype_formats',
    verbose_name=_('Format'),
  )
  mime_type = models.ForeignKey(
    MimeType,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='datatype_mime_types',
    verbose_name=_('MIME-Typ'),
  )

  class Meta(Base.Meta):
    ordering = ['title']
    verbose_name = _('Datentyp')
    verbose_name_plural = _('Datentypen')

  def __str__(self):
    return self.title


class Legal(Base):
  """
  legal (rechtliche Informationen)
  """

  title = models.CharField(unique=True, validators=standard_validators, verbose_name=_('Titel'))
  access = models.ForeignKey(
    Access, on_delete=models.PROTECT, related_name='legal_accesses', verbose_name=_('Zugriff')
  )
  license = models.ForeignKey(
    License, on_delete=models.PROTECT, related_name='legal_licenses', verbose_name=_('Lizenz')
  )
  constraints = NullTextField(
    blank=True, null=True, validators=standard_validators, verbose_name=_('Nutzungsbedingungen')
  )

  class Meta(Base.Meta):
    ordering = ['title']
    verbose_name = _('Rechtsstatus')
    verbose_name_plural = _('Rechtsstatus')

  def __str__(self):
    return self.title


class SpatialReference(Base):
  """
  spatial reference (räumlicher Bezug)
  """

  title = models.CharField(unique=True, validators=standard_validators, verbose_name=_('Titel'))
  extent_spatial_south = models.DecimalField(
    max_digits=8, decimal_places=5, verbose_name=_('Süden (räumliche Ausdehnung)')
  )
  extent_spatial_east = models.DecimalField(
    max_digits=8, decimal_places=5, verbose_name=_('Osten (räumliche Ausdehnung)')
  )
  extent_spatial_north = models.DecimalField(
    max_digits=8, decimal_places=5, verbose_name=_('Norden (räumliche Ausdehnung)')
  )
  extent_spatial_west = models.DecimalField(
    max_digits=8, decimal_places=5, verbose_name=_('Westen (räumliche Ausdehnung)')
  )
  political_geocoding_level = models.ForeignKey(
    PoliticalGeocodingLevel,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='spatialreference_legal_political_geocoding_levels',
    verbose_name=_('Ebene der geopolitischen Verwaltungscodierung'),
  )
  political_geocoding = models.ForeignKey(
    PoliticalGeocoding,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='spatialreference_legal_political_geocodings',
    verbose_name=_('Geopolitische Verwaltungscodierung'),
  )

  class Meta(Base.Meta):
    ordering = ['title']
    verbose_name = _('Raumbezug')
    verbose_name_plural = _('Raumbezüge')

  def __str__(self):
    return self.title


class Organization(Base):
  """
  organization (Organisation)
  """

  name = models.CharField(
    unique=True,
    validators=[
      RegexValidator(
        regex=kleinbuchstaben_bindestrich_regex, message=kleinbuchstaben_bindestrich_message
      )
    ],
    verbose_name=_('Name'),
  )
  title = models.CharField(validators=standard_validators, verbose_name=_('Titel'))
  image = models.URLField(blank=True, null=True, verbose_name=_('Bild (URL)'))

  class Meta(Base.Meta):
    ordering = ['title']
    verbose_name = _('Organisation')
    verbose_name_plural = _('Organisationen')

  def __str__(self):
    return self.title


class Contact(Base):
  """
  contact (Kontakt)
  """

  first_name = models.CharField(
    blank=True, null=True, validators=personennamen_validators, verbose_name=_('Vorname')
  )
  last_name = models.CharField(
    blank=True, null=True, validators=personennamen_validators, verbose_name=_('Nachname')
  )
  email = models.EmailField(verbose_name=_('E-Mail-Adresse'))
  organization = models.ForeignKey(
    Organization,
    on_delete=models.CASCADE,
    blank=True,
    null=True,
    related_name='contact_organizations',
    verbose_name=_('Organisation'),
  )

  class Meta(Base.Meta):
    ordering = ['last_name', 'first_name', 'email']
    verbose_name = _('Kontakt')
    verbose_name_plural = _('Kontakte')

  def __str__(self):
    name = f'{self.first_name or ""} {self.last_name or ""}'.strip()
    return name or self.email
