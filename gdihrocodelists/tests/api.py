from gdihrocodelists.models import (
  Codelist,
  CodelistValue,
)

from .abstract import DefaultApiTestCase


class CodelistApiTest(DefaultApiTestCase):
  """
  test class for model:
  codelist (Codeliste)
  """

  model = Codelist
  attributes_values = {
    'name': 'initial',
    'title': 'InitialCodelist',
  }

  def setUp(self):
    self.init()

  def test_authorized(self):
    self.generic_api_test(
      log_in=True,
      view_name='codelist-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )

  def test_anonymous(self):
    self.generic_api_test(
      log_in=False,
      view_name='codelist-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )


class CodelistValueApiTest(DefaultApiTestCase):
  """
  test class for model:
  codelist value (Codelistenwert)
  """

  model = CodelistValue
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_codelist = Codelist.objects.create(name='test', title='TestCodelist')
    cls.attributes_values = {
      'codelist': test_codelist,
      'value': 'initial',
      'title': 'InitialCodelistValue',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values)

  def setUp(self):
    self.init()

  def test_authorized(self):
    self.generic_api_test(
      log_in=True,
      view_name='codelistvalue-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )

  def test_anonymous(self):
    self.generic_api_test(
      log_in=False,
      view_name='codelistvalue-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )


class GetByUuidTest(DefaultApiTestCase):
  """
  test class for API function get_by_uuid()
  """

  model = CodelistValue
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    test_codelist = Codelist.objects.create(name='test', title='TestCodelist')
    cls.attributes_values = {
      'codelist': test_codelist,
      'value': 'initial',
      'title': 'InitialCodelistValue',
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values)

  def setUp(self):
    self.init()

  def test_authorized_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_by_uuid',
      view_args={'uuid': str(self.test_object.uuid)},
      status_code=200,
      content_type='application/json',
      string=str(self.test_object.uuid),
    )

  def test_anonymous_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_by_uuid',
      view_args={'uuid': str(self.test_object.uuid)},
      status_code=200,
      content_type='application/json',
      string=str(self.test_object.uuid),
    )

  def test_authorized_not_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_by_uuid',
      view_args={'uuid': '550e8400-e29b-41d4-a716-446655440000'},
      status_code=404,
      content_type='application/json',
      string='Kein Objekt',
    )

  def test_anonymous_not_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_by_uuid',
      view_args={'uuid': '550e8400-e29b-41d4-a716-446655440000'},
      status_code=404,
      content_type='application/json',
      string='Kein Objekt',
    )
