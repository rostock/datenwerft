from django.contrib.auth.models import User
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from .forms import ExternalAuthenticationForm
from .models import UserAuthToken


class MockRequest:
  def __init__(self, session=None, status_code=None, url=None):
    self.session = session
    self.status_code = status_code
    self.url = url


class AccountTestCase(APITestCase):
  USERNAME = 'foo@bar.de'
  PASSWORD = 'Secret4000'

  def init(self):
    self.csrf_client = APIClient(enforce_csrf_checks=True)
    self.test_user = User.objects.create_user(
      username=self.USERNAME,
      password=self.PASSWORD,
    )
    self.auth_tokens = UserAuthToken.objects.create(user=self.test_user)


class TestLoginForm(AccountTestCase):
  def setUp(self):
    self.init()

  def test_signup_no_session_token(self):
    form = ExternalAuthenticationForm(data={'email_token': self.auth_tokens.email_token})
    self.assertFalse(form.is_valid())
    error_messages_key = 'invalid_login'
    self.assertEqual(
      form.error_messages[error_messages_key],
      ExternalAuthenticationForm.error_messages.get(error_messages_key),
    )

  def test_signup_pass(self):
    mock_request = MockRequest(session={'_token': self.auth_tokens.session_token})
    form = ExternalAuthenticationForm(
      data={'email_token': self.auth_tokens.email_token}, request=mock_request
    )
    self.assertTrue(form.is_valid())

  def test_signup_email_token_fail(self):
    mock_request = MockRequest(session={'_token': self.auth_tokens.session_token})
    form = ExternalAuthenticationForm(data={'email_token': 'ABC'}, request=mock_request)
    self.assertFalse(form.is_valid())
    error_messages_key = 'invalid_login'
    self.assertEqual(
      form.error_messages[error_messages_key],
      ExternalAuthenticationForm.error_messages.get(error_messages_key),
    )

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @override_settings(AUTH_LDAP_EXTENSION_INTERNAL_IP_ADDRESSES=[])
  def test_pre_login_view(self):
    response = self.client.post(
      reverse('accounts:login'),
      data={
        'username': self.USERNAME,
        'password': self.PASSWORD,
      },
    )
    auth_tokens = UserAuthToken.objects.get(user=self.test_user)
    self.assertTrue(response.wsgi_request.user.is_anonymous)
    self.assertEqual(response.wsgi_request.session['_token'], auth_tokens.session_token)

  @override_settings(AUTH_LDAP_EXTENSION_INTERNAL_IP_ADDRESSES=[])
  def test_external_login_view(self):
    last_login = self.test_user.last_login
    self.assertIsNone(last_login)
    session = self.client.session
    session['_token'] = f'{self.auth_tokens.session_token}'
    session.save()
    response = self.client.post(
      reverse('accounts:external_login', kwargs={'url_token': self.auth_tokens.url_token}),
      data={'email_token': self.auth_tokens.email_token},
    )
    self.assertEqual(response.wsgi_request.user, self.test_user)
    self.test_user.refresh_from_db()
    self.assertIsNotNone(self.test_user.last_login)


class TestPasswordChangeView(AccountTestCase):
  NEW_PASSWORD = 'NewSecret4000!'
  URL = reverse('accounts:password_change')

  def setUp(self):
    self.init()

  def test_unauthenticated_get(self):
    """
    Nicht-eingeloggte Nutzer erhalten bei GET einen 403-Fehler.
    """
    response = self.client.get(self.URL)
    self.assertEqual(response.status_code, 403)

  def test_unauthenticated_post(self):
    """
    Nicht-eingeloggte Nutzer erhalten auch bei POST einen 403-Fehler.
    """
    response = self.client.post(self.URL, data={
      'old_password': self.PASSWORD,
      'new_password1': self.NEW_PASSWORD,
      'new_password2': self.NEW_PASSWORD,
    })
    self.assertEqual(response.status_code, 403)

  def test_ldap_user_get(self):
    """
    LDAP-Nutzer (kein nutzbares Django-Passwort) erhalten bei GET einen 403-Fehler.
    """
    self.test_user.set_unusable_password()
    self.test_user.save()
    self.client.force_login(self.test_user)
    response = self.client.get(self.URL)
    self.assertEqual(response.status_code, 403)

  def test_ldap_user_post(self):
    """
    LDAP-Nutzer (kein nutzbares Django-Passwort) erhalten auch bei POST einen 403-Fehler.
    """
    self.test_user.set_unusable_password()
    self.test_user.save()
    self.client.force_login(self.test_user)
    response = self.client.post(self.URL, data={
      'old_password': self.PASSWORD,
      'new_password1': self.NEW_PASSWORD,
      'new_password2': self.NEW_PASSWORD,
    })
    self.assertEqual(response.status_code, 403)

  def test_local_user_get(self):
    """
    Lokale Django-Nutzer können das Passwort-Ändern-Formular aufrufen (200).
    """
    self.client.force_login(self.test_user)
    response = self.client.get(self.URL)
    self.assertEqual(response.status_code, 200)

  def test_local_user_post_success(self):
    """
    Lokale Django-Nutzer werden nach erfolgreichem Passwort-Ändern zur Done-Seite weitergeleitet.
    """
    self.client.force_login(self.test_user)
    response = self.client.post(self.URL, data={
      'old_password': self.PASSWORD,
      'new_password1': self.NEW_PASSWORD,
      'new_password2': self.NEW_PASSWORD,
    })
    self.assertRedirects(response, reverse('accounts:password_change_done'))

  def test_local_user_post_wrong_old_password(self):
    """
    Ein falsches aktuelles Passwort führt zu einem Formfehler, kein Redirect.
    """
    self.client.force_login(self.test_user)
    response = self.client.post(self.URL, data={
      'old_password': 'WrongPassword!',
      'new_password1': self.NEW_PASSWORD,
      'new_password2': self.NEW_PASSWORD,
    })
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.context['form'].errors)

  def test_local_user_post_mismatched_passwords(self):
    """
    Unterschiedliche neue Passwörter führen zu einem Formfehler, kein Redirect.
    """
    self.client.force_login(self.test_user)
    response = self.client.post(self.URL, data={
      'old_password': self.PASSWORD,
      'new_password1': self.NEW_PASSWORD,
      'new_password2': self.NEW_PASSWORD + 'X',
    })
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.context['form'].errors)
