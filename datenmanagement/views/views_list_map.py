from datetime import date, datetime, timezone
from decimal import Decimal
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import serialize
from django.urls import reverse
from django.utils.html import escape
from django.views.generic.base import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from jsonview.views import JsonView
from json import dumps, loads
from re import IGNORECASE, match, sub
from time import time
from zoneinfo import ZoneInfo

from datenmanagement.utils import get_data, get_thumb_url, localize_number
from toolbox.models import SuitableFor
from toolbox.utils import optimize_datatable_filter
from .functions import add_basic_model_context_elements, add_user_agent_context_elements, \
  get_model_objects


class TableDataCompositionView(BaseDatatableView):
  """
  view for table data composition of a model
  """

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    model_name = self.model.__name__
    self.model_name = model_name
    self.model_name_lower = model_name.lower()
    self.model_is_editable = self.model.BasemodelMeta.editable
    self.fields_with_foreign_key_to_linkify = (
      self.model.BasemodelMeta.fields_with_foreign_key_to_linkify)
    self.columns = self.model.BasemodelMeta.list_fields
    self.columns_with_number = self.model.BasemodelMeta.list_fields_with_number
    self.columns_with_date = self.model.BasemodelMeta.list_fields_with_date
    self.columns_with_datetime = self.model.BasemodelMeta.list_fields_with_datetime
    self.columns_with_foreign_key = self.model.BasemodelMeta.list_fields_with_foreign_key
    self.column_as_highlight_flag = self.model.BasemodelMeta.highlight_flag
    self.thumbs = self.model.BasemodelMeta.thumbs
    super().__init__(*args, **kwargs)

  def get_initial_queryset(self):
    if self.kwargs and 'subset_id' in self.kwargs and self.kwargs['subset_id']:
      return get_model_objects(self.model, self.kwargs['subset_id'])
    else:
      return get_model_objects(self.model)

  def prepare_results(self, qs):
    """
    loops passed queryset, creates cleaned-up JSON representation of the queryset and returns it

    :param qs: queryset
    :return: cleaned-up JSON representation of the queryset
    """
    json_data = []
    for item in qs:
      item_data = []
      item_pk = getattr(item, self.model._meta.pk.name)
      if (
          self.model_is_editable and
          self.request.user.has_perm('datenmanagement.delete_' + self.model_name_lower)
      ):
        item_data.append(
          '<input class="action-checkbox" type="checkbox" value="' + str(item_pk) + '">')
      for column in self.columns:
        # all columns except address strings!
        if not column == 'anschrift':
          value = getattr(item, column)
          data = None
          # handle non-empty fields only!
          if value is not None:
            # format foreign keys
            if (
                self.columns_with_foreign_key
                and column in self.columns_with_foreign_key
                and self.fields_with_foreign_key_to_linkify
                and column in self.fields_with_foreign_key_to_linkify
            ):
              foreign_model = value._meta.label
              foreign_model_primary_key = value._meta.pk.name
              foreign_model_title = self.columns.get(column)
              foreign_model_attribute_for_text = self.columns_with_foreign_key.get(column)
              data = '<a href="' + reverse(
                  'datenmanagement:' + foreign_model.replace(
                      value._meta.app_label + '.',
                      ''
                  ) + '_change',
                  args=[getattr(value, foreign_model_primary_key)]
              ) + '" target="_blank" rel="noopener noreferrer" class="required" title="'\
                + foreign_model_title + ' ansehen oder bearbeiten">' + str(
                  getattr(value, foreign_model_attribute_for_text)) + '</a>'
            # format numbers
            elif self.columns_with_number and column in self.columns_with_number:
              if isinstance(value, Decimal) or match(r"^[0-9]+\.[0-9]+$", str(value)):
                data = localize_number(Decimal(str(value)))
              else:
                data = value
            # format dates
            elif self.columns_with_date and column in self.columns_with_date:
              data = datetime.strptime(str(value), '%Y-%m-%d').strftime('%d.%m.%Y')
            # format datetimes
            elif self.columns_with_datetime and column in self.columns_with_datetime:
              datetimestamp_str = sub(r'([+-][0-9]{2}):', '\\1', str(value))
              datetimestamp = datetime.strptime(datetimestamp_str, '%Y-%m-%d %H:%M:%S%z').\
                replace(tzinfo=timezone.utc).astimezone(ZoneInfo(settings.TIME_ZONE))
              datetimestamp_str = datetimestamp.strftime('%d.%m.%Y, %H:%M:%S Uhr')
              data = datetimestamp_str
            # handle highlight flags
            elif self.column_as_highlight_flag and column == self.column_as_highlight_flag:
              data = '<p class="text-danger" title="Konflikt(e) vorhanden!">ja</p>'
            # handle photo files
            elif column == 'foto':
              try:
                data = ('<a href="' + value.url + '?' + str(time()) +
                        '" target="_blank" rel="noopener noreferrer" ' +
                        'title="große Ansicht öffnen…">')
                if self.thumbs:
                  data += '<img src="' + get_thumb_url(
                      value.url) + '?' + str(
                      time()) + '" alt="Vorschau" />'
                else:
                  data += '<img src="' + value.url + '?' + str(
                      time()) + '" alt="Vorschau" width="70px" />'
                data += '</a>'
              except ValueError:
                pass
            # handle PDF files
            elif column == 'dokument' or column == 'pdf':
              try:
                data = '<a href="' + value.url + '?' + str(
                    time()) + '" target="_blank" rel="noopener noreferrer" title="' + (
                    ('PDF' if column == 'pdf' else 'Dokument')) + ' öffnen…">Link zum ' + (
                    ('PDF' if column == 'pdf' else 'Dokument')) + '</a>'
              except ValueError:
                pass
            # format Boolean ``True``
            elif value is True:
              data = 'ja'
            # format Boolean ``False``
            elif value is False:
              data = 'nein'
            # format lists
            elif type(value) in [list, tuple]:
              data = ', '.join(map(str, value))
            # format external links
            elif isinstance(value, str) and value.startswith('http'):
              data = ('<a href="' + value +
                      '" target="_blank" rel="noopener noreferrer" title="Link öffnen…">' +
                      value + '</a>')
            # format colors
            elif isinstance(value, str) and match(r"^#[a-f0-9]{6}$", value, IGNORECASE):
              data = '<div style="background-color:' + value + '" title="Hex-Wert: ' \
                     + value + ' || RGB-Wert: ' + str(int(value[1:3], 16)) + ', ' \
                     + str(int(value[3:5], 16)) + ', ' + str(int(value[5:7], 16)) \
                     + '">&zwnj;</div>'
            # take all other values as they are
            else:
              data = escape(value)
          item_data.append(data)
        # handle address strings
        else:
          # append address string once
          # instead of appending individual strings for all address related values
          item_data.append(self.model.objects.get(pk=item_pk).address())
      # append links for updating, viewing and/or deleting
      if self.model_is_editable:
        links = ''
        if self.request.user.has_perm('datenmanagement.change_' + self.model_name_lower):
          links = '<a href="' + \
                  reverse('datenmanagement:' + self.model_name + '_change', args=[item_pk]) + \
                  '"><i class="fas fa-edit" title="Datensatz bearbeiten"></i></a>'
        elif self.request.user.has_perm('datenmanagement.view_' + self.model_name_lower):
          links = '<a href="' + \
                  reverse('datenmanagement:' + self.model_name + '_change', args=[item_pk]) + \
                  '"><i class="fas fa-eye" title="Datensatz ansehen"></i></a>'
        if self.request.user.has_perm('datenmanagement.delete_' + self.model_name_lower):
          links += '<a class="ms-2" href="' + \
                   reverse('datenmanagement:' + self.model_name + '_delete', args=[item_pk]) + \
                   '"><i class="fas fa-trash" title="Datensatz löschen"></i></a>'
        item_data.append(links)
      json_data.append(item_data)
    return json_data

  def filter_queryset(self, qs):
    """
    filters passed queryset

    :param qs: queryset
    :return: filtered queryset
    """
    current_search = self.request.GET.get('search[value]', None)
    if current_search:
      qs_params = None
      for search_element in current_search.lower().split():
        qs_params_inner = None
        for column in self.columns:
          # take care of foreign key columns
          if self.columns_with_foreign_key:
            column_with_foreign_key = self.columns_with_foreign_key.get(column)
            if column_with_foreign_key is not None:
              column = column + str('__') + column_with_foreign_key
          qs_params_inner = optimize_datatable_filter(search_element, column, qs_params_inner)
        qs_params = qs_params & qs_params_inner if qs_params else qs_params_inner
      qs = qs.filter(qs_params)
    return qs

  def ordering(self, qs):
    """
    sorts passed queryset

    :param qs: queryset
    :return: sorted queryset
    """
    # assume initial order since multiple column sorting is prohibited
    if self.request.GET.get('order[1][column]') is not None:
      return qs
    elif self.request.GET.get('order[0][column]') is not None:
      order_column = self.request.GET.get('order[0][column]')
      order_dir = self.request.GET.get('order[0][dir]', None)
      column_names = []
      # careful here!
      # use the same clauses as in prepare_results() above since otherwise,
      # the wrong order columns could be choosed
      address_handled = False
      for column in self.columns:
        # all columns except address strings!
        if not column == 'anschrift':
          column_names.append(column)
        # handle address strings
        else:
          column_names.append('anschrift_strasse')
      column_name = column_names[int(order_column) - 1]
      directory = '-' if order_dir is not None and order_dir == 'desc' else ''
      return qs.order_by(directory + column_name)


