from bemas.models import Complaint, Contact, Event, Organization, Originator, Person, Sector, \
  Status, TypeOfEvent, TypeOfImmission
from .base import DefaultManyToManyTestCase, DefaultModelTestCase, DefaultViewTestCase
from .constants_vars import INVALID_STRING, TABLEDATA_VIEW_PARAMS, VALID_DATE, VALID_POINT_DB, \
  VALID_POINT_VIEW


#
# object classes
#


class OrganizationModelTest(DefaultModelTestCase):
  """
  model test class for object class organization (Organisation)
  """

  model = Organization
  attributes_values_db_initial = {
    'name': 'arTc9w6J'
  }
  attributes_values_db_updated = {
    'name': 'g4Wsx9jj'
  }
  attributes_values_view_initial = {
    'name': 'aSEpwomZ'
  }
  attributes_values_view_updated = {
    'name': '5ir0FTs1'
  }
  attributes_values_view_invalid = {
    'name': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, False, 'organization_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 1, 'created'
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, False, 'organization_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neue', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, False, 'organization_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, False, 'organization_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, False, 'organization_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0, 'deleted'
    )


class OrganizationViewsTest(DefaultViewTestCase):
  """
  views test class for object class organization (Organisation)
  """

  def setUp(self):
    self.init()

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'organization_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'ok'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'organization_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'organization_table', None,
      200, 'text/html; charset=utf-8', 'vorhanden'
    )

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'organization_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'organization_create', None,
      200, 'text/html; charset=utf-8', 'neue'
    )


class PersonModelTest(DefaultModelTestCase):
  """
  model test class for object class person (Person)
  """

  model = Person
  attributes_values_db_initial = {
    'last_name': 'g7QXisvP'
  }
  attributes_values_db_updated = {
    'last_name': 'CkLihFLE'
  }
  attributes_values_view_initial = {
    'last_name': 'x85bUiPH'
  }
  attributes_values_view_updated = {
    'last_name': 'aghIw237'
  }
  attributes_values_view_invalid = {
    'last_name': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, False, 'person_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 1, 'created'
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, False, 'person_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neue', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, False, 'person_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, False, 'person_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, False, 'person_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0, 'deleted'
    )


class PersonViewsTest(DefaultViewTestCase):
  """
  views test class for object class person (Person)
  """

  def setUp(self):
    self.init()

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'person_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'ok'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'person_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'person_table', None,
      200, 'text/html; charset=utf-8', 'vorhanden'
    )

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'person_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'person_create', None,
      200, 'text/html; charset=utf-8', 'neue'
    )


class ContactModelTest(DefaultModelTestCase):
  """
  model test class for object class contact (Ansprechpartner:in)
  """

  model = Contact
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    organization = Organization.objects.create(
      name='iJjKAb2P'
    )
    person = Person.objects.create(
      last_name='9pKAIF5E'
    )
    cls.attributes_values_db_initial = {
      'organization': organization,
      'person': person
    }
    cls.attributes_values_db_updated = {
      'function': '3R7ZGdLu'
    }
    cls.attributes_values_view_initial = {
      'organization': str(organization.pk),
      'person': str(person.pk)
    }
    cls.attributes_values_view_updated = {
      'organization': str(organization.pk),
      'person': str(person.pk),
      'function': 'AQg4OopU'
    }
    cls.attributes_values_view_invalid = {
      'function': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, False, 'contact_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 2, 'created'
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, False, 'contact_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neue', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, False, 'contact_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, False, 'contact_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, False, 'contact_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0, 'deleted'
    )


class ContactViewsTest(DefaultViewTestCase):
  """
  views test class for object class contact (Ansprechpartner:in)
  """

  def setUp(self):
    self.init()

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'contact_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'contact_create', None,
      200, 'text/html; charset=utf-8', 'neue'
    )


class OriginatorModelTest(DefaultModelTestCase):
  """
  model test class for object class originator (Verursacher)
  """

  model = Originator
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    sector = Sector.objects.first()
    operator1 = Organization.objects.create(
      name='OqEGVai4'
    )
    operator2 = Organization.objects.create(
      name='PFqzwRF9'
    )
    cls.attributes_values_db_initial = {
      'sector': sector,
      'operator': operator1,
      'description': 'd1ZpOwn8',
      'emission_point': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'description': 'WhPxUQik'
    }
    cls.attributes_values_view_initial = {
      'sector': str(sector.pk),
      'operator': str(operator1.pk),
      'description': 's2fpbQ9n',
      'emission_point': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'sector': str(sector.pk),
      'operator': str(operator2.pk),
      'description': 'x4O4uocT',
      'emission_point': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'description': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, False, 'originator_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 1, 'created'
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, False, 'originator_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neue', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, False, 'originator_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1, 'updated_operator'
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, False, 'originator_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, False, 'originator_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0, 'deleted'
    )


