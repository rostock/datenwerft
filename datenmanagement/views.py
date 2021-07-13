import json
import os
import re
import requests
import time
import uuid
from datetime import datetime
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, Permission, User
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.forms import CheckboxSelectMultiple, ChoiceField, ModelForm, UUIDField, ValidationError
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse
from django.utils.html import escape
from django.views import generic
from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.core import ObjectPermissionChecker
from leaflet.forms.widgets import LeafletWidget
from operator import attrgetter
from tempus_dominus.widgets import DatePicker



#
# eigene Funktionen
#

def assign_widgets(field, widget = None):
  if field.name == 'geometrie':
    return field.formfield(widget = LeafletWidget())
  elif field.__class__.__name__ == 'DateField':
    return field.formfield(widget = DatePicker(attrs = {
     'input_toggle': False,
     'append': 'fa fa-calendar'
    }))
  elif field.__class__.__name__ == 'DateTimeField':
    return field.formfield(widget = DateTimePicker(attrs = {
     'input_toggle': False,
     'append': 'fa fa-clock'
    }))
  elif field.__class__.__name__ == 'ChoiceArrayField':
    return field.formfield(empty_value = None, widget = CheckboxSelectMultiple())
  else:
    return field.formfield()


def delete_object_immediately(request, pk):
  model_name = re.sub('^.*\/', '', re.sub('\/deleteimmediately.*$', '', request.path_info))
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  obj = get_object_or_404(model, pk=pk)
  if ObjectPermissionChecker(request.user).has_perm('delete_' + model_name.lower(), obj):
    obj.delete()
  else:
    raise PermissionDenied()
  return HttpResponse(status = 204)


def get_thumb_url(url):
  head, tail = os.path.split(url)
  return head + '/thumbs/' + tail


def is_valid_uuid(value):
  try:
    uuid.UUID(str(value))
    return True
  except ValueError:
    return False



#
# eigene Felder
#

class AddressUUIDField(UUIDField):
  def to_python(self, value):
    if value in self.empty_values:
      return None
    adressen = apps.get_app_config('datenmanagement').get_model('Adressen')
    return adressen.objects.get(pk=value)


class StreetUUIDField(UUIDField):
  def to_python(self, value):
    if value in self.empty_values:
      return None
    strassen = apps.get_app_config('datenmanagement').get_model('Strassen')
    return strassen.objects.get(pk=value)



#
# eigene Views
#

class OWSProxyView(generic.View):
  http_method_names = ['get',]
  
  def dispatch(self, request, *args, **kwargs):
    self.destination_url = settings.OWS_BASE + re.sub('^.*owsproxy', '', str(request.get_full_path))
    return super(OWSProxyView, self).dispatch(request, *args, **kwargs)

  def get(self, request, *args, **kwargs):
    response = requests.get(self.destination_url, timeout = 60)
    return HttpResponse(response, content_type = response.headers['content-type'])


class AddressSearchView(generic.View):
  http_method_names = ['get',]
  
  def dispatch(self, request, *args, **kwargs):
    self.addresssearch_type = 'search'
    self.addresssearch_class = 'address_hro'
    self.addresssearch_query = request.GET.get('query', '')
    self.addresssearch_out_epsg = '4326'
    self.addresssearch_shape = 'bbox'
    self.addresssearch_limit = '5'
    return super(AddressSearchView, self).dispatch(request, *args, **kwargs)

  def get(self, request, *args, **kwargs):
    response = requests.get(settings.ADDRESS_SEARCH_URL + 'key=' + settings.ADDRESS_SEARCH_KEY + '&type=' + self.addresssearch_type + '&class=' + self.addresssearch_class + '&query=' + self.addresssearch_query + '&out_epsg=' + self.addresssearch_out_epsg + '&shape=' + self.addresssearch_shape + '&limit=' + self.addresssearch_limit, timeout = 3)
    return HttpResponse(response, content_type = 'application/json')


class ReverseSearchView(generic.View):
  http_method_names = ['get',]
  
  def dispatch(self, request, *args, **kwargs):
    self.reversesearch_type = 'reverse'
    self.reversesearch_class = 'address'
    self.reversesearch_x = request.GET.get('x', '')
    self.reversesearch_y = request.GET.get('y', '')
    self.reversesearch_in_epsg = '4326'
    self.reversesearch_radius = '200'
    return super(ReverseSearchView, self).dispatch(request, *args, **kwargs)

  def get(self, request, *args, **kwargs):
    response = requests.get(settings.ADDRESS_SEARCH_URL + 'key=' + settings.ADDRESS_SEARCH_KEY + '&type=' + self.reversesearch_type + '&class=' + self.reversesearch_class + '&query=' + self.reversesearch_x + ',' + self.reversesearch_y + '&in_epsg=' + self.reversesearch_in_epsg + '&radius=' + self.reversesearch_radius, timeout = 3)
    return HttpResponse(response, content_type = 'application/json')


