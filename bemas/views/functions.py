from django.conf import settings
from django.forms import Textarea
from django.urls import reverse
from django_user_agents.utils import get_user_agent
from leaflet.forms.widgets import LeafletWidget

from bemas.models import Codelist, GeometryObjectclass, Complaint, LogEntry, Originator
from bemas.utils import get_foreign_key_target_model, get_foreign_key_target_object, \
  is_bemas_admin, is_bemas_user, is_geometry_field


def add_codelist_context_elements(context, model, curr_object=None):
  """
  adds codelist related elements to a context and returns it

  :param context: context
  :param model: codelist model
  :param curr_object: codelist entry
  :return: context with codelist related elements added
  """
  context['codelist_name'] = model.__name__
  context['codelist_verbose_name'] = model._meta.verbose_name
  context['codelist_verbose_name_plural'] = model._meta.verbose_name_plural
  context['codelist_description'] = model.BasemodelMeta.description
  context['codelist_cancel_url'] = reverse('bemas:codelists_' + model.__name__.lower() + '_table')
  context['codelist_creation_url'] = reverse(
    'bemas:codelists_' + model.__name__.lower() + '_create'
  )
  if curr_object:
    context['codelist_deletion_url'] = reverse(
      'bemas:codelists_' + model.__name__.lower() + '_delete', args=[curr_object.pk]
    )
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
  context['objectclass_creation_url'] = reverse('bemas:' + model.__name__.lower() + '_create')
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
      # handle non-geometry related fields only!
      if not is_geometry_field(field.__class__):
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
  prefix = 'codelists_' if issubclass(model, Codelist) else ''
  context['tabledata_url'] = reverse(
    'bemas:' + prefix + model.__name__.lower() + '_tabledata'
  )
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
  model = field.model
  # get dictionary with numeric model fields (as keys) and their minimum legal values
  min_numbers, max_numbers = {}, {}
  if hasattr(model, 'CustomMeta'):
    if hasattr(model.CustomMeta, 'min_numbers'):
      min_numbers = model.CustomMeta.min_numbers
    if hasattr(model.CustomMeta, 'max_numbers'):
      max_numbers = model.CustomMeta.max_numbers
  # handle inputs
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
  # handle text areas
  elif issubclass(form_field.widget.__class__, Textarea):
    form_field.widget.attrs['class'] = 'form-control'
  # handle geometry related fields
  elif is_geometry_field(field.__class__):
    form_field = field.formfield(
      widget=LeafletWidget()
    )
  # field is array field?
  if is_array_field:
    # highlight corresponding form field as array field via custom HTML attribute
    form_field.widget.attrs['is_array_field'] = 'true'
  return form_field


def create_log_entry(model, object_pk, object_str, action, user):
  """
  creates new log entry based on given affected model, affected (target) object, action and user

  :param model: affected model
  :param object_pk: affected object id
  :param object_str: string representation of affected object (target object in some cases)
  :param action: action
  :param user: user
  """
  user_string = (
    user.first_name + ' ' + user.last_name if user.first_name and user.last_name else user.username
  )
  LogEntry.objects.create(
    model=model.__name__,
    object_pk=object_pk,
    object_str=object_str,
    action=action,
    user=user_string
  )


def generate_foreign_key_link(foreign_key_field, source_object):
  """
  generates a foreign key link by means of given foreign key field and source object and returns it

  :param foreign_key_field: foreign key field
  :param source_object: source object
  :return: foreign key link, generated by means of foreign key field and source object
  """
  target_model = get_foreign_key_target_model(foreign_key_field)
  target_object = get_foreign_key_target_object(source_object, foreign_key_field)
  return '<a href="' +\
    reverse('bemas:' + target_model.__name__.lower() + '_update', args=[target_object.pk]) +\
    '" title="' + target_model._meta.verbose_name + ' bearbeiten">' + str(target_object) + '</a>'


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


def set_generic_objectclass_create_update_delete_context(context, request, model, cancel_url,
                                                         curr_object=None):
  """
  sets generic object class context for create, update and/or delete views and returns it

  :param context: context
  :param request: request
  :param model: object class model
  :param cancel_url: custom cancel URL
  :param curr_object: object
  :return: generic object class context for create, update and/or delete views
  """
  # add default elements to context
  context = add_default_context_elements(context, request.user)
  # add user agent related elements to context
  context = add_user_agent_context_elements(context, request)
  # add other necessary elements to context
  context = add_generic_objectclass_context_elements(context, model)
  # optionally add custom cancel URL (called when cancel button is clicked) to context
  context['objectclass_cancel_url'] = (
    cancel_url if cancel_url else reverse('bemas:' + model.__name__.lower() + '_table')
  )
  # add deletion URL to context if object exists
  if curr_object:
    context['objectclass_deletion_url'] = reverse(
      'bemas:' + model.__name__.lower() + '_delete', args=[curr_object.pk]
    )
  # if object class contains geometry:
  # add geometry related information to context
  if issubclass(model, GeometryObjectclass):
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['REVERSE_SEARCH_RADIUS'] = settings.REVERSE_SEARCH_RADIUS
    context['objectclass_is_geometry_model'] = True
    context['objectclass_geometry_field'] = model.BasemodelMeta.geometry_field
  return context


def set_log_action_and_object_str(model, curr_object, changed_data):
  """
  sets action and string representation of affected object (target object in some cases)
  for a new log entry, based on given model, object and changed data, and returns them

  :param model: model
  :param curr_object: object
  :param changed_data: changed data
  :return: action and string representation of affected object (target object in some cases)
  for a new log entry, based on given model, object and changed data
  """
  if issubclass(model, Complaint):
    if 'originator' in changed_data:
      return 'updated_originator', str(curr_object.originator)
    elif 'status' in changed_data:
      return 'updated_status', str(curr_object.status)
  elif issubclass(model, Originator):
    if 'operator' in changed_data:
      return 'updated_operator', str(curr_object.operator)
  return None, None
