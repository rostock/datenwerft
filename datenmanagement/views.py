import os
import re
import requests
from datetime import datetime
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core import serializers
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.forms import ModelForm, ValidationError
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template import loader
from django.urls import reverse
from django.utils.html import escape
from django.views import generic
from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.core import ObjectPermissionChecker
from guardian.shortcuts import assign_perm
from leaflet.forms.widgets import LeafletWidget
from operator import itemgetter
from tempus_dominus.widgets import DatePicker



def assign_widgets(field, widget = None):
  if field.name == 'geometrie':
    return field.formfield(widget = LeafletWidget())
  elif field.__class__.__name__ == 'DateField':
    return field.formfield(widget = DatePicker())
  else:
    return field.formfield()


def delete_object_immediately(request, pk):
  model_name = re.sub('^.*\/', '', re.sub('\/deleteimmediately.*$', '', request.path_info))
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  obj = get_object_or_404(model, pk = pk)
  if ObjectPermissionChecker(request.user).has_perm('delete_' + model_name.lower(), obj):
    obj.delete()
  else:
    raise PermissionDenied()
  return HttpResponse(status = 204)


def get_thumb_url(url):
  head, tail = os.path.split(url)
  return head + '/thumbs/' + tail


class AddressSearchView(generic.View):
  http_method_names = ['get',]
  
  def dispatch(self, request, *args, **kwargs):
    self.addresssearch_type = 'search'
    self.addresssearch_class = 'address'
    self.addresssearch_query = 'rostock ' + request.GET.get('query', '')
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
    multi_foto_field = kwargs.pop('multi_foto_field', None)
    multi_files = kwargs.pop('multi_files', None)
    model = kwargs.pop('model', None)
    super(DataForm, self).__init__(*args, **kwargs)
    self.multi_foto_field = multi_foto_field
    self.multi_files = multi_files
    self.model = model
    self.foreign_key_label = (self.instance._meta.foreign_key_label if hasattr(self.instance._meta, 'foreign_key_label') else '')
    self.address_optional = (self.instance._meta.address_optional if hasattr(self.instance._meta, 'address_optional') else None)
    
    for field in self.fields.values():
      if field.label == 'Geometrie':
        message = 'Es muss ein Marker in der Karte gesetzt werden bzw. eine Linie oder Fläche gezeichnet werden, falls es sich um Daten linien- oder flächenhafter Repräsentation handelt!'
      elif field.__class__.__name__ == 'ModelChoiceField':
        message = 'Die Referenz zu „{label}“ ist Pflicht!'.format(label = self.foreign_key_label)
      else:
        message = 'Das Attribut „{label}“ ist Pflicht!'.format(label = field.label)
      field.error_messages = { 'required': message, 'invalid_image': 'Sie müssen eine valide Bilddatei hochladen!' }

  # Hinweis: Diese Methode wird durch Django ignoriert, falls kein Feld mit Namen foto existiert.
  def clean_foto(self):
    if self.multi_foto_field and self.multi_foto_field == True:
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
      
  def clean_geometrie(self):
    data = self.cleaned_data['geometrie']
    error_text = 'Es muss ein Marker in der Karte gesetzt werden bzw. eine Linie oder Fläche gezeichnet werden, falls es sich um Daten linien- oder flächenhafter Repräsentation handelt!'
    if '-' in str(data):
      raise ValidationError(error_text)
    return data
  
  def clean_strasse_name(self):
    data = self.cleaned_data['strasse_name']
    if not data and self.address_optional:
      return data
    elif not data and not self.address_optional:
      raise ValidationError('Das Attribut „Adresse“ ist Pflicht!')
    elif data and self.address_optional:
      error_text = 'Bitte geben Sie eine eindeutige und existierende Adresse oder Straße an. Die Schreibweise muss korrekt sein, vor allem die Groß- und Kleinschreibung!'
    else:
      error_text = 'Bitte geben Sie eine eindeutige und existierende Adresse an. Die Schreibweise muss korrekt sein, vor allem die Groß- und Kleinschreibung!'
    request = requests.get(settings.ADDRESS_SEARCH_URL + 'key=' + settings.ADDRESS_SEARCH_KEY + '&type=search&class=address&query=rostock ' + data, timeout = 3)
    json = request.json()
    ergebnisse = json.get('features')
    if not ergebnisse:
      raise ValidationError(error_text)
    for ergebnis in ergebnisse:
      if re.sub('^.*\, ', '', ergebnis.get('properties').get('_title_')) == data:
        return data
    raise ValidationError(error_text)


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
    return context


