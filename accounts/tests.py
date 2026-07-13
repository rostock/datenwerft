from django.contrib.auth.models import Group, User
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

from angebotsdb.constants_vars import USERS_GROUP
from angebotsdb.models.base import UserProfile

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


class TestPasswordChangeOnSettingsPage(AccountTestCase):
  NEW_PASSWORD = 'NewSecret4000!'
  URL = reverse('accounts:settings')
  databases = {'default', 'angebotsdb'}

  def setUp(self):
    self.init()

  def password_change_data(self, **overrides):
    data = {
      'change_password': '1',
      'old_password': self.PASSWORD,
      'new_password1': self.NEW_PASSWORD,
      'new_password2': self.NEW_PASSWORD,
    }
    data.update(overrides)
    return data

  def test_ldap_user_sees_no_password_form(self):
    """
    LDAP-Nutzer (kein nutzbares Django-Passwort) sehen kein Passwort-Formular,
    sondern den Hinweis auf das zentrale Benutzerkonto.
    """
    self.test_user.set_unusable_password()
    self.test_user.save()
    self.client.force_login(self.test_user)
    response = self.client.get(self.URL)
    self.assertEqual(response.status_code, 200)
    self.assertNotContains(response, 'old_password')
    self.assertContains(response, 'zentrale Benutzerkonto')

  def test_ldap_user_post_forbidden(self):
    """
    LDAP-Nutzer erhalten bei POST des Passwort-Formulars einen 403-Fehler.
    """
    self.test_user.set_unusable_password()
    self.test_user.save()
    self.client.force_login(self.test_user)
    response = self.client.post(self.URL, data=self.password_change_data())
    self.assertEqual(response.status_code, 403)

  def test_local_user_sees_password_form(self):
    """
    Lokale Django-Nutzer sehen das Passwort-Formular auf der Einstellungs-Seite.
    """
    self.client.force_login(self.test_user)
    response = self.client.get(self.URL)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'old_password')

  def test_local_user_post_success(self):
    """
    Erfolgreiches Passwort-Ändern leitet zurück zur Einstellungs-Seite,
    das neue Passwort gilt und die Session bleibt eingeloggt.
    """
    self.client.force_login(self.test_user)
    response = self.client.post(self.URL, data=self.password_change_data())
    self.assertRedirects(response, self.URL)
    self.test_user.refresh_from_db()
    self.assertTrue(self.test_user.check_password(self.NEW_PASSWORD))
    # Session bleibt gültig (update_session_auth_hash)
    response = self.client.get(self.URL)
    self.assertEqual(response.wsgi_request.user, self.test_user)

  def test_local_user_post_wrong_old_password(self):
    """
    Ein falsches aktuelles Passwort führt zu einem Formfehler, kein Redirect.
    """
    self.client.force_login(self.test_user)
    response = self.client.post(
      self.URL, data=self.password_change_data(old_password='WrongPassword!')
    )
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.context['password_form'].errors)

  def test_local_user_post_mismatched_passwords(self):
    """
    Unterschiedliche neue Passwörter führen zu einem Formfehler, kein Redirect.
    """
    self.client.force_login(self.test_user)
    response = self.client.post(
      self.URL, data=self.password_change_data(new_password2=self.NEW_PASSWORD + 'X')
    )
    self.assertEqual(response.status_code, 200)
    self.assertTrue(response.context['password_form'].errors)


class TestUserSettingsView(AccountTestCase):
  URL = reverse('accounts:settings')
  databases = {'default', 'angebotsdb'}

  def setUp(self):
    self.init()

  def make_angebotsdb_user(self):
    group, _ = Group.objects.get_or_create(name=USERS_GROUP)
    self.test_user.groups.add(group)

  def test_unauthenticated_get_redirects_to_login(self):
    """
    Nicht-eingeloggte Nutzer werden zum Login umgeleitet.
    """
    response = self.client.get(self.URL)
    self.assertEqual(response.status_code, 302)

  def test_non_angebotsdb_user_get(self):
    """
    Nutzer ohne AngebotsDB-Rolle sehen die Seite ohne Benachrichtigungs-Abschnitt.
    """
    self.client.force_login(self.test_user)
    response = self.client.get(self.URL)
    self.assertEqual(response.status_code, 200)
    self.assertNotContains(response, 'receive_email_notifications')

  def test_non_angebotsdb_user_post_forbidden(self):
    """
    Nutzer ohne AngebotsDB-Rolle dürfen die Einstellung nicht speichern.
    """
    self.client.force_login(self.test_user)
    response = self.client.post(self.URL, data={'receive_email_notifications': 'on'})
    self.assertEqual(response.status_code, 403)

  def test_angebotsdb_user_get(self):
    """
    AngebotsDB-Nutzer sehen den Benachrichtigungs-Abschnitt.
    """
    self.make_angebotsdb_user()
    self.client.force_login(self.test_user)
    response = self.client.get(self.URL)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'receive_email_notifications')

  def test_superuser_get(self):
    """
    Superuser sehen den Benachrichtigungs-Abschnitt ebenfalls.
    """
    self.test_user.is_superuser = True
    self.test_user.save(update_fields=['is_superuser'])
    self.client.force_login(self.test_user)
    response = self.client.get(self.URL)
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'receive_email_notifications')

  def test_angebotsdb_user_post_enables_notifications(self):
    """
    Speichern mit gesetzter Checkbox legt bei Bedarf ein UserProfile an
    und aktiviert die Benachrichtigungen.
    """
    self.make_angebotsdb_user()
    self.client.force_login(self.test_user)
    response = self.client.post(self.URL, data={'receive_email_notifications': 'on'})
    self.assertEqual(response.status_code, 302)
    profile = UserProfile.objects.get(user_id=self.test_user.id)
    self.assertTrue(profile.receive_email_notifications)

  def test_angebotsdb_user_post_disables_notifications(self):
    """
    Speichern ohne Checkbox deaktiviert die Benachrichtigungen wieder.
    """
    self.make_angebotsdb_user()
    UserProfile.objects.create(user_id=self.test_user.id, receive_email_notifications=True)
    self.client.force_login(self.test_user)
    response = self.client.post(self.URL, data={})
    self.assertEqual(response.status_code, 302)
    profile = UserProfile.objects.get(user_id=self.test_user.id)
    self.assertFalse(profile.receive_email_notifications)
