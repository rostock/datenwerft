from django.apps import AppConfig


class DatenmanagementConfig(AppConfig):
  name = 'datenmanagement'
  verbose_name = 'Datenmanagement'
  description = 'System zur Bearbeitung von Daten im Rahmen der GDI.HRO'
  datenwerft_app = True
