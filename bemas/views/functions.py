from bemas.utils import is_bemas_admin, is_bemas_user


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


def add_user_agent_context_elements(context, user_agent):
  """
  adds user agent related elements to a context and returns it

  :param context: context
  :param user_agent: user agent
  :return: context with user agent related elements added
  """
  if user_agent.is_mobile or user_agent.is_tablet:
    context['is_mobile'] = True
  else:
    context['is_mobile'] = False
  return context


def assign_widget(field, min_numbers=None):
  """
  creates corresponding form field (widget) to given model field and returns it

  :param field: model field
  :param min_numbers: dictionary with numeric model fields (as keys) and their minimum legal values
  :return: corresponding form field (widget) to given model field
  """
  form_field = field.formfield()
  print(field.name)
  if hasattr(form_field.widget, 'input_type'):
    if form_field.widget.input_type == 'checkbox':
      form_field.widget.attrs['class'] = 'form-check-input'
    else:
      form_field.widget.attrs['class'] = 'form-control'
    if form_field.widget.input_type == 'number' and min_numbers is not None:
      form_field.widget.attrs['min'] = min_numbers.get('a', 0)
  return form_field
