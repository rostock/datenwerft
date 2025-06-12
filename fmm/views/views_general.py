from datetime import date, datetime

from django.urls import reverse
from django.views.generic.base import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from toolbox.utils import format_date_datetime

from ..models import Fmf
from ..utils import get_icon_from_settings, is_fmm_user
from .functions import (
  add_model_context_elements,
  add_permissions_context_elements,
  add_useragent_context_elements,
  get_fmf_queryset,
  get_referer,
  get_referer_url,
)


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

  :param model: model
  :param columns: table columns with names (as keys) and titles/headers (as values)
  """

  model = Fmf
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
    if is_fmm_user(self.request.user):
      return self.get_json_response(context)
    return self.get_json_response('{"has_necessary_permissions": false}')

  def get_initial_queryset(self):
    """
    loads initial queryset
    """
    if is_fmm_user(self.request.user):
      return get_fmf_queryset()
    return self.model.objects.none()

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
    if is_fmm_user(self.request.user):
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
        links += reverse(viewname='fmm:fmf_update', kwargs={'pk': item['id']})
        links += '"><i class="fas fa-' + get_icon_from_settings('show')
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

  :param model: model
  :param template_name: template name
  :param referer_url: custom referer URL
  """

  model = Fmf
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
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    # add table related context elements
    context['objects_count'] = self.model.objects.count()
    context['column_titles'] = list(TableDataView.columns.values())
    context['initial_order'] = [0, 'desc']
    context['tabledata_url'] = reverse('fmm:tabledata')
    # add custom referer URL to context
    context['referer_url'] = get_referer_url(
      referer=get_referer(self.request), fallback=self.referer_url
    )
    return context
