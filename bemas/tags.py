from django import template
from django.apps import apps
from django.template.defaultfilters import stringfilter

from .utils import get_icon_from_settings

register = template.Library()


@register.filter
def beautify_model_string(model_name, plural=True):
  """
  turns passed model name into model verbose name plural with prefixed icon

  :param model_name: model name
  :param plural: title shall be model verbose name plural?
  :return: passed model name turned into model verbose name plural with prefixed icon
  """
  icon = '<i class="fas fa-{}"></i>'.format(get_icon_from_settings(model_name.lower()))
  model = apps.get_app_config('bemas').get_model(model_name)
  model_title = model._meta.verbose_name_plural if plural else model._meta.verbose_name
  return icon + ' ' + model_title


@register.filter
@stringfilter
def get_icon(key):
  """
  returns icon (i.e. value) of passed key in icon dictionary

  :param key: key in icon dictionary
  :return: icon (i.e. value) of passed key in icon dictionary
  """
  return get_icon_from_settings(key)