class DataView(BaseDatatableView):
  def __init__(self, model = None):
    self.model = model
    self.model_name = self.model.__name__
    self.model_name_lower = self.model.__name__.lower()
    self.columns = self.model._meta.list_fields
    self.columns_with_number = (self.model._meta.list_fields_with_number if hasattr(self.model._meta, 'list_fields_with_number') else None)
    self.columns_with_date = (self.model._meta.list_fields_with_date if hasattr(self.model._meta, 'list_fields_with_date') else None)
    self.thumbs = (self.model._meta.thumbs if hasattr(self.model._meta, 'thumbs') else None)
    self.parent_field_name_for_filter = (self.model._meta.parent_field_name_for_filter if hasattr(self.model._meta, 'parent_field_name_for_filter') else 'bezeichnung')
    super(DataView, self).__init__()

  def prepare_results(self, qs):
    json_data = []
    for item in qs:
      item_data = []
      item_id = getattr(item, self.model._meta.pk.name)
      checker = ObjectPermissionChecker(self.request.user)
      obj = self.model.objects.get(pk=item_id)
      if checker.has_perm('delete_' + self.model_name_lower, obj):
        item_data.append('<input class="action_checkbox" type="checkbox" value="' + str(item_id) + '">')
      else:
        item_data.append('')
      for column in self.columns:
        data = None
        value = getattr(item, column)
        if value is not None and self.columns_with_number is not None and column in self.columns_with_number:
          data = value
        elif value is not None and self.columns_with_date is not None and column in self.columns_with_date:
          data = datetime.strptime(str(value), '%Y-%m-%d').strftime('%d.%m.%Y')
        elif value is not None and column == 'foto':
          data = '<a href="' + value.url + '" target="_blank" title="große Ansicht öffnen…">'
          if self.thumbs is not None and self.thumbs == True:
            data += '<img src="' + get_thumb_url(value.url) + '" alt="Vorschau" />'
          else:
            data += '<img src="' + value.url + '" alt="Vorschau" width="70px" />'
          data += '</a>'
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
        item_data.append('<a href="' + reverse('datenmanagement:' + self.model_name + 'change', args=[item_id]) + '"><span class="glyphicon glyphicon-pencil"/></a>')
      else:
        item_data.append('')
      if checker.has_perm('delete_' + self.model_name_lower, obj):
        item_data.append('<a href="' + reverse('datenmanagement:' + self.model_name + 'delete', args=[item_id]) + '"><span class="glyphicon glyphicon-trash"/></a>')
      else:
        item_data.append('')
      json_data.append(item_data)
    return json_data

  def filter_queryset(self, qs):
    search = self.request.GET.get('search[value]', None)
    if search:
      qs_params = None
      for column in self.columns:
        if column == 'parent':
          column = 'parent__' + self.parent_field_name_for_filter
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
    column = str(self.columns[int(order_column) - 1])
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
    context['list_fields'] = self.model._meta.list_fields
    context['list_fields_labels'] = self.model._meta.list_fields_labels
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
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model._meta.description
    context['list_fields'] = self.model._meta.list_fields
    context['list_fields_labels'] = self.model._meta.list_fields_labels
    context['show_alkis'] = (self.model._meta.show_alkis if hasattr(self.model._meta, 'show_alkis') else None)
    context['map_feature_tooltip_field'] = (self.model._meta.map_feature_tooltip_field if hasattr(self.model._meta, 'map_feature_tooltip_field') else None)
    context['geometry_type'] = (self.model._meta.geometry_type if hasattr(self.model._meta, 'geometry_type') else None)
    return context


class DataAddView(generic.CreateView):
  def get_form_kwargs(self):
    kwargs = super(DataAddView, self).get_form_kwargs()
    self.multi_foto_field = (self.model._meta.multi_foto_field if hasattr(self.model._meta, 'multi_foto_field') else None)
    self.multi_files = (self.request.FILES if hasattr(self.model._meta, 'multi_foto_field') and self.request.method == 'POST' else None)
    kwargs['multi_foto_field'] = self.multi_foto_field
    kwargs['multi_files'] = self.multi_files
    kwargs['model'] = self.model
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
    context['READONLY_FIELD_DEFAULT'] = settings.READONLY_FIELD_DEFAULT
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model._meta.description
    context['show_alkis'] = (self.model._meta.show_alkis if hasattr(self.model._meta, 'show_alkis') else None)
    context['address'] = (self.model._meta.address if hasattr(self.model._meta, 'address') else None)
    context['address_optional'] = (self.model._meta.address_optional if hasattr(self.model._meta, 'address_optional') else None)
    context['geometry_type'] = (self.model._meta.geometry_type if hasattr(self.model._meta, 'geometry_type') else None)
    context['foreign_key_label'] = (self.model._meta.foreign_key_label if hasattr(self.model._meta, 'foreign_key_label') else None)
    context['readonly_fields'] = (self.model._meta.readonly_fields if hasattr(self.model._meta, 'readonly_fields') else None)
    context['multi_foto_field'] = (self.model._meta.multi_foto_field if hasattr(self.model._meta, 'multi_foto_field') else None)
    return context

  def get_initial(self):
    return {
      'ansprechpartner': self.request.user.first_name + ' ' + self.request.user.last_name + ' (' + self.request.user.email.lower() + ')',
      'bearbeiter': self.request.user.first_name + ' ' + self.request.user.last_name
    }

  def form_valid(self, form):
    form.instance = form.save(commit = False)
    if hasattr(self.model._meta, 'address') and self.model._meta.address:
      if form.instance.strasse_name:
        adresse = form.instance.strasse_name
        form.instance.strasse_name = re.sub(' [0-9]+([a-z]+)?$', '', adresse)
        m = re.search('[0-9]+[a-z]+$', adresse)
        if m:
          form.instance.hausnummer = re.sub('[a-z]+', '', m.group(0))
          form.instance.hausnummer_zusatz = re.sub('\d+', '', m.group(0))
        m = re.search('[0-9]+$', adresse)
        if m:
          form.instance.hausnummer = m.group(0)
    form.instance = form.save()
    assign_perm('datenmanagement.change_' + self.model.__name__.lower(), self.request.user, form.instance)
    assign_perm('datenmanagement.delete_' + self.model.__name__.lower(), self.request.user, form.instance)
    for group in Group.objects.all():
      if group.permissions.filter(codename = 'change_' + self.model.__name__.lower()):
        assign_perm('datenmanagement.change_' + self.model.__name__.lower(), group, form.instance)
      if group.permissions.filter(codename = 'delete_' + self.model.__name__.lower()):
        assign_perm('datenmanagement.delete_' + self.model.__name__.lower(), group, form.instance)
    return super(DataAddView, self).form_valid(form)


