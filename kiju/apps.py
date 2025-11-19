from django.apps import AppConfig


class KijuConfig(AppConfig):
  default_auto_field = 'django.db.models.BigAutoField'
  name = 'kiju'
  verbose_name = 'Angebotsdatenbank'
  description = 'Angebotsdatenbank Kinder & Jugendhilfe'
  datenwerft_app = True
