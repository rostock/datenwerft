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

from ..abstract import DefaultModelTestCase


class CrsSetModelTest(DefaultModelTestCase):
  """
  test class for auxiliary model:
  set of coordinate reference systems (Set aus einem oder mehreren Koordinatenreferenzsystem(en))
  """

  model = CrsSet
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.attributes_values_db_initial = {
      'title': 'InitialCrsSet',
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedCrsSet',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    test_crs = Crs.objects.create(code='https://example.org/crs/test', title='TestCrs')
    cls.test_object.crs.add(test_crs)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    self.generic_string_representation_test(self.test_object.title)


class DataTypeModelTest(DefaultModelTestCase):
  """
  test class for auxiliary model:
  data type (Datentyp)
  """

  model = DataType
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_format = Format.objects.create(code='https://example.org/format/test', title='TestFormat')
    test_mime_type = MimeType.objects.create(
      code='https://example.org/mimetype/test', title='TestMimeType'
    )
    cls.attributes_values_db_initial = {
      'title': 'InitialDataType',
      'format': test_format,
      'mime_type': test_mime_type,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedDataType',
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

  def test_string_representation(self):
    self.generic_string_representation_test(self.test_object.title)


class LegalModelTest(DefaultModelTestCase):
  """
  test class for auxiliary model:
  legal (rechtliche Informationen)
  """

  model = Legal
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_access = Access.objects.create(code='https://example.org/access/test', title='TestAccess')
    test_license = License.objects.create(
      code='https://example.org/license/test', title='TestLicense'
    )
    cls.attributes_values_db_initial = {
      'title': 'InitialLegal',
      'access': test_access,
      'license': test_license,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedLegal',
      'constraints': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam.',
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

  def test_string_representation(self):
    self.generic_string_representation_test(self.test_object.title)


class SpatialReferenceModelTest(DefaultModelTestCase):
  """
  test class for auxiliary model:
  spatial reference (räumlicher Bezug)
  """

  model = SpatialReference
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_political_geocoding_level = PoliticalGeocodingLevel.objects.create(
      code='https://example.org/politicalgecodinglevel/test', title='TestPoliticalGeocodingLevel'
    )
    test_political_geocoding = PoliticalGeocoding.objects.create(
      code='https://example.org/politicalgeocoding/test', title='TestPoliticalGeocoding'
    )
    cls.attributes_values_db_initial = {
      'title': 'InitialSpatialReference',
      'extent_spatial_south': Decimal('-10.12345'),
      'extent_spatial_west': Decimal('-40.12345'),
      'extent_spatial_north': Decimal('30.12345'),
      'extent_spatial_east': Decimal('20.12345'),
      'political_geocoding_level': test_political_geocoding_level,
      'political_geocoding': test_political_geocoding,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedSpatialReference',
      'extent_spatial_south': Decimal('-15.12345'),
      'extent_spatial_west': Decimal('-45.12345'),
      'extent_spatial_north': Decimal('35.12345'),
      'extent_spatial_east': Decimal('25.12345'),
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

  def test_string_representation(self):
    self.generic_string_representation_test(self.test_object.title)


class OrganizationModelTest(DefaultModelTestCase):
  """
  test class for auxiliary model:
  organization (Organisation)
  """

  model = Organization
  attributes_values_db_initial = {
    'name': 'initial-organization',
    'title': 'InitialOrganization',
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

  def test_string_representation(self):
    self.generic_string_representation_test(self.test_object.title)


class ContactModelTest(DefaultModelTestCase):
  """
  test class for auxiliary model:
  contact (Kontakt)
  """

  model = Contact
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    cls.attributes_values_db_initial = {
      'first_name': 'Test',
      'last_name': 'User',
      'email': 'test.user@example.org',
      'organization': test_organization,
    }
    cls.attributes_values_db_updated = {
      'first_name': 'Updated',
      'last_name': 'Person',
      'email': 'updated.person@example.org',
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

  def test_string_representation_with_name(self):
    name = f'{self.test_object.first_name} {self.test_object.last_name}'
    expected = name + f' ({self.test_object.organization})'
    self.generic_string_representation_test(expected)

  def test_string_representation_without_name(self):
    self.test_object.first_name, self.test_object.last_name = None, None
    expected = f'{self.test_object.email} ({self.test_object.organization})'
    self.generic_string_representation_test(expected)
