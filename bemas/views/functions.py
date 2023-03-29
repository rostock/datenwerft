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


def add_table_context_elements(context, model):
  """
  adds table related elements to a context and returns it

  :param context: context
  :param model: model
  :return: context with table related elements added
  """
  context['objects_count'] = model.objects.count()
  column_titles = []
  for field in model._meta.fields:
    column_titles.append(field.verbose_name)
  context['column_titles'] = column_titles
  # determine initial order
  initial_order = []
  if model._meta.ordering:
    for field_name in model._meta.ordering:
      # determine order direction and clean field name
      if field_name.startswith('-'):
        order_direction = 'desc'
        cleaned_field_name = field_name[1:]
      else:
        order_direction = 'asc'
        cleaned_field_name = field_name
      # determine index of field
      order_index = 0
      for index, field in enumerate(model._meta.fields):
        if field.name == cleaned_field_name:
          order_index = index
          break
      initial_order.append([order_index, order_direction])
  context['initial_order'] = initial_order
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
  min_numbers, max_numbers = {}, {}
  if hasattr(model, 'CustomMeta'):
    if hasattr(model.CustomMeta, 'min_numbers'):
      min_numbers = model.CustomMeta.min_numbers
    if hasattr(model.CustomMeta, 'max_numbers'):
      max_numbers = model.CustomMeta.max_numbers
  if hasattr(form_field.widget, 'input_type'):
    if form_field.widget.input_type == 'checkbox':
      form_field.widget.attrs['class'] = 'form-check-input'
    else:
      form_field.widget.attrs['class'] = 'form-control'
    # set minimum and maximum values for numeric model fields
    if form_field.widget.input_type == 'number':
      if min_numbers is not None:
        form_field.widget.attrs['min'] = min_numbers.get(field.name, 0)
      if max_numbers is not None:
        form_field.widget.attrs['max'] = max_numbers.get(field.name, 0)
  return form_field
