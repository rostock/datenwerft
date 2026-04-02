from datetime import date

from gdihrometadata.models.auxiliary import (
  Contact,
  DataType,
  Organization,
)
from gdihrometadata.models.codelists import (
  Access,
  AssetType,
  Charset,
  DatathemeCategory,
  Language,
  License,
)
from gdihrometadata.models.core import (
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
from gdihrometadata.models.enums import (
  ProcessingType,
  RepositoryType,
  ServiceType,
)

from ..abstract import DefaultModelTestCase


class SourceModelTest(DefaultModelTestCase):
  """
  test class for core model:
  source (Datenquelle)
  """

  model = Source
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_frequency = Frequency.objects.create(
      code='https://example.org/frequency/test', title='TestFrequency'
    )
    test_data_type = DataType.objects.create(title='TestDataType')
    cls.attributes_values_db_initial = {
      'last_import': date(2023, 1, 1),
      'import_frequency': test_frequency,
      'processing_type': ProcessingType.MANUALLY,
      'type': RepositoryType.FILE,
      'connection_info': 'test-connection-info',
      'data_type': test_data_type,
    }
    cls.attributes_values_db_updated = {
      'description': 'Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam.',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=test_organization,
    )
    cls.test_object.authors.add(test_contact)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    expected = f'{self.test_object.get_type_display()} ({self.test_object.connection_info})'
    self.generic_string_representation_test(expected)


class RepositoryModelTest(DefaultModelTestCase):
  """
  test class for core model:
  repository (Speicherort)
  """

  model = Repository
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_frequency = Frequency.objects.create(
      code='https://example.org/frequency/test', title='TestFrequency'
    )
    test_data_type = DataType.objects.create(title='TestDataType')
    cls.attributes_values_db_initial = {
      'creation': date(2023, 1, 1),
      'last_update': date(2023, 2, 1),
      'update_frequency': test_frequency,
      'type': RepositoryType.INTERFACE,
      'connection_info': 'test-connection-info',
      'data_type': test_data_type,
    }
    cls.attributes_values_db_updated = {
      'description': 'At vero eos et accusam et justo duo dolores et ea rebum.',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=test_organization,
    )
    cls.test_object.maintainers.add(test_contact)
    cls.test_object.authors.add(test_contact)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    expected = f'{self.test_object.get_type_display()} ({self.test_object.connection_info})'
    self.generic_string_representation_test(expected)


class AssetsetModelTest(DefaultModelTestCase):
  """
  test class for core model:
  asset-set (Asset-Sammlung)
  """

  model = Assetset
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_frequency = Frequency.objects.create(
      code='https://example.org/frequency/test', title='TestFrequency'
    )
    test_access = Access.objects.create(code='https://example.org/access/test', title='TestAccess')
    test_license = License.objects.create(
      code='https://example.org/license/test', title='TestLicense'
    )
    test_legal = Legal.objects.create(title='TestLegal', access=test_access, license=test_license)
    test_asset_type = AssetType.objects.create(
      code='https://example.org/assettype/test', title='TestAssetType'
    )
    cls.attributes_values_db_initial = {
      'creation': date(2023, 1, 1),
      'last_update': date(2023, 2, 1),
      'name': 'initial-assetset',
      'title': 'InitialAssetset',
      'update_frequency': test_frequency,
      'legal': test_legal,
      'type': test_asset_type,
    }
    cls.attributes_values_db_updated = {
      'name': 'updated-assetset',
      'title': 'UpdatedAssetset',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=test_organization,
    )
    cls.test_object.publishers.add(test_contact)
    cls.test_object.maintainers.add(test_contact)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation_with_title(self):
    self.generic_string_representation_test(self.test_object.title)

  def test_string_representation_without_title(self):
    self.test_object.title = None
    self.generic_string_representation_test(self.test_object.name)


class DatasetModelTest(DefaultModelTestCase):
  """
  test class for core model:
  dataset (Datensatz)
  """

  model = Dataset
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_frequency = Frequency.objects.create(
      code='https://example.org/frequency/test', title='TestFrequency'
    )
    test_access = Access.objects.create(code='https://example.org/access/test', title='TestAccess')
    test_license = License.objects.create(
      code='https://example.org/license/test', title='TestLicense'
    )
    test_legal = Legal.objects.create(title='TestLegal', access=test_access, license=test_license)
    test_data_type = DataType.objects.create(title='TestDataType')
    cls.attributes_values_db_initial = {
      'creation': date(2023, 1, 1),
      'last_update': date(2023, 2, 1),
      'name': 'initial-dataset',
      'title': 'InitialDataset',
      'link': 'https://example.org/dataset/test',
      'update_frequency': test_frequency,
      'legal': test_legal,
      'data_type': test_data_type,
    }
    cls.attributes_values_db_updated = {
      'name': 'updated-dataset',
      'title': 'UpdatedDataset',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=test_organization,
    )
    cls.test_object.publishers.add(test_contact)
    cls.test_object.maintainers.add(test_contact)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    expected = f'{self.test_object.title} ({self.test_object.name})'
    self.generic_string_representation_test(expected)


class ServiceModelTest(DefaultModelTestCase):
  """
  test class for core model:
  service (Service)
  """

  model = Service
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_access = Access.objects.create(code='https://example.org/access/test', title='TestAccess')
    test_license = License.objects.create(
      code='https://example.org/license/test', title='TestLicense'
    )
    test_legal = Legal.objects.create(title='TestLegal', access=test_access, license=test_license)
    test_language = Language.objects.create(
      code='https://example.org/language/test', title='TestLanguage'
    )
    test_charset = Charset.objects.create(
      code='https://example.org/charset/test', title='TestCharset'
    )
    cls.attributes_values_db_initial = {
      'name': 'initial-service',
      'title': 'InitialService',
      'link': 'https://example.org/service/test',
      'legal': test_legal,
      'type': ServiceType.WMS,
      'language': test_language,
      'charset': test_charset,
    }
    cls.attributes_values_db_updated = {
      'name': 'updated-service',
      'title': 'UpdatedService',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=test_organization,
    )
    cls.test_object.publishers.add(test_contact)
    cls.test_object.maintainers.add(test_contact)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    expected = (
      f'{self.test_object.get_type_display()} – {self.test_object.title} ({self.test_object.name})'
    )
    self.generic_string_representation_test(expected)


class TopicModelTest(DefaultModelTestCase):
  """
  test class for core model:
  topic (Datenthema)
  """

  model = Topic
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.attributes_values_db_initial = {
      'name': 'initial-topic',
      'title': 'InitialTopic',
    }
    cls.attributes_values_db_updated = {
      'name': 'updated-topic',
      'title': 'UpdatedTopic',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    test_category = DatathemeCategory.objects.create(
      code='https://example.org/datathemecategory/test', title='TestDatathemeCategory'
    )
    cls.test_object.categories.add(test_category)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    expected = f'{self.test_object.title} ({self.test_object.name})'
    self.generic_string_representation_test(expected)


class AppModelTest(DefaultModelTestCase):
  """
  test class for core model:
  app (App)
  """

  model = App
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_access = Access.objects.create(code='https://example.org/access/test', title='TestAccess')
    test_license = License.objects.create(
      code='https://example.org/license/test', title='TestLicense'
    )
    test_legal = Legal.objects.create(title='TestLegal', access=test_access, license=test_license)
    cls.attributes_values_db_initial = {
      'name': 'initial-app',
      'title': 'InitialApp',
      'link': 'https://example.org/app/test',
      'legal': test_legal,
    }
    cls.attributes_values_db_updated = {
      'name': 'updated-app',
      'title': 'UpdatedApp',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    test_organization = Organization.objects.create(
      name='test-organization', title='TestOrganization'
    )
    test_contact = Contact.objects.create(
      first_name='Test',
      last_name='Contact',
      email='test.contact@example.org',
      organization=test_organization,
    )
    cls.test_object.publishers.add(test_contact)
    cls.test_object.maintainers.add(test_contact)
    test_language = Language.objects.create(
      code='https://example.org/language/test', title='TestLanguage'
    )
    cls.test_object.languages.add(test_language)

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    expected = f'{self.test_object.title} ({self.test_object.name})'
    self.generic_string_representation_test(expected)
