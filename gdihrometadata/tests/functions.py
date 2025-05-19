from django.contrib.auth.models import Group
from django.db.models import (
  BigIntegerField,
  BooleanField,
  CharField,
  DateField,
  FloatField,
  IntegerField,
  TextField,
)

from .constants_vars import PASSWORD, USERNAME


def clean_object_filter(object_filter, model=None):
  """
  cleans dictionary to make it usable as object filter

  :param object_filter: dictionary to be cleaned into object filter
  :param model: model of object (default: None)
  :return: cleaned object filter
  """
  # initialize empty dictionary
  dictionary = {}
  # copy keys and values from object filter into dictionary, if values present
  for key in object_filter:
    value = object_filter[key]
    if value:
      dictionary[key] = value
  # no model specified? -> object filter should equal dictionary at this point
  if not model:
    return dictionary
  # model specified? -> check if value should be checked against "icontains"
  for field_name in list(dictionary.keys()):
    # check whether field exists for specified model
    try:
      field = model._meta.get_field(field_name)
    except Exception:  # pragma: no cover
      # this is needed to prevent failing tests when admin panel sends extra fields
      continue
    # check type of model field to determine whether value should be checked against "icontains"
    if type(field) not in [BigIntegerField, BooleanField, DateField, FloatField, IntegerField]:
      if type(field) in [CharField, TextField] and field_name + '__icontains' not in dictionary:
        # add key and value for "icontains" to dictionary
        dictionary[field_name + '__icontains'] = dictionary[field_name]
        # remove original key and value from dictionary
        del dictionary[field_name]
  # return cleaned object filter
  return dictionary


def get_object(model, object_filter):
  """
  filters out a query through a passed filter and returns first object from query

  :param model: model of the object to be found
  :param object_filter: object filter
  :return: first object from query
  """
  query = model.objects.filter(**object_filter)
  return query.first()


def login(testcase, gdihro_user=False, gdihro_admin=False):
  """
  logs a test user in for the testcase object

  :param testcase: testcase object
  :param gdihro_user: assign standard rights to user?
  :param gdihro_admin: assign admin rights to user?
  """
  # clear all group memberships
  testcase.test_user.groups.clear()
  # assign standard rights to test user?
  if gdihro_user:
    # assign standard rights to test user
    group = Group.objects.get(name=testcase.test_gdihro_user_group.name)
    group.user_set.add(testcase.test_user)
  # assign admin rights to test user?
  if gdihro_admin:
    # assign admin rights to test user
    group = Group.objects.get(name=testcase.test_gdihro_admin_group.name)
    group.user_set.add(testcase.test_user)
  # log test user in
  testcase.client.login(username=USERNAME, password=PASSWORD)
