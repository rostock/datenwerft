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

  def test_authorized_detail(self):
    self.generic_api_test(
      log_in=True,
      view_name='codelist-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )

  def test_anonymous_detail(self):
    self.generic_api_test(
      log_in=False,
      view_name='codelist-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )

  def test_authorized_list(self):
    self.generic_api_test(
      log_in=True,
      view_name='codelist-list',
      view_args=None,
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )

  def test_anonymous_list(self):
    self.generic_api_test(
      log_in=False,
      view_name='codelist-list',
      view_args=None,
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

  def test_authorized_detail(self):
    self.generic_api_test(
      log_in=True,
      view_name='codelistvalue-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )

  def test_anonymous_detail(self):
    self.generic_api_test(
      log_in=False,
      view_name='codelistvalue-detail',
      view_args={'pk': self.test_object.pk},
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )

  def test_authorized_list(self):
    self.generic_api_test(
      log_in=True,
      view_name='codelistvalue-list',
      view_args=None,
      status_code=200,
      content_type='application/json',
      string=self.test_object.title,
    )

  def test_anonymous_list(self):
    self.generic_api_test(
      log_in=False,
      view_name='codelistvalue-list',
      view_args=None,
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

  def test_authorized_uuid_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_codelist_or_codelistvalue_by_uuid',
      view_args={'uuid': str(self.test_object.uuid)},
      status_code=200,
      content_type='application/json',
      string=str(self.test_object.uuid),
    )

  def test_anonymous_uuid_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_codelist_or_codelistvalue_by_uuid',
      view_args={'uuid': str(self.test_object.uuid)},
      status_code=200,
      content_type='application/json',
      string=str(self.test_object.uuid),
    )

  def test_authorized_uuid_not_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_codelist_or_codelistvalue_by_uuid',
      view_args={'uuid': '550e8400-e29b-41d4-a716-446655440000'},
      status_code=404,
      content_type='application/json',
      string='Kein Objekt',
    )

  def test_anonymous_uuid_not_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_codelist_or_codelistvalue_by_uuid',
      view_args={'uuid': '550e8400-e29b-41d4-a716-446655440000'},
      status_code=404,
      content_type='application/json',
      string='Kein Objekt',
    )

  def test_authorized_invalid_uuid(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_codelist_or_codelistvalue_by_uuid',
      view_args={'uuid': '73t5Ahfe'},
      status_code=400,
      content_type='application/json',
      string='weist kein',
    )

  def test_anonymous_invalid_uuid(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_codelist_or_codelistvalue_by_uuid',
      view_args={'uuid': 'gfa68gHg'},
      status_code=400,
      content_type='application/json',
      string='weist kein',
    )


class GetCodelistValueByCodelistAndUuidTest(DefaultApiTestCase):
  """
  test class for API function get_codelistvalue_by_codelist_and_uuid()
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

  def test_authorized_codelistvalue_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_codelistvalue_by_codelist_and_uuid',
      view_args={
        'codelist_name': str(self.test_object.codelist.name),
        'codelistvalue_uuid': str(self.test_object.uuid),
      },
      status_code=200,
      content_type='application/json',
      string=str(self.test_object.uuid),
    )

  def test_anonymous_codelistvalue_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_codelistvalue_by_codelist_and_uuid',
      view_args={
        'codelist_name': str(self.test_object.codelist.name),
        'codelistvalue_uuid': str(self.test_object.uuid),
      },
      status_code=200,
      content_type='application/json',
      string=str(self.test_object.uuid),
    )

  def test_authorized_codelistvalue_not_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_codelistvalue_by_codelist_and_uuid',
      view_args={
        'codelist_name': str(self.test_object.codelist.name),
        'codelistvalue_uuid': '550e8400-e29b-41d4-a716-446655440000',
      },
      status_code=404,
      content_type='application/json',
      string='Kein Codelistenwert',
    )

  def test_anonymous_codelistvalue_not_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_codelistvalue_by_codelist_and_uuid',
      view_args={
        'codelist_name': str(self.test_object.codelist.name),
        'codelistvalue_uuid': '550e8400-e29b-41d4-a716-446655440000',
      },
      status_code=404,
      content_type='application/json',
      string='Kein Codelistenwert',
    )

  def test_authorized_codelist_not_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_codelistvalue_by_codelist_and_uuid',
      view_args={
        'codelist_name': '73t5Ahfe',
        'codelistvalue_uuid': str(self.test_object.uuid),
      },
      status_code=404,
      content_type='application/json',
      string='Keine Codeliste',
    )

  def test_anonymous_codelist_not_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_codelistvalue_by_codelist_and_uuid',
      view_args={
        'codelist_name': 'gfa68gHg',
        'codelistvalue_uuid': str(self.test_object.uuid),
      },
      status_code=404,
      content_type='application/json',
      string='Keine Codeliste',
    )

  def test_authorized_invalid_uuid(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_codelistvalue_by_codelist_and_uuid',
      view_args={
        'codelist_name': str(self.test_object.codelist.name),
        'codelistvalue_uuid': '73t5Ahfe',
      },
      status_code=400,
      content_type='application/json',
      string='weist kein',
    )

  def test_anonymous_invalid_uuid(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_codelistvalue_by_codelist_and_uuid',
      view_args={
        'codelist_name': str(self.test_object.codelist.name),
        'codelistvalue_uuid': 'gfa68gHg',
      },
      status_code=400,
      content_type='application/json',
      string='weist kein',
    )


class GetCodelistValuesByCodelistTest(DefaultApiTestCase):
  """
  test class for API function get_codelistvalues_by_codelist()
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

  def test_authorized_codelist_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_codelistvalues_by_codelist',
      view_args={'codelist_name': str(self.test_object.codelist.name)},
      status_code=200,
      content_type='application/json',
      string=str(self.test_object.uuid),
    )

  def test_anonymous_codelist_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_codelistvalues_by_codelist',
      view_args={'codelist_name': str(self.test_object.codelist.name)},
      status_code=200,
      content_type='application/json',
      string=str(self.test_object.uuid),
    )

  def test_authorized_codelist_not_found(self):
    self.generic_api_test(
      log_in=True,
      view_name='get_codelistvalues_by_codelist',
      view_args={'codelist_name': '73t5Ahfe'},
      status_code=404,
      content_type='application/json',
      string='Keine Codeliste',
    )

  def test_anonymous_codelist_not_found(self):
    self.generic_api_test(
      log_in=False,
      view_name='get_codelistvalues_by_codelist',
      view_args={'codelist_name': 'gfa68gHg'},
      status_code=404,
      content_type='application/json',
      string='Keine Codeliste',
    )
