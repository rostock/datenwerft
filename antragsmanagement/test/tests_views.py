from django.utils.crypto import get_random_string

from antragsmanagement.models import CodelistRequestStatus, CleanupEventCodelistWasteQuantity, \
  CleanupEventCodelistWasteType, CleanupEventCodelistEquipment, Authority, Email, Requester, \
  CleanupEventRequest, CleanupEventEvent, CleanupEventVenue, CleanupEventDetails, \
  CleanupEventContainer
from .base import DefaultViewTestCase, DefaultFormViewTestCase
from .constants_vars import VALID_DATE, VALID_EMAIL, VALID_FIRST_NAME, VALID_LAST_NAME, \
  VALID_POINT_DB, VALID_POINT_VIEW, VALID_POLYGON_DB, VALID_POLYGON_VIEW, VALID_STRING, VALID_TEXT


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
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables=None
    )

  def test_post_update_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='authority_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables=None
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
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables=None
    )

  def test_post_update_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='email_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables=None
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
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables=None
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_create',
      object_filter=self.attributes_values_view_create_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables=None
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
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables=None
    )

  def test_post_update_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='requester_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables=None
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
      content_type='text/html; charset=utf-8', string='Kontaktdaten erstellen'
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
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables=None
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_create',
      object_filter=self.attributes_values_view_create_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables=None
    )


class CleanupEventRequestUpdateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for updating an instance of object for request type clean-up events
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
    cls.attributes_values_view_update_valid = {
      'status': str(status2.pk),
      'requester': str(requester.pk)
    }
    cls.attributes_values_view_update_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_update', status_code=200,
      content_type='text/html; charset=utf-8', string='Kontaktdaten erstellen'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='cleanupeventrequest_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_post_create_success(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_update',
      object_filter=self.attributes_values_view_update_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables=None
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventrequest_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables=None
    )


class CleanupEventEventCreateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  event (Aktion)
  """

  model = CleanupEventEvent
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
    responsibility = Authority.objects.create(
      group=VALID_STRING,
      name=VALID_STRING,
      email=VALID_EMAIL
    )
    cleanupevent_request1 = CleanupEventRequest.objects.create(
      status=status1,
      requester=requester
    )
    cleanupevent_request1.responsibilities.add(responsibility)
    cleanupevent_request2 = CleanupEventRequest.objects.create(
      status=status2,
      requester=requester
    )
    cleanupevent_request2.responsibilities.add(responsibility)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request1,
      'from_date': VALID_DATE,
      'area': VALID_POLYGON_DB
    }
    cls.attributes_values_view_create_valid = {
      'cleanupevent_request': str(cleanupevent_request2.pk),
      'from_date': VALID_DATE,
      'area': VALID_POLYGON_VIEW
    }
    cls.attributes_values_view_create_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventevent_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventevent_create', status_code=200,
      content_type='text/html; charset=utf-8', string='Antrag erstellen'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='cleanupeventevent_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='cleanupeventevent_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )
"""
  def test_post_create_success(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventevent_create',
      object_filter=self.attributes_values_view_create_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables={'request_id': 2}
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventevent_create',
      object_filter=self.attributes_values_view_create_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables={'request_id': 2}
    )
"""


class CleanupEventEventUpdateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  event (Aktion)
  """

  model = CleanupEventEvent
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
    responsibility = Authority.objects.create(
      group=VALID_STRING,
      name=VALID_STRING,
      email=VALID_EMAIL
    )
    cleanupevent_request1 = CleanupEventRequest.objects.create(
      status=status1,
      requester=requester
    )
    cleanupevent_request1.responsibilities.add(responsibility)
    cleanupevent_request2 = CleanupEventRequest.objects.create(
      status=status2,
      requester=requester
    )
    cleanupevent_request2.responsibilities.add(responsibility)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request1,
      'from_date': VALID_DATE,
      'area': VALID_POLYGON_DB
    }
    cls.attributes_values_view_update_valid = {
      'cleanupevent_request': str(cleanupevent_request2.pk),
      'from_date': VALID_DATE,
      'area': VALID_POLYGON_VIEW
    }
    cls.attributes_values_view_update_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventevent_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventevent_update', status_code=200,
      content_type='text/html; charset=utf-8', string='Antrag erstellen'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='cleanupeventevent_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='cleanupeventevent_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_post_create_success(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventevent_update',
      object_filter=self.attributes_values_view_update_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables={'request_id': 2}
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventevent_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables={'request_id': 2}
    )


class CleanupEventVenueCreateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  venue (Treffpunkt)
  """

  model = CleanupEventVenue
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
    responsibility = Authority.objects.create(
      group=VALID_STRING,
      name=VALID_STRING,
      email=VALID_EMAIL
    )
    cleanupevent_request1 = CleanupEventRequest.objects.create(
      status=status1,
      requester=requester
    )
    cleanupevent_request1.responsibilities.add(responsibility)
    cleanupevent_request2 = CleanupEventRequest.objects.create(
      status=status2,
      requester=requester
    )
    cleanupevent_request2.responsibilities.add(responsibility)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request1,
      'place': VALID_POINT_DB
    }
    cls.attributes_values_view_create_valid = {
      'cleanupevent_request': str(cleanupevent_request2.pk),
      'place': VALID_POINT_VIEW
    }
    cls.attributes_values_view_create_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_create', status_code=200,
      content_type='text/html; charset=utf-8', string='Antrag erstellen'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='cleanupeventvenue_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )
"""
  def test_post_create_success(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_create',
      object_filter=self.attributes_values_view_create_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables={'request_id': 2}
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_create',
      object_filter=self.attributes_values_view_create_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables={'request_id': 2}
    )
