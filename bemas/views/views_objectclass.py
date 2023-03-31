from django.contrib.messages import error, success
from django.db.models import ProtectedError
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from json import dumps

from .forms import GenericForm
from .functions import add_default_context_elements, add_generic_objectclass_context_elements, \
  add_table_context_elements, add_user_agent_context_elements, assign_widget, \
  generate_protected_objects_list


class GenericObjectclassTableView(TemplateView):
  """
  generic table page for an object class view

  :param model: object class model
  """

  model = None
  template_name = 'bemas/generic-objectclass-table.html'

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
    context = add_generic_objectclass_context_elements(context, self.model)
    return context


class GenericObjectclassCreateView(CreateView):
  """
  generic form page for creating an instance of an object class view
  """

  template_name = 'bemas/generic-objectclass-form.html'

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
    context = add_generic_objectclass_context_elements(context, self.model)
    return context

  def form_valid(self, form):
    """
    sends HTTP response if given form is valid

    :param form: form
    :return: HTTP response if given form is valid
    """
    success(
      self.request,
      self.model.BasemodelMeta.definite_article.capitalize() + ' neue ' +
      self.model._meta.verbose_name + ' <strong><em>%s</em></strong> '
      'wurde erfolgreich angelegt!' % str(form.instance)
    )
    return super().form_valid(form)


class GenericObjectclassUpdateView(UpdateView):
  """
  generic form page for updating an instance of an object class view
  """

  template_name = 'bemas/generic-objectclass-form.html'

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
    context = add_generic_objectclass_context_elements(context, self.model)
    # handle array fields and their values
    # (i.e. those array fields containing more than one value)
    array_fields_values = {}
    for field in self.model._meta.get_fields():
      if field.__class__.__name__ == 'ArrayField':
        values = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        if values is not None and len(values) > 1:
          # create a list starting from second array element
          # and add it to prepared dictionary
          array_field_values = values[1:]
          array_fields_values[field.name] = array_field_values
    # JSON serialize dictionary with array fields and their values
    # (i.e. with those array fields containing more than one value)
    # and add it to context
    if array_fields_values:
      context['array_fields_values'] = dumps(array_fields_values)
    return context

  def get_initial(self):
    """
    sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    initial_field_values = {}
    for field in self.model._meta.get_fields():
      # handle array fields and their values
      # (i.e. those array fields containing at least one value)
      if field.__class__.__name__ == 'ArrayField':
        values = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        if values is not None and len(values) > 0 and values[0] is not None:
          # set initial value for this field to first array element
          # and add it to prepared dictionary
          initial_field_value = values[0]
          initial_field_values[field.name] = initial_field_value
    return initial_field_values

  def form_valid(self, form):
    """
    sends HTTP response if given form is valid

    :param form: form
    :return: HTTP response if given form is valid
    """
    success(
      self.request,
      self.model.BasemodelMeta.definite_article.capitalize() + ' ' +
      self.model._meta.verbose_name + ' <strong><em>%s</em></strong> '
      'wurde erfolgreich geändert!' % str(form.instance)
    )
    return super().form_valid(form)

  def form_invalid(self, form, **kwargs):
    """
    re-opens given form if it is not valid
    (purpose: reset non-valid array fields to their initial state)

    :param form: form
    :return: given form if it is not valid
    """
    context_data = self.get_context_data(**kwargs)
    form.data = form.data.copy()
    # reset all array fields to their initial state
    for field in self.model._meta.get_fields():
      if field.__class__.__name__ == 'ArrayField':
        values = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        if values is not None and len(values) > 0 and values[0] is not None:
          form.data[field.name] = values[0]
        else:
          form.data[field.name] = values
    context_data['form'] = form
    return self.render_to_response(context_data)


class GenericObjectclassDeleteView(DeleteView):
  """
  generic form page for deleting an instance of an object class view
  """

  template_name = 'bemas/generic-objectclass-delete.html'

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
    context = add_generic_objectclass_context_elements(context, self.model)
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
        self.model.BasemodelMeta.definite_article.capitalize() + ' ' +
        self.model._meta.verbose_name + ' <strong><em>%s</em></strong> '
        'wurde erfolgreich gelöscht!' % str(self.object)
      )
      return HttpResponseRedirect(success_url)
    except ProtectedError as exception:
      error(
        self.request,
        self.model.BasemodelMeta.definite_article.capitalize() + ' ' +
        self.model._meta.verbose_name + ' <strong><em>' + str(self.object) +
        '</em></strong> kann nicht gelöscht werden! Folgende(s) Objekt(e) verweist/verweisen '
        'noch auf ' + self.model.BasemodelMeta.personal_pronoun + ':<br><br>' +
        generate_protected_objects_list(exception.protected_objects)
      )
      return self.render_to_response(self.get_context_data(form=form))
