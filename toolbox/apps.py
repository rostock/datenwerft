from django.apps import AppConfig


class ToolboxConfig(AppConfig):
  name = 'toolbox'
  verbose_name = 'Toolbox'

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
