from django.apps import AppConfig


class PygeoapiConfig(AppConfig):
  name = 'pygeoapi'
  verbose_name = 'pygeoapi-Konfiguration'
  admin_app = True
  description = 'System zur Konfiguration von pygeoapi im Rahmen der GDI.HRO'

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
