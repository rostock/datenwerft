from django.db.models import Max

from bemas.models import Sector, Status, TypeOfEvent, TypeOfImmission
from .base import DefaultCodelistTestCase, DefaultViewTestCase


#
# codelists
#

class StatusTest(DefaultCodelistTestCase):
  """
  test class for codelist status (Bearbeitungsstatus)
  """

  model = Status
  count = Status.objects.count()
  # get current max value of column ordinal
  ordinal_max = Status.objects.aggregate(Max('ordinal')).get('ordinal__max', 0)
  attributes_values_db_initial = {
    'ordinal': ordinal_max + 1,
    'title': 'title1',
    'icon': 'icon1'
  }
  attributes_values_db_updated = {
    'ordinal': ordinal_max + 2,
    'title': 'title2',
    'icon': 'icon2'
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test(self.model)

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)


class SectorTest(DefaultCodelistTestCase):
  """
  test class for codelist sector (Branche)
  """

  model = Sector
  count = Sector.objects.count()
  attributes_values_db_initial = {
    'title': 'title1'
  }
  attributes_values_db_updated = {
    'title': 'title2'
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test(self.model)

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)


class TypeOfEventTest(DefaultCodelistTestCase):
  """
  test class for codelist type of event (Ereignisart)
  """

  model = TypeOfEvent
  count = TypeOfEvent.objects.count()
  attributes_values_db_initial = {
    'title': 'title1',
    'icon': 'icon1'
  }
  attributes_values_db_updated = {
    'title': 'title2',
    'icon': 'icon2'
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test(self.model)

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)


class TypeOfImmissionTest(DefaultCodelistTestCase):
  """
  test class for codelist type of immission (Immissionsart)
  """

  model = TypeOfImmission
  count = TypeOfImmission.objects.count()
  attributes_values_db_initial = {
    'title': 'title1',
    'icon': 'icon1'
  }
  attributes_values_db_updated = {
    'title': 'title2',
    'icon': 'icon2'
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test(self.model)

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)


#
# general views
#

class IndexViewTest(DefaultViewTestCase):
  """
  test class for main page
  """

  def setUp(self):
    self.init()

  def test_view_no_rights(self):
    self.generic_view_test(
      False, False, 'index', 200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'index', 200, 'text/html; charset=utf-8', 'Codelisten'
    )


class CodelistsIndexViewTest(DefaultViewTestCase):
  """
  test class for codelists entry page
  """

  def setUp(self):
    self.init()

  def test_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists', 200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists', 200, 'text/html; charset=utf-8', 'Ereignisarten'
    )
