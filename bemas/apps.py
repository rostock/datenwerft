from django.apps import AppConfig


class BemasConfig(AppConfig):
  name = 'bemas'
  verbose_name = 'BEMAS'
  description = 'Beschwerdemanagementsystem'
  datenwerft_app = True

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
