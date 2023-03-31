from .base import DefaultViewTestCase


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
      False, False, 'index', None, 200,
      'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'index', None, 200,
      'text/html; charset=utf-8', 'Codelisten'
    )
