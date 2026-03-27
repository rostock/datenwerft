from django.contrib.gis.db.models.fields import PointField
from django.db.models import (
  CASCADE,
  SET_NULL,
  BooleanField,
  CharField,
  DateField,
  EmailField,
  FloatField,
  ForeignKey,
  ImageField,
  IntegerField,
  JSONField,
  ManyToManyField,
  TextField,
  URLField,
)

from .base import Base, Law, Provider, Tag, TargetGroup, Topic

SERVICE_STATUS_CHOICES = [
  ('draft', 'Entwurf'),
  ('in_review', 'In Prüfung'),
  ('revision_needed', 'Überarbeitung nötig'),
  ('published', 'Veröffentlicht'),
]


class Service(Base):
  """
  Abstrakte Basisklasse für alle Service-Modelle (Angebote).
  """

  # Logical attributes
  list_fields = {
    'name': 'Name',
    'status': 'Status',
    'host': 'Anbieter',
    'tags': 'Schlagworte',
    'updated_at': 'Zuletzt aktualisiert',
  }

  # Database fields
  name = CharField(max_length=255, verbose_name='Name')
  description = TextField(verbose_name='Beschreibung')
  topic = ManyToManyField(
    to=Topic,
    verbose_name='Kategorie(n)',
    related_name='%(class)s',
  )
  target_group = ManyToManyField(
    to=TargetGroup,
    verbose_name='Zielgruppe(n)',
    blank=True,
    related_name='%(class)s',
  )
  tags = ManyToManyField(
    to=Tag,
    verbose_name='Schlagworte',
    blank=True,
    related_name='%(class)s',
  )
  geometry = PointField('Geometrie', srid=25833, default='POINT(0 0)')
  street = CharField(
    max_length=150,
    verbose_name='Straße und Hausnummer',
  )
  zip = IntegerField(
    verbose_name='PLZ',
  )
  city = CharField(
    max_length=100,
    verbose_name='Gemeinde',
  )
  contact_hours = TextField(
    verbose_name='Kontaktzeiträume',
    null=True,
    blank=True,
    help_text='z.B. Mo Di Mi 7:30 - 15:00 Uhr, Do 8:00 - 13:00 Uhr',
  )
  email = EmailField(max_length=255, verbose_name='E-Mail')
  host = ForeignKey(to=Provider, verbose_name='Anbieter', on_delete=CASCADE)
  legal_basis = ManyToManyField(
    to=Law,
    verbose_name='Gesetzliche Grundlage',
    related_name='%(class)s',
  )
  expiry_date = DateField(
    verbose_name='Ablaufdatum',
    help_text='Datum, an dem das Angebot ausläuft.',
  )
  info_url = URLField(
    max_length=500,
    verbose_name='Weiterführender Link',
    null=True,
    blank=True,
    help_text='Externe URL für weitere Informationen (z.B. Träger-Website).',
  )
  status = CharField(
    max_length=20,
    choices=SERVICE_STATUS_CHOICES,
    default='draft',
    verbose_name='Status',
  )
  published_version = ForeignKey(
    'self',
    on_delete=SET_NULL,
    null=True,
    blank=True,
    related_name='draft_copies',
    verbose_name='Veröffentlichte Version',
    help_text=(
      'Zeigt auf den originalen published-Datensatz, von dem diese '
      'Draft-Copy abgeleitet wurde. Null bei normalen Services.'
    ),
  )

  class Meta:
    abstract = True

  def __str__(self) -> str:
    return self.name


class ServiceImage(Base):
  """
  Bild zu einem Service-Angebot.
  Referenziert den Service über service_type + service_id
  (kein GenericForeignKey wegen Cross-DB).
  """

  # Logical Attributes
  dashboard_mode = None
  _exclude_from_crud = True

  # Database Attributes
  service_type = CharField(max_length=100, verbose_name='Angebotstyp')
  service_id = IntegerField(verbose_name='Service-ID')
  image = ImageField(upload_to='angebotsdb/services/', verbose_name='Bild')
  position = IntegerField(default=0, verbose_name='Reihenfolge')

  class Meta:
    db_table = 'kiju_service_image'
    verbose_name = 'Service-Bild'
    verbose_name_plural = 'Service-Bilder'
    ordering = ['position', 'pk']

  def __str__(self):
    return f'Bild #{self.pk} für {self.service_type} #{self.service_id}'


class ChildrenAndYouthService(Service):
  """
  Angebot für Kinder und Jugendliche
  """

  # Logic Attributes
  icon = 'fa-solid fa-hand-holding-heart'
  dashboard_mode = 'tile'
  dashboard_color = 'primary'
  dashboard_admin_only = False
  PYGEOAPI_FIELDS = {
    'catchment_area_urls': {
      'endpoint': 'https://geo.sv.rostock.de/service/ogcapi/collections/gemeindeteile/items',
      'params': {'f': 'json', 'gemeinde': 'bbc6d790-2c4d-11e5-98d1-0050569b7e95'},
      'label_property': 'bezeichnung',
    }
  }

  # Database Fields
  setting = TextField(
    verbose_name='Beratungssetting',
    null=True,
    blank=True,
  )
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  costs = FloatField(verbose_name='Kosten in Euro')
  catchment_area_urls = JSONField(
    verbose_name='Einzugsgebiet',
    default=list,
    blank=True,
    help_text=(
      'Liste von PyGeoAPI-Endpunkt-URIs. Für jeden Stadtteil im Einzugsgebiet '
      'wird die entsprechende Endpunkt-URI gespeichert.'
    ),
  )

  class Meta:
    verbose_name = 'Angebot für Kinder und Jugendliche'
    verbose_name_plural = 'Angebote für Kinder und Jugendliche'


class FamilyService(Service):
  """
  Angebot für Familien
  """

  # Logic Attributes
  icon = 'fa-solid fa-hand-holding-heart'
  dashboard_mode = 'tile'
  dashboard_color = 'primary'
  dashboard_admin_only = False
  PYGEOAPI_FIELDS = {
    'catchment_area_urls': {
      'endpoint': 'https://geo.sv.rostock.de/service/ogcapi/collections/gemeindeteile/items',
      'params': {'f': 'json', 'gemeinde': 'bbc6d790-2c4d-11e5-98d1-0050569b7e95'},
      'label_property': 'bezeichnung',
    }
  }

  # Database Fields
  setting = TextField(verbose_name='Beratungssetting')
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  costs = FloatField(verbose_name='Kosten in Euro')
  catchment_area_urls = JSONField(
    verbose_name='Einzugsgebiet',
    default=list,
    blank=True,
    help_text=(
      'Liste von PyGeoAPI-Endpunkt-URIs. Für jeden Stadtteil im Einzugsgebiet '
      'wird die entsprechende Endpunkt-URI gespeichert.'
    ),
  )

  class Meta:
    verbose_name = 'Angebot für Familien'
    verbose_name_plural = 'Angebote für Familien'


class WoftGService(Service):
  """
  Angebot im Rahmen des WoftG.
  """

  # Logic Attributes
  icon = 'fa-solid fa-hand-holding-heart'
  dashboard_mode = 'tile'
  dashboard_color = 'primary'
  dashboard_admin_only = False

  # Database Fields
  setting = TextField(verbose_name='Beratungssetting')
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  costs = FloatField(verbose_name='Kosten in Euro')
  handicap_accessible = BooleanField(verbose_name='Barrierefreier Zugang?')

  class Meta:
    verbose_name = 'Angebot im Rahmen des WoftG'
    verbose_name_plural = 'Angebote im Rahmen des WoftG'
