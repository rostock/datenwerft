from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase, override_settings
from django.urls import reverse

from angebotsdb.constants_vars import ADMIN_GROUP, USERS_GROUP

from .constant_vars import DATABASES, PASSWORD, USERNAME, USERNAME_PROVIDER, USERNAME_REVIEWER
from .functions import get_object


class MockResponse:
  """
  Minimale Mock-Response für requests.get-Aufrufe der PyGeoAPIMultipleChoiceField.
  Gibt eine leere Features-Liste zurück, damit das Feld keine externe HTTP-Anfrage stellt.
  """

  def __init__(self, features=None):
    self._data = {'features': features or []}

  def raise_for_status(self):
    pass

  def json(self):
    return self._data


class DefaultTestCase(TestCase):
  """
  Abstrakte Basis-Testklasse für alle AngebotsDB-Tests.

  Legt Test-User und -Gruppen an. Wird per self.init() aus setUp() aufgerufen.
  """

  databases = DATABASES

  def init(self):
    self.admin_group = Group.objects.create(name=ADMIN_GROUP)
    self.users_group = Group.objects.create(name=USERS_GROUP)
    # Alle App-Berechtigungen der Admin-Gruppe zuweisen
    permissions = Permission.objects.filter(content_type__app_label='angebotsdb')
    for perm in permissions:
      self.admin_group.permissions.add(perm)
    self.admin_user = User.objects.create_user(username=USERNAME, password=PASSWORD)
    self.provider_user = User.objects.create_user(username=USERNAME_PROVIDER, password=PASSWORD)
    self.reviewer_user = User.objects.create_user(username=USERNAME_REVIEWER, password=PASSWORD)


class ModelTestCase(DefaultTestCase):
  """
  Abstrakte Testklasse für Modell-Tests.
  """

  model = None
  count = 0
  create_test_object_in_classmethod = True
  attributes_values_db_initial = {}
  attributes_values_db_updated = {}
  test_object = None

  @classmethod
  def setUpTestData(cls):
    if cls.create_test_object_in_classmethod:
      cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def init(self):
    super().init()

  def generic_existance_test(self, test_object):
    """
    Prüft die grundlegende Existenz des Testobjekts.

    :param test_object: Testobjekt
    """
    self.assertEqual(self.model.objects.only('pk').all().count(), self.count + 1)
    self.assertEqual(test_object, self.test_object)

  def generic_create_test(self):
    """
    Testet das Anlegen des Testobjekts des übergebenen Modells.
    """
    object_filter = self.attributes_values_db_initial
    test_object = get_object(self.model, object_filter)
    self.generic_existance_test(test_object)
    self.assertEqual(self.model.objects.only('pk').filter(**object_filter).count(), 1)

  def generic_update_test(self):
    """
    Testet das Aktualisieren des Testobjekts des übergebenen Modells.
    """
    for key in self.attributes_values_db_updated:
      setattr(self.test_object, key, self.attributes_values_db_updated[key])
    self.test_object.save()
    object_filter = self.attributes_values_db_updated
    test_object = get_object(self.model, object_filter)
    self.generic_existance_test(test_object)
    self.assertEqual(self.model.objects.only('pk').filter(**object_filter).count(), 1)

  def generic_delete_test(self):
    """
    Testet das Löschen des Testobjekts des übergebenen Modells.
    """
    self.test_object.delete()
    self.assertEqual(self.model.objects.only('pk').all().count(), self.count)

  def generic_string_representation_test(self, string_representation):
    """
    Testet die String-Repräsentation des Testobjekts.

    :param string_representation: erwartete String-Repräsentation
    """
    self.assertEqual(str(self.test_object), string_representation)


class ViewTestCase(DefaultTestCase):
  """
  Abstrakte Testklasse für View-Tests.
  """

  def init(self):
    super().init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_get_test(self, login_fn, view_name, view_args, status_code, content_type, string):
    """
    Testet eine View via GET.

    :param login_fn: Login-Funktion (z.B. login_as_admin)
    :param view_name: Name der View (ohne App-Prefix)
    :param view_args: URL-Argumente (dict oder None)
    :param status_code: erwarteter HTTP-Statuscode
    :param content_type: erwarteter Content-Type
    :param string: erwarteter String in der Response
    """
    login_fn(self)
    if view_args:
      url = reverse(f'angebotsdb:{view_name}', kwargs=view_args)
    else:
      url = reverse(f'angebotsdb:{view_name}')
    response = self.client.get(url)
    self.assertEqual(response.status_code, status_code)
    self.assertEqual(response['content-type'].lower(), content_type)
    self.assertIn(string, response.content.decode('utf-8'))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @override_settings(MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage')
  def generic_post_test(self, login_fn, view_name, view_args, form_data, status_code):
    """
    Testet eine View via POST.

    :param login_fn: Login-Funktion
    :param view_name: Name der View (ohne App-Prefix)
    :param view_args: URL-Argumente (dict oder None)
    :param form_data: POST-Daten
    :param status_code: erwarteter HTTP-Statuscode
    """
    login_fn(self)
    if view_args:
      url = reverse(f'angebotsdb:{view_name}', kwargs=view_args)
    else:
      url = reverse(f'angebotsdb:{view_name}')
    response = self.client.post(url, form_data)
    self.assertEqual(response.status_code, status_code)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_ajax_delete_test(self, login_fn, view_name, view_args, expected_success):
    """
    Testet den AJAX-Lösch-Endpoint via POST mit X-Requested-With-Header.

    :param login_fn: Login-Funktion
    :param view_name: Name der View (ohne App-Prefix)
    :param view_args: URL-Argumente (dict)
    :param expected_success: True wenn JSON-Antwort {'success': True} erwartet wird
    """
    import json
    login_fn(self)
    url = reverse(f'angebotsdb:{view_name}', kwargs=view_args)
    response = self.client.post(url, {}, headers={'x-requested-with': 'XMLHttpRequest'})
    self.assertEqual(response.status_code, 200)
    data = json.loads(response.content)
    self.assertEqual(data['success'], expected_success)


class FormViewTestCase(ModelTestCase, ViewTestCase):
  """
  Abstrakte Testklasse für Formular-View-Tests (kombiniert Model- und View-Tests).
  """

  def init(self):
    super().init()
