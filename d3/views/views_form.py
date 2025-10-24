from django.contrib.contenttypes.models import ContentType
from django.contrib.messages import error, success
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic.edit import CreateView

from d3.models import Vorgang, VorgangMetadaten
from d3.utils import (
  erstelle_vorgang,
  lade_akten_ordner,
  lade_alle_metadaten,
  lade_d3_session_id,
  lade_oder_erstelle_akte,
)
from d3.views.forms import VorgangForm
from datenwerft.settings import D3_ENABLED


class ErstelleVorgangView(CreateView):
  model = Vorgang
  datenmanagement_model = ''
  object_id = ''
  metadaten = []

  """
  view for form page for creating an object of a model
  """

  def __init__(self, model=None, *args, **kwargs):
    self.datenmanagement_model = kwargs['datenmanagement_model']
    self.content_type_id = ContentType.objects.get(
      app_label='datenmanagement', model=self.datenmanagement_model.lower()
    ).id
    self.akten_ordner = lade_akten_ordner(self.content_type_id)
    self.metadaten = lade_alle_metadaten('vorgang')

    self.model = model
    self.form_class = VorgangForm

    self.multi_file_upload = None
    self.multi_files = None
    self.file = None
    super().__init__(*args, **kwargs)

  def render_to_response(self, context, **response_kwargs):
    if not D3_ENABLED:
      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', self.object_id)

    if lade_d3_session_id(self.request) is None:
      error(
        self.request,
        'Die Anmeldung in d.3 ist fehlgeschlagen. Bitte versuchen Sie sich erneut einzuloggen oder kontaktieren Sie den Systemadministrator.',  # noqa: E501
      )
      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', self.object_id)

    try:
      ContentType.objects.get_for_id(self.content_type_id).get_object_for_this_type(
        uuid=self.object_id
      )
    except Exception:
      error(self.request, self.datenmanagement_model + ' existiert nicht.')
      return redirect('datenmanagement:' + self.datenmanagement_model + '_start')

    if self.akten_ordner is None:
      error(
        self.request,
        'Der D3-Ordner für Akten dieser Objektart ist nicht konfiguriert. Bitte kontaktieren Sie den Systemadministrator.',  # noqa: E501
      )
      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', self.object_id)

    return super().render_to_response(context, **response_kwargs)

  def get_form_kwargs(self):
    """
    returns ``**kwargs`` as a dictionary with form attributes

    :return: ``**kwargs`` as a dictionary with form attributes
    """
    self.object_id = self.kwargs['pk']

    kwargs = super().get_form_kwargs()
    kwargs['metadaten'] = self.metadaten
    return kwargs

  def get_context_data(self, **kwargs):
    context = super().get_context_data(**kwargs)
    context['url_back'] = reverse(
      'datenmanagement:' + self.datenmanagement_model + '_change', args=[self.object_id]
    )
    return context

  def form_valid(self, form):
    """
    sends HTTP response if passed form is valid

    :param form: form
    :return: HTTP response if passed form is valid
    """
    form.instance.erstellt_durch = self.request.user

    vorgang_metadaten = []

    for metadaten in self.metadaten:
      wert = form.data.get('metadaten.' + str(metadaten.id))

      if metadaten.gui_element == 'checkbox' and 'on' != wert:
        wert = 'Nein'
      if metadaten.gui_element == 'checkbox' and 'on' == wert:
        wert = 'Ja'

      if wert:
        vorgang_meta = VorgangMetadaten()
        vorgang_meta.vorgang = form.instance
        vorgang_meta.metadaten = metadaten
        vorgang_meta.erstellt_durch = self.request.user
        vorgang_meta.wert = wert
        vorgang_metadaten.append(vorgang_meta)

    try:
      form.instance.akten = lade_oder_erstelle_akte(
        self.request, self.content_type_id, self.object_id, self.akten_ordner
      )
      form.instance.d3_id = erstelle_vorgang(
        self.request, form.instance, vorgang_metadaten, self.metadaten
      )
    except Exception:
      error(
        self.request,
        'Beim Anlegen des Vorgangs in d.3 ist ein Fehler aufgetreten. Bitte kontaktieren Sie den Systemadministrator.',  # noqa: E501
      )
      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', self.object_id)

    # return to the page for creating another object of this model,
    # based on the object just created
    self.success_url = reverse(
      'datenmanagement:' + self.datenmanagement_model + '_change', args=[self.object_id]
    )

    success(self.request, 'neuer Vorgang erfolgreich angelegt')
    response = super().form_valid(form)

    for vorgang_metadaten_object in vorgang_metadaten:
      vorgang_metadaten_object.save()
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
