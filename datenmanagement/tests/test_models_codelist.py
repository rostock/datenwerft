from django.test import override_settings
from django.urls import reverse
from datenmanagement.models import Adressen, Strassen, Anbieter_Carsharing

from .base import DefaultTestCase
from .constants_vars import *
from .functions import load_sql_schema


#
# Meta-Datenmodelle
#

class AdressenTest(DefaultTestCase):
  """
  Testklasse für Adressen
  """

  model = Adressen
  INITIAL = 'Deppendorfer Str. 23a'
  UPDATED = 'Suppenkasperweg 42'

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()
    cls.test_object = cls.model.objects.create(adresse=cls.INITIAL)

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    # Datenmodell als Meta-Datenmodell deklariert?
    self.assertTrue(
      hasattr(self.model._meta, 'metamodel')
      and self.model._meta.metamodel is True
    )
    # Datenmodell nicht bearbeitbar?
    self.assertTrue(
      hasattr(self.model._meta, 'editable')
      and self.model._meta.editable is False
    )

  def test_create(self):
    # genau ein Objekt erstellt?
    self.assertEqual(self.model.objects.all().count(), 1)
    # erstelltes Objekt wie erwartet erstellt?
    test_object = self.model.objects.get(adresse=self.INITIAL)
    self.assertEqual(test_object, self.test_object)
    # erstelltes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(self.model.objects.filter(adresse=self.INITIAL).count(), 1)
    # erstelltes Objekt umfasst ein UUID-Feld, das als Primärschlüssel deklariert ist?
    self.assertEqual(test_object.pk, test_object.uuid)

  def test_update(self):
    self.test_object.adresse = self.UPDATED
    self.test_object.save()
    # existiert nach der Aktualisierung immer noch genau ein Objekt?
    self.assertEqual(self.model.objects.all().count(), 1)
    # aktualisiertes Objekt wie erwartet aktualisiert?
    test_object = self.model.objects.get(adresse=self.UPDATED)
    self.assertEqual(test_object, self.test_object)
    # aktualisiertes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(self.model.objects.filter(adresse=self.UPDATED).count(), 1)

  def test_delete(self):
    # keine Objekte mehr vorhanden?
    self.test_object.delete()
    self.assertEqual(self.model.objects.all().count(), 0)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_start_success(self):
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    pass


class StrassenTest(DefaultTestCase):
  """
  Testklasse für Straßen
  """

  model = Strassen
  INITIAL = 'Deppendorfer Str.'
  UPDATED = 'Suppenkasperweg'

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()
    cls.test_object = cls.model.objects.create(strasse=cls.INITIAL)

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    # Datenmodell als Meta-Datenmodell deklariert?
    self.assertTrue(
      hasattr(self.model._meta, 'metamodel')
      and self.model._meta.metamodel is True
    )
    # Datenmodell nicht bearbeitbar?
    self.assertTrue(
      hasattr(self.model._meta, 'editable')
      and self.model._meta.editable is False
    )

  def test_create(self):
    # genau ein Objekt erstellt?
    self.assertEqual(self.model.objects.all().count(), 1)
    # erstelltes Objekt wie erwartet erstellt?
    test_object = self.model.objects.get(strasse=self.INITIAL)
    self.assertEqual(test_object, self.test_object)
    # erstelltes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(self.model.objects.filter(strasse=self.INITIAL).count(), 1)
    # erstelltes Objekt umfasst ein UUID-Feld, das als Primärschlüssel deklariert ist?
    self.assertEqual(test_object.pk, test_object.uuid)

  def test_update(self):
    self.test_object.strasse = self.UPDATED
    self.test_object.save()
    # existiert nach der Aktualisierung immer noch genau ein Objekt?
    self.assertEqual(self.model.objects.all().count(), 1)
    # aktualisiertes Objekt wie erwartet aktualisiert?
    test_object = self.model.objects.get(strasse=self.UPDATED)
    self.assertEqual(test_object, self.test_object)
    # aktualisiertes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(self.model.objects.filter(strasse=self.UPDATED).count(), 1)

  def test_delete(self):
    # keine Objekte mehr vorhanden?
    self.test_object.delete()
    self.assertEqual(self.model.objects.all().count(), 0)


#
# Codelisten
#

class AnbieterCarsharingTest(DefaultTestCase):
  """
  Testklasse für Carsharing-Anbieter
  """

  model = Anbieter_Carsharing
  INITIAL = 'Deppendorf GmbH & Co. KG'
  UPDATED = 'Suppenkasper AG'

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()
    cls.test_object = cls.model.objects.create(anbieter=cls.INITIAL)

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    # Datenmodell als Codeliste deklariert?
    self.assertTrue(
      hasattr(self.model._meta, 'codelist')
      and self.model._meta.codelist is True
    )

  def test_create(self):
    # genau ein Objekt erstellt?
    self.assertEqual(self.model.objects.all().count(), 1)
    # erstelltes Objekt wie erwartet erstellt?
    test_object = self.model.objects.get(anbieter=self.INITIAL)
    self.assertEqual(test_object, self.test_object)
    # erstelltes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(self.model.objects.filter(anbieter=self.INITIAL).count(), 1)
    # erstelltes Objekt umfasst ein UUID-Feld, das als Primärschlüssel deklariert ist?
    self.assertEqual(test_object.pk, test_object.uuid)

  def test_update(self):
    self.test_object.anbieter = self.UPDATED
    self.test_object.save()
    # existiert nach der Aktualisierung immer noch genau ein Objekt?
    self.assertEqual(self.model.objects.all().count(), 1)
    # aktualisiertes Objekt wie erwartet aktualisiert?
    test_object = self.model.objects.get(anbieter=self.UPDATED)
    self.assertEqual(test_object, self.test_object)
    # aktualisiertes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(self.model.objects.filter(anbieter=self.UPDATED).count(), 1)

  def test_delete(self):
    # keine Objekte mehr vorhanden?
    self.test_object.delete()
    self.assertEqual(self.model.objects.all().count(), 0)
