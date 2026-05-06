from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.fields import BooleanField, CharField, PositiveSmallIntegerField, TextField
from django.utils.translation import gettext_lazy as _

from toolbox.constants_vars import standard_validators
from toolbox.fields import NullTextField


class FilteredTopicManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().filter(topic=None)


class FilteredCategoryManager(models.Manager):
  def get_queryset(self):
    return super().get_queryset().exclude(topic=None)


class Topic(models.Model):
  """
  Themenbereich
  """

  id = CharField(max_length=50, primary_key=True, editable=False)
  name = CharField(verbose_name=_('Anzeigename'), max_length=200, validators=standard_validators)
  topic = models.ForeignKey(
    to='self',
    on_delete=models.RESTRICT,
    db_column='parent_id',
    related_name='topic_topics',
    editable=False,
  )
  sorting = PositiveSmallIntegerField(
    verbose_name=_('Sortierung'), db_column='sortierung', validators=[MinValueValidator(0)]
  )

  objects = FilteredTopicManager()

  class Meta:
    managed = False
    db_table = 'metadaten"."kategorien'
    ordering = ['sorting']
    verbose_name = _('Themenbereich')
    verbose_name_plural = _('Themenbereiche')

  class ExtendedMeta:
    table_fields = {
      'name': _('Anzeigename'),
      'sorting': _('Sortierung'),
    }

  def __str__(self):
    return f'{self.name}'


class Category(models.Model):
  """
  Kategorie
  """

  id = CharField(max_length=50, primary_key=True, editable=False)
  name = CharField(verbose_name=_('Anzeigename'), max_length=200, validators=standard_validators)
  topic = models.ForeignKey(
    to=Topic,
    on_delete=models.RESTRICT,
    db_column='parent_id',
    related_name='category_topics',
    verbose_name=_('Themenbereich'),
  )
  sorting = PositiveSmallIntegerField(
    verbose_name=_('Sortierung'), db_column='sortierung', validators=[MinValueValidator(0)]
  )

  objects = FilteredCategoryManager()

  class Meta:
    managed = False
    db_table = 'metadaten"."kategorien'
    ordering = ['topic', 'sorting']
    verbose_name = _('Kategorie')
    verbose_name_plural = _('Kategorien')

  class ExtendedMeta:
    table_fields = {
      'name': _('Anzeigename'),
      'topic': _('Themenbereich'),
      'sorting': _('Sortierung'),
    }

  def __str__(self):
    return f'{self.topic} → {self.name}'


class Source(models.Model):
  """
  Quellenangabe
  """

  id = CharField(max_length=50, primary_key=True, editable=False)
  name = CharField(verbose_name=_('Anzeigename'), max_length=500, validators=standard_validators)
  short_name = CharField(
    verbose_name=_('Kurzname'),
    db_column='kurzname',
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
      'name': _('Anzeigename'),
      'short_name': _('Kurzname'),
    }

  def __str__(self):
    return f'{self.name}'


class Indicator(models.Model):
  """
  Indikator
  """

  id = CharField(max_length=150, primary_key=True, editable=False)
  active = BooleanField(verbose_name=' aktiv?', db_column='aktiv')
  category = models.ForeignKey(
    to=Category,
    on_delete=models.RESTRICT,
    db_column='kategorie_id',
    related_name='indicator_categories',
    verbose_name=_('Kategorie'),
  )
  name = CharField(
    verbose_name=_('Anzeigename'),
    db_column='anzeige_name',
    max_length=300,
    validators=standard_validators,
  )
  description = TextField(
    verbose_name=_('Beschreibung'), db_column='beschreibung', validators=standard_validators
  )
  hint = NullTextField(
    verbose_name=_('Hinweis'),
    db_column='hinweis',
    blank=True,
    null=True,
    validators=standard_validators,
  )
  absolute_values_description = NullTextField(
    verbose_name=_('Beschreibung der Absolutwerte'),
    db_column='absolutwerte_beschreibung',
    blank=True,
    null=True,
    validators=standard_validators,
  )
  uom = CharField(
    verbose_name=_('Einheit'),
    db_column='einheit',
    max_length=50,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  source = models.ForeignKey(
    to=Source,
    on_delete=models.RESTRICT,
    db_column='quelle_id',
    blank=True,
    null=True,
    related_name='indicator_sourcess',
    verbose_name=_('Quellenangabe'),
  )
  deadline = CharField(
    verbose_name=_('Stichtag'),
    db_column='stichtag',
    max_length=50,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  sorting = PositiveSmallIntegerField(
    verbose_name=_('Sortierung'),
    db_column='sortierung',
    unique=True,
    validators=[MinValueValidator(0)],
  )

  class Meta:
    managed = False
    db_table = 'metadaten"."indikatoren'
    ordering = ['category', 'sorting']
    verbose_name = _('Indikator')
    verbose_name_plural = _('Indikatoren')

  class ExtendedMeta:
    table_fields = {
      'active': _('aktiv?'),
      'category': _('Kategorie'),
      'name': _('Anzeigename'),
      'uom': _('Einheit'),
      'deadline': _('Stichtag'),
      'sorting': _('Sortierung'),
    }

  def __str__(self):
    return f'{self.category} → {self.name}'
