from datetime import date, datetime
from django.contrib.messages import success
from django.forms.models import modelform_factory
from django.urls import reverse
from django.utils.html import escape
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from .forms import ObjectForm
from .functions import add_model_context_elements, \
  add_table_context_elements, add_useragent_context_elements, assign_widget, get_model_objects
from antragsmanagement.constants_vars import REQUESTERS, AUTHORITIES, ADMINS
from antragsmanagement.utils import get_icon_from_settings, has_necessary_permissions, \
  is_antragsmanagement_user
from toolbox.utils import format_date_datetime, optimize_datatable_filter


class ObjectTableDataView(BaseDatatableView):
  """
  generic view for composing table data out of instances of an object

  :param model: model
  :param update_view_name: name of view for form page for updating
  :param permissions_level: permissions level user has to have
  """

  model = None
  update_view_name = ''
  permissions_level = ''

  @staticmethod
  def check_necessary_permissions(user, permissions_level):
    """
    checks if passed user has necessary permissions

    :param user: user
    :param permissions_level: permissions level passed user has to have
    (if empty, check if  passed user is an Antragsmanagement user at least)
    :return: passed user has necessary permissions?
    """
    necessary_permissions = user.is_superuser
    if not necessary_permissions:
      if permissions_level:
        permissions_map = {
          'REQUESTERS': REQUESTERS,
          'AUTHORITIES': AUTHORITIES,
          'ADMINS': ADMINS
        }
        check_group = permissions_map.get(permissions_level)
        if check_group:
          necessary_permissions = has_necessary_permissions(user, check_group)
      else:
        necessary_permissions = is_antragsmanagement_user(user)
    return necessary_permissions

  def render_to_response(self, context):
    """
    returns a JSON response containing passed context as payload
    or an empty dictionary if no context is provided
    """
    if self.check_necessary_permissions(self.request.user, self.permissions_level):
      return self.get_json_response(context)
    return self.get_json_response('{"has_necessary_permissions": false}')

  def get_initial_queryset(self):
    """
    loads initial queryset
    """
    if self.check_necessary_permissions(self.request.user, self.permissions_level):
      return get_model_objects(self.model, False)
    return self.model.objects.none()

  def prepare_results(self, qs):
    """
    loops passed queryset, creates cleaned-up JSON representation of the queryset and returns it

    :param qs: queryset
    :return: cleaned-up JSON representation of the queryset
    """
    json_data = []
    if self.check_necessary_permissions(self.request.user, self.permissions_level):
      for item in qs:
        item_data, item_pk, address_handled = [], getattr(item, self.model._meta.pk.name), False
        for column in self.model._meta.fields:
          data = None
          value = getattr(item, column.name)
          # "icon" columns
          if column.name == 'icon':
            item_data.append('<i class="fas fa-{}"></i>'.format(value))
          # address related columns
          elif column.name.startswith('address_') and not address_handled:
            # append address string only once
            # instead of appending individual strings for all address related values
            data = self.model.objects.get(pk=item_pk).address()
            address_handled = True
            item_data.append(data)
          # ordinary columns
          elif not column.name.startswith('address_'):
            if value is not None:
              # format dates and datetimes
              if isinstance(value, date) or isinstance(value, datetime):
                data = format_date_datetime(value)
              else:
                data = escape(value)
            item_data.append(data)
        # append link for updating
        permission_suffix = self.model.__name__.lower()
        if (
            self.request.user.has_perm('antragsmanagement.view_' + permission_suffix)
            or self.request.user.has_perm('antragsmanagement.change_' + permission_suffix)
        ):
          link = '<a href="'
          link += reverse(self.update_view_name, kwargs={'pk': item_pk})
          link += '"><i class="fas fa-' + get_icon_from_settings('update')
          link += '" title="' + self.model._meta.verbose_name
          link += ' ansehen oder bearbeiten"></i></a>'
          item_data.append(link)
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
        for column in self.model._meta.fields:
          search_column = column.name
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
    if self.request.GET.get('order[0][column]', None):
      order_column = self.request.GET.get('order[0][column]')
      order_dir = self.request.GET.get('order[0][dir]', None)
      column_names = []
      # careful here! use the same clauses as in prepare_results() above since otherwise,
      # the wrong order columns could be chosen
      address_handled = False
      for column in self.model._meta.fields:
        # handle addresses
        if column.name.startswith('address_') and not address_handled:
          # append one column for address string
          # instead of appending individual columns for all address related values
          column_names.append(column.name)
          address_handled = True
        # ordinary columns
        elif not column.name.startswith('address_'):
          column_names.append(column.name)
      column_name = column_names[int(order_column)]
      direction = '-' if order_dir is not None and order_dir == 'desc' else ''
      return qs.order_by(direction + column_name)
    else:
      return qs


class ObjectTableView(TemplateView):
  """
  generic view for table page for instances of an object

  :param model: model
  :param template_name: template name
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = None
  template_name = 'antragsmanagement/table_simple.html'
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
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    # add table related context elements
    context = add_table_context_elements(context, self.model, self.table_data_view_name)
    # add to context: icon
    context['icon'] = self.icon_name
    return context


class ObjectMixin:
  """
  generic mixin for form page for creating or updating an instance of an object

  :param model: model
  :param template_name: template name
  :param form: form
  :param success_message: custom success message
  :param cancel_url: custom cancel URL
  """

  model = None
  template_name = 'antragsmanagement/form_simple.html'
  form = ObjectForm
  success_message = ''
  cancel_url = None

  def get_form_class(self):
    # ensure the model is set before creating the form class
    if not self.model:
      raise ValueError('The model attribute must be set before calling get_form_class.')
    # dynamically create the form class
    form_class = modelform_factory(
      self.model,
      form=self.form,
      fields='__all__',
      formfield_callback=assign_widget
    )
    return form_class

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    success(
      self.request,
      self.success_message.format(self.model._meta.verbose_name, str(form.instance))
    )
    return super().form_valid(form)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add user agent related context elements
    context = add_useragent_context_elements(context, self.request)
    # add model related context elements
    context = add_model_context_elements(context, self.model)
    # add to context: URLs
    if self.cancel_url:
      context['cancel_url'] = reverse(self.cancel_url)
    else:
      context['cancel_url'] = reverse('antragsmanagement:index')
    return context


class ObjectCreateView(ObjectMixin, CreateView):
  """
  generic view for form page for creating an instance of an object

  :param success_message: custom success message
  """

  success_message = '{} <strong><em>{}</em></strong> erfolgreich gespeichert!'


class ObjectUpdateView(ObjectMixin, UpdateView):
  """
  generic view for form page for updating an instance of an object

  :param success_message: custom success message
  """

  success_message = '{} <strong><em>{}</em></strong> erfolgreich aktualisiert!'
