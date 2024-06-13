from .base import DefaultViewTestCase, DefaultFormViewTestCase


#
# general
#

class IndexViewTest(DefaultViewTestCase):
  """
  test class for main page
  """

  def setUp(self):
    self.init()

  def test_no_permissions(self):
    self.generic_view_test(
      antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='index', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_requester_permissions(self):
    self.generic_view_test(
      antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='index', status_code=200,
      content_type='text/html; charset=utf-8', string='Ant'
    )

  def test_authority_permissions(self):
    self.generic_view_test(
      antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='index', status_code=200,
      content_type='text/html; charset=utf-8', string='Beh'
    )

  def test_admin_permissions(self):
    self.generic_view_test(
      antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='index', status_code=200,
      content_type='text/html; charset=utf-8', string='Adm'
    )


#
# general objects
#

class AuthorityUpdateView(DefaultFormViewTestCase):
  """
  test class for form page for updating an instance of general object:
  authority (Behörde)
  """

  def setUp(self):
    self.init()

  # Tests: 4x perms-kram wie oben

  def test_update_success(self):
    self.generic_form_view_test(
      antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='index', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  # Test: test_update_error
