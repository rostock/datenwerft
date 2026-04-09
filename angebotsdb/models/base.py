from django.apps import apps
from django.contrib.auth.models import User
from django.db.models import (
  CASCADE,
  SET_NULL,
  AutoField,
  BooleanField,
  CharField,
  DateTimeField,
  EmailField,
  ForeignKey,
  ImageField,
  IntegerField,
  JSONField,
  Model,
  TextField,
)


def get_service_type_choices():
  """
  Discovers all concrete (non-abstract) subclasses of service models at runtime and
  returns them as a choices list.

  :return: list of tuples (lowercase_model_name, verbose_name_plural),
  e.g. [('childrenandyouthservice', 'Angebote für Kinder und Jugendliche'), ...]
  """
  # avoid circular imports
  from .services import Service

  choices = []
  for model in apps.get_app_config('angebotsdb').get_models():
    if issubclass(model, Service) and not model._meta.abstract:
      choices.append(
        (
          model.__name__.lower(),
          model._meta.verbose_name_plural,
        )
      )
  return sorted(choices, key=lambda c: c[1])


class Base(Model):
  """
  Abstract base class for all domain models.
  """

  # Logical Attributes
  list_fields = {
    '__str__': 'Bezeichnung',
    'updated_at': 'Zuletzt aktualisiert',
  }

  # Database Fields
  id = AutoField(verbose_name='ID', primary_key=True, editable=False)
  created_at = DateTimeField(
    verbose_name='Erstellung',
    auto_now_add=True,
    editable=False,
  )
  updated_at = DateTimeField(verbose_name='letzte Änderung', auto_now=True, editable=False)

  class Meta:
    abstract = True
    get_latest_by = 'updated_at'
    ordering = ['-updated_at']


class Topic(Base):
  """
  Categoriers for services.
  """

  # Logical Attributes
  icon = 'fa-solid fa-folder'
  icon_plural = 'fa-solid fa-folder-tree'
  dashboard_mode = 'container_button'
  dashboard_container = 'basisdaten'

  # Database Fields
  name = CharField(max_length=255, verbose_name='Bezeichnung')

  class Meta:
    db_table = 'topic'
    verbose_name = 'Kategorie'
    verbose_name_plural = 'Kategorien'
    ordering = ['name']

  def __str__(self):
    return str(self.name)


class Provider(Base):
  """
  Anbietende Einrichtung
  """

  # Logical attributes
  icon = 'fa-regular fa-building'
  dashboard_mode = 'container_button'
  dashboard_container = 'basisdaten'

  # Database fields
  name = CharField(max_length=255, verbose_name='Bezeichnung')
  description = TextField(
    verbose_name='Beschreibung',
    null=True,
    blank=True,
  )
  logo = ImageField(
    upload_to='angebotsdb/hosts/',
    verbose_name='Logo',
    null=True,
    blank=True,
  )
  address = CharField(max_length=255, verbose_name='Adresse', null=True, blank=True)
  contact_person = CharField(max_length=255, verbose_name='Ansprechpartner', null=True, blank=True)
  email = EmailField(max_length=255, verbose_name='E-Mail', null=True, blank=True)
  phone = CharField(max_length=255, verbose_name='Telefonnummer', null=True, blank=True)

  class Meta:
    db_table = 'provider'
    verbose_name = 'Träger'
    verbose_name_plural = 'Träger'
    ordering = ['name']

  def __str__(self):
    return str(self.name)


class Law(Base):
  """
  Gesetze
  """

  # Logical Attributes
  icon = 'fa-solid fa-scale-balanced'
  dashboard_mode = 'container_button'
  dashboard_container = 'basisdaten'

  # Database fields
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
    ordering = ['law_book', 'paragraph']

  def __str__(self):
    return f'§{self.paragraph} {self.law_book}'