class DataForm(ModelForm):
  required_css_class = 'required'
  
  def __init__(self, *args, **kwargs):
    associated_objects = kwargs.pop('associated_objects', None)
    associated_new = kwargs.pop('associated_new', None)
    fields_with_foreign_key_to_linkify = kwargs.pop('fields_with_foreign_key_to_linkify', None)
    choices_models_for_choices_fields = kwargs.pop('choices_models_for_choices_fields', None)
    group_with_users_for_choice_field = kwargs.pop('group_with_users_for_choice_field', None)
    admin_group = kwargs.pop('admin_group', None)
    multi_foto_field = kwargs.pop('multi_foto_field', None)
    multi_files = kwargs.pop('multi_files', None)
    file = kwargs.pop('file', None)
    model = kwargs.pop('model', None)
    request = kwargs.pop('request', None)
    kwargs.setdefault('label_suffix', '')
    super(DataForm, self).__init__(*args, **kwargs)
    self.associated_objects = associated_objects
    self.associated_new = associated_new
    self.fields_with_foreign_key_to_linkify = fields_with_foreign_key_to_linkify
    self.choices_models_for_choices_fields = choices_models_for_choices_fields
    self.group_with_users_for_choice_field = group_with_users_for_choice_field
    self.admin_group = admin_group
    self.multi_foto_field = multi_foto_field
    self.multi_files = multi_files
    self.file = file
    self.model = model
    self.request = request
    self.address_type = (self.instance._meta.address_type if hasattr(self.instance._meta, 'address_type') else None)
    self.address_mandatory = (self.instance._meta.address_mandatory if hasattr(self.instance._meta, 'address_mandatory') else None)

    for field in self.model._meta.get_fields(): 
      if field.name == 'ansprechpartner' or field.name == 'bearbeiter':
        # Textfelder in Auswahllisten umwandeln, falls Benutzer kein Admin und kein Mitglied der Gruppe von Benutzern ist, die als Admin-Gruppe für dieses Datenthema gilt
        if self.group_with_users_for_choice_field and Group.objects.filter(name = self.group_with_users_for_choice_field).exists() and not (self.request.user.is_superuser or self.request.user.groups.filter(name = self.admin_group).exists()):
          users = sorted(User.objects.filter(groups__name = self.group_with_users_for_choice_field), key=attrgetter('last_name', 'first_name'))
          choice_field = ChoiceField(
            choices = [(user.first_name + ' ' + user.last_name + ' (' + user.email.lower() + ')', user.first_name + ' ' + user.last_name + ' (' + user.email.lower() + ')') for user in users],
            initial = request.user.first_name + ' ' + request.user.last_name + ' (' + request.user.email.lower() + ')'
          )
          if field.name == 'ansprechpartner':
            self.fields[field.name] = choice_field
          if field.name == 'bearbeiter':
            self.fields[field.name] = choice_field
      # Adressfelder in eigenen Feldtypen umwandeln
      elif field.name == 'adresse' or field.name == 'strasse':
        if field.name == 'adresse':
          self.fields[field.name] = AddressUUIDField(
            label = field.verbose_name,
            required = self.address_mandatory
          )
        elif field.name == 'strasse':
          self.fields[field.name] = StreetUUIDField(
            label = field.verbose_name,
            required = self.address_mandatory
          )
      # bestimmte Modelle für bestimmte Felder zur Befüllung entsprechender Auswahllisten heranziehen
      elif self.choices_models_for_choices_fields:
        choices_model_for_choices_field = self.choices_models_for_choices_fields.get(field.name)
        if choices_model_for_choices_field is not None:
          choices_model = apps.get_app_config('datenmanagement').get_model(choices_model_for_choices_field)
          choices = []
          for choices_model_object in choices_model.objects.all():
            choices.append((choices_model_object, choices_model_object))
          self.fields[field.name].choices = choices

    for field in self.fields.values():
      if field.label == 'Geometrie':
        required_message = 'Es muss ein Marker in der Karte gesetzt werden bzw. eine Linie oder Fläche gezeichnet werden, falls es sich um Daten linien- oder flächenhafter Repräsentation handelt!'
      else:
        required_message = 'Das Attribut <strong><em>{label}</em></strong> ist Pflicht!'.format(label = field.label)
      invalid_image_message = 'Sie müssen eine valide Bilddatei hochladen!'
      unique_message = 'Es existiert bereits ein Datensatz mit dem angegebenen Wert im Attribut <strong><em>{label}</em></strong>!'.format(label = field.label)
      field.error_messages = { 'required': required_message, 'invalid_image': invalid_image_message, 'unique': unique_message }

  # Hinweis: Diese Methode wird durch Django ignoriert, falls kein Feld mit Namen foto existiert.
  def clean_foto(self):
    if self.multi_foto_field and self.multi_foto_field == True:
      # alle weiteren Operationen nur durchführen, wenn auch wirklich alle Pflichtfelder gefüllt sind – ansonsten klappt die Übernahme für die weiteren Foto-Datensätze nämlich nicht!
      ok = True
      for field in self.model._meta.get_fields():
        if field.name != self.model._meta.pk.name and field.name != 'foto' and self.fields[field.name].required == True and not self.data[field.name]:
          ok = False
          break
      if ok == True:
        fotos_count = len(self.multi_files.getlist('foto'))
        if fotos_count > 1:
          i = 1
          for foto in self.multi_files.getlist('foto'):
            if i < fotos_count:
              m = self.model()
              for field in self.model._meta.get_fields():
                if field.name == 'dateiname_original':
                  setattr(m, field.name, foto.name)
                elif field.name == 'foto':
                  setattr(m, field.name, foto)
                elif field.name != m._meta.pk.name:
                  setattr(m, field.name, self.cleaned_data[field.name])
              m.save()
              i += 1
    # Hinweis: Das return-Statement passt in jedem Fall, das heißt bei normalem Dateifeld und bei Multi-Dateifeld, da hier immer die – in alphabetischer Reihenfolge des Dateinamens – letzte Datei behandelt wird.
    return self.cleaned_data['foto']

  # Hinweis: Diese Methode wird durch Django ignoriert, falls kein Feld mit Namen dateiname_original existiert.
  def clean_dateiname_original(self):
    data = self.cleaned_data['dateiname_original']
    if self.multi_foto_field and self.multi_foto_field == True:
      if self.multi_files:
        data = self.multi_files.getlist('foto')[len(self.multi_files.getlist('foto')) - 1].name
    else:
      if self.file:
        data = self.file.getlist('foto')[0].name
    return data

  # Hinweis: Diese Methode wird durch Django ignoriert, falls kein Feld mit Namen geometrie existiert.
  def clean_geometrie(self):
    data = self.cleaned_data['geometrie']
    error_text = 'Es muss ein Marker in der Karte gesetzt werden bzw. eine Linie oder Fläche gezeichnet werden, falls es sich um Daten linien- oder flächenhafter Repräsentation handelt!'
    if '-' in str(data):
      raise ValidationError(error_text)
    return data


