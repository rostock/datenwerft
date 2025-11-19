from django.contrib.gis.db.models.fields import PointField
from django.db.models import (
  CASCADE,
  BooleanField,
  CharField,
  DateTimeField,
  EmailField,
  FloatField,
  ForeignKey,
  ImageField,
  ManyToManyField,
  SmallIntegerField,
  TextField,
)

from .base import Base, Host, Law, TargetGroup, Topic


class Service(Base):
  name = CharField(max_length=255, verbose_name='Name')
  description = TextField(verbose_name='Beschreibung')
  image = ImageField(
    upload_to='services/',
    verbose_name='Bild',
    null=True,
    blank=True,
  )
  topic = ManyToManyField(
    to=Topic,
    verbose_name='Kategorie(n)',
    blank=True,
    related_name='services',
  )
  target_group = ManyToManyField(
    to=TargetGroup,
    verbose_name='Zielgruppe(n)',
    blank=True,
    related_name='services',
  )
  geometry = PointField('Geometrie', srid=25833, default='POINT(0 0)')
  email = EmailField(max_length=255, verbose_name='E-Mail')
  host = ForeignKey(to=Host, verbose_name='Anbieter', on_delete=CASCADE)

  def __str__(self) -> str:
    return self.name


class HolidayService(Service):
  icon = 'fa-solid fa-people-roof'
  time = DateTimeField(verbose_name='Zeitpunkt')
  maximum_participants = SmallIntegerField(verbose_name='max. Teilnehmende')
  costs = FloatField(verbose_name='Teilnehmerbetrag in €')
  meeting_point = CharField(verbose_name='Treffpunkt', max_length=255)

  class Meta:
    db_table: str = 'ferienangebote'
    verbose_name: str = 'Ferienangebot'
    verbose_name_plural: str = 'Ferienangebote'


class PreventionService(Service):
  icon = 'fa-solid fa-hand-holding-heart'
  setting = TextField(verbose_name='Beratungssetting')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  legal_basis = ManyToManyField(
    to=Law,
    verbose_name='Gesetzliche Grundlage',
    blank=True,
    related_name='prevention_services',
  )
  costs = FloatField(verbose_name='Kosten in Euro')
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')

  class Meta:
    verbose_name = 'Präventionsangebot'
    verbose_name_plural = 'Präventionsangebote'