class TargetGroup(Base):
  """
  Zielgruppen
  """

  # Logical Attributes
  icon = 'fa-solid fa-users-viewfinder'
  dashboard_mode = 'container_button'
  dashboard_container = 'basisdaten'

  # Database fields
  name = CharField(
    verbose_name='Zielgruppe',
    max_length=100,
    blank=False,
    null=False,
    unique=True,
  )

  class Meta:
    db_table = 'target_group'
    verbose_name = 'Zielgruppe'
    verbose_name_plural = 'Zielgruppen'
    ordering = ['name']

  def __str__(self):
    return self.name


class Tag(Base):
  """
  Schlagworte
  """

  # Logical Attributes
  icon = 'fa-solid fa-tag'
  icon_plural = 'fa-solid fa-tags'
  dashboard_mode = None

  # Database fields
  name = CharField(max_length=100, verbose_name='Bezeichnung', unique=True)

  class Meta:
    db_table = 'tag'
    verbose_name = 'Schlagwort'
    verbose_name_plural = 'Schlagworte'
    ordering = ['name']

  def __str__(self):
    return self.name


class OrgUnit(Base):
  """
  Organizational Unit (OE) for grouping users of the local administration.
  Each OE is responsible for reviewing specific types of services.
  """

  # Logical Attributes
  icon = 'fa-solid fa-sitemap'
  dashboard_mode = 'container_button'
  dashboard_container = 'benutzerverwaltung'
  list_fields = {
    'name': 'Bezeichnung',
    'description': 'Beschreibung',
    'updated_at': 'Zuletzt aktualisiert',
  }

  # Database fields
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
    db_table = 'angebotsdb_organisational_unit'
    verbose_name = 'Organisationseinheit'
    verbose_name_plural = 'Organisationseinheiten'
    ordering = ['name']

  def __str__(self):
    return self.name


class OrgUnitServicePermission(Base):
  """
  Verbindung zwischen OrgUnit und Service-Klassen.
  Definiert, welche Service-Typen von einer OrgUnit bearbeitet werden können.
  """

  # Logical Attributes
  icon = 'fa-solid fa-key'
  dashboard_mode = 'container_button'
  dashboard_container = 'benutzerverwaltung'
  list_fields = {
    'organisational_unit': 'Organisationseinheit',
    'service_type': 'Angebotstyp',
    'updated_at': 'Zuletzt aktualisiert',
  }

  # Database fields
  organisational_unit = ForeignKey(
    'OrgUnit',
    on_delete=CASCADE,
    related_name='service_permissions',
    verbose_name='Organisationseinheit',
  )
  # Saves the lowercase modelsnames of the service types.
  # Because of Cross-DB-Issues, it is not saved as ForeignKey to ContentType.
  # The resolution to the model class is done by apps.get_model() (see below).
  service_type = CharField(
    max_length=100,
    verbose_name='Angebotstyp',
    choices=get_service_type_choices,
  )

  class Meta:
    db_table = 'angebotsdb_org_unit_service_permission'
    verbose_name = 'OE-Angebot-Berechtigung'
    verbose_name_plural = 'OE-Angebot-Berechtigungen'
    # Verhindert Duplikate: Eine OrgUnit kann jeden Service-Typ nur einmal haben
    unique_together = [['organisational_unit', 'service_type']]

  def __str__(self):
    # Lesbaren Anzeigenamen aus den Choices holen, Fallback auf den rohen Wert
    label = dict(get_service_type_choices()).get(self.service_type, self.service_type)
    return f'{self.organisational_unit} → {label}'

  def get_service_class(self):
    """
    Gibt die Service-Klasse anhand des gespeicherten Model-Namens zurück.
    Nutzt apps.get_model() statt ContentType.model_class(), da ContentType
    nicht Cross-DB-tauglich ist (siehe Feldkommentar service_type).
    """
    try:
      return apps.get_model('angebotsdb', self.service_type)
    except LookupError:
      return None

  def get_service_instances(self):
    """Gibt alle Instanzen des Service-Typs zurück."""
    service_class = self.get_service_class()
    if service_class:
      return service_class.objects.all()
    return None


