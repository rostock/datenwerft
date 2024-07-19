from django.conf import settings


REQUESTERS = getattr(
  settings,
  'ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME',
  'antragsmanagement_requester'
)
AUTHORITIES = getattr(
  settings,
  'ANTRAGSMANAGEMENT_AUTHORITY_GROUPS_NAMES', [
    'antragsmanagement_authority_67'
  ]
)
ADMINS = getattr(
  settings,
  'ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME',
  'antragsmanagement_admin'
)
SCOPE_WFS_SEARCH_ELEMENT = 'kreis_schluessel'
SCOPE_WFS_SEARCH_STRING = '13003'
MANAGEDAREAS_WFS_SEARCH_ELEMENT = 'bewirtschafter'
AUTHORITIES_KEYWORD_PUBLIC_GREEN_AREAS = 'Stadtgrün'
