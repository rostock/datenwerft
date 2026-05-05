from django.urls import reverse
from django.utils.html import escape
from django.views.generic.base import TemplateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from stadtbereichskatalog.models import Category
from stadtbereichskatalog.utils import get_icon_from_settings, is_stadtbereichskatalog_user
from toolbox.utils import optimize_datatable_filter

from .functions import (
  add_app_context_elements,
  add_model_context_elements,
  add_permissions_context_elements,
  add_useragent_context_elements,
  get_model_objects,
)


class TableDataView(BaseDatatableView):
  """
  generic view for composing table data out of instances of an object

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = None
  edit_view_name = ''

  def render_to_response(self, context):
    """
    returns a JSON response containing passed context as payload
    or an empty dictionary if no context is provided
    """
    if self.request.user.is_superuser or is_stadtbereichskatalog_user(self.request.user):
      return self.get_json_response(context)
    return self.get_json_response('{"has_necessary_permissions": false}')

  def get_initial_queryset(self):
    """
    loads initial queryset
    """
    if self.request.user.is_superuser or is_stadtbereichskatalog_user(self.request.user):
      return get_model_objects(self.model, False)
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
    if self.request.user.is_superuser or is_stadtbereichskatalog_user(self.request.user):
      for item in qs:
        item_data, item_pk = [], getattr(item, self.model._meta.pk.name)
        for column in self.model.ExtendedMeta.table_fields.keys():
          data = getattr(item, column)
          item_data.append(escape(data)) if data else item_data.append('')
        # append links
        links = '<a class="btn btn-sm btn-outline-warning" role="button" href="'
        links += reverse(self.edit_view_name, kwargs={'pk': item_pk})
        links += '"><i class="fa-solid fa-' + get_icon_from_settings('edit') + '"</i></a>'
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
        for search_column in list(self.model.ExtendedMeta.table_fields.keys()):
          # handle foreign keys
          if search_column == 'parent':
            search_column = search_column + str('__name')
          qs_params_inner = optimize_datatable_filter(
            search_element, search_column, qs_params_inner
          )
        qs_params = qs_params & qs_params_inner if qs_params else qs_params_inner
      qs = qs.filter(qs_params)
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
      value = getattr(x, column_name)

      # handle foreign keys
      if isinstance(value, Category):
        value = value.name

      return (value is None, value)

    # assume initial order since multiple column sorting is prohibited
    if self.request.GET.get('order[0][column]', None):
      order_column = self.request.GET.get('order[0][column]')
      order_dir = self.request.GET.get('order[0][dir]', None)
      column_name = list(self.model.ExtendedMeta.table_fields.keys())[int(order_column)]
      reverse_order = True if order_dir is not None and order_dir == 'desc' else False
      return sorted(qs, key=sort_key, reverse=reverse_order)
    else:
      return qs


class TableView(TemplateView):
  """
  generic view for table page for instances of an object

  :param model: model
  :param template_name: template name
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = None
  template_name = 'stadtbereichskatalog/table.html'
  table_data_view_name = None
  icon_name = None

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add global app related context elements
    context = add_app_context_elements(context)
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    # add table related context elements
    context['objects_count'] = get_model_objects(self.model, True)
    context['column_titles'] = list(self.model.ExtendedMeta.table_fields.values())
    context['tabledata_url'] = reverse(self.table_data_view_name)
    # add to context: icon
    context['icon'] = self.icon_name
    return context
