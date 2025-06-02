from ..abstract import DefaultViewTestCase


class IndexViewTest(DefaultViewTestCase):
  """
  test class for main page
  """

  def setUp(self):
    self.init()

  def test_view_with_permissions(self):
    self.generic_view_test(
      assign_permissions=True,
      view_name='index',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='FMF',
    )

  def test_view_without_permissions(self):
    self.generic_view_test(
      assign_permissions=False,
      view_name='index',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )
