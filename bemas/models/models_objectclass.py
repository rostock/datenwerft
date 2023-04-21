from datetime import date
from django.contrib.gis.db.models.fields import PointField
from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator, RegexValidator
from django.db.models import ForeignKey, ManyToManyField, CASCADE, PROTECT
from django.db.models.fields import BigIntegerField, CharField, DateField, DateTimeField, TextField
from django.utils import timezone

from toolbox.constants_vars import standard_validators, personennamen_validators, \
  d3_regex, d3_message, email_message, hausnummer_regex, hausnummer_message, \
  postleitzahl_regex, postleitzahl_message, rufnummer_regex, rufnummer_message
from bemas.utils import concat_address, shorten_string
from .base import GeometryObjectclass, Objectclass
from .models_codelist import Sector, Status, TypeOfEvent, TypeOfImmission


class Organization(Objectclass):
  """
  model class for object class organization (Organisation)
  """

  search_content = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False
  )
  name = CharField(
    'Name',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  address_street = CharField(
    'Straße',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  address_house_number = CharField(
    'Hausnummer',
    max_length=4,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=hausnummer_regex,
        message=hausnummer_message
      )
    ]
  )
  address_postal_code = CharField(
    'Postleitzahl',
    max_length=5,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=postleitzahl_regex,
        message=postleitzahl_message
      )
    ]
  )
  address_place = CharField(
    'Ort',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  email_addresses = ArrayField(
    CharField(
      verbose_name='E-Mail-Adresse(n)',
      max_length=255,
      blank=True,
      null=True,
      validators=[
        EmailValidator(
          message=email_message
        )
      ]
    ),
    verbose_name='E-Mail-Adresse(n)',
    blank=True,
    null=True
  )
  telephone_numbers = ArrayField(
    CharField(
      verbose_name='Telefonnummer(n)',
      max_length=255,
      blank=True,
      null=True,
      validators=[
        RegexValidator(
          regex=rufnummer_regex,
          message=rufnummer_message
        )
      ]
    ),
    verbose_name='Telefonnummer(n)',
    blank=True,
    null=True
  )
  dms_link = CharField(
    ' d.3',
    max_length=16,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=d3_regex,
        message=d3_message
      )
    ]
  )

  class Meta(Objectclass.Meta):
    db_table = 'organization'
    ordering = ['name']
    verbose_name = 'Organisation'
    verbose_name_plural = 'Organisationen'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Betreiberinnen oder Beschwerdeführerinnen'
    definite_article = 'die'
    indefinite_article = 'eine'
    personal_pronoun = 'sie'
    new = 'neue'

  def __str__(self):
    return self.name

  def address(self):
    return concat_address(self.address_street, self.address_house_number,
                          self.address_postal_code, self.address_place)

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # store search content in designated field
    contacts_str = ''
    contacts = self.contact_set.all()
    if contacts:
      for index, contact in enumerate(contacts):
        contacts_str += ' || ' if index > 0 else ''
        contacts_str += contact.name_and_function()
    self.search_content = str(self) + (' || ' + contacts_str if contacts_str else '')
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )


class Person(Objectclass):
  """
  model class for object class person (Person)
  """

  search_content = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False
  )
  first_name = CharField(
    'Vorname',
    max_length=255,
    blank=True,
    null=True,
    validators=personennamen_validators
  )
  last_name = CharField(
    'Nachname',
    max_length=255,
    validators=personennamen_validators
  )
  address_street = CharField(
    'Straße',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  address_house_number = CharField(
    'Hausnummer',
    max_length=4,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=hausnummer_regex,
        message=hausnummer_message
      )
    ]
  )
  address_postal_code = CharField(
    'Postleitzahl',
    max_length=5,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=postleitzahl_regex,
        message=postleitzahl_message
      )
    ]
  )
  address_place = CharField(
    'Ort',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  email_addresses = ArrayField(
    CharField(
      verbose_name='E-Mail-Adresse(n)',
      max_length=255,
      blank=True,
      null=True,
      validators=[
        EmailValidator(
          message=email_message
        )
      ]
    ),
    verbose_name='E-Mail-Adresse(n)',
    blank=True,
    null=True
  )
  telephone_numbers = ArrayField(
    CharField(
      verbose_name='Telefonnummer(n)',
      max_length=255,
      blank=True,
      null=True,
      validators=[
        RegexValidator(
          regex=rufnummer_regex,
          message=rufnummer_message
        )
      ]
    ),
    verbose_name='Telefonnummer(n)',
    blank=True,
    null=True
  )

  class Meta(Objectclass.Meta):
    db_table = 'person'
    ordering = ['last_name', 'first_name']
    verbose_name = 'Person'
    verbose_name_plural = 'Personen'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Beschwerdeführer:innen oder Ansprechpartner:innen'
    definite_article = 'die'
    indefinite_article = 'eine'
    personal_pronoun = 'sie'
    new = 'neue'

  def __str__(self):
    return (self.first_name + ' ' if self.first_name else '') + self.last_name

  def address(self):
    return concat_address(self.address_street, self.address_house_number,
                          self.address_postal_code, self.address_place)

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # store search content in designated field
    self.search_content = str(self)
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )


