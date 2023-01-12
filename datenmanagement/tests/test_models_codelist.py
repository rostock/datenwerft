from datenmanagement.models import Adressen, Strassen, Anbieter_Carsharing

from . import classes, functions


class AdressenTest(classes.DefaultModelTestCase):
  INITIAL = 'Deppendorfer Str. 23a'
  UPDATED = 'Suppenkasperweg 42'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.test_object = Adressen.objects.create(adresse=cls.INITIAL)

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
    test_object = Adressen.objects.get(adresse=self.INITIAL)
    self.assertEqual(test_object, self.test_object)
    # created object contains specific value in one of its fields?
    self.assertEqual(Adressen.objects.filter(adresse=self.INITIAL).count(), 1)
    # created object has UUID field which is defined as primary key?
    self.assertEqual(test_object.pk, test_object.uuid)

  def test_update(self):
    self.test_object.adresse = self.UPDATED
    self.test_object.save()
    # still exactly one object?
    self.assertEqual(Adressen.objects.all().count(), 1)
    # object updated exactly as it should have been updated?
    test_object = Adressen.objects.get(adresse=self.UPDATED)
    self.assertEqual(test_object, self.test_object)
    # exactly one (i.e. the updated) object contains specific value in one of its fields?
    self.assertEqual(Adressen.objects.filter(adresse=self.UPDATED).count(), 1)

  def test_delete(self):
    # no more objects left?
    self.test_object.delete()
    self.assertEqual(Adressen.objects.all().count(), 0)


class StrassenTest(classes.DefaultModelTestCase):
  INITIAL = 'Deppendorfer Str.'
  UPDATED = 'Suppenkasperweg'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.test_object = Strassen.objects.create(strasse=cls.INITIAL)

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
    test_object = Strassen.objects.get(strasse=self.INITIAL)
    self.assertEqual(test_object, self.test_object)
    # created object contains specific value in one of its fields?
    self.assertEqual(Strassen.objects.filter(strasse=self.INITIAL).count(), 1)
    # created object has UUID field which is defined as primary key?
    self.assertEqual(test_object.pk, test_object.uuid)

  def test_update(self):
    self.test_object.strasse = self.UPDATED
    self.test_object.save()
    # still exactly one object?
    self.assertEqual(Strassen.objects.all().count(), 1)
    # object updated exactly as it should have been updated?
    test_object = Strassen.objects.get(strasse=self.UPDATED)
    self.assertEqual(test_object, self.test_object)
    # exactly one (i.e. the updated) object contains specific value in one of its fields?
    self.assertEqual(Strassen.objects.filter(strasse=self.UPDATED).count(), 1)

  def test_delete(self):
    # no more objects left?
    self.test_object.delete()
    self.assertEqual(Strassen.objects.all().count(), 0)


class AnbieterCarsharingTest(classes.DefaultModelTestCase):
  INITIAL = 'Deppendorf GmbH & Co. KG'
  UPDATED = 'Suppenkasper AG'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.test_object = Anbieter_Carsharing.objects.create(anbieter=cls.INITIAL)

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
    test_object = Anbieter_Carsharing.objects.get(anbieter=self.INITIAL)
    self.assertEqual(test_object, self.test_object)
    # created object contains specific value in one of its fields?
    self.assertEqual(Anbieter_Carsharing.objects.filter(anbieter=self.INITIAL).count(), 1)
    # created object has UUID field which is defined as primary key?
    self.assertEqual(test_object.pk, test_object.uuid)

  def test_update(self):
    self.test_object.anbieter = self.UPDATED
    self.test_object.save()
    # still exactly one object?
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    # object updated exactly as it should have been updated?
    test_object = Anbieter_Carsharing.objects.get(anbieter=self.UPDATED)
    self.assertEqual(test_object, self.test_object)
    # exactly one (i.e. the updated) object contains specific value in one of its fields?
    self.assertEqual(Anbieter_Carsharing.objects.filter(anbieter=self.UPDATED).count(), 1)

  def test_delete(self):
    # no more objects left?
    self.test_object.delete()
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 0)
