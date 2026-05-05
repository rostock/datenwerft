from .constants_vars import PASSWORD, USERNAME


def login(test, assign_permissions=False):
  """
  logs test user in (and optionally assigns permissions to test user)

  :param test: current test case
  :param assign_permissions: assigns permissions to test user?
  """
  if assign_permissions:
    test.test_group.user_set.add(test.test_user)
  test.client.login(username=USERNAME, password=PASSWORD)
