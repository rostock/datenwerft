from django.apps import AppConfig


class D3Config(AppConfig):
  name = 'd3'
  verbose_name = 'd3'

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