class IndexView(generic.ListView):
  template_name = 'datenmanagement/index.html'

  def get_queryset(self):
    model_list = []
    app_models = apps.get_app_config('datenmanagement').get_models()
    for model in app_models:
      model_list.append(model)
    return model_list


class StartView(generic.ListView):
  def __init__(self, model = None, template_name = None):
    self.model = model
    self.template_name = template_name
    super(StartView, self).__init__()

  def get_context_data(self, **kwargs):
    context = super(StartView, self).get_context_data(**kwargs)
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model._meta.description
    context['geometry_type'] = (self.model._meta.geometry_type if hasattr(self.model._meta, 'geometry_type') else None)
    context['additional_wms_layers'] = (self.model._meta.additional_wms_layers if hasattr(self.model._meta, 'additional_wms_layers') else None)
    return context


class DataView(BaseDatatableView):
  def __init__(self, model = None):
    self.model = model
    self.model_name = self.model.__name__
    self.model_name_lower = self.model.__name__.lower()
    self.columns = self.model._meta.list_fields
    self.columns_with_foreign_key_to_linkify = (self.model._meta.fields_with_foreign_key_to_linkify if hasattr(self.model._meta, 'fields_with_foreign_key_to_linkify') else None)
    self.columns_with_foreign_key = (self.model._meta.list_fields_with_foreign_key if hasattr(self.model._meta, 'list_fields_with_foreign_key') else None)
    self.columns_with_number = (self.model._meta.list_fields_with_number if hasattr(self.model._meta, 'list_fields_with_number') else None)
    self.columns_with_date = (self.model._meta.list_fields_with_date if hasattr(self.model._meta, 'list_fields_with_date') else None)
    self.column_as_highlight_flag = (self.model._meta.highlight_flag if hasattr(self.model._meta, 'highlight_flag') else None)
    self.thumbs = (self.model._meta.thumbs if hasattr(self.model._meta, 'thumbs') else None)
    super(DataView, self).__init__()

  def prepare_results(self, qs):
    json_data = []
    for item in qs:
      item_data = []
      item_id = getattr(item, self.model._meta.pk.name)
      checker = ObjectPermissionChecker(self.request.user)
      obj = self.model.objects.get(pk=item_id)
      if checker.has_perm('delete_' + self.model_name_lower, obj):
        item_data.append('<input class="action-checkbox" type="checkbox" value="' + str(item_id) + '">')
      else:
        item_data.append('')
      for column in self.columns:
        data = None
        value = getattr(item, column)
        if value is not None and self.columns_with_foreign_key is not None and column in self.columns_with_foreign_key and self.columns_with_foreign_key_to_linkify is not None and column in self.columns_with_foreign_key_to_linkify:
          foreign_model = value._meta.label
          foreign_model_primary_key = value._meta.pk.name
          foreign_model_title = self.columns.get(column)
          foreign_model_attribute_for_text = self.columns_with_foreign_key.get(column)
          data = '<a href="' + reverse('datenmanagement:' + foreign_model.replace(value._meta.app_label + '.', '') + 'change', args=[getattr(value, foreign_model_primary_key)]) + '" target="_blank" class="required" title="' + foreign_model_title + ' ansehen oder bearbeiten">' + str(getattr(value, foreign_model_attribute_for_text)) + '</a>'
        elif value is not None and self.columns_with_number is not None and column in self.columns_with_number:
          data = value
        elif value is not None and self.columns_with_date is not None and column in self.columns_with_date:
          data = datetime.strptime(str(value), '%Y-%m-%d').strftime('%d.%m.%Y')
        elif value is not None and value == True and self.column_as_highlight_flag is not None and column == self.column_as_highlight_flag:
          data = '<i class="fas fa-exclamation-triangle text-danger" title="Konflikt(e) vorhanden!"></i>'
        elif value is not None and column == 'foto':
          try:
            data = '<a href="' + value.url + '?' + str(time.time()) + '" target="_blank" title="große Ansicht öffnen…">'
            if self.thumbs is not None and self.thumbs == True:
              data += '<img src="' + get_thumb_url(value.url) + '?' + str(time.time()) + '" alt="Vorschau" />'
            else:
              data += '<img src="' + value.url + '?' + str(time.time()) + '" alt="Vorschau" width="70px" />'
            data += '</a>'
          except ValueError:
            pass
        elif value is not None and (column == 'dokument' or column == 'pdf'):
          try:
            data = '<a href="' + value.url + '?' + str(time.time()) + '" target="_blank" title="PDF öffnen…">PDF</a>'
          except ValueError:
            pass
        elif value is not None and value == True:
          data = 'ja'
        elif value is not None and value == False:
          data = 'nein'
        elif value is not None and type(value) in [list, tuple]:
          data = ', '.join(map(str, value)) 
        elif value is not None:
          data = escape(value)
        item_data.append(data)
      if checker.has_perm('change_' + self.model_name_lower, obj):
        item_data.append('<a href="' + reverse('datenmanagement:' + self.model_name + 'change', args=[item_id]) + '"><i class="fas fa-edit" title="Datensatz bearbeiten"></i></a>')
      elif self.request.user.has_perm('datenmanagement.view_' + self.model_name_lower):
        item_data.append('<a href="' + reverse('datenmanagement:' + self.model_name + 'change', args=[item_id]) + '"><i class="fas fa-eye" title="Datensatz ansehen"></i></a>')
      else:
        item_data.append('')
      if checker.has_perm('delete_' + self.model_name_lower, obj):
        item_data.append('<a href="' + reverse('datenmanagement:' + self.model_name + 'delete', args=[item_id]) + '"><i class="fas fa-trash" title="Datensatz löschen"></i></a>')
      else:
        item_data.append('')
      json_data.append(item_data)
    return json_data

  def filter_queryset(self, qs):
    search = self.request.GET.get('search[value]', None)
    if search:
      qs_params = None
      for column in self.columns:
        if self.columns_with_foreign_key:
          column_with_foreign_key = self.columns_with_foreign_key.get(column)
          if column_with_foreign_key is not None:
            column = column + str('__') + column_with_foreign_key
        kwargs = {
          '{0}__{1}'.format(column, 'icontains'): search
        }
        q = Q(**kwargs)
        lower_search = search.lower()
        m = re.search('^[0-9]{2}\.[0-9]{4}$', lower_search)
        n = re.search('^[0-9]{2}\.[0-9]{2}$', lower_search)
        if m:
          kwargs = {
            '{0}__{1}'.format(column, 'icontains'): re.sub('^[0-9]{2}\.', '', m.group(0)) + '-' + re.sub('\.[0-9]{4}$', '', m.group(0))
          }
          q = q|Q(**kwargs)
        elif n:
          kwargs = {
            '{0}__{1}'.format(column, 'icontains'): re.sub('^[0-9]{2}\.', '', n.group(0)) + '-' + re.sub('\.[0-9]{2}$', '', n.group(0))
          }
          q = q|Q(**kwargs)
        elif lower_search == 'ja':
          kwargs = {
            '{0}__{1}'.format(column, 'icontains'): 'true'
          }
          q = q|Q(**kwargs)
        elif lower_search == 'nein' or lower_search == 'nei':
          kwargs = {
            '{0}__{1}'.format(column, 'icontains'): 'false'
          }
          q = q|Q(**kwargs)
        qs_params = qs_params | q if qs_params else q
      qs = qs.filter(qs_params)
    return qs

  def ordering(self, qs):
    order_column = self.request.GET.get('order[0][column]', None)
    order_dir = self.request.GET.get('order[0][dir]', None)
    columns = list(self.columns.keys())
    column = str(columns[int(order_column) - 1])
    dir = '-' if order_dir is not None and order_dir == 'desc' else ''
    if order_column is not None:
      return qs.order_by(dir + column)
    else:
      return qs


