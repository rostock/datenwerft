from django.contrib.auth.models import User
from django.urls import reverse
from django.test import override_settings
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
    self.assertEqual(form.error_messages[error_messages_key],
                     ExternalAuthenticationForm.error_messages.get(error_messages_key))

  def test_signup_pass(self):
    mock_request = MockRequest(session={'_token': self.auth_tokens.session_token})
    form = ExternalAuthenticationForm(
      data={'email_token': self.auth_tokens.email_token},
      request=mock_request
    )
    self.assertTrue(form.is_valid())

  def test_signup_email_token_fail(self):
    mock_request = MockRequest(session={'_token': self.auth_tokens.session_token})
    form = ExternalAuthenticationForm(
      data={'email_token': 'ABC'},
      request=mock_request
    )
    self.assertFalse(form.is_valid())
    error_messages_key = 'invalid_login'
    self.assertEqual(form.error_messages[error_messages_key],
                     ExternalAuthenticationForm.error_messages.get(error_messages_key))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
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

  def test_external_login_view(self):
    last_login = self.test_user.last_login
    self.assertIsNone(last_login)
    session = self.client.session
    session['_token'] = f'{self.auth_tokens.session_token}'
    session.save()
    response = self.client.post(reverse(
      'accounts:external_login',
      kwargs={'url_token': self.auth_tokens.url_token}),
      data={'email_token': self.auth_tokens.email_token},
    )
    self.assertEqual(response.wsgi_request.user, self.test_user)
    self.test_user.refresh_from_db()
    self.assertIsNotNone(self.test_user.last_login)
