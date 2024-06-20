from django.conf import settings

from .models import Requester


def belongs_to_antragsmanagement_authority(user):
  """
  checks if passed user belongs to an Antragsmanagement authority

  :param user: user
  :return: passed user belongs to an Antragsmanagement authority?
  """
  return user.groups.filter(
    name__in=settings.ANTRAGSMANAGEMENT_AUTHORITY_GROUPS_NAMES
  ).exists()


def get_corresponding_requester(user, only_primary_key=True):
  """
  returns (primary key of) corresponding requester object for passed user

  :param user: user
  :param only_primary_key: return only primary key?
  :return: (primary key of) corresponding requester object for passed user
  """
  try:
    requester = Requester.objects.get(user_id=user.pk)
    return requester.pk if only_primary_key else Requester.objects.filter(user_id=user.pk)
  except Requester.DoesNotExist:
    return None


def get_icon_from_settings(key):
  """
  returns icon (i.e. value) of passed key in icon dictionary

  :param key: key in icon dictionary
  :return: icon (i.e. value) of passed key in icon dictionary
  """
  return settings.ANTRAGSMANAGEMENT_ICONS.get(key, 'poo')


def get_request(model, request_id, only_primary_key=True):
  """
  returns (primary key of) request object of passed model with passed ID

  :param model: model
  :param request_id: ID of request object
  :param only_primary_key: return only primary key?
  :return: (primary key of) request object of passed model with passed ID
  """
  try:
    request = model.objects.get(id=request_id)
    return request.pk if only_primary_key else model.objects.filter(id=request_id)
  except model.DoesNotExist:
    return None


def has_necessary_permissions(user, necessary_group):
  """
  checks if passed user belongs to passed group and thus has necessary permissions

  :param user: user
  :param necessary_group: group that passed user must belong to for necessary permissions
  :return: passed user belongs to passed group and thus has necessary permissions?
  """
  if isinstance(necessary_group, list):
    return user.groups.filter(name__in=necessary_group).exists()
  else:
    return user.groups.filter(name=necessary_group).exists()


def is_antragsmanagement_admin(user):
  """
  checks if passed user is an Antragsmanagement admin

  :param user: user
  :return: passed user is an Antragsmanagement admin?
  """
  return user.groups.filter(name=settings.ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME).exists()


def is_antragsmanagement_requester(user):
  """
  checks if passed user is an Antragsmanagement requester

  :param user: user
  :return: passed user is an Antragsmanagement requester?
  """
  return user.groups.filter(name=settings.ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME).exists()


def is_antragsmanagement_user(user, only_antragsmanagement_user_check=False):
  """
  checks if passed user is an Antragsmanagement user
  (and optionally checks if it is an Antragsmanagement user only)

  :param user: user
  :param only_antragsmanagement_user_check: check if user is an Antragsmanagement user only?
  :return: passed user is an Antragsmanagement user (only)?
  """
  group_names = list(settings.ANTRAGSMANAGEMENT_AUTHORITY_GROUPS_NAMES)
  group_names.extend([
    settings.ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME, settings.ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME
  ])
  if user.groups.filter(name__in=group_names).exists():
    if only_antragsmanagement_user_check:
      # if user is an Antragsmanagement user only, he is not a member of any other group
      return user.groups.filter(name__in=group_names).count() == user.groups.all().count()
    else:
      return True
  else:
    return False
