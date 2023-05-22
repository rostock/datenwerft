from django.contrib.auth.models import Permission, User
from django.contrib.messages import storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse, reverse_lazy
from json import loads
from datenmanagement.views.views_form import DataAddView, DataChangeView, DataDeleteView

from .constants_vars import *
from .functions import clean_object_filter, create_test_subset, get_object, load_sql_schema


class DefaultTestCase(TestCase):
  """
  Standardtest (abstrakt)
  """

  databases = DATABASES

  def init(self):
    self.test_user = User.objects.create_user(username=USERNAME, password=PASSWORD)


class DefaultModelTestCase(DefaultTestCase):
  """
  Standardtest für Datenmodelle (abstrakt)
  """

  model = None
  create_test_object_in_classmethod = True
  create_test_subset_in_classmethod = True
  attributes_values_db_initial = {}
  test_object = None

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()
    if cls.create_test_object_in_classmethod:
      cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    if cls.test_object and cls.create_test_subset_in_classmethod:
      cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def init(self):
    super().init()

  def generic_existance_test(self, model, test_object):
    """
    testet die generelle Existenz eines Objekts des übergebenen Datenmodells

    :param self
    :param model: Datenmodell
    :param test_object: Objekt des übergebenen Datenmodells
    """
    # genau ein Objekt erstellt
    # bzw. existiert nach der Aktualisierung immer noch genau ein Objekt?
    self.assertEqual(model.objects.all().count(), 1)
    # erstelltes Objekt wie erwartet erstellt
    # bzw. aktualisiertes Objekt wie erwartet aktualisiert?
    self.assertEqual(test_object, self.test_object)

  def generic_create_test(self, model, object_filter):
    """
    testet die Erstellung eines Objekts des übergebenen Datenmodells

    :param self
    :param model: Datenmodell
    :param object_filter: Objektfilter
    """
    # Objektfilter bereinigen
    object_filter = clean_object_filter(model, object_filter)
    test_object = get_object(model, object_filter)
    self.generic_existance_test(model, test_object)
    # erstelltes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(model.objects.filter(**object_filter).count(), 1)
    # erstelltes Objekt umfasst ein UUID-Feld, das als Primärschlüssel deklariert ist?
    self.assertEqual(test_object.pk, test_object.uuid)

  def generic_update_test(self, model, object_filter):
    """
    testet die Aktualisierung eines Objekts des übergebenen Datenmodells

    :param self
    :param model: Datenmodell
    :param object_filter: Objektfilter
    """
    for key in object_filter:
      setattr(self.test_object, key, object_filter[key])
    self.test_object.save()
    # Objektfilter bereinigen
    object_filter = clean_object_filter(model, object_filter)
    test_object = get_object(model, object_filter)
    self.generic_existance_test(model, test_object)
    # aktualisiertes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(model.objects.filter(**object_filter).count(), 1)

  def generic_delete_test(self, model):
    """
    testet die Löschung eines Objekts des übergebenen Datenmodells

    :param self
    :param model: Datenmodell
    """
    # keine Objekte mehr vorhanden?
    self.test_object.delete()
    self.assertEqual(model.objects.all().count(), 0)

  def login_assign_permissions(self, model):
    """
    führt einen Login durch
    und setzt alle notwendigen Berechtigungen am übergebenen Datenmodell

    :param self
    :param model: Datenmodell
    """
    self.test_user.user_permissions.add(
      Permission.objects.get(codename='view_' + model._meta.model_name)
    )
    self.test_user.user_permissions.add(
      Permission.objects.get(codename='add_' + model._meta.model_name)
    )
    self.test_user.user_permissions.add(
      Permission.objects.get(codename='change_' + model._meta.model_name)
    )
    self.test_user.user_permissions.add(
      Permission.objects.get(codename='delete_' + model._meta.model_name)
    )
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_view_test(self, model, view_name, url_params, status_code, content_type, string):
    """
    testet einen View via GET

    :param self
    :param model: Datenmodell
    :param view_name: Name des Views
    :param url_params: URL-Parameter
    :param status_code: Status-Code, den die Antwort aufweisen soll
    :param content_type: Content-Type, den die Antwort aufweisen soll
    :param string: bestimmter Wert, der in Antwort enthalten sein soll
    """
    # Login durchführen und alle notwendigen Berechtigungen setzen
    self.login_assign_permissions(model)
    # Seite via GET aufrufen
    if view_name.endswith('_subset'):
      subset_id = url_params['subset_id']
      url_params.pop('subset_id')
      response = self.client.get(reverse(
        'datenmanagement:' + view_name,
        args=[subset_id]
      ), url_params)
    else:
      response = self.client.get(reverse('datenmanagement:' + view_name), url_params)
    # Status-Code der Antwort wie erwartet?
    self.assertEqual(response.status_code, status_code)
    # Content-Type der Antwort wie erwartet?
    self.assertEqual(response['content-type'].lower(), content_type)
    # Antwort enthält bestimmten Wert?
    if 'json' in response['content-type'].lower():
      self.assertIn(string, str(loads(response.content)))
    else:
      self.assertIn(string, str(response.content))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @override_settings(MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage')
  def generic_add_update_view_test(self, update_mode, model, object_filter,
                                   status_code, content_type, object_count,
                                   file=None, file_attribute=None, file_content_type=None,
                                   multiple_files=False):
    """
    testet den View zur Erstellung oder Aktualisierung
    eines (neuen) Objekts des übergebenen Datenmodells

    :param self
    :param update_mode: Aktualisierungsmodus?
    :param model: Datenmodell
    :param object_filter: Objektfilter
    :param status_code: Status-Code, den die Antwort aufweisen soll
    :param content_type: Content-Type, den die Antwort aufweisen soll
    :param object_count: Anzahl der Objekte, die am Ende gefunden werden sollen
    :param file: Datei
    :param file_attribute: Attribut für Datei
    :param file_content_type: Content-Type der Datei
    :param multiple_files: mehrere Dateien behandeln?
    """
    # Login durchführen und alle notwendigen Berechtigungen setzen
    self.login_assign_permissions(model)
    # Seite aufrufen und via POST notwendige Daten mitgeben
    factory = RequestFactory()
    if update_mode:
      url = reverse(
        'datenmanagement:' + self.model.__name__ + '_change',
        args=[model.objects.last().pk]
      )
    else:
      url = reverse('datenmanagement:' + self.model.__name__ + '_add')
    data = object_filter
    # Dateien-Attribute korrekt in POST einfügen
    if file and file_attribute:
      # falls mehrere Dateien behandelt werden sollen...
      if multiple_files:
        # ...erhöht sich die Anzahl der Objekte, die am Ende gefunden werden sollen, um zwei
        object_count += 2
        data[file_attribute] = [
          SimpleUploadedFile(file.name, open(file, 'rb').read(), file_content_type),
          SimpleUploadedFile(file.name, open(file, 'rb').read(), file_content_type),
          SimpleUploadedFile(file.name, open(file, 'rb').read(), file_content_type)
        ]
      else:
        with open(file, 'rb') as f:
          file_upload = SimpleUploadedFile(file.name, f.read(), file_content_type)
          data[file_attribute] = file_upload
    request = factory.post(
      url,
      data=data
    )
    request.user = self.test_user
    request._messages = storage.default_storage(request)
    template_name = 'datenmanagement/form.html'
    success_url = reverse_lazy('datenmanagement:' + self.model.__name__ + '_start')
    # Status-Code der Antwort wie erwartet?
    if update_mode:
      response = DataChangeView.as_view(
        model=model,
        template_name=template_name,
        success_url=success_url
      )(request, pk=model.objects.last().pk)
    else:
      response = DataAddView.as_view(
        model=model,
        template_name=template_name,
        success_url=success_url
      )(request)
    self.assertEqual(response.status_code, status_code)
    # Content-Type der Antwort wie erwartet?
    self.assertEqual(response['content-type'].lower(), content_type)
    # Objektfilter bereinigen
    object_filter = clean_object_filter(model, object_filter)
    # Konstellation der Objekte wie erwartet?
    # bei Fehler...
    if object_count == 0:
      # fehlerhaftes Objekt erst gar nicht erstellt oder aktualisiert?
      # Anmerkung: Bei einem leeren Objektfilter werden alle Objekte gefunden.
      # Da aber bei einem leeren Objektfilter die Absicht zu unterstellen ist,
      # dass nichts gefunden werden soll, wird in diesem Fall die Objektmenge auf 0 gesetzt.
      num_objects = model.objects.filter(**object_filter).count()
      if object_filter == {}:
        num_objects = 0
      self.assertEqual(num_objects, object_count)
    # bei Erfolg...
    else:
      if update_mode:
        # aktualisiertes Objekt umfasst in einem seiner Felder eine bestimmte Information?
        self.assertEqual(model.objects.filter(**object_filter).count(), object_count)
      else:
        # erstelltes Objekt umfasst in einem seiner Felder eine bestimmte Information?
        # Anmerkung: Es können hier auch mehrere Objekt gefunden werden (daher assertGreaterEqual),
        # zum Beispiel bei Datenmodellen, die ausschließlich Pflichtattribute aufweisen!
        self.assertGreaterEqual(model.objects.filter(**object_filter).count(), object_count)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @override_settings(MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage')
  def generic_delete_view_test(self, immediately, model, object_filter, status_code, content_type):
    """
    testet den View zur Löschung
    eines Objekts des übergebenen Datenmodells

    :param self
    :param immediately: sofort löschen (ohne View)?
    :param model: Datenmodell
    :param object_filter: Objektfilter
    :param status_code: Status-Code, den die Antwort aufweisen soll
    :param content_type: Content-Type, den die Antwort aufweisen soll
    """
    # Login durchführen und alle notwendigen Berechtigungen setzen
    self.login_assign_permissions(model)
    # Objektfilter bereinigen
    object_filter = clean_object_filter(model, object_filter)
    # Seite aufrufen und via POST notwendige Daten mitgeben
    deletion_object = get_object(model, object_filter)
    if immediately:
      response = self.client.get(
        reverse(
          'datenmanagement:' + self.model.__name__ + '_deleteimmediately',
          args=[deletion_object.pk]
        )
      )
    else:
      factory = RequestFactory()
      request = factory.post(
        reverse(
          'datenmanagement:' + self.model.__name__ + '_delete',
          args=[deletion_object.pk]
        )
      )
      request.user = self.test_user
      request._messages = storage.default_storage(request)
      template_name = 'datenmanagement/form.html'
      success_url = reverse_lazy('datenmanagement:' + self.model.__name__ + '_start')
      # Status-Code der Antwort wie erwartet?
      response = DataDeleteView.as_view(
        model=model,
        template_name=template_name,
        success_url=success_url
      )(request, pk=deletion_object.pk)
    self.assertEqual(response.status_code, status_code)
    # Content-Type der Antwort wie erwartet?
    self.assertEqual(response['content-type'].lower(), content_type)
    # Objekt nicht mehr vorhanden?
    self.assertEqual(model.objects.filter(**object_filter).count(), 0)


class DefaultMetaModelTestCase(DefaultModelTestCase):
  """
  Standardtest für Meta-Datenmodelle
  """

  def init(self):
    super().init()

  def generic_is_metamodel_test(self, model):
    """
    testet, ob das Datenmodell ein Meta-Datenmodell ist

    :param self
    :param model: Datenmodell
    """
    # Datenmodell als Meta-Datenmodell deklariert?
    self.assertTrue(
      hasattr(model._meta, 'metamodel')
      and model._meta.metamodel is True
    )
    # Datenmodell nicht bearbeitbar?
    self.assertTrue(
      hasattr(model._meta, 'editable')
      and model._meta.editable is False
    )


class DefaultCodelistTestCase(DefaultModelTestCase):
  """
  Standardtest für Codelisten
  """

  def init(self):
    super().init()

  def generic_is_codelist_test(self, model):
    """
    testet, ob das Datenmodell eine Codeliste ist

    :param self
    :param model: Datenmodell
    """
    # Datenmodell als Codeliste deklariert?
    self.assertTrue(
      hasattr(model._meta, 'codelist')
      and model._meta.codelist is True
    )


class DefaultSimpleModelTestCase(DefaultModelTestCase):
  """
  Standardtest für einfache Datenmodelle
  """

  def init(self):
    super().init()

  def generic_is_simplemodel_test(self, model):
    """
    testet, ob das Datenmodell ein einfaches Datenmodell ist

    :param self
    :param model: Datenmodell
    """
    # Datenmodell als einfaches Datenmodell deklariert?
    self.assertTrue(
      (not hasattr(model._meta, 'metamodel') or model._meta.metamodel is False)
      and (not hasattr(model._meta, 'codelist') or model._meta.codelist is False)
      and (not hasattr(model._meta, 'complex') or model._meta.complex is False)
    )


class DefaultComplexModelTestCase(DefaultModelTestCase):
  """
  Standardtest für komplexe Datenmodelle
  """

  def init(self):
    super().init()

  def generic_is_complexmodel_test(self, model):
    """
    testet, ob das Datenmodell ein komplexes Datenmodell ist

    :param self
    :param model: Datenmodell
    """
    # Datenmodell als komplexes Datenmodell deklariert?
    self.assertTrue(
      (not hasattr(model._meta, 'metamodel') or model._meta.metamodel is False)
      and (not hasattr(model._meta, 'codelist') or model._meta.codelist is False)
      and hasattr(model._meta, 'complex')
      and model._meta.complex is True
    )


class GenericRSAGTestCase(DefaultComplexModelTestCase):
  """
  Standardtest für RSAG-Datenmodelle
  """

  attributes_values_db_initial = {
    'quelle': 'Quelle1',
    'geometrie': VALID_LINE_DB
  }
  attributes_values_db_updated = {
    'quelle': 'Quelle2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'quelle': 'Quelle3',
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'quelle': 'Quelle4',
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_invalid = {
    'quelle': INVALID_STRING
  }

  def init(self):
    super().init()


class GISFiletoGeoJSONTestCase(DefaultTestCase):
  """
  Standardtest für Übergabe einer Datei an FME Server und Rückgabe des generierten GeoJSON
  (abstrakt)
  """

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()

  def init(self):
    super().init()

  def generic_view_test(self, file, file_parameter, status_code, string):
    """
    testet den View

    :param self
    :param file: Datei
    :param file_parameter: POST-Parameter mit Datei
    :param status_code: Status-Code, den die Antwort aufweisen soll
    :param string: bestimmter Wert, der in Antwort enthalten sein soll
    """
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # Seite aufrufen und via POST notwendige Daten mitgeben
    with open(file, 'rb') as file_data:
      response = self.client.post(
        reverse('datenmanagement:gisfiletogeojson'),
        data={
          file_parameter: file_data
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
