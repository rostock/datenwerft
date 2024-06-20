from django.conf import settings
from django.forms import CheckboxSelectMultiple, Textarea
from django.urls import reverse
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
  context['model_verbose_name_plural'] = model._meta.verbose_name_plural
  # if object contains geometry:
  # add geometry related information to context
  if issubclass(model, GeometryObject):
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['is_geometry_model'] = True
    context['geometry_field'] = model.BaseMeta.geometry_field
    context['geometry_type'] = model.BaseMeta.geometry_type
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


def add_table_context_elements(context, model, table_data_view_name):
  """
  adds table related elements to a context and returns it

  :param context: context
  :param model: model
  :param table_data_view_name: name of view for composing table data out of instances
  :return: context with table related elements added
  """
  context['objects_count'] = get_model_objects(model, True)
  column_titles = []
  address_handled = False
  for field in model._meta.fields:
    # handle addresses
    if field.name.startswith('address_') and not address_handled:
      # append one column for address string
      # instead of appending individual columns for all address related values
      column_titles.append('Anschrift')
      address_handled = True
    # ordinary columns
    elif not field.name.startswith('address_'):
      column_titles.append(field.verbose_name)
  context['column_titles'] = column_titles
  # determine initial order
  initial_order = []
  if model._meta.ordering:
    fields = []
    for field in model._meta.fields:
      fields.append(field)
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
      for index, field in enumerate(fields):
        if field.name == cleaned_field_name:
          order_index = index
          break
      initial_order.append([order_index, order_direction])
  context['initial_order'] = initial_order
  context['tabledata_url'] = reverse(table_data_view_name)
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
    if form_field.widget.input_type == 'select':
      # handle multiple selects
      if form_field.widget.__class__.__name__ == 'SelectMultiple':
        form_field.widget = CheckboxSelectMultiple()
      # handle ordinary (single) selects
      else:
        form_field.widget.attrs['class'] = 'form-select'
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


def get_model_objects(model, count=False):
  """
  either gets all objects of passed model and returns them
  or counts objects of passed model and returns the count

  :param model: model
  :param count: return objects count instead of objects?
  :return: either all objects of passed model or objects count of passed model
  """
  objects = model.objects.all()
  return objects.count() if count else objects
