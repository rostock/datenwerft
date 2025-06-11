from django.conf import settings
from django.forms import CheckboxSelectMultiple, Textarea
from django.urls import reverse, reverse_lazy
from django_user_agents.utils import get_user_agent
from leaflet.forms.widgets import LeafletWidget

from toolbox.utils import is_geometry_field

from ..models import Fmf
from ..utils import is_fmm_user


def add_model_context_elements(context, model):
  """
  adds model related elements to a context and returns it

  :param context: context
  :param model: model
  :return: context with model related elements added
  """
  context['model_verbose_name'] = model._meta.verbose_name
  context['model_verbose_name_plural'] = model._meta.verbose_name_plural
  context['model_icon'] = model.BaseMeta.icon
  # add geometry related information to context, if necessary
  if issubclass(model, Fmf):
    geometry_field_name = model.BaseMeta.geometry_field
    geometry_field = model._meta.get_field(geometry_field_name)
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['is_geometry_model'] = True
    context['geometry_field'] = geometry_field_name
    context['geometry_field_label'] = geometry_field.verbose_name
    context['geometry_type'] = model.BaseMeta.geometry_type
  return context


def add_permissions_context_elements(context, user):
  """
  adds permissions related elements to a context and returns it

  :param context: context
  :param user: user
  :return: context with permissions related elements added
  """
  permissions = {
    'is_fmm_user': is_fmm_user(user),
  }
  if user.is_superuser:
    permissions = {key: True for key in permissions}
  context.update(permissions)
  return context


def add_useragent_context_elements(context, request):
  """
  adds user agent related elements to a context and returns it

  :param context: context
  :param request: request
  :return: context with user agent related elements added
  """
  user_agent = get_user_agent(request)
  if user_agent.is_mobile or user_agent.is_tablet:
    context['is_mobile'] = True
  else:
    context['is_mobile'] = False
  return context


def assign_widget(field):
  """
  creates corresponding form field (widget) to passed model field and returns it

  :param field: form field
  :return: corresponding form field (widget) to passed model field
  """
  form_field = field.formfield()
  # handle date widgets
  if field.__class__.__name__ == 'DateField':
    form_field.widget.input_type = 'date'
  # handle inputs
  if hasattr(form_field.widget, 'input_type'):
    if form_field.widget.input_type == 'select':
      # handle multiple selects
      if form_field.widget.__class__.__name__ == 'SelectMultiple':
        form_field.widget = CheckboxSelectMultiple()
      # handle ordinary (single) selects
      else:
        form_field.widget.attrs['class'] = 'form-select'
    else:
      if form_field.widget.input_type == 'checkbox':
        form_field.widget.attrs['class'] = 'form-check-input'
      else:
        form_field.widget.attrs['class'] = 'form-control'
  # handle text areas
  elif issubclass(form_field.widget.__class__, Textarea):
    form_field.widget.attrs['class'] = 'form-control'
    form_field.widget.attrs['rows'] = 10
  # handle geometry widgets
  elif is_geometry_field(field.__class__):
    form_field = field.formfield(widget=LeafletWidget())
  return form_field


def geometry_keeper(form_data, context_data):
  """
  returns passed context data with geometry kept in passed form data

  :param form_data: form data
  :param context_data: context data
  :return: passed context data with geometry kept in passed form data
  """
  # keep geometry (otherwise it would be lost on re-rendering)
  geometry = form_data.get(context_data['geometry_field'], None)
  if geometry and '0,0' not in geometry and '[]' not in geometry:
    context_data['geometry'] = geometry
  return context_data


def get_referer(request):
  """
  returns referer for passed request

  :param request: request
  :return: referer for passed request
  """
  return request.META['HTTP_REFERER'] if 'HTTP_REFERER' in request.META else None


def get_referer_url(referer, fallback, lazy=False):
  """
  returns URL used for "cancel" buttons and/or used in case of successfully submitted forms

  :param referer: referer URL
  :param fallback: fallback URL
  :param lazy: lazy?
  :return: URL used for "cancel" buttons and/or used in case of successfully submitted forms
  """
  if referer:
    return reverse_lazy(referer) if lazy else referer
  return reverse_lazy(fallback) if lazy else reverse(fallback)
