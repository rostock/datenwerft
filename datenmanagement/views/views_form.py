from django.apps import apps
from django.contrib.messages import success
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db import connections
from django.forms.models import modelform_factory
from django.urls import reverse
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from json import dumps
from re import sub
from time import time

from datenmanagement.utils import get_field_name_for_address_type, get_thumb_url, \
  is_address_related_field, is_geometry_field
from .forms import GenericForm
from .functions import add_basic_model_context_elements, add_model_form_context_elements, \
  add_user_agent_context_elements, assign_widgets, set_form_attributes


class DataAddView(CreateView):
  """
  view for form page for creating an object of a model
  """

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.form_class = modelform_factory(
        self.model,
        form=GenericForm,
        fields='__all__',
        formfield_callback=assign_widgets
    )
    self.multi_foto_field = None
    self.multi_files = None
    self.file = None
    super().__init__(*args, **kwargs)

  def get_form_kwargs(self):
    """
    returns ``**kwargs`` as a dictionary with form attributes

    :return: ``**kwargs`` as a dictionary with form attributes
    """
    kwargs = super().get_form_kwargs()
    self = set_form_attributes(self)
    if self.model.BasemodelMeta.multi_foto_field and self.request.method == 'POST':
      self.multi_files = self.request.FILES
    if self.request.method == 'POST':
      self.file = self.request.FILES
    kwargs['request'] = self.request
    kwargs['model'] = self.model
    kwargs['fields_with_foreign_key_to_linkify'] = self.fields_with_foreign_key_to_linkify
    kwargs['choices_models_for_choices_fields'] = self.choices_models_for_choices_fields
    kwargs['group_with_users_for_choice_field'] = self.group_with_users_for_choice_field
    kwargs['multi_foto_field'] = self.model.BasemodelMeta.multi_foto_field
    kwargs['file'] = self.file
    kwargs['multi_files'] = self.multi_files
    return kwargs

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    model_name = self.model.__name__
    context = super().get_context_data(**kwargs)
    # add user agent related elements to context
    context = add_user_agent_context_elements(context, self.request)
    # add basic model related elements to context
    context = add_basic_model_context_elements(context, self.model)
    # add model form related elements to context
    context = add_model_form_context_elements(context, self.model)
    # add further elements to context
    context['multi_foto_field'] = self.model.BasemodelMeta.multi_foto_field
    context['url_back'] = reverse('datenmanagement:' + model_name + '_start')
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    ansprechpartner = None
    bearbeiter = None
    preselect_field = self.request.GET.get('preselect_field', None)
    preselect_value = self.request.GET.get('preselect_value', None)
    for field in self.model._meta.get_fields():
      if field.name == 'ansprechpartner':
        ansprechpartner = (
            self.request.user.first_name + ' '
            + self.request.user.last_name
            + ' (' + self.request.user.email.lower() + ')'
        )
      if field.name == 'bearbeiter':
        bearbeiter = (
            self.request.user.first_name + ' '
            + self.request.user.last_name
            + ' (' + self.request.user.email.lower() + ')'
        )
    if ansprechpartner or bearbeiter or (preselect_field and preselect_value):
      if not self.model.BasemodelMeta.group_with_users_for_choice_field:
        return {
            'ansprechpartner': ansprechpartner,
            'bearbeiter': bearbeiter,
            preselect_field: preselect_value
        }

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    form.instance.user = self.request.user
    success(
      self.request,
      'Der neue Datensatz <strong><em>%s</em></strong> '
      'wurde erfolgreich angelegt!' % str(form.instance)
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
    for field in self.model._meta.get_fields():
      # empty all array fields
      if field.__class__.__name__ == 'ArrayField':
        form.data[field.name] = None
      # keep address reference (otherwise it would be lost on re-rendering)
      elif is_address_related_field(field):
        field_name_for_address_type = get_field_name_for_address_type(self.model, False)
        context_data['current_' + field_name_for_address_type] = form.data.get(field.name, None)
        address = form.data.get(field.name + '_temp', None)
        form.data[field.name] = address
      # keep geometry (otherwise it would be lost on re-rendering)
      elif is_geometry_field(field.__class__):
        geometry = form.data.get(field.name, None)
        if geometry and '0,0' not in geometry and '[]' not in geometry:
          context_data['geometry'] = geometry
    context_data['form'] = form
    return self.render_to_response(context_data)


class DataChangeView(UpdateView):
  """
  view for form page for updating an object of a model
  """

  def __init__(self, model=None, *args, **kwargs):
    self.model = model
    self.form_class = modelform_factory(
        self.model,
        form=GenericForm,
        fields='__all__',
        formfield_callback=assign_widgets
    )
    self.file = None
    self.associated_objects = None
    self.associated_new = None
    self.associated_models = None
    super().__init__(*args, **kwargs)

  def get_form_kwargs(self):
    """
    returns ``**kwargs`` as a dictionary with form attributes

    :return: ``**kwargs`` as a dictionary with form attributes
    """
    kwargs = super().get_form_kwargs()
    self = set_form_attributes(self)
    self.associated_objects = None
    self.associated_new = None
    self.associated_models = self.model.BasemodelMeta.associated_models
    if self.request.method == 'POST':
      self.file = self.request.FILES
    kwargs['request'] = self.request
    kwargs['model'] = self.model
    kwargs['associated_objects'] = self.associated_objects
    kwargs['associated_new'] = self.associated_new
    kwargs['fields_with_foreign_key_to_linkify'] = self.fields_with_foreign_key_to_linkify
    kwargs['choices_models_for_choices_fields'] = self.choices_models_for_choices_fields
    kwargs['group_with_users_for_choice_field'] = self.group_with_users_for_choice_field
    kwargs['file'] = self.file
    # use associated models to provide corresponding links
    if self.associated_models:
      self.associated_new = []
      self.associated_objects = []
      for associated_model in self.associated_models:
        associated_model_model = apps.get_app_config('datenmanagement').get_model(associated_model)
        associated_model_foreign_key_field = self.associated_models.get(associated_model)
        title = ''
        if associated_model_model.BasemodelMeta.object_title:
          if associated_model_model.BasemodelMeta.foreign_key_label:
            foreign_key_label = associated_model_model.BasemodelMeta.foreign_key_label
          else:
            foreign_key_label = associated_model_model._meta.verbose_name
          title = (
            sub('^[a-z]{3} ', '', associated_model_model.BasemodelMeta.object_title) +
            ' zu ' + foreign_key_label
          )
        associated_new_dict = {
            'title': title,
            'link': reverse(
                'datenmanagement:' +
                associated_model +
                '_add') +
            '?preselect_field=' +
            associated_model_foreign_key_field +
            '&preselect_value=' +
            str(self.object.pk)
        }
        self.associated_new.append(associated_new_dict)
        curr_filter = {
            associated_model_foreign_key_field: self.object.pk
        }
        for associated_object in associated_model_model.objects.filter(**curr_filter):
          foto = associated_object.foto if hasattr(associated_object, 'foto') else None
          preview_img_url = ''
          preview_thumb_url = ''
          if foto:
            try:
              preview_img_url = foto.url + '?' + str(time())
              if associated_model_model.BasemodelMeta.thumbs:
                preview_thumb_url = get_thumb_url(foto.url) + '?' + str(time())
            except ValueError:
              pass
          associated_object_dict = {
              'title': title,
              'name': str(associated_object),
              'id': associated_object.pk,
              'link': reverse(
                  'datenmanagement:' + associated_model + '_change', args=[associated_object.pk]),
              'preview_img_url': preview_img_url,
              'preview_thumb_url': preview_thumb_url
          }
          self.associated_objects.append(associated_object_dict)
      kwargs['associated_objects'] = self.associated_objects
      kwargs['associated_new'] = self.associated_new
    return kwargs

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    model_name = self.model.__name__
    context = super().get_context_data(**kwargs)
    # add user agent related elements to context
    context = add_user_agent_context_elements(context, self.request)
    # add basic model related elements to context
    context = add_basic_model_context_elements(context, self.model)
    # add model form related elements to context
    context = add_model_form_context_elements(context, self.model)
    # add further elements to context
    context['associated_objects'] = self.associated_objects if self.associated_objects else None
    context['associated_new'] = self.associated_new if self.associated_new else None
    if self.model.BasemodelMeta.geometry_type:
      with connections['datenmanagement'].cursor() as cursor:
        cursor.execute(
            'SELECT ST_AsGeoJSON(ST_Transform(geometrie, 4326)) FROM ' +
            self.model._meta.db_table.replace('"', '') +
            ' WHERE UUID=%s;',
            [self.kwargs['pk']]
        )
        result = cursor.fetchone()[0]
        context['geometry'] = result
    else:
      context['geometry'] = None
    if self.model.BasemodelMeta.address_type:
      field_name_for_address_type = get_field_name_for_address_type(self.model, False)
      if field_name_for_address_type == 'adresse' and self.object.adresse:
        context['current_' + field_name_for_address_type] = self.object.adresse.pk
      elif field_name_for_address_type == 'strasse' and self.object.strasse:
        context['current_' + field_name_for_address_type] = self.object.strasse.pk
      elif field_name_for_address_type == 'gemeindeteil' and self.object.gemeindeteil:
        context['current_' + field_name_for_address_type] = self.object.gemeindeteil.pk
    # prepare a dictionary for all array fields and their contents that contain more than one value
    array_fields_values = {}
    for field in self.model._meta.get_fields():
      if field.__class__.__name__ == 'ArrayField':
        # read values
        values = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        # if more than one value...
        if values is not None and len(values) > 1:
          # compile the list for this field from all array contents starting from the second one
          array_field_values = values[1:]
          # if base field of array field is of type Date...
          if field.base_field.__class__.__name__ == 'DateField':
            # format list contents
            cleaned_array_field_values = []
            for array_field_value in array_field_values:
              cleaned_array_field_values.append(array_field_value.strftime('%Y-%m-%d'))
            array_field_values = cleaned_array_field_values
          # insert list into prepared dictionary
          array_fields_values[field.name] = array_field_values
    # create a new context and insert a JSON-serialized dictionary for all array fields
    # and their contents that contain more than one value
    context['array_fields_values'] = dumps(array_fields_values)
    context['url_back'] = reverse('datenmanagement:' + model_name + '_start')
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """
    # declare empty dictionary for initial field values in the view
    curr_dict = {}
    # if address, street or district exists...
    if self.model.BasemodelMeta.address_type:
      # add the appropriate initial field value for address, street or district to the dictionary
      field_name_for_address_type = get_field_name_for_address_type(self.model)
      if field_name_for_address_type == 'adresse' and self.object.adresse:
        curr_dict[field_name_for_address_type] = self.object.adresse
      elif field_name_for_address_type == 'strasse' and self.object.strasse:
        curr_dict[field_name_for_address_type] = self.object.strasse
      elif field_name_for_address_type == 'gemeindeteil' and self.object.gemeindeteil:
        curr_dict[field_name_for_address_type] = self.object.gemeindeteil
    for field in self.model._meta.get_fields():
      if field.__class__.__name__ == 'ArrayField':
        values = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        if values is not None and len(values) > 0 and values[0] is not None:
          # set initial value for this field to first array element
          # and add it to prepared dictionary
          initial_value = values[0]
          curr_dict[field.name] = initial_value
    return curr_dict

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    form.instance.user = self.request.user
    success(
      self.request,
      'Der Datensatz <strong><em>%s</em></strong> '
      'wurde erfolgreich geändert!' % str(form.instance)
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
    for field in self.model._meta.get_fields():
      # reset all array fields to their initial state
      if field.__class__.__name__ == 'ArrayField':
        values = getattr(self.model.objects.get(pk=self.object.pk), field.name)
        if values is not None and len(values) > 0 and values[0] is not None:
          form.data[field.name] = values[0]
        else:
          form.data[field.name] = values
      # keep address reference (otherwise it would be lost on re-rendering)
      elif is_address_related_field(field):
        field_name_for_address_type = get_field_name_for_address_type(self.model, False)
        context_data['current_' + field_name_for_address_type] = form.data.get(field.name, None)
        address = form.data.get(field.name + '_temp', None)
        form.data[field.name] = address
      # keep geometry (otherwise it would be lost on re-rendering)
      elif is_geometry_field(field.__class__):
        geometry = form.data.get(field.name, None)
        if geometry and '0,0' not in geometry and '[]' not in geometry:
          context_data['geometry'] = geometry
    context_data['form'] = form
    return self.render_to_response(context_data)

  def get_object(self, *args, **kwargs):
    """
    returns object to be changed;
    if rights are missing, a ``PermissionDenied()`` exception is thrown

    :param args:
    :param kwargs:
    :return: object to be changed
    """
    obj = super().get_object(*args, **kwargs)
    return obj


class DataDeleteView(SuccessMessageMixin, DeleteView):
  """
  view for form page for deleting an object of a model
  """

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return:
    """
    context = super().get_context_data(**kwargs)
    # add basic model related elements to context
    context = add_basic_model_context_elements(context, self.model)
    return context

  def get_object(self, *args, **kwargs):
    """
    returns object to be deleted;
    if rights are missing, a ``PermissionDenied()`` exception is thrown

    :param args:
    :param kwargs:
    :return: object to be deleted
    """
    obj = super().get_object(*args, **kwargs)
    if not self.request.user.has_perm('datenmanagement.delete_' + self.model.__name__.lower()):
      raise PermissionDenied()
    return obj

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    success(
      self.request,
      'Der Datensatz <strong><em>%s</em></strong> '
      'wurde erfolgreich gelöscht!' % str(self.object)
    )
    return super().form_valid(form)
