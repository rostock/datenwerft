from fmm.models import (
  InformationspaketUmwelt,
  Stammpaket,
)

from ..abstract import DefaultModelTestCase
from ..constants_vars import (
  VALID_MULTIPOLYGON_DB_A,
  VALID_MULTIPOLYGON_DB_B,
  VALID_STRING_A,
  VALID_STRING_B,
)


class StammpaketModelTest(DefaultModelTestCase):
  """
  test class for model:
  Stammpaket
  """

  model = Stammpaket
  attributes_values_db_initial = {
    'bezeichnung': VALID_STRING_A,
    'geometrie': VALID_MULTIPOLYGON_DB_A,
  }
  attributes_values_db_updated = {
    'bezeichnung': VALID_STRING_B,
    'geometrie': VALID_MULTIPOLYGON_DB_B,
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    expected = f'{self.test_object.bezeichnung}'
    self.generic_string_representation_test(expected)


class InformationspaketUmweltModelTest(DefaultModelTestCase):
  """
  test class for model:
  Informationspaket Umwelt
  """

  model = InformationspaketUmwelt
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_stammpaket_a = Stammpaket.objects.create(
      bezeichnung=VALID_STRING_A,
      geometrie=VALID_MULTIPOLYGON_DB_A,
    )
    cls.attributes_values_db_initial = {
      'stammpaket': test_stammpaket_a,
      'trinkwassernotbrunnen': False,
    }
    test_stammpaket_b = Stammpaket.objects.create(
      bezeichnung=VALID_STRING_B,
      geometrie=VALID_MULTIPOLYGON_DB_B,
    )
    cls.attributes_values_db_updated = {
      'stammpaket': test_stammpaket_b,
      'trinkwassernotbrunnen': True,
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    stammpaket_bezeichnung = f'{self.test_object.stammpaket.bezeichnung}'
    created = f'erstellt am {self.test_object.created.strftime("%d.%m.%Y")}'
    modified = f'geändert am {self.test_object.modified.strftime("%d.%m.%Y")}'
    expected = f'{stammpaket_bezeichnung} → Informationspaket Umwelt ({created}, {modified})'
    self.generic_string_representation_test(expected)
