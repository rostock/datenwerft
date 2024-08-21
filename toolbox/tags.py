from cloudinit.reporting.events import status
from django import template
from django.conf import settings
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

@register.filter(is_safe=True)
@stringfilter
def get_logo(value):
  instance_status = settings.INSTANCE_STATUS
  logos = {
    'DEVEL': 'img/logo-devel.svg',
    'TESTING': 'img/logo-testing.svg',
    'PRODUCTION': 'img/logo.svg'
  }
  if instance_status in logos:
    return logos[instance_status]
  else:
    return value
