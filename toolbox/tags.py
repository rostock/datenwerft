from django import template
from django.template.defaultfilters import stringfilter

from toolbox.constants_vars import standard_validators
from toolbox.utils import is_geometry_field

register = template.Library()


@register.filter
def get_dict_value_by_key(arg_dict, key):
  """
  returns value of passed key in passed dictionary

  :param arg_dict: dictionary
  :param key: key in dictionary
  :return: value of passed key in passed dictionary
  """
  return arg_dict.get(key)


@register.filter
def is_field_geometry_field(field):
  """
  checks if passed field is a geometry related field

  :param field: field
  :return: passed field is a geometry related field?
  """
  return is_geometry_field(field.field.__class__)


@register.filter
def is_list(value):
  """
  checks if passed value is a list

  :param value: value
  :return: passed value is a list?
  """
  return isinstance(value, list)


@register.filter
def is_linebreak_error(errors):
  """
  checks if passed form field errors represent a line break error

  :param errors: form field errors
  :return: passed form field errors represent a line break error?
  """
  if str(errors).count('<li>') == len(standard_validators):
    return True
  return False


@register.filter
@stringfilter
def replace(value, arg):
  """
  replaces string in passed value

  :param value: value
  :param arg: source string and target string
  :return: value with replaced strings
  """
  if len(arg.split('|')) != 2:
    return value
  source, target = arg.split('|')
  return value.replace(source, target)
