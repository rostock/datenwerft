from django_user_agents.utils import get_user_agent

from bemas.utils import is_bemas_admin, is_bemas_user


def add_codelist_context_elements(context, model):
  """
  adds codelist related elements to a context and returns it

  :param context: context
  :param model: codelist model
  :return: context with codelist related elements added
  """
  context['codelist_name'] = model.__name__
  context['codelist_verbose_name'] = model._meta.verbose_name
  context['codelist_verbose_name_plural'] = model._meta.verbose_name_plural
  context['codelist_description'] = model.BasemodelMeta.description
  return context


def add_default_context_elements(context, user):
  """
  adds default elements to a context and returns it

  :param context: context
  :param user: user
  :return: context with default elements added
  """
  context['is_bemas_user'], context['is_bemas_admin'] = False, False
  if user.is_superuser:
    context['is_bemas_user'], context['is_bemas_admin'] = True, True
  elif is_bemas_user(user) or is_bemas_admin(user):
    context['is_bemas_user'] = True
    if is_bemas_admin(user):
      context['is_bemas_admin'] = True
  return context


def add_user_agent_context_elements(context, request):
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
  creates corresponding form field (widget) to given model field and returns it

  :param field: model field
  :return: corresponding form field (widget) to given model field
  """
  form_field = field.formfield()
  # get dictionary with numeric model fields (as keys) and their minimum legal values
  model = field.model
  min_numbers = {}
  if hasattr(model, 'CustomMeta') and hasattr(model.CustomMeta, 'min_numbers'):
    min_numbers = model.CustomMeta.min_numbers
  if hasattr(form_field.widget, 'input_type'):
    if form_field.widget.input_type == 'checkbox':
      form_field.widget.attrs['class'] = 'form-check-input'
    else:
      form_field.widget.attrs['class'] = 'form-control'
    # set minimum legal values for numeric model fields
    if form_field.widget.input_type == 'number' and min_numbers is not None:
      form_field.widget.attrs['min'] = min_numbers.get(field.name, 0)
  return form_field
