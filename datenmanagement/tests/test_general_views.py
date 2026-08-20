from django.contrib.auth.models import User
from django.urls import reverse

from .base import DefaultTestCase, GISFiletoGeoJSONTestCase
from .constants_vars import (
  INVALID_GEOJSON_FILE,
  INVALID_GPX_FILE,
  USERNAME,
  VALID_GEOJSON_FILE,
  VALID_GPX_FILE,
)

#
# general views
#


class IndexViewTest(DefaultTestCase):
  """
  test class for main page
  """

  def setUp(self):
    self.test_user = User.objects.create_user(username=USERNAME)
    self.init()

  def generic_view_test(self, login, status_code, string=''):
    """
    tests the view

    :param self
    :param login: with login?
    :param status_code: expected status code of response
    :param string: specific string that should be contained in response
    """
    # with login?
    if login:
      # log test user in
      # (i.e. simulate the effect of the test user logging into the site
      # sind the details of how the test user logged in aren't important here)
      self.client.force_login(self.test_user)
    # try GETting the view
    response = self.client.get(reverse('datenmanagement:index'))
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), 'text/html; charset=utf-8')
    # specific string contained in response?
    if string:
      self.assertIn(string, str(response.content))

  def test_view_logged_in(self):
    self.generic_view_test(True, 200, 'keine Datenthemen')

  def test_view_not_logged_in(self):
    self.generic_view_test(False, 302)


class GeoJSONtoGeoJSONTest(GISFiletoGeoJSONTestCase):
  """
  test class for passing a GeoJSON file to FME Server and returning the generated GeoJSON
  """

  def setUp(self):
    self.init()

  def test_view_success(self):
    self.generic_view_test(VALID_GEOJSON_FILE, 'geojson', 200, 'Feature')

  def test_view_error(self):
    self.generic_view_test(INVALID_GEOJSON_FILE, 'geojson', 422, 'error_log')


class GPXtoGeoJSONTest(GISFiletoGeoJSONTestCase):
  """
  test class for passing a GPX file to FME Server and returning the generated GeoJSON
  """

  def setUp(self):
    self.init()

  def test_view_success(self):
    self.generic_view_test(VALID_GPX_FILE, 'gpx', 200, 'Feature')

  def test_view_error(self):
    self.generic_view_test(INVALID_GPX_FILE, 'gpx', 422, 'error_log')