class UserProfile(Model):
  """
  Extended user profile for angebotsdb application.
  Links users to Hosts (for facility users) and OE (for admin users).
  """

  # Logical Attributes
  administrative_model = True
  icon = 'fa-solid fa-user'
  icons_plural = 'fa-solid fa-users'
  dashboard_mode = 'container_button'
  dashboard_container = 'benutzerverwaltung'
  list_fields = {
    'user': 'Benutzer',
    'provider': 'Träger',
    'organisational_unit': 'Organisationseinheit',
    'updated_at': 'Zuletzt aktualisiert',
  }

  # Database Fields
  user_id = IntegerField(
    verbose_name='Benutzer-ID',
    unique=True,
    help_text='ID des Django Users',
  )  # needed for Cross-Database operations
  provider = ForeignKey(
    'Provider',
    on_delete=SET_NULL,
    null=True,
    blank=True,
    related_name='facility_users',
    verbose_name='Träger',
    help_text='Träger für Einrichtungsnutzer',
  )
  organisational_unit = ForeignKey(
    'OrgUnit',
    on_delete=SET_NULL,
    null=True,
    blank=True,
    related_name='admin_users',
    verbose_name='Organisationseinheit',
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
    db_table = 'user_profile'
    verbose_name = 'Benutzerprofil'
    verbose_name_plural = 'Benutzerprofile'

  def __str__(self):
    return f'Profil für {self.user.username}'

  @property
  def user(self):
    """
    Lädt den User aus der Default-Datenwerft-Datenbank.
    """
    try:
      return User.objects.using('default').get(id=self.user_id)
    except User.DoesNotExist:
      return None

  def get_username(self):
    """
    returns the username
    """
    user = self.user
    return user.username if user else self.user_id


class ReviewTask(Base):
  """
  Ein Prüfauftrag für einen Service.
  Wird erstellt, wenn ein Provider-Nutzer einen Service zur Prüfung freigibt.
  Pro Service existiert maximal ein aktiver (pending) ReviewTask.
  """

  # Logical Attributes
  icon = 'fa-solid fa-clipboard-check'
  dashboard_mode = None
  list_fields = {
    'service_type': 'Angebotstyp',
    'service_id': 'Service-ID',
    'assigned_org_unit': 'Zuständige OE',
    'task_status': 'Status',
    'updated_at': 'Zuletzt aktualisiert',
  }

  TASK_STATUS_CHOICES = [
    ('pending', 'Offen'),
    ('approved', 'Freigegeben'),
    ('rejected', 'Zurückgewiesen'),
  ]

  # Generische Referenz auf den Service (ohne ContentType wg. Cross-DB)
  service_type = CharField(
    max_length=100,
    verbose_name='Angebotstyp',
  )
  service_id = IntegerField(
    verbose_name='Service-ID',
  )

  # Zuordnung
  assigned_org_unit = ForeignKey(
    'OrgUnit',
    on_delete=CASCADE,
    related_name='review_tasks',
    verbose_name='Zuständige OE',
  )
  created_by_user_id = IntegerField(
    verbose_name='Erstellt von (User-ID)',
  )
  reviewed_by_user_id = IntegerField(
    verbose_name='Geprüft von (User-ID)',
    null=True,
    blank=True,
  )

  # Task-Status
  task_status = CharField(
    max_length=20,
    choices=TASK_STATUS_CHOICES,
    default='pending',
    verbose_name='Task-Status',
  )

  # Kommentare des Reviewers: { "field_name": "Kommentartext", ... }
  comments = JSONField(
    default=dict,
    blank=True,
    verbose_name='Feld-Kommentare',
  )

  # Snapshot des Zustands zum Zeitpunkt der letzten Freigabe (Diff-Basis)
  approved_snapshot = JSONField(
    default=dict,
    blank=True,
    verbose_name='Freigegebener Snapshot',
  )

  # Snapshot des Zustands zum Zeitpunkt der aktuellen Einreichung (Diff-Vergleich)
  submitted_snapshot = JSONField(
    default=dict,
    blank=True,
    verbose_name='Eingereichter Snapshot',
  )

  class Meta:
    db_table = 'review_task'
    verbose_name = 'Prüfauftrag'
    verbose_name_plural = 'Prüfaufträge'
    ordering = ['-created_at']

  def __str__(self):
    return f'Prüfauftrag #{self.pk} – {self.service_type} (ID {self.service_id})'

  def get_service_instance(self):
    """
    Löst service_type + service_id zu einer konkreten Service-Instanz auf.
    Gibt None zurück wenn das Modell nicht gefunden wird oder das Objekt nicht existiert.
    """
    try:
      model = apps.get_model('angebotsdb', self.service_type)
      return model.objects.get(pk=self.service_id)
    except (LookupError, model.DoesNotExist):
      return None

  @property
  def created_by_user(self):
    """Lädt den User aus der Default-Datenwerft-Datenbank."""
    try:
      return User.objects.using('default').get(id=self.created_by_user_id)
    except User.DoesNotExist:
      return None

  @property
  def reviewed_by_user(self):
    """Lädt den prüfenden User aus der Default-Datenwerft-Datenbank."""
    if not self.reviewed_by_user_id:
      return None
    try:
      return User.objects.using('default').get(id=self.reviewed_by_user_id)
    except User.DoesNotExist:
      return None


class InboxMessage(Base):
  """
  Nachricht in der Inbox eines Nutzers.
  Wird entweder an eine OrgUnit (Reviewer-Aufgabe) oder
  an einen Provider (Überarbeitungs-Aufgabe) gerichtet.
  Genau eines der beiden Felder target_org_unit / target_provider ist gesetzt.
  """

  # Logical Attributes
  icon = 'fa-solid fa-inbox'
  dashboard_mode = None
  list_fields = {
    'message_type': 'Typ',
    'review_task': 'Prüfauftrag',
    'is_read': 'Gelesen',
    'is_resolved': 'Erledigt',
    'updated_at': 'Zuletzt aktualisiert',
  }

  MESSAGE_TYPE_CHOICES = [
    ('review_request', 'Prüfauftrag'),
    ('revision_request', 'Überarbeitungsauftrag'),
  ]

  message_type = CharField(
    max_length=30,
    choices=MESSAGE_TYPE_CHOICES,
    verbose_name='Nachrichtentyp',
  )
  review_task = ForeignKey(
    'ReviewTask',
    on_delete=CASCADE,
    related_name='inbox_messages',
    verbose_name='Prüfauftrag',
  )

  # Empfänger — genau eines der beiden Felder ist gesetzt:
  target_org_unit = ForeignKey(
    'OrgUnit',
    null=True,
    blank=True,
    on_delete=CASCADE,
    related_name='inbox_messages',
    verbose_name='Empfänger-OE',
  )
  target_provider = ForeignKey(
    'Provider',
    null=True,
    blank=True,
    on_delete=CASCADE,
    related_name='inbox_messages',
    verbose_name='Empfänger-Einrichtung',
  )

  is_read = BooleanField(
    default=False,
    verbose_name='Gelesen',
  )
  is_resolved = BooleanField(
    default=False,
    verbose_name='Erledigt',
  )

  class Meta:
    db_table = 'inbox_message'
    verbose_name = 'Inbox-Nachricht'
    verbose_name_plural = 'Inbox-Nachrichten'
    ordering = ['-created_at']

  def get_message_type_display(self) -> str:
    """Gibt den lesbaren Anzeigenamen des Nachrichtentyps zurück (Django choices)."""
    return dict(self.MESSAGE_TYPE_CHOICES).get(self.message_type, self.message_type)

  def __str__(self):
    recipient = self.target_org_unit or self.target_provider or 'Unbekannt'
    return f'{self.get_message_type_display()} → {recipient}'
