from django import forms
from django.utils.translation import gettext_lazy as _

from accounts.models import UserAuthToken


class ExternalAuthenticationForm(forms.Form):
  email_token = forms.CharField(label='Token', max_length=100)

  error_messages = {
    'invalid_login': _("Bitte geben Sie einen gültigen %(email_token)s ein."),
    'expired_token': _("Login-Code abgelaufen: Bitte führen Sie den Anmeldevorgang erneut aus."),
    'inactive': _("Dieses Benutzerkonto ist inaktiv."),
  }

  def __init__(self, request=None, *args, **kwargs):
    """
    The 'request' parameter is set for custom auth use by subclasses.
    The form data comes in via the standard 'data' kwarg.
    """
    self.request = request
    self.user_cache = None
    super().__init__(*args, **kwargs)

  def clean(self):
    email_token = self.cleaned_data.get('email_token')
    try:
      session_token = self.request.session.pop('_token')
    except AttributeError:
      raise self.get_invalid_login_error()
    if not session_token:
      raise self.get_invalid_login_error()
    try:
      self.user_cache = UserAuthToken.objects.get(
        email_token=email_token,
        session_token=session_token
      ).user
    except UserAuthToken.DoesNotExist:
      raise self.get_invalid_login_error()
    else:
      self.confirm_login_allowed(self.user_cache)

    return self.cleaned_data

  def confirm_login_allowed(self, user):
    if not user.is_active:
      raise forms.ValidationError(
        self.error_messages['inactive'],
        code='inactive',
      )
    if user.userauthtoken.is_expired_token():
      raise forms.ValidationError(
        self.error_messages['expired_token'],
        code='expired_token',
      )

  def get_user(self):
    self.user_cache.backend = 'accounts.backend.DatenwerftAuthBackend'
    return self.user_cache

  def get_invalid_login_error(self):
    return forms.ValidationError(
      self.error_messages['invalid_login'],
      code='invalid_login',
      params={'email_token': 'Code'},
    )
