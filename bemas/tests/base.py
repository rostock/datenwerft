from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse
from json import loads

from .constants_vars import *


class DefaultTestCase(TestCase):
  """
  default abstract test class
  """

  databases = DATABASES

  def init(self):
    self.test_bemas_admin_group = Group.objects.create(name=settings.BEMAS_ADMIN_GROUP_NAME)
    self.test_bemas_user_group = Group.objects.create(name=settings.BEMAS_USERS_GROUP_NAME)
    self.test_user = User.objects.create_user(username=USERNAME, password=PASSWORD)


class DefaultViewTestCase(DefaultTestCase):
  """
  abstract test class for views
  """

  def init(self):
    super().init()

  def login(self, bemas_user=False, bemas_admin=False):
    """
    logs test user in
    (and assigns standard and/or admin rights)

    :param self
    :param bemas_user: assign standard rights to user?
    :param bemas_admin: assign admin rights to user?
    """
    if bemas_user:
      self.test_bemas_user_group.user_set.add(self.test_user)
    if bemas_admin:
      self.test_bemas_admin_group.user_set.add(self.test_user)
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_view_test(self, bemas_user, bemas_admin, view_name,
                        status_code, content_type, string):
    """
    tests a view via GET

    :param self
    :param bemas_user: assign standard rights to user?
    :param bemas_admin: assign admin rights to user?
    :param view_name: name of the view
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    """
    # log test user in
    self.login(bemas_user, bemas_admin)
    # try GETting the view
    response = self.client.get(reverse('bemas:' + view_name))
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # specific string contained in response?
    if 'json' in response['content-type'].lower():
      self.assertIn(string, str(loads(response.content)))
    else:
      self.assertIn(string, str(response.content))
