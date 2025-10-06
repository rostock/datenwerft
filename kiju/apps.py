from django.apps import AppConfig


class KijuConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'kiju'
  verbose_name = 'KiJu'
  description = 'KiJu Angebotsdatenbank'
  datenwerft_app = True
