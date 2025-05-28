from gdihrocodelists.models import (
  Codelist,
  CodelistValue,
)

from ..abstract import DefaultModelTestCase


class CodelistModelTest(DefaultModelTestCase):
  """
  test class for model:
  codelist (Codeliste)
  """

  model = Codelist
  attributes_values_db_initial = {
    'name': 'initial',
    'title': 'InitialCodelist',
  }
  attributes_values_db_updated = {
    'name': 'updated',
    'title': 'UpdatedCodelist',
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
    expected = f'{self.test_object.title} ({self.test_object.name})'
    self.generic_string_representation_test(expected)


class CodelistValueModelTest(DefaultModelTestCase):
  """
  test class for model:
  codelist value (Codelistenwert)
  """

  model = CodelistValue
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_codelist = Codelist.objects.create(name='test', title='TestCodelist')
    cls.attributes_values_db_initial = {
      'codelist': test_codelist,
      'value': 'initial',
      'title': 'InitialCodelistValue',
    }
    cls.attributes_values_db_updated = {
      'ordinal': 42,
      'title': 'UpdatedCodelistValue',
      'description': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam.',
      'details': '{ "lorem_ipsum": "dolor sit amet", "consetetur_sadipscing": 23 }',
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
    codelist_string = f'{self.test_object.codelist.title} ({self.test_object.codelist.name})'
    object_string = f'{self.test_object.title} ({self.test_object.value})'
    self.generic_string_representation_test(f'{codelist_string} → {object_string}')
