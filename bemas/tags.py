from django import template
from django.apps import apps
from django.template.defaultfilters import stringfilter

from bemas.utils import get_icon_from_settings, is_geometry_field

register = template.Library()


@register.filter
def beautify_model_string(model_name):
  """
  checks if passed field is a geometry related field

  :param model_name: model name
  :return: passed field is a geometry related field?
  """
  icon = '<i class="fas fa-{}"></i>'.format(get_icon_from_settings(model_name.lower()))
  model = apps.get_app_config('bemas').get_model(model_name)
  model_title = model._meta.verbose_name_plural
  return icon + ' ' + model_title


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
@stringfilter
def get_icon(key):
  """
  returns icon (i.e. value) of passed key in icon dictionary

  :param key: key in icon dictionary
  :return: icon (i.e. value) of passed key in icon dictionary
  """
  return get_icon_from_settings(key)


@register.filter
def is_field_geometry_field(field):
  """
  checks if passed field is a geometry related field

  :param field: field
  :return: passed field is a geometry related field?
  """
  return is_geometry_field(field.field.__class__)


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
