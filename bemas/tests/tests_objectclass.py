from bemas.models import Address, Organization, Person
from .base import DefaultModelTestCase


#
# object classes
#

class AddressModelTest(DefaultModelTestCase):
  """
  model test class for object class address (Anschrift)
  """

  model = Address
  attributes_values_db_initial = {
    'street': 'UekrRtHY',
    'house_number': 23,
    'postal_code': '12345',
    'place': 'vq54YS4o'
  }
  attributes_values_db_updated = {
    'street': 'c6zalxog',
    'house_number': 42,
    'postal_code': '54321',
    'place': 'TNjVmNPH'
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


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
