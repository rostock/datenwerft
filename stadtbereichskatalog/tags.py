from django import template
from django.template.defaultfilters import stringfilter

from .utils import get_icon_from_settings

register = template.Library()


@register.filter
@stringfilter
def get_icon(key):
  """
  returns icon (i.e. value) of passed key in icon dictionary

  :param key: key in icon dictionary
  :return: icon (i.e. value) of passed key in icon dictionary
  """
  return get_icon_from_settings(key)
