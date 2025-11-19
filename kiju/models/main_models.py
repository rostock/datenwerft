from django.db.models import (
  BooleanField,
  CharField,
  DateTimeField,
  FloatField,
  SmallIntegerField,
  TextField,
)

from .base import Service


class Angebot(Service):
  setting = TextField(
    verbose_name='Beratungssetting',
    blank=True,
    null=True,
  )
  phone = CharField(
    max_length=255,
    verbose_name='Telefonnummer',
    blank=True,
    null=True,
  )
  legal_basis = CharField(
    max_length=255,
    verbose_name='Gesetzliche Grundlage',
    blank=True,
    null=True,
  )
  costs = FloatField(
    verbose_name='Kosten in Euro',
    blank=True,
    null=True,
  )
  application_needed = BooleanField(
    verbose_name='Antrag erforderlich?',
    default=False,
  )

  class Meta:  # type: ignore
    db_table = 'angebot'
    verbose_name = 'Angebot'
    verbose_name_plural = 'Angebote'


class Ferienangebot(Service):
  time = DateTimeField(
    verbose_name='Zeitpunkt',
    blank=True,
    null=True,
  )
  maximum_participants = SmallIntegerField(
    verbose_name='max. Teilnehmende',
    blank=True,
    null=True,
  )
  costs = FloatField(
    verbose_name='Teilnehmerbetrag in €',
    blank=True,
    null=True,
  )
  meeting_point: CharField = CharField(
    verbose_name='Alternativer Treffpunkt',
    max_length=255,
    blank=True,
    null=True,
  )

  class Meta:  # type: ignore
    db_table = 'ferienangebot'
    verbose_name = 'Ferienangebot'
    verbose_name_plural = 'Ferienangebote'
