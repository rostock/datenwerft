from bemas.models import Sector, Status, TypeOfEvent, TypeOfImmission
from .base import DefaultCodelistTestCase, DefaultViewTestCase
from .constants_vars import INVALID_STRING, TABLEDATA_VIEW_PARAMS


#
# codelists
#

class StatusModelTest(DefaultCodelistTestCase):
  """
  model test class for codelist status (Bearbeitungsstatus)
  """

  model = Status
  count = 2
  attributes_values_db_initial = {
    'ordinal': 3,
    'title': 'I0JBAMtz',
    'icon': '3jw5UCfJ'
  }
  attributes_values_db_updated = {
    'ordinal': 4,
    'title': '4Ke2ZalC',
    'icon': '3ZtNGShd'
  }
  attributes_values_view_initial = {
    'ordinal': 5,
    'title': 'C1wePTPw',
    'icon': 'wacsjIgS'
  }
  attributes_values_view_updated = {
    'ordinal': 6,
    'title': 'Ye5nXUid',
    'icon': 'ABys0FRo'
  }
  attributes_values_view_invalid = {
    'ordinal': 6,
    'title': INVALID_STRING,
    'icon': INVALID_STRING
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

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, True, 'codelists_status_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, True, 'codelists_status_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neuen', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_status_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_status_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_status_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0
    )


class StatusViewsTest(DefaultViewTestCase):
  """
  views test class for codelist status (Bearbeitungsstatus)
  """

  def setUp(self):
    self.init()

  def test_index_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_status', None, 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_index_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_status', None, 200,
      'text/html; charset=utf-8', 'auflisten'
    )

  def test_index_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_status', None, 200,
      'text/html; charset=utf-8', 'anlegen'
    )

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_status_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'in Bearbeitung'
    )

  def test_tabledata_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_status_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'bearbeiten'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_status_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_status_table', None,
      200, 'text/html; charset=utf-8', 'Titel'
    )

  def test_table_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_status_table', None,
      200, 'text/html; charset=utf-8', 'Aktionen'
    )

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_status_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_status_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_status_create', None,
      200, 'text/html; charset=utf-8', 'neuen'
    )

  def test_update_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_status_update', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_update_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_status_update', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_update_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_status_update', [1],
      200, 'text/html; charset=utf-8', 'nderungen'
    )

  def test_delete_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_status_delete', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_delete_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_status_delete', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_delete_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_status_delete', [1],
      200, 'text/html; charset=utf-8', 'schen'
    )


class SectorModelTest(DefaultCodelistTestCase):
  """
  model test class for codelist sector (Branche)
  """

  model = Sector
  count = 1
  attributes_values_db_initial = {
    'title': 'hFxVbEb2'
  }
  attributes_values_db_updated = {
    'title': 'HFGXNmxC'
  }
  attributes_values_view_initial = {
    'title': 'kr3wiVK5'
  }
  attributes_values_view_updated = {
    'title': 'YvNVTYmQ'
  }
  attributes_values_view_invalid = {
    'title': INVALID_STRING
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

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, True, 'codelists_sector_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, True, 'codelists_sector_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neuen', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_sector_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_sector_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_sector_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0
    )


class SectorViewsTest(DefaultViewTestCase):
  """
  views test class for codelist sector (Branche)
  """

  def setUp(self):
    self.init()

  def test_index_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_sector', None, 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_index_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_sector', None, 200,
      'text/html; charset=utf-8', 'auflisten'
    )

  def test_index_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_sector', None, 200,
      'text/html; charset=utf-8', 'anlegen'
    )

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_sector_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'Baubetrieb'
    )

  def test_tabledata_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_sector_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'bearbeiten'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_sector_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_sector_table', None,
      200, 'text/html; charset=utf-8', 'Titel'
    )

  def test_table_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_sector_table', None,
      200, 'text/html; charset=utf-8', 'Aktionen'
    )

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_sector_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_sector_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_sector_create', None,
      200, 'text/html; charset=utf-8', 'neuen'
    )

  def test_update_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_sector_update', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_update_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_sector_update', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_update_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_sector_update', [1],
      200, 'text/html; charset=utf-8', 'nderungen'
    )

  def test_delete_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_sector_delete', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_delete_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_sector_delete', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_delete_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_sector_delete', [1],
      200, 'text/html; charset=utf-8', 'schen'
    )


