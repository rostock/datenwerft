import uuid

from django.contrib.contenttypes.models import ContentType
from django.contrib.messages.api import error, success
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, resolve_url, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from jsonview.views import JsonView

from d3.models import VorgangMetadaten, Metadaten, Vorgang
from d3.utils import suche_dateien, lade_akte, lade_datei_inhalt, erstelle_dokument, lade_dokument, bearbeite_dokument
from d3.views.forms import UploadDokumentForm, BearbeiteDokumentForm


class FetchMetaDataRequestView(JsonView):

  def get(self, request, *args, **kwargs):
    """
    Returns metadata for the given process ID as JSON.
    """
    process_id = request.GET.get('processId')

    if not process_id:
      return JsonResponse(
        {"error": "Missing 'processId' parameter."},
        status=400
      )

    vorgang = Vorgang.objects.get(pk=process_id)
    model_name = vorgang.akten.model.model_class().__name__
    model_id = vorgang.akten.object_id

    process_metadata = VorgangMetadaten.objects.filter(vorgang__id=process_id)

    html = render_to_string('d3/metadata_detail.html', {
      "random_uuid": str(uuid.uuid4()),
      "file_list_url": resolve_url('d3:' + str(model_name) + '_d3_list_file', model_id, vorgang.id),
      "model_name": model_name,
      "model_id": model_id,
      "vorgangs_id": vorgang.id,
      "metadata": [
           {
            "titel": pm.metadaten.titel,
            "wert": pm.wert
           }
           for pm in process_metadata
         ]
    })

    return JsonResponse({"html": html})

class ListeDateienView(View):

  datenmanagement_model = ''
  content_type_id = 0

  def __init__(self, datenmanagement_model=None, *args, **kwargs):

    self.datenmanagement_model = datenmanagement_model
    self.content_type_id = ContentType.objects.get(app_label='datenmanagement', model=datenmanagement_model.lower()).id

    super().__init__(**kwargs)

  def get(self, request, *args, **kwargs):

    error = None
    akte = None
    dateien = []

    vorgang = Vorgang.objects.get(pk=kwargs['id'])

    try:
      akte = lade_akte(self.content_type_id, kwargs['pk'])
    except:
      error = 'Datenobjekt besitzt keine Akte.'

    if akte and vorgang.akten != akte:
      error = 'Vorgang gehört nicht zu dieser Akte.'

    if akte and vorgang.akten == akte:

      try:
        dateien = []

        for dms_object in suche_dateien(vorgang.d3_id):
          datei = {"id": dms_object.id}

          for source_property in dms_object.sourceProperties:

            if 'property_filename' == source_property.key:
              datei['filename'] = source_property.value
            if 'property_caption' == source_property.key:
              datei['name'] = source_property.value
          dateien.append(datei)
      except:
        error = 'Dateien konnten nicht geladen werden. Bitte kontaktieren Sie den Systemadministrator.'

    view_params = {
      "file_download_view": f"d3:{self.datenmanagement_model}_file_download",
      "file_change_view": f"d3:{self.datenmanagement_model}_change_file",
      "object_id": kwargs['pk'],
      "vorgang_id": vorgang.id,
      "error": error,
      "dateien": dateien,
    }

    return render(request, "d3/file_list.html", context=view_params)

class DownloadView(View):

  datenmanagement_model = ''
  content_type_id = 0

  def __init__(self, datenmanagement_model=None, *args, **kwargs):

    self.datenmanagement_model = datenmanagement_model
    self.content_type_id = ContentType.objects.get(app_label='datenmanagement', model=datenmanagement_model.lower()).id

    super().__init__(**kwargs)

  def get(self, request, *args, **kwargs):

    datei = lade_datei_inhalt(kwargs['file_id'])

    return HttpResponse(datei.content, content_type=datei.mime_type)

