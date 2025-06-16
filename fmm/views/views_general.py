from datetime import date, datetime

from django.urls import reverse
from django.views.generic.base import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from toolbox.utils import format_boolean, format_date_datetime

from ..models import Fmf, PaketUmwelt
from ..utils import get_icon_from_settings, is_fmm_user
from .functions import (
  add_permissions_context_elements,
  add_useragent_context_elements,
  get_fmf_queryset,
  get_referer,
  get_referer_url,
)
from .views_forms import ObjectUpdateView


class IndexView(TemplateView):
  """
  view for main page

  :param template_name: template name
  """

  template_name = 'fmm/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    return context


class TableDataView(BaseDatatableView):
  """
  view for composing table data

  :param columns: table columns with names (as keys) and titles/headers (as values)
  """

  columns = {
    'id': 'ID',
    'created': 'Erstellungszeitpunkt',
    'modified': 'Änderungszeitpunkt',
    'bezeichnung': 'Bezeichnung',
  }

  def render_to_response(self, context):
    """
    returns a JSON response containing passed context as payload
    or an empty dictionary if no context is provided
    """
    if self.request.user.is_superuser or is_fmm_user(self.request.user):
      return self.get_json_response(context)
    return self.get_json_response('{"has_necessary_permissions": false}')

  def get_initial_queryset(self):
    """
    loads initial queryset
    """
    if self.request.user.is_superuser or is_fmm_user(self.request.user):
      return get_fmf_queryset()
    return Fmf.objects.none()

  def count_records(self, qs):
    """
    calculates the number of records in the queryset
    """
    return len(qs) if isinstance(qs, list) else qs.count()

  def prepare_results(self, qs):
    """
    loops passed queryset, creates cleaned-up JSON representation of the queryset and returns it

    :param qs: queryset
    :return: cleaned-up JSON representation of the queryset
    """
    json_data = []
    if self.request.user.is_superuser or is_fmm_user(self.request.user):
      for item in qs:
        item_data = []
        for column in item.keys():
          data, value = '', item[column]
          if value:
            # format dates and datetimes
            if isinstance(value, date) or isinstance(value, datetime):
              data = format_date_datetime(value)
            else:
              data = value
          item_data.append(data)
        # append links
        links = '<a class="btn btn-sm btn-outline-warning" role="button" href="'
        links += reverse(viewname='fmm:overview', kwargs={'pk': item['id']})
        links += '"><i class="fas fa-' + get_icon_from_settings('overview')
        links += '" title="Übersichtsseite öffnen"></i></a>'
        links += '<a class="ms-1 btn btn-sm btn-outline-danger" role="button" href="'
        links += reverse(viewname='fmm:fmf_delete', kwargs={'pk': item['id']})
        links += '"><i class="fas fa-' + get_icon_from_settings('delete')
        links += '" title="löschen"></i></a>'
        item_data.append(links)
        json_data.append(item_data)
    return json_data

  def filter_queryset(self, qs):
    """
    filters passed queryset

    :param qs: queryset
    :return: filtered queryset
    """

    def search(search_base, search_str):
      search_str_lower = search_str.lower()
      return [
        search_item
        for search_item in search_base
        if any(
          search_str_lower in format_date_datetime(value)
          if isinstance(value, (date, datetime))
          else search_str_lower in str(value).lower()
          for value in search_item.values()
        )
      ]

    current_search_str = self.request.GET.get('search[value]', None)
    if current_search_str:
      return search(qs, current_search_str)
    return qs

  def ordering(self, qs):
    """
    sorts passed queryset

    :param qs: queryset
    :return: sorted queryset
    """

    def sort_key(x):
      """
      returns a tuple where the first element is a boolean
      (True if value at the passed key in the passed dict is None, False otherwise)
      and the second element is the value at the passed key in the passed dict itself
      """
      return x[column_name] is None, x[column_name]

    # assume initial order since multiple column sorting is prohibited
    if self.request.GET.get('order[0][column]', None):
      order_column = self.request.GET.get('order[0][column]')
      order_dir = self.request.GET.get('order[0][dir]', None)
      column_name = list(self.columns.keys())[int(order_column)]
      reverse_order = True if order_dir is not None and order_dir == 'desc' else False
      return sorted(qs, key=sort_key, reverse=reverse_order)
    else:
      return qs


class TableView(TemplateView):
  """
  view for table page

  :param template_name: template name
  :param referer_url: custom referer URL
  """

  template_name = 'fmm/table.html'
  referer_url = 'fmm:index'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    # add table related context elements
    context['objects_count'] = Fmf.objects.count()
    context['column_titles'] = list(TableDataView.columns.values())
    context['initial_order'] = [0, 'desc']
    context['tabledata_url'] = reverse('fmm:tabledata')
    # add custom referer URL to context
    context['referer_url'] = get_referer_url(
      referer=get_referer(self.request), fallback=self.referer_url
    )
    return context


class OverviewView(ObjectUpdateView):
  """
  view for overview page

  :param model: model
  :param template_name: template name
  """

  model = Fmf
  template_name = 'fmm/overview.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    fmf = self.object
    # compile the master data of the FMF and add it to context
    context['master_data'] = [
      {'label': 'ID', 'value': fmf.id},
      {'label': 'Erstellungszeitpunkt', 'value': format_date_datetime(fmf.created)},
      {'label': 'Änderungszeitpunkt', 'value': format_date_datetime(fmf.modified)},
      {'label': 'Bezeichnung', 'value': fmf.bezeichnung},
    ]
    # compile all Paket Umwelt data related to the FMF and add it to context
    if PaketUmwelt.objects.filter(fmf=fmf).exists():
      data_packages = []
      for package in PaketUmwelt.objects.filter(fmf=fmf).all():
        data_package = {
          'id': package.id,
          'created': format_date_datetime(package.created),
          'modified': format_date_datetime(package.modified),
          'update_url': reverse(viewname='fmm:paketumwelt_update', kwargs={'pk': package.id}),
          'delete_url': reverse(viewname='fmm:paketumwelt_delete', kwargs={'pk': package.id}),
          'items': [
            {
              'label': 'Trinkwassernotbrunnen',
              'value': format_boolean(package.trinkwassernotbrunnen),
            },
          ],
        }
        data_packages.append(data_package)
      context['data_packages_umwelt'] = data_packages
    return context