class OriginatorViewsTest(DefaultViewTestCase):
  """
  views test class for object class originator (Verursacher)
  """

  def setUp(self):
    self.init()

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'originator_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'ok'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'originator_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'originator_table', None,
      200, 'text/html; charset=utf-8', 'vorhanden'
    )

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'originator_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'originator_create', None,
      200, 'text/html; charset=utf-8', 'neue'
    )

  def test_mapdata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'originator_mapdata', None,
      200, 'application/json', 'FeatureCollection'
    )


class ComplaintModelTest(DefaultModelTestCase):
  """
  model test class for object class complaint (Beschwerde)
  """

  model = Complaint
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    status1 = Status.objects.first()
    status2 = Status.objects.latest()
    type_of_immission = TypeOfImmission.objects.first()
    sector = Sector.objects.first()
    operator = Organization.objects.create(
      name='PUAlDiMq'
    )
    originator = Originator.objects.create(
      sector=sector,
      operator=operator,
      description='PEbwEh9H',
      emission_point=VALID_POINT_DB
    )
    cls.attributes_values_db_initial = {
      'status': status1,
      'type_of_immission': type_of_immission,
      'immission_point': VALID_POINT_DB,
      'originator': originator,
      'description': 'qut1URs0'
    }
    cls.attributes_values_db_updated = {
      'description': 'zt9auXPa'
    }
    cls.attributes_values_view_initial = {
      'date_of_receipt': VALID_DATE,
      'status': str(status1.pk),
      'type_of_immission': str(type_of_immission.pk),
      'immission_point': VALID_POINT_VIEW,
      'originator': str(originator.pk),
      'description': 'kUcRCEq7'
    }
    cls.attributes_values_view_updated = {
      'date_of_receipt': VALID_DATE,
      'status': str(status2.pk),
      'type_of_immission': str(type_of_immission.pk),
      'immission_point': VALID_POINT_VIEW,
      'originator': str(originator.pk),
      'description': 'TRLfDH9k'
    }
    cls.attributes_values_view_invalid = {
      'description': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, False, 'complaint_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 1, 'created'
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, False, 'complaint_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neue', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, False, 'complaint_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1, 'updated_status'
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, False, 'complaint_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, False, 'complaint_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0, 'deleted'
    )


class ComplaintViewsTest(DefaultViewTestCase):
  """
  views test class for object class complaint (Beschwerde)
  """

  def setUp(self):
    self.init()

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'complaint_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'ok'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'complaint_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'complaint_table', None,
      200, 'text/html; charset=utf-8', 'vorhanden'
    )

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'complaint_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'complaint_create', None,
      200, 'text/html; charset=utf-8', 'neue'
    )

  def test_mapdata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'complaint_mapdata', None,
      200, 'application/json', 'FeatureCollection'
    )


class ComplaintOrganizationManyToManyTest(DefaultManyToManyTestCase):
  """
  test class for many-to-many-relationship
  between complaint (Beschwerde) and organization (Organisation)
  """

  model_from = Complaint
  model_to = Organization

  @classmethod
  def setUpTestData(cls):
    type_of_immission = TypeOfImmission.objects.first()
    sector = Sector.objects.first()
    operator = Organization.objects.create(
      name='sklAapDM'
    )
    originator = Originator.objects.create(
      sector=sector,
      operator=operator,
      description='fiqgCONB',
      emission_point=VALID_POINT_DB
    )
    cls.model_from_attributes_values_db = {
      'type_of_immission': type_of_immission,
      'immission_point': VALID_POINT_DB,
      'originator': originator,
      'description': 'aBkb453M'
    }
    cls.model_to_attributes_values_db = {
      'name': 'CCykCmTx'
    }
    cls.test_object_from = cls.model_from.objects.create(**cls.model_from_attributes_values_db)
    cls.test_object_to = cls.model_to.objects.create(**cls.model_to_attributes_values_db)
    cls.test_object_from.complainers_organizations.add(cls.test_object_to)
    cls.relationship = cls.test_object_from.complainers_organizations

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_delete(self):
    self.generic_delete_test()


