from django.contrib.auth.models import Permission, User
from django.contrib.messages import storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from json import loads

from datenmanagement.models.base import Codelist, ComplexModel, Metamodel, SimpleModel
from datenmanagement.views import DataAddView, DataChangeView, DataDeleteView
from .constants_vars import *
from .functions import clean_object_filter, create_test_subset, get_object, load_sql_schema


class DefaultTestCase(TestCase):
  """
  default abstract test class
  """

  databases = DATABASES

  def init(self):
    self.test_user = User.objects.create_user(username=USERNAME, password=PASSWORD)


class DefaultModelTestCase(DefaultTestCase):
  """
  abstract test class for models
  """

  model = None
  create_test_object_in_classmethod = True
  create_test_subset_in_classmethod = True
  attributes_values_db_initial = {}
  test_object = None

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()
    if cls.create_test_object_in_classmethod:
      cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    if cls.test_object and cls.create_test_subset_in_classmethod:
      cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def init(self):
    super().init()

  def generic_existance_test(self, model, test_object):
    """
    tests general existance of passed test object

    :param self
    :param model: model
    :param test_object: test object
    """
    # actual number of objects equals one?
    self.assertEqual(model.objects.all().count(), 1)
    # on creation: object created exactly as it should have been created?
    # on update: object updated exactly as it should have been updated?
    self.assertEqual(test_object, self.test_object)

  def generic_create_test(self, model, object_filter):
    """
    tests creation of test object of passed model

    :param self
    :param model: model
    :param object_filter: object filter
    """
    # clean object filter
    object_filter = clean_object_filter(model, object_filter)
    # get object by object filter
    test_object = get_object(model, object_filter)
    # test general existance of object
    self.generic_existance_test(model, test_object)
    # created object contains specific value in one of its fields?
    self.assertEqual(model.objects.filter(**object_filter).count(), 1)
    # created object includes an UUID field declared as its primary key?
    self.assertEqual(test_object.pk, test_object.uuid)

  def generic_update_test(self, model, object_filter):
    """
    tests update of test object of passed model

    :param self
    :param model: model
    :param object_filter: object filter
    """
    for key in object_filter:
      setattr(self.test_object, key, object_filter[key])
    self.test_object.save()
    # clean object filter
    object_filter = clean_object_filter(model, object_filter)
    # get object by object filter
    test_object = get_object(model, object_filter)
    # test general existance of object
    self.generic_existance_test(model, test_object)
    # updated object contains specific value in one of its fields?
    self.assertEqual(model.objects.filter(**object_filter).count(), 1)

  def generic_delete_test(self, model):
    """
    tests deletion of test object of passed model

    :param self
    :param model: model
    """
    # no more test objects left?
    self.test_object.delete()
    self.assertEqual(model.objects.all().count(), 0)

  def login_assign_permissions(self, model):
    """
    performs a login and sets all necessary rights on the passed model

    :param self
    :param model: model
    """
    # set all necessary rights on the passed model
    self.test_user.user_permissions.add(
      Permission.objects.get(codename='view_' + model._meta.model_name)
    )
    self.test_user.user_permissions.add(
      Permission.objects.get(codename='add_' + model._meta.model_name)
    )
    self.test_user.user_permissions.add(
      Permission.objects.get(codename='change_' + model._meta.model_name)
    )
    self.test_user.user_permissions.add(
      Permission.objects.get(codename='delete_' + model._meta.model_name)
    )
    # log test user in
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_view_test(self, model, view_name, url_params, status_code, content_type, string):
    """
    tests a view via GET

    :param self
    :param model: model
    :param view_name: name of the view
    :param url_params: URL parameters
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    """
    # perform login and set all necessary rights on the passed model
    self.login_assign_permissions(model)
    # GETting the view
    if view_name.endswith('_subset'):
      subset_id = url_params['subset_id']
      url_params.pop('subset_id')
      response = self.client.get(reverse(
        'datenmanagement:' + view_name,
        args=[subset_id]
      ), url_params)
    else:
      response = self.client.get(reverse('datenmanagement:' + view_name), url_params)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # specific string contained in response?
    if 'json' in response['content-type'].lower():
      self.assertIn(string, str(loads(response.content)))
    else:
      self.assertIn(string, str(response.content))

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @override_settings(MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage')
  def generic_add_update_view_test(self, update_mode, model, object_filter,
                                   status_code, content_type, object_count,
                                   file=None, file_attribute=None, file_content_type=None,
                                   multiple_files=False):
    """
    tests a view for creating or updating an object via POST

    :param self
    :param update_mode: update mode?
    :param model: model
    :param object_filter: object filter
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param object_count: expected number of objects passing the object filter
    :param file: file
    :param file_attribute: file attribute
    :param file_content_type: file content type
    :param multiple_files: handle multiple files?
    """
    # perform login and set all necessary rights on the passed model
    self.login_assign_permissions(model)
    # prepare the POST
    factory = RequestFactory()
    if update_mode:
      url = reverse(
        'datenmanagement:' + self.model.__name__ + '_change',
        args=[model.objects.last().pk]
      )
    else:
      url = reverse('datenmanagement:' + self.model.__name__ + '_add')
    data = object_filter
    # insert file attributes correctly in POST
    if file and file_attribute:
      # if multiple files are to be handled...
      if multiple_files:
        # ...the number of objects to be found at the end increases by two
        object_count += 2
        with open(file, 'rb') as f1, open(file, 'rb') as f2, open(file, 'rb') as f3:
          data[file_attribute] = [
            SimpleUploadedFile(file.name, f1.read(), file_content_type),
            SimpleUploadedFile(file.name, f2.read(), file_content_type),
            SimpleUploadedFile(file.name, f3.read(), file_content_type)
          ]
      else:
        with open(file, 'rb') as f:
          file_upload = SimpleUploadedFile(file.name, f.read(), file_content_type)
          data[file_attribute] = file_upload
    request = factory.post(
      url,
      data=data
    )
    request.user = self.test_user
    request._messages = storage.default_storage(request)
    template_name = 'datenmanagement/form.html'
    # try POSTing the view
    if update_mode:
      response = DataChangeView.as_view(
        model=model,
        template_name=template_name
      )(request, pk=model.objects.last().pk)
    else:
      response = DataAddView.as_view(
        model=model,
        template_name=template_name
      )(request)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # clean object filter
    object_filter = clean_object_filter(model, object_filter)
    # constellation of objects as expected?
    # in case of error...
    if object_count == 0:
      # faulty object not even created or updated?
      # Note: If the object filter is empty, all objects are found.
      # However, since the intention of an empty object filter is to assume
      # that nothing should be found, in this case the object set is set to 0.
      num_objects = model.objects.filter(**object_filter).count()
      if object_filter == {}:
        num_objects = 0
      self.assertEqual(num_objects, object_count)
    # if successful...
    else:
      if update_mode:
        # updated object contains specific value in one of its fields?
        self.assertEqual(model.objects.filter(**object_filter).count(), object_count)
      else:
        # created object contains specific value in one of its fields?
        # Note: Multiple objects can also be found here (hence assertGreaterEqual),
        # for example in models that only have mandatory attributes!
        self.assertGreaterEqual(model.objects.filter(**object_filter).count(), object_count)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @override_settings(MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage')
  def generic_delete_view_test(self, immediately, model, object_filter, status_code, content_type):
    """
    tests a view for deleteing an object via POST

    :param self
    :param immediately: delete immediately (without view)?
    :param model: model
    :param object_filter: object filter
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    """
    # perform login and set all necessary rights on the passed model
    self.login_assign_permissions(model)
    # clean object filter
    object_filter = clean_object_filter(model, object_filter)
    # prepare the GET/POST
    deletion_object = get_object(model, object_filter)
    if immediately:
      response = self.client.get(
        reverse(
          'datenmanagement:' + self.model.__name__ + '_deleteimmediately',
          args=[deletion_object.pk]
        )
      )
    else:
      factory = RequestFactory()
      request = factory.post(
        reverse(
          'datenmanagement:' + self.model.__name__ + '_delete',
          args=[deletion_object.pk]
        )
      )
      request.user = self.test_user
      request._messages = storage.default_storage(request)
      template_name = 'datenmanagement/delete.html'
      response = DataDeleteView.as_view(
        model=model,
        template_name=template_name
      )(request, pk=deletion_object.pk)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # no more test objects left?
    self.assertEqual(model.objects.filter(**object_filter).count(), 0)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_assign_view_test(self, model, target_object_filter, updated_object_filter,
                               field, value, status_code, content_type, object_count):
    """
    tests a view for assigning a specific value to a specific field of an object via GET

    :param self
    :param model: model
    :param target_object_filter: target object filter
    :param updated_object_filter: updated object filter
    :param field: specific field to which the specific value is to be assigned
    :param value: specific value to be assigned
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param object_count: expected number of objects passing the object filter
    """
    # perform login and set all necessary rights on the passed model
    self.login_assign_permissions(model)
    # clean object filters
    target_object_filter = clean_object_filter(model, target_object_filter)
    updated_object_filter = clean_object_filter(model, updated_object_filter)
    # prepare the GET
    target_object = get_object(model, target_object_filter)
    response = self.client.get(
      reverse(
        'datenmanagement:' + self.model.__name__ + '_assign', args=[target_object.pk]
      ) + '?field=' + field + '&value=' + value
    )
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # updated object contains specific value which was assigned to its specific field?
    self.assertEqual(model.objects.filter(**updated_object_filter).count(), object_count)


class DefaultMetaModelTestCase(DefaultModelTestCase):
  """
  abstract test class for meta models
  (i.e. non-editable data models)
  """

  def init(self):
    super().init()

  def generic_is_metamodel_test(self):
    """
    tests if model is meta model

    :param self
    """
    # model declared as meta model?
    self.assertTrue(issubclass(self.model, Metamodel))
    # model not editable?
    self.assertTrue(self.model.BasemodelMeta.editable is False)


class DefaultCodelistTestCase(DefaultModelTestCase):
  """
  abstract test class for codelists
  """

  def init(self):
    super().init()

  def generic_is_codelist_test(self):
    """
    tests if model is codelist

    :param self
    """
    # model declared as codelist?
    self.assertTrue(issubclass(self.model, Codelist))


class DefaultSimpleModelTestCase(DefaultModelTestCase):
  """
  abstract test class for simple data models
  """

  def init(self):
    super().init()

  def generic_is_simplemodel_test(self):
    """
    tests if model is simple data model

    :param self
    """
    # model declared as simple data model?
    self.assertTrue(issubclass(self.model, SimpleModel))


class DefaultComplexModelTestCase(DefaultModelTestCase):
  """
  abstract test class for complex data models
  """

  def init(self):
    super().init()

  def generic_is_complexmodel_test(self):
    """
    tests if model is complex data model

    :param self
    """
    # model declared as complex data model?
    self.assertTrue(issubclass(self.model, ComplexModel))


class GenericRSAGTestCase(DefaultComplexModelTestCase):
  """
  generic test class for complex RSAG data models
  """

  attributes_values_db_initial = {
    'quelle': 'Quelle1',
    'geometrie': VALID_LINE_DB
  }
  attributes_values_db_updated = {
    'quelle': 'Quelle2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'quelle': 'Quelle3',
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'quelle': 'Quelle4',
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_invalid = {
    'quelle': INVALID_STRING
  }

  def init(self):
    super().init()


class GISFiletoGeoJSONTestCase(DefaultTestCase):
  """
  abstract test class for passing a file to FME Server and returning the generated GeoJSON
  """

  @classmethod
  def setUpTestData(cls):
    load_sql_schema()

  def init(self):
    super().init()

  def generic_view_test(self, file, file_parameter, status_code, string):
    """
    tests a view via POST

    :param self
    :param file: file
    :param file_parameter: POST parameters with file
    :param status_code: expected status code of response
    :param string: specific string that should be contained in response
    """
    # log test user in
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # try POSTing the view
    with open(file, 'rb') as file_data:
      response = self.client.post(
        reverse('datenmanagement:gisfiletogeojson'),
        data={
          file_parameter: file_data
        }
      )
    # if test is executed without a valid FME Server token
    # (for example based on secrets.template)...
    if response.status_code == 401:
      pass
    # otherwise, i.e. with a valid FME Server token...
    else:
      # status code of response as expected?
      self.assertEqual(response.status_code, status_code)
      # content type of response as expected?
      self.assertEqual(response['content-type'].lower(), 'application/json')
      # specific string contained in response?
      self.assertIn(string, str(loads(response.content)))
