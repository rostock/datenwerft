from django.test import override_settings
from django.urls import reverse
from json import loads

from .base import DefaultTestCase
from .constants_vars import *


class IndexViewTest(DefaultTestCase):
  """
  Testklasse für Liste der Datenthemen, die zur Verfügung stehen
  """

  def setUp(self):
    self.init()

  def generic_view_test(self, login, string):
    """
    testet den View

    :param self
    :param login: mit Login?
    :param string: bestimmter Wert, der in Antwort enthalten sein soll
    """
    if login:
      self.client.login(
        username=USERNAME,
        password=PASSWORD
      )
    # Seite via GET aufrufen
    response = self.client.get(reverse('datenmanagement:index'))
    # Aufruf erfolgreich?
    self.assertEqual(response.status_code, 200)
    # Content-Type der Antwort wie erwartet?
    self.assertEqual(response['content-type'].lower(), 'text/html; charset=utf-8')
    # Antwort enthält bestimmten Wert?
    self.assertIn(string, str(response.content))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_logged_in(self):
    self.generic_view_test(True, 'keine Datenthemen')

  def test_view_not_logged_in(self):
    self.generic_view_test(False, 'Willkommen bei')


class GPXtoGeoJSONTest(DefaultTestCase):
  """
  Testklasse für Übergabe einer GPX-Datei an FME Server und Rückgabe des generierten GeoJSON
  """

  GPX_FILE_SUCCESS = TEST_DIR / 'data' / 'gpx_valid.gpx'
  GPX_FILE_ERROR = TEST_DIR / 'data' / 'gpx_invalid.gpx'

  def setUp(self):
    self.init()

  def generic_view_test(self, file, status_code, string):
    """
    testet den View

    :param self
    :param file: Datei
    :param status_code: Status-Code, den die Antwort aufweisen soll
    :param string: bestimmter Wert, der in Antwort enthalten sein soll
    """
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # Seite aufrufen und via POST notwendige Daten mitgeben
    with open(file, 'rb') as gpx:
      response = self.client.post(
        reverse('datenmanagement:gpxtogeojson'),
        data={
          'gpx': gpx
        }
      )
    # Antwort mit erwartetem Status-Code?
    self.assertEqual(response.status_code, status_code)
    # Content-Type der Antwort wie erwartet?
    self.assertEqual(response['content-type'].lower(), 'application/json')
    # Antwort enthält bestimmten Wert?
    self.assertIn(string, str(loads(response.content)))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_success(self):
    self.generic_view_test(self.GPX_FILE_SUCCESS, 200, 'Feature')

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_error(self):
    self.generic_view_test(self.GPX_FILE_ERROR, 422, 'error_log')
