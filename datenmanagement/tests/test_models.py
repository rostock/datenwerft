from django.db import connections
from django.test import TestCase
from datenmanagement.models import Anbieter_Carsharing
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


class AnbieterCarsharingCRUDTest(TestCase):
  databases = {
    'default',
    'datenmanagement'
  }
  text_a = 'Deppendorf GmbH & Co. KG'
  text_b = 'Suppenkasper AG'

  @classmethod
  def setUpTestData(cls):
    schema_file = open(BASE_DIR / 'sql/schema.sql', 'r')
    schema_sql = schema_file.read()
    with connections['datenmanagement'].cursor() as cursor:
      cursor.execute(schema_sql)
    cls.anbieter_carsharing = Anbieter_Carsharing.objects.create(anbieter=cls.text_a)

  def test_create(self):
    anbieter_carsharing = Anbieter_Carsharing.objects.get(anbieter=self.text_a)
    self.assertIsInstance(anbieter_carsharing, Anbieter_Carsharing)
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    self.assertEqual(anbieter_carsharing, self.anbieter_carsharing)

  def test_update(self):
    self.anbieter_carsharing.anbieter = self.text_b
    self.anbieter_carsharing.save()
    anbieter_carsharing = Anbieter_Carsharing.objects.get(anbieter=self.text_b)
    self.assertIsInstance(anbieter_carsharing, Anbieter_Carsharing)
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    self.assertEqual(anbieter_carsharing, self.anbieter_carsharing)

  def test_delete(self):
    self.anbieter_carsharing.delete()
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 0)
    with self.assertRaises(Anbieter_Carsharing.DoesNotExist):
      Anbieter_Carsharing.objects.get(anbieter=self.text_a)