class DataListView(generic.ListView):
  def __init__(self, model = None, template_name = None, success_url = None):
    self.model = model
    self.template_name = template_name
    super(DataListView, self).__init__()

  def get_context_data(self, **kwargs):
    context = super(DataListView, self).get_context_data(**kwargs)
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model._meta.description
    context['list_fields_labels'] = list(self.model._meta.list_fields.values())
    context['geometry_type'] = (self.model._meta.geometry_type if hasattr(self.model._meta, 'geometry_type') else None)
    context['thumbs'] = (self.model._meta.thumbs if hasattr(self.model._meta, 'thumbs') else None)
    return context


class DataMapView(generic.ListView):
  def __init__(self, model = None, template_name = None, success_url = None):
    self.model = model
    self.template_name = template_name
    super(DataMapView, self).__init__()

  def get_context_data(self, **kwargs):
    context = super(DataMapView, self).get_context_data(**kwargs)
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model._meta.description
    context['highlight_flag'] = (self.model._meta.highlight_flag if hasattr(self.model._meta, 'highlight_flag') else None)
    context['map_feature_tooltip_field'] = (self.model._meta.map_feature_tooltip_field if hasattr(self.model._meta, 'map_feature_tooltip_field') else None)
    context['map_feature_tooltip_fields'] = (self.model._meta.map_feature_tooltip_fields if hasattr(self.model._meta, 'map_feature_tooltip_fields') else None)
    context['map_filters_enabled'] = (True if hasattr(self.model._meta, 'map_filter_fields') or hasattr(self.model._meta, 'map_rangefilter_fields') else None)
    context['map_rangefilter_fields'] = (list(self.model._meta.map_rangefilter_fields.keys()) if hasattr(self.model._meta, 'map_rangefilter_fields') else None)
    context['map_rangefilter_fields_json'] = (json.dumps(list(self.model._meta.map_rangefilter_fields.keys())) if hasattr(self.model._meta, 'map_rangefilter_fields') else None)
    context['map_rangefilter_fields_labels'] = (list(self.model._meta.map_rangefilter_fields.values()) if hasattr(self.model._meta, 'map_rangefilter_fields') else None)
    context['map_filter_fields'] = (list(self.model._meta.map_filter_fields.keys()) if hasattr(self.model._meta, 'map_filter_fields') else None)
    context['map_filter_fields_json'] = (json.dumps(list(self.model._meta.map_filter_fields.keys())) if hasattr(self.model._meta, 'map_filter_fields') else None)
    context['map_filter_fields_labels'] = (list(self.model._meta.map_filter_fields.values()) if hasattr(self.model._meta, 'map_filter_fields') else None)
    context['map_filter_fields_as_list'] = (self.model._meta.map_filter_fields_as_list if hasattr(self.model._meta, 'map_filter_fields_as_list') else None)
    context['map_filter_boolean_fields_as_checkbox'] = (self.model._meta.map_filter_boolean_fields_as_checkbox if hasattr(self.model._meta, 'map_filter_boolean_fields_as_checkbox') else None)
    context['map_filter_field_hide_initial'] = (next(iter(self.model._meta.map_filter_hide_initial.keys())) if hasattr(self.model._meta, 'map_filter_hide_initial') and len(self.model._meta.map_filter_hide_initial) == 1 else None)
    context['map_filter_value_hide_initial'] = (next(iter(self.model._meta.map_filter_hide_initial.values())) if hasattr(self.model._meta, 'map_filter_hide_initial') and len(self.model._meta.map_filter_hide_initial) == 1 else None)
    context['additional_wms_layers'] = (self.model._meta.additional_wms_layers if hasattr(self.model._meta, 'additional_wms_layers') else None)
    context['geometry_type'] = (self.model._meta.geometry_type if hasattr(self.model._meta, 'geometry_type') else None)
    return context


