from fmm.models import (
  Fmf,
  PaketUmwelt,
)

from ..abstract import FormViewTestCase, ViewTestCase
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


class PaketUmweltUpdateViewTest(FormViewTestCase):
  """
  test class for form page for updating a Paket Umwelt instance
  """

  model = PaketUmwelt
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_fmf_a = Fmf.objects.create(
      bezeichnung=VALID_STRING_A,
      geometrie=VALID_POLYGON_DB_A,
    )
    cls.attributes_values_db_initial = {
      'fmf': test_fmf_a,
      'trinkwassernotbrunnen': False,
    }
    test_fmf_b = Fmf.objects.create(
      bezeichnung=VALID_STRING_B,
      geometrie=VALID_POLYGON_DB_B,
    )
    cls.test_fmf_b = test_fmf_b
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.form_data_valid = {
      'fmf': str(test_fmf_b.pk),
      'trinkwassernotbrunnen': True,
    }
    cls.form_data_invalid = {
      'trinkwassernotbrunnen': False,
    }

  def setUp(self):
    self.init()

  def test_get_with_permissions(self):
    self.generic_form_get_test(
      assign_permissions=True,
      view_name='paketumwelt_update',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='aktualisieren ',
    )

  def test_get_without_permissions(self):
    self.generic_form_get_test(
      assign_permissions=False,
      view_name='paketumwelt_update',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )

  def test_post_success(self):
    self.generic_form_post_test(
      assign_permissions=True,
      view_name='paketumwelt_update',
      form_data=self.form_data_valid,
      status_code=302,
    )

  def test_post_error(self):
    self.generic_form_post_test(
      assign_permissions=True,
      view_name='paketumwelt_update',
      form_data=self.form_data_invalid,
      status_code=200,
    )


class PaketUmweltDeleteViewTest(FormViewTestCase):
  """
  test class for form page for deleting a Paket Umwelt instance
  """

  model = PaketUmwelt
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_fmf = Fmf.objects.create(
      bezeichnung=VALID_STRING_A,
      geometrie=VALID_POLYGON_DB_A,
    )
    cls.attributes_values_db_initial = {
      'fmf': test_fmf,
      'trinkwassernotbrunnen': False,
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def setUp(self):
    self.init()

  def test_get_with_permissions(self):
    self.generic_form_get_test(
      assign_permissions=True,
      view_name='paketumwelt_delete',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='schen ',
    )

  def test_get_without_permissions(self):
    self.generic_form_get_test(
      assign_permissions=False,
      view_name='paketumwelt_delete',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )

  def test_post_success(self):
    self.generic_form_post_test(
      assign_permissions=True,
      view_name='paketumwelt_delete',
      form_data={},
      status_code=302,
    )
