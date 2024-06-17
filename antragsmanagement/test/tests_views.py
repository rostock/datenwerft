from django.utils.crypto import get_random_string

from antragsmanagement.models import CodelistRequestStatus, Authority, Email, Requester, \
  CleanupEventRequest
from .base import DefaultViewTestCase, DefaultFormViewTestCase
from .constants_vars import VALID_EMAIL, VALID_FIRST_NAME, VALID_LAST_NAME, VALID_STRING, \
  VALID_TEXT


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
      content_type='text/html; charset=utf-8', string='Kontaktdaten'
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
      content_type='text/html; charset=utf-8', string='E-Mail-Adresse'
    )


#
# general objects
#

class AuthorityUpdateViewTest(DefaultFormViewTestCase):
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
      status_code=302, content_type='text/html; charset=utf-8', string=None
    )

  def test_post_update_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='authority_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert'
    )


class EmailUpdateViewTest(DefaultFormViewTestCase):
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
      status_code=302, content_type='text/html; charset=utf-8', string=None
    )

  def test_post_update_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='email_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert'
    )


class RequesterCreateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for creating an instance of general object:
  requester (Antragsteller:in)
  """

  model = Requester
  attributes_values_db_create = {
    'first_name': VALID_FIRST_NAME,
    'last_name': VALID_LAST_NAME,
    'email': VALID_EMAIL
  }
  attributes_values_view_create_valid = {
    'organization': VALID_STRING,
    'first_name': VALID_FIRST_NAME,
    'last_name': VALID_LAST_NAME,
    'email': VALID_EMAIL
  }
  attributes_values_view_create_invalid = {
  }

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_create', status_code=200,
      content_type='text/html; charset=utf-8', string='neu '
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='requester_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='requester_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_post_create_success(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_create',
      object_filter=self.attributes_values_view_create_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_create',
      object_filter=self.attributes_values_view_create_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert'
    )


class RequesterUpdateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for updating an instance of general object:
  requester (Antragsteller:in)
  """

  model = Requester
  attributes_values_db_create = {
    'first_name': VALID_FIRST_NAME,
    'last_name': VALID_LAST_NAME,
    'email': VALID_EMAIL
  }
  attributes_values_view_update_valid = {
    'organization': VALID_STRING,
    'first_name': VALID_FIRST_NAME,
    'last_name': VALID_LAST_NAME,
    'email': VALID_EMAIL
  }
  attributes_values_view_update_invalid = {
  }

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_update', status_code=200,
      content_type='text/html; charset=utf-8', string='ndern '
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='requester_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='requester_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_post_update_success(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_update',
      object_filter=self.attributes_values_view_update_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None
    )

  def test_post_update_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert'
    )


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventRequestCreateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  request (Antrag)
  """

  model = CleanupEventRequest
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    status1 = CodelistRequestStatus.get_status_processed()
    status2 = CodelistRequestStatus.get_status_new()
    requester = Requester.objects.create(
      first_name=VALID_FIRST_NAME,
      last_name=VALID_LAST_NAME,
      email=VALID_EMAIL
    )
    cls.attributes_values_db_create = {
      'status': status1,
      'requester': requester
    }
    cls.attributes_values_view_create_valid = {
      'status': str(status2.pk),
      'requester': str(requester.pk)
    }
    cls.attributes_values_view_create_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_create', status_code=200,
      content_type='text/html; charset=utf-8', string='Ihre Kontaktdaten erstellen'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='cleanupeventrequest_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_post_create_success(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_create',
      object_filter=self.attributes_values_view_create_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_create',
      object_filter=self.attributes_values_view_create_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert'
    )