class TableListView(TemplateView):
  """
  view for table page of a model

  :param model: model
  """

  model = None

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    model_name = self.model.__name__
    model_name_lower = model_name.lower()
    context = super().get_context_data(**kwargs)
    # add user agent related elements to context
    context = add_user_agent_context_elements(context, self.request)
    # add basic model related elements to context
    context = add_basic_model_context_elements(context, self.model)
    # add further elements to context
    if (
        self.model.BasemodelMeta.editable
        and self.request.user.has_perm('datenmanagement.delete_' + model_name_lower)
    ):
      context['actions'] = True
      context['url_model_deleteimmediately_placeholder'] = reverse(
        'datenmanagement:' + model_name + '_deleteimmediately', args=['worschdsupp'])
    context['column_titles'] = list(self.model.BasemodelMeta.list_fields.values()) if (
      self.model.BasemodelMeta.list_fields) else None
    if (
        self.model.BasemodelMeta.editable
        and (
          self.request.user.has_perm('datenmanagement.change_' + model_name_lower)
          or self.request.user.has_perm('datenmanagement.delete_' + model_name_lower)
          or self.request.user.has_perm('datenmanagement.view_' + model_name_lower)
        )
    ):
      context['column_actions'] = True
    if (
        self.model.BasemodelMeta.editable
        and self.request.user.has_perm('datenmanagement.add_' + model_name_lower)
    ):
      context['url_model_add'] = reverse('datenmanagement:' + model_name + '_add')
      if self.model.BasemodelMeta.geometry_type:
        context['url_model_map'] = reverse('datenmanagement:' + model_name + '_map')
        context['url_model_map_subset_placeholder'] = reverse(
          'datenmanagement:' + model_name + '_map_subset', args=['worschdsupp'])
    context['url_model_tabledata'] = reverse('datenmanagement:' + model_name + '_data')
    if self.kwargs and 'subset_id' in self.kwargs and self.kwargs['subset_id']:
      subset_id = kwargs['subset_id']
      context['subset_id'] = subset_id
      context['objects_count'] = get_model_objects(self.model, subset_id, True)
      context['url_model_tabledata_subset'] = reverse(
        'datenmanagement:' + model_name + '_data_subset', args=[subset_id])
    else:
      context['objects_count'] = get_model_objects(self.model, None, True)
    context['url_back'] = reverse('datenmanagement:' + model_name + '_start')
    content_type = ContentType.objects.get_for_model(self.model)
    suitable_templates = SuitableFor.objects.filter(datenthema=content_type)
    context['suitables'] = suitable_templates
    return context


