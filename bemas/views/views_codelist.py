from django.contrib.messages import error, success
from django.db.models import ProtectedError
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

from .base import GenericTableDataView
from .forms import GenericForm
from .functions import add_codelist_context_elements, add_default_context_elements, \
  add_table_context_elements, add_user_agent_context_elements, assign_widget, \
  generate_protected_objects_list


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


class CodelistTableDataView(GenericTableDataView):
  """
  table data composition for a codelist view
  """
  pass


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
  form page for creating a codelist instance view
  """

  template_name = 'bemas/codelist-form.html'

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.form_class = modelform_factory(
      self.model,
      form=GenericForm,
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
  form page for updating a codelist instance view
  """

  template_name = 'bemas/codelist-form.html'

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.form_class = modelform_factory(
      self.model,
      form=GenericForm,
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
  form page for deleting a codelist instance view
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
      error(
        self.request,
        'Die/der ' + self.model._meta.verbose_name + ' <strong><em>' + str(self.object) +
        '</em></strong> kann nicht gelöscht werden! Folgende(s) Objekt(e) verweist/verweisen '
        'noch auf ihn:<br><br>' + generate_protected_objects_list(exception.protected_objects)
      )
      return self.render_to_response(self.get_context_data(form=form))
