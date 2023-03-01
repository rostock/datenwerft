from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.urls import reverse
from json import loads

from .constants_vars import *
from .functions import clean_object_filter, get_object


class DefaultTestCase(TestCase):
  """
  default abstract test class
  """

  databases = DATABASES

  def init(self):
    self.test_bemas_admin_group = Group.objects.create(name=settings.BEMAS_ADMIN_GROUP_NAME)
    self.test_bemas_user_group = Group.objects.create(name=settings.BEMAS_USERS_GROUP_NAME)
    self.test_user = User.objects.create_user(username=USERNAME, password=PASSWORD)


class DefaultModelTestCase(DefaultTestCase):
  """
  abstract test class for models
  """

  model = None
  count = 0
  create_test_object_in_classmethod = True
  attributes_values_db_initial = {}
  test_object = None

  @classmethod
  def setUpTestData(cls):
    if cls.create_test_object_in_classmethod:
      cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)

  def init(self):
    super().init()

  def generic_existance_test(self, model, test_object):
    """
    tests general existance of given test object of given model

    :param self
    :param model: model
    :param test_object: test object of given model
    """
    # actual number of objects equals expected number of objects?
    self.assertEqual(model.objects.all().count(), self.count + 1)
    # on creation: object created exactly as it should have been created?
    # on update: object updated exactly as it should have been updated?
    self.assertEqual(test_object, self.test_object)

  def generic_create_test(self, model, object_filter):
    """
    tests creation of test object of given model

    :param self
    :param model: model
    :param object_filter: object filter
    """
    # clean object filter
    object_filter = clean_object_filter(object_filter)
    # get object by object filter
    test_object = get_object(model, object_filter)
    # test general existance of object
    self.generic_existance_test(model, test_object)
    # created object contains specific value in one of its fields?
    self.assertEqual(model.objects.filter(**object_filter).count(), 1)

  def generic_update_test(self, model, object_filter):
    """
    tests update of test object of given model

    :param self
    :param model: model
    :param object_filter: object filter
    """
    for key in object_filter:
      setattr(self.test_object, key, object_filter[key])
    self.test_object.save()
    # clean object filter
    object_filter = clean_object_filter(object_filter)
    # get object by object filter
    test_object = get_object(model, object_filter)
    # test general existance of object
    self.generic_existance_test(model, test_object)
    # created object contains specific value in one of its fields?
    self.assertEqual(model.objects.filter(**object_filter).count(), 1)

  def generic_delete_test(self, model):
    """
    tests deletion of test object of given model

    :param self
    :param model: model
    """
    # no more test objects left?
    self.test_object.delete()
    self.assertEqual(model.objects.all().count(), self.count)


class DefaultCodelistTestCase(DefaultModelTestCase):
  """
  abstract test class for codelists
  """

  def init(self):
    super().init()

  def generic_is_codelist_test(self, model):
    """
    tests if model is codelist

    :param self
    :param model: model
    """
    # model declared as codelist?
    self.assertTrue(
      hasattr(model._meta, 'codelist')
      and model._meta.codelist is True
    )


class DefaultViewTestCase(DefaultTestCase):
  """
  abstract test class for views
  """

  def init(self):
    super().init()

  def login(self, bemas_user=False, bemas_admin=False):
    """
    logs test user in
    (and assigns standard and/or admin rights)

    :param self
    :param bemas_user: assign standard rights to user?
    :param bemas_admin: assign admin rights to user?
    """
    if bemas_user:
      self.test_bemas_user_group.user_set.add(self.test_user)
    if bemas_admin:
      self.test_bemas_admin_group.user_set.add(self.test_user)
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_view_test(self, bemas_user, bemas_admin, view_name,
                        status_code, content_type, string):
    """
    tests a view via GET

    :param self
    :param bemas_user: assign standard rights to user?
    :param bemas_admin: assign admin rights to user?
    :param view_name: name of the view
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    :param string: specific string that should be contained in response
    """
    # log test user in
    self.login(bemas_user, bemas_admin)
    # try GETting the view
    response = self.client.get(reverse('bemas:' + view_name))
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
    # specific string contained in response?
    if 'json' in response['content-type'].lower():
      self.assertIn(string, str(loads(response.content)))
    else:
      self.assertIn(string, str(response.content))
