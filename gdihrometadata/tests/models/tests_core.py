from datetime import date

from gdihrometadata.models import (
  App,
  Assetset,
  Dataset,
  Frequency,
  Legal,
  Repository,
  Service,
  Source,
  Topic,
)
from gdihrometadata.models.auxiliary import (
  Contact,
  DataType,
  Organization,
)
from gdihrometadata.models.codelists import (
  Access,
  AssetType,
  Charset,
  Language,
  License,
)
from gdihrometadata.models.enums import (
  ProcessingType,
  RepositoryType,
  ServiceType,
)

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
    cls.test_frequency = Frequency.objects.create(
      code='https://example.org/frequency/test', title='TestFrequency'
    )
    cls.test_data_type = DataType.objects.create(title='TestDataType')

    # Set up attributes
    cls.attributes_values_db_initial = {
      'last_import': '2023-01-01',
      'import_frequency': cls.test_frequency,
      'processing_type': ProcessingType.MANUALLY,
      'type': RepositoryType.FILE,
      'connection_info': 'test-connection-info',
      'data_type': cls.test_data_type,
    }
    cls.attributes_values_db_updated = {
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
    expected = f'{self.test_object.get_type_display()} ({self.test_object.connection_info})'
    self.assertEqual(str(self.test_object), expected)


class RepositoryModelTest(DefaultModelTestCase):
  """
  tests for Repository model
  """

  @classmethod
  def setUpTestData(cls):
    # Create related models
    # Create a valid source first
    cls.test_frequency = Frequency.objects.create(
      code='https://example.org/frequency/test', title='TestFrequency'
    )
    cls.test_data_type = DataType.objects.create(title='TestSourceDataType')
    cls.test_source_type = RepositoryType.FILE
    cls.test_source = Source.objects.create(
      last_import=date(2023, 1, 1),
      import_frequency=cls.test_frequency,
      processing_type=ProcessingType.AUTOMATICALLY,
      type=cls.test_source_type,  # Use created SourceType
      connection_info='test-source-connection-info',
      data_type=cls.test_data_type,
    )

    cls.test_update_frequency = Frequency.objects.create(code='CONTINUOUS', title='Continuous')

    # Set up attributes
    cls.attributes_values_db_initial = {
      # 'title': 'TestRepository', # Removed title
      'connection_info': 'test-connection-info',
      'type': RepositoryType.INTERFACE,
      'creation': date(2023, 1, 1),
      'last_update': date(2023, 2, 1),
    }
    cls.attributes_values_db_updated = {
      'connection_info': 'test-connection-info-updated',
      'type': RepositoryType.DATABASE,
      'creation': date(2023, 1, 2),
      'last_update': date(2023, 2, 2),
    }

    cls.attributes_values_db_initial['source'] = cls.test_source
    cls.attributes_values_db_initial['data_type'] = cls.test_data_type
    cls.attributes_values_db_initial['update_frequency'] = cls.test_update_frequency

    # Create the object with initial attributes
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
    expected = f'{self.test_object.get_type_display()} ({self.test_object.connection_info})'
    self.assertEqual(str(self.test_object), expected)


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

    # Create related models needed for Assetset
    cls.test_legal = Legal.objects.create(
      title='TestLegal', access=cls.test_access, license=cls.test_license
    )
    cls.test_update_frequency = Frequency.objects.create(code='BIANNUALLY', title='Biannually')
    cls.test_asset_type = AssetType.objects.create(
      code='https://example.org/assettype/test', title='TestAssetType'
    )
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
      'name': 'test-assetset',
      'title': 'TestAssetset',
      'update_frequency': cls.test_update_frequency,
      'legal': cls.test_legal,
      'type': cls.test_asset_type,
      'creation': date(2023, 1, 1),
      'last_update': date(2023, 2, 1),
    }
    cls.attributes_values_db_updated = {
      'name': 'test-assetset-updated',
      'title': 'UpdatedAssetset',
      'last_update': date(2023, 3, 1),
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
    cls.test_data_type = DataType.objects.create(title='TestDatasetDataType')
    cls.test_access = Access.objects.create(
      code='https://example.org/access/test', title='TestAccess'
    )
    cls.test_license = License.objects.create(
      code='https://example.org/license/test', title='TestLicense'
    )
    cls.test_legal = Legal.objects.create(
      title='TestLegal', access=cls.test_access, license=cls.test_license
    )
    cls.test_update_frequency = Frequency.objects.create(code='ANNUALLY', title='Annually')

    # Set up attributes
    cls.attributes_values_db_initial = {
      'name': 'test-dataset',
      'title': 'TestDataset',
      'link': 'https://example.org/dataset/test',
      'creation': date(2023, 1, 1),
      'last_update': date(2023, 2, 1),
    }
    cls.attributes_values_db_updated = {
      'name': 'test-dataset-updated',
      'title': 'TestDatasetUpdated',
      'link': 'https://example.org/dataset/test-updated',
      'creation': date(2023, 1, 2),
      'last_update': date(2023, 2, 2),
    }

    cls.attributes_values_db_initial['data_type'] = cls.test_data_type
    cls.attributes_values_db_initial['legal'] = cls.test_legal
    cls.attributes_values_db_initial['update_frequency'] = cls.test_update_frequency

    # Create the object with initial attributes
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
    # Create necessary fields for Dataset
    cls.test_data_type = DataType.objects.create(title='TestDatasetDataType')
    cls.test_access = Access.objects.create(
      code='https://example.org/access/test-service', title='TestServiceAccess'
    )
    cls.test_license = License.objects.create(
      code='https://example.org/license/test-service', title='TestServiceLicense'
    )
    cls.test_legal = Legal.objects.create(
      title='TestServiceLegal', access=cls.test_access, license=cls.test_license
    )
    cls.test_language = Language.objects.create(
      code='https://www.loc.gov/standards/iso639-2#eng', title='English'
    )
    cls.test_charset = Charset.objects.create(
      code='https://www.iana.org/assignments/character-sets/utf-8', title='UTF-8'
    )

    cls.test_dataset = Dataset.objects.create(
      name='test-dataset',
      title='TestDataset',
      link='https://example.org/dataset/test',
      update_frequency=cls.test_frequency,
      legal=cls.test_legal,
      data_type=cls.test_data_type,
      creation=date(2023, 1, 1),
      last_update=date(2023, 2, 1),
    )

    # Set up attributes
    cls.attributes_values_db_initial = {
      'name': 'test-service',
      'title': 'TestService',
      'link': 'https://example.org/service/test',
      'legal': cls.test_legal,
      'type': ServiceType.WMS,
      'language': cls.test_language,
      'charset': cls.test_charset,
    }
    cls.attributes_values_db_updated = {
      'name': 'test-service-updated',
      'title': 'UpdatedService',
      'link': 'https://example.org/service/updated',
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
    expected = f'{self.test_object.title} ({self.test_object.get_type_display()})'
    self.assertEqual(str(self.test_object), expected)

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
    # Create necessary fields for Dataset
    cls.test_data_type = DataType.objects.create(title='TestTopicDataType')
    cls.test_access = Access.objects.create(
      code='https://example.org/access/test-topic', title='TestTopicAccess'
    )
    cls.test_license = License.objects.create(
      code='https://example.org/license/test-topic', title='TestTopicLicense'
    )
    cls.test_legal = Legal.objects.create(
      title='TestTopicLegal', access=cls.test_access, license=cls.test_license
    )
    cls.test_dataset = Dataset.objects.create(
      name='test-dataset-for-topic',
      title='TestDataset',
      link='https://example.org/dataset/test',
      update_frequency=Frequency.objects.create(
        code='http://inspire.ec.europa.eu/metadata-codelist/MaintenanceFrequency/daily',
        title='täglich',
      ),
      data_type=cls.test_data_type,
      legal=cls.test_legal,
      creation=date(2023, 1, 1),
      last_update=date(2023, 2, 1),
    )
    cls.test_service = Service.objects.create(
      name='test-service',
      title='TestService',
      link='https://example.org/service/test',
      legal=cls.test_legal,
      type=ServiceType.API_FEATURES,
      language=Language.objects.create(
        code='https://www.loc.gov/standards/iso639-2#ger', title='Deutsch'
      ),
      charset=Charset.objects.create(
        code='https://www.iana.org/assignments/character-sets/utf-8', title='UTF-8'
      ),
    )

    # Set up attributes
    cls.attributes_values_db_initial = {
      'name': 'test-topic',
      'title': 'TestTopic',
      'description': 'Description of the test topic',
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
    # Create necessary fields for Dataset
    cls.test_data_type = DataType.objects.create(title='TestAppDatasetDataType')
    cls.test_access = Access.objects.create(
      code='https://example.org/access/test-app', title='TestAppAccess'
    )
    cls.test_license = License.objects.create(
      code='https://example.org/license/test-app', title='TestAppLicense'
    )
    cls.test_legal = Legal.objects.create(
      title='TestAppLegal', access=cls.test_access, license=cls.test_license
    )
    cls.test_language = Language.objects.create(
      code='https://www.loc.gov/standards/iso639-2#eng', title='English'
    )
    cls.test_charset = Charset.objects.create(
      code='https://www.iana.org/assignments/character-sets/utf-8', title='UTF-8'
    )
    cls.test_frequency = Frequency.objects.create(
      code='http://inspire.ec.europa.eu/metadata-codelist/MaintenanceFrequency/monthly',
      title='monatlich',
    )

    cls.test_dataset = Dataset.objects.create(
      name='test-dataset-for-app',
      title='TestDataset',
      link='https://example.org/dataset/test-app',
      update_frequency=cls.test_frequency,
      data_type=cls.test_data_type,
      legal=cls.test_legal,
      creation=date(2023, 1, 1),
      last_update=date(2023, 2, 1),
    )
    cls.test_service = Service.objects.create(
      name='test-service-for-app',
      title='TestServiceForApp',
      link='https://example.org/service/test-app',
      legal=cls.test_legal,
      type=ServiceType.WCS,
      language=cls.test_language,
      charset=cls.test_charset,
    )

    # Set up attributes
    cls.attributes_values_db_initial = {
      'name': 'test-app',
      'title': 'TestApp',
      'link': 'https://example.org/app/test',
      'legal': cls.test_legal,
    }
    cls.attributes_values_db_updated = {
      'name': 'test-app-updated',
      'title': 'UpdatedApp',
      'link': 'https://example.org/app/updated',
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
