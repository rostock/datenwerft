from django.apps import AppConfig


class AngebotsDBConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'angebotsdb'
  verbose_name = 'Angebotsdatenbank'
  description = 'Angebotsdatenbank'
  datenwerft_app = True

  def ready(self):
    from django.db.models import fields

    from . import signals  # noqa: F401

    fields.BLANK_CHOICE_LABEL = '----------'
