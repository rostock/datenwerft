from bemas.models import Organization, Person
from .base import DefaultModelTestCase


#
# object classes
#


class OrganizationModelTest(DefaultModelTestCase):
  """
  model test class for object class organization (Organisation)
  """

  model = Organization
  attributes_values_db_initial = {
    'name': 'arTc9w6J'
  }
  attributes_values_db_updated = {
    'name': 'g4Wsx9jj'
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class PersonModelTest(DefaultModelTestCase):
  """
  model test class for object class person (Person)
  """

  model = Person
  attributes_values_db_initial = {
    'last_name': 'g7QXisvP'
  }
  attributes_values_db_updated = {
    'last_name': 'CkLihFLE'
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()
