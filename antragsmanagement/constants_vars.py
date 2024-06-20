from django.conf import settings


REQUESTERS = getattr(
  settings,
  'ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME',
  'antragsmanagement_requester'
)
AUTHORITIES = getattr(
  settings,
  'ANTRAGSMANAGEMENT_AUTHORITY_GROUPS_NAMES', [
    'antragsmanagement_authority_66',
    'antragsmanagement_authority_67',
    'antragsmanagement_authority_77'
  ]
)
ADMINS = getattr(
  settings,
  'ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME',
  'antragsmanagement_admin'
)
