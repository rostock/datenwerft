from django.apps import AppConfig


class StadtbereichskatalogConfig(AppConfig):
  name = 'stadtbereichskatalog'
  verbose_name = 'Stadtbereichskatalog'
  description = 'System zur Bearbeitung der Inhalte des Stadtbereichskatalogs'
  datenwerft_app = True