class Contact(Objectclass):
  """
  model class for object class contact (Ansprechpartner:in)
  """

  search_content = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False
  )
  organization = ForeignKey(
    Organization,
    verbose_name='Organisation',
    on_delete=CASCADE
  )
  person = ForeignKey(
    Person,
    verbose_name='Person',
    on_delete=CASCADE
  )
  function = CharField(
    'Funktion',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(Objectclass.Meta):
    db_table = 'contact'
    ordering = ['organization__name', 'person__last_name', 'person__first_name']
    verbose_name = 'Ansprechpartner:in'
    verbose_name_plural = 'Ansprechpartner:innen'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Kontaktpersonen in Organisationen'
    definite_article = 'die/der'
    indefinite_article = 'ein:e'
    personal_pronoun = 'sie/ihn'
    new = 'neue:n'

  def __str__(self):
    return str(self.person) + ' in der Organisation ' + str(self.organization) + \
           (' (Funktion: ' + self.function + ')' if self.function else '')

  def name_and_function(self):
    return str(self.person) + (' (Funktion: ' + self.function + ')' if self.function else '')

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # store search content in designated field
    self.search_content = self.name_and_function()
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )


class Originator(GeometryObjectclass):
  """
  model class for geometry object class originator (Verursacher)
  """

  search_content = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False
  )
  sector = ForeignKey(
    Sector,
    verbose_name='Branche',
    on_delete=PROTECT
  )
  operator = ForeignKey(
    Organization,
    verbose_name='Betreiberin',
    on_delete=PROTECT
  )
  description = TextField(
    'Beschreibung',
    validators=standard_validators
  )
  emission_point = PointField(
    'Emissionsort'
  )
  address = CharField(
    'Adresse',
    max_length=255,
    blank=True,
    null=True
  )
  dms_link = CharField(
    ' d.3',
    max_length=16,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=d3_regex,
        message=d3_message
      )
    ]
  )

  class Meta(GeometryObjectclass.Meta):
    db_table = 'originator'
    ordering = ['sector__title', 'operator__name', 'description']
    verbose_name = 'Verursacher'
    verbose_name_plural = 'Verursacher'

  class BasemodelMeta(GeometryObjectclass.BasemodelMeta):
    geometry_field = 'emission_point'
    description = 'Verursacher von Emissionen'
    definite_article = 'der'
    indefinite_article = 'ein'
    personal_pronoun = 'er'
    new = 'neuen'

  def __str__(self):
    return str(self.sector) + ' mit der Betreiberin ' + str(self.operator) + \
           ' (' + shorten_string(self.description) + ')'

  def sector_and_operator(self):
    return str(self.sector) + ' (Betreiberin: ' + str(self.operator) + ')'

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # store search content in designated field
    self.search_content = self.sector_and_operator()
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )


