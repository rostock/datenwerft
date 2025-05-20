from django.contrib.auth.models import Group, Permission, User
from django.test import TestCase, override_settings
from django.urls import reverse

from gdihrometadata.constants_vars import GROUP
from gdihrometadata.models import Codelist

from .constants_vars import DATABASES, PASSWORD, USERNAME


def get_object(model, object_filter):
  """
  filters out a query through a passed filter and returns first object from query

  :param model: model of the object to be found
  :param object_filter: object filter
  :return: first object from query
  """
  query = model.objects.filter(**object_filter)
  return query.first()


def login(test):
  """
  logs test user in

  :param test: current test case
  """
  test.client.login(username=USERNAME, password=PASSWORD)


class DefaultTestCase(TestCase):
  """
  abstract test class
  """

  databases = DATABASES

  def init(self):
    self.test_group: Group = Group.objects.create(name=GROUP)
    # assign permissions to test group
    permissions = Permission.objects.filter(content_type__app_label='gdihrometadata')
    for permission in permissions:
      self.test_group.permissions.add(permission)
    self.test_user: User = User.objects.create_user(username=USERNAME, password=PASSWORD)
    # add test user to test group
    self.test_user.is_staff = True
    self.test_user.groups.add(self.test_group)


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
    tests general existance of passed test object

    :param self
    :param test_object: test object
    """
    # actual number of objects equals expected number of objects?
    self.assertEqual(self.model.objects.only('pk').all().count(), self.count + 1)
    # on creation: object created exactly as it should have been created?
    # on update: object updated exactly as it should have been updated?
    self.assertEqual(test_object, self.test_object)

  def generic_create_test(self):
    """
    tests creation of test object of passed model

    :param self
    """
    # set object filter
    object_filter = self.attributes_values_db_initial
    # get object by object filter
    test_object = get_object(self.model, object_filter)
    # test general existance of object
    self.generic_existance_test(test_object)
    # created object contains specific value in one of its fields?
    self.assertEqual(self.model.objects.only('pk').filter(**object_filter).count(), 1)

  def generic_update_test(self):
    """
    tests update of test object of passed model

    :param self
    """
    for key in self.attributes_values_db_updated:
      setattr(self.test_object, key, self.attributes_values_db_updated[key])
    self.test_object.save()
    # set object filter
    object_filter = self.attributes_values_db_updated
    # get object by object filter
    test_object = get_object(self.model, object_filter)
    # test general existance of object
    self.generic_existance_test(test_object)
    # updated object contains specific value in one of its fields?
    self.assertEqual(self.model.objects.only('pk').filter(**object_filter).count(), 1)

  def generic_delete_test(self):
    """
    tests deletion of test object of passed model

    :param self
    """
    # no more test objects left?
    self.test_object.delete()
    self.assertEqual(self.model.objects.only('pk').all().count(), self.count)

  def generic_string_representation_test(self, string_representation):
    """
    tests string representation of test object of passed model

    :param self
    :param string_representation: expected string representation
    """
    self.assertEqual(str(self.test_object), string_representation)


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


class DefaultViewTestCase(DefaultTestCase):
  """
  abstract test class for views
  """

  def init(self):
    super().init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def generic_view_test(self, view_name, status_code, content_type):
    """
    tests a view via GET

    :param self
    :param view_name: name of the view
    :param status_code: expected status code of response
    :param content_type: expected content type of response
    """
    # log test user in
    login(self)
    # prepare the GET
    url = reverse(f'admin:gdihrometadata_{view_name}')
    # try GETting the view
    response = self.client.get(url, follow=True)
    # status code of response as expected?
    self.assertEqual(response.status_code, status_code)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), content_type)
