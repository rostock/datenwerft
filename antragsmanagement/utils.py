from django.conf import settings

from .constants_vars import REQUESTERS, AUTHORITIES, ADMINS
from .models import Authority, Requester


def belongs_to_antragsmanagement_authority(user):
  """
  checks if passed user belongs to an Antragsmanagement authority

  :param user: user
  :return: passed user belongs to an Antragsmanagement authority?
  """
  return user.groups.filter(name__in=AUTHORITIES).exists()


def check_necessary_permissions(user, permissions_level):
  """
  checks if passed user has necessary permissions

  :param user: user
  :param permissions_level: permissions level passed user has to have
  (if empty, check if  passed user is an Antragsmanagement user at least)
  :return: passed user has necessary permissions?
  """
  necessary_permissions = user.is_superuser
  if not necessary_permissions:
    if permissions_level:
      permissions_map = {
        'REQUESTERS': REQUESTERS,
        'AUTHORITIES': AUTHORITIES,
        'ADMINS': ADMINS
      }
      check_group = permissions_map.get(permissions_level)
      if check_group:
        necessary_permissions = has_necessary_permissions(user, check_group)
    else:
      necessary_permissions = is_antragsmanagement_user(user)
  return necessary_permissions


def get_antragsmanagement_authorities(user, only_primary_keys=True):
  """
  returns (primary keys of) all Antragsmanagement authorities the passed user belongs to

  :param user: user
  :param only_primary_keys: return only primary keys?
  :return: (primary keys of) all Antragsmanagement authorities the passed user belongs to
  """
  # get all groups the passed user belongs to
  user_groups = user.groups.values_list('name', flat=True)
  # filter authorities based on the user's groups
  authorities = Authority.objects.filter(group__in=list(user_groups))
  # return primary keys or full objects based on the parameter
  if only_primary_keys:
    return list(authorities.values_list('pk', flat=True))
  else:
    return list(authorities)


def get_authorities_from_managed_areas_wfs(search_element, wfs_features):
  """
  returns all authorities found in passed search element of passed WFS features

  :param search_element: WFS feature search element
  :param wfs_features: WFS features
  :return: all authorities found in passed search element of passed WFS features
  """
  authorities = []
  for wfs_feature in wfs_features:
    properties = wfs_feature.get('properties', {})
    authority = properties.get(search_element)
    if authority:
      authorities.append(authority)
  return sorted(set(authorities))


def get_corresponding_antragsmanagement_authorities(authority_names):
  """
  returns corresponding Antragsmanagement authorities to passed list of authority names

  :param authority_names: list of authority names
  :return: corresponding Antragsmanagement authorities to passed list of authority names
  """
  return Authority.objects.filter(name__in=authority_names)


def get_corresponding_requester(user, request=None, only_primary_key=True):
  """
  returns (primary key of) corresponding requester object for passed user or passed request

  :param user: user
  :param request: request
  :param only_primary_key: return only primary key?
  :return: (primary key of) corresponding requester object for passed user or passed request
  """
  if user and user.pk is not None:
    if only_primary_key:
      try:
        requester = Requester.objects.only('pk').get(user_id=user.pk)
        return requester.pk
      except Requester.DoesNotExist:
        return None
    else:
      queryset = Requester.objects.filter(user_id=user.pk)
      return queryset if queryset.exists() else None
  elif request:
    requester_pk = request.session.get('corresponding_requester', None)
    if requester_pk:
      if only_primary_key:
        try:
          requester = Requester.objects.only('pk').get(pk=requester_pk)
          return requester.pk
        except Requester.DoesNotExist:
          return None
      else:
        queryset = Requester.objects.filter(pk=requester_pk)
        return queryset if queryset.exists() else None
  return None


def get_icon_from_settings(key):
  """
  returns icon (i.e. value) of passed key in icon dictionary

  :param key: key in icon dictionary
  :return: icon (i.e. value) of passed key in icon dictionary
  """
  return getattr(settings, 'ANTRAGSMANAGEMENT_ICONS', {}).get(key, 'poo')


def get_request(model, request_id, only_primary_key=True):
  """
  returns (primary key of) request object of passed model with passed ID

  :param model: model
  :param request_id: ID of request object
  :param only_primary_key: return only primary key?
  :return: (primary key of) request object of passed model with passed ID
  """
  if only_primary_key:
    try:
      request = model.objects.only('pk').get(pk=request_id)
      return request.pk
    except model.DoesNotExist:
      return None
  else:
    queryset = model.objects.filter(pk=request_id)
    return queryset if queryset.exists() else None


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
  return user.groups.filter(name=ADMINS).exists()


def is_antragsmanagement_requester(user):
  """
  checks if passed user is an Antragsmanagement requester

  :param user: user
  :return: passed user is an Antragsmanagement requester?
  """
  return user.groups.filter(name=REQUESTERS).exists()


def is_antragsmanagement_user(user, only_antragsmanagement_user_check=False):
  """
  checks if passed user is an Antragsmanagement user
  (and optionally checks if it is an Antragsmanagement user only)

  :param user: user
  :param only_antragsmanagement_user_check: check if user is an Antragsmanagement user only?
  :return: passed user is an Antragsmanagement user (only)?
  """
  group_names = list(AUTHORITIES)
  group_names.extend([ADMINS, REQUESTERS])
  if user.groups.filter(name__in=group_names).exists():
    if only_antragsmanagement_user_check:
      # if user is an Antragsmanagement user only, he is not a member of any other group
      return user.groups.filter(name__in=group_names).count() == user.groups.all().count()
    else:
      return True
  else:
    return False
