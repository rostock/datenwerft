from django.db.models import PROTECT, ForeignKey, Model, TextChoices
from django.db.models.fields import (
  AutoField,
  BigIntegerField,
  BooleanField,
  CharField,
  PositiveSmallIntegerField,
)
from django.utils.translation import gettext_lazy as _


class StorageCrs(TextChoices):
  EPSG_25833 = 'https://www.opengis.net/def/crs/EPSG/0/25833', _('EPSG:25833')
  EPSG_4326 = 'https://www.opengis.net/def/crs/EPSG/0/4326', _('EPSG:4326')
  CRS_84 = 'https://www.opengis.net/def/crs/OGC/0/CRS84', _('CRS:84')


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
  database_connection = ForeignKey(
    DatabaseConnection,
    on_delete=PROTECT,
    related_name='collection_database_connections',
    verbose_name=_('Datenbankquelle'),
  )
  schema = CharField(verbose_name=_('Name des Schemas in der Datenbankquelle'), max_length=100)
  table = CharField(
    verbose_name=_('Name der/des Tabelle/Views in der Datenbankquelle'), max_length=100
  )
  id_field = CharField(verbose_name=_('Name des ID-Attributs in der Datenquelle'), max_length=100)
  title_field = CharField(
    verbose_name=_(
      'Name des Attributs mit (möglichst eindeutiger) Bezeichnung in der Datenquelle'
    ),
    max_length=100,
  )
  geom_field = CharField(
    verbose_name=_('Name des Geometrie-Attributs in der Datenquelle'), max_length=100
  )
  storage_crs = CharField(
    choices=StorageCrs.choices,
    verbose_name=_('Koordinatenreferenzsystem der Geometrie in der Datenquelle'),
  )
  deactivated = BooleanField(verbose_name='deaktiviert')

  class Meta:
    db_table = 'pygeoapi_collection'
    ordering = ['service_id']
    verbose_name = _('Kollektion')
    verbose_name_plural = _('Kollektionen')

  def __str__(self):
    return f'{self.id}'
