from django.apps import apps
from django.views import generic


class IndexView(generic.ListView):
    """
    Liste der Datenthemen, die zur Verfügung stehen
    """
    template_name = 'datenmanagement/index.html'

    def get_queryset(self):
        """
        Funktion für Standard-Rückgabewert überschreiben,
        damit diese nichts zurückgibt
        statt stumpf die Gesamtmenge aller Objekte des Datenmodells
        """
        return

    def get_context_data(self, **kwargs):
        codelist_models = False
        codelist_models_list = []
        complex_models = False
        complex_models_list = []
        simple_models = False
        simple_models_list = []
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
                if (hasattr(model._meta, 'codelist') and
                        model._meta.codelist is True):
                    codelist_models = True
                    codelist_models_list.append(list_model)
                elif (hasattr(model._meta, 'complex') and
                        model._meta.complex is True):
                    complex_models = True
                    complex_models_list.append(list_model)
                else:
                    simple_models = True
                    simple_models_list.append(list_model)
        context = super(IndexView, self).get_context_data(**kwargs)
        context['codelist_models'] = codelist_models
        context['codelist_models_list'] = codelist_models_list
        context['complex_models'] = complex_models
        context['complex_models_list'] = complex_models_list
        context['simple_models'] = simple_models
        context['simple_models_list'] = simple_models_list
        return context


class StartView(generic.ListView):
    """
    Startansicht eines Datenthemas mit folgenden Möglichkeiten:
    * neuen Datensatz anlegen
    * Datensätze in Tabelle auflisten
    * Datensätze auf Karte anzeigen
    """

    def __init__(self, model=None, template_name=None):
        self.model = model
        self.template_name = template_name
        super(StartView, self).__init__()

    def get_context_data(self, **kwargs):
        context = super(StartView, self).get_context_data(**kwargs)
        context['model_name'] = self.model.__name__
        context['model_name_lower'] = self.model.__name__.lower()
        context[
            'model_verbose_name_plural'] = self.model._meta.verbose_name_plural
        context['model_description'] = self.model._meta.description
        context['geometry_type'] = (
            self.model._meta.geometry_type if hasattr(
                self.model._meta, 'geometry_type') else None)
        context['additional_wms_layers'] = (
            self.model._meta.additional_wms_layers if hasattr(
                self.model._meta, 'additional_wms_layers') else None)
        return context
