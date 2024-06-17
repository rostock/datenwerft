from django.conf import settings
from django.forms import Textarea
from django_user_agents.utils import get_user_agent
from leaflet.forms.widgets import LeafletWidget

from toolbox.utils import is_geometry_field
from antragsmanagement.models import GeometryObject
from antragsmanagement.utils import belongs_to_antragsmanagement_authority, \
  has_necessary_permissions, is_antragsmanagement_admin, is_antragsmanagement_requester, \
  is_antragsmanagement_user


def add_model_context_elements(context, model):
  """
  adds model related elements to a context and returns it

  :param context: context
  :param model: model
  :return: context with model related elements added
  """
  context['model_verbose_name'] = model._meta.verbose_name
  # if object contains geometry:
  # add geometry related information to context
  if issubclass(model, GeometryObject):
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['REVERSE_SEARCH_RADIUS'] = settings.REVERSE_SEARCH_RADIUS
    context['is_geometry_model'] = True
    context['geometry_field'] = model.BaseMeta.geometry_field
  return context


def add_permissions_context_elements(context, user, necessary_group=None):
  """
  adds permissions related elements to a context and returns it

  :param context: context
  :param user: user
  :param necessary_group: group that passed user must belong to for necessary permissions
  :return: context with permissions related elements added
  """
  permissions = {
    'is_antragsmanagement_user': is_antragsmanagement_user(user),
    'is_antragsmanagement_requester': is_antragsmanagement_requester(user),
    'belongs_to_antragsmanagement_authority': belongs_to_antragsmanagement_authority(user),
    'is_antragsmanagement_admin': is_antragsmanagement_admin(user),
    'has_necessary_permissions': has_necessary_permissions(user, necessary_group) if
    necessary_group else None
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

  :param field: model field
  :return: corresponding form field (widget) to passed model field
  """
  form_field = field.formfield()
  # handle date widgets
  if field.__class__.__name__ == 'DateField':
    form_field.widget.input_type = 'date'
  # handle inputs
  if hasattr(form_field.widget, 'input_type'):
    if form_field.widget.input_type == 'checkbox':
      form_field.widget.attrs['class'] = 'form-check-input'
    # handle ordinary (single) selects
    elif form_field.widget.input_type == 'select':
      form_field.widget.attrs['class'] = 'form-select'
      # handle multiple selects
      if form_field.widget.__class__.__name__ == 'SelectMultiple':
        form_field.widget.attrs['size'] = 5
    else:
      form_field.widget.attrs['class'] = 'form-control'
  # handle text areas
  elif issubclass(form_field.widget.__class__, Textarea):
    form_field.widget.attrs['class'] = 'form-control'
    form_field.widget.attrs['rows'] = 10
  # handle geometry widgets
  elif is_geometry_field(field.__class__):
    form_field = field.formfield(
      widget=LeafletWidget()
    )
  return form_field
