from django.contrib.auth.models import Permission, User
from django.contrib.messages import storage
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse, reverse_lazy
from json import loads
from datenmanagement.views.views_form import DataAddView, DataChangeView, DataDeleteView

from .constants_vars import *
from .functions import load_sql_schema


class DefaultTestCase(TestCase):
  """
  Standardtest (abstrakt)
  """

  databases = DATABASES

  def init(self):
    self.test_user = User.objects.create_user(
      username=USERNAME,
      password=PASSWORD
    )


class DefaultModelTestCase(DefaultTestCase):
  """
  Standardtest für Datenmodelle (abstrakt)
  """

  model = None
  attributes_values_db_initial = {}

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def init(self):
    super().init()

  @staticmethod
  def get_object(model, object_filter):
    """
    holt ein Objekt des übergebenen Datenmodells aus der Datenbank,
    auf den der übergebene Objektfilter passt, und liefert dieses zurück

    :param model: Datenmodell
    :param object_filter: Objektfilter
    :return: Objekt des übergebenen Datenmodells, auf den der übergebene Objektfilter passt
    """
    return model.objects.get(**object_filter)

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
    test_object = self.get_object(model, object_filter)
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
    test_object = self.get_object(model, object_filter)
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
                                   status_code, content_type, object_count):
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
    request = factory.post(
      url,
      data=object_filter
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
    # Konstellation der Objekte wie erwartet?
    # bei Erfolg:
    # erstelltes oder aktualisiertes Objekt
    # umfasst in einem seiner Felder eine bestimmte Information?
    # bei Fehler:
    # fehlerhaftes Objekt erst gar nicht erstellt oder aktualisiert?
    self.assertEqual(model.objects.filter(**object_filter).count(), object_count)

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
    # Seite aufrufen und via POST notwendige Daten mitgeben
    deletion_object = self.get_object(model, object_filter)
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
  Standardtest für Meta-Datenmodelle
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
