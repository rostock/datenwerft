from django.apps import AppConfig


class DatenmanagementConfig(AppConfig):
  name = 'datenmanagement'
  verbose_name = 'Datenmanagement'
  description = 'System zur Bearbeitung von Daten im Rahmen der GDI.HRO'
  datenwerft_app = True

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