"""


class CleanupEventVenueUpdateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  venue (Treffpunkt)
  """

  model = CleanupEventVenue
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
    responsibility = Authority.objects.create(
      group=VALID_STRING,
      name=VALID_STRING,
      email=VALID_EMAIL
    )
    cleanupevent_request1 = CleanupEventRequest.objects.create(
      status=status1,
      requester=requester
    )
    cleanupevent_request1.responsibilities.add(responsibility)
    cleanupevent_request2 = CleanupEventRequest.objects.create(
      status=status2,
      requester=requester
    )
    cleanupevent_request2.responsibilities.add(responsibility)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request1,
      'place': VALID_POINT_DB
    }
    cls.attributes_values_view_update_valid = {
      'cleanupevent_request': str(cleanupevent_request2.pk),
      'place': VALID_POINT_VIEW
    }
    cls.attributes_values_view_update_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_update', status_code=200,
      content_type='text/html; charset=utf-8', string='Antrag erstellen'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='cleanupeventvenue_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_post_create_success(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_update',
      object_filter=self.attributes_values_view_update_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables={'request_id': 2}
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventvenue_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables={'request_id': 2}
    )


class CleanupEventDetailsCreateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for creating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  details (Detailangaben)
  """

  model = CleanupEventDetails
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
    responsibility = Authority.objects.create(
      group=VALID_STRING,
      name=VALID_STRING,
      email=VALID_EMAIL
    )
    cleanupevent_request1 = CleanupEventRequest.objects.create(
      status=status1,
      requester=requester
    )
    cleanupevent_request1.responsibilities.add(responsibility)
    cleanupevent_request2 = CleanupEventRequest.objects.create(
      status=status2,
      requester=requester
    )
    cleanupevent_request2.responsibilities.add(responsibility)
    waste_quantity = CleanupEventCodelistWasteQuantity.objects.first()
    waste_type = CleanupEventCodelistWasteType.objects.first()
    equipment = CleanupEventCodelistEquipment.objects.first()
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request1,
      'waste_quantity': waste_quantity
    }
    cls.attributes_values_view_create_valid = {
      'cleanupevent_request': str(cleanupevent_request2.pk),
      'waste_quantity': str(waste_quantity.pk),
      'waste_types_annotation': VALID_STRING
    }
    cls.attributes_values_view_create_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_create', status_code=200,
      content_type='text/html; charset=utf-8', string='Antrag erstellen'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=False, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='cleanupeventdetails_create', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )
"""
  def test_post_create_success(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_create',
      object_filter=self.attributes_values_view_create_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables={'request_id': 2}
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=False, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_create',
      object_filter=self.attributes_values_view_create_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables={'request_id': 2}
    )
"""


class CleanupEventDetailsUpdateViewTest(DefaultFormViewTestCase):
  """
  test class for form page for updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  details (Detailangaben)
  """

  model = CleanupEventDetails
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
    responsibility = Authority.objects.create(
      group=VALID_STRING,
      name=VALID_STRING,
      email=VALID_EMAIL
    )
    cleanupevent_request1 = CleanupEventRequest.objects.create(
      status=status1,
      requester=requester
    )
    cleanupevent_request1.responsibilities.add(responsibility)
    cleanupevent_request2 = CleanupEventRequest.objects.create(
      status=status2,
      requester=requester
    )
    cleanupevent_request2.responsibilities.add(responsibility)
    waste_quantity = CleanupEventCodelistWasteQuantity.objects.first()
    waste_type = CleanupEventCodelistWasteType.objects.first()
    equipment = CleanupEventCodelistEquipment.objects.first()
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request1,
      'waste_quantity': waste_quantity
    }
    cls.attributes_values_view_update_valid = {
      'cleanupevent_request': str(cleanupevent_request2.pk),
      'waste_quantity': str(waste_quantity.pk),
      'waste_types_annotation': VALID_STRING
    }
    cls.attributes_values_view_update_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)
    cls.test_object.waste_types.add(waste_type)
    cls.test_object.equipments.add(equipment)

  def setUp(self):
    self.init()

  def test_get_no_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_requester_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_update', status_code=200,
      content_type='text/html; charset=utf-8', string='Antrag erstellen'
    )

  def test_get_authority_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=True,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_get_admin_permissions(self):
    self.generic_form_view_get_test(
      update_mode=True, antragsmanagement_requester=False, antragsmanagement_authority=False,
      antragsmanagement_admin=True, view_name='cleanupeventdetails_update', status_code=200,
      content_type='text/html; charset=utf-8', string='keine Rechte'
    )

  def test_post_create_success(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_update',
      object_filter=self.attributes_values_view_update_valid, count=1,
      status_code=302, content_type='text/html; charset=utf-8', string=None,
      session_variables={'request_id': 2}
    )

  def test_post_create_error(self):
    self.generic_form_view_post_test(
      update_mode=True, antragsmanagement_requester=True, antragsmanagement_authority=False,
      antragsmanagement_admin=False, view_name='cleanupeventdetails_update',
      object_filter=self.attributes_values_view_update_invalid, count=1,
      status_code=200, content_type='text/html; charset=utf-8', string='alert',
      session_variables={'request_id': 2}
    )