class MapDataCompositionView(JsonView):
  """
  view for map data composition of a model

  * limit: limit to n database objects (SQL: LIMIT)
  * offset: all other database objects starting from the n-th database object (SQL: OFFSET)

  :param model: model
  """

  model = None

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    model_name = self.model.__name__
    self.model_name = model_name
    self.model_name_lower = model_name.lower()
    self.model_is_editable = self.model.BasemodelMeta.editable
    self.model_pk_field_name = self.model._meta.pk.name
    super().__init__(*args, **kwargs)

  def get_context_data(self, **kwargs):
    """
    returns GeoJSON feature collection

    :param kwargs:
    :return: GeoJSON feature collection
    """
    feature_collection, limit, offset, objects = None, None, None, None
    if self.request.GET.get('limit'):
      limit = int(self.request.GET.get('limit'))
    if self.request.GET.get('offset'):
      offset = int(self.request.GET.get('offset'))
    if self.kwargs and 'subset_id' in self.kwargs and self.kwargs['subset_id']:
      objects = get_model_objects(self.model, self.kwargs['subset_id'])
    else:
      objects = get_model_objects(self.model)
    # handle objects
    if objects:
      if limit is not None and offset is not None:
        objects = objects[offset:(offset + limit)]
      elif limit is not None:
        objects = objects[:limit]
      # declare empty GeoJSON feature collection
      feature_collection = {
          'type': 'FeatureCollection',
          'features': []
      }
      for curr_object in objects:
        # only if geometry is not empty...
        if curr_object.geometrie:
          # serialize object as GeoJSON
          object_serialized = loads(serialize('geojson', [curr_object], srid=25833))
          # create tooltip
          if self.model.BasemodelMeta.map_feature_tooltip_field:
            data = getattr(curr_object, self.model.BasemodelMeta.map_feature_tooltip_field)
            if isinstance(data, date):
              data = data.strftime('%d.%m.%Y')
            elif isinstance(data, datetime):
              data = data.strftime('%d.%m.%Y, %H:%M:%S Uhr')
            tooltip = str(data)
          elif self.model.BasemodelMeta.map_feature_tooltip_fields:
            previous_value = ''
            tooltip_value = ''
            index = 0
            for field in self.model.BasemodelMeta.map_feature_tooltip_fields:
              field_value = ''
              if field and getattr(curr_object, field) is not None:
                field_value = str(getattr(curr_object, field))
              tooltip_value = (
                  # place spaces between individual tooltip components
                  # but not between housenumber and housenumber suffix
                  tooltip_value + (
                      '' if (match(r'^[a-z]$', field_value) and
                             match(r'^[0-9]+$', previous_value)) else ' '
                  ) + field_value if index > 0 else field_value
              )
              index += 1
              previous_value = field_value
            tooltip = tooltip_value.strip()
          else:
            tooltip = str(curr_object.pk)
          # create GeoJSON feature:
          # * get geometry from serialized GeoJSON
          # * get properties from previously declared variables
          feature = {
              'type': 'Feature',
              'geometry': object_serialized['features'][0]['geometry'],
              'properties': {
                  self.model_pk_field_name: str(curr_object.pk),
                  'tooltip': tooltip
              },
              'crs': {
                  'type': 'name',
                  'properties': {
                      'name': 'urn:ogc:def:crs:EPSG::25833'
                  }
              }
          }
          if self.model_is_editable:
            # set object link as property
            feature['properties']['link'] = (
                reverse('datenmanagement:' + self.model_name + '_change', args=[curr_object.pk])
            )
          # optional: mark object as inactive
          if hasattr(curr_object, 'aktiv') and curr_object.aktiv is False:
            feature['properties']['inaktiv'] = 'true'
          # optional: mark object as to hide it initially
          if self.model.BasemodelMeta.map_filter_hide_initial:
            if str(
                getattr(
                    curr_object, list(
                        self.model.BasemodelMeta.map_filter_hide_initial.keys())[0])) == str(
                list(
                    self.model.BasemodelMeta.map_filter_hide_initial.values())[0]):
              feature['properties']['hide_initial'] = 'true'
          # optional: mark object as to highlight it
          if self.model.BasemodelMeta.highlight_flag:
            data = getattr(curr_object, self.model.BasemodelMeta.highlight_flag)
            if data:
              feature['properties']['highlight'] = data
          # optional: set deadline map filter as properties
          if self.model.BasemodelMeta.map_deadlinefilter_fields:
            for index, field in enumerate(self.model.BasemodelMeta.map_deadlinefilter_fields):
              data = getattr(curr_object, field)
              if isinstance(data, date):
                data = data.strftime('%Y-%m-%d')
              elif isinstance(data, datetime):
                data = data.strftime('%Y-%m-%d %H:%M:%S')
              feature['properties']['deadline_' + str(index)] = str(data)
              # additionally set field as an ordinary map filter property, too
              feature['properties'][field] = str(data)
          # optional: set deadline interval map filter as properties
          if self.model.BasemodelMeta.map_intervalfilter_fields:
            for field in self.model.BasemodelMeta.map_intervalfilter_fields.keys():
              feature['properties'][field] = str(get_data(curr_object, field))
          # optional: set all other map filters as properties
          if self.model.BasemodelMeta.map_filter_fields:
            for field in self.model.BasemodelMeta.map_filter_fields.keys():
              feature['properties'][field] = str(get_data(curr_object, field))
          # add GeoJSON feature to GeoJSON feature collection
          feature_collection['features'].append(feature)
    return feature_collection


