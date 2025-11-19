from django.contrib.gis.db.models.fields import PointField
from django.db.models import (
  CASCADE,
  AutoField,
  BooleanField,
  CharField,
  DateTimeField,
  EmailField,
  FloatField,
  ForeignKey,
  ImageField,
  ManyToManyField,
  Model,
  SmallIntegerField,
  TextField,
)

from .host import Host
from .law import Law
from .topic import Topic


class Service(Model):
  id = AutoField(primary_key=True, verbose_name='ID')
  name = CharField(max_length=255, verbose_name='Name')
  description = TextField(verbose_name='Beschreibung')
  image = ImageField(upload_to='services/', verbose_name='Bild')
  topic = ForeignKey(to=Topic, on_delete=CASCADE)
  geometrie = PointField('Geometrie', srid=25833, default='POINT(0 0)')
  email = EmailField(max_length=255, verbose_name='E-Mail')
  host = ForeignKey(to=Host, on_delete=CASCADE)

  def __str__(self) -> str:
    return self.name


class HolidayService(Service):
  time = DateTimeField(verbose_name='Zeitpunkt')
  maximum_participants = SmallIntegerField(verbose_name='max. Teilnehmende')
  costs = FloatField(verbose_name='Teilnehmerbetrag in €')
  meeting_point = CharField(verbose_name='Treffpunkt', max_length=255)

  class Meta:
    db_table: str = 'ferienangebote'
    verbose_name: str = 'Ferienangebot'
    verbose_name_plural: str = 'Ferienangebote'


class PreventionService(Service):
  setting = TextField(verbose_name='Beratungssetting')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  legal_basis = ManyToManyField(to=Law, verbose_name='Gesetzliche Grundlage')
  costs = FloatField(verbose_name='Kosten in Euro')
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')

  class Meta:
    verbose_name = 'Angebot'
    verbose_name_plural = 'Angebote'
