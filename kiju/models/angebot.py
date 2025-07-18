from django.db.models import BooleanField, CharField, FloatField, TextField

from .service import Service


class Angebot(Service):
  setting = TextField(verbose_name='Beratungssetting')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  legal_basis = CharField(max_length=255, verbose_name='Gesetzliche Grundlage')
  costs = FloatField(verbose_name='Kosten in Euro')
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')

  class Meta:
    verbose_name = 'Angebot'
    verbose_name_plural = 'Angebote'
