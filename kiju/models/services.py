from django.contrib.gis.db.models.fields import PointField
from django.db.models import (
  CASCADE,
  BooleanField,
  CharField,
  EmailField,
  FloatField,
  ForeignKey,
  ImageField,
  IntegerField,
  ManyToManyField,
  TextField,
)

from .base import Base, Host, Law, Tag, TargetGroup, Topic


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
  tags = ManyToManyField(
    to=Tag,
    verbose_name='Schlagworte',
    blank=True,
    related_name='services',
  )
  geometry = PointField('Geometrie', srid=25833, default='POINT(0 0)')
  street = CharField(
    max_length=150,
    verbose_name='Straße und Hausnummer',
    null=True,
    blank=True,
  )
  zip = IntegerField(
    verbose_name='PLZ',
    null=True,
    blank=True,
  )
  city = CharField(
    max_length=100,
    verbose_name='Stadt',
    null=True,
    blank=True,
  )
  email = EmailField(max_length=255, verbose_name='E-Mail')
  host = ForeignKey(to=Host, verbose_name='Anbieter', on_delete=CASCADE)

  def __str__(self) -> str:
    return self.name


class PreventionService(Service):
  icon = 'fa-solid fa-hand-holding-heart'
  setting = TextField(verbose_name='Beratungssetting')
  legal_basis = ManyToManyField(
    to=Law,
    verbose_name='Gesetzliche Grundlage',
    blank=True,
    related_name='prevention_services',
  )
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  costs = FloatField(verbose_name='Kosten in Euro')

  class Meta:
    verbose_name = 'Präventionsangebot'
    verbose_name_plural = 'Präventionsangebote'
