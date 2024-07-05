from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from django.core.serializers import serialize
from django.forms import CheckboxSelectMultiple, Textarea
from django.urls import reverse, reverse_lazy
from django_user_agents.utils import get_user_agent
from json import loads
from leaflet.forms.widgets import LeafletWidget

from antragsmanagement.models import GeometryObject, Requester, CleanupEventRequest, \
  CleanupEventEvent, CleanupEventVenue, CleanupEventDetails, CleanupEventContainer, \
  CleanupEventDump
from antragsmanagement.utils import belongs_to_antragsmanagement_authority, \
  get_antragsmanagement_authorities, has_necessary_permissions, is_antragsmanagement_admin, \
  is_antragsmanagement_requester, is_antragsmanagement_user
from toolbox.utils import format_date_datetime, is_geometry_field


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
    geometry_field_name = model.BaseMeta.geometry_field
    geometry_field = model._meta.get_field(geometry_field_name)
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['is_geometry_model'] = True
    context['geometry_field'] = geometry_field_name
    context['geometry_field_label'] = geometry_field.verbose_name
    context['geometry_required'] = False if geometry_field.blank else True
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


def clean_initial_field_values(fields, model, curr_obj):
  """
  returns cleaned form field values for initial setting in update views of passed model

  :param fields: form fields
  :param model: model
  :param curr_obj: object
  :return: cleaned form field values for initial setting in update views of passed model
  """
  initial_field_values = {}
  for field in fields:
    if field.__class__.__name__ == 'DateField':
      value = getattr(model.objects.get(pk=curr_obj.pk), field.name)
      initial_field_values[field.name] = value.strftime('%Y-%m-%d') if value else None
  return initial_field_values


def geometry_keeper(form_data, model, context_data):
  """
  returns passed context data with geometry kept in passed form data of passed model

  :param form_data: form data
  :param model: model
  :param context_data: context data
  :return: passed context data with geometry kept in passed form data of passed model
  """
  for field in model._meta.get_fields():
    # keep geometry (otherwise it would be lost on re-rendering)
    if is_geometry_field(field.__class__):
      geometry = form_data.get(field.name, None)
      if geometry and '0,0' not in geometry and '[]' not in geometry:
        context_data['geometry'] = geometry
  return context_data


