from django.utils.crypto import get_random_string

from antragsmanagement.models import CodelistRequestStatus, CleanupEventCodelistWasteQuantity, \
  CleanupEventCodelistWasteType, CleanupEventCodelistEquipment
from antragsmanagement.test.base import DefaultCodelistTestCase


#
# general codelists
#

class CodelistRequestStatusTest(DefaultCodelistTestCase):
  """
  test class for general codelist:
  request status (Antragsstatus)
  """

  model = CodelistRequestStatus
  count = 4
  attributes_values_db_create = {
    'ordinal': 4,
    'name': get_random_string(length=12),
    'icon': get_random_string(length=12)
  }
  attributes_values_db_update = {
    'ordinal': 5,
    'name': get_random_string(length=12),
    'icon': get_random_string(length=12)
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


#
# codelists for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventCodelistWasteQuantityTest(DefaultCodelistTestCase):
  """
  test class for codelist for request type clean-up events (Müllsammelaktionen):
  waste quantity (Abfallmenge)
  """

  model = CleanupEventCodelistWasteQuantity
  count = 4
  attributes_values_db_create = {
    'ordinal': 4,
    'name': get_random_string(length=12)
  }
  attributes_values_db_update = {
    'ordinal': 5,
    'name': get_random_string(length=12)
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CleanupEventCodelistWasteTypeTest(DefaultCodelistTestCase):
  """
  test class for codelist for request type clean-up events (Müllsammelaktionen):
  waste type (Abfallart)
  """

  model = CleanupEventCodelistWasteType
  count = 6
  attributes_values_db_create = {
    'name': get_random_string(length=12)
  }
  attributes_values_db_update = {
    'name': get_random_string(length=12)
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CleanupEventCodelistEquipmentTest(DefaultCodelistTestCase):
  """
  test class for codelist for request type clean-up events (Müllsammelaktionen):
  equipment (Austattung)
  """

  model = CleanupEventCodelistEquipment
  count = 5
  attributes_values_db_create = {
    'name': get_random_string(length=12)
  }
  attributes_values_db_update = {
    'name': get_random_string(length=12)
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()
