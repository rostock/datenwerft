from django.apps import apps
from django.views import generic



class IndexView(generic.ListView):
    """
    Liste der Datenthemen, die zur Verfügung stehen
    """
    template_name = 'datenmanagement/index.html'

    def get_queryset(self):
        model_list = []
        app_models = apps.get_app_config('datenmanagement').get_models()
        for model in app_models:
            model_list.append(model)
        return model_list


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