class ComplaintPersonManyToManyTest(DefaultManyToManyTestCase):
  """
  test class for many-to-many-relationship
  between complaint (Beschwerde) and person (Person)
  """

  model_from = Complaint
  model_to = Person

  @classmethod
  def setUpTestData(cls):
    type_of_immission = TypeOfImmission.objects.first()
    sector = Sector.objects.first()
    operator = Organization.objects.create(
      name='NXtnFe8H'
    )
    originator = Originator.objects.create(
      sector=sector,
      operator=operator,
      description='i7g3qten',
      emission_point=VALID_POINT_DB
    )
    cls.model_from_attributes_values_db = {
      'type_of_immission': type_of_immission,
      'immission_point': VALID_POINT_DB,
      'originator': originator,
      'description': '7JXQtscq'
    }
    cls.model_to_attributes_values_db = {
      'last_name': 'qRPUyrLI'
    }
    cls.test_object_from = cls.model_from.objects.create(**cls.model_from_attributes_values_db)
    cls.test_object_to = cls.model_to.objects.create(**cls.model_to_attributes_values_db)
    cls.test_object_from.complainers_persons.add(cls.test_object_to)
    cls.relationship = cls.test_object_from.complainers_persons

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_delete(self):
    self.generic_delete_test()


class EventModelTest(DefaultModelTestCase):
  """
  model test class for object class event (Journalereignis)
  """

  model = Event
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    sector = Sector.objects.first()
    operator = Organization.objects.create(
      name='szWLszDf'
    )
    originator = Originator.objects.create(
      sector=sector,
      operator=operator,
      description='amPaaSKF',
      emission_point=VALID_POINT_DB
    )
    type_of_immission = TypeOfImmission.objects.first()
    complaint = Complaint.objects.create(
      type_of_immission=type_of_immission,
      immission_point=VALID_POINT_DB,
      originator=originator,
      description='miDkPXSW'
    )
    type_of_event = TypeOfEvent.objects.first()
    cls.attributes_values_db_initial = {
      'complaint': complaint,
      'type_of_event': type_of_event,
      'user': 'DEg7UdpI'
    }
    cls.attributes_values_db_updated = {
      'user': 'eoSqXfg4'
    }
    cls.attributes_values_view_initial = {
      'complaint': str(complaint.pk),
      'type_of_event': str(type_of_event.pk),
      'user': '0tzYPl8C'
    }
    cls.attributes_values_view_updated = {
      'complaint': str(complaint.pk),
      'type_of_event': str(type_of_event.pk),
      'user': 'PYSZQDSu'
    }
    cls.attributes_values_view_invalid = {
      'user': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_view_create_success(self):
    self.generic_crud_view_test(
      False, True, False, 'event_create', self.attributes_values_view_initial,
      302, 'text/html; charset=utf-8', '', 1, 'created'
    )

  def test_view_create_error(self):
    self.generic_crud_view_test(
      False, True, False, 'event_create', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'neue', 0
    )

  def test_view_update_success(self):
    self.generic_crud_view_test(
      True, True, False, 'event_update', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 1
    )

  def test_view_update_error(self):
    self.generic_crud_view_test(
      True, True, False, 'event_update', self.attributes_values_view_invalid,
      200, 'text/html; charset=utf-8', 'nderungen', 1
    )

  def test_view_delete(self):
    self.generic_crud_view_test(
      True, True, False, 'event_delete', self.attributes_values_view_updated,
      302, 'text/html; charset=utf-8', '', 0, 'deleted'
    )


class EventViewsTest(DefaultViewTestCase):
  """
  views test class for object class event (Journalereignis)
  """

  def setUp(self):
    self.init()

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'event_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'ok'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'event_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'event_table', None,
      200, 'text/html; charset=utf-8', 'vorhanden'
    )

  def test_create_view_no_rights(self):
    self.generic_view_test(
      False, False, 'event_create', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_create_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'event_create', None,
      200, 'text/html; charset=utf-8', 'neue'
    )


class LogEntryViewsTest(DefaultViewTestCase):
  """
  views test class for object class log entry (Eintrag im Bearbeitungsverlauf)
  """

  def setUp(self):
    self.init()

  def test_tabledata_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'logentry_tabledata', TABLEDATA_VIEW_PARAMS, 200,
      'application/json', 'ok'
    )

  def test_table_view_no_rights(self):
    self.generic_view_test(
      False, False, 'logentry_table', None,
      200, 'text/html; charset=utf-8', 'keine Rechte'
    )

  def test_table_view_standard_rights(self):
    self.generic_view_test(
      True, False, 'logentry_table', None,
      200, 'text/html; charset=utf-8', 'vorhanden'
    )
