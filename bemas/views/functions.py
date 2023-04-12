from django.urls import reverse
from django_user_agents.utils import get_user_agent

from bemas.models import Codelist
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
  context['codelist_clone_url'] = reverse('bemas:codelists_' + model.__name__.lower() + '_create')
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


def add_generic_objectclass_context_elements(context, model):
  """
  adds generic object class related elements to a context and returns it

  :param context: context
  :param model: object class model
  :return: context with generic object class related elements added
  """
  context['objectclass_name'] = model.__name__
  context['objectclass_verbose_name'] = model._meta.verbose_name
  context['objectclass_verbose_name_plural'] = model._meta.verbose_name_plural
  context['objectclass_description'] = model.BasemodelMeta.description
  context['objectclass_definite_article'] = model.BasemodelMeta.definite_article
  context['objectclass_new'] = model.BasemodelMeta.new
  context['objectclass_clone_url'] = reverse('bemas:' + model.__name__.lower() + '_create')
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
  address_handled = False
  for field in model._meta.fields:
    if not field.name.startswith('address_'):
      column_titles.append(field.verbose_name)
    # handle addresses
    elif field.name.startswith('address_') and not address_handled:
      # append one column for address string
      # instead of appending individual columns for all address related values
      column_titles.append('Anschrift')
      address_handled = True
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
  is_array_field = False
  # field is array field?
  if field.__class__.__name__ == 'ArrayField':
    # override the class of the field by the class of its base field
    field = field.base_field
    is_array_field = True
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
    elif form_field.widget.input_type == 'select':
      form_field.widget.attrs['class'] = 'form-select'
    else:
      form_field.widget.attrs['class'] = 'form-control'
    # set minimum and maximum values for numeric model fields
    if form_field.widget.input_type == 'number':
      if min_numbers is not None:
        form_field.widget.attrs['min'] = min_numbers.get(field.name)
      if max_numbers is not None:
        form_field.widget.attrs['max'] = max_numbers.get(field.name)
  # field is array field?
  if is_array_field:
    # highlight corresponding form field as array field via custom HTML attribute
    form_field.widget.attrs['is_array_field'] = 'true'
  return form_field


def generate_protected_objects_list(protected_objects):
  """
  generates an HTML list of given protected objects and returns it

  :param protected_objects: protected objects
  :return: HTML list of given protected objects
  """
  object_list = ''
  for protected_object in protected_objects:
    object_list += ('<li>' if len(protected_objects) > 1 else '')
    object_list += '<strong><em>' + str(protected_object) + '</em></strong> '
    if issubclass(protected_object.__class__, Codelist):
      object_list += 'aus Codeliste '
    else:
      object_list += 'aus Objektklasse '
    object_list += '<strong>' + protected_object._meta.verbose_name_plural + '</strong>'
    object_list += ('</li>' if len(protected_objects) > 1 else '')
  if len(protected_objects) > 1:
    return '<ul class="error_object_list">' + object_list + '</ul>'
  else:
    return object_list


def set_generic_objectclass_create_update_delete_context(context, request, model, cancel_url):
  """
  sets generic object class context for create, update and/or delete views and returns it

  :param context: context
  :param request: request
  :param model: object class model
  :param cancel_url: custom cancel URL
  :return: generic object class context for create, update and/or delete views
  """
  # add default elements to context
  context = add_default_context_elements(context, request.user)
  # add user agent related elements to context
  context = add_user_agent_context_elements(context, request)
  # add other necessary elements to context
  context = add_generic_objectclass_context_elements(context, model)
  # optionally add custom cancel URL (called when cancel button is clicked) to context
  context['cancel_url'] = (
    cancel_url if cancel_url else reverse('bemas:' + model.__name__.lower() + '_table')
  )
  return context
