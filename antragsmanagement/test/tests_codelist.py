from antragsmanagement.models import CodelistRequestStatus, CleanupEventCodelistWasteQuantity, \
  CleanupEventCodelistWasteType, CleanupEventCodelistEquipment
from .base import DefaultCodelistTestCase


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
  attributes_values_db_initial = {
    'ordinal': 4,
    'name': 'I0JBAMtz',
    'icon': '3jw5UCfJ'
  }
  attributes_values_db_updated = {
    'ordinal': 5,
    'name': '4Ke2ZalC',
    'icon': '3ZtNGShd'
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
  attributes_values_db_initial = {
    'ordinal': 4,
    'name': 'I0JBAMtz'
  }
  attributes_values_db_updated = {
    'ordinal': 5,
    'name': '4Ke2ZalC'
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
  attributes_values_db_initial = {
    'name': 'I0JBAMtz'
  }
  attributes_values_db_updated = {
    'name': '4Ke2ZalC'
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
  attributes_values_db_initial = {
    'name': 'I0JBAMtz'
  }
  attributes_values_db_updated = {
    'name': '4Ke2ZalC'
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
