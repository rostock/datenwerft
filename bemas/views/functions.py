from datetime import date
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.serializers import serialize
from django.forms import Select, Textarea
from django.urls import reverse
from django_user_agents.utils import get_user_agent
from json import dumps, loads
from leaflet.forms.widgets import LeafletWidget
from operator import itemgetter

from bemas.models import Codelist, GeometryObjectclass, Complaint, Contact, Event, LogEntry, \
  Originator, Status
from bemas.utils import LOG_ACTIONS, format_date_datetime, generate_user_string, \
  get_foreign_key_target_model, get_foreign_key_target_object, get_icon_from_settings, \
  get_json_data, is_bemas_admin, is_bemas_user, is_geometry_field


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
  objectclass_lower_name = model.__name__.lower()
  context['objectclass_lower_name'] = objectclass_lower_name
  context['objectclass_verbose_name'] = model._meta.verbose_name
  context['objectclass_verbose_name_plural'] = model._meta.verbose_name_plural
  context['objectclass_description'] = model.BasemodelMeta.description
  context['objectclass_definite_article'] = model.BasemodelMeta.definite_article
  context['objectclass_new'] = model.BasemodelMeta.new
  if not issubclass(model, LogEntry):
    context['objectclass_creation_url'] = reverse('bemas:' + objectclass_lower_name + '_create')
  return context


def add_sector_examples_context_element(context, sector):
  """
  adds sector examples to a context and returns it

  :param context: context
  :param sector: sectormodel
  :return: context with sector examples added
  """
  sectors = sector.objects.all()
  context['sector_examples'] = dumps({sector.pk: sector.examples for sector in sectors})
  return context


def add_table_context_elements(context, model, kwargs=None):
  """
  adds table related elements to a context and returns it

  :param context: context
  :param model: model
  :param kwargs: view kwargs
  :return: context with table related elements added
  """
  context['objects_count'] = get_model_objects(model, True, kwargs)
  column_titles = []
  address_handled = False
  for field in model._meta.fields:
    if not field.name.startswith('address_'):
      # handle non-geometry related fields and non-search content fields only!
      if not is_geometry_field(field.__class__) and not field.name == 'search_content':
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
  if issubclass(model, Codelist):
    context['tabledata_url'] = reverse('bemas:codelists_' + model.__name__.lower() + '_tabledata')
  else:
    if (
        issubclass(model, LogEntry)
        and 'model' in kwargs
        and kwargs['model']
        and 'object_pk' in kwargs
        and kwargs['object_pk']
    ):
      context['tabledata_url'] = reverse(
        'bemas:logentry_tabledata_model_object',
        args=[kwargs['model'], kwargs['object_pk']]
      )
    elif issubclass(model, LogEntry) and 'model' in kwargs and kwargs['model']:
      context['tabledata_url'] = reverse(
        'bemas:logentry_tabledata_model',
        args=[kwargs['model']]
      )
    elif issubclass(model, Event) and 'complaint_pk' in kwargs and kwargs['complaint_pk']:
      context['tabledata_url'] = reverse(
        'bemas:event_tabledata_complaint',
        args=[kwargs['complaint_pk']]
      )
    elif (
        (issubclass(model, Complaint) or issubclass(model, Originator))
        and 'subset_pk' in kwargs
        and kwargs['subset_pk']
    ):
      context['tabledata_url'] = reverse(
        'bemas:' + model.__name__.lower() + '_tabledata_subset',
        args=[kwargs['subset_pk']]
      )
    else:
      context['tabledata_url'] = reverse('bemas:' + model.__name__.lower() + '_tabledata')
  if not issubclass(model, LogEntry):
    context['logentry_url'] = reverse('bemas:logentry_table_model', args=[model.__name__])
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
  # handle date widgets
  if field.__class__.__name__ == 'DateField':
    form_field.widget.input_type = 'date'
  # convert text input for users to select input with all BEMAS users as choices
  elif field.name == 'user':
    users = list(
      User.objects.filter(
        groups__name__in=[settings.BEMAS_ADMIN_GROUP_NAME, settings.BEMAS_USERS_GROUP_NAME]
      ).values('first_name', 'last_name', 'username')
    )
    sorted_users = sorted(users, key=itemgetter('last_name', 'first_name', 'username'))
    user_list = []
    for user in sorted_users:
      user_list.append(generate_user_string(user))
    choices = [(user, user) for user in user_list]
    # prepend choices with empty value
    choices.insert(0, ('', '---------'))
    form_field.widget = Select(
      choices=choices
    )
  # handle inputs
  if hasattr(form_field.widget, 'input_type'):
    if form_field.widget.input_type == 'checkbox':
      form_field.widget.attrs['class'] = 'form-check-input'
    elif form_field.widget.input_type == 'select':
      form_field.widget.attrs['class'] = 'form-select'
      if form_field.widget.__class__.__name__ == 'SelectMultiple':
        form_field.widget.attrs['size'] = 5
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
  # handle geometry widgets
  elif is_geometry_field(field.__class__):
    form_field = field.formfield(
      widget=LeafletWidget()
    )
  # field is array field?
  if is_array_field:
    # highlight corresponding form field as array field via custom HTML attribute
    form_field.widget.attrs['is_array_field'] = 'true'
  return form_field


