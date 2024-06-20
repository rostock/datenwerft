from antragsmanagement.test.constants_vars import USERNAME, PASSWORD


def login(test, antragsmanagement_requester=False, antragsmanagement_authority=False,
          antragsmanagement_admin=False):
  """
  logs test user in
  (and assigns Antragsmanagement requester, authority and/or admin permissions)

  :param test: current test case
  :param antragsmanagement_requester: assign Antragsmanagement requester permissions to user?
  :param antragsmanagement_authority: assign Antragsmanagement authority permissions to user?
  :param antragsmanagement_admin: assign Antragsmanagement admin permissions to user?
  """
  if antragsmanagement_requester:
    test.test_antragsmanagement_requester_group.user_set.add(test.test_user)
  if antragsmanagement_authority:
    test.test_antragsmanagement_authority_group.user_set.add(test.test_user)
  if antragsmanagement_admin:
    test.test_antragsmanagement_admin_group.user_set.add(test.test_user)
  test.client.login(
    username=USERNAME,
    password=PASSWORD
  )
