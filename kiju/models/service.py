from django.contrib.gis.db.models.fields import PointField
from django.db.models import (
  CASCADE,
  AutoField,
  CharField,
  EmailField,
  ForeignKey,
  ImageField,
  Model,
  TextField,
)

from .host import Host
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

  def __str__(self):
    return self.name
