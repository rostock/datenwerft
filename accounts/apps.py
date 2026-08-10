from django.apps import AppConfig


class AccountsConfig(AppConfig):
  name = 'accounts'
  verbose_name = 'Accounts'

  def ready(self):
    from django.db.models import fields

    fields.BLANK_CHOICE_LABEL = '----------'
