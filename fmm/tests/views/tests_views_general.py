from fmm.models import (
  Fmf,
)

from ..abstract import FormViewTestCase, ViewTestCase
from ..constants_vars import (
  VALID_POLYGON_DB_A,
  VALID_STRING_A,
)


class IndexViewTest(ViewTestCase):
  """
  test class for main page
  """

  def setUp(self):
    self.init()

  def test_get_with_permissions(self):
    self.generic_get_test(
      assign_permissions=True,
      view_name='index',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='FMF',
    )

  def test_get_without_permissions(self):
    self.generic_get_test(
      assign_permissions=False,
      view_name='index',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )


class TableDataViewTest(ViewTestCase):
  """
  test class for composing table data
  """

  def setUp(self):
    self.init()

  def test_get_with_permissions(self):
    self.generic_get_test(
      assign_permissions=True,
      view_name='tabledata',
      status_code=200,
      content_type='application/json',
      string='ok',
    )

  def test_get_without_permissions(self):
    self.generic_get_test(
      assign_permissions=False,
      view_name='tabledata',
      status_code=200,
      content_type='application/json',
      string='has_necessary_permissions',
    )


class TableViewTest(ViewTestCase):
  """
  test class for table page
  """

  def setUp(self):
    self.init()

  def test_get_with_permissions(self):
    self.generic_get_test(
      assign_permissions=True,
      view_name='table',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='FMF',
    )

  def test_get_without_permissions(self):
    self.generic_get_test(
      assign_permissions=False,
      view_name='table',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )


class OverviewViewTest(FormViewTestCase):
  """
  test class for overview page
  """

  model = Fmf
  attributes_values_db_initial = {
    'bezeichnung': VALID_STRING_A,
    'geometrie': VALID_POLYGON_DB_A,
  }

  def setUp(self):
    self.init()

  def test_get_with_permissions(self):
    self.generic_form_get_test(
      assign_permissions=True,
      view_name='overview',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='text/html; charset=utf-8',
      string=VALID_STRING_A,
    )

  def test_get_without_permissions(self):
    self.generic_form_get_test(
      assign_permissions=False,
      view_name='overview',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )
