from django.apps import AppConfig


class GdiHroCodelistsConfig(AppConfig):
  name = 'gdihrocodelists'
  verbose_name = 'GDI.HRO Codelists'
  description = 'System zur Administration von Codelisten im Rahmen der GDI.HRO'
  admin_app = True

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
