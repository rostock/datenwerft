from django.apps import AppConfig


class AngebotsDBConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'angebotsdb'
  verbose_name = 'Angebotsdatenbank'
  description = 'Angebotsdatenbank'
  datenwerft_app = True
