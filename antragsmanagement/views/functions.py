from django.forms import Textarea
from django_user_agents.utils import get_user_agent
from leaflet.forms.widgets import LeafletWidget

from toolbox.utils import is_geometry_field
from antragsmanagement.utils import belongs_to_antragsmanagement_authority, \
  is_antragsmanagement_admin, is_antragsmanagement_requester, is_antragsmanagement_user


def add_rbac_context_elements(context, user):
  """
  adds role-based access control (RBAC) related elements to a context and returns it

  :param context: context
  :param user: user
  :return: context with role-based access control (RBAC) related elements added
  """
  roles = {
    'is_antragsmanagement_user': is_antragsmanagement_user(user),
    'is_antragsmanagement_requester': is_antragsmanagement_requester(user),
    'belongs_to_antragsmanagement_authority': belongs_to_antragsmanagement_authority(user),
    'is_antragsmanagement_admin': is_antragsmanagement_admin(user)
  }
  if user.is_superuser:
    roles = {key: True for key in roles}
  context.update(roles)
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
    form_field.widget.attrs['rows'] = 5
  # handle geometry widgets
  elif is_geometry_field(field.__class__):
    form_field = field.formfield(
      widget=LeafletWidget()
    )
  return form_field
