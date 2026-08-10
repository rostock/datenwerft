from django.apps import AppConfig


class FmmConfig(AppConfig):
  name = 'fmm'
  verbose_name = 'FMM'
  description = 'Flächenmanagementsystem'
  datenwerft_app = True

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
