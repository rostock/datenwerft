from django.apps import apps
from django.views.generic import ListView


class IndexView(ListView):
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
    models_meta, models_codelist, models_complex, models_simple = [], [], [], []
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
        if hasattr(model._meta, 'metamodel') and model._meta.metamodel is True:
          models_meta.append(list_model)
        elif hasattr(model._meta, 'codelist') and model._meta.codelist is True:
          models_codelist.append(list_model)
        elif hasattr(model._meta, 'complex') and model._meta.complex is True:
          models_complex.append(list_model)
        else:
          models_simple.append(list_model)
    context = super(IndexView, self).get_context_data(**kwargs)
    context['models_meta'] = models_meta
    context['models_codelist'] = models_codelist
    context['models_complex'] = models_complex
    context['models_simple'] = models_simple
    return context


class StartView(ListView):
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
    context['editable'] = (
        self.model._meta.editable if hasattr(
            self.model._meta, 'editable') else True)
    context['geometry_type'] = (
        self.model._meta.geometry_type if hasattr(
            self.model._meta, 'geometry_type') else None)
    return context
