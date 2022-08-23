import json
import re
import time

from datetime import datetime, timezone
from django.conf import settings
from django.db.models import Q
from django.urls import reverse
from django.utils.html import escape
from django.views import generic
from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.core import ObjectPermissionChecker
from zoneinfo import ZoneInfo

from . import functions



class DataView(BaseDatatableView):
    """
    bereitet Datenbankobjekte für Tabellenansicht auf
    """

    def __init__(self, model=None):
        self.model = model
        self.model_name = self.model.__name__
        self.model_name_lower = self.model.__name__.lower()
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

    def prepare_results(self, qs):
        """
        Checkt Datensatz auf Datentypen und erstellt daraus eine
        Liste mit angepasstem Inhalt (Bsp: True -> ja)

        :param qs: QuerySet
        :return: Json
        """
        json_data = []
        for item in qs:
            item_data = []
            item_id = getattr(item, self.model._meta.pk.name)
            checker = ObjectPermissionChecker(self.request.user)
            obj = self.model.objects.get(pk=item_id)
            if checker.has_perm('delete_' + self.model_name_lower, obj):
                item_data.append(
                    '<input class="action-checkbox" type="checkbox" value="' +
                    str(item_id) +
                    '">')
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
                    data = '<a href="' + reverse(
                        'datenmanagement:' + foreign_model.replace(
                            value._meta.app_label + '.',
                            ''
                        ) + 'change',
                        args=[
                            getattr(
                                value,
                                foreign_model_primary_key
                            )
                        ]
                    ) + '" target="_blank" class="required" title="' + foreign_model_title + ' ansehen oder bearbeiten">' + str(
                        getattr(
                            value,
                            foreign_model_attribute_for_text)) + '</a>'
                elif value is not None and self.columns_with_number is not None and column in self.columns_with_number:
                    data = value
                elif value is not None and self.columns_with_date is not None and column in self.columns_with_date:
                    data = datetime.strptime(str(value), '%Y-%m-%d').strftime(
                        '%d.%m.%Y')
                elif value is not None and self.columns_with_datetime is not None and column in self.columns_with_datetime:
                    datetimestamp_str = re.sub(r'([+-][0-9]{2})\:', '\\1', str(value))
                    datetimestamp = datetime.strptime(datetimestamp_str, '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=timezone.utc).astimezone(ZoneInfo(settings.TIME_ZONE))
                    datetimestamp_str = datetimestamp.strftime('%d.%m.%Y, %H:%M:%S Uhr')
                    data = datetimestamp_str
                elif value is not None and value and self.column_as_highlight_flag is not None and column == self.column_as_highlight_flag:
                    data = '<p class="text-danger" title="Konflikt(e) vorhanden!">ja</p>'
                elif value is not None and column == 'foto':
                    try:
                        data = '<a href="' + value.url + '?' + str(
                            time.time()) + '" target="_blank" title="große Ansicht öffnen…">'
                        if self.thumbs is not None and self.thumbs:
                            data += '<img src="' + functions.get_thumb_url(
                                value.url) + '?' + str(
                                time.time()) + '" alt="Vorschau" />'
                        else:
                            data += '<img src="' + value.url + '?' + str(
                                time.time()) + '" alt="Vorschau" width="70px" />'
                        data += '</a>'
                    except ValueError:
                        pass
                elif value is not None and (
                        column == 'dokument' or column == 'pdf'):
                    try:
                        data = '<a href="' + value.url + '?' + str(time.time()) \
                            + '" target="_blank" title="' + (('PDF' if column == 'pdf'
                                else 'Dokument')) \
                            + ' öffnen…">Link zum ' + (('PDF'
                 if column == 'pdf' else 'Dokument')) + '</a>'
                    except ValueError:
                        pass
                elif value is not None and value is True:
                    data = 'ja'  # True durch 'Ja' ersetzen
                elif value is not None and value is False:
                    data = 'nein'  # False durch 'nein' ersetzen
                elif value is not None and type(value) in [list, tuple]:
                    data = ', '.join(map(str, value))
                elif value is not None and \
                        isinstance(value, str) and value.startswith('http'):
                    data = '<a href="' + value + '" target="_blank" title="Link öffnen…">' + value + '</a>'
                elif value is not None and \
                        isinstance(value, str) and re.match(r"^#[a-f0-9]{6}$", value, re.IGNORECASE):
                            data = '<div style="background-color:' + value + '" title="Hex-Wert: ' \
                                + value + ' || RGB-Wert: ' + str(int(value[1:3], 16)) + ', ' \
                                + str(int(value[3:5], 16)) + ', ' + str(int(value[5:7], 16)) \
                                + '">&zwnj;</div>'
                elif value is not None:
                    data = escape(value)
                item_data.append(data)
            if checker.has_perm('change_' + self.model_name_lower, obj):
                item_data.append(
                    '<a href="' +
                    reverse(
                        'datenmanagement:' +
                        self.model_name +
                        'change',
                        args=[item_id]) +
                    '"><i class="fas fa-edit" title="Datensatz bearbeiten"></i></a>')
            elif self.request.user.has_perm(
                    'datenmanagement.view_' + self.model_name_lower):
                item_data.append(
                    '<a href="' +
                    reverse(
                        'datenmanagement:' +
                        self.model_name +
                        'change',
                        args=[item_id]) +
                    '"><i class="fas fa-eye" title="Datensatz ansehen"></i></a>')
            else:
                item_data.append('')
            if checker.has_perm('delete_' + self.model_name_lower, obj):
                item_data.append(
                    '<a href="' +
                    reverse(
                        'datenmanagement:' +
                        self.model_name +
                        'delete',
                        args=[item_id]) +
                    '"><i class="fas fa-trash" title="Datensatz löschen"></i></a>')
            else:
                item_data.append('')
            json_data.append(item_data)
        return json_data

    def filter_queryset(self, qs):
        """

        :param qs:
        :return:
        """
        search = self.request.GET.get('search[value]', None)
        if search:
            qs_params = None
            for column in self.columns:
                if self.columns_with_foreign_key:
                    column_with_foreign_key = self.columns_with_foreign_key.get(
                        column)
                    if column_with_foreign_key is not None:
                        column = column + str('__') + column_with_foreign_key
                kwargs = {
                    '{0}__{1}'.format(column, 'icontains'): search
                }
                q = Q(**kwargs)
                lower_search = search.lower()
                m = re.search('^[0-9]{2}\\.[0-9]{4}$', lower_search)
                n = re.search('^[0-9]{2}\\.[0-9]{2}$', lower_search)
                if m:
                    kwargs = {
                        '{0}__{1}'.format(column, 'icontains'): re.sub(
                            '^[0-9]{2}\\.', '', m.group(0)) + '-' + re.sub(
                            '\\.[0-9]{4}$', '', m.group(0))
                    }
                    q = q | Q(**kwargs)
                elif n:
                    kwargs = {
                        '{0}__{1}'.format(column, 'icontains'): re.sub(
                            '^[0-9]{2}\\.', '', n.group(0)) + '-' + re.sub(
                            '\\.[0-9]{2}$', '', n.group(0))
                    }
                    q = q | Q(**kwargs)
                elif lower_search == 'ja':
                    kwargs = {
                        '{0}__{1}'.format(column, 'icontains'): 'true'
                    }
                    q = q | Q(**kwargs)
                elif lower_search == 'nein' or lower_search == 'nei':
                    kwargs = {
                        '{0}__{1}'.format(column, 'icontains'): 'false'
                    }
                    q = q | Q(**kwargs)
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
    """
    listet alle Datenbankobjekte eines Datensatzes in einer Tabelle auf
    """

    def __init__(self, model=None, template_name=None, success_url=None):
        self.model = model
        self.template_name = template_name
        super(DataListView, self).__init__()

    def get_context_data(self, **kwargs):
        context = super(DataListView, self).get_context_data(**kwargs)
        context['model_name'] = self.model.__name__
        context['model_name_lower'] = self.model.__name__.lower()
        context['model_verbose_name'] = self.model._meta.verbose_name
        context[
            'model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        context['model_description'] = self.model._meta.description
        context['list_fields_labels'] = list(
            self.model._meta.list_fields.values())
        context['geometry_type'] = (
            self.model._meta.geometry_type if hasattr(
                self.model._meta, 'geometry_type') else None)
        context['thumbs'] = (
            self.model._meta.thumbs if hasattr(self.model._meta,
                                               'thumbs') else None)
        return context


class DataMapView(generic.ListView):
    """
    zeigt alle Datenbankobjekte eines Datensatzes auf einer Karte an;
    außerdem werden, falls definiert, entsprechende Filtermöglichkeiten geladen
    """

    def __init__(self, model=None, template_name=None):
        self.model = model
        self.template_name = template_name
        super(DataMapView, self).__init__()

    def get_context_data(self, **kwargs):
        """
        Liefert Dictionary mit Context des DataMapView.

        :param kwargs:
        :return:
        """
        context = super(DataMapView, self).get_context_data(**kwargs)
        context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
        context['model_name'] = self.model.__name__
        context['model_name_lower'] = self.model.__name__.lower()
        context['model_verbose_name'] = self.model._meta.verbose_name
        context[
            'model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        context['model_description'] = self.model._meta.description
        context['highlight_flag'] = (
            self.model._meta.highlight_flag if hasattr(
                self.model._meta, 'highlight_flag') else None)
        context['map_feature_tooltip_field'] = (
            self.model._meta.map_feature_tooltip_field if hasattr(
                self.model._meta, 'map_feature_tooltip_field') else None)
        context['map_feature_tooltip_fields'] = (
            self.model._meta.map_feature_tooltip_fields if hasattr(
                self.model._meta, 'map_feature_tooltip_fields') else None)
        context['map_filters_enabled'] = (
            True if hasattr(self.model._meta, 'map_filter_fields') or hasattr(
                self.model._meta, 'map_rangefilter_fields') else None)
        context['map_rangefilter_fields'] = (
            list(self.model._meta.map_rangefilter_fields.keys()) if hasattr(
                self.model._meta, 'map_rangefilter_fields') else None)
        context['map_rangefilter_fields_json'] = (json.dumps(
            list(self.model._meta.map_rangefilter_fields.keys())) if hasattr(
            self.model._meta, 'map_rangefilter_fields') else None)
        context['map_rangefilter_fields_labels'] = (
            list(self.model._meta.map_rangefilter_fields.values()) if hasattr(
                self.model._meta, 'map_rangefilter_fields') else None)
        context['map_deadlinefilter_fields'] = (
            self.model._meta.map_deadlinefilter_fields if hasattr(
                self.model._meta, 'map_deadlinefilter_fields') else None)
        context['map_filter_fields'] = (
            list(self.model._meta.map_filter_fields.keys()) if hasattr(
                self.model._meta, 'map_filter_fields') else None)
        context['map_filter_fields_json'] = (json.dumps(
            list(self.model._meta.map_filter_fields.keys())) if hasattr(
            self.model._meta, 'map_filter_fields') else None)
        context['map_filter_fields_labels'] = (
            list(self.model._meta.map_filter_fields.values()) if hasattr(
                self.model._meta, 'map_filter_fields') else None)
        context['map_filter_fields_as_list'] = (
            self.model._meta.map_filter_fields_as_list if hasattr(
                self.model._meta, 'map_filter_fields_as_list') else None)
        context['map_filter_boolean_fields_as_checkbox'] = (
            self.model._meta.map_filter_boolean_fields_as_checkbox if hasattr(
                self.model._meta,
                'map_filter_boolean_fields_as_checkbox') else None)
        context['map_filter_field_hide_initial'] = (next(
            iter(self.model._meta.map_filter_hide_initial.keys())) if hasattr(
            self.model._meta, 'map_filter_hide_initial') and len(
            self.model._meta.map_filter_hide_initial) == 1 else None)
        context['map_filter_value_hide_initial'] = (next(
            iter(self.model._meta.map_filter_hide_initial.values())) if hasattr(
            self.model._meta, 'map_filter_hide_initial') and len(
            self.model._meta.map_filter_hide_initial) == 1 else None)
        context['additional_wms_layers'] = (
            self.model._meta.additional_wms_layers if hasattr(
                self.model._meta, 'additional_wms_layers') else None)
        context['geometry_type'] = (
            self.model._meta.geometry_type if hasattr(
                self.model._meta, 'geometry_type') else None)
        return context