def create_geojson_feature(curr_object):
  """
  creates a GeoJSON feature based on given object and returns it

  :param curr_object: object
  :return: GeoJSON feature based on given object
  """
  # GeoJSON-serialize object
  object_geojson_serialized = loads(serialize('geojson', [curr_object]))
  model = curr_object.__class__.__name__.lower()
  pk = curr_object.pk
  # define GeoJSON feature:
  # get geometry from GeoJSON-serialized object,
  # get (meta) properties directly from object
  geojson_feature = {
    'type': 'Feature',
    'geometry': object_geojson_serialized['features'][0]['geometry'],
    'properties': {
      '_model': model,
      '_pk': pk,
      '_tooltip': str(curr_object),
      '_title': curr_object.__class__._meta.verbose_name,
      '_link_update': reverse('bemas:' + model + '_update', args=[pk]),
      '_link_delete': reverse('bemas:' + model + '_delete', args=[pk]),
      '_link_logentries': reverse(
        'bemas:logentry_table_model_object', args=[curr_object.__class__.__name__, pk])
    }
  }
  # add properties for map pop-up to GeoJSON feature
  for field in curr_object.__class__._meta.concrete_fields:
    if (
        getattr(curr_object, field.name)
        and (
          (
              issubclass(curr_object.__class__, Complaint)
              and field.name in (
                  'id', 'created_at', 'updated_at', 'date_of_receipt', 'status',
                  'status_updated_at', 'type_of_immission', 'address', 'originator',
                  'description', 'dms_link', 'storage_location'
              )
          )
          or (
              issubclass(curr_object.__class__, Originator)
              and field.name in (
                  'id', 'created_at', 'updated_at', 'sector', 'operator_organization',
                  'operator_person', 'description', 'address', 'dms_link'
              )
          )
        )
    ):
      geojson_feature['properties'][field.verbose_name] = get_json_data(curr_object, field.name)
  # object class complaint:
  if issubclass(curr_object.__class__, Complaint):
    # add events link as property to GeoJSON feature
    geojson_feature['properties']['_link_events'] = reverse(
      'bemas:event_table_complaint', args=[pk])
    # add complainers as property to GeoJSON feature
    complainers = ''
    complainers_organizations = Complaint.objects.get(pk=pk).complainers_organizations.all()
    if complainers_organizations:
      for index, organization in enumerate(complainers_organizations):
        complainers += '<br>' if index > 0 else ''
        complainers += str(organization)
    complainers_persons = Complaint.objects.get(pk=pk).complainers_persons.all()
    if complainers_persons:
      for index, person in enumerate(complainers_persons):
        complainers += '<br>' if index > 0 or complainers_organizations else ''
        complainers += str(person)
    # designate anonymous complaint if necessary
    if not complainers:
      complainers = 'anonyme Beschwerde'
    geojson_feature['properties']['Beschwerdeführung'] = complainers
  # add properties for filters to GeoJSON feature
  for field in curr_object.__class__._meta.concrete_fields:
    if (
        (
            issubclass(curr_object.__class__, Complaint)
            and field.name in (
                'id', 'date_of_receipt', 'status',
                'type_of_immission', 'originator', 'description'
            )
        )
        or (
            issubclass(curr_object.__class__, Originator)
            and field.name in (
                'sector', 'operator_organization', 'operator_person', 'description'
            )
        )
    ):
      geojson_feature['properties']['_' + field.name + '_'] = get_json_data(
        curr_object, field.name, True)
  if issubclass(curr_object.__class__, Complaint):
    geojson_feature['properties']['_originator__id_'] = get_json_data(
      curr_object.originator, 'id', True)
  return geojson_feature


def create_log_entry(model, object_pk, action, content, user):
  """
  creates new log entry based on given affected model, affected (target) object, action and user

  :param model: affected model
  :param object_pk: affected object id
  :param action: action
  :param content: content
  :param user: user
  """
  LogEntry.objects.create(
    model=model.__name__,
    object_pk=object_pk,
    action=action,
    content=content,
    user=generate_user_string(user)
  )


def generate_foreign_key_objects_list(foreign_key_objects, formation_hint=None):
  """
  generates an HTML list of given foreign key objects and returns it

  :param foreign_key_objects: foreign key objects
  :param formation_hint: formation hint
  :return: HTML list of given foreign key objects
  """
  object_list = ''
  for foreign_key_object in foreign_key_objects:
    link_text, suffix = '', ''
    object_list += ('<li>' if len(foreign_key_objects) > 1 else '')
    if issubclass(foreign_key_object.__class__, Contact) and formation_hint == 'person':
      if foreign_key_object.function:
        suffix = ' mit der Funktion ' + foreign_key_object.function
      foreign_key_object = foreign_key_object.person
    elif issubclass(foreign_key_object.__class__, Contact) and formation_hint == 'organization':
      if foreign_key_object.function:
        suffix = ' (dort mit der Funktion ' + foreign_key_object.function + ')'
      foreign_key_object = foreign_key_object.organization
    if issubclass(foreign_key_object.__class__, Event):
      link_text = foreign_key_object.type_of_event_and_created_at()
    object_list += generate_foreign_key_link_simplified(
      foreign_key_object.__class__, foreign_key_object, link_text)
    object_list += suffix
    object_list += ('</li>' if len(foreign_key_objects) > 1 else '')
  if len(foreign_key_objects) > 1:
    return '<ul class="object_list">' + object_list + '</ul>'
  else:
    return object_list


def generate_foreign_key_link(foreign_key_field, source_object, link_text=None):
  """
  generates a foreign key link by means of given foreign key field and source object and returns it

  :param foreign_key_field: foreign key field
  :param source_object: source object
  :param link_text: link text
  :return: foreign key link, generated by means of given foreign key field and source object
  """
  target_model = get_foreign_key_target_model(foreign_key_field)
  target_object = get_foreign_key_target_object(source_object, foreign_key_field)
  if issubclass(target_model, Originator):
    link_text = target_object.sector_and_operator()
  elif issubclass(target_model, Event):
    link_text = target_object.type_of_event_and_created_at()
  return generate_foreign_key_link_simplified(target_model, target_object, link_text)


def generate_foreign_key_link_simplified(target_model, target_object, link_text=None):
  """
  generates a foreign key link by means of given target model and target object and returns it

  :param target_model: target model
  :param target_object: target object
  :param link_text: link text
  :return: foreign key link, generated by means of given target model and target object
  """
  if not link_text:
    link_text = str(target_object)
  target_model_name = target_model.__name__.lower()
  icon = '<i class="fas fa-' + get_icon_from_settings(target_model_name) + '"></i>'
  return '<a href="' + \
    reverse('bemas:' + target_model_name + '_update', args=[target_object.pk]) + \
    '" title="' + target_model._meta.verbose_name + ' bearbeiten">' + \
    icon + ' ' + link_text + '</a>'


def get_lastest_activity_objects(count=5, template=True):
  """
  returns `count` lastest activity objects (i.e. log entries)

  :param count: count of lastest activity objects
  :param template: objects representation for template?
  :return: `count` lastest activity objects (i.e. log entries)
  """
  # get `count` lastest log entries as activity objects
  activity_objects = LogEntry.objects.order_by('-created_at')[:count]
  # optionally transform activity objects into representations for a template
  return transform_activity_objects(activity_objects) if template else activity_objects


