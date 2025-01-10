from .constants_vars import USERNAME, PASSWORD, VALID_FIRST_NAME, VALID_LAST_NAME, VALID_EMAIL, \
  VALID_STRING
from antragsmanagement.models import CodelistRequestStatus, Authority, Requester, \
  CleanupEventRequest


def create_cleanupevent_request(two=False):
  """
  create (two) clean-up event request object(s)

  :param two: create two clean-up event request objects?
  :return: (two) clean-up event request object(s)
  """
  status1 = CodelistRequestStatus.get_status_processed()
  requester = Requester.objects.create(
    first_name=VALID_FIRST_NAME,
    last_name=VALID_LAST_NAME,
    email=VALID_EMAIL
  )
  responsibility = Authority.objects.create(
    group=VALID_STRING,
    name=VALID_STRING,
    email=VALID_EMAIL
  )
  cleanupevent_request1 = CleanupEventRequest.objects.create(
    status=status1,
    requester=requester
  )
  cleanupevent_request1.responsibilities.add(responsibility, through_defaults={'main': False})
  if two:
    status2 = CodelistRequestStatus.get_status_new()
    cleanupevent_request2 = CleanupEventRequest.objects.create(
      status=status2,
      requester=requester
    )
    cleanupevent_request2.responsibilities.add(responsibility, through_defaults={'main': False})
    return cleanupevent_request1, cleanupevent_request2
  return cleanupevent_request1


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
