from django.contrib.auth.models import User
from django.db.models import (
  CASCADE,
  SET_NULL,
  AutoField,
  CharField,
  DateTimeField,
  EmailField,
  ForeignKey,
  ImageField,
  IntegerField,
  ManyToManyField,
  Model,
  OneToOneField,
  TextField,
)


class Base(Model):
  id = AutoField(verbose_name='ID', primary_key=True, editable=False)
  created_at = DateTimeField(
    verbose_name='Erstellung',
    auto_now_add=True,
    editable=False,
  )
  updated_at = DateTimeField(verbose_name='letzte Änderung', auto_now=True, editable=False)

  list_fields = {
    '__str__': 'Bezeichnung',
    'updated_at': 'Zuletzt aktualisiert',
  }

  class Meta:
    abstract = True
    get_latest_by = 'updated_at'
    ordering = ['-updated_at']


class Topic(Base):
  icon = 'fa-solid fa-folder'
  icon_plural = 'fa-solid fa-folder-tree'
  name = CharField(max_length=255, verbose_name='Bezeichnung')

  class Meta:  # type: ignore
    db_table = 'topic'
    verbose_name = 'Kategorie'
    verbose_name_plural = 'Kategorien'

  def __str__(self):
    return str(self.name)


class Provider(Base):
  icon = 'fa-solid fa-handshake'
  name = CharField(max_length=255, verbose_name='Bezeichnung')
  description = TextField(
    verbose_name='Beschreibung',
    null=True,
    blank=True,
  )
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
  email = EmailField(
    max_length=255,
    verbose_name='E-Mail',
    null=True,
    blank=True,
  )
  phone = CharField(max_length=255, verbose_name='Telefonnummer', null=True, blank=True)

  class Meta:  # type: ignore
    db_table = 'provider'
    verbose_name = 'Träger'
    verbose_name_plural = 'Träger'

  def __str__(self):
    return str(self.name)


class Host(Base):
  icon = 'fa-regular fa-building'
  name = CharField(max_length=255, verbose_name='Bezeichnung')
  provider = ForeignKey(
    'Provider',
    on_delete=CASCADE,
    related_name='hosts',
    verbose_name='Träger',
    null=True,
    blank=True,
  )
  description = TextField(
    verbose_name='Beschreibung',
    null=True,
    blank=True,
  )
  logo = ImageField(
    upload_to='hosts/',
    verbose_name='Logo',
    null=True,
    blank=True,
  )
  address = CharField(max_length=255, verbose_name='Adresse', null=True, blank=True)
  contact_person = CharField(max_length=255, verbose_name='Ansprechpartner', null=True, blank=True)
  email = EmailField(max_length=255, verbose_name='E-Mail', null=True, blank=True)
  phone = CharField(max_length=255, verbose_name='Telefonnummer', null=True, blank=True)

  class Meta:  # type: ignore
    db_table = 'host'
    verbose_name = 'Einrichtung'
    verbose_name_plural = 'Einrichtungen'

  def __str__(self):
    return str(self.name)


class Law(Base):
  icon = 'fa-solid fa-scale-balanced'
  law_book = CharField(
    verbose_name='Gesetzesbuch (Abkürzung, z.B. SGB VIII)',
    max_length=25,
    blank=False,
    null=False,
  )
  paragraph = CharField(
    verbose_name='Paragraph (ohne §, z.B. 8a)',
    max_length=25,
    blank=False,
    null=False,
  )

  class Meta:
    db_table = 'law'
    verbose_name = 'Gesetz'
    verbose_name_plural = 'Gesetze'

  def __str__(self):
    return f'§{self.paragraph} {self.law_book}'


class TargetGroup(Base):
  icon = 'fa-solid fa-users-viewfinder'
  name = CharField(
    verbose_name='Zielgruppe',
    max_length=100,
    blank=False,
    null=False,
  )

  class Meta:
    db_table = 'target_group'
    verbose_name = 'Zielgruppe'
    verbose_name_plural = 'Zielgruppen'

  def __str__(self):
    return self.name


class Tag(Base):
  icon = 'fa-solid fa-tag'
  icon_plural = 'fa-solid fa-tags'
  name = CharField(max_length=100, verbose_name='Bezeichnung', unique=True)

  class Meta:
    db_table = 'tag'
    verbose_name = 'Schlagwort'
    verbose_name_plural = 'Schlagworte'

  def __str__(self):
    return self.name


class OrgUnit(Base):
  """
  Organizational Unit (OE) for grouping users of the local administration.
  Each OE is responsible for reviewing specific types of services.
  """

  icon = 'fa-solid fa-sitemap'

  name = CharField(
    max_length=255,
    verbose_name='Bezeichnung',
    unique=True,
  )
  description = TextField(
    verbose_name='Beschreibung',
    null=True,
    blank=True,
  )
  created_at = DateTimeField(
    verbose_name='Erstellung',
    auto_now_add=True,
    editable=False,
  )
  updated_at = DateTimeField(
    verbose_name='letzte Änderung',
    auto_now=True,
    editable=False,
  )

  class Meta:
    db_table = 'kiju_organisational_unit'
    verbose_name = 'Organisationseinheit'
    verbose_name_plural = 'Organisationseinheiten'
    ordering = ['name']

  def __str__(self):
    return self.name


class UserProfile(Model):
  """
  Extended user profile for Kiju application.
  Links users to Hosts (for facility users) and OE (for admin users).
  """

  user = OneToOneField(
    User,
    on_delete=CASCADE,
    primary_key=True,
    related_name='kiju_profile',
    verbose_name='Benutzer',
  )
  host = ForeignKey(
    'kiju.Host',
    on_delete=SET_NULL,
    null=True,
    blank=True,
    related_name='facility_users',
    verbose_name='Einrichtung',
    help_text='Einrichtung für Einrichtungsnutzer',
  )
  organisational_units = ManyToManyField(
    'kiju.OrganisationalUnit',
    blank=True,
    related_name='admin_users',
    verbose_name='Organisationseinheiten',
    help_text='OE für Verwaltungsnutzer',
  )
  created_at = DateTimeField(
    verbose_name='Erstellung',
    auto_now_add=True,
    editable=False,
  )
  updated_at = DateTimeField(
    verbose_name='letzte Änderung',
    auto_now=True,
    editable=False,
  )

  class Meta:
    db_table = 'kiju_user_profile'
    verbose_name = 'Benutzerprofil'
    verbose_name_plural = 'Benutzerprofile'

  def __str__(self):
    return f'Profil für {self.user.username}'

  def is_facility_user(self):
    """Check if user is a facility user (has a host assigned)"""
    return self.host is not None

  def is_admin_user(self):
    """Check if user is an admin user (has OE assigned)"""
    return self.organisational_units.exists()
