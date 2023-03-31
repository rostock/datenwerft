from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator, RegexValidator
from django.db.models.fields import CharField

from datenmanagement.models.constants_vars import standard_validators, personennamen_validators, \
  d3_regex, d3_message, email_message, hausnummer_regex, hausnummer_message, \
  postleitzahl_regex, postleitzahl_message, rufnummer_regex, rufnummer_message
from bemas.utils import concat_address
from .base import Objectclass


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
