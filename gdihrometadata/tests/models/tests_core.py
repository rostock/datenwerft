from datetime import date, datetime
from decimal import Decimal

from gdihrometadata.models import (
  Access,
  App,
  Assetset,
  Contact,
  Crs,
  Dataset,
  DataType,
  Frequency,
  License,
  Organization,
  Repository,
  Service,
  Source,
  SpatialReference,
  Topic,
)
from gdihrometadata.models.enums import ProcessingType, RepositoryType, ServiceType

from ..base import DefaultModelTestCase


class SourceModelTest(DefaultModelTestCase):
  """
  tests for Source model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models
    cls.test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    cls.test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=cls.test_organization,
    )

    # Set up attributes
    cls.attributes_values_db_initial = {
      'title': 'TestSource',
      'provider': cls.test_organization,
      'contact': cls.test_contact,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedSource',
      'description': 'Description of the updated source',
    }

    # Create the test object
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.count = 0
    cls.create_test_object_in_classmethod = False

  model = Source

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


class RepositoryModelTest(DefaultModelTestCase):
  """
  tests for Repository model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models
    cls.test_source = Source.objects.create(title='TestRepositorySource')

    # Set up attributes
    cls.attributes_values_db_initial = {
      'title': 'TestRepository',
      'endpoint': 'https://example.org/repo/test',
      'source': cls.test_source,
      'type': RepositoryType.GITHUB,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedRepository',
      'endpoint': 'https://example.org/repo/updated',
      'description': 'Description of the updated repository',
    }

    # Create the test object
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.count = 0
    cls.create_test_object_in_classmethod = False

  model = Repository

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


class AssetsetModelTest(DefaultModelTestCase):
  """
  tests for Assetset model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models
    cls.test_access = Access.objects.create(
      code='https://example.org/access/test', title='TestAccess'
    )
    cls.test_license = License.objects.create(
      code='https://example.org/license/test', title='TestLicense'
    )

    # Set up attributes
    cls.attributes_values_db_initial = {
      'title': 'TestAssetset',
      'version': '1.0.0',
      'access_url': 'https://example.org/assets/test',
      'processing_type': ProcessingType.PROCESSED,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedAssetset',
      'version': '1.1.0',
      'access_url': 'https://example.org/assets/updated',
      'description': 'Description of the updated assetset',
    }

    # Create the test object
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.count = 0
    cls.create_test_object_in_classmethod = False

  model = Assetset

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


class DatasetModelTest(DefaultModelTestCase):
  """
  tests for Dataset model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models
    cls.test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    cls.test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=cls.test_organization,
    )
    cls.test_frequency = Frequency.objects.create(
      code='https://example.org/frequency/test', title='TestFrequency'
    )
    cls.test_spatial_reference = SpatialReference.objects.create(
      title='TestSpatialReference',
      extent_spatial_south=Decimal('-10.12345'),
      extent_spatial_east=Decimal('20.12345'),
      extent_spatial_north=Decimal('30.12345'),
      extent_spatial_west=Decimal('-40.12345'),
    )
    cls.test_crs = Crs.objects.create(code='https://example.org/crs/test', title='TestCrs')
    cls.test_data_type = DataType.objects.create(title='TestDataType')

    # Set up attributes
    cls.attributes_values_db_initial = {
      'title': 'TestDataset',
      'publisher': cls.test_organization,
      'contact': cls.test_contact,
      'creation': date(2023, 1, 1),
      'last_update': date(2023, 2, 1),
      'update_frequency': cls.test_frequency,
      'spatial_reference': cls.test_spatial_reference,
      'native_crs': cls.test_crs,
      'data_type': cls.test_data_type,
      'extent_temporal_start': datetime(2023, 1, 1, 0, 0, 0),
      'extent_temporal_end': datetime(2023, 2, 1, 23, 59, 59),
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedDataset',
      'creation': date(2023, 1, 15),
      'last_update': date(2023, 2, 15),
      'description': 'Description of the updated dataset',
    }

    # Create the test object
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.count = 0
    cls.create_test_object_in_classmethod = False

  model = Dataset

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


