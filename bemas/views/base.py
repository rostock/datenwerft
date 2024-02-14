from datetime import date, datetime
from django.apps import apps
from django.db.models import ForeignKey
from django.urls import reverse
from django.utils.html import escape
from django_datatables_view.base_datatable_view import BaseDatatableView
from jsonview.views import JsonView

from .functions import create_geojson_feature, format_date_datetime, generate_foreign_key_link, \
  generate_foreign_key_link_simplified, get_model_objects
from toolbox.models import Subsets
from toolbox.utils import optimize_datatable_filter
from bemas.models import Codelist, Complaint, Contact, LogEntry, Organization, Originator, Person
from bemas.utils import LOG_ACTIONS, get_foreign_key_target_model, get_foreign_key_target_object, \
  get_icon_from_settings, is_bemas_admin, is_bemas_user


class GenericTableDataView(BaseDatatableView):
  """
  generic table data composition view
  """

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.columns = self.model._meta.fields
    super().__init__(*args, **kwargs)

  def get_initial_queryset(self):
    objects = None
    if self.kwargs and 'subset_pk' in self.kwargs and self.kwargs['subset_pk']:
      subset = Subsets.objects.get(pk=self.kwargs['subset_pk'])
      if (
          subset is not None
          and isinstance(subset, Subsets)
          and subset.model.model == self.model.__name__.lower()
      ):
        objects = self.model.objects.filter(pk__in=subset.pk_values)
    else:
      objects = get_model_objects(self.model, False, self.kwargs)
    return objects

  def prepare_results(self, qs):
    """
    loops passed queryset, creates cleaned-up JSON representation of the queryset and returns it

    :param qs: queryset
    :return: cleaned-up JSON representation of the queryset
    """
    json_data = []
    if (
        is_bemas_admin(self.request.user)
        or is_bemas_user(self.request.user)
        or self.request.user.is_superuser
    ):
      for item in qs:
        item_data = []
        item_pk = getattr(item, self.model._meta.pk.name)
        address_handled = False
        for column in self.columns:
          # handle included fields only!
          if column.name not in self.model.BasemodelMeta.table_exclusion_fields:
            data = None
            value = getattr(item, column.name)
            # codelist specific column "icon"
            if issubclass(self.model, Codelist) and column.name == 'icon':
              item_data.append('<i class="fas fa-{}"></i>'.format(value))
            # log entry specific column "model"
            elif issubclass(self.model, LogEntry) and column.name == 'model':
              # generate appropriate text (link in most cases)
              model = apps.get_app_config('bemas').get_model(value)
              model_name = model.__name__.lower()
              model_title = model._meta.verbose_name_plural
              icon = '<i class="fas fa-{}"></i>'.format(get_icon_from_settings(model_name))
              text = icon + ' ' + model_title
              if value != 'Contact':
                text = '<a href="' + reverse('bemas:' + model_name + '_table') + \
                       '" title="Tabelle anzeigen">' + text + '</a>'
              item_data.append(text)
            # log entry specific column "object_pk"
            elif issubclass(self.model, LogEntry) and column.name == 'object_pk':
              # generate appropriate link (if target object exists)
              model = apps.get_app_config('bemas').get_model(item.model)
              model_name = model.__name__.lower()
              text = str(value)
              if model.objects.filter(pk=value).exists():
                text = '<a href="' + reverse('bemas:' + model_name + '_update', args=[value]) + \
                       '" title="Objekt bearbeiten">' + text + '</a>'
              item_data.append(text)
            # log entry specific column "action"
            elif issubclass(self.model, LogEntry) and column.name == 'action':
              item_data.append(LOG_ACTIONS[value])
            # log entry specific column "content"
            elif issubclass(self.model, LogEntry) and column.name == 'content' and value:
              item_data.append('<em>' + value + '</em>')
            # foreign key columns
            elif issubclass(column.__class__, ForeignKey) and value:
              # foreign key to object class:
              # generate appropriate foreign key links
              if not issubclass(get_foreign_key_target_model(column), Codelist):
                item_data.append(generate_foreign_key_link(column, item))
              # foreign key to codelist and if codelist entry icon available:
              # add icon and foreign key text
              elif hasattr(get_foreign_key_target_model(column), 'icon'):
                foreign_key_target_object = get_foreign_key_target_object(item, column)
                icon = '<i class="fas fa-' + foreign_key_target_object.icon + '"></i> '
                item_data.append(icon + escape(value))
              # foreign key to codelist and if codelist entry icon is not available:
              # add foreign key text
              else:
                item_data.append(escape(value))
            # ordinary columns
            elif not column.name.startswith('address_'):
              if value is not None:
                # format dates and datetimes
                if isinstance(value, date) or isinstance(value, datetime):
                  data = format_date_datetime(value)
                # format lists
                elif type(value) is list:
                  data = '<br>'.join(value)
                else:
                  data = escape(value)
              item_data.append(data)
            # handle addresses
            elif column.name.startswith('address_') and not address_handled:
              # append address string once
              # instead of appending individual strings for all address related values
              data = self.model.objects.get(pk=item_pk).address()
              address_handled = True
              item_data.append(data)
        # object class organization:
        # add column which lists contact(s)
        if issubclass(self.model, Organization):
          data = ''
          contacts = Organization.objects.get(pk=item_pk).contact_set.all()
          if contacts:
            for index, contact in enumerate(contacts):
              data += '<br>' if index > 0 else ''
              data += generate_foreign_key_link_simplified(
                Contact, contact, contact.name_and_function()
              )
          item_data.append(data)
        # object class originator:
        # add column which lists operator(s)
        elif issubclass(self.model, Originator):
          data = ''
          operator_organization = getattr(item, 'operator_organization')
          if operator_organization:
            data = generate_foreign_key_link_simplified(Organization, operator_organization)
          operator_person = getattr(item, 'operator_person')
          if operator_person:
            data += '<br>' if operator_organization else ''
            data += generate_foreign_key_link_simplified(Person, operator_person)
          # designate anonymous complaint if necessary
          if not data:
            data = '<em><i class="fas fa-' + \
                   get_icon_from_settings('originator_without_operator') + \
                   '"></i> unbekannte Betreiberverhältnisse</em>'
          item_data.append(data)
        # object class complaint:
        # add column which lists complainer(s)
        elif issubclass(self.model, Complaint):
          data = ''
          complainers_organizations = Complaint.objects.get(
            pk=item_pk).complainers_organizations.all()
          if complainers_organizations:
            for index, organization in enumerate(complainers_organizations):
              data += '<br>' if index > 0 else ''
              data += generate_foreign_key_link_simplified(Organization, organization)
          complainers_persons = Complaint.objects.get(pk=item_pk).complainers_persons.all()
          if complainers_persons:
            for index, person in enumerate(complainers_persons):
              data += '<br>' if index > 0 or complainers_organizations else ''
              data += generate_foreign_key_link_simplified(Person, person)
          # designate anonymous complaint if necessary
          if not data:
            data = '<em><i class="fas fa-' + get_icon_from_settings('anonymous_complaint') + \
                   '"></i> anonyme Beschwerde</em>'
          item_data.append(data)
        # append links for updating, deleting, etc.
        if (
            (
                issubclass(self.model, Codelist)
                and (
                    is_bemas_admin(self.request.user)
                    or self.request.user.is_superuser
                )
            )
            or not issubclass(self.model, LogEntry)
        ):
          view_name_prefix = self.model.__name__.lower()
          if issubclass(self.model, Codelist):
            view_name_prefix = 'codelists_' + view_name_prefix
            title = 'Codelisteneintrag'
            log_entry_link = ''
          else:
            title = self.model._meta.verbose_name
            log_entry_link = '<a class="ms-2" href="' + reverse(
              'bemas:logentry_table_model_object', args=[self.model.__name__, item_pk])
            log_entry_link += '"><i class="fas fa-' + get_icon_from_settings('logentry') + \
                              '" title="Einträge im Bearbeitungsverlauf anzeigen"></i></a>'
          event_link = ''
          if issubclass(self.model, Complaint):
            event_link = '<a class="ms-2" href="' + reverse(
              'bemas:event_table_complaint', args=[item_pk])
            event_link += '"><i class="fas fa-' + get_icon_from_settings('event') + \
                          '" title="Journalereignisse anzeigen"></i></a>'
          map_link = ''
          if issubclass(self.model, Complaint) or issubclass(self.model, Originator):
            point = getattr(item, self.model.BasemodelMeta.geometry_field)
            map_link = '<a class="ms-2" href="' + reverse('bemas:map')
            map_link += '?center=' + str(point.x) + ',' + str(point.y) + '">'
            map_link += '<i class="fas fa-' + get_icon_from_settings('show_on_map') + \
                        '" title="' + title + ' auf Karte anzeigen"></i></a>'
          item_data.append(
            '<a href="' +
            reverse('bemas:' + view_name_prefix + '_update', args=[item_pk]) +
            '"><i class="fas fa-' + get_icon_from_settings('update') +
            '" title="' + title + ' bearbeiten"></i></a>' +
            '<a class="ms-2" href="' +
            reverse('bemas:' + view_name_prefix + '_delete', args=[item_pk]) +
            '"><i class="fas fa-' + get_icon_from_settings('delete') +
            '" title="' + title + ' löschen"></i></a>' +
            event_link +
            log_entry_link +
            map_link
          )
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
          search_column = column.name
          # take care of foreign key columns
          if issubclass(column.__class__, ForeignKey):
            # foreign key target model is codelist
            if issubclass(get_foreign_key_target_model(column), Codelist):
              search_column += '__title'
            # foreign key target model is object class
            else:
              search_column += '__search_content'
          qs_params_inner = optimize_datatable_filter(
            search_element, search_column, qs_params_inner)
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
      # the wrong order columns could be chosen
      address_handled = False
      for column in self.columns:
        # handle included fields only!
        if column.name not in self.model.BasemodelMeta.table_exclusion_fields:
          # ordinary columns
          if not column.name.startswith('address_'):
            column_names.append(column.name)
          # handle addresses
          elif column.name.startswith('address_') and not address_handled:
            # append one column for address string
            # instead of appending individual columns for all address related values
            column_names.append(column.name)
            address_handled = True
      column_name = column_names[int(order_column)]
      directory = '-' if order_dir is not None and order_dir == 'desc' else ''
      return qs.order_by(directory + column_name)


class GenericMapDataView(JsonView):
  """
  map data composition view

  :param model: model
  """

  model = None

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    super().__init__(*args, **kwargs)

  def get_context_data(self, **kwargs):
    """
    returns GeoJSON feature collection

    :param kwargs:
    :return: GeoJSON feature collection
    """
    feature_collection, objects = None, None
    if self.kwargs and 'subset_pk' in self.kwargs and self.kwargs['subset_pk']:
      subset = Subsets.objects.get(pk=self.kwargs['subset_pk'])
      if (
          subset is not None
          and isinstance(subset, Subsets)
          and subset.model.model == self.model.__name__.lower()
      ):
        objects = self.model.objects.filter(pk__in=subset.pk_values)
    else:
      objects = get_model_objects(self.model, False)
    # handle objects
    if objects:
      # declare empty GeoJSON feature collection
      feature_collection = {
          'type': 'FeatureCollection',
          'features': []
      }
      for curr_object in objects:
        # create GeoJSON feature
        feature = create_geojson_feature(curr_object)
        # add GeoJSON feature to GeoJSON feature collection
        feature_collection['features'].append(feature)
    return feature_collection
