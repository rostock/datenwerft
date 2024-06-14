from django.utils.crypto import get_random_string

from antragsmanagement.models import Authority, Email, Requester
from .base import DefaultViewTestCase, DefaultFormViewTestCase
from .constants_vars import VALID_EMAIL, VALID_STRING, VALID_TEXT


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

  model = Authority
  attributes_values_db_create = {
    'group': VALID_STRING,
    'name': get_random_string(length=12),
    'email': VALID_EMAIL
  }
  attributes_values_view_update_valid = {
    'email': 'golda.meir@gov.il'
  }
  attributes_values_view_update_invalid = {
    'email': get_random_string(length=12)
  }

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='authority_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='authority_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='authority_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='authority_update', status_code=200,
      content_type='text/html; charset=utf-8', string='ndern '
    )

  def test_post_update_success(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='authority_update',
      object_filter=self.attributes_values_view_update_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8'
    )

  def test_post_update_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='authority_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8'
    )


class EmailUpdateView(DefaultFormViewTestCase):
  """
  test class for form page for updating an instance of general object:
  email (E-Mail)
  """

  model = Email
  attributes_values_db_create = {
    'key': get_random_string(length=12),
    'body': VALID_TEXT
  }
  attributes_values_view_update_valid = {
    'body': get_random_string(length=12)
  }
  attributes_values_view_update_invalid = {
    'body': get_random_string(length=12)
  }

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='email_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='email_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='email_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='email_update', status_code=200,
      content_type='text/html; charset=utf-8', string='ndern '
    )

  def test_post_update_success(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='email_update',
      object_filter=self.attributes_values_view_update_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8'
    )


class RequesterUpdateView(DefaultFormViewTestCase):
  """
  test class for form page for updating an instance of general object:
  requester (Antragsteller:in)
  """

  model = Requester
  attributes_values_db_create = {
    'key': get_random_string(length=12),
    'body': VALID_TEXT
  }
  attributes_values_view_update_valid = {
    'body': get_random_string(length=12)
  }
  attributes_values_view_update_invalid = {
    'body': get_random_string(length=12)
  }

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='email_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='email_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='email_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='email_update', status_code=200,
      content_type='text/html; charset=utf-8', string='ndern '
    )

  def test_post_update_success(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='email_update',
      object_filter=self.attributes_values_view_update_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8'
    )
