from django.db.models import Max

from bemas.models import Sector, Status, TypeOfEvent, TypeOfImmission
from .base import DefaultCodelistTestCase, DefaultViewTestCase


#
# codelists
#

class StatusModelTest(DefaultCodelistTestCase):
  """
  model test class for codelist status (Bearbeitungsstatus)
  """

  model = Status
  count = Status.objects.count()
  # get current max value of column ordinal
  ordinal_max = Status.objects.aggregate(Max('ordinal')).get('ordinal__max', 0)
  attributes_values_db_initial = {
    'ordinal': ordinal_max + 1,
    'title': 'I0JBAMtz',
    'icon': '3jw5UCfJ'
  }
  attributes_values_db_updated = {
    'ordinal': ordinal_max + 2,
    'title': '4Ke2ZalC',
    'icon': '3ZtNGShd'
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


class StatusViewsTest(DefaultViewTestCase):
  """
  views test class for codelist status (Bearbeitungsstatus)
  """

  def setUp(self):
    self.init()

  def test_index_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_status', 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_index_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_status', 200,
      'text/html; charset=utf-8', 'auflisten'
    )

  def test_index_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_status', 200,
      'text/html; charset=utf-8', 'anlegen'
    )


class SectorModelTest(DefaultCodelistTestCase):
  """
  model test class for codelist sector (Branche)
  """

  model = Sector
  count = Sector.objects.count()
  attributes_values_db_initial = {
    'title': 'hFxVbEb2'
  }
  attributes_values_db_updated = {
    'title': 'HFGXNmxC'
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


class SectorViewsTest(DefaultViewTestCase):
  """
  views test class for codelist sector (Branche)
  """

  def setUp(self):
    self.init()

  def test_index_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_sector', 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_index_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_sector', 200,
      'text/html; charset=utf-8', 'auflisten'
    )

  def test_index_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_sector', 200,
      'text/html; charset=utf-8', 'anlegen'
    )


class TypeOfEventModelTest(DefaultCodelistTestCase):
  """
  model test class for codelist type of event (Ereignisart)
  """

  model = TypeOfEvent
  count = TypeOfEvent.objects.count()
  attributes_values_db_initial = {
    'title': 'UIO0F3n8',
    'icon': 'qgzUK9gf'
  }
  attributes_values_db_updated = {
    'title': 'o3XwyDzw',
    'icon': 'svNUGQAd'
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


class TypeOfEventViewsTest(DefaultViewTestCase):
  """
  views test class for codelist type of event (Ereignisart)
  """

  def setUp(self):
    self.init()

  def test_index_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofevent', 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_index_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofevent', 200,
      'text/html; charset=utf-8', 'auflisten'
    )

  def test_index_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofevent', 200,
      'text/html; charset=utf-8', 'anlegen'
    )


class TypeOfImmissionModelTest(DefaultCodelistTestCase):
  """
  model test class for codelist type of immission (Immissionsart)
  """

  model = TypeOfImmission
  count = TypeOfImmission.objects.count()
  attributes_values_db_initial = {
    'title': 'eaDUeltd',
    'icon': 'wLIe5cDw'
  }
  attributes_values_db_updated = {
    'title': 'mNyvaDBE',
    'icon': 'WMEmWR5M'
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


class TypeOfImmissionViewsTest(DefaultViewTestCase):
  """
  views test class for codelist type of immission (Immissionsart)
  """

  def setUp(self):
    self.init()

  def test_index_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofimmission', 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_index_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofimmission', 200,
      'text/html; charset=utf-8', 'auflisten'
    )

  def test_index_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofimmission', 200,
      'text/html; charset=utf-8', 'anlegen'
    )


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
      False, False, 'index', 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'index', 200,
      'text/html; charset=utf-8', 'Codelisten'
    )


class CodelistsIndexViewTest(DefaultViewTestCase):
  """
  test class for codelists entry page
  """

  def setUp(self):
    self.init()

  def test_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists', 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists', 200,
      'text/html; charset=utf-8', 'Codelisten'
    )
