from datetime import datetime, timezone
from django.conf import settings
from django.contrib.messages import error, success
from django.db.models import ProtectedError, Q
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import escape
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView
from re import match, search, sub
from zoneinfo import ZoneInfo

from bemas.models import Codelist
from bemas.utils import get_icon_from_settings, is_bemas_admin, is_bemas_user
from .forms import CodelistForm
from .functions import add_codelist_context_elements, add_default_context_elements, \
  add_table_context_elements, add_user_agent_context_elements, assign_widget


class CodelistIndexView(TemplateView):
  """
  entry page for a codelist view

  :param model: codelist model
  """

  model = None
  template_name = 'bemas/codelist.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add default elements to context
    context = add_default_context_elements(context, self.request.user)
    # add other necessary elements to context
    context = add_codelist_context_elements(context, self.model)
    return context


class CodelistTableDataView(BaseDatatableView):
  """
  table data composition for a codelist view
  """

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.columns = self.model._meta.fields
    super().__init__(*args, **kwargs)

  def prepare_results(self, qs):
    """
    loops given queryset, creates cleaned-up JSON representation of the queryset and returns it

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
        for column in self.columns:
          data = None
          value = getattr(item, column.name)
          if value is not None:
            # format Booleans
            if isinstance(value, bool):
              data = ('ja' if value is True else 'nein')
            # format timestamps
            elif isinstance(value, datetime):
              value_tz = value.replace(tzinfo=timezone.utc).astimezone(
                ZoneInfo(settings.TIME_ZONE))
              data = value_tz.strftime('%d.%m.%Y, %H:%M Uhr')
            else:
              data = escape(value)
          item_data.append(data)
        # append links for updating and deleting
        if is_bemas_admin(self.request.user) or self.request.user.is_superuser:
          item_data.append(
            '<a href="' +
            reverse('bemas:codelists_' + self.model.__name__.lower() + '_update', args=[item_pk]) +
            '"><i class="fas fa-' + get_icon_from_settings('edit') +
            '" title="Codelisteneintrag bearbeiten"></i></a>' +
            '<a class="ms-3" href="' +
            reverse('bemas:codelists_' + self.model.__name__.lower() + '_delete', args=[item_pk]) +
            '"><i class="fas fa-' + get_icon_from_settings('delete') +
            '" title="Codelisteneintrag löschen"></i></a>'
          )
        json_data.append(item_data)
    return json_data

  def filter_queryset(self, qs):
    """
    filters given queryset

    :param qs: queryset
    :return: filtered queryset
    """
    current_search = self.request.GET.get('search[value]', None)
    if current_search:
      qs_params = None
      for search_element in current_search.lower().split():
        qs_params_inner = None
        for column in self.columns:
          case_a = search('^[0-9]{2}\\.[0-9]{2}\\.[0-9]{4}$', search_element)
          case_b = search('^[0-9]{2}\\.[0-9]{4}$', search_element)
          case_c = search('^[0-9]{2}\\.[0-9]{2}$', search_element)
          if case_a or case_b or case_c:
            search_element_splitted = search_element.split('.')
            kwargs = {
                '{0}__{1}'.format(column.name, 'icontains'): (search_element_splitted[
                    2] + '-' if case_a else '') +
                search_element_splitted[1] + '-' +
                search_element_splitted[0]
            }
          elif search_element == 'ja':
            kwargs = {
                '{0}__{1}'.format(column.name, 'icontains'): 'true'
            }
          elif search_element == 'nein' or search_element == 'nei':
            kwargs = {
                '{0}__{1}'.format(column.name, 'icontains'): 'false'
            }
          elif match(r"^[0-9]+,[0-9]+$", search_element):
            kwargs = {
                '{0}__{1}'.format(column.name, 'icontains'): sub(',', '.', search_element)
            }
          else:
            kwargs = {
                '{0}__{1}'.format(column.name, 'icontains'): search_element
            }
          q = Q(**kwargs)
          qs_params_inner = qs_params_inner | q if qs_params_inner else q
        qs_params = qs_params & qs_params_inner if qs_params else qs_params_inner
      qs = qs.filter(qs_params)
    return qs

  def ordering(self, qs):
    """
    sorts given queryset

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
      for column in self.columns:
        column_names.append(column.name)
      column_name = column_names[int(order_column)]
      directory = '-' if order_dir is not None and order_dir == 'desc' else ''
      return qs.order_by(directory + column_name)


