from uuid import uuid4

from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from toolbox.constants_vars import (
  kleinbuchstaben_bindestrich_message,
  kleinbuchstaben_bindestrich_regex,
  standard_validators,
)
from toolbox.fields import NullTextField


class Base(models.Model):
  """
  default abstract model class
  """

  id = models.BigAutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  created = models.DateTimeField(verbose_name=_('Erstellung'), auto_now_add=True, editable=False)
  modified = models.DateTimeField(verbose_name=_('Änderung'), auto_now=True, editable=False)
  uuid = models.UUIDField(default=uuid4, editable=False, unique=True, verbose_name=_('UUID'))

  class Meta:
    abstract = True
    ordering = ['-created']
    get_latest_by = 'modified'


class Codelist(Base):
  """
  codelist (Codeliste)
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

  class Meta(Base.Meta):
    ordering = ['title', 'name']
    verbose_name = _('Codeliste')
    verbose_name_plural = _('Codelisten')

  def __str__(self):
    return f'{self.title} ({self.name})'


class CodelistValue(Base):
  """
  codelist value (Codelistenwert)
  """

  codelist = models.ForeignKey(
    Codelist,
    on_delete=models.CASCADE,
    related_name='codelistvalue_codelists',
    verbose_name=_('Codeliste'),
  )
  value = models.CharField(
    validators=[
      RegexValidator(
        regex=kleinbuchstaben_bindestrich_regex, message=kleinbuchstaben_bindestrich_message
      )
    ],
    verbose_name=_('Wert'),
  )
  parent = models.ForeignKey(
    'self',
    on_delete=models.CASCADE,
    blank=True,
    null=True,
    related_name='codelistvalue_codelistvalues',
    verbose_name=_('Elternelement'),
  )
  ordinal = models.PositiveSmallIntegerField(blank=True, null=True, verbose_name=_('Ordinalzahl'))
  title = models.CharField(
    blank=True, null=True, validators=standard_validators, verbose_name=_('Titel')
  )
  description = NullTextField(
    blank=True, null=True, validators=standard_validators, verbose_name=_('Beschreibung')
  )
  details = models.JSONField(blank=True, null=True, verbose_name=_('Details'))

  class Meta(Base.Meta):
    unique_together = ['codelist', 'value']
    ordering = ['codelist', 'title', 'value']
    verbose_name = _('Codelistenwert')
    verbose_name_plural = _('Codelistenwerte')

  def __str__(self):
    return f'{self.codelist.title} ({self.codelist.name}) → {self.title} ({self.value})'
