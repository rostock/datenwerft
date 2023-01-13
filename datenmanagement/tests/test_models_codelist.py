from datenmanagement.models import Adressen, Strassen, Anbieter_Carsharing

from .base import DefaultTestCase
from .functions import load_sql_schema


#
# Meta-Datenmodelle
#

class AdressenTest(DefaultTestCase):
  """
  Testklasse für Adressen
  """

  INITIAL = 'Deppendorfer Str. 23a'
  UPDATED = 'Suppenkasperweg 42'

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()
    cls.test_object = Adressen.objects.create(adresse=cls.INITIAL)

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    # Datenmodell als Meta-Datenmodell deklariert?
    self.assertTrue(
      hasattr(Adressen._meta, 'metamodel')
      and Adressen._meta.metamodel is True
    )
    # Datenmodell nicht bearbeitbar?
    self.assertTrue(
      hasattr(Adressen._meta, 'editable')
      and Adressen._meta.editable is False
    )

  def test_create(self):
    # genau ein Objekt erstellt?
    self.assertEqual(Adressen.objects.all().count(), 1)
    # erstelltes Objekt wie erwartet erstellt?
    test_object = Adressen.objects.get(adresse=self.INITIAL)
    self.assertEqual(test_object, self.test_object)
    # erstelltes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(Adressen.objects.filter(adresse=self.INITIAL).count(), 1)
    # erstelltes Objekt umfasst ein UUID-Feld, das als Primärschlüssel deklariert ist?
    self.assertEqual(test_object.pk, test_object.uuid)

  def test_update(self):
    self.test_object.adresse = self.UPDATED
    self.test_object.save()
    # existiert nach der Aktualisierung immer noch genau ein Objekt?
    self.assertEqual(Adressen.objects.all().count(), 1)
    # aktualisiertes Objekt wie erwartet aktualisiert?
    test_object = Adressen.objects.get(adresse=self.UPDATED)
    self.assertEqual(test_object, self.test_object)
    # aktualisiertes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(Adressen.objects.filter(adresse=self.UPDATED).count(), 1)

  def test_delete(self):
    # keine Objekte mehr vorhanden?
    self.test_object.delete()
    self.assertEqual(Adressen.objects.all().count(), 0)


class StrassenTest(DefaultTestCase):
  """
  Testklasse für Straßen
  """

  INITIAL = 'Deppendorfer Str.'
  UPDATED = 'Suppenkasperweg'

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()
    cls.test_object = Strassen.objects.create(strasse=cls.INITIAL)

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    # Datenmodell als Meta-Datenmodell deklariert?
    self.assertTrue(
      hasattr(Strassen._meta, 'metamodel')
      and Strassen._meta.metamodel is True
    )
    # Datenmodell nicht bearbeitbar?
    self.assertTrue(
      hasattr(Strassen._meta, 'editable')
      and Strassen._meta.editable is False
    )

  def test_create(self):
    # genau ein Objekt erstellt?
    self.assertEqual(Strassen.objects.all().count(), 1)
    # erstelltes Objekt wie erwartet erstellt?
    test_object = Strassen.objects.get(strasse=self.INITIAL)
    self.assertEqual(test_object, self.test_object)
    # erstelltes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(Strassen.objects.filter(strasse=self.INITIAL).count(), 1)
    # erstelltes Objekt umfasst ein UUID-Feld, das als Primärschlüssel deklariert ist?
    self.assertEqual(test_object.pk, test_object.uuid)

  def test_update(self):
    self.test_object.strasse = self.UPDATED
    self.test_object.save()
    # existiert nach der Aktualisierung immer noch genau ein Objekt?
    self.assertEqual(Strassen.objects.all().count(), 1)
    # aktualisiertes Objekt wie erwartet aktualisiert?
    test_object = Strassen.objects.get(strasse=self.UPDATED)
    self.assertEqual(test_object, self.test_object)
    # aktualisiertes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(Strassen.objects.filter(strasse=self.UPDATED).count(), 1)

  def test_delete(self):
    # keine Objekte mehr vorhanden?
    self.test_object.delete()
    self.assertEqual(Strassen.objects.all().count(), 0)


#
# Codelisten
#

class AnbieterCarsharingTest(DefaultTestCase):
  """
  Testklasse für Carsharing-Anbieter
  """

  INITIAL = 'Deppendorf GmbH & Co. KG'
  UPDATED = 'Suppenkasper AG'

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()
    cls.test_object = Anbieter_Carsharing.objects.create(anbieter=cls.INITIAL)

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    # Datenmodell als Codeliste deklariert?
    self.assertTrue(
      hasattr(Anbieter_Carsharing._meta, 'codelist')
      and Anbieter_Carsharing._meta.codelist is True
    )

  def test_create(self):
    # genau ein Objekt erstellt?
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    # erstelltes Objekt wie erwartet erstellt?
    test_object = Anbieter_Carsharing.objects.get(anbieter=self.INITIAL)
    self.assertEqual(test_object, self.test_object)
    # erstelltes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(Anbieter_Carsharing.objects.filter(anbieter=self.INITIAL).count(), 1)
    # erstelltes Objekt umfasst ein UUID-Feld, das als Primärschlüssel deklariert ist?
    self.assertEqual(test_object.pk, test_object.uuid)

  def test_update(self):
    self.test_object.anbieter = self.UPDATED
    self.test_object.save()
    # existiert nach der Aktualisierung immer noch genau ein Objekt?
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    # aktualisiertes Objekt wie erwartet aktualisiert?
    test_object = Anbieter_Carsharing.objects.get(anbieter=self.UPDATED)
    self.assertEqual(test_object, self.test_object)
    # aktualisiertes Objekt umfasst in einem seiner Felder eine bestimmte Information?
    self.assertEqual(Anbieter_Carsharing.objects.filter(anbieter=self.UPDATED).count(), 1)

  def test_delete(self):
    # keine Objekte mehr vorhanden?
    self.test_object.delete()
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 0)