class CodelistTableView(TemplateView):
  """
  table page for a codelist view

  :param model: codelist model
  """

  model = None
  template_name = 'bemas/codelist-table.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add default elements to context
    context = add_default_context_elements(context, self.request.user)
    # add table related elements to context
    context = add_table_context_elements(context, self.model)
    # add other necessary elements to context
    context = add_codelist_context_elements(context, self.model)
    return context


class CodelistCreateView(CreateView):
  """
  form page for creating a codelist view
  """

  template_name = 'bemas/codelist-form.html'

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.form_class = modelform_factory(
      self.model,
      form=CodelistForm,
      fields='__all__',
      formfield_callback=assign_widget
    )
    super().__init__(*args, **kwargs)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add default elements to context
    context = add_default_context_elements(context, self.request.user)
    # add user agent related elements to context
    context = add_user_agent_context_elements(context, self.request)
    # add other necessary elements to context
    context = add_codelist_context_elements(context, self.model)
    return context

  def form_valid(self, form):
    """
    sends HTTP response if given form is valid

    :param form: form
    :return: HTTP response if given form is valid
    """
    success(
      self.request,
      'Der neue Codelisteneintrag <strong><em>%s</em></strong> '
      'wurde erfolgreich angelegt!' % str(form.instance)
    )
    return super().form_valid(form)


class CodelistUpdateView(UpdateView):
  """
  form page for updating a codelist view
  """

  template_name = 'bemas/codelist-form.html'

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.form_class = modelform_factory(
      self.model,
      form=CodelistForm,
      fields='__all__',
      formfield_callback=assign_widget
    )
    super().__init__(*args, **kwargs)

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add default elements to context
    context = add_default_context_elements(context, self.request.user)
    # add user agent related elements to context
    context = add_user_agent_context_elements(context, self.request)
    # add other necessary elements to context
    context = add_codelist_context_elements(context, self.model)
    return context

  def form_valid(self, form):
    """
    sends HTTP response if given form is valid

    :param form: form
    :return: HTTP response if given form is valid
    """
    success(
      self.request,
      'Der Codelisteneintrag <strong><em>%s</em></strong> '
      'wurde erfolgreich geändert!' % str(form.instance)
    )
    return super().form_valid(form)


class CodelistDeleteView(DeleteView):
  """
  form page for deleting a codelist view
  """

  template_name = 'bemas/codelist-delete.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add default elements to context
    context = add_default_context_elements(context, self.request.user)
    # add user agent related elements to context
    context = add_user_agent_context_elements(context, self.request)
    # add other necessary elements to context
    context = add_codelist_context_elements(context, self.model)
    return context

  def form_valid(self, form):
    """
    sends HTTP response if given form is valid

    :param form: form
    :return: HTTP response if given form is valid
    """
    success_url = self.get_success_url()
    try:
      self.object.delete()
      success(
        self.request,
        'Der Codelisteneintrag <strong><em>%s</em></strong> '
        'wurde erfolgreich gelöscht!' % str(self.object)
      )
      return HttpResponseRedirect(success_url)
    except ProtectedError as exception:
      object_list = ''
      for protected_object in exception.protected_objects:
        object_list += ('<li>' if len(exception.protected_objects) > 1 else '')
        object_list += '<strong><em>' + str(protected_object) + '</em></strong> '
        if issubclass(protected_object.__class__, Codelist):
          object_list += 'aus Codeliste '
        else:
          object_list += 'aus Objektklasse '
        object_list += '<strong>' + protected_object._meta.verbose_name_plural + '</strong>'
        object_list += ('</li>' if len(exception.protected_objects) > 1 else '')
      if len(exception.protected_objects) > 1:
        object_reference_text = 'Folgende Objekte verweisen '
        object_list = '<ul class="error_object_list">' + object_list + '</ul>'
      else:
        object_reference_text = 'Folgendes Objekt verweist '
      error(
        self.request,
        'Der Codelisteneintrag <strong><em>' + str(self.object) + '</em></strong> '
        'kann nicht gelöscht werden! ' + object_reference_text + ' noch auf ihn:' +
        '<br><br>' + object_list
      )
      return self.render_to_response(self.get_context_data(form=form))
