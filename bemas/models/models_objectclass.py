from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator, RegexValidator
from django.db.models import CheckConstraint, ForeignKey, Q, SET_NULL, UniqueConstraint
from django.db.models.fields import CharField, SmallIntegerField

from datenmanagement.models.constants_vars import standard_validators, personennamen_validators, \
  email_message, hausnummer_zusatz_regex, hausnummer_zusatz_message, postleitzahl_regex, \
  postleitzahl_message, rufnummer_regex, rufnummer_message
from .base import Objectclass


class Address(Objectclass):
  """
  model class for object class address (Anschrift)
  """

  street = CharField(
    'Straße',
    max_length=255,
    validators=standard_validators
  )
  house_number = SmallIntegerField(
    'Hausnummer'
  )
  house_number_suffix = CharField(
    'Hausnummernzusatz',
    max_length=1,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=hausnummer_zusatz_regex,
        message=hausnummer_zusatz_message
      )
    ]
  )
  postal_code = CharField(
    'Postleitzahl',
    max_length=5,
    validators=[
      RegexValidator(
        regex=postleitzahl_regex,
        message=postleitzahl_message
      )
    ]
  )
  place = CharField(
    'Ort',
    max_length=255,
    validators=standard_validators
  )

  class Meta(Objectclass.Meta):
    constraints = [
      CheckConstraint(
        check=Q(house_number__gte=1),
        name='address_house_number_gte_1'
      ),
      CheckConstraint(
        check=Q(house_number__lte=999),
        name='address_house_number_lte_999'
      ),
      UniqueConstraint(
        fields=['place', 'postal_code', 'street', 'house_number', 'house_number_suffix'],
        name='address_with_house_number_suffix_unique'
      ),
      UniqueConstraint(
        fields=['place', 'postal_code', 'street', 'house_number'],
        condition=Q(house_number_suffix__isnull=True),
        name='address_without_house_number_suffix_unique'
      )
    ]
    db_table = 'address'
    ordering = ['place', 'postal_code', 'street', 'house_number', 'house_number_suffix']
    verbose_name = 'Anschrift'
    verbose_name_plural = 'Anschriften'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Anschrift'

  class CustomMeta:
    min_numbers = {
      'house_number': 1
    }
    max_numbers = {
      'house_number': 999
    }

  def __str__(self):
    return self.street + ' ' + str(self.house_number) + \
      (self.house_number_suffix if self.house_number_suffix else '') + \
      ', ' + self.postal_code + ' ' + self.place


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
  address = ForeignKey(
    Address,
    verbose_name='Anschrift',
    on_delete=SET_NULL,
    blank=True,
    null=True
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
    db_table = 'organization'
    ordering = ['name']
    verbose_name = 'Organisation'
    verbose_name_plural = 'Organisationen'

  class BasemodelMeta(Objectclass.BasemodelMeta):
    description = 'Organisation (Betreiber:in, wenn mit einem Verursacher verknüpft; ' \
                  'Beschwerdeführer:in, wenn mit einer Beschwerde verknüpft)'

  def __str__(self):
    return self.name


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
  address = ForeignKey(
    Address,
    verbose_name='Anschrift',
    on_delete=SET_NULL,
    blank=True,
    null=True
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
    description = 'Person (Beschwerdeführer:in, wenn mit einer Beschwerde verknüpft)'

  def __str__(self):
    return (self.first_name + ' ' if self.first_name else '') + self.last_name
