from bemas.models import GeometryObjectclass
from .constants_vars import USERNAME, PASSWORD


def clean_object_filter(object_filter, model=None):
  """
  cleans passed object filter and returns it

  :param object_filter: object filter
  :param model: model
  :return: cleaned version of passed object filter
  """
  cleaned_object_filter = object_filter.copy()
  # remove geometry field from object filter
  if model and issubclass(model, GeometryObjectclass):
    cleaned_object_filter.pop(model.BasemodelMeta.geometry_field, None)
  return cleaned_object_filter


def get_object(model, object_filter):
  """
  fetches object of passed model from the database according to passed object filter and returns it

  :param model: model
  :param object_filter: object filter
  :return: object of passed model from the database according to passed object filter
  """
  return model.objects.get(**object_filter)


def login(test, bemas_user=False, bemas_admin=False):
  """
  logs test user in
  (and assigns standard and/or admin rights)

  :param test: current test case
  :param bemas_user: assign standard rights to user?
  :param bemas_admin: assign admin rights to user?
  """
  if bemas_user:
    test.test_bemas_user_group.user_set.add(test.test_user)
  if bemas_admin:
    test.test_bemas_admin_group.user_set.add(test.test_user)
  test.client.login(
    username=USERNAME,
    password=PASSWORD
  )