class DokumentenView:

  datenmanagement_model = ''

  def lese_metadaten(self, form):
    """
    lese die Metadaten aus dem Formular und gebe sie als dictionary zurück, welches an D3 gesendet werden kann.

    Args:
        form (Form): validiertes Formular mit den aktuellen Daten

    Returns:
        dict: Dictionary mit den Metadaten, welche an D3 gesendet werden sollen.
    """
    properties = {}

    for metadaten in Metadaten.objects.filter(category="dokument"):

      wert = form.cleaned_data.get('metadaten.' + str(metadaten.id))

      if metadaten.gui_element == 'checkbox' and 'on' != wert:
        wert = "Nein"
      if metadaten.gui_element == 'checkbox' and 'on' == wert:
        wert = "Ja"

      if wert and metadaten.d3_id:
        properties[metadaten.d3_id] = wert
    return properties

  def render_view(self, request, form, object_id: str):

    view_params = {
      "url_back": reverse('datenmanagement:' + self.datenmanagement_model + '_change', args = [object_id]),
      "form": form,
    }
    return render(request, "d3/dokument-form.html", view_params)

class DokumentenErstellenView(View, DokumentenView):

  content_type_id = 0

  def __init__(self, datenmanagement_model=None, *args, **kwargs):

    self.datenmanagement_model = datenmanagement_model
    self.content_type_id = ContentType.objects.get(app_label='datenmanagement', model=datenmanagement_model.lower()).id

    super().__init__(**kwargs)

  def get(self, request, *args, **kwargs):

    object_id = kwargs["pk"]

    try:
      vorgang = Vorgang.objects.get(pk=kwargs['vorgang_id'])
    except:
      error(self.request,'Vorgang existiert nicht. Bitte kontaktieren Sie den Systemadministrator.')
      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', object_id)

    return self.render_view(request, UploadDokumentForm(), object_id)

  def post(self, request, *args, **kwargs):

    vorgang = Vorgang.objects.get(pk=kwargs['vorgang_id'])
    object_id = kwargs["pk"]

    form = UploadDokumentForm(request.POST, request.FILES)

    if form.is_valid():
      properties = self.lese_metadaten(form)

      try:
        erstelle_dokument(vorgang, form.cleaned_data['file'], properties)
        success(self.request, 'neues Dokument erfolgreich angelegt')
      except:
        error(self.request, 'Beim Hochladen des Dokuments in D3 ist ein Fehler aufgetreten. Bitte kontaktieren Sie den Systemadministrator.')

      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', object_id)
    else:

      return self.render_view(request, form, object_id)

class DokumentenBearbeitenView(View, DokumentenView):

  content_type_id = 0

  def __init__(self, datenmanagement_model=None, *args, **kwargs):

    self.datenmanagement_model = datenmanagement_model
    self.content_type_id = ContentType.objects.get(app_label='datenmanagement', model=datenmanagement_model.lower()).id

    super().__init__(**kwargs)

  def get(self, request, *args, **kwargs):

    object_id = kwargs["pk"]
    dokumenten_id = kwargs["file_id"]

    try:
      dokument = lade_dokument(dokumenten_id)
    except:
      error(self.request,'Dokument konnte nicht geladen werden. Bitte kontaktieren Sie den Systemadministrator.')
      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', object_id)

    form_data = {}

    for metadaten in Metadaten.objects.filter(category="dokument"):

      if metadaten.d3_id is None:
        continue

      for source_property in dokument.sourceProperties:

        if source_property.key == metadaten.d3_id:
          wert = source_property.value
          if 'checkbox' == metadaten.gui_element and wert == "Ja":
            form_data['metadaten.' + str(metadaten.id)] = 'on'
          elif 'checkbox' != metadaten.gui_element:
            form_data['metadaten.' + str(metadaten.id)] = wert
          break
    print(form_data)

    return self.render_view(request, BearbeiteDokumentForm(initial=form_data), object_id)

  def post(self, request, *args, **kwargs):

    vorgang = Vorgang.objects.get(pk=kwargs['vorgang_id'])
    object_id = kwargs["pk"]
    dokumenten_id = kwargs["file_id"]

    form = BearbeiteDokumentForm(request.POST, request.FILES)

    if form.is_valid():

      properties = self.lese_metadaten(form)

      try:
        bearbeite_dokument(dokumenten_id, vorgang, form.cleaned_data['file'], properties)
        success(self.request, 'Das Dokument erfolgreich bearbeitet')
      except:
        error(self.request, 'Beim Bearbeiten des Dokuments in D3 ist ein Fehler aufgetreten. Bitte kontaktieren Sie den Systemadministrator.')

      return redirect('datenmanagement:' + self.datenmanagement_model + '_change', object_id)
    else:

      return self.render_view(request, form, object_id)
