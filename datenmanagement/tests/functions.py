from django.db import connections
from pathlib import Path


def load_sql_schema():
  schema_file = open(Path(__file__).resolve().parent.parent / 'sql/schema.sql', 'r')
  schema_sql = schema_file.read()
  with connections['datenmanagement'].cursor() as cursor:
    cursor.execute(schema_sql)
