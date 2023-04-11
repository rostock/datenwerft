from bemas.models import Contact, Organization, Person
from .base import DefaultModelTestCase, DefaultViewTestCase
from .constants_vars import INVALID_STRING, TABLEDATA_VIEW_PARAMS


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
      302, 'text/html; charset=utf-8', '', 1
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
      302, 'text/html; charset=utf-8', '', 0
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
      302, 'text/html; charset=utf-8', '', 1
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
      302, 'text/html; charset=utf-8', '', 0
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
      302, 'text/html; charset=utf-8', '', 2
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
      302, 'text/html; charset=utf-8', '', 0
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
