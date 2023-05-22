from django.test import override_settings
from django.urls import reverse

from .base import DefaultTestCase, GISFiletoGeoJSONTestCase
from .constants_vars import *


class IndexViewTest(DefaultTestCase):
  """
  Testklasse für Liste der Datenthemen, die zur Verfügung stehen
  """

  def setUp(self):
    self.init()

  def generic_view_test(self, login, status_code, string=''):
    """
    testet den View

    :param self
    :param login: mit Login?
    :param status_code: : Status-Code, den die Antwort aufweisen soll
    :param string: bestimmter Wert, der in Antwort enthalten sein soll
    """
    if login:
      self.client.login(
        username=USERNAME,
        password=PASSWORD
      )
    # Seite via GET aufrufen
    response = self.client.get(reverse('datenmanagement:index'))
    # Status-Code der Antwort wie erwartet?
    self.assertEqual(response.status_code, status_code)
    # Content-Type der Antwort wie erwartet?
    self.assertEqual(response['content-type'].lower(), 'text/html; charset=utf-8')
    if string:
      # Antwort enthält bestimmten Wert?
      self.assertIn(string, str(response.content))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_logged_in(self):
    self.generic_view_test(True, 200, 'keine Datenthemen')

  def test_view_not_logged_in(self):
    self.generic_view_test(False, 302)


class GeoJSONtoGeoJSONTest(GISFiletoGeoJSONTestCase):
  """
  Testklasse für Übergabe einer GeoJSON-Datei an FME Server und Rückgabe des generierten GeoJSON
  """

  def setUp(self):
    self.init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_success(self):
    self.generic_view_test(VALID_GEOJSON_FILE, 'geojson', 200, 'Feature')

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_error(self):
    self.generic_view_test(INVALID_GEOJSON_FILE, 'geojson', 422, 'error_log')


class GPXtoGeoJSONTest(GISFiletoGeoJSONTestCase):
  """
  Testklasse für Übergabe einer GPX-Datei an FME Server und Rückgabe des generierten GeoJSON
  """

  def setUp(self):
    self.init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_success(self):
    self.generic_view_test(VALID_GPX_FILE, 'gpx', 200, 'Feature')

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_error(self):
    self.generic_view_test(INVALID_GPX_FILE, 'gpx', 422, 'error_log')
