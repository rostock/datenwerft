from django.contrib.messages import success
from django.db.models import ForeignKey
from django.forms.models import modelform_factory
from django.urls import reverse
from django.utils.html import escape
from django.views.generic.base import TemplateView
from django.views.generic.edit import UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from stadtbereichskatalog.utils import get_icon_from_settings, is_stadtbereichskatalog_user
from toolbox.utils import optimize_datatable_filter

from ..apps import StadtbereichskatalogConfig as appConfig
from .forms import MetadataForm
from .functions import (
  add_app_context_elements,
  add_model_context_elements,
  add_permissions_context_elements,
  assign_widget,
  get_model_objects,
)


class MetadataTableDataView(BaseDatatableView):
  """
  generic view for composing table data out of instances of a metadata model class

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
          data, value = None, getattr(item, column)
          # handle booleans
          if isinstance(value, bool):
            data = 'ja' if value else 'nein'
          elif value is not None:
            data = escape(value)
          else:
            data = ''
          item_data.append(data)
        # append links
        links = '<a class="btn btn-sm btn-warning" role="button" href="'
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
        for column in list(self.model.ExtendedMeta.table_fields.keys()):
          # handle foreign keys
          if issubclass(self.model._meta.get_field(column).__class__, ForeignKey):
            column = column + str('__name')
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
    if self.request.GET.get('order[0][column]', None):
      order_column = self.request.GET.get('order[0][column]')
      order_dir = self.request.GET.get('order[0][dir]', None)
      columns = []
      for column in list(self.model.ExtendedMeta.table_fields.keys()):
        # handle foreign keys
        if issubclass(self.model._meta.get_field(column).__class__, ForeignKey):
          column = column + str('__name')
        columns.append(column)
      column = columns[int(order_column)]
      direction = '-' if order_dir is not None and order_dir == 'desc' else ''
      return qs.order_by(direction + column)
    else:
      return qs


class MetadataTableView(TemplateView):
  """
  generic view for table page for instances of a metadata model class

  :param model: model
  :param template_name: template name
  :param table_data_view_name: name of view for composing table data
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


class MetadataMixin:
  """
  generic mixin for form page for editing an instance of a metadata model class

  :param model: model
  :param template_name: template name
  :param form: form
  :param success_message: custom success message
  :param cancel_url: custom cancel URL
  """

  model = None
  template_name = 'stadtbereichskatalog/form.html'
  form = MetadataForm
  success_message = ''
  cancel_url = None

  def get_form_class(self):
    # ensure the model is set before creating the form class
    if not self.model:
      raise ValueError('The model attribute must be set before calling get_form_class.')
    # dynamically create the form class
    form_class = modelform_factory(
      self.model, form=self.form, fields='__all__', formfield_callback=assign_widget
    )
    return form_class

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    success(
      self.request, self.success_message.format(self.model._meta.verbose_name, str(form.instance))
    )
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add global app related context elements
    context = add_app_context_elements(context)
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    # add to context: URLs
    if self.cancel_url:
      context['cancel_url'] = reverse(self.cancel_url)
    else:
      context['cancel_url'] = reverse(f'{appConfig.name}:index')
    return context


class MetadataEditView(MetadataMixin, UpdateView):
  """
  generic view for form page for editing an instance of a metadata model class

  :param success_message: custom success message
  """

  success_message = '{} <strong><em>{}</em></strong> erfolgreich aktualisiert!'
