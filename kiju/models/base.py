from django.contrib.gis.db.models.fields import PointField
from django.db.models import (
  CASCADE,
  AutoField,
  CharField,
  DateTimeField,
  EmailField,
  ForeignKey,
  ImageField,
  ManyToManyField,
  Model,
  TextField,
)


class Base(Model):
  id = AutoField(verbose_name='ID', primary_key=True, editable=False)
  created_at = DateTimeField(verbose_name='Erstellung', auto_now_add=True, editable=False)
  updated_at = DateTimeField(verbose_name='letzte Änderung', auto_now=True, editable=False)

  class Meta:
    abstract = True
    get_latest_by = 'updated_at'
    ordering = ['-updated_at']


class Topic(Base):
  name = CharField(max_length=255, verbose_name='Bezeichnung')

  class Meta:  # type: ignore
    db_table = 'topic'
    verbose_name = 'Kategorie'
    verbose_name_plural = 'Kategorien'

  def __str__(self):
    return str(self.name)


class Host(Base):
  name = CharField(max_length=255, verbose_name='Bezeichnung')
  description = TextField(verbose_name='Beschreibung')
  logo = ImageField(upload_to='hosts/', verbose_name='Logo')
  address = CharField(max_length=255, verbose_name='Adresse')
  contact_person = CharField(max_length=255, verbose_name='Ansprechpartner')
  email = EmailField(max_length=255, verbose_name='E-Mail')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')

  class Meta:  # type: ignore
    db_table = 'host'
    verbose_name = 'Anbietender'
    verbose_name_plural = 'Anbietende'

  def __str__(self):
    return str(self.name)


class Service(Base):
  name = CharField(max_length=255, verbose_name='Name')
  description = TextField(verbose_name='Beschreibung', blank=True, null=True)
  image = ImageField(upload_to='services/', verbose_name='Bild', blank=True, null=True)
  # topic = ForeignKey(to=Topic, on_delete=CASCADE)
  topics = ManyToManyField(verbose_name='Kategorien', to=Topic, blank=True)
  geometrie = PointField('Geometrie', srid=25833, default='POINT(0 0)')
  email = EmailField(max_length=255, verbose_name='E-Mail')
  host = ForeignKey(to=Host, on_delete=CASCADE)

  def __str__(self):
    return str(self.name)
