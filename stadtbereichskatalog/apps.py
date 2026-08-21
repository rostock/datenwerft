from django.apps import AppConfig


class StadtbereichskatalogConfig(AppConfig):
  name = 'stadtbereichskatalog'
  verbose_name = 'Stadtbereichskatalog'
  description = 'System zur Bearbeitung der Inhalte des Stadtbereichskatalogs'
  datenwerft_app = True

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
