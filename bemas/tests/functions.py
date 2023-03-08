from .constants_vars import USERNAME, PASSWORD


def clean_object_filter(object_filter):
  """
  cleans given object filter and returns it

  :param object_filter: object filter
  :return: cleaned version of given object filter
  """
  cleaned_object_filter = object_filter.copy()
  # remove GIS attribute(s) from object filter
  cleaned_object_filter.pop('location', None)
  return cleaned_object_filter


def get_object(model, object_filter):
  """
  fetches object of given model from the database according to given object filter and returns it

  :param model: model
  :param object_filter: object filter
  :return: object of given model from the database according to given object filter
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
