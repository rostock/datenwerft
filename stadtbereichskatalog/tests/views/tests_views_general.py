from ..abstract import ViewTestCase


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
      string='Metadaten',
    )

  def test_get_without_permissions(self):
    self.generic_get_test(
      assign_permissions=False,
      view_name='index',
      status_code=200,
      content_type='text/html; charset=utf-8',
      string='keine Rechte',
    )