def get_cleanupeventrequest_queryset(user, count=False):
  """
  either gets all objects of model CleanupEventRequest and returns them
  or counts objects of model CleanupEventRequest and returns the count

  :param user: user
  :param count: return objects count instead of objects?
  :return: either all objects of model CleanupEventRequest
  or objects count of model CleanupEventRequest
  """
  if belongs_to_antragsmanagement_authority(user):
    # only requests for which user is responsible
    queryset = CleanupEventRequest.objects.prefetch_related(
      'status',
      'requester',
      'cleanupeventevent',
      'cleanupeventdetails',
      'cleanupeventcontainer'
    ).filter(
      responsibilities__in=get_antragsmanagement_authorities(user)
    )
  else:
    queryset = CleanupEventRequest.objects.prefetch_related(
      'status',
      'requester',
      'cleanupeventevent',
      'cleanupeventdetails',
      'cleanupeventcontainer'
    )
  queryset = queryset.values(
    'id',
    'created',
    'status__name',
    'requester__pk',
    'cleanupeventevent__from_date',
    'cleanupeventevent__to_date',
    'cleanupeventdetails__waste_quantity__name',
    'cleanupeventcontainer__delivery_date',
    'cleanupeventcontainer__pickup_date'
  )
  for item in queryset:
    #
    # "status" field
    #
    # use "status" instead of "status_name"
    item['status'] = item['status__name']
    item.pop('status__name', None)
    #
    # "requester" field
    #
    # fetch related Requester object
    requester, requester_value = Requester.objects.only('pk').get(pk=item['requester__pk']), ''
    if (
        belongs_to_antragsmanagement_authority(user)
        or is_antragsmanagement_admin(user)
        or user.is_superuser
    ):
      requester_value = requester.verbose()
    elif requester.user_id == user.pk:
      requester_value = '<strong><em>eigener Antrag</strong></em>'
    else:
      requester_value = requester.pseudonym()
    # use "requester" instead of "requester__pk" and set it to text from Requester object
    item['requester'] = requester_value
    item.pop('requester__pk', None)
    #
    # "responsibilities" field
    #
    responsibilities_value = None
    # fetch CleanupEventRequest object
    request = CleanupEventRequest.objects.get(pk=item['id'])
    # if responsibilities exist
    if request.responsibilities.exists():
      # use list comprehension to create authorities' short names and join them with '<br>'
      responsibilities_value = '<br>'.join(
        [responsibility.short_name() for responsibility in request.responsibilities.all()]
      )
    # set "responsibilities" to authorities' short names
    item['responsibilities'] = responsibilities_value
    #
    # fields relating to event
    #
    # use "event_from" instead of "cleanupeventevent__from_date"
    item['event_from'] = item['cleanupeventevent__from_date']
    item.pop('cleanupeventevent__from_date', None)
    # use "event_to" instead of "cleanupeventevent__to_date"
    item['event_to'] = item['cleanupeventevent__to_date']
    item.pop('cleanupeventevent__to_date', None)
    #
    # fields relating to details
    #
    # use "details_waste_quantity" instead of "cleanupeventdetails__waste_quantity__name"
    item['details_waste_quantity'] = item['cleanupeventdetails__waste_quantity__name']
    item.pop('cleanupeventdetails__waste_quantity__name', None)
    # fetch related CleanupEventDetails object
    details = CleanupEventDetails.objects.filter(cleanupevent_request=item['id']).first()
    if details:
      waste_types_value = None
      # if waste types exist
      if details.waste_types.exists():
        # use list comprehension to join waste types with '<br>'
        waste_types_value = '<br>'.join(
          [waste_type.name for waste_type in details.waste_types.all()]
        )
      # otherwise use waste types annotation
      elif details.waste_types_annotation:
        waste_types_value = 'Sonstiges: ' + details.waste_types_annotation
      # set "details_waste_types" to waste types
      item['details_waste_types'] = waste_types_value
      equipments_value = None
      # if equipments exist
      if details.equipments.exists():
        # use list comprehension to join equipments with '<br>'
        equipments_value = '<br>'.join(
          [equipment.name for equipment in details.equipments.all()]
        )
      # set "details_equipments" to equipments
      item['details_equipments'] = equipments_value
    else:
      item['details_waste_types'] = None
      item['details_equipments'] = None
    #
    # fields relating to container
    #
    # use "container_delivery" instead of "cleanupeventcontainer__delivery_date"
    item['container_delivery'] = item['cleanupeventcontainer__delivery_date']
    item.pop('cleanupeventcontainer__delivery_date', None)
    # use "container_pickup" instead of "cleanupeventcontainer__pickup_date"
    item['container_pickup'] = item['cleanupeventcontainer__pickup_date']
    item.pop('cleanupeventcontainer__pickup_date', None)
  return queryset.count() if count else queryset


