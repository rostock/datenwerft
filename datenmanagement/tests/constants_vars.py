from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent

DATABASES = {
  'default',
  'datenmanagement'
}

USERNAME = 'worschdsupp'
PASSWORD = 'worschdsupp42'

VALID_POLYGON = 'POLYGON((12.057 54.158, 12.057 54.159, ' \
                '12.058 54.159, 12.058 54.158, 12.057 54.158))'
VALID_MULTIPOLYGON = 'MULTIPOLYGON(((12.057 54.158, 12.057 54.159, ' \
                     '12.058 54.159, 12.058 54.158, 12.057 54.158)))'

INVALID_STRING = 'Worsch´d  supp'

START_VIEW_STRING = 'in Tabelle auflisten'
LIST_VIEW_STRING = 'Liste aller'
DATA_VIEW_PARAMS = {
  'order[0][column]': 0
}
