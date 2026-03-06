from decimal import Decimal

from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import CASCADE, ForeignKey, Model, OneToOneField, PROTECT
from django.db.models.fields import AutoField, BooleanField, CharField, IntegerField, DecimalField


class DatabaseConnection(Model):
  id = AutoField(primary_key=True)
  host = CharField(verbose_name='Host', max_length=255)
  port = IntegerField(verbose_name='Port')
  dbname = CharField(verbose_name='Datenbank', max_length=1024)
  user = CharField(verbose_name='Username', max_length=1024)
  password = CharField(verbose_name='Passwort', max_length=1024)

  class Meta:
    verbose_name = 'Datenbankverbindung'
    verbose_name_plural = 'Datenbankverbindungen'
    db_table = 'pygeoapi_database_connection'

  def __str__(self):
    return f'{self.id})'

class Collection(Model):
  id = AutoField(primary_key=True)
  model = OneToOneField(
    ContentType, on_delete=CASCADE, limit_choices_to={'app_label': 'datenmanagement'}
  )
  database_connection = ForeignKey(DatabaseConnection, on_delete=PROTECT)
  name = CharField(verbose_name='Name', max_length=255, unique=True)
  title = CharField(verbose_name='Titel', max_length=255)
  description = CharField(verbose_name='Beschreibung', max_length=1024)
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
    verbose_name='Kartenbereich (Ost)'
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
    verbose_name='Kartenbereich (Süd)'
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
    verbose_name='Kartenbereich (West)'
  )
  deactivated = BooleanField(verbose_name='deaktiviert')

  class Meta:
    verbose_name = 'Collection'
    verbose_name_plural = 'Collections'
    db_table = 'pygeoapi_collection'

  def __str__(self):
    return f'{self.id})'

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
