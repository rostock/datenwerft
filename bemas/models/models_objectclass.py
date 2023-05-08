from datetime import date
from django.apps import apps
from django.contrib.gis.db.models.fields import PointField
from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator, RegexValidator
from django.db.models import ForeignKey, ManyToManyField, CASCADE, PROTECT
from django.db.models.fields import BigIntegerField, CharField, DateField, DateTimeField, TextField
from django.db.models.signals import m2m_changed
from django.utils import timezone

from datenmanagement.models.fields import NullTextField
from toolbox.constants_vars import standard_validators, personennamen_validators, \
  d3_regex, d3_message, email_message, hausnummer_regex, hausnummer_message, \
  postleitzahl_regex, postleitzahl_message, rufnummer_regex, rufnummer_message
from bemas.utils import LOG_ACTIONS, concat_address, shorten_string
from .base import GeometryObjectclass, Objectclass
from .functions import store_complaint_search_content
from .models_codelist import Sector, Status, TypeOfEvent, TypeOfImmission


class Organization(Objectclass):
  """
  model class for object class organization (Organisation)
  """

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
    self.search_content = str(self)
    # add contacts to search content if organization already exists
    # (since before, there can be no contacts for this organization, of course)
    if self.pk:
      contacts_str = ''
      contacts = self.contact_set.all()
      if contacts:
        for index, contact in enumerate(contacts):
          contacts_str += ' | ' if index > 0 else ''
          contacts_str += contact.name_and_function()
        self.search_content += ' || ' + contacts_str
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )

  def delete(self, **kwargs):
    # update search content in designated field of object class complaint:
    # first, get all corresponding complaints
    # second, remove many-to-many-relationship between each complaint and organization-to-remove
    # (which triggers signal to update search content)
    complaints = Complaint.objects.filter(complainers_organizations__pk=self.pk)
    if complaints:
      for complaint in complaints:
        complaint.complainers_organizations.remove(self)
    super().delete()


class Person(Objectclass):
  """
  model class for object class person (Person)
  """

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

  def delete(self, **kwargs):
    # update search content in designated field of object class complaint:
    # first, get all corresponding complaints
    # second, remove many-to-many-relationship between each complaint and person-to-remove
    # (which triggers signal to update search content)
    complaints = Complaint.objects.filter(complainers_persons__pk=self.pk)
    if complaints:
      for complaint in complaints:
        complaint.complainers_persons.remove(self)
    super().delete()


class Contact(Objectclass):
  """
  model class for object class contact (Ansprechpartner:in)
  """

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
           (' mit der Funktion ' + self.function if self.function else '')

  def name_and_function(self):
    return str(self.person) + (' (Funktion: ' + self.function + ')' if self.function else '')

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # (1/2) store search content in designated field of object class organization:
    # first get organization...
    organization = Organization.objects.get(pk=self.organization.pk)
    # store search content in designated field
    self.search_content = self.name_and_function()
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )
    # (2/2) store search content in designated field of object class organization:
    # ...and then save organization since now, its contact is referenced
    organization.save()

  def delete(self, **kwargs):
    # (1/2) store search content in designated field of object class organization:
    # first get organization...
    organization = Organization.objects.get(pk=self.organization.pk)
    super().delete()
    # (2/2) store search content in designated field of object class organization:
    # ...and then save organization since now, its contact is unreferenced
    organization.save()


class Originator(GeometryObjectclass):
  """
  model class for geometry object class originator (Verursacher)
  """

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
    personal_pronoun = 'ihn'
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
    ordering = ['-id']
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
    return '#' + str(self.id) + ' vom ' + self.date_of_receipt.strftime('%d.%m.%Y') + \
           ' (' + str(self.status) + ')'

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # on creation:
    if not self.pk and Status.get_default_status():
      # store default status in designated field
      if not hasattr(self, 'status'):
        self.status = Status.get_default_status()
      # store search content in designated field
      self.search_content = 'anonyme Beschwerde'
    # on status update:
    # store datetime of status update in designated field
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


# extend search content in designated field
# (via signal since the many-to-many-relationship is needed here)
m2m_changed.connect(
  store_complaint_search_content, sender=Complaint.complainers_organizations.through)
m2m_changed.connect(
  store_complaint_search_content, sender=Complaint.complainers_persons.through)


class Event(Objectclass):
  """
  model class for object class event (Journalereignis)
  """

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
    max_length=255
  )
  description = NullTextField(
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
    ordering = ['-complaint__id', '-created_at']
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

  def type_of_event_and_complaint(self):
    return str(self.type_of_event) + ' (Beschwerde: ' + str(self.complaint) + ')'

  def type_of_event_and_created_at(self):
    return str(self.type_of_event) + ' vom ' + self.created_at.strftime('%d.%m.%Y') + \
           (' (' + shorten_string(self.description) + ')' if self.description else '')

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # store search content in designated field
    self.search_content = self.type_of_event_and_complaint()
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
  action = CharField(
    'Aktion',
    max_length=255,
    editable=False
  )
  content = CharField(
    'Inhalt',
    max_length=255,
    blank=True,
    null=True,
    editable=False
  )
  user = CharField(
    'Benutzer:in',
    max_length=255,
    editable=False
  )

  class Meta(Objectclass.Meta):
    db_table = 'logentry'
    ordering = ['-created_at']
    verbose_name = 'Eintrag im Bearbeitungsverlauf'
    verbose_name_plural = 'Einträge im Bearbeitungsverlauf'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Logbucheinträge, die durch ausgewählte Ereignisse ausgelöst werden'
    definite_article = 'der'
    indefinite_article = 'ein'
    personal_pronoun = 'ihn'
    new = 'neuen'

  def __str__(self):
    return '#' + str(self.id)

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # force object string to be NULL
    if self.content == '/':
      self.content = None
    # store search content in designated field
    model_title = apps.get_app_config('bemas').get_model(self.model)._meta.verbose_name_plural
    self.search_content = model_title + ' || ' + LOG_ACTIONS[self.action]
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )
