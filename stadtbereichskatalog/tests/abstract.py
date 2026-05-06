from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase, override_settings
from django.urls import reverse

from stadtbereichskatalog.constants_vars import GROUP

from ..apps import StadtbereichskatalogConfig as appConfig
from .constants_vars import DATABASES, PASSWORD, USERNAME
from .functions import login


class DefaultTestCase(TestCase):
  """
  abstract test class
  """

  databases = DATABASES

  def init(self):
    self.test_group: Group = Group.objects.create(name=GROUP)
    # assign permissions to test group
    permissions = Permission.objects.filter(content_type__app_label='stadtbereichskatalog')
    for permission in permissions:
      self.test_group.permissions.add(permission)
    self.test_user: User = User.objects.create_user(username=USERNAME, password=PASSWORD)


class ViewTestCase(DefaultTestCase):
  """
  abstract test class for views
  """

  def init(self):
    super().init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_get_test(self, assign_permissions, view_name, status_code, content_type, string):
    """
    tests a view via GET

    :param self
    :param assign_permissions: assign permissions to test user?
    :param view_name: name of the view
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    """
    # log test user in
    login(self, assign_permissions)
    # prepare the GET
    url = reverse(f'{appConfig.name}:{view_name}')
    # try GETting the view
    response = self.client.get(url)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # specific string contained in response?
    self.assertIn(string, str(response.content))