def get_cleanupeventrequest_feature(curr_object, curr_type, authorative_rights):
  """
  creates a GeoJSON feature based on passed object of model CleanupEventRequest and returns it

  :param curr_object: object of model CleanupEventRequest
  :param curr_type: type of object (i.e. where to fetch the geometry from)
  :param authorative_rights: user has authorative rights (i.e. add links)?
  :return: GeoJSON feature based on passed object of model CleanupEventRequest
  """
  # define mapping for passed type of object to get model class
  model_mapping = {
    'event': CleanupEventEvent,
    'venue': CleanupEventVenue,
    'container': CleanupEventContainer,
    'dump': CleanupEventDump
  }
  # get model class based on passed type of object
  model_class = model_mapping.get(curr_type)
  # perform query if valid model class was found
  if model_class:
    target = model_class.objects.filter(cleanupevent_request=curr_object['id']).first()
    if target:
      # GeoJSON-serialize target object
      target_geojson_serialized = loads(serialize('geojson', [target]))
      # define mapping for passed type of object to get tooltip prefix
      prefix_mapping = {
        'event': 'Fäche',
        'venue': 'Treffpunkt',
        'container': 'Containerstandort',
        'dump': 'Müllablageplatz'
      }
      # get tooltip prefix based on passed type of object
      prefix = prefix_mapping.get(curr_type)
      title = str(CleanupEventRequest.objects.get(pk=curr_object['id']))
      # define GeoJSON feature:
      # get geometry from GeoJSON-serialized target object,
      # get (meta) properties directly from passed object of model CleanupEventRequest
      geojson_feature = {
        'type': 'Feature',
        'geometry': target_geojson_serialized['features'][0]['geometry'],
        'properties': {
          '_tooltip': prefix + ' zu ' + title,
          '_title': title,
          '_filter_id': curr_object['id'],
          '_filter_created': curr_object['created'],
          '_filter_status': curr_object['status'],
          '_filter_responsibilities': curr_object['responsibilities'],
          'ID': curr_object['id'],
          'Eingang': format_date_datetime(curr_object['created']),
          'Status': curr_object['status'],
          'Antragsteller:in': curr_object['requester'],
          'Zuständigkeit(en)': curr_object['responsibilities'],
          'von': format_date_datetime(curr_object['event_from']),
          'bis': format_date_datetime(curr_object['event_to']),
          'Abfallmenge': curr_object['details_waste_quantity'],
          'Abfallart(en)': curr_object['details_waste_types'],
          'Austattung(en)': curr_object['details_equipments'],
          'Container-Stellung': format_date_datetime(curr_object['container_delivery']),
          'Container-Abholung': format_date_datetime(curr_object['container_pickup'])
        }
      }
      # add links if user has authorative rights
      if authorative_rights:
        geojson_feature['properties']['_link_request'] = reverse(
          viewname='antragsmanagement:cleanupeventrequest_authorative_update',
          kwargs={'pk': curr_object['id']}
        )
        event = CleanupEventEvent.objects.filter(cleanupevent_request=curr_object['id']).first()
        if event:
          geojson_feature['properties']['_link_event'] = reverse(
            viewname='antragsmanagement:cleanupeventevent_authorative_update',
            kwargs={'pk': event.pk}
          )
        venue = CleanupEventVenue.objects.filter(cleanupevent_request=curr_object['id']).first()
        if venue:
          geojson_feature['properties']['_link_venue'] = reverse(
            viewname='antragsmanagement:cleanupeventvenue_authorative_update',
            kwargs={'pk': venue.pk}
          )
        details = CleanupEventDetails.objects.filter(
          cleanupevent_request=curr_object['id']).first()
        if details:
          geojson_feature['properties']['_link_details'] = reverse(
            viewname='antragsmanagement:cleanupeventdetails_authorative_update',
            kwargs={'pk': details.pk}
          )
        container = CleanupEventContainer.objects.filter(
          cleanupevent_request=curr_object['id']).first()
        if container:
          link_container = reverse(
            viewname='antragsmanagement:cleanupeventcontainer_authorative_update',
            kwargs={'pk': container.pk}
          )
          geojson_feature['properties']['_link_container_delete'] = reverse(
            viewname='antragsmanagement:cleanupeventcontainer_delete',
            kwargs={'pk': container.pk}
          )
        else:
          link_container = reverse(
            viewname='antragsmanagement:cleanupeventcontainer_authorative_create',
            kwargs={'request_id': curr_object['id']}
          )
        geojson_feature['properties']['_link_container'] = link_container
        dump = CleanupEventDump.objects.filter(cleanupevent_request=curr_object['id']).first()
        if dump:
          link_dump = reverse(
            viewname='antragsmanagement:cleanupeventdump_authorative_update',
            kwargs={'pk': dump.pk}
          )
          geojson_feature['properties']['_link_dump_delete'] = reverse(
            viewname='antragsmanagement:cleanupeventdump_delete',
            kwargs={'pk': dump.pk}
          )
        else:
          link_dump = reverse(
            viewname='antragsmanagement:cleanupeventdump_authorative_create',
            kwargs={'request_id': curr_object['id']}
          )
        geojson_feature['properties']['_link_dump'] = link_dump
      return geojson_feature
  return {}


def get_corresponding_cleanupeventrequest_geometry(request_id, model, text):
  """
  returns geometry of passed model corresponding to passed CleanupEventRequest object

  :param request_id: primary key of CleanupEventRequest object to get corresponding geometry for
  :param model: model with geometry
  :param text: text to return along geometry
  :return: geometry of passed model corresponding to passed CleanupEventRequest object
  """
  geometry_object = model.objects.filter(cleanupevent_request=request_id).first()
  if geometry_object:
    geometry = getattr(geometry_object, model.BaseMeta.geometry_field)
    if geometry:
      return {
        'text': text,
        'geometry': GEOSGeometry(geometry).geojson
      }
    return None
  return None


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
