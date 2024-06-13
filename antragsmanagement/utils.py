from django.conf import settings


def belongs_to_antragsmanagement_authority(user):
  """
  checks if passed user belongs to an Antragsmanagement authority

  :param user: user
  :return: passed user belongs to an Antragsmanagement authority?
  """
  return user.groups.filter(
    name__in=settings.ANTRAGSMANAGEMENT_AUTHORITY_GROUPS_NAMES
  )


def is_antragsmanagement_admin(user):
  """
  checks if passed user is an Antragsmanagement admin

  :param user: user
  :return: passed user is an Antragsmanagement admin?
  """
  return user.groups.filter(name=settings.ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME)


def is_antragsmanagement_requester(user):
  """
  checks if passed user is an Antragsmanagement requester

  :param user: user
  :return: passed user is an Antragsmanagement requester?
  """
  return user.groups.filter(name=settings.ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME)


def is_antragsmanagement_user(user, only_antragsmanagement_user_check=False):
  """
  checks if passed user is an Antragsmanagement user
  (and optionally checks if it is an Antragsmanagement user only)

  :param user: user
  :param only_antragsmanagement_user_check: check if user is an Antragsmanagement user only?
  :return: passed user is an Antragsmanagement user (only)?
  """
  groups = settings.ANTRAGSMANAGEMENT_AUTHORITY_GROUPS_NAMES
  groups.extend([
    settings.ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME, settings.ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME
  ])
  in_antragsmanagement_groups = user.groups.filter(name__in=groups)
  if in_antragsmanagement_groups:
    if only_antragsmanagement_user_check:
      # if user is an Antragsmanagement user only, he is not a member of any other group
      return in_antragsmanagement_groups.count() == user.groups.all().count()
    else:
      return True
  else:
    return False