class DataChangeView(generic.UpdateView):
  def __init__(self, model = None, template_name = None, success_url = None):
    self.model = model
    self.template_name = template_name
    self.success_url = success_url
    self.form_class = modelform_factory(self.model, form = DataForm, fields = '__all__', formfield_callback = assign_widgets)
    super(DataChangeView, self).__init__()

  def get_context_data(self, **kwargs):
    context = super(DataChangeView, self).get_context_data(**kwargs)
    context['READONLY_FIELD_DEFAULT'] = settings.READONLY_FIELD_DEFAULT
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name'] = self.model._meta.verbose_name
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model._meta.description
    context['show_alkis'] = (self.model._meta.show_alkis if hasattr(self.model._meta, 'show_alkis') else None)
    context['address'] = (self.model._meta.address if hasattr(self.model._meta, 'address') else None)
    context['address_optional'] = (self.model._meta.address_optional if hasattr(self.model._meta, 'address_optional') else None)
    context['geometry_type'] = (self.model._meta.geometry_type if hasattr(self.model._meta, 'geometry_type') else None)
    context['foreign_key_label'] = (self.model._meta.foreign_key_label if hasattr(self.model._meta, 'foreign_key_label') else None)
    context['readonly_fields'] = (self.model._meta.readonly_fields if hasattr(self.model._meta, 'readonly_fields') else None)
    return context

  def get_initial(self):
    if hasattr(self.model._meta, 'address') and self.model._meta.address:
      if hasattr(self.object, 'strasse_name') and self.object.strasse_name:
        adresse = self.object.strasse_name.strip()
        if hasattr(self.object, 'hausnummer') and self.object.hausnummer:
          adresse = (adresse + ' ' + self.object.hausnummer.strip())
          if hasattr(self.object, 'hausnummer_zusatz') and self.object.hausnummer_zusatz:
            adresse = adresse + self.object.hausnummer_zusatz.strip()
        return {
          'strasse_name': adresse
        }
      else:
        return {
        }
    else:
      return {
      }

  def form_valid(self, form):
    form.instance = form.save(commit = False)
    if hasattr(self.model._meta, 'address') and self.model._meta.address:
      if form.instance.strasse_name:
        adresse = form.instance.strasse_name
        form.instance.strasse_name = re.sub(' [0-9]+([a-z]+)?$', '', adresse)
        m = re.search('[0-9]+[a-z]+$', adresse)
        if m:
          form.instance.hausnummer = re.sub('[a-z]+', '', m.group(0))
          form.instance.hausnummer_zusatz = re.sub('\d+', '', m.group(0))
        m = re.search('[0-9]+$', adresse)
        if m:
          form.instance.hausnummer = m.group(0)
    form.instance = form.save()
    return super(DataChangeView, self).form_valid(form)
    
  def get_object(self, *args, **kwargs):
    obj = super(DataChangeView, self).get_object(*args, **kwargs)
    userobjperm = ObjectPermissionChecker(self.request.user).has_perm('change_' + self.model.__name__.lower(), obj)
    if not userobjperm:
      raise PermissionDenied()
    return obj


class DataDeleteView(generic.DeleteView):
  def get_object(self, *args, **kwargs):
    obj = super(DataDeleteView, self).get_object(*args, **kwargs)
    userobjperm = ObjectPermissionChecker(self.request.user).has_perm('delete_' + self.model.__name__.lower(), obj)
    if not userobjperm:
      raise PermissionDenied()
    return obj