def get_model_objects(model, count=False, kwargs=None):
  """
  either gets all objects of given model and returns them
  or counts objects of given model and returns the count

  :param model: model
  :param kwargs: view kwargs
  :param count: return objects count instead of objects?
  :return: either all objects of given model or objects count of given model
  """
  if (
      issubclass(model, LogEntry)
      and kwargs
      and 'model' in kwargs
      and kwargs['model']
      and 'object_pk' in kwargs
      and kwargs['object_pk']
  ):
    objects = LogEntry.objects.filter(
      model=kwargs['model'], object_pk=kwargs['object_pk'])
  elif (
      issubclass(model, LogEntry)
      and kwargs
      and 'model' in kwargs
      and kwargs['model']
  ):
    objects = LogEntry.objects.filter(model=kwargs['model'])
  elif (
      issubclass(model, Event)
      and kwargs
      and 'complaint_pk' in kwargs
      and kwargs['complaint_pk']
  ):
    objects = Event.objects.filter(complaint=kwargs['complaint_pk'])
  else:
    objects = model.objects.all()
  return objects.count() if count else objects


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


def set_log_action_and_content(model, curr_object, changed_attribute, cleaned_data=None):
  """
  sets action and content of affected object for a new log entry,
  based on given model, object and changed data attribute, and returns them

  :param model: model
  :param curr_object: object
  :param changed_attribute: changed data attribute
  :param cleaned_data: cleaned form data
  (if many-to-many-relationships where changed, the new data is only found in here)
  :return: action and content of affected object for a new log entry,
  based on given model, object and changed data attribute
  """
  if issubclass(model, Complaint):
    if changed_attribute == 'originator':
      return 'updated_originator', str(curr_object.originator)
    elif changed_attribute == 'status':
      return 'updated_status', str(curr_object.status)
    elif changed_attribute == 'complainers_organizations':
      string = ''
      for index, organization in enumerate(cleaned_data['complainers_organizations'].all()):
        string += ', ' if index > 0 else ''
        string += str(organization)
      if string:
        return 'updated_complainers_organizations', string
      else:
        return 'cleared_complainers_organizations', '/'
    elif changed_attribute == 'complainers_persons':
      string = ''
      for index, person in enumerate(cleaned_data['complainers_persons'].all()):
        string += ', ' if index > 0 else ''
        string += str(person)
      if string:
        return 'updated_complainers_persons', string
      else:
        return 'cleared_complainers_persons', '/'
  elif issubclass(model, Originator):
    if changed_attribute == 'operator_organization':
      return 'updated_operator_organization', str(curr_object.operator_organization)
    elif changed_attribute == 'operator_person':
      return 'updated_operator_person', str(curr_object.operator_person)
  return None, None


def transform_activity_objects(activity_objects):
  """
  returns representations for a template of given activity objects

  :param activity_objects: activity objects
  :return: representations for a template of given activity objects
  """
  activity_objects_list = []
  for activity_object in activity_objects:
    # set appropriate icon
    icon = get_icon_from_settings(activity_object.action)
    if activity_object.action.startswith('cleared_'):
      icon = get_icon_from_settings('deleted')
    elif activity_object.action == 'updated_status':
      icon = Status.objects.filter(title=activity_object.content)[0].icon
    elif activity_object.action.startswith('updated_'):
      icon = get_icon_from_settings('updated')
    # set appropriate model information
    model = apps.get_app_config('bemas').get_model(activity_object.model)
    model_title = model._meta.verbose_name
    model_icon = '<i class="fas fa-{}"></i>'.format(get_icon_from_settings(model.__name__.lower()))
    model_text = model_icon + ' ' + model_title
    # set appropriate action information
    action = LOG_ACTIONS[activity_object.action]
    if activity_object.action == 'created' or activity_object.action == 'deleted':
      action = '<em>#{}</em> '.format(activity_object.object_pk) + action
    elif activity_object.action == 'updated_status':
      action += ' auf <em>{}</em>'.format(activity_object.content)
    # set appropriate object link
    link = ''
    model_name = model.__name__.lower()
    if model.objects.filter(pk=activity_object.object_pk).exists():
      link = reverse('bemas:' + model_name + '_update', args=[activity_object.object_pk])
    # set appropriate datetime information
    created_at = activity_object.created_at
    if created_at.date() == date.today():
      created_at = format_date_datetime(created_at, True)
    else:
      created_at = format_date_datetime(created_at)
    activity_object_dict = {
      'icon': icon,
      'user': activity_object.user,
      'model': model_text,
      'action': action,
      'created_at': created_at,
      'link': link,
      'tooltip': model_title + ' bearbeiten' if link else ''
    }
    activity_objects_list.append(activity_object_dict)
  return activity_objects_list
