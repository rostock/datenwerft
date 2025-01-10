from datetime import timedelta
from django.utils.crypto import get_random_string

from .base import DefaultModelTestCase
from .constants_vars import VALID_DATE, VALID_EMAIL, VALID_FIRST_NAME, \
  VALID_LAST_NAME, VALID_POINT_DB, VALID_POLYGON_DB, VALID_STRING, VALID_TELEPHONE, VALID_TEXT
from .functions import create_cleanupevent_request
from antragsmanagement.models import CodelistRequestStatus, CleanupEventCodelistWasteQuantity, \
  CleanupEventCodelistWasteType, CleanupEventCodelistEquipment, Authority, Email, Requester, \
  CleanupEventRequest, CleanupEventEvent, CleanupEventVenue, CleanupEventDetails, \
  CleanupEventContainer, CleanupEventDump, CleanupEventRequestComment


#
# general objects
#

class AuthorityTest(DefaultModelTestCase):
  """
  test class for general object:
  authority (Behörde)
  """

  model = Authority
  attributes_values_db_create = {
    'group': VALID_STRING,
    'name': get_random_string(length=12),
    'email': VALID_EMAIL
  }
  attributes_values_db_update = {
    'name': get_random_string(length=12)
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class EmailTest(DefaultModelTestCase):
  """
  test class for general object:
  email (E-Mail)
  """

  model = Email
  attributes_values_db_create = {
    'key': get_random_string(length=12),
    'body': VALID_TEXT
  }
  attributes_values_db_update = {
    'key': get_random_string(length=12)
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class RequesterTest(DefaultModelTestCase):
  """
  test class for general object:
  requester (Antragsteller:in)
  """

  model = Requester
  attributes_values_db_create = {
    'first_name': VALID_FIRST_NAME,
    'last_name': VALID_LAST_NAME,
    'email': VALID_EMAIL,
    'telephone': VALID_TELEPHONE
  }
  attributes_values_db_update = {
    'organization': VALID_STRING
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventRequestTest(DefaultModelTestCase):
  """
  test class for object for request type clean-up events (Müllsammelaktionen):
  request (Antrag)
  """

  model = CleanupEventRequest
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    status1 = CodelistRequestStatus.get_status_new()
    status2 = CodelistRequestStatus.get_status_in_process()
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
    cls.attributes_values_db_create = {
      'status': status1,
      'requester': requester
    }
    cls.attributes_values_db_update = {
      'status': status2
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)
    cls.test_object.responsibilities.add(responsibility, through_defaults={'main': False})

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CleanupEventEventTest(DefaultModelTestCase):
  """
  test class for object for request type clean-up events (Müllsammelaktionen):
  event (Aktion)
  """

  model = CleanupEventEvent
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cleanupevent_request = create_cleanupevent_request(False)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request,
      'from_date': VALID_DATE,
      'area': VALID_POLYGON_DB
    }
    cls.attributes_values_db_update = {
      'to_date': VALID_DATE
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CleanupEventVenueTest(DefaultModelTestCase):
  """
  test class for object for request type clean-up events (Müllsammelaktionen):
  venue (Treffpunkt)
  """

  model = CleanupEventVenue
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cleanupevent_request1, cleanupevent_request2 = create_cleanupevent_request(True)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request1,
      'place': VALID_POINT_DB
    }
    cls.attributes_values_db_update = {
      'cleanupevent_request': cleanupevent_request2
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CleanupEventDetailsTest(DefaultModelTestCase):
  """
  test class for object for request type clean-up events (Müllsammelaktionen):
  details (Detailangaben)
  """

  model = CleanupEventDetails
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    waste_quantity = CleanupEventCodelistWasteQuantity.objects.first()
    waste_type = CleanupEventCodelistWasteType.objects.first()
    equipment = CleanupEventCodelistEquipment.objects.first()
    cleanupevent_request = create_cleanupevent_request(False)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request,
      'waste_quantity': waste_quantity
    }
    cls.attributes_values_db_update = {
      'waste_types_annotation': VALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)
    cls.test_object.waste_types.add(waste_type)
    cls.test_object.equipments.add(equipment)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CleanupEventContainerTest(DefaultModelTestCase):
  """
  test class for object for request type clean-up events (Müllsammelaktionen):
  container (Container)
  """

  model = CleanupEventContainer
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cleanupevent_request1, cleanupevent_request2 = create_cleanupevent_request(True)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request1,
      'delivery_date': VALID_DATE,
      'pickup_date': VALID_DATE + timedelta(days=1),
      'place': VALID_POINT_DB
    }
    cls.attributes_values_db_update = {
      'cleanupevent_request': cleanupevent_request2
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CleanupEventDumpTest(DefaultModelTestCase):
  """
  test class for object for request type clean-up events (Müllsammelaktionen):
  dump (Müllablageplatz)
  """

  model = CleanupEventDump
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cleanupevent_request1, cleanupevent_request2 = create_cleanupevent_request(True)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request1,
      'place': VALID_POINT_DB
    }
    cls.attributes_values_db_update = {
      'cleanupevent_request': cleanupevent_request2
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CleanupEventRequestCommentTest(DefaultModelTestCase):
  """
  test class for object for request type clean-up events (Müllsammelaktionen):
  request comment (Kommentar zu Antrag)
  """

  model = CleanupEventRequestComment
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cleanupevent_request = create_cleanupevent_request(False)
    cls.attributes_values_db_create = {
      'cleanupevent_request': cleanupevent_request,
      'content': VALID_TEXT
    }
    cls.attributes_values_db_update = {
      'send_to_requester': True
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_create)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()
