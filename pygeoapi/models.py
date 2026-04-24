from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models import CASCADE, PROTECT, ForeignKey, Model
from django.db.models.fields import (
  AutoField,
  BigIntegerField,
  BooleanField,
  CharField,
  DecimalField,
  PositiveSmallIntegerField,
  TextField,
)
from django.utils.translation import gettext_lazy as _

from gdihrometadata.models import Service


class DatabaseConnection(Model):
  id = AutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  host = CharField(verbose_name=_('Host'), max_length=100)
  port = PositiveSmallIntegerField(verbose_name=_('Port'), default=5432)
  dbname = CharField(verbose_name=_('Datenbank'), max_length=100)
  user = CharField(verbose_name=_('Benutzername'), max_length=100)
  password = CharField(verbose_name=_('Passwort'), max_length=100)

  class Meta:
    db_table = 'pygeoapi_database_connection'
    ordering = ['host', 'dbname', 'user']
    verbose_name = _('Datenbankverbindung')
    verbose_name_plural = _('Datenbankverbindungen')

  def __str__(self):
    return f'{self.host} → {self.dbname} → {self.user}'


class Collection(Model):
  id = AutoField(verbose_name=_('ID'), primary_key=True, editable=False)
  service_id = BigIntegerField(unique=True)
  name = CharField(verbose_name=_('Name'), unique=True, max_length=100)
  title = CharField(verbose_name=_('Titel'), max_length=255)
  description = TextField(verbose_name=_('Beschreibung'))
  database_connection = ForeignKey(
    DatabaseConnection,
    on_delete=PROTECT,
    related_name='collection_database_connections',
    verbose_name=_('Datenbankverbindung'),
  )
  schema = CharField(verbose_name='Datenbank Schema', max_length=255)
  table = CharField(verbose_name='Datenbank Tabelle', max_length=255)
  id_field = CharField(verbose_name='ID Feld', max_length=255)
  geometry_field = CharField(verbose_name='Geometrie Feld', max_length=255)
  storage_crs = CharField(verbose_name='EPSG-Code des Koordinatenreferenzsystems', max_length=255)
  bbox_north = DecimalField(
    max_digits=8,
    decimal_places=5,
    validators=[
      MinValueValidator(
        Decimal('-90'),
        'Der Wert für Norden (räumliche Ausdehnung) muss mindestens -90 sein.',
      ),
      MaxValueValidator(
        Decimal('90'),
        'Der Wert für Norden (räumliche Ausdehnung) darf höchstens 90 sein.',
      ),
    ],
    verbose_name='Kartenbereich (Nord)',
  )
  bbox_east = DecimalField(
    max_digits=8,
    decimal_places=5,
    validators=[
      MinValueValidator(
        Decimal('-180'),
        'Der Wert für Osten (räumliche Ausdehnung) muss mindestens -180 sein.',
      ),
      MaxValueValidator(
        Decimal('180'),
        'Der Wert für Osten (räumliche Ausdehnung) darf höchstens 180 sein.',
      ),
    ],
    verbose_name='Kartenbereich (Ost)',
  )
  bbox_south = DecimalField(
    max_digits=8,
    decimal_places=5,
    validators=[
      MinValueValidator(
        Decimal('-90'),
        'Der Wert für Süden (räumliche Ausdehnung) muss mindestens -90 sein.',
      ),
      MaxValueValidator(
        Decimal('90'),
        'Der Wert für Süden (räumliche Ausdehnung) darf höchstens 90 sein.',
      ),
    ],
    verbose_name='Kartenbereich (Süd)',
  )
  bbox_west = DecimalField(
    max_digits=8,
    decimal_places=5,
    validators=[
      MinValueValidator(
        Decimal('-180'),
        'Der Wert für Westen (räumliche Ausdehnung) muss mindestens -180 sein.',
      ),
      MaxValueValidator(
        Decimal('180'),
        'Der Wert für Westen (räumliche Ausdehnung) darf höchstens 180 sein.',
      ),
    ],
    verbose_name='Kartenbereich (West)',
  )
  deactivated = BooleanField(verbose_name='deaktiviert')

  class Meta:
    db_table = 'pygeoapi_collection'
    ordering = ['name']
    verbose_name = _('Kollektion')
    verbose_name_plural = _('Kollektionen')

  def __str__(self):
    return f'{self.name}'


class CollectionKeyword(Model):
  id = AutoField(primary_key=True)
  collection = ForeignKey(Collection, on_delete=CASCADE)
  keyword = CharField(verbose_name='Keyword', max_length=255)

  class Meta:
    verbose_name = 'Collection Keyword'
    verbose_name_plural = 'Collection Keywords'
    db_table = 'pygeoapi_collection_keyword'

  def __str__(self):
    return f'{self.id})'


class CollectionCrs(Model):
  id = AutoField(primary_key=True)
  collection = ForeignKey(Collection, on_delete=CASCADE)
  crs = CharField(verbose_name='EPSG-Code', max_length=255)

  class Meta:
    verbose_name = 'Collection Crs'
    verbose_name_plural = 'Collection Crs'
    db_table = 'pygeoapi_collection_crs'

  def __str__(self):
    return f'{self.id})'
