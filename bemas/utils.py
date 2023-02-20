from django.conf import settings


def is_bemas_user(user, only_bemas_user_check=False):
  """
  checks if given user is a BEMAS user
  (and optionally checks if it is a BEMAS user only)

  :param user: user
  :param only_bemas_user_check: check if user is a BEMAS user only?
  :return: given user is a BEMAS user (only)?
  """
  in_bemas_groups = user.groups.filter(
    name__in=[settings.BEMAS_ADMIN_GROUP_NAME, settings.BEMAS_USERS_GROUP_NAME]
  )
  if in_bemas_groups:
    if only_bemas_user_check:
      # if user is a BEMAS user only, he is not a member of any other group
      return in_bemas_groups.count() == user.groups.all().count()
    else:
      return True
  else:
    return False