class ServiceModelTest(DefaultModelTestCase):
  """
  tests for Service model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models
    cls.test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    cls.test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=cls.test_organization,
    )
    cls.test_frequency = Frequency.objects.create(
      code='https://example.org/frequency/test', title='TestFrequency'
    )
    cls.test_dataset = Dataset.objects.create(
      title='TestDataset',
      creation=date(2023, 1, 1),
      last_update=date(2023, 2, 1),
    )

    # Set up attributes
    cls.attributes_values_db_initial = {
      'title': 'TestService',
      'provider': cls.test_organization,
      'contact': cls.test_contact,
      'creation': date(2023, 1, 1),
      'last_update': date(2023, 2, 1),
      'update_frequency': cls.test_frequency,
      'endpoint': 'https://example.org/service/test',
      'service_type': ServiceType.REST,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedService',
      'endpoint': 'https://example.org/service/updated',
      'description': 'Description of the updated service',
    }

    # Create the test object
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.count = 0
    cls.create_test_object_in_classmethod = False

  model = Service

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

  def test_dataset_relation(self):
    # Test adding a dataset to the service
    self.test_object.datasets.add(self.test_dataset)
    self.assertEqual(self.test_object.datasets.count(), 1)
    self.assertEqual(self.test_object.datasets.first(), self.test_dataset)


class TopicModelTest(DefaultModelTestCase):
  """
  tests for Topic model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models
    cls.test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    cls.test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=cls.test_organization,
    )
    cls.test_dataset = Dataset.objects.create(
      title='TestDataset',
      creation=date(2023, 1, 1),
      last_update=date(2023, 2, 1),
    )
    cls.test_service = Service.objects.create(
      title='TestService',
      creation=date(2023, 1, 1),
      last_update=date(2023, 2, 1),
      endpoint='https://example.org/service/test',
      service_type=ServiceType.REST,
    )

    # Set up attributes
    cls.attributes_values_db_initial = {
      'title': 'TestTopic',
      'owner': cls.test_organization,
      'contact': cls.test_contact,
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedTopic',
      'description': 'Description of the updated topic',
    }

    # Create the test object
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.count = 0
    cls.create_test_object_in_classmethod = False

  model = Topic

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

  def test_dataset_relation(self):
    # Test adding a dataset to the topic
    self.test_object.datasets.add(self.test_dataset)
    self.assertEqual(self.test_object.datasets.count(), 1)
    self.assertEqual(self.test_object.datasets.first(), self.test_dataset)

  def test_service_relation(self):
    # Test adding a service to the topic
    self.test_object.services.add(self.test_service)
    self.assertEqual(self.test_object.services.count(), 1)
    self.assertEqual(self.test_object.services.first(), self.test_service)


class AppModelTest(DefaultModelTestCase):
  """
  tests for App model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models
    cls.test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    cls.test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=cls.test_organization,
    )
    cls.test_dataset = Dataset.objects.create(
      title='TestDataset',
      creation=date(2023, 1, 1),
      last_update=date(2023, 2, 1),
    )
    cls.test_service = Service.objects.create(
      title='TestService',
      creation=date(2023, 1, 1),
      last_update=date(2023, 2, 1),
      endpoint='https://example.org/service/test',
      service_type=ServiceType.REST,
    )

    # Set up attributes
    cls.attributes_values_db_initial = {
      'title': 'TestApp',
      'publisher': cls.test_organization,
      'contact': cls.test_contact,
      'app_url': 'https://example.org/app/test',
    }
    cls.attributes_values_db_updated = {
      'title': 'UpdatedApp',
      'app_url': 'https://example.org/app/updated',
      'description': 'Description of the updated app',
    }

    # Create the test object
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.count = 0
    cls.create_test_object_in_classmethod = False

  model = App

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

  def test_dataset_relation(self):
    # Test adding a dataset to the app
    self.test_object.datasets.add(self.test_dataset)
    self.assertEqual(self.test_object.datasets.count(), 1)
    self.assertEqual(self.test_object.datasets.first(), self.test_dataset)

  def test_service_relation(self):
    # Test adding a service to the app
    self.test_object.services.add(self.test_service)
    self.assertEqual(self.test_object.services.count(), 1)
    self.assertEqual(self.test_object.services.first(), self.test_service)