class DataAddView(generic.CreateView):
  def get_form_kwargs(self):
    kwargs = super(DataAddView, self).get_form_kwargs()
    self.fields_with_foreign_key_to_linkify = (self.model._meta.fields_with_foreign_key_to_linkify if hasattr(self.model._meta, 'fields_with_foreign_key_to_linkify') else None)
    self.choices_models_for_choices_fields = (self.model._meta.choices_models_for_choices_fields if hasattr(self.model._meta, 'choices_models_for_choices_fields') else None)
    self.group_with_users_for_choice_field = (self.model._meta.group_with_users_for_choice_field if hasattr(self.model._meta, 'group_with_users_for_choice_field') else None)
    self.admin_group = (self.model._meta.admin_group if hasattr(self.model._meta, 'admin_group') else None)
    self.multi_foto_field = (self.model._meta.multi_foto_field if hasattr(self.model._meta, 'multi_foto_field') else None)
    self.multi_files = (self.request.FILES if hasattr(self.model._meta, 'multi_foto_field') and self.request.method == 'POST' else None)
    self.file = (self.request.FILES if self.request.method == 'POST' else None)
    kwargs['fields_with_foreign_key_to_linkify'] = self.fields_with_foreign_key_to_linkify
    kwargs['choices_models_for_choices_fields'] = self.choices_models_for_choices_fields
    kwargs['group_with_users_for_choice_field'] = self.group_with_users_for_choice_field
    kwargs['admin_group'] = self.admin_group
    kwargs['multi_foto_field'] = self.multi_foto_field
    kwargs['multi_files'] = self.multi_files
    kwargs['file'] = self.file
    kwargs['model'] = self.model
    kwargs['request'] = self.request
    return kwargs
    
  def __init__(self, model = None, template_name = None, success_url = None):
    self.model = model
    self.template_name = template_name
    self.success_url = success_url
    self.form_class = modelform_factory(self.model, form = DataForm, fields = '__all__', formfield_callback = assign_widgets)
    super(DataAddView, self).__init__()

  def get_context_data(self, **kwargs):
    context = super(DataAddView, self).get_context_data(**kwargs)
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model._meta.description
    context['fields_with_foreign_key_to_linkify'] = (self.model._meta.fields_with_foreign_key_to_linkify if hasattr(self.model._meta, 'fields_with_foreign_key_to_linkify') else None)
    context['choices_models_for_choices_fields'] = (self.model._meta.choices_models_for_choices_fields if hasattr(self.model._meta, 'choices_models_for_choices_fields') else None)
    context['address_type'] = (self.model._meta.address_type if hasattr(self.model._meta, 'address_type') else None)
    context['address_mandatory'] = (self.model._meta.address_mandatory if hasattr(self.model._meta, 'address_mandatory') else None)
    context['geometry_type'] = (self.model._meta.geometry_type if hasattr(self.model._meta, 'geometry_type') else None)
    context['readonly_fields'] = (self.model._meta.readonly_fields if hasattr(self.model._meta, 'readonly_fields') else None)
    context['multi_foto_field'] = (self.model._meta.multi_foto_field if hasattr(self.model._meta, 'multi_foto_field') else None)
    context['group_with_users_for_choice_field'] = (self.model._meta.group_with_users_for_choice_field if hasattr(self.model._meta, 'group_with_users_for_choice_field') else None)
    context['admin_group'] = (self.model._meta.admin_group if hasattr(self.model._meta, 'admin_group') else None)
    context['additional_wms_layers'] = (self.model._meta.additional_wms_layers if hasattr(self.model._meta, 'additional_wms_layers') else None)
    return context

  def get_initial(self):
    ansprechpartner = None
    bearbeiter = None
    preselect_field = self.request.GET.get('preselect_field', 'foobar')
    preselect_value = self.request.GET.get('preselect_value', '')
    for field in self.model._meta.get_fields():
      if field.name == 'ansprechpartner':
        ansprechpartner = (self.request.user.first_name + ' ' + self.request.user.last_name if self.request.user.first_name and self.request.user.last_name else self.request.user.username) + ' (' + self.request.user.email.lower() + ')'
      if field.name == 'bearbeiter':
        bearbeiter = self.request.user.first_name + ' ' + self.request.user.last_name if self.request.user.first_name and self.request.user.last_name else self.request.user.username
    if ansprechpartner or bearbeiter or (preselect_field and preselect_value):
      if self.request.user.is_superuser or (hasattr(self.model._meta, 'admin_group') and self.request.user.groups.filter(name = self.model._meta.admin_group).exists()) or not hasattr(self.model._meta, 'group_with_users_for_choice_field') or not hasattr(self.model._meta, 'admin_group'):
        return {
          'ansprechpartner': ansprechpartner,
          'bearbeiter': bearbeiter,
          preselect_field: preselect_value
        }

  def form_valid(self, form):
    return super(DataAddView, self).form_valid(form)


