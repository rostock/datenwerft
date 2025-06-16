from django.conf import settings

from .constants_vars import GROUP


def get_icon_from_settings(key):
  """
  returns icon (i.e. value) of passed key in icon dictionary

  :param key: key in icon dictionary
  :return: icon (i.e. value) of passed key in icon dictionary
  """
  return getattr(settings, 'FMM_ICONS', {}).get(key, 'poo')


def is_fmm_user(user, only_fmm_user_check=False):
  """
  checks if passed user is a FMM user
  (and optionally checks if it is a FMM user only)

  :param user: user
  :param only_fmm_user_check: check if user is a FMM user only?
  :return: passed user is a FMM user (only)?
  """
  if user.groups.filter(name=GROUP).exists():
    if only_fmm_user_check:
      # if user is a FMM user only, he is not a member of any other group
      return user.groups.filter(name=GROUP).count() == user.groups.all().count()
    else:
      return True
  else:
    return False
