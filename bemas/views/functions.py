from django.conf import settings


def is_bemas_user(user):
  """
  checks if a user is a BEMAS user (or an admin)

  :param user: user
  :return: user is a BEMAS user (or an admin)?
  """
  if (
      user.groups.filter(
        name__in=[settings.BEMAS_ADMIN_GROUP_NAME, settings.BEMAS_USERS_GROUP_NAME]
      )
      or user.is_superuser
  ):
    return True
  else:
    return False
