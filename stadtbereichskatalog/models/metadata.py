from django.db import models
from django.db.models.fields import CharField, IntegerField
from django.utils.translation import gettext_lazy as _

from toolbox.constants_vars import standard_validators


class Category(models.Model):
  """
  Themenbereich und/oder Kategorie
  """

  id = CharField(verbose_name=_('ID'), max_length=50, primary_key=True, editable=False)
  name = CharField(verbose_name=_('Name'), max_length=200, validators=standard_validators)
  parent = models.ForeignKey(
    'self',
    on_delete=models.RESTRICT,
    db_column='parent_id',
    null=True,
    blank=True,
    related_name='category_children',
    verbose_name=_('Themenbereich'),
  )
  sortierung = IntegerField(verbose_name=_('Sortierung'))

  class Meta:
    managed = False
    db_table = 'metadaten"."kategorien'
    ordering = ['name', 'id']
    verbose_name = _('Themenbereich und/oder Kategorie')
    verbose_name_plural = _('Themenbereiche und Kategorien')

  class ExtendedMeta:
    table_fields = {
      'name': _('Name'),
      'parent': _('Themenbereich'),
      'sortierung': _('Sortierung'),
    }

  def __str__(self):
    return f'{self.parent.name} → {self.name}' if self.parent else f'{self.name}'


class Source(models.Model):
  """
  Quellenangabe
  """

  id = CharField(verbose_name=_('ID'), max_length=50, primary_key=True, editable=False)
  name = CharField(verbose_name=_('Name'), max_length=500, validators=standard_validators)
  kurzname = CharField(
    verbose_name=_('Kurzname'),
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )

  class Meta:
    managed = False
    db_table = 'metadaten"."quellen'
    ordering = ['name', 'id']
    verbose_name = _('Quellenangabe')
    verbose_name_plural = _('Quellenangaben')

  class ExtendedMeta:
    table_fields = {
      'name': _('Name'),
      'kurzname': _('Kurzname'),
    }

  def __str__(self):
    return f'{self.name}'
