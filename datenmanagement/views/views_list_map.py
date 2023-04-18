from datetime import date, datetime, timezone
from decimal import Decimal
from django.conf import settings
from django.core.serializers import serialize
from django.db.models import Q
from django.urls import reverse
from django.utils.html import escape
from django.views import generic
from django_datatables_view.base_datatable_view import BaseDatatableView
from jsonview.views import JsonView
from json import dumps, loads
from re import IGNORECASE, match, search, sub
from time import time
from zoneinfo import ZoneInfo

from .functions import get_data, get_model_objects, get_thumb_url, \
  localize_number, set_model_related_context_elements


class DataView(BaseDatatableView):
  """
  bereitet Datenbankobjekte für Tabellenansicht auf

  :param model: Datenmodell
  """

  def __init__(self, model=None):
    self.model = model
    self.model_name = self.model.__name__
    self.model_name_lower = self.model.__name__.lower()
    self.editable = (
        self.model._meta.editable if hasattr(
            self.model._meta, 'editable') else True)
    self.columns = self.model._meta.list_fields
    self.columns_with_foreign_key_to_linkify = (
        self.model._meta.fields_with_foreign_key_to_linkify if hasattr(
            self.model._meta,
            'fields_with_foreign_key_to_linkify') else None)
    self.columns_with_foreign_key = (
        self.model._meta.list_fields_with_foreign_key if hasattr(
            self.model._meta, 'list_fields_with_foreign_key') else None)
    self.columns_with_number = (
        self.model._meta.list_fields_with_number if hasattr(
            self.model._meta, 'list_fields_with_number') else None)
    self.columns_with_date = (
        self.model._meta.list_fields_with_date if hasattr(
            self.model._meta,
            'list_fields_with_date') else None)
    self.columns_with_datetime = (
        self.model._meta.list_fields_with_datetime if hasattr(
            self.model._meta,
            'list_fields_with_datetime') else None)
    self.column_as_highlight_flag = (
        self.model._meta.highlight_flag if hasattr(
            self.model._meta, 'highlight_flag') else None)
    self.thumbs = (self.model._meta.thumbs if hasattr(self.model._meta,
                                                      'thumbs') else None)
    super(DataView, self).__init__()

  def get_initial_queryset(self):
    if self.kwargs and self.kwargs['subset_id']:
      return get_model_objects(self.model, int(self.kwargs['subset_id']))
    else:
      return get_model_objects(self.model)

  def prepare_results(self, qs):
    """
    prüft Datensatz auf Datentypen und erstellt daraus ein JSON mit angepasstem Inhalt
    (Beispiel: True -> ja)

    :param qs: Datensatz
    :return: Datensatz als JSON
    """
    json_data = []
    for item in qs:
      item_data = []
      item_id = getattr(item, self.model._meta.pk.name)
      d = ''
      if (
          not self.editable or
          not self.request.user.has_perm('datenmanagement.delete_' + self.model_name_lower)
      ):
        d = ' disabled'
      cb = '<input class="action-checkbox" type="checkbox" value="' + str(item_id) + '"' + d + '>'
      item_data.append(cb)
      for column in self.columns:
        data = None
        value = getattr(item, column)
        if (value is not None and
            self.columns_with_foreign_key is not None and
            column in self.columns_with_foreign_key and
            self.columns_with_foreign_key_to_linkify is not None and
            column in self.columns_with_foreign_key_to_linkify):
          foreign_model = value._meta.label
          foreign_model_primary_key = value._meta.pk.name
          foreign_model_title = self.columns.get(column)
          foreign_model_attribute_for_text = self.columns_with_foreign_key.get(
              column)
          data = '<a href="' + reverse(
              'datenmanagement:' + foreign_model.replace(
                  value._meta.app_label + '.',
                  ''
              ) + '_change',
              args=[
                  getattr(
                      value,
                      foreign_model_primary_key
                  )
              ]
          ) + '" target="_blank" rel="noopener noreferrer" class="required" title="'\
            + foreign_model_title + ' ansehen oder bearbeiten">' + str(
              getattr(
                  value,
                  foreign_model_attribute_for_text)) + '</a>'
        elif (value is not None and
              self.columns_with_number is not None and
              column in self.columns_with_number):
          if isinstance(value, Decimal) or match(r"^[0-9]+\.[0-9]+$", str(value)):
            data = localize_number(Decimal(str(value)))
          else:
            data = value
        elif (value is not None and
              self.columns_with_date is not None and
              column in self.columns_with_date):
          data = datetime.strptime(str(value), '%Y-%m-%d').strftime(
              '%d.%m.%Y')
        elif (value is not None and
              self.columns_with_datetime is not None and
              column in self.columns_with_datetime):
          datetimestamp_str = sub(r'([+-][0-9]{2}):', '\\1', str(value))
          datetimestamp = datetime.strptime(datetimestamp_str, '%Y-%m-%d %H:%M:%S%z').\
            replace(tzinfo=timezone.utc).astimezone(ZoneInfo(settings.TIME_ZONE))
          datetimestamp_str = datetimestamp.strftime('%d.%m.%Y, %H:%M:%S Uhr')
          data = datetimestamp_str
        elif (value is not None and
              value and
              self.column_as_highlight_flag is not None and
              column == self.column_as_highlight_flag):
          data = '<p class="text-danger" title="Konflikt(e) vorhanden!">ja</p>'
        elif value is not None and column == 'foto':
          try:
            data = ('<a href="' + value.url + '?' + str(time()) +
                    '" target="_blank" rel="noopener noreferrer" title="große Ansicht öffnen…">')
            if self.thumbs is not None and self.thumbs:
              data += '<img src="' + get_thumb_url(
                  value.url) + '?' + str(
                  time()) + '" alt="Vorschau" />'
            else:
              data += '<img src="' + value.url + '?' + str(
                  time()) + '" alt="Vorschau" width="70px" />'
            data += '</a>'
          except ValueError:
            pass
        elif value is not None and (column == 'dokument' or column == 'pdf'):
          try:
            data = '<a href="' + value.url + '?' + str(
                time()) + '" target="_blank" rel="noopener noreferrer" title="' + (
                ('PDF' if column == 'pdf' else 'Dokument')) + ' öffnen…">Link zum ' + (
                ('PDF' if column == 'pdf' else 'Dokument')) + '</a>'
          except ValueError:
            pass
        elif value is not None and value is True:
          data = 'ja'  # True durch 'Ja' ersetzen
        elif value is not None and value is False:
          data = 'nein'  # False durch 'nein' ersetzen
        elif value is not None and type(value) in [list, tuple]:
          data = ', '.join(map(str, value))
        elif value is not None and isinstance(value, str) and value.startswith('http'):
          data = ('<a href="' + value +
                  '" target="_blank" rel="noopener noreferrer" title="Link öffnen…">' +
                  value + '</a>')
        elif (value is not None and
              isinstance(value, str) and
              match(r"^#[a-f0-9]{6}$", value, IGNORECASE)):
          data = '<div style="background-color:' + value + '" title="Hex-Wert: ' \
                 + value + ' || RGB-Wert: ' + str(int(value[1:3], 16)) + ', ' \
                 + str(int(value[3:5], 16)) + ', ' + str(int(value[5:7], 16)) \
                 + '">&zwnj;</div>'
        elif value is not None:
          data = escape(value)
        item_data.append(data)
      if (
          self.editable
          and self.request.user.has_perm('datenmanagement.change_' + self.model_name_lower)
      ):
        item_data.append(
            '<a href="' +
            reverse(
                'datenmanagement:' +
                self.model_name +
                '_change',
                args=[item_id]) +
            '"><i class="fas fa-edit" title="Datensatz bearbeiten"></i></a>')
      elif (
          self.editable
          and self.request.user.has_perm('datenmanagement.view_' + self.model_name_lower)
      ):
        item_data.append(
            '<a href="' +
            reverse(
                'datenmanagement:' +
                self.model_name +
                '_change',
                args=[item_id]) +
            '"><i class="fas fa-eye" title="Datensatz ansehen"></i></a>')
      if (
          self.editable
          and self.request.user.has_perm('datenmanagement.delete_' + self.model_name_lower)
      ):
        item_data.append(
            '<a href="' +
            reverse(
                'datenmanagement:' +
                self.model_name +
                '_delete',
                args=[item_id]) +
            '"><i class="fas fa-trash" title="Datensatz löschen"></i></a>')
      json_data.append(item_data)
    return json_data

  def filter_queryset(self, qs):
    """
    filtert Datensatz

    :param qs: Datensatz
    :return: gefilterter Datensatz
    """
    current_search = self.request.GET.get('search[value]', None)
    if current_search:
      qs_params = None
      for search_element in current_search.lower().split():
        qs_params_inner = None
        for column in self.columns:
          if self.columns_with_foreign_key:
            column_with_foreign_key = self.columns_with_foreign_key.get(
                column)
            if column_with_foreign_key is not None:
              column = column + str('__') + column_with_foreign_key
          case_a = search('^[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}$', search_element)
          case_b = search('^[0-9]{2}\\.[0-9]{4}$', search_element)
          case_c = search('^[0-9]{2}\\.[0-9]{2}$', search_element)
          if case_a or case_b or case_c:
            search_element_splitted = search_element.split('.')
            kwargs = {
                '{0}__{1}'.format(column, 'icontains'): (search_element_splitted[
                    2] + '-' if case_a else '') +
                search_element_splitted[1] + '-' +
                search_element_splitted[0]
            }
          elif search_element == 'ja':
            kwargs = {
                '{0}__{1}'.format(column, 'icontains'): 'true'
            }
          elif search_element == 'nein' or search_element == 'nei':
            kwargs = {
                '{0}__{1}'.format(column, 'icontains'): 'false'
            }
          elif match(r"^[0-9]+,[0-9]+$", search_element):
            kwargs = {
                '{0}__{1}'.format(column, 'icontains'): sub(',', '.', search_element)
            }
          else:
            kwargs = {
                '{0}__{1}'.format(column, 'icontains'): search_element
            }
          q = Q(**kwargs)
          qs_params_inner = qs_params_inner | q if qs_params_inner else q
        qs_params = qs_params & qs_params_inner if qs_params else qs_params_inner
      qs = qs.filter(qs_params)
    return qs

  def ordering(self, qs):
    """
    sortiert Datensatz

    :param qs: Datensatz
    :return: sortierter Datensatz
    """
    order_column = self.request.GET.get('order[0][column]', None)
    order_dir = self.request.GET.get('order[0][dir]', None)
    columns = list(self.columns.keys())
    column = str(columns[int(order_column) - 1])
    directory = '-' if order_dir is not None and order_dir == 'desc' else ''
    if order_column is not None:
      return qs.order_by(directory + column)
    else:
      return qs