class DataChangeView(generic.UpdateView):
  def get_form_kwargs(self):
    kwargs = super(DataChangeView, self).get_form_kwargs()
    self.associated_objects = None
    self.associated_new = None
    self.associated_models = (self.model._meta.associated_models if hasattr(self.model._meta, 'associated_models') else None)
    self.fields_with_foreign_key_to_linkify = (self.model._meta.fields_with_foreign_key_to_linkify if hasattr(self.model._meta, 'fields_with_foreign_key_to_linkify') else None)
    self.choices_models_for_choices_fields = (self.model._meta.choices_models_for_choices_fields if hasattr(self.model._meta, 'choices_models_for_choices_fields') else None)
    self.group_with_users_for_choice_field = (self.model._meta.group_with_users_for_choice_field if hasattr(self.model._meta, 'group_with_users_for_choice_field') else None)
    self.admin_group = (self.model._meta.admin_group if hasattr(self.model._meta, 'admin_group') else None)
    self.file = (self.request.FILES if self.request.method == 'POST' else None)
    kwargs['associated_objects'] = self.associated_objects
    kwargs['associated_new'] = self.associated_new
    kwargs['fields_with_foreign_key_to_linkify'] = self.fields_with_foreign_key_to_linkify
    kwargs['choices_models_for_choices_fields'] = self.choices_models_for_choices_fields
    kwargs['group_with_users_for_choice_field'] = self.group_with_users_for_choice_field
    kwargs['admin_group'] = self.admin_group
    kwargs['file'] = self.file
    kwargs['model'] = self.model
    kwargs['request'] = self.request

    # assoziierte Modelle für die Bereitstellung entsprechender Links heranziehen
    if self.associated_models:
      self.associated_new = []
      self.associated_objects = []
      for associated_model in self.associated_models:
        associated_model_model = apps.get_app_config('datenmanagement').get_model(associated_model)
        associated_model_foreign_key_field = self.associated_models.get(associated_model)
        title = (re.sub('^.* ', '', associated_model_model._meta.object_title) + ' zu ' + associated_model_model._meta.foreign_key_label if hasattr(associated_model_model._meta, 'object_title') and hasattr(associated_model_model._meta, 'foreign_key_label') else associated_model_model._meta.verbose_name)
        associated_new_dict = {
          'title': title,
          'link': reverse('datenmanagement:' + associated_model + 'add') + '?preselect_field=' + associated_model_foreign_key_field + '&preselect_value=' + str(self.object.pk)
        }
        self.associated_new.append(associated_new_dict)
        filter = {}
        filter[associated_model_foreign_key_field] = self.object.pk
        for associated_object in associated_model_model.objects.filter(**filter):
          foto = (associated_object.foto if hasattr(associated_object, 'foto') else None)
          thumbs = (associated_model_model._meta.thumbs if foto and hasattr(associated_model_model._meta, 'thumbs') else None)
          preview_img_url = ''
          preview_thumb_url = ''
          if foto:
            try:
              preview_img_url = foto.url + '?' + str(time.time())
              if thumbs is not None and thumbs == True:
                preview_thumb_url = get_thumb_url(foto.url) + '?' + str(time.time())
              else:
                preview_thumb_url = ''
            except ValueError:
              pass
          associated_object_dict = {
            'title': title,
            'name': str(associated_object),
            'id': associated_object.pk,
            'link': reverse('datenmanagement:' + associated_model + 'change', args=[associated_object.pk]),
            'preview_img_url': preview_img_url,
            'preview_thumb_url': preview_thumb_url
          }
          self.associated_objects.append(associated_object_dict)
      kwargs['associated_objects'] = self.associated_objects
      kwargs['associated_new'] = self.associated_new

    return kwargs

  def __init__(self, model = None, template_name = None, success_url = None):
    self.model = model
    self.template_name = template_name
    self.success_url = success_url
    self.form_class = modelform_factory(self.model, form = DataForm, fields = '__all__', formfield_callback = assign_widgets)
    super(DataChangeView, self).__init__()

  def get_context_data(self, **kwargs):
    context = super(DataChangeView, self).get_context_data(**kwargs)
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model._meta.description
    context['associated_objects'] = (self.associated_objects if self.associated_objects else None)
    context['associated_new'] = (self.associated_new if self.associated_new else None)
    context['fields_with_foreign_key_to_linkify'] = (self.model._meta.fields_with_foreign_key_to_linkify if hasattr(self.model._meta, 'fields_with_foreign_key_to_linkify') else None)
    context['choices_models_for_choices_fields'] = (self.model._meta.choices_models_for_choices_fields if hasattr(self.model._meta, 'choices_models_for_choices_fields') else None)
    context['address_type'] = (self.model._meta.address_type if hasattr(self.model._meta, 'address_type') else None)
    context['address_mandatory'] = (self.model._meta.address_mandatory if hasattr(self.model._meta, 'address_mandatory') else None)
    context['geometry_type'] = (self.model._meta.geometry_type if hasattr(self.model._meta, 'geometry_type') else None)
    context['readonly_fields'] = (self.model._meta.readonly_fields if hasattr(self.model._meta, 'readonly_fields') else None)
    context['group_with_users_for_choice_field'] = (self.model._meta.group_with_users_for_choice_field if hasattr(self.model._meta, 'group_with_users_for_choice_field') else None)
    context['admin_group'] = (self.model._meta.admin_group if hasattr(self.model._meta, 'admin_group') else None)
    context['current_address'] = (self.object.adresse.pk if hasattr(self.model._meta, 'address_type') and self.model._meta.address_type == 'Adresse' and self.object.adresse else None)
    context['current_street'] = (self.object.strasse.pk if hasattr(self.model._meta, 'address_type') and self.model._meta.address_type == 'Straße' and self.object.strasse else None)
    context['additional_wms_layers'] = (self.model._meta.additional_wms_layers if hasattr(self.model._meta, 'additional_wms_layers') else None)
    return context

  def get_initial(self):
    if hasattr(self.model._meta, 'address_type'):
      if self.model._meta.address_type == 'Adresse' and self.object.adresse:
        return {
          'adresse': self.object.adresse
        }
      elif self.model._meta.address_type == 'Straße' and self.object.strasse:
        return {
          'strasse': self.object.strasse
        }
      else:
        return {
        }
    else:
      return {
      }

  def form_valid(self, form):
    return super(DataChangeView, self).form_valid(form)
    
  def get_object(self, *args, **kwargs):
    obj = super(DataChangeView, self).get_object(*args, **kwargs)
    userobjperm_change = ObjectPermissionChecker(self.request.user).has_perm('change_' + self.model.__name__.lower(), obj)
    userperm_view = self.request.user.has_perm('datenmanagement.view_' + self.model.__name__.lower())
    if not userobjperm_change and not userperm_view:
      raise PermissionDenied()
    return obj


class DataDeleteView(generic.DeleteView):
  def get_object(self, *args, **kwargs):
    obj = super(DataDeleteView, self).get_object(*args, **kwargs)
    userobjperm_delete = ObjectPermissionChecker(self.request.user).has_perm('delete_' + self.model.__name__.lower(), obj)
    if not userobjperm_delete:
      raise PermissionDenied()
    return obj
