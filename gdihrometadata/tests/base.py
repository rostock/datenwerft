from json import loads

from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse

from gdihrometadata.models import Codelist

from .constants_vars import DATABASES, PASSWORD, TABLEDATA_VIEW_PARAMS, USERNAME
from .functions import clean_object_filter, get_object, login


class DefaultTestCase(TestCase):
  """
  default abstract test class
  """

  databases = DATABASES

  def init(self):
    self.test_gdihro_admin_group: Group = Group.objects.create(name='gdihrometadata-admin')
    self.test_gdihro_user_group: Group = Group.objects.create(name='gdihrometadata-users')
    self.test_user: User = User.objects.create_user(username=USERNAME, password=PASSWORD)


class DefaultModelTestCase(DefaultTestCase):
  """
  abstract test class for models
  """

  model = None
  count = 0
  create_test_object_in_classmethod = True
  attributes_values_db_initial, attributes_values_db_updated = {}, {}
  test_object = None

  @classmethod
  def setUpTestData(cls):
    if cls.create_test_object_in_classmethod:
      cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def init(self):
    super().init()

  def generic_existance_test(self, test_object):
    """
    Docstring for generic_existance_test

    :param test_object: test object
    """
    # actual number of objects equals expected number of objects?
    self.assertEqual(self.model.objects.all().count(), self.count + 1)
    # on creation: object created exactly as it should have been created?
    # on update: object updated exactly as it should have been updated?
    self.assertEqual(test_object, self.test_object)

  def generic_create_test(self):
    """
    tests creation of test object of passed model
    """
    # clean object filter
    object_filter = clean_object_filter(self.attributes_values_db_initial)
    # get object by object filter
    test_object = get_object(self.model, object_filter)
    # test general existance of object
    self.generic_existance_test(test_object)
    # created object contains specific value in one of its fields?
    self.assertEqual(self.model.objects.filter(**object_filter).count(), 1)

  def generic_update_test(self):
    """
    tests update of test object of passed model
    """
    for key in self.attributes_values_db_updated:
      setattr(self.test_object, key, self.attributes_values_db_updated[key])
    self.test_object.save()
    # clean object filter
    object_filter = clean_object_filter(self.attributes_values_db_updated)
    # get object by object filter
    test_object = get_object(self.model, object_filter)
    # test general existance of object
    self.generic_existance_test(test_object)
    # updated object contains specific value in one of its fields?
    self.assertEqual(self.model.objects.filter(**object_filter).count(), 1)

  def generic_delete_test(self):
    """
    tests deletion of test object of passed model
    """
    # no more test objects left?
    self.test_object.delete()
    self.assertEqual(self.model.objects.all().count(), self.count)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @override_settings(MESSAGE_STORAGE='django.contrib.messages.storage.cookie.CookieStorage')
  def generic_crud_view_test(
    self,
    update_mode,
    gdihro_user,
    gdihro_admin,
    view_name,
    object_filter,
    status_code,
    content_type,
    string,
    count,
    log_entry_action=None,
  ):
    """
    tests a view for creating or updating an object via POST

    :param update_mode: update mode?
    :param metadata_user: assign standard rights to user?
    :param metadata_admin: assign admin rights to user?
    :param view_name: name of the view
    :param object_filter: object filter
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    :param count: expected number of objects passing the object filter
    :param log_entry_action: log entry action (i.e. test log entry if present)
    """
    # log test user in
    login(self, gdihro_user, gdihro_admin)
    # for update mode: get primary key of last object
    last_pk = self.model.objects.last().pk
    # prepare the POST
    if update_mode:
      url = reverse('gdihrometadata:' + view_name, args=[last_pk])
    else:
      url = reverse('gdihrometadata:' + view_name)
    data = object_filter
    # try POSTing the view
    response = self.client.post(url, data)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # clean object filter
    object_filter = clean_object_filter(object_filter, self.model)
    # number of objects passing the object filter as expected?
    if update_mode:
      self.assertEqual(self.model.objects.filter(pk=last_pk).count(), count)
    else:
      self.assertEqual(self.model.objects.filter(**object_filter).count(), count)
    # specific string contained in response?
    if string:
      self.assertIn(string, str(response.content))
    # log entry created as expected?
    if log_entry_action:
      self.assertEqual(
        LogEntry.objects.filter(model=self.model.__name__, action=log_entry_action).count(), 1
      )


