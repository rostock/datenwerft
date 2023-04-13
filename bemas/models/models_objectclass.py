from datetime import date
from django.contrib.gis.db.models.fields import PointField
from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator, RegexValidator
from django.db.models import ForeignKey, ManyToManyField, CASCADE, PROTECT
from django.db.models.fields import CharField, DateField, DateTimeField, TextField, UUIDField
from django.utils import timezone

from toolbox.constants_vars import standard_validators, personennamen_validators, \
  d3_regex, d3_message, email_message, hausnummer_regex, hausnummer_message, \
  postleitzahl_regex, postleitzahl_message, rufnummer_regex, rufnummer_message
from bemas.utils import concat_address, shorten_string
from .base import Objectclass
from .models_codelist import Sector, Status, TypeOfImmission


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
    description = 'Beschwerdeführer:innen'
    definite_article = 'die'
    indefinite_article = 'eine'
    personal_pronoun = 'sie'
    new = 'neue'

  def __str__(self):
    return (self.first_name + ' ' if self.first_name else '') + self.last_name

  def address(self):
    return concat_address(self.address_street, self.address_house_number,
                          self.address_postal_code, self.address_place)


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
           (' (Funktion: ' + self.function + ')' if self.function else '')

  def name_and_function(self):
    return str(self.person) + (' (Funktion: ' + self.function + ')' if self.function else '')


class Originator(Objectclass):
  """
  model class for object class originator (Verursacher)
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
    'Emissionsort',
    srid=25833
  )
  address = UUIDField(
    'Adresse',
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
    db_table = 'originator'
    ordering = ['sector__title', 'operator__name', 'description']
    verbose_name = 'Verursacher'
    verbose_name_plural = 'Verursacher'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Verursacher von Emissionen'
    definite_article = 'der'
    indefinite_article = 'ein'
    personal_pronoun = 'er'
    new = 'neuer'

  def __str__(self):
    return str(self.sector) + ' mit der Betreiberin ' + str(self.operator) + \
           ' (Beschreibung: ' + shorten_string(self.description) + ')'


class Complaint(Objectclass):
  """
  model class for object class complaint (Beschwerde)
  """

  date_of_receipt = DateField(
    'Eingangsdatum',
    default=date.today
  )
  status = ForeignKey(
    Status,
    verbose_name='Bearbeitungsstatus',
    on_delete=PROTECT,
    default=Status.get_default_status_pk()
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
    'Immissionsort',
    srid=25833
  )
  address = UUIDField(
    'Adresse',
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
    verbose_name='Beschwerdeführerin'
  )
  complainers_persons = ManyToManyField(
    Person,
    db_table='complainers_persons',
    verbose_name='Beschwerdeführer:in'
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

  class Meta(Objectclass.Meta):
    db_table = 'complaint'
    ordering = ['id']
    verbose_name = 'Beschwerde'
    verbose_name_plural = 'Beschwerden'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Folgen von Immissionen'
    definite_article = 'die'
    indefinite_article = 'eine'
    personal_pronoun = 'sie'
    new = 'neue'

  def __str__(self):
    return str(self.id)

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
    # on status update:
    # store timestamp of status update in designated field
    if self.pk and self.status != Complaint.objects.get(pk=self.pk).status:
      self.status_updated_at = timezone.now()
    if update_fields is not None and 'status' in update_fields:
      update_fields = {'status_updated_at'}.union(update_fields)
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )
