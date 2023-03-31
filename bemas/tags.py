from django import template
from django.template.defaultfilters import stringfilter

from bemas.utils import get_icon_from_settings

register = template.Library()


@register.filter
@stringfilter
def get_icon(key):
  """
  returns icon (i.e. value) of given key in icon dictionary

  :param key: key in icon dictionary
  :return: icon (i.e. value) of given key in icon dictionary
  """
  return get_icon_from_settings(key)


@register.filter
@stringfilter
def replace(value, arg):
  """
  replaces string in given value

  :param value: value
  :param arg: source string and target string
  :return: value with replaced strings
  """
  if len(arg.split('|')) != 2:
    return value
  source, target = arg.split('|')
  return value.replace(source, target)