class DefaultCodelistTestCase(DefaultModelTestCase):
  """
  abstract test class for codelists
  """

  def init(self):
    super().init()

  def generic_is_codelist_test(self):
    """
    tests if model is codelist
    """
    # model declared as codelist?
    self.assertTrue(issubclass(self.model, Codelist))


class DefaultManyToManyTestCase(DefaultTestCase):
  """
  abstract test class for many-to-many-relationships

  :attr model_from: model from
  :attr model_to: model to
  :attr model_from_attributes_values_db: initial values for test object from
  :attr model_to_attributes_values_db: initial values for test object to
  :attr test_object_from: test object from
  :attr test_object_to: test object to
  :attr relationship: many-to-many-relationship itself
  :attr count: number of objects in model
  """

  model_from = None
  model_to = None
  model_from_attributes_values_db, model_to_attributes_values_db = {}, {}
  test_object_from = None
  test_object_to = None
  relationship = None
  count = 0

  def init(self):
    super().init()

  def generic_existance_test(self, test_object_from, test_object_to, relationship):
    """
    tests general existance of many-to-many-relationship of passed test objects

    :param test_object_from: test object (from)
    :param test_object_to: test object (to)
    :param relationship: many-to-many-relationship itself
    """
    # actual number of many-to-many-relationships
    # equals expected number of many-to-many-relationships?
    self.assertEqual(relationship.all().count(), self.count + 1)
    # objects created exactly as they should have been created?
    self.assertEqual(test_object_from, self.test_object_from)
    self.assertEqual(test_object_to, self.test_object_to)

  def generic_create_test(self):
    """
    tests creation of many-to-many-relationship of test objects of passed models
    """
    # clean object filters
    object_filter_from = clean_object_filter(self.model_from_attributes_values_db)
    object_filter_to = clean_object_filter(self.model_to_attributes_values_db)
    # get objects by object filters
    test_object_from = get_object(self.model_from, object_filter_from)
    test_object_to = get_object(self.model_to, object_filter_to)
    # test general existance of many-to-many-relationship of objects
    self.generic_existance_test(test_object_from, test_object_to, self.relationship)
    # created objects contain specific values in one of their respective fields?
    self.assertEqual(self.model_from.objects.filter(**object_filter_from).count(), 1)
    self.assertEqual(self.model_to.objects.filter(**object_filter_to).count(), 1)

  def generic_delete_test(self):
    """
    tests deletion of many-to-many-relationship of test objects of passed models
    """
    # no more many-to-many-relationship left?
    self.test_object_to.delete()
    self.assertEqual(self.relationship.all().count(), self.count)


class DefaultViewTestCase(DefaultTestCase):
  """
  abstract test class for views
  """

  def init(self):
    super().init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_view_test(
    self, gdihro_user, gdihro_admin, view_name, view_args, status_code, content_type, string
  ):
    """
    tests a view via GET

    :param metadata_user: assign standard rights to user?
    :param metadata_admin: assign admin rights to user?
    :param view_name: name of the view
    :param view_args: arguments passed to the view
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    """
    # log test user in
    login(self, gdihro_user, gdihro_admin)
    # prepare the GET
    if view_args and type(view_args) is list:
      url = reverse('gdihrometadata:' + view_name, args=view_args)
    else:
      url = reverse('gdihrometadata:' + view_name)
    # try GETting the view
    if view_args and type(view_args) is dict:
      response = self.client.get(url, view_args)
    elif '_tabledata_subset' in view_name:
      response = self.client.get(url, TABLEDATA_VIEW_PARAMS)
    else:
      response = self.client.get(url)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # specific string contained in response?
    if 'json' in response['content-type'].lower():
      self.assertIn(string, str(loads(response.content)))
    else:
      self.assertIn(string, str(response.content))
