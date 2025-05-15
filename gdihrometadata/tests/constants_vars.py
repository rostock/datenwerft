DATABASES = {'default', 'gdihrometadata'}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'

INVALID_STRING = 'Worsch´d  supp'

# Parameters for table data view
TABLEDATA_VIEW_PARAMS = {
  'draw': 1,
  'start': 0,
  'length': 10,
  'search[value]': '',
  'search[regex]': 'false',
  'order[0][column]': 0,
  'order[0][dir]': 'asc',
}

# Action constants
ACTION_CREATE = 'create'
ACTION_UPDATE = 'update'
ACTION_DELETE = 'delete'

# Content type constants
CONTENT_TYPE_HTML = 'text/html'
CONTENT_TYPE_JSON = 'application/json'

# Status constants
STATUS_OK = 200
STATUS_REDIRECT = 302
STATUS_FORBIDDEN = 403

# Message constants
MSG_CREATE = 'created successfully'
MSG_UPDATE = 'updated successfully'
MSG_DELETE = 'deleted successfully'
MSG_PERMISSION = 'Permission denied'
