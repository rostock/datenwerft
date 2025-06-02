from .constants_vars import PASSWORD, USERNAME


def get_object(model, object_filter):
  """
  filters out a query through a passed filter and returns first object from query

  :param model: model of the object to be found
  :param object_filter: object filter
  :return: first object from query
  """
  query = model.objects.filter(**object_filter)
  return query.first()


def login(test, assign_permissions=False):
  """
  logs test user in (and optionally assigns permissions to test user)

  :param test: current test case
  :param assign_permissions: assigns permissions to test user?
  """
  if assign_permissions:
    test.test_group.user_set.add(test.test_user)
  test.client.login(username=USERNAME, password=PASSWORD)
