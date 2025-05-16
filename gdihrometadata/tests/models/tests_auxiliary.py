from decimal import Decimal

from gdihrometadata.models import (
  Access,
  Contact,
  Crs,
  CrsSet,
  DataType,
  Format,
  Legal,
  License,
  MimeType,
  Organization,
  PoliticalGeocoding,
  PoliticalGeocodingLevel,
  SpatialReference,
)

from ..base import DefaultModelTestCase


class CrsSetModelTest(DefaultModelTestCase):
  """
  tests for CrsSet model
  """

  model = CrsSet
  attributes_values_db_initial = {'title': 'TestCrsSet'}
  attributes_values_db_updated = {'title': 'UpdatedCrsSet'}

  def setUp(self):
    self.init()
    # Create related Crs for testing
    self.test_crs = Crs.objects.create(code='https://example.org/crs/test', title='TestCrs')

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_add_crs(self):
    # Test adding a Crs to the CrsSet
    self.test_object.crs.add(self.test_crs)
    self.assertEqual(self.test_object.crs.count(), 1)
    self.assertEqual(self.test_object.crs.first(), self.test_crs)


class DataTypeModelTest(DefaultModelTestCase):
  """
  tests for DataType model
  """

  model = DataType
  attributes_values_db_initial = {'title': 'TestDataType'}
  attributes_values_db_updated = {'title': 'UpdatedDataType'}

  def setUp(self):
    self.init()
    # Create related models
    self.test_format = Format.objects.create(
      code='https://example.org/format/test', title='TestFormat'
    )
    self.test_mime_type = MimeType.objects.create(
      code='https://example.org/mimetype/test', title='TestMimeType'
    )

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_with_related_models(self):
    # Test with related models
    self.test_object.format = self.test_format
    self.test_object.mime_type = self.test_mime_type
    self.test_object.save()

    # Verify relationships
    self.assertEqual(self.test_object.format, self.test_format)
    self.assertEqual(self.test_object.mime_type, self.test_mime_type)


class LegalModelTest(DefaultModelTestCase):
  """
  tests for Legal model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models first
    cls.test_access = Access.objects.create(
      code='https://example.org/access/test', title='TestAccess'
    )
    cls.test_license = License.objects.create(
      code='https://example.org/license/test', title='TestLicense'
    )

    # Set up attributes with foreign keys
    cls.attributes_values_db_initial = {
      'title': 'TestLegal',
      'access': cls.test_access,
      'license': cls.test_license,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedLegal',
      'constraints': 'Test constraints',
    }

    # Create the test object
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.count = 0
    cls.create_test_object_in_classmethod = False

  model = Legal

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class SpatialReferenceModelTest(DefaultModelTestCase):
  """
  tests for SpatialReference model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models first
    cls.test_political_geocoding_level = PoliticalGeocodingLevel.objects.create(
      code='https://example.org/politicalgecodinglevel/test', title='TestPoliticalGeocodingLevel'
    )
    cls.test_political_geocoding = PoliticalGeocoding.objects.create(
      code='https://example.org/politicalgeocoding/test', title='TestPoliticalGeocoding'
    )

    # Set up attributes with required fields and foreign keys
    cls.attributes_values_db_initial = {
      'title': 'TestSpatialReference',
      'extent_spatial_south': Decimal('-10.12345'),
      'extent_spatial_east': Decimal('20.12345'),
      'extent_spatial_north': Decimal('30.12345'),
      'extent_spatial_west': Decimal('-40.12345'),
      'political_geocoding_level': cls.test_political_geocoding_level,
      'political_geocoding': cls.test_political_geocoding,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedSpatialReference',
      'extent_spatial_south': Decimal('-15.12345'),
      'extent_spatial_east': Decimal('25.12345'),
      'extent_spatial_north': Decimal('35.12345'),
      'extent_spatial_west': Decimal('-45.12345'),
    }

    # Create the test object
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.count = 0
    cls.create_test_object_in_classmethod = False

  model = SpatialReference

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class OrganizationModelTest(DefaultModelTestCase):
  """
  tests for Organization model
  """

  model = Organization
  attributes_values_db_initial = {
    'name': 'test-organization',
    'title': 'TestOrganization',
    'image': 'https://example.org/images/org.png',
  }
  attributes_values_db_updated = {
    'name': 'updated-organization',
    'title': 'UpdatedOrganization',
    'image': 'https://example.org/images/updated-org.png',
  }

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_str_method(self):
    # Test the string representation
    self.assertEqual(str(self.test_object), self.test_object.title)


class ContactModelTest(DefaultModelTestCase):
  """
  tests for Contact model
  """

  model = Contact
  attributes_values_db_initial = {
    'first_name': 'Test',
    'last_name': 'User',
    'email': 'test.user@example.org',
  }
  attributes_values_db_updated = {
    'first_name': 'Updated',
    'last_name': 'Person',
    'email': 'updated.person@example.org',
  }

  def setUp(self):
    self.init()
    # Create related organization
    self.test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_with_organization(self):
    # Test with organization relationship
    self.test_object.organization = self.test_organization
    self.test_object.save()

    # Verify relationship
    self.assertEqual(self.test_object.organization, self.test_organization)

  def test_str_method_with_name(self):
    # Test string representation with name
    self.assertEqual(
      str(self.test_object), f'{self.test_object.first_name} {self.test_object.last_name}'
    )

  def test_str_method_without_name(self):
    # Test string representation without name
    self.test_object.first_name = None
    self.test_object.last_name = None
    self.test_object.save()
    self.assertEqual(str(self.test_object), self.test_object.email)
