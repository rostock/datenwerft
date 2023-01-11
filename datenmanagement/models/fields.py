from django.contrib.postgres.fields import ArrayField
from django.contrib.gis.db.models.fields import LineStringField, MultiLineStringField, \
  MultiPolygonField, PointField, PolygonField
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, RegexValidator, URLValidator
from django.db.models.fields import BooleanField, CharField, PositiveIntegerField, \
  PositiveSmallIntegerField, TextField
from django.forms import Textarea, TypedMultipleChoiceField

from .constants_vars import standard_validators, personennamen_validators, email_message, \
  rufnummer_regex, rufnummer_message, url_message


class ChoiceArrayField(ArrayField):
  """
  Multiple-Choice-Feld
  (Quelle: https://gist.github.com/danni/f55c4ce19598b2b345ef)
  """

  def formfield(self, **kwargs):
    defaults = {
      'form_class': TypedMultipleChoiceField,
      'choices': self.base_field.choices,
    }
    defaults.update(kwargs)
    return super(ArrayField, self).formfield(**defaults)

  def to_python(self, value):
    res = super().to_python(value)
    if isinstance(res, list):
      value = [self.base_field.to_python(val) for val in res]
    else:
      value = None
    return value

  def validate(self, value, model_instance):
    if not self.editable:
      return
    if value is None or value in self.empty_values:
      return None
    if self.choices is not None and value not in self.empty_values:
      if set(value).issubset(
          {option_key for option_key, _ in self.choices}):
        return
      raise ValidationError(
        self.error_messages['invalid_choice'],
        code='invalid_choice',
        params={
          'value': value
        }
      )

    if value is None and not self.null:
      raise ValidationError(
        self.error_messages['null'],
        code='null'
      )

    if not self.blank and value in self.empty_values:
      raise ValidationError(
        self.error_messages['blank'],
        code='blank'
      )


class NullTextField(TextField):
  """
  Textfeld, das NULL-Werte statt Leerstrings schreibt
  """

  def get_internal_type(self):
    return 'TextField'

  def to_python(self, value):
    if value is None or value in self.empty_values:
      return None
    elif isinstance(value, str):
      return value
    return str(value)

  def get_prep_value(self, value):
    value = super(NullTextField, self).get_prep_value(value)
    return self.to_python(value)

  def formfield(self, **kwargs):
    return super(NullTextField, self).formfield(**{
      'max_length': self.max_length,
      **({} if self.choices is not None else {'widget': Textarea}),
      **kwargs,
    })


class PositiveIntegerRangeField(PositiveIntegerField):
  """
  positives Integer-Feld mit Minimal- und Maximalwert
  """

  def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
    self.min_value, self.max_value = min_value, max_value
    PositiveIntegerField.__init__(self, verbose_name, name, **kwargs)

  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value, 'max_value': self.max_value}
    defaults.update(kwargs)
    return super(PositiveIntegerRangeField, self).formfield(**defaults)


class PositiveIntegerMinField(PositiveIntegerField):
  """
  positives Integer-Feld mit Minimalwert
  """

  def __init__(self, verbose_name=None, name=None, min_value=None, **kwargs):
    self.min_value = min_value
    PositiveIntegerField.__init__(self, verbose_name, name, **kwargs)

  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value}
    defaults.update(kwargs)
    return super(PositiveIntegerMinField, self).formfield(**defaults)


class PositiveSmallIntegerMinField(PositiveSmallIntegerField):
  """
  positives Small-Integer-Feld mit Minimalwert
  """

  def __init__(self, verbose_name=None, name=None, min_value=None, **kwargs):
    self.min_value = min_value
    PositiveSmallIntegerField.__init__(self, verbose_name, name, **kwargs)

  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value}
    defaults.update(kwargs)
    return super(PositiveSmallIntegerMinField, self).formfield(**defaults)


class PositiveSmallIntegerRangeField(PositiveSmallIntegerField):
  """
  positives Small-Integer-Feld mit Minimal- und Maximalwert
  """

  def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
    self.min_value, self.max_value = min_value, max_value
    PositiveSmallIntegerField.__init__(self, verbose_name, name, **kwargs)

  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value, 'max_value': self.max_value}
    defaults.update(kwargs)
    return super(PositiveSmallIntegerRangeField, self).formfield(**defaults)


barrierefrei_field = BooleanField(
  ' barrierefrei?',
  blank=True,
  null=True
)
bearbeiter_field = CharField(
  'Bearbeiter:in',
  max_length=255,
  validators=standard_validators
)
bemerkungen_field = CharField(
  'Bemerkungen',
  max_length=255,
  blank=True,
  null=True,
  validators=standard_validators
)
bezeichnung_field = CharField(
  'Bezeichnung',
  max_length=255,
  validators=standard_validators
)
email_field = CharField(
  'E-Mail-Adresse',
  max_length=255,
  blank=True,
  null=True,
  validators=[
    EmailValidator(
      message=email_message
    )
  ]
)
nachname_field = CharField(
  'Nachname',
  max_length=255,
  validators=personennamen_validators
)
oeffnungszeiten_field = CharField(
  'Öffnungszeiten',
  max_length=255,
  blank=True,
  null=True
)
plaetze_field = PositiveSmallIntegerMinField(
  'Plätze',
  min_value=1,
  blank=True,
  null=True
)
telefon_festnetz_field = CharField(
  'Telefon (Festnetz)',
  max_length=255,
  blank=True,
  null=True,
  validators=[
    RegexValidator(
      regex=rufnummer_regex,
      message=rufnummer_message
    )
  ]
)
telefon_mobil_field = CharField(
  'Telefon (mobil)',
  max_length=255,
  blank=True,
  null=True,
  validators=[
    RegexValidator(
      regex=rufnummer_regex,
      message=rufnummer_message
    )
  ]
)
vorname_field = CharField(
  'Vorname',
  max_length=255,
  validators=personennamen_validators
)
website_field = CharField(
  'Website',
  max_length=255,
  blank=True,
  null=True,
  validators=[
    URLValidator(
      message=url_message
    )
  ]
)

punkt_field = PointField(
  'Geometrie',
  srid=25833,
  default='POINT(0 0)'
)
linie_field = LineStringField(
  'Geometrie',
  srid=25833
)
multilinie_field = MultiLineStringField(
  'Geometrie',
  srid=25833
)
flaeche_field = PolygonField(
  'Geometrie',
  srid=25833
)
multiflaeche_field = MultiPolygonField(
  'Geometrie',
  srid=25833
)
