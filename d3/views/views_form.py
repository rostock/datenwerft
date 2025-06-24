from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import success
from django.contrib.messages import error
from django.forms.models import modelform_factory
from django.shortcuts import redirect
from django.views.generic.edit import CreateView

from d3.models import Vorgang
from d3.utils import lade_akten_ordner, lade_akte
from d3.views.forms import VorgangForm
from datenmanagement.utils import (
  get_field_name_for_address_type,
  is_address_related_field,
)
from datenmanagement.views import get_url_back, set_form_attributes, GenericForm
from toolbox.utils import is_geometry_field


class DataAddView(CreateView):

  model = Vorgang
  datenmanagement_model = ''
  object_id = ''

  """
  view for form page for creating an object of a model
  """

  def __init__(self, model=None, *args, **kwargs):

    self.datenmanagement_model = kwargs['datenmanagement_model']
    self.content_type_id = ContentType.objects.get(app_label='datenmanagement', model=self.datenmanagement_model.lower()).id
    self.akten_ordner = lade_akten_ordner(self.content_type_id)

    self.model = model
    self.form_class = VorgangForm

    self.multi_file_upload = None
    self.multi_files = None
    self.file = None
    super().__init__(*args, **kwargs)

  def render_to_response(self, context, **response_kwargs):

    if (self.akten_ordner == None):

      error(self.request, 'Der D3-Ordner für Akten dieser Objektart ist nicht konfiguriert. Bitte kontaktieren Sie den Systemadministrator.')
      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', self.object_id)

    return super().render_to_response(context, **response_kwargs)

  def get_form_kwargs(self):
    """
    returns ``**kwargs`` as a dictionary with form attributes

    :return: ``**kwargs`` as a dictionary with form attributes
    """
    self.object_id = self.kwargs['pk']

    kwargs = super().get_form_kwargs()
    return kwargs

  def get_context_data(self, **kwargs):

    context = super().get_context_data(**kwargs)
    return context

  def get_initial(self):
    """
    conditionally sets initial field values for this view

    :return: dictionary with initial field values for this view
    """


  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    form.instance.erstellt_durch = self.request.user

    try:
      form.instance.akten_id = lade_akte(self.content_type_id, self.object_id, self.akten_ordner)
    except:
      error(self.request, 'Beim Anlegen des Vorgangs in D3 ist ein Fehler aufgetreten. Bitte kontaktieren Sie den Systemadministrator.')
      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', self.object_id)

    object_just_created = form.instance
    # return to the page for creating another object of this model,
    # based on the object just created
    self.success_url = get_url_back(None, 'datenmanagement:' + self.model.__name__ + '_add_another', True)

    success(self.request, 'neuer Vorgang erfolgreich angelegt')
    response = super().form_valid(form)
    return response

  def form_invalid(self, form, **kwargs):
    """
    re-opens passed form if it is not valid
    (purpose: empty non-valid array fields)

    :param form: form
    :return: passed form if it is not valid
    """
    context_data = self.get_context_data(**kwargs)

    context_data['form'], context_data['url_back'] = form, form.data.get('original_url_back', None)
    return self.render_to_response(context_data)
