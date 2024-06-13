from .base import DefaultViewTestCase


#
# general
#

class IndexViewTest(DefaultViewTestCase):
  """
  test class for main page
  """

  def setUp(self):
    self.init()

  def test_view_no_permissions(self):
    self.generic_view_test(
      antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='index', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_view_requester_permissions(self):
    self.generic_view_test(
      antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='index', status_code=200,
      content_type='text/html; charset=utf-8', string='Ant'
    )

  def test_view_authority_permissions(self):
    self.generic_view_test(
      antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='index', status_code=200,
      content_type='text/html; charset=utf-8', string='Beh'
    )

  def test_view_admin_permissions(self):
    self.generic_view_test(
      antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='index', status_code=200,
      content_type='text/html; charset=utf-8', string='Adm'
    )
