from datetime import date

from gdihrometadata.models.auxiliary import (
  Contact,
  DataType,
  Organization,
)
from gdihrometadata.models.codelists import (
  Frequency,
)
from gdihrometadata.models.core import (
  Repository,
  Source,
)
from gdihrometadata.models.enums import (
  ProcessingType,
  RepositoryType,
)

from .abstract import DefaultApiTestCase


class SourceApiTest(DefaultApiTestCase):
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
    cls.attributes_values = {
      'last_import': date(2023, 1, 1),
      'import_frequency': test_frequency,
      'processing_type': ProcessingType.MANUALLY,
      'type': RepositoryType.FILE,
      'connection_info': 'test-connection-info',
      'data_type': test_data_type,
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values)
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

  def test_authorized_detail(self):
    self.generic_api_test(
      log_in=True,
      view_name='source-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.connection_info,
    )

  def test_anonymous_detail(self):
    self.generic_api_test(
      log_in=False,
      view_name='source-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string='*** hidden on read-only access ***',
    )

  def test_authorized_list(self):
    self.generic_api_test(
      log_in=True,
      view_name='source-list',
      view_args=None,
      status_code=200,
      content_type='application/json',
      string=self.test_object.connection_info,
    )

  def test_anonymous_list(self):
    self.generic_api_test(
      log_in=False,
      view_name='source-list',
      view_args=None,
      status_code=200,
      content_type='application/json',
      string='*** hidden on read-only access ***',
    )


class RepositoryApiTest(DefaultApiTestCase):
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
    cls.attributes_values = {
      'creation': date(2023, 1, 1),
      'last_update': date(2023, 2, 1),
      'update_frequency': test_frequency,
      'type': RepositoryType.INTERFACE,
      'connection_info': 'test-connection-info',
      'data_type': test_data_type,
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values)
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

  def test_authorized_detail(self):
    self.generic_api_test(
      log_in=True,
      view_name='repository-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.connection_info,
    )

  def test_anonymous_detail(self):
    self.generic_api_test(
      log_in=False,
      view_name='repository-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string='*** hidden on read-only access ***',
    )

  def test_authorized_list(self):
    self.generic_api_test(
      log_in=True,
      view_name='repository-list',
      view_args=None,
      status_code=200,
      content_type='application/json',
      string=self.test_object.connection_info,
    )

  def test_anonymous_list(self):
    self.generic_api_test(
      log_in=False,
      view_name='repository-list',
      view_args=None,
      status_code=200,
      content_type='application/json',
      string='*** hidden on read-only access ***',
    )


class GetByUuidTest(DefaultApiTestCase):
  """
  test class for API function get_by_uuid()
  """

  model = Source
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_frequency = Frequency.objects.create(
      code='https://example.org/frequency/test', title='TestFrequency'
    )
    test_data_type = DataType.objects.create(title='TestDataType')
    cls.attributes_values = {
      'last_import': date(2023, 1, 1),
      'import_frequency': test_frequency,
      'processing_type': ProcessingType.MANUALLY,
      'type': RepositoryType.FILE,
      'connection_info': 'test-connection-info',
      'data_type': test_data_type,
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values)
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

  def test_authorized_uuid_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_metadata_by_uuid',
      view_args={'uuid': str(self.test_object.uuid)},
      status_code=200,
      content_type='application/json',
      string=str(self.test_object.uuid),
    )

  def test_anonymous_uuid_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_metadata_by_uuid',
      view_args={'uuid': str(self.test_object.uuid)},
      status_code=200,
      content_type='application/json',
      string='*** hidden on read-only access ***',
    )

  def test_authorized_uuid_not_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_metadata_by_uuid',
      view_args={'uuid': '550e8400-e29b-41d4-a716-446655440000'},
      status_code=404,
      content_type='application/json',
      string='Kein Objekt',
    )

  def test_anonymous_uuid_not_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_metadata_by_uuid',
      view_args={'uuid': '550e8400-e29b-41d4-a716-446655440000'},
      status_code=404,
      content_type='application/json',
      string='Kein Objekt',
    )

  def test_authorized_invalid_uuid(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_metadata_by_uuid',
      view_args={'uuid': '73t5Ahfe'},
      status_code=400,
      content_type='application/json',
      string='weist kein',
    )

  def test_anonymous_invalid_uuid(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_metadata_by_uuid',
      view_args={'uuid': 'gfa68gHg'},
      status_code=400,
      content_type='application/json',
      string='weist kein',
    )
