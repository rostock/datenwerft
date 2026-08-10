from django.apps import AppConfig


class AntragsmanagementConfig(AppConfig):
  name = 'antragsmanagement'
  verbose_name = 'Antragsmanagement'
  description = 'System zum Management von Anträgen'
  datenwerft_app = True

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
