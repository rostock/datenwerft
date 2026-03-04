from django.contrib.gis.db.models.fields import PointField
from django.db.models import (
  CASCADE,
  SET_NULL,
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
    'description': 'Beschreibung',
    'host': 'Anbieter',
    'tags': 'Schlagworte',
    'status': 'Status',
    'updated_at': 'Zuletzt aktualisiert',
  }

  # Database fields
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
  host = ForeignKey(to=Provider, verbose_name='Anbieter', on_delete=CASCADE)
  legal_basis = ManyToManyField(
    to=Law,
    verbose_name='Gesetzliche Grundlage',
    blank=True,
    related_name='%(class)s',
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


class ChildrenAndYouthService(Service):
  """
  Angebot für Kinder und Jugendliche
  """

  # Logic Attributes
  icon = 'fa-solid fa-hand-holding-heart'

  # Database Fields
  setting = TextField(verbose_name='Beratungssetting')
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  costs = FloatField(verbose_name='Kosten in Euro')

  class Meta:
    verbose_name = 'Angebot für Kinder und Jugendliche'
    verbose_name_plural = 'Angebote für Kinder und Jugendliche'


class FamilyService(Service):
  """
  Angebot für Familien
  """

  # Logic Attributes
  icon = 'fa-solid fa-hand-holding-heart'

  # Database Fields
  setting = TextField(verbose_name='Beratungssetting')
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  costs = FloatField(verbose_name='Kosten in Euro')

  class Meta:
    verbose_name = 'Angebot für Familien'
    verbose_name_plural = 'Angebote für Familien'


class WoftGService(Service):
  """
  Angebot im Rahmen des WoftG.
  """

  # Logic Attributes
  icon = 'fa-solid fa-hand-holding-heart'

  # Database Fields
  setting = TextField(verbose_name='Beratungssetting')
  application_needed = BooleanField(verbose_name='Antrag erforderlich?')
  phone = CharField(max_length=255, verbose_name='Telefonnummer')
  costs = FloatField(verbose_name='Kosten in Euro')
  handicap_accessible = BooleanField(verbose_name='Barrierefreier Zugang?')

  class Meta:
    verbose_name = 'Angebot im Rahmen des WoftG'
    verbose_name_plural = 'Angebote im Rahmen des WoftG'
