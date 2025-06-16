from fmm.models import (
  Fmf,
  PaketUmwelt,
)

from ..abstract import ModelTestCase
from ..constants_vars import (
  VALID_POLYGON_DB_A,
  VALID_POLYGON_DB_B,
  VALID_STRING_A,
  VALID_STRING_B,
)


class FmfModelTest(ModelTestCase):
  """
  test class for model:
  FMF
  """

  model = Fmf
  attributes_values_db_initial = {
    'bezeichnung': VALID_STRING_A,
    'geometrie': VALID_POLYGON_DB_A,
  }
  attributes_values_db_updated = {
    'bezeichnung': VALID_STRING_B,
    'geometrie': VALID_POLYGON_DB_B,
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


class PaketUmweltModelTest(ModelTestCase):
  """
  test class for model:
  Paket Umwelt
  """

  model = PaketUmwelt
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_fmf_a = Fmf.objects.create(
      bezeichnung=VALID_STRING_A,
      geometrie=VALID_POLYGON_DB_A,
    )
    cls.attributes_values_db_initial = {
      'fmf': test_fmf_a,
      'trinkwassernotbrunnen': False,
    }
    test_fmf_b = Fmf.objects.create(
      bezeichnung=VALID_STRING_B,
      geometrie=VALID_POLYGON_DB_B,
    )
    cls.attributes_values_db_updated = {
      'fmf': test_fmf_b,
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
    expected = (
      f'mit Erstellungszeitpunkt {self.test_object.created.strftime("%d.%m.%Y, %H:%M Uhr")}'
    )
    self.generic_string_representation_test(expected)
