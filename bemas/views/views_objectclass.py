from django.contrib.gis.db.models.functions import AsGeoJSON
from django.contrib.messages import error, success
from django.db.models import ProtectedError
from django.forms.models import modelform_factory
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views.generic.base import TemplateView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from json import dumps

from bemas.models import GeometryObjectclass, Complaint, Contact, Event, LogEntry, Organization, \
  Originator, Sector, Status
from .forms import GenericForm
from .functions import add_default_context_elements, add_generic_objectclass_context_elements, \
  add_sector_examples_context_element, add_table_context_elements, assign_widget, \
  create_log_entry, generate_foreign_key_objects_list, \
  set_generic_objectclass_create_update_delete_context, set_log_action_and_content
from bemas.utils import generate_user_string, shorten_string


class GenericObjectclassTableView(TemplateView):
  """
  view for generic table page for an object class

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
    context = add_table_context_elements(context, self.model, self.kwargs)
    # add other necessary elements to context
    context = add_generic_objectclass_context_elements(context, self.model)
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
    # set generic object class context for create, update and/or delete views
    context = set_generic_objectclass_create_update_delete_context(
      super().get_context_data(**kwargs),
      self.request,
      self.model,
      self.cancel_url
    )
    # object class originator:
    # add list of sector examples to context
    if issubclass(self.model, Originator):
      context = add_sector_examples_context_element(context, Sector)
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    initial_field_values = {}
    # object class contact:
    # optionally set initial value for organization field
    if issubclass(self.model, Contact) and self.request.GET.get('organization', None):
      initial_field_values['organization'] = self.request.GET.get('organization')
    # object class event:
    elif issubclass(self.model, Event):
      # optionally set initial value for complaint field
      if self.request.GET.get('complaint', None):
        initial_field_values['complaint'] = self.request.GET.get('complaint')
      # pre-select current user as user for a new event
      initial_field_values['user'] = generate_user_string(self.request.user)
    else:
      for field in self.model._meta.get_fields():
        # handle date fields and their values
        if field.__class__.__name__ == 'DateField':
          initial_field_values[field.name] = field.get_default().strftime('%Y-%m-%d')
        # set default status for a new complaint
        elif issubclass(self.model, Complaint) and field.name == 'status':
          initial_field_values['status'] = Status.get_default_status()
    return initial_field_values

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    # string representation of new complaint equals its primary key
    # (which is not yet available) and thus use its description here
    if issubclass(self.model, Complaint):
      obj_str = shorten_string(form.instance.description)
    else:
      obj_str = str(form.instance)
    success(
      self.request,
      '{} neue {} <strong><em>{}</em></strong> wurde erfolgreich angelegt!'.format(
        self.model.BasemodelMeta.definite_article.capitalize(),
        self.model._meta.verbose_name,
        obj_str
      )
    )
    # create new log entry (except for object class log entry itself, of course)
    if not issubclass(self.model, LogEntry):
      curr_object = form.save(commit=False)
      curr_object.save()
      create_log_entry(
        self.model,
        curr_object.pk,
        'created',
        str(curr_object),
        self.request.user
      )
    return super().form_valid(form)

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: empty non-valid array fields)

    :param form: form
    :return: passed form if it is not valid
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
    # set generic object class context for create, update and/or delete views
    context = set_generic_objectclass_create_update_delete_context(
      super().get_context_data(**kwargs),
      self.request,
      self.model,
      self.cancel_url,
      self.object
    )
    # optionally add log entries link
    if not issubclass(self.model, LogEntry):
      context['objectclass_logentry_url'] = reverse(
        'bemas:logentry_table_model_object',
        args=[self.model.__name__, self.object.pk]
      )
    # object class organization:
    # optionally add list of contacts to context
    if issubclass(self.model, Organization):
      contacts = Organization.objects.get(pk=self.object.pk).contact_set.all()
      if contacts:
        contacts_list = []
        for contact in contacts:
          contact_dict = {
            'link': reverse('bemas:contact_update', args=[contact.pk]),
            'text': contact.name_and_function()
          }
          contacts_list.append(contact_dict)
        context['contacts'] = contacts_list
    # object class complaint:
    # optionally add list of events to context
    elif issubclass(self.model, Complaint):
      events = Event.objects.filter(complaint=self.object.pk)
      if events:
        events_list = []
        for event in events:
          event_dict = {
            'link': reverse('bemas:event_update', args=[event.pk]),
            'text': event.type_of_event_and_created_at()
          }
          events_list.append(event_dict)
        context['events'] = events_list
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
    # if object class contains geometry:
    # GeoJSONify geometry and add it to context
    if issubclass(self.model, GeometryObjectclass):
      geometry = getattr(self.object, self.model.BasemodelMeta.geometry_field)
      if geometry:
        geometry = self.model.objects.annotate(
          geojson=AsGeoJSON(geometry)
        ).get(pk=self.object.pk).geojson
      context['geometry'] = geometry
    # object class originator:
    # add list of sector examples to context
    if issubclass(self.model, Originator):
      context = add_sector_examples_context_element(context, Sector)
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
      # handle date fields and their values
      elif field.__class__.__name__ == 'DateField':
        value = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        initial_field_values[field.name] = value.strftime('%Y-%m-%d')
    return initial_field_values

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    success(
      self.request,
      '{} {} <strong><em>{}</em></strong> wurde erfolgreich geändert!'.format(
        self.model.BasemodelMeta.definite_article.capitalize(),
        self.model._meta.verbose_name,
        str(form.instance)
      )
    )
    if form.has_changed():
      # create new log entry for the following object classes:
      # Complaint, Originator
      if (
          issubclass(self.model, Complaint)
          or issubclass(self.model, Originator)
      ):
        curr_object = form.save(commit=False)
        curr_object.save()
        # loop changed data in order to create individual log entries
        for changed_attribute in form.changed_data:
          log_action, content = set_log_action_and_content(
            self.model, curr_object, changed_attribute, form.cleaned_data)
          if log_action and content:
            create_log_entry(
              self.model,
              curr_object.pk,
              log_action,
              content,
              self.request.user
            )
    return super().form_valid(form)

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: reset non-valid array fields to their initial state)

    :param form: form
    :return: passed form if it is not valid
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
    # set generic object class context for create, update and/or delete views
    context = set_generic_objectclass_create_update_delete_context(
      super().get_context_data(**kwargs),
      self.request,
      self.model,
      self.cancel_url
    )
    # optionally add log entries link
    if not issubclass(self.model, LogEntry):
      context['objectclass_logentry_url'] = reverse(
        'bemas:logentry_table_model_object',
        args=[self.model.__name__, self.object.pk]
      )
    # optionally add custom deletion hints (shown as text to user) to context
    if self.deletion_hints:
      context['deletion_hints'] = self.deletion_hints
    return context

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    success_url = self.get_success_url()
    try:
      object_pk, content = self.object.pk, str(self.object)
      self.object.delete()
      success(
        self.request,
        '{} {} <strong><em>{}</em></strong> wurde erfolgreich gelöscht!'.format(
          self.model.BasemodelMeta.definite_article.capitalize(),
          self.model._meta.verbose_name,
          str(self.object)
        )
      )
      # create new log entry (except for object class log entry itself, of course)
      if not issubclass(self.model, LogEntry):
        create_log_entry(
          self.model,
          object_pk,
          'deleted',
          content,
          self.request.user
        )
      return HttpResponseRedirect(success_url)
    except ProtectedError as exception:
      error(
        self.request,
        self.model.BasemodelMeta.definite_article.capitalize() + ' ' +
        self.model._meta.verbose_name + ' <strong><em>' + str(self.object) +
        '</em></strong> kann nicht gelöscht werden! Folgende(s) Objekt(e) verweist/verweisen '
        'noch auf ' + self.model.BasemodelMeta.personal_pronoun + ':<br><br>' +
        generate_foreign_key_objects_list(exception.protected_objects)
      )
      return self.render_to_response(self.get_context_data(form=form))


class OrganizationDeleteView(GenericObjectclassDeleteView):
  """
  view for form page for deleting an instance of object class organization
  """

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    # list persons of linked contacts (if any) which will automatically be deleted
    self.deletion_hints = []
    contacts = self.object.contact_set.all()
    if contacts:
      deletion_hint = 'Es werden automatisch auch alle Ansprechpartner:innen-Verbindungen ' \
                      'mit folgender/folgenden Person(en) gelöscht:<br><br>'
      deletion_hint += generate_foreign_key_objects_list(contacts, 'person')
      self.deletion_hints.append(deletion_hint)
    # list linked complaints (if any) which will automatically be unlinked
    complaints = Complaint.objects.filter(complainers_organizations__id=self.object.pk)
    if complaints:
      deletion_hint = 'Es werden automatisch auch alle Verbindungen als Beschwerdeführerin ' \
                      'mit folgender/folgenden Beschwerden(n) gelöst:<br><br>'
      deletion_hint += generate_foreign_key_objects_list(complaints)
      self.deletion_hints.append(deletion_hint)
    # set generic object class context for this view
    context = set_generic_objectclass_create_update_delete_context(
      super().get_context_data(**kwargs),
      self.request,
      self.model,
      self.cancel_url
    )
    # add custom deletion hints (shown as text to user) to context
    context['deletion_hints'] = self.deletion_hints
    return context


class PersonDeleteView(GenericObjectclassDeleteView):
  """
  view for form page for deleting an instance of object class person
  """

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    # list organizations of linked contacts (if any) which will automatically be deleted
    self.deletion_hints = []
    contacts = self.object.contact_set.all()
    if contacts:
      deletion_hint = 'Es werden automatisch auch alle Ansprechpartner:innen-Verbindungen ' \
                      'mit folgender/folgenden Organisation(en) gelöscht:<br><br>'
      deletion_hint += generate_foreign_key_objects_list(contacts, 'organization')
      self.deletion_hints.append(deletion_hint)
    # list linked complaints (if any) which will automatically be unlinked
    complaints = Complaint.objects.filter(complainers_persons__id=self.object.pk)
    if complaints:
      deletion_hint = 'Es werden automatisch auch alle Verbindungen als Beschwerdeführer:in ' \
                      'mit folgender/folgenden Beschwerden(n) gelöst:<br><br>'
      deletion_hint += generate_foreign_key_objects_list(complaints)
      self.deletion_hints.append(deletion_hint)
    # set generic object class context for this view
    context = set_generic_objectclass_create_update_delete_context(
      super().get_context_data(**kwargs),
      self.request,
      self.model,
      self.cancel_url
    )
    # add custom deletion hints (shown as text to user) to context
    context['deletion_hints'] = self.deletion_hints
    return context


class ComplaintDeleteView(GenericObjectclassDeleteView):
  """
  view for form page for deleting an instance of object class complaint
  """

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    # list linked events (if any) which will automatically be deleted
    self.deletion_hints = []
    events = self.object.event_set.all()
    if events:
      deletion_hint = 'Es werden automatisch auch alle Journalereignisse ' \
                      'zu dieser Beschwerde gelöscht:<br><br>'
      deletion_hint += generate_foreign_key_objects_list(events)
      self.deletion_hints.append(deletion_hint)
    # set generic object class context for this view
    context = set_generic_objectclass_create_update_delete_context(
      super().get_context_data(**kwargs),
      self.request,
      self.model,
      self.cancel_url
    )
    # add custom deletion hints (shown as text to user) to context
    context['deletion_hints'] = self.deletion_hints
    return context


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
