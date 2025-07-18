from django.db.models import CharField, DateTimeField, FloatField, SmallIntegerField

from .service import Service


class Ferienangebot(Service):
  time = DateTimeField(verbose_name='Zeitpunkt')
  maximum_participants = SmallIntegerField(verbose_name='max. Teilnehmende')
  costs = FloatField(verbose_name='Teilnehmerbetrag in €')
  meeting_point = CharField(verbose_name='Treffpunkt', max_length=255)

  class Meta:
    db_table = 'ferienangebote'
    verbose_name = 'Ferienangebot'
    verbose_name_plural = 'Ferienangebote'
