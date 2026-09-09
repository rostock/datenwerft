from django.db import models
from django.db.models.fields import CharField, IntegerField
from django.utils.translation import gettext_lazy as _

from toolbox.constants_vars import standard_validators


class Candidate(models.Model):
  """
  Kandidat:in
  """

  id = IntegerField(primary_key=True, editable=False)
  name = CharField(verbose_name=_('Name'), max_length=200, validators=standard_validators)

  class Meta:
    managed = False
    db_table = 'wahlen"."kandidaten'
    ordering = ['name', 'id']
    verbose_name = _('Kandidat:in')
    verbose_name_plural = _('Kandidat:innen')

  class ExtendedMeta:
    table_fields = {
      'id': _('ID'),
      'name': _('Name'),
    }

  def __str__(self):
    return f'{self.name}'


class PoliticalParty(models.Model):
  """
  Partei
  """

  id = CharField(max_length=30, primary_key=True, editable=False)
  name = CharField(verbose_name=_('Anzeigename'), max_length=100, validators=standard_validators)
  short_name = CharField(
    verbose_name=_('Kurzname'),
    db_column='kurzname',
    max_length=30,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  farbe = CharField(
    verbose_name=_('Farbe'),
    db_column='farbe',
    max_length=7,
    blank=True,
    null=True,
  )

  class Meta:
    managed = False
    db_table = 'public"."parteien'
    ordering = ['name', 'id']
    verbose_name = _('Partei')
    verbose_name_plural = _('Parteien')

  class ExtendedMeta:
    table_fields = {
      'id': _('ID'),
      'name': _('Anzeigename'),
      'short_name': _('Kurzname'),
    }

  def __str__(self):
    return f'{self.name}'