class MapListView(TemplateView):
  """
  view for map page of a model

  :param model: model
  """

  model = None

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    # declare variables for filter fields that are to act as interval map filters,
    # one variable with the minimum value and one variable with the maximum value
    interval_filter_min = None
    interval_filter_max = None
    if self.model.BasemodelMeta.map_intervalfilter_fields:
      # define field for minimum values
      field_name = list(self.model.BasemodelMeta.map_intervalfilter_fields.keys())[0]
      # construct NOT NULL filter
      field_name_isnull = field_name + '__isnull'
      # get minimum value and insert into declared variable
      interval_filter_min = self.model.objects.exclude(**{field_name_isnull: True}).order_by(
          field_name).values_list(field_name, flat=True).first()
      if isinstance(interval_filter_min, date):
        interval_filter_min = interval_filter_min.strftime('%Y-%m-%d')
      elif isinstance(interval_filter_min, datetime):
        interval_filter_min = interval_filter_min.strftime('%Y-%m-%d %H:%M:%S')
      # define field for maximum values
      field_name = list(self.model.BasemodelMeta.map_intervalfilter_fields.keys())[1]
      # construct NOT NULL filter
      field_name_isnull = field_name + '__isnull'
      # get maximum value and insert into declared variable
      interval_filter_max = self.model.objects.exclude(**{field_name_isnull: True}).order_by(
          field_name).values_list(field_name, flat=True).last()
      if isinstance(interval_filter_max, date):
        interval_filter_max = interval_filter_max.strftime('%Y-%m-%d')
      elif isinstance(interval_filter_max, datetime):
        interval_filter_max = interval_filter_max.strftime('%Y-%m-%d %H:%M:%S')
    # declare dictionary for filter fields that are to act as selections
    list_filter_lists = {}
    if self.model.BasemodelMeta.map_filter_fields_as_list:
      # go through all appropriately defined fields...
      for field_name in self.model.BasemodelMeta.map_filter_fields_as_list:
        # identify suitable target model
        target_model = self.model._meta.get_field(field_name).remote_field.model
        # identify the suitable field in the target model for sorting
        foreign_field_name_ordering = target_model._meta.ordering[0]
        # identify the suitable field in the target model for display
        if target_model.BasemodelMeta.naming:
          foreign_field_name_naming = target_model.BasemodelMeta.naming
        else:
          foreign_field_name_naming = foreign_field_name_ordering
        # construct NOT NULL filter
        field_name_isnull = field_name + '__isnull'
        # sorted list of all unique values of the matching field obtained from the target model
        value_list = list(
            self.model.objects.exclude(**{field_name_isnull: True}).order_by(
                field_name + '__' + foreign_field_name_ordering).values_list(
                field_name + '__' + foreign_field_name_naming, flat=True).distinct())
        # convert decimal numbers in list to strings,
        # since decimal numbers cannot be serialized as JSON
        cleaned_value_list = []
        for value in value_list:
          cleaned_value_list.append(str(value) if isinstance(value, Decimal) else value)
        # insert list into declared dictionary
        list_filter_lists[field_name] = cleaned_value_list
    # declare dictionary for filter fields that are to act as checkbox sets
    checkbox_filter_lists = {}
    if self.model.BasemodelMeta.map_filter_fields:
      # go through all appropriately defined fields...
      for field_name in self.model.BasemodelMeta.map_filter_fields:
        # if it is a ChoiceArrayField or the field shall explicitly function as a checkbox set...
        if (
          self.model._meta.get_field(field_name).__class__.__name__ == 'ChoiceArrayField'
          or (
            self.model.BasemodelMeta.map_filter_fields_as_checkbox
            and field_name in self.model.BasemodelMeta.map_filter_fields_as_checkbox
          )
        ):
          complete_field_name_ordering = complete_field_name_naming = field_name
          # if it is a foreign key field...
          if (
            hasattr(self.model._meta.get_field(field_name), 'remote_field')
            and self.model._meta.get_field(field_name).remote_field is not None
          ):
            # identify suitable target model
            target_model = self.model._meta.get_field(field_name).remote_field.model
            # identify the suitable field in the target model for sorting
            foreign_field_name_ordering = target_model._meta.ordering[0]
            # identify the suitable field in the target model for display
            if target_model.BasemodelMeta.naming:
              foreign_field_name_naming = target_model.BasemodelMeta.naming
            else:
              foreign_field_name_naming = foreign_field_name_ordering
            complete_field_name_ordering = field_name + '__' + foreign_field_name_ordering
            complete_field_name_naming = field_name + '__' + foreign_field_name_naming
          # construct NOT NULL filter
          field_name_isnull = field_name + '__isnull'
          # sorted list of all unique values of the matching field obtained from the target model
          values_list = list(
            self.model.objects.exclude(**{field_name_isnull: True}).order_by(
              complete_field_name_ordering).values_list(
              complete_field_name_naming, flat=True).distinct())
          # if it is NOT a foreign key field...
          if field_name == complete_field_name_ordering:
            # separate values and get a sorted list of all unique individual values
            value_list = list([item for sublist in values_list for item in sublist])
            distinct_value_list = []
            for value_list_item in value_list:
              if value_list_item not in distinct_value_list:
                distinct_value_list.append(value_list_item)
            # convert decimal numbers in list to strings,
            # since decimal numbers cannot be serialized as JSON
            cleaned_distinct_value_list = []
            for distinct_value in distinct_value_list:
              cleaned_distinct_value_list.append(str(distinct_value)
                                                 if isinstance(distinct_value, Decimal)
                                                 else distinct_value)
            # insert list into declared dictionary
            checkbox_filter_lists[field_name] = cleaned_distinct_value_list
          # otherwise...
          else:
            # insert a sorted list of all unique individual values
            # directly into the declared dictionary
            checkbox_filter_lists[field_name] = values_list
    model_name = self.model.__name__
    model_name_lower = model_name.lower()
    context = super().get_context_data(**kwargs)
    # add user agent related elements to context
    context = add_user_agent_context_elements(context, self.request)
    # add basic model related elements to context
    context = add_basic_model_context_elements(context, self.model)
    # add further elements to context
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    if self.kwargs and 'subset_id' in self.kwargs and self.kwargs['subset_id']:
      subset_id = kwargs['subset_id']
      context['subset_id'] = subset_id
      context['objects_count'] = get_model_objects(self.model, subset_id, True)
      context['url_model_mapdata_subset'] = reverse(
        'datenmanagement:' + model_name + '_mapdata_subset', args=[subset_id])
    else:
      context['objects_count'] = get_model_objects(self.model, None, True)
    context['highlight_flag'] = self.model.BasemodelMeta.highlight_flag
    context['heavy_load_limit'] = self.model.BasemodelMeta.heavy_load_limit
    context['additional_wms_layers'] = self.model.BasemodelMeta.additional_wms_layers
    if (
        self.model.BasemodelMeta.editable
        and self.request.user.has_perm('datenmanagement.add_' + model_name_lower)
    ):
      context['url_model_add'] = reverse('datenmanagement:' + model_name + '_add')
    context['url_model_list'] = reverse('datenmanagement:' + model_name + '_list')
    context['url_model_list_subset_placeholder'] = reverse(
      'datenmanagement:' + model_name + '_list_subset', args=['worschdsupp'])
    context['url_model_mapdata'] = reverse('datenmanagement:' + model_name + '_mapdata')
    context['url_back'] = reverse('datenmanagement:' + model_name + '_start')
    # add map filter related elements to context
    if (
        self.model.BasemodelMeta.map_filter_fields
        or self.model.BasemodelMeta.map_intervalfilter_fields
    ):
      context['map_filters_enabled'] = True
    context['map_one_click_filters'] = self.model.BasemodelMeta.map_one_click_filters
    context['map_deadlinefilter_fields'] = self.model.BasemodelMeta.map_deadlinefilter_fields
    if self.model.BasemodelMeta.map_intervalfilter_fields:
      context['map_intervalfilter_fields'] = list(
        self.model.BasemodelMeta.map_intervalfilter_fields.keys())
      context['map_intervalfilter_fields_labels'] = list(
        self.model.BasemodelMeta.map_intervalfilter_fields.values())
    context['interval_filter_min'] = interval_filter_min
    context['interval_filter_max'] = interval_filter_max
    if self.model.BasemodelMeta.map_filter_fields:
      context['map_filter_fields'] = list(self.model.BasemodelMeta.map_filter_fields.keys())
      context['map_filter_fields_labels'] = list(
        self.model.BasemodelMeta.map_filter_fields.values())
    context['map_filter_fields_as_checkbox'] = (
      self.model.BasemodelMeta.map_filter_fields_as_checkbox)
    context['map_filter_fields_as_list'] = self.model.BasemodelMeta.map_filter_fields_as_list
    context['list_filter_lists'] = dumps(list_filter_lists)
    context['checkbox_filter_lists'] = dumps(checkbox_filter_lists)
    context['map_filter_boolean_fields_as_checkbox'] = (
      self.model.BasemodelMeta.map_filter_boolean_fields_as_checkbox)
    context['map_filter_hide_initial'] = self.model.BasemodelMeta.map_filter_hide_initial
    return context
