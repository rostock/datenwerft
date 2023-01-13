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

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_logged_in(self):
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
    self.assertIn('keine Datenthemen', str(response.content))

  def test_view_not_logged_in(self):
    # Seite via GET aufrufen
    response = self.client.get(reverse('datenmanagement:index'))
    # Aufruf erfolgreich?
    self.assertEqual(response.status_code, 200)
    # Content-Type der Antwort wie erwartet?
    self.assertEqual(response['content-type'].lower(), 'text/html; charset=utf-8')
    # Antwort enthält bestimmten Wert?
    self.assertIn('Willkommen bei', str(response.content))


class GPXtoGeoJSONTest(DefaultTestCase):
  """
  Testklasse für Übergabe einer GPX-Datei an FME Server und Rückgabe des generierten GeoJSON
  """

  GPX_FILE_SUCCESS = TEST_DIR / 'data' / 'gpx_valid.gpx'
  GPX_FILE_ERROR = TEST_DIR / 'data' / 'gpx_invalid.gpx'

  def setUp(self):
    self.init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_success(self):
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # Seite aufrufen und via POST notwendige Daten mitgeben
    with open(self.GPX_FILE_SUCCESS, 'rb') as file:
      response = self.client.post(
        reverse('datenmanagement:gpxtogeojson'),
        data={
          'gpx': file
        }
      )
    # Aufruf erfolgreich?
    self.assertEqual(response.status_code, 200)
    # Content-Type der Antwort wie erwartet?
    self.assertEqual(response['content-type'].lower(), 'application/json')
    # Antwort enthält bestimmten Wert?
    self.assertIn('Feature', str(loads(response.content)))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_error(self):
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # Seite aufrufen und via POST notwendige Daten mitgeben
    with open(self.GPX_FILE_ERROR, 'rb') as file:
      response = self.client.post(
        reverse('datenmanagement:gpxtogeojson'),
        data={
          'gpx': file
        }
      )
    # Aufruf nicht erfolgreich?
    self.assertEqual(response.status_code, 422)
    # Content-Type der Antwort wie erwartet?
    self.assertEqual(response['content-type'].lower(), 'application/json')
    # Antwort enthält bestimmten Wert?
    self.assertIn('error_log', str(loads(response.content)))
