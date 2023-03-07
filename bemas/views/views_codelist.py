from django.contrib.messages import error, success
from django.db.models import ProtectedError
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import escape
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django_datatables_view.base_datatable_view import BaseDatatableView

from bemas.models import Codelist
from bemas.utils import get_icon_from_settings, is_bemas_admin
from .forms import CodelistForm
from .functions import add_codelist_context_elements, add_default_context_elements, \
  add_user_agent_context_elements, assign_widget


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
    self.pk_name = self.model._meta.pk.name
    super().__init__(*args, **kwargs)

  def prepare_results(self, qs):
    """
    loops given queryset, creates cleaned-up JSON representation of the queryset and returns it

    :param qs: queryset
    :return: cleaned-up JSON representation of the queryset
    """
    json_data = []
    for item in qs:
      item_data = []
      item_pk = getattr(item, self.pk_name)
      for column in self.columns:
        data = None
        value = getattr(item, column.name)
        if value is not None:
          # replace Python Booleans
          if value is True:
            data = 'ja'
          elif value is False:
            data = 'nein'
          else:
            data = escape(value)
        item_data.append(data)
      # append links for updating and deleting
      if is_bemas_admin(self.request.user) or self.request.user.is_superuser:
        item_data.append(
          '<a href="' +
          reverse('bemas:codelists_' + self.model.__name__ + '_update', args=[item_pk]) +
          '"><i class="fas fa-' + get_icon_from_settings('edit') +
          '" title="Codelisteneintrag bearbeiten"></i></a>'
        )
        item_data.append(
          '<a href="' +
          reverse('bemas:codelists_' + self.model.__name__ + '_delete', args=[item_pk]) +
          '"><i class="fas fa-' + get_icon_from_settings('delete') +
          '" title="Codelisteneintrag löschen"></i></a>'
        )
      json_data.append(item_data)
    return json_data


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
