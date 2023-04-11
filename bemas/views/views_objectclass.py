from django.contrib.messages import error, success
from django.db.models import ProtectedError
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from json import dumps

from bemas.models import Contact, Organization
from .forms import GenericForm
from .functions import add_default_context_elements, add_generic_objectclass_context_elements, \
  add_table_context_elements, add_user_agent_context_elements, assign_widget, \
  generate_protected_objects_list


class GenericObjectclassTableView(TemplateView):
  """
  view for generic table page for an object class

  :param model: object class model
  :param further_objectclass_name: name of further object class accessible via creation button
  :param further_objectclass_button_text: text for creation button of further object class
  """

  model = None
  template_name = 'bemas/generic-objectclass-table.html'
  further_objectclass_name = None
  further_objectclass_button_text = None

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
    # optionally add name of object class additionally addable via button
    # and the corresponding button text to context
    if self.further_objectclass_name and self.further_objectclass_button_text:
      context['further_objectclass_name'] = self.further_objectclass_name
      context['further_objectclass_button_text'] = self.further_objectclass_button_text
    return context


class GenericObjectclassCreateView(CreateView):
  """
  view for generic form page for creating an instance of an object class

  :param cancel_url: custom cancel URL
  """

  template_name = 'bemas/generic-objectclass-form.html'
  cancel_url = None

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
    # optionally add custom cancel URL (called when cancel button is clicked) to context
    if self.cancel_url:
      context['cancel_url'] = self.cancel_url
    else:
      context['cancel_url'] = reverse('bemas:' + self.model.__name__.lower() + '_table')
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

  def form_invalid(self, form, **kwargs):
    """
    re-opens given form if it is not valid
    (purpose: empty non-valid array fields)

    :param form: form
    :return: given form if it is not valid
    """
    context_data = self.get_context_data(**kwargs)
    form.data = form.data.copy()
    # empty all array fields
    for field in self.model._meta.get_fields():
      if field.__class__.__name__ == 'ArrayField':
        form.data[field.name] = None
    context_data['form'] = form
    return self.render_to_response(context_data)


class GenericObjectclassUpdateView(UpdateView):
  """
  view for generic form page for updating an instance of an object class

  :param cancel_url: custom cancel URL
  """

  template_name = 'bemas/generic-objectclass-form.html'
  cancel_url = None

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
    # optionally add custom cancel URL (called when cancel button is clicked) to context
    if self.cancel_url:
      context['cancel_url'] = self.cancel_url
    else:
      context['cancel_url'] = reverse('bemas:' + self.model.__name__.lower() + '_table')
    # object class organization:
    # optionally add list of contacts to context
    if issubclass(self.model, Organization):
      contacts = Contact.objects.filter(organization=self.object.pk)
      if contacts:
        contacts_list = []
        for contact in contacts:
          contact_dict = {
            'link': reverse('bemas:contact_update', args=[contact.pk]),
            'text': str(contact.person) + (
              ' (Funktion: ' + contact.function + ')' if contact.function else ''
            )
          }
          contacts_list.append(contact_dict)
        context['contacts'] = contacts_list
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
  view for generic form page for deleting an instance of an object class

  :param cancel_url: custom cancel URL
  :param deletion_hints: custom deletion hints
  """

  template_name = 'bemas/generic-objectclass-delete.html'
  cancel_url = None
  deletion_hints = None

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
    # optionally add custom cancel URL (called when cancel button is clicked) to context
    if self.cancel_url:
      context['cancel_url'] = self.cancel_url
    else:
      context['cancel_url'] = reverse('bemas:' + self.model.__name__.lower() + '_table')
    # optionally add custom deletion hints (shown as text to user) to context
    if self.deletion_hints:
      context['deletion_hints'] = self.deletion_hints
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


class OrganizationTableView(GenericObjectclassTableView):
  """
  view for table page for object class organization

  :param further_objectclass_name: name of further object class accessible via creation button
  :param further_objectclass_button_text: text for creation button of further object class
  """

  further_objectclass_name = 'contact'
  further_objectclass_button_text = 'neue:n Ansprechpartner:in anlegen'


class OrganizationDeleteView(GenericObjectclassDeleteView):
  """
  view for form page for deleting an instance of object class organization

  :param deletion_hints: custom deletion hints
  """

  deletion_hints = 'Es werden automatisch auch alle ' \
                   'Ansprechpartner:innen-Verknüpfungen mit Personen gelöscht.'


class PersonDeleteView(GenericObjectclassDeleteView):
  """
  view for form page for deleting an instance of object class person

  :param deletion_hints: custom deletion hints
  """

  deletion_hints = 'Es werden automatisch auch alle ' \
                   'Ansprechpartner:innen-Verknüpfungen mit Organisationen gelöscht.'


class ContactCreateView(GenericObjectclassCreateView):
  """
  view for form page for creating an instance of object class contact

  :param cancel_url: custom cancel URL
  """

  cancel_url = reverse_lazy('bemas:organization_table')


class ContactUpdateView(GenericObjectclassUpdateView):
  """
  view for form page for updating an instance of object class contact

  :param cancel_url: custom cancel URL
  """

  cancel_url = reverse_lazy('bemas:organization_table')


class ContactDeleteView(GenericObjectclassDeleteView):
  """
  view for form page for deleting an instance of object class contact

  :param cancel_url: custom cancel URL
  """

  cancel_url = reverse_lazy('bemas:organization_table')
