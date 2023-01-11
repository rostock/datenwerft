from datenmanagement.models import Adressen, Strassen, Anbieter_Carsharing

from . import classes, functions


class AdressenTest(classes.DefaultModelTestCase):
  ADRESSE_INITIAL = 'Deppendorfer Str. 23a'
  ADRESSE_UPDATED = 'Suppenkasperweg 42'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.adresse = Adressen.objects.create(adresse=cls.ADRESSE_INITIAL)

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    # model declared as meta-model?
    self.assertTrue(
      hasattr(Adressen._meta, 'metamodel')
      and Adressen._meta.metamodel is True
    )
    # model not editable?
    self.assertTrue(
      hasattr(Adressen._meta, 'editable')
      and Adressen._meta.editable is False
    )

  def test_create(self):
    # exactly one object created?
    self.assertEqual(Adressen.objects.all().count(), 1)
    # object created exactly as it should have been created?
    adresse = Adressen.objects.get(adresse=self.ADRESSE_INITIAL)
    self.assertEqual(adresse, self.adresse)
    # created object contains specific value in one of its fields?
    self.assertEqual(Adressen.objects.filter(adresse=self.ADRESSE_INITIAL).count(), 1)
    # created object has UUID field which is defined as primary key?
    self.assertEqual(adresse.pk, adresse.uuid)

  def test_update(self):
    self.adresse.adresse = self.ADRESSE_UPDATED
    self.adresse.save()
    # still exactly one object?
    self.assertEqual(Adressen.objects.all().count(), 1)
    # object updated exactly as it should have been updated?
    adresse = Adressen.objects.get(adresse=self.ADRESSE_UPDATED)
    self.assertEqual(adresse, self.adresse)
    # exactly one (i.e. the updated) object contains specific value in one of its fields?
    self.assertEqual(Adressen.objects.filter(adresse=self.ADRESSE_UPDATED).count(), 1)

  def test_delete(self):
    # no more objects left?
    self.adresse.delete()
    self.assertEqual(Adressen.objects.all().count(), 0)


class StrassenTest(classes.DefaultModelTestCase):
  STRASSE_INITIAL = 'Deppendorfer Str.'
  STRASSE_UPDATED = 'Suppenkasperweg'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.strasse = Strassen.objects.create(strasse=cls.STRASSE_INITIAL)

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    # model declared as meta-model?
    self.assertTrue(
      hasattr(Strassen._meta, 'metamodel')
      and Strassen._meta.metamodel is True
    )
    # model not editable?
    self.assertTrue(
      hasattr(Strassen._meta, 'editable')
      and Strassen._meta.editable is False
    )

  def test_create(self):
    # exactly one object created?
    self.assertEqual(Strassen.objects.all().count(), 1)
    # object created exactly as it should have been created?
    strasse = Strassen.objects.get(strasse=self.STRASSE_INITIAL)
    self.assertEqual(strasse, self.strasse)
    # created object contains specific value in one of its fields?
    self.assertEqual(Strassen.objects.filter(strasse=self.STRASSE_INITIAL).count(), 1)
    # created object has UUID field which is defined as primary key?
    self.assertEqual(strasse.pk, strasse.uuid)

  def test_update(self):
    self.strasse.strasse = self.STRASSE_UPDATED
    self.strasse.save()
    # still exactly one object?
    self.assertEqual(Strassen.objects.all().count(), 1)
    # object updated exactly as it should have been updated?
    strasse = Strassen.objects.get(strasse=self.STRASSE_UPDATED)
    self.assertEqual(strasse, self.strasse)
    # exactly one (i.e. the updated) object contains specific value in one of its fields?
    self.assertEqual(Strassen.objects.filter(strasse=self.STRASSE_UPDATED).count(), 1)

  def test_delete(self):
    # no more objects left?
    self.strasse.delete()
    self.assertEqual(Strassen.objects.all().count(), 0)


class AnbieterCarsharingTest(classes.DefaultModelTestCase):
  ANBIETER_INITIAL = 'Deppendorf GmbH & Co. KG'
  ANBIETER_UPDATED = 'Suppenkasper AG'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.anbieter_carsharing = Anbieter_Carsharing.objects.create(anbieter=cls.ANBIETER_INITIAL)

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    # model declared as codelist?
    self.assertTrue(
      hasattr(Anbieter_Carsharing._meta, 'codelist')
      and Anbieter_Carsharing._meta.codelist is True
    )

  def test_create(self):
    # exactly one object created?
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    # object created exactly as it should have been created?
    anbieter_carsharing = Anbieter_Carsharing.objects.get(anbieter=self.ANBIETER_INITIAL)
    self.assertEqual(anbieter_carsharing, self.anbieter_carsharing)
    # created object contains specific value in one of its fields?
    self.assertEqual(Anbieter_Carsharing.objects.filter(anbieter=self.ANBIETER_INITIAL).count(), 1)
    # created object has UUID field which is defined as primary key?
    self.assertEqual(anbieter_carsharing.pk, anbieter_carsharing.uuid)

  def test_update(self):
    self.anbieter_carsharing.anbieter = self.ANBIETER_UPDATED
    self.anbieter_carsharing.save()
    # still exactly one object?
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    # object updated exactly as it should have been updated?
    anbieter_carsharing = Anbieter_Carsharing.objects.get(anbieter=self.ANBIETER_UPDATED)
    self.assertEqual(anbieter_carsharing, self.anbieter_carsharing)
    # exactly one (i.e. the updated) object contains specific value in one of its fields?
    self.assertEqual(Anbieter_Carsharing.objects.filter(anbieter=self.ANBIETER_UPDATED).count(), 1)

  def test_delete(self):
    # no more objects left?
    self.anbieter_carsharing.delete()
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 0)