class DataListView(generic.ListView):
  """
  listet alle Datenbankobjekte eines Datensatzes in einer Tabelle auf

  :param model: Datenmodell
  :param template_name: Name des Templates
  :param success_url: Success-URL
  """

  def __init__(self, model=None, template_name=None, success_url=None):
    self.model = model
    self.template_name = template_name
    super(DataListView, self).__init__()

  def get_queryset(self):
    """
    überschreibt Funktion für Standard-Rückgabewert,
    damit diese nichts zurückgibt statt stumpf die Gesamtmenge aller Objekte des Datenmodells
    """
    return

  def get_context_data(self, **kwargs):
    """
    liefert Dictionary mit Kontextelementen des Views

    :param kwargs:
    :return: Dictionary mit Kontextelementen des Views
    """
    context = super(DataListView, self).get_context_data(**kwargs)
    context = set_model_related_context_elements(context, self.model, self.kwargs)
    context['list_fields_labels'] = list(self.model._meta.list_fields.values())
    context['thumbs'] = (self.model._meta.thumbs if hasattr(self.model._meta, 'thumbs') else None)
    return context


class DataMapView(JsonView):
  """
  Abfrage aller Datenbankobjekte eines Datensatzes für die Karte
  * limit: auf n Datenbankobjekte limitieren (entspricht SQL-LIMIT)
  * offset: alle weiteren Datenbankobjekte ab dem n-ten Datenbankobjekt (entspricht SQL-OFFSET)

  :param model: Datenmodell
  """
  model = None

  def __init__(self, model):
    self.model = model
    self.model_name = self.model.__name__
    self.model_name_lower = self.model.__name__.lower()
    self.model_pk_field = self.model._meta.pk.name
    self.editable = (
        self.model._meta.editable if hasattr(
            self.model._meta, 'editable') else True)
    super(DataMapView, self).__init__()

  def get_context_data(self, **kwargs):
    """
    liefert Dictionary mit Kontextelementen des Views

    :param kwargs:
    :return: Dictionary mit Kontextelementen des Views
    """
    map_features, limit, offset, objects = None, None, None, None
    if self.request.GET.get('limit'):
      limit = int(self.request.GET.get('limit'))
    if self.request.GET.get('offset'):
      offset = int(self.request.GET.get('offset'))
    # GeoJSON-FeatureCollection definieren
    map_features = {
        'type': 'FeatureCollection',
        'features': []
    }
    if self.kwargs and self.kwargs['subset_id']:
      objects = get_model_objects(self.model, int(self.kwargs['subset_id']))
    else:
      objects = get_model_objects(self.model)
    if limit is not None and offset is not None:
      objects = objects[offset:(offset + limit)]
    elif limit is not None:
      objects = objects[:limit]
    # über alle Objekte gehen...
    for curr_object in objects:
      # nur, falls Geometrie nicht leer ist...
      if curr_object.geometrie:
        # Objekt als GeoJSON serializieren
        object_serialized = loads(
            serialize('geojson',
                      [curr_object],
                      srid=25833))
        # Tooltip erzeugen
        if hasattr(self.model._meta, 'map_feature_tooltip_field'):
          data = getattr(
              curr_object, self.model._meta.map_feature_tooltip_field)
          if isinstance(data, date):
            data = data.strftime('%d.%m.%Y')
          elif isinstance(data, datetime):
            data = data.strftime('%d.%m.%Y, %H:%M:%S Uhr')
          tooltip = str(data)
        elif hasattr(self.model._meta, 'map_feature_tooltip_fields'):
          previous_value = ''
          tooltip_value = ''
          index = 0
          for field in self.model._meta.map_feature_tooltip_fields:
            field_value = ''
            if field and getattr(curr_object, field) is not None:
              field_value = str(getattr(curr_object, field))
            tooltip_value = (
                # Leerzeichen zwischen einzelne Tooltip-Bestandteilen setzen,
                # aber nicht zwischen Hausnummer und Hausnummernzusatz
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
        # GeoJSON-Feature definieren:
        # * Geometrie aus serialisiertem GeoJSON holen
        # * Eigenschaften aus den zuvor befüllten Variablen holen
        feature = {
            'type': 'Feature',
            'geometry': object_serialized['features'][0]['geometry'],
            'properties': {
                self.model_pk_field: str(curr_object.pk),
                'tooltip': tooltip
            },
            'crs': {
                'type': 'name',
                'properties': {
                    'name': 'urn:ogc:def:crs:EPSG::25833'
                }
            }
        }
        # falls Datenmodell generell bearbeitet werden darf...
        if self.editable:
          # Link auf Objekt als Eigenschaft setzen
          feature['properties']['link'] = (
              reverse(
                  'datenmanagement:' +
                  self.model_name +
                  '_change',
                  args=[curr_object.pk]))
        # optional: Objekt als inaktiv kennzeichnen
        if curr_object.aktiv is False:
          feature['properties']['inaktiv'] = True
        # optional: Flag zum initialen Erscheinen des Objekts auf der Karte als Eigenschaft setzen,
        # falls entsprechende Klausel in der Modelldefinition existiert
        if hasattr(self.model._meta, 'map_filter_hide_initial'):
          if str(
              getattr(
                  curr_object, list(
                      self.model._meta.map_filter_hide_initial.keys())[0])) == str(
              list(
                  self.model._meta.map_filter_hide_initial.values())[0]):
            feature['properties']['hide_initial'] = True
        # optional: Flag zum Highlighten des Objekts auf der Karte als Eigenschaft setzen,
        # falls entsprechende Klausel in der Modelldefinition existiert
        if hasattr(self.model._meta, 'highlight_flag'):
          data = getattr(
              curr_object, self.model._meta.highlight_flag)
          if data:
            feature['properties']['highlight'] = data
        # optional: Stichtagsfilter als Eigenschaften setzen,
        # falls entsprechende Klausel in der Modelldefinition existiert
        if hasattr(self.model._meta, 'map_deadlinefilter_fields'):
          for index, field in enumerate(
                  self.model._meta.map_deadlinefilter_fields):
            data = getattr(curr_object, field)
            if isinstance(data, date):
              data = data.strftime('%Y-%m-%d')
            elif isinstance(data, datetime):
              data = data.strftime('%Y-%m-%d %H:%M:%S')
            feature['properties']['deadline_' +
                                  str(index)] = str(data)
            # zusätzlich Feld auch als "normale" Filtereigenschaft setzen
            feature['properties'][field] = str(data)
        # optional: Intervallfilter als Eigenschaften setzen,
        # falls entsprechende Klausel in der Modelldefinition existiert
        if hasattr(self.model._meta, 'map_rangefilter_fields'):
          for field in self.model._meta.map_rangefilter_fields.keys():
            feature['properties'][field] = str(get_data(curr_object, field))
        # optional: sonstige Filter als Eigenschaften setzen,
        # falls entsprechende Klausel in der Modelldefinition existiert
        if hasattr(self.model._meta, 'map_filter_fields'):
          for field in self.model._meta.map_filter_fields.keys():
            feature['properties'][field] = str(get_data(curr_object, field))
        # GeoJSON-Feature zur GeoJSON-FeatureCollection hinzufügen
        map_features['features'].append(feature)
    return map_features


class DataMapListView(generic.ListView):
  """
  zeigt alle Datenbankobjekte eines Datensatzes auf einer Karte an;
  außerdem werden, falls definiert, entsprechende Filtermöglichkeiten geladen

  :param model: Datenmodell
  :param template_name: Name des Templates
  """

  def __init__(self, model=None, template_name=None):
    self.model = model
    self.model_name = self.model.__name__
    self.model_name_lower = self.model.__name__.lower()
    self.template_name = template_name
    super(DataMapListView, self).__init__()

  def get_queryset(self):
    """
    überschreibt Funktion für Standard-Rückgabewert,
    damit diese nichts zurückgibt statt stumpf die Gesamtmenge aller Objekte des Datenmodells
    """
    return

  def get_context_data(self, **kwargs):
    """
    liefert Dictionary mit Kontextelementen des Views

    :param kwargs:
    :return: Dictionary mit Kontextelementen des Views
    """
    # Variablen für Filterfelder vorbereiten, die als Intervallfelder fungieren sollen,
    # und zwar eine Variable mit dem Minimal- und eine Variable mit dem Maximalwert
    interval_filter_min = None
    interval_filter_max = None
    if hasattr(self.model._meta, 'map_rangefilter_fields'):
      # Feld für Minimalwerte definieren
      field_name = list(self.model._meta.map_rangefilter_fields.keys())[0]
      # NOT-NULL-Filter konstruieren
      field_name_isnull = field_name + '__isnull'
      # Minimalwert erhalten und in vorbereitete Variable einfügen
      interval_filter_min = self.model.objects.exclude(**{field_name_isnull: True}).order_by(
          field_name).values_list(field_name, flat=True).first()
      if isinstance(interval_filter_min, date):
        interval_filter_min = interval_filter_min.strftime('%Y-%m-%d')
      elif isinstance(interval_filter_min, datetime):
        interval_filter_min = interval_filter_min.strftime('%Y-%m-%d %H:%M:%S')
      # Feld für Maximalwerte definieren
      field_name = list(self.model._meta.map_rangefilter_fields.keys())[1]
      # NOT-NULL-Filter konstruieren
      field_name_isnull = field_name + '__isnull'
      # Maximalwert erhalten und in vorbereitete Variable einfügen
      interval_filter_max = self.model.objects.exclude(**{field_name_isnull: True}).order_by(
          field_name).values_list(field_name, flat=True).last()
      if isinstance(interval_filter_max, date):
        interval_filter_max = interval_filter_max.strftime('%Y-%m-%d')
      elif isinstance(interval_filter_max, datetime):
        interval_filter_max = interval_filter_max.strftime('%Y-%m-%d %H:%M:%S')
    # Dictionary für Filterfelder vorbereiten, die als Auswahlfeld fungieren sollen
    list_filter_lists = {}
    if hasattr(self.model._meta, 'map_filter_fields_as_list'):
      # alle entsprechend definierten Felder durchgehen
      for field_name in self.model._meta.map_filter_fields_as_list:
        # passendes Zielmodell identifizieren
        target_model = self.model._meta.get_field(field_name).remote_field.model
        # passendes Feld im Zielmodell für die Sortierung identifizieren
        foreign_field_name_ordering = target_model._meta.ordering[0]
        # passendes Feld im Zielmodell für die Anzeige identifizieren
        if hasattr(target_model._meta, 'naming'):
          foreign_field_name_naming = target_model._meta.naming
        else:
          foreign_field_name_naming = foreign_field_name_ordering
        # NOT-NULL-Filter konstruieren
        field_name_isnull = field_name + '__isnull'
        # sortierte Liste aller eindeutigen Werte des passenden Feldes aus Zielmodell erhalten
        value_list = list(
            self.model.objects.exclude(**{field_name_isnull: True}).order_by(
                field_name + '__' + foreign_field_name_ordering).values_list(
                field_name + '__' + foreign_field_name_naming, flat=True).distinct())
        # Dezimalzahlen in Liste in Strings umwandeln,
        # da Dezimalzahlen nicht als JSON serialisiert werden können
        cleaned_value_list = []
        for value in value_list:
          cleaned_value_list.append(str(value) if isinstance(value, Decimal) else value)
        # Liste in vorbereitetes Dictionary einfügen
        list_filter_lists[field_name] = cleaned_value_list
    # Dictionary für Filterfelder vorbereiten, die als Checkboxen-Set fungieren sollen
    checkbox_filter_lists = {}
    if hasattr(self.model._meta, 'map_filter_fields'):
      # alle entsprechend definierten Felder durchgehen
      for field_name in self.model._meta.map_filter_fields:
        # falls es sich um ein ChoiceArrayField handelt
        # oder das Feld explizit als Checkboxen-Set fungieren soll...
        if (
          self.model._meta.get_field(field_name).__class__.__name__ == 'ChoiceArrayField'
          or (
            hasattr(self.model._meta, 'map_filter_fields_as_checkbox')
            and field_name in self.model._meta.map_filter_fields_as_checkbox
          )
        ):
          complete_field_name_ordering = complete_field_name_naming = field_name
          # falls es sich um ein Fremdschlüsselfeld handelt...
          if (
            hasattr(self.model._meta.get_field(field_name), 'remote_field')
            and self.model._meta.get_field(field_name).remote_field is not None
          ):
            # passendes Zielmodell identifizieren
            target_model = self.model._meta.get_field(field_name).remote_field.model
            # passendes Feld im Zielmodell für die Sortierung identifizieren
            foreign_field_name_ordering = target_model._meta.ordering[0]
            # passendes Feld im Zielmodell für die Anzeige identifizieren
            if hasattr(target_model._meta, 'naming'):
              foreign_field_name_naming = target_model._meta.naming
            else:
              foreign_field_name_naming = foreign_field_name_ordering
            complete_field_name_ordering = field_name + '__' + foreign_field_name_ordering
            complete_field_name_naming = field_name + '__' + foreign_field_name_naming
          # NOT-NULL-Filter konstruieren
          field_name_isnull = field_name + '__isnull'
          # sortierte Liste aller eindeutigen Werte des Feldes erhalten
          values_list = list(
            self.model.objects.exclude(**{field_name_isnull: True}).order_by(
              complete_field_name_ordering).values_list(
              complete_field_name_naming, flat=True).distinct())
          # falls es sich NICHT um ein Fremdschlüsselfeld handelt...
          if field_name == complete_field_name_ordering:
            # Werte vereinzeln und sortierte Liste aller eindeutigen Einzelwerte erhalten
            value_list = list([item for sublist in values_list for item in sublist])
            distinct_value_list = []
            for value_list_item in value_list:
              if value_list_item not in distinct_value_list:
                distinct_value_list.append(value_list_item)
            # Dezimalzahlen in Liste in Strings umwandeln,
            # da Dezimalzahlen nicht als JSON serialisiert werden können
            cleaned_distinct_value_list = []
            for distinct_value in distinct_value_list:
              cleaned_distinct_value_list.append(str(distinct_value)
                                                 if isinstance(distinct_value, Decimal)
                                                 else distinct_value)
            # Liste in vorbereitetes Dictionary einfügen
            checkbox_filter_lists[field_name] = cleaned_distinct_value_list
          # ansonsten...
          else:
            # sortierte Liste aller eindeutigen Einzelwerte
            # direkt in vorbereitetes Dictionary einfügen
            checkbox_filter_lists[field_name] = values_list
    context = super(DataMapListView, self).get_context_data(**kwargs)
    context = set_model_related_context_elements(context, self.model, self.kwargs)
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['subset_id'] = (
        int(self.kwargs['subset_id']) if self.kwargs and self.kwargs['subset_id'] else None)
    context['highlight_flag'] = (
        self.model._meta.highlight_flag if hasattr(
            self.model._meta, 'highlight_flag') else None)
    context['map_filters_enabled'] = (
        True if hasattr(self.model._meta, 'map_filter_fields') or hasattr(
            self.model._meta, 'map_rangefilter_fields') else None)
    context['map_one_click_filters'] = (
        self.model._meta.map_one_click_filters if hasattr(
            self.model._meta, 'map_one_click_filters') else None)
    context['map_rangefilter_fields'] = (
        list(self.model._meta.map_rangefilter_fields.keys()) if hasattr(
            self.model._meta, 'map_rangefilter_fields') else None)
    context['map_rangefilter_fields_labels'] = (
        list(self.model._meta.map_rangefilter_fields.values()) if hasattr(
            self.model._meta, 'map_rangefilter_fields') else None)
    context['interval_filter_min'] = interval_filter_min
    context['interval_filter_max'] = interval_filter_max
    context['map_deadlinefilter_fields'] = (
        self.model._meta.map_deadlinefilter_fields if hasattr(
            self.model._meta, 'map_deadlinefilter_fields') else None)
    context['map_filter_fields'] = (
        list(self.model._meta.map_filter_fields.keys()) if hasattr(
            self.model._meta, 'map_filter_fields') else None)
    context['map_filter_fields_labels'] = (
        list(self.model._meta.map_filter_fields.values()) if hasattr(
            self.model._meta, 'map_filter_fields') else None)
    context['map_filter_fields_as_checkbox'] = (
        self.model._meta.map_filter_fields_as_checkbox if hasattr(
            self.model._meta, 'map_filter_fields_as_checkbox') else None)
    context['checkbox_filter_lists'] = dumps(checkbox_filter_lists)
    context['map_filter_fields_as_list'] = (
        self.model._meta.map_filter_fields_as_list if hasattr(
            self.model._meta, 'map_filter_fields_as_list') else None)
    context['list_filter_lists'] = dumps(list_filter_lists)
    context['map_filter_boolean_fields_as_checkbox'] = (
        self.model._meta.map_filter_boolean_fields_as_checkbox if hasattr(
            self.model._meta,
            'map_filter_boolean_fields_as_checkbox') else None)
    context['map_filter_hide_initial'] = (
        True if hasattr(
            self.model._meta, 'map_filter_hide_initial') else False)
    context['additional_wms_layers'] = (
        self.model._meta.additional_wms_layers if hasattr(
            self.model._meta, 'additional_wms_layers') else None)
    context['heavy_load_limit'] = (
        self.model._meta.heavy_load_limit if hasattr(
            self.model._meta, 'heavy_load_limit') else None)
    return context
