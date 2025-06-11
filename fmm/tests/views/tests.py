from fmm.models import (
  Fmf,
  PaketUmwelt,
)

from ..abstract import ViewTestCase, FormViewTestCase
from ..constants_vars import (
  VALID_POLYGON_DB_A,
  VALID_POLYGON_DB_B,
  VALID_POLYGON_VIEW_A,
  VALID_POLYGON_VIEW_B,
  VALID_STRING_A,
  VALID_STRING_B,
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


class FmfCreateViewTest(ViewTestCase):
  """
  test class for form page for creating a FMF instance
  """

  form_data_valid = {
    'bezeichnung': VALID_STRING_A,
    'geometrie': VALID_POLYGON_VIEW_A,
  }
  form_data_invalid = {
    'geometrie': VALID_POLYGON_VIEW_B,
  }

  def setUp(self):
    self.init()

  def test_get_with_permissions(self):
    self.generic_get_test(
      assign_permissions=True,
      view_name='fmf_create',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='neu ',
    )

  def test_get_without_permissions(self):
    self.generic_get_test(
      assign_permissions=False,
      view_name='fmf_create',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )

  def test_post_success(self):
    self.generic_post_test(
      assign_permissions=True,
      view_name='fmf_create',
      form_data=self.form_data_valid,
      status_code=302,
    )

  def test_post_error(self):
    self.generic_post_test(
      assign_permissions=True,
      view_name='fmf_create',
      form_data=self.form_data_invalid,
      status_code=200,
    )


class FmfUpdateViewTest(FormViewTestCase):
  """
  test class for form page for updating a FMF instance
  """

  model = Fmf
  attributes_values_db_initial = {
    'bezeichnung': VALID_STRING_A,
    'geometrie': VALID_POLYGON_DB_A,
  }
  form_data_valid = {
    'bezeichnung': VALID_STRING_B,
    'geometrie': VALID_POLYGON_VIEW_B,
  }
  form_data_invalid = {
    'geometrie': VALID_POLYGON_VIEW_A,
  }

  def setUp(self):
    self.init()

  def test_get_with_permissions(self):
    self.generic_form_get_test(
      assign_permissions=True,
      view_name='fmf_update',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='aktualisieren ',
    )

  def test_get_without_permissions(self):
    self.generic_form_get_test(
      assign_permissions=False,
      view_name='fmf_update',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )

  def test_post_success(self):
    self.generic_form_post_test(
      assign_permissions=True,
      view_name='fmf_update',
      form_data=self.form_data_valid,
      status_code=302,
    )

  def test_post_error(self):
    self.generic_form_post_test(
      assign_permissions=True,
      view_name='fmf_update',
      form_data=self.form_data_invalid,
      status_code=200,
    )


class FmfDeleteViewTest(FormViewTestCase):
  """
  test class for form page for deleting a FMF instance
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
      view_name='fmf_delete',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='schen ',
    )

  def test_get_without_permissions(self):
    self.generic_form_get_test(
      assign_permissions=False,
      view_name='fmf_delete',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )

  def test_post_success(self):
    self.generic_form_post_test(
      assign_permissions=True,
      view_name='fmf_delete',
      form_data={},
      status_code=302,
    )
