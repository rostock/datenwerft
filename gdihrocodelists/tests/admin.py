from .abstract import DefaultViewTestCase


class CodelistViewTest(DefaultViewTestCase):
  """
  test class for model:
  codelist (Codeliste)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='codelist_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class CodelistValueViewTest(DefaultViewTestCase):
  """
  test class for model:
  codelist value (Codelistenwert)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='codelistvalue_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )
