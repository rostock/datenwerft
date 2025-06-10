from django.contrib.gis.db.models.fields import MultiPolygonField
from django.db import models
from django.utils.translation import gettext_lazy as _

from toolbox.constants_vars import standard_validators

from .abstract import Base


class Fmf(Base):
  """
  FMF
  """

  bezeichnung = models.CharField(
    unique=True, validators=standard_validators, verbose_name=_('Bezeichnung')
  )
  geometrie = MultiPolygonField(verbose_name=_('Flächengeometrie'))

  class Meta(Base.Meta):
    ordering = ['bezeichnung']
    verbose_name = _('FMF')
    verbose_name_plural = _('FMF')

  class BaseMeta(Base.BaseMeta):
    geometry_field = 'geometrie'
    geometry_type = 'MultiPolygon'

  def __str__(self):
    return f'{self.bezeichnung}'


class PaketUmwelt(Base):
  """
  Paket Umwelt
  """

  fmf = models.ForeignKey(
    Fmf,
    on_delete=models.CASCADE,
    related_name='informationspaketumwelt_fmf',
    verbose_name=_('FMF'),
  )
  trinkwassernotbrunnen = models.BooleanField(verbose_name=_('Trinkwassernotbrunnen'))

  class Meta(Base.Meta):
    ordering = ['fmf', '-modified']
    verbose_name = _('Paket Umwelt')
    verbose_name_plural = _('Pakete Umwelt')

  def __str__(self):
    created = f'erstellt am {self.created.strftime("%d.%m.%Y")}'
    modified = f'geändert am {self.modified.strftime("%d.%m.%Y")}'
    return f'{self.fmf.bezeichnung} → Paket Umwelt ({created}, {modified})'
