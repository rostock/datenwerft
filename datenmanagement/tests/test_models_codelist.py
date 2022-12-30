from django.test import TestCase

from datenmanagement.models import Adressen, Strassen, Anbieter_Carsharing

from . import constants_vars, functions


class AdressenTest(TestCase):
  databases = constants_vars.DATABASES
  ADRESSE_INITIAL = 'Deppendorfer Str. 23a'
  ADRESSE_UPDATED = 'Suppenkasperweg 42'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.adresse = Adressen.objects.create(adresse=cls.ADRESSE_INITIAL)

  def test_create(self):
    self.assertEqual(Adressen.objects.all().count(), 1)
    adresse = Adressen.objects.get(adresse=self.ADRESSE_INITIAL)
    self.assertEqual(adresse, self.adresse)
    self.assertEqual(Adressen.objects.filter(adresse=self.ADRESSE_INITIAL).count(), 1)

  def test_update(self):
    self.adresse.adresse = self.ADRESSE_UPDATED
    self.adresse.save()
    self.assertEqual(Adressen.objects.all().count(), 1)
    adresse = Adressen.objects.get(adresse=self.ADRESSE_UPDATED)
    self.assertEqual(adresse, self.adresse)
    self.assertEqual(Adressen.objects.filter(adresse=self.ADRESSE_UPDATED).count(), 1)

  def test_delete(self):
    self.assertEqual(Adressen.objects.all().count(), 1)
    self.adresse.delete()
    self.assertEqual(Adressen.objects.all().count(), 0)


class StrassenTest(TestCase):
  databases = constants_vars.DATABASES
  STRASSE_INITIAL = 'Deppendorfer Str.'
  STRASSE_UPDATED = 'Suppenkasperweg'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.strasse = Strassen.objects.create(strasse=cls.STRASSE_INITIAL)

  def test_create(self):
    self.assertEqual(Strassen.objects.all().count(), 1)
    strasse = Strassen.objects.get(strasse=self.STRASSE_INITIAL)
    self.assertEqual(strasse, self.strasse)
    self.assertEqual(Strassen.objects.filter(strasse=self.STRASSE_INITIAL).count(), 1)

  def test_update(self):
    self.strasse.strasse = self.STRASSE_UPDATED
    self.strasse.save()
    self.assertEqual(Strassen.objects.all().count(), 1)
    strasse = Strassen.objects.get(strasse=self.STRASSE_UPDATED)
    self.assertEqual(strasse, self.strasse)
    self.assertEqual(Strassen.objects.filter(strasse=self.STRASSE_UPDATED).count(), 1)

  def test_delete(self):
    self.assertEqual(Strassen.objects.all().count(), 1)
    self.strasse.delete()
    self.assertEqual(Strassen.objects.all().count(), 0)


class AnbieterCarsharingTest(TestCase):
  databases = constants_vars.DATABASES
  ANBIETER_INITIAL = 'Deppendorf GmbH & Co. KG'
  ANBIETER_UPDATED = 'Suppenkasper AG'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.anbieter_carsharing = Anbieter_Carsharing.objects.create(anbieter=cls.ANBIETER_INITIAL)

  def test_create(self):
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    anbieter_carsharing = Anbieter_Carsharing.objects.get(anbieter=self.ANBIETER_INITIAL)
    self.assertEqual(anbieter_carsharing, self.anbieter_carsharing)
    self.assertEqual(Anbieter_Carsharing.objects.filter(anbieter=self.ANBIETER_INITIAL).count(), 1)

  def test_update(self):
    self.anbieter_carsharing.anbieter = self.ANBIETER_UPDATED
    self.anbieter_carsharing.save()
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    anbieter_carsharing = Anbieter_Carsharing.objects.get(anbieter=self.ANBIETER_UPDATED)
    self.assertEqual(anbieter_carsharing, self.anbieter_carsharing)
    self.assertEqual(Anbieter_Carsharing.objects.filter(anbieter=self.ANBIETER_UPDATED).count(), 1)

  def test_delete(self):
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    self.anbieter_carsharing.delete()
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 0)
