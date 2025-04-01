from django.contrib.gis.db.models.fields import (
  LineStringField,
  MultiLineStringField,
  MultiPolygonField,
  PointField,
  PolygonField,
)
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db.models.fields import PositiveIntegerField, PositiveSmallIntegerField
from django.forms import TypedMultipleChoiceField

#
# extensions of existing model fields
#


class ChoiceArrayField(ArrayField):
  """
  ArrayField with multiple choices,
  i.e. a model field that allows to store an array of choices
  (source: https://gist.github.com/danni/f55c4ce19598b2b345ef)
  """

  def formfield(self, **kwargs):
    defaults = {
      'form_class': TypedMultipleChoiceField,
      'choices': self.base_field.choices,
      'coerce': self.base_field.to_python,
    }
    defaults.update(kwargs)
    return super(ArrayField, self).formfield(**defaults)

  def validate(self, value, model_instance):
    if not self.editable:
      return
    if value is None or value in self.empty_values:
      return None
    if self.choices is not None and value not in self.empty_values:
      if set(value).issubset({option_key for option_key, _ in self.choices}):
        return
      raise ValidationError(
        self.error_messages['invalid_choice'], code='invalid_choice', params={'value': value}
      )

    if value is None and not self.null:
      raise ValidationError(self.error_messages['null'], code='null')

    if not self.blank and value in self.empty_values:
      raise ValidationError(self.error_messages['blank'], code='blank')


class PositiveIntegerMinField(PositiveIntegerField):
  """
  PositiveIntegerField with minimum value
  """

  def __init__(self, verbose_name=None, name=None, min_value=None, **kwargs):
    self.min_value = min_value
    PositiveIntegerField.__init__(self, verbose_name, name, **kwargs)

  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value}
    defaults.update(kwargs)
    return super().formfield(**defaults)


class PositiveIntegerRangeField(PositiveIntegerField):
  """
  PositiveIntegerField with minimum and maximum value
  """

  def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
    self.min_value, self.max_value = min_value, max_value
    PositiveIntegerField.__init__(self, verbose_name, name, **kwargs)

  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value, 'max_value': self.max_value}
    defaults.update(kwargs)
    return super().formfield(**defaults)


class PositiveSmallIntegerMinField(PositiveSmallIntegerField):
  """
  PositiveSmallIntegerField with minimum value
  """

  def __init__(self, verbose_name=None, name=None, min_value=None, **kwargs):
    self.min_value = min_value
    PositiveSmallIntegerField.__init__(self, verbose_name, name, **kwargs)

  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value}
    defaults.update(kwargs)
    return super().formfield(**defaults)


class PositiveSmallIntegerRangeField(PositiveSmallIntegerField):
  """
  PositiveSmallIntegerField with minimum and maximum value
  """

  def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
    self.min_value, self.max_value = min_value, max_value
    PositiveSmallIntegerField.__init__(self, verbose_name, name, **kwargs)

  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value, 'max_value': self.max_value}
    defaults.update(kwargs)
    return super().formfield(**defaults)


#
# definition of geometry model fields
#

point_field = PointField('Geometrie', srid=25833, default='POINT(0 0)')
line_field = LineStringField('Geometrie', srid=25833)
multiline_field = MultiLineStringField('Geometrie', srid=25833)
polygon_field = PolygonField('Geometrie', srid=25833)
multipolygon_field = MultiPolygonField('Geometrie', srid=25833)
nullable_multipolygon_field = MultiPolygonField('Geometrie', srid=25833, blank=True, null=True)
