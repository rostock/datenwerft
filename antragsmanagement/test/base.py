from django.contrib.auth.models import User
from django.test import TestCase

from antragsmanagement.models import Codelist
from bemas.tests.functions import clean_object_filter, get_object
from .constants_vars import DATABASES, USERNAME, PASSWORD


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
    self.assertEqual(self.model.objects.all().count(), self.count + 1)
    # on creation: object created exactly as it should have been created?
    # on update: object updated exactly as it should have been updated?
    self.assertEqual(test_object, self.test_object)

  def generic_create_test(self):
    """
    tests creation of test object of passed model

    :param self
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

    :param self
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

    :param self
    """
    # no more test objects left?
    self.test_object.delete()
    self.assertEqual(self.model.objects.all().count(), self.count)


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
