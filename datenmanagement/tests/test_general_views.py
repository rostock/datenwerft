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


class GISFiletoGeoJSONTest(DefaultTestCase):
  """
  Testklasse für Übergabe einer GPX-Datei an FME Server und Rückgabe des generierten GeoJSON
  """

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
        reverse('datenmanagement:gisfiletogeojson'),
        data={
          'gpx': gpx
        }
      )
    # falls Test ausgeführt wird ohne gültiges FME-Token
    # (also zum Beispiel auf Basis der secrets.template)...
    if response.status_code == 401:
      pass
    # ansonsten, also bei gültigem FME-Token...
    else:
      # Antwort mit erwartetem Status-Code?
      self.assertEqual(response.status_code, status_code)
      # Content-Type der Antwort wie erwartet?
      self.assertEqual(response['content-type'].lower(), 'application/json')
      # Antwort enthält bestimmten Wert?
      self.assertIn(string, str(loads(response.content)))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_success(self):
    self.generic_view_test(VALID_GPX_FILE, 200, 'Feature')

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_error(self):
    self.generic_view_test(INVALID_GPX_FILE, 422, 'error_log')
