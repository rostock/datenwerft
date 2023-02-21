from .base import DefaultViewTestCase


class IndexViewTest(DefaultViewTestCase):
  """
  test class for index view
  """

  def setUp(self):
    self.init()

  def test_view_no_rights(self):
    self.generic_view_test(False, False, 'index', 200, 'text/html; charset=utf-8', 'keine Rechte')

  def test_view_standard_rights(self):
    self.generic_view_test(True, False, 'index', 200, 'text/html; charset=utf-8', 'BEMAS')
