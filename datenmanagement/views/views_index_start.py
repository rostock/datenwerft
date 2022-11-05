from django.apps import apps
from django.conf import settings
from django.views import generic


class IndexView(generic.ListView):
  """
  Liste der Datenthemen, die zur Verfügung stehen
  """

  template_name = 'datenmanagement/index.html'

  def get_queryset(self):
    """
    überschreibt Funktion für Standard-Rückgabewert,
    damit diese nichts zurückgibt statt stumpf die Gesamtmenge aller Objekte des Datenmodells
    """
    return

  def get_context_data(self, **kwargs):
    """
    liefert Dictionary mit Kontextelementen des Views

    :param kwargs:
    :return: Dictionary mit Kontextelementen des Views
    """
    models_codelist = False
    models_codelist_list = []
    models_complex = False
    models_complex_list = []
    models_simple = False
    models_simple_list = []
    app_models = apps.get_app_config('datenmanagement').get_models()
    for model in app_models:
      if (
          self.request.user.has_perm(
              'datenmanagement.add_' +
              model.__name__.lower()) or self.request.user.has_perm(
              'datenmanagement.change_' +
              model.__name__.lower()) or self.request.user.has_perm(
              'datenmanagement.delete_' +
              model.__name__.lower()) or self.request.user.has_perm(
              'datenmanagement.view_' +
              model.__name__.lower())):
        list_model = {
            'name': model.__name__,
            'verbose_name_plural': model._meta.verbose_name_plural,
            'description': model._meta.description
        }
        if hasattr(model._meta, 'codelist') and model._meta.codelist is True:
          models_codelist = True
          models_codelist_list.append(list_model)
        elif hasattr(model._meta, 'complex') and model._meta.complex is True:
          models_complex = True
          models_complex_list.append(list_model)
        else:
          models_simple = True
          models_simple_list.append(list_model)
    context = super(IndexView, self).get_context_data(**kwargs)
    context['LOGIN_URL'] = settings.LOGIN_URL
    context['models_codelist'] = models_codelist
    context['models_codelist_list'] = models_codelist_list
    context['models_complex'] = models_complex
    context['models_complex_list'] = models_complex_list
    context['models_simple'] = models_simple
    context['models_simple_list'] = models_simple_list
    return context


class StartView(generic.ListView):
  """
  Startansicht eines Datenthemas

  folgende Möglichkeiten:
  * neuen Datensatz anlegen
  * Datensätze in Tabelle auflisten
  * Datensätze auf Karte anzeigen

  :param model: Datenmodell
  :param template_name: Name des Templates
  """

  def __init__(self, model=None, template_name=None):
    self.model = model
    self.template_name = template_name
    super(StartView, self).__init__()

  def get_context_data(self, **kwargs):
    """
    liefert Dictionary mit Kontextelementen des Views

    :param kwargs:
    :return: Dictionary mit Kontextelementen des Views
    """
    context = super(StartView, self).get_context_data(**kwargs)
    context['model_name'] = self.model.__name__
    context['model_name_lower'] = self.model.__name__.lower()
    context['model_verbose_name_plural'] = self.model._meta.verbose_name_plural
    context['model_description'] = self.model._meta.description
    context['geometry_type'] = (
        self.model._meta.geometry_type if hasattr(
            self.model._meta, 'geometry_type') else None)
    context['additional_wms_layers'] = (
        self.model._meta.additional_wms_layers if hasattr(
            self.model._meta, 'additional_wms_layers') else None)
    return context