class TypeOfEventModelTest(DefaultCodelistTestCase):
  """
  model test class for codelist type of event (Ereignisart)
  """

  model = TypeOfEvent
  count = 6
  attributes_values_db_initial = {
    'title': 'UIO0F3n8',
    'icon': 'qgzUK9gf'
  }
  attributes_values_db_updated = {
    'title': 'o3XwyDzw',
    'icon': 'svNUGQAd'
  }
  attributes_values_view_initial = {
    'title': 'l68MH5Nz',
    'icon': 'DvXUWHev'
  }
  attributes_values_view_updated = {
    'title': 'yPDDJ55N',
    'icon': 'zomEtOOV'
  }
  attributes_values_view_invalid = {
    'title': INVALID_STRING,
    'icon': INVALID_STRING
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

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, True, 'codelists_typeofevent_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, True, 'codelists_typeofevent_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neuen', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_typeofevent_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_typeofevent_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_typeofevent_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0
    )


class TypeOfEventViewsTest(DefaultViewTestCase):
  """
  views test class for codelist type of event (Ereignisart)
  """

  def setUp(self):
    self.init()

  def test_index_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofevent', None, 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_index_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofevent', None, 200,
      'text/html; charset=utf-8', 'auflisten'
    )

  def test_index_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofevent', None, 200,
      'text/html; charset=utf-8', 'anlegen'
    )

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofevent_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'Telefonat'
    )

  def test_tabledata_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofevent_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'bearbeiten'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofevent_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofevent_table', None,
      200, 'text/html; charset=utf-8', 'Titel'
    )

  def test_table_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofevent_table', None,
      200, 'text/html; charset=utf-8', 'Aktionen'
    )

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofevent_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofevent_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofevent_create', None,
      200, 'text/html; charset=utf-8', 'neuen'
    )

  def test_update_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofevent_update', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_update_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofevent_update', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_update_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofevent_update', [1],
      200, 'text/html; charset=utf-8', 'nderungen'
    )

  def test_delete_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofevent_delete', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_delete_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofevent_delete', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_delete_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofevent_delete', [1],
      200, 'text/html; charset=utf-8', 'schen'
    )


class TypeOfImmissionModelTest(DefaultCodelistTestCase):
  """
  model test class for codelist type of immission (Immissionsart)
  """

  model = TypeOfImmission
  count = 6
  attributes_values_db_initial = {
    'title': 'eaDUeltd',
    'icon': 'wLIe5cDw'
  }
  attributes_values_db_updated = {
    'title': 'mNyvaDBE',
    'icon': 'WMEmWR5M'
  }
  attributes_values_view_initial = {
    'title': 'eXbkQgzK',
    'icon': 'ZKPgKvlQ'
  }
  attributes_values_view_updated = {
    'title': 'iRSX9DF8',
    'icon': '8FxlFjWU'
  }
  attributes_values_view_invalid = {
    'title': INVALID_STRING,
    'icon': INVALID_STRING
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

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, True, 'codelists_typeofimmission_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, True, 'codelists_typeofimmission_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neuen', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_typeofimmission_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_typeofimmission_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, True, 'codelists_typeofimmission_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0
    )


class TypeOfImmissionViewsTest(DefaultViewTestCase):
  """
  views test class for codelist type of immission (Immissionsart)
  """

  def setUp(self):
    self.init()

  def test_index_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofimmission', None, 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_index_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofimmission', None, 200,
      'text/html; charset=utf-8', 'auflisten'
    )

  def test_index_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofimmission', None, 200,
      'text/html; charset=utf-8', 'anlegen'
    )

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofimmission_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'Geruch'
    )

  def test_tabledata_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofimmission_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'bearbeiten'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofimmission_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofimmission_table', None,
      200, 'text/html; charset=utf-8', 'Titel'
    )

  def test_table_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofimmission_table', None,
      200, 'text/html; charset=utf-8', 'Aktionen'
    )

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofimmission_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofimmission_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofimmission_create', None,
      200, 'text/html; charset=utf-8', 'neuen'
    )

  def test_update_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofimmission_update', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_update_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofimmission_update', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_update_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofimmission_update', [1],
      200, 'text/html; charset=utf-8', 'nderungen'
    )

  def test_delete_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists_typeofimmission_delete', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_delete_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists_typeofimmission_delete', [1],
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_delete_view_admin_rights(self):
    self.generic_view_test(
      True, True, 'codelists_typeofimmission_delete', [1],
      200, 'text/html; charset=utf-8', 'schen'
    )


#
# general views
#

class CodelistsIndexViewTest(DefaultViewTestCase):
  """
  test class for codelists entry page
  """

  def setUp(self):
    self.init()

  def test_view_no_rights(self):
    self.generic_view_test(
      False, False, 'codelists', None, 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'codelists', None, 200,
      'text/html; charset=utf-8', 'Codelisten'
    )