class Complaint(GeometryObjectclass):
  """
  model class for geometry object class complaint (Beschwerde)
  """

  search_content = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False
  )
  date_of_receipt = DateField(
    'Eingangsdatum',
    default=date.today
  )
  status = ForeignKey(
    Status,
    verbose_name='Bearbeitungsstatus',
    on_delete=PROTECT
  )
  status_updated_at = DateTimeField(
    'letzte Änderung Bearbeitungsstatus',
    auto_now_add=True,
    editable=False
  )
  type_of_immission = ForeignKey(
    TypeOfImmission,
    verbose_name='Immissionsart',
    on_delete=PROTECT
  )
  immission_point = PointField(
    'Immissionsort'
  )
  address = CharField(
    'Adresse',
    max_length=255,
    blank=True,
    null=True
  )
  originator = ForeignKey(
    Originator,
    verbose_name='Verursacher',
    on_delete=PROTECT
  )
  complainers_organizations = ManyToManyField(
    Organization,
    db_table='complainers_organizations',
    verbose_name='Organisation(en) als Beschwerdeführerin(nen)',
    blank=True
  )
  complainers_persons = ManyToManyField(
    Person,
    db_table='complainers_persons',
    verbose_name='Person(en) als Beschwerdeführer:in(nen)',
    blank=True
  )
  description = TextField(
    'Beschreibung',
    validators=standard_validators
  )
  dms_link = CharField(
    ' d.3',
    max_length=16,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=d3_regex,
        message=d3_message
      )
    ]
  )
  storage_location = CharField(
    'Ablageort analog',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(GeometryObjectclass.Meta):
    db_table = 'complaint'
    ordering = ['id']
    verbose_name = 'Beschwerde'
    verbose_name_plural = 'Beschwerden'

  class BasemodelMeta(GeometryObjectclass.BasemodelMeta):
    geometry_field = 'immission_point'
    description = 'Folgen von Immissionen'
    definite_article = 'die'
    indefinite_article = 'eine'
    personal_pronoun = 'sie'
    new = 'neue'

  def __str__(self):
    return '#' + str(self.id)

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # store search content in designated field
    complainers_str = ''
    complainers_organizations = self.complainers_organizations.all()
    if complainers_organizations:
      for index, complainer_organization in enumerate(complainers_organizations):
        complainers_str += ' || ' if index > 0 else ''
        complainers_str += str(complainer_organization)
    complainers_persons = self.complainers_persons.all()
    if complainers_persons:
      for index, complainer_person in enumerate(complainers_persons):
        complainers_str += ' || ' if index > 0 or complainers_organizations else ''
        complainers_str += str(complainer_person)
    self.search_content = str(self) + ' || ' + (
      complainers_str if complainers_str else 'anonyme Beschwerde')
    # on creation:
    # store default status in designated field
    if not self.pk and Status.get_default_status():
      self.status = Status.get_default_status()
    # on status update:
    # store timestamp of status update in designated field
    elif self.pk and self.status != Complaint.objects.get(pk=self.pk).status:
      self.status_updated_at = timezone.now()
    if update_fields is not None and 'status' in update_fields:
      update_fields = {'status_updated_at'}.union(update_fields)
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )


class Event(Objectclass):
  """
  model class for object class event (Journalereignis)
  """

  search_content = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False
  )
  complaint = ForeignKey(
    Complaint,
    verbose_name='Beschwerde',
    on_delete=CASCADE
  )
  type_of_event = ForeignKey(
    TypeOfEvent,
    verbose_name='Ereignisart',
    on_delete=PROTECT
  )
  user = CharField(
    'Benutzer:in',
    max_length=255,
    editable=False
  )
  description = TextField(
    'Beschreibung',
    blank=True,
    null=True,
    validators=standard_validators
  )
  dms_link = CharField(
    ' d.3',
    max_length=16,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=d3_regex,
        message=d3_message
      )
    ]
  )

  class Meta(Objectclass.Meta):
    db_table = 'event'
    ordering = ['complaint__id', 'created_at']
    verbose_name = 'Journalereignis'
    verbose_name_plural = 'Journalereignisse'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Ereignisse im Journal zu einer Beschwerde'
    definite_article = 'das'
    indefinite_article = 'ein'
    personal_pronoun = 'es'
    new = 'neues'

  def __str__(self):
    return str(self.type_of_event) + ' zur Beschwerde ' + str(self.complaint) + \
           (' (' + shorten_string(self.description) + ')' if self.description else '')

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # store search content in designated field
    self.search_content = str(self)
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )


class LogEntry(Objectclass):
  """
  model class for object class log entry (Eintrag im Bearbeitungsverlauf)
  """

  model = CharField(
    'Objektklasse',
    max_length=255,
    editable=False
  )
  object_pk = BigIntegerField(
    'ID des Objekts',
    editable=False
  )
  object_str = CharField(
    'Objekt',
    max_length=255,
    editable=False
  )
  action = CharField(
    'Aktion',
    max_length=255,
    editable=False
  )
  user = CharField(
    'Benutzer:in',
    max_length=255,
    editable=False
  )

  class Meta(Objectclass.Meta):
    db_table = 'logentry'
    ordering = ['id']
    verbose_name = 'Eintrag im Bearbeitungsverlauf'
    verbose_name_plural = 'Einträge im Bearbeitungsverlauf'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Logbucheinträge, die durch ausgewählte Ereignisse ausgelöst werden'
    definite_article = 'der'
    indefinite_article = 'ein'
    personal_pronoun = 'er'
    new = 'neuen'

  def __str__(self):
    return '#' + str(self.id)
