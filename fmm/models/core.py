from django.contrib.gis.db.models.fields import MultiPolygonField
from django.db import models
from django.utils.translation import gettext_lazy as _

from toolbox.constants_vars import standard_validators

from .abstract import Base


class Stammpaket(Base):
  """
  Stammpaket
  """

  bezeichnung = models.CharField(
    unique=True, validators=standard_validators, verbose_name=_('Bezeichnung')
  )
  geometrie = MultiPolygonField(verbose_name=_('Flächengeometrie'))

  class Meta(Base.Meta):
    ordering = ['bezeichnung']
    verbose_name = _('Stammpaket')
    verbose_name_plural = _('Stammpakete')

  def __str__(self):
    return f'{self.bezeichnung}'


class InformationspaketUmwelt(Base):
  """
  Informationspaket Umwelt
  """

  stammpaket = models.ForeignKey(
    Stammpaket,
    on_delete=models.CASCADE,
    related_name='informationspaketumwelt_stammpakete',
    verbose_name=_('Stammpaket'),
  )
  trinkwassernotbrunnen = models.BooleanField(verbose_name=_('Trinkwassernotbrunnen'))

  class Meta(Base.Meta):
    ordering = ['stammpaket', '-modified']
    verbose_name = _('Informationspaket Umwelt')
    verbose_name_plural = _('Informationspakete Umwelt')

  def __str__(self):
    created = f'erstellt am {self.created.strftime("%d.%m.%Y")}'
    modified = f'geändert am {self.modified.strftime("%d.%m.%Y")}'
    return f'{self.stammpaket.bezeichnung} → Informationspaket Umwelt ({created}, {modified})'
