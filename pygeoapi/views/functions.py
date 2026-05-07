from django.db import connections


def get_database_schemas(database_connection):
  """
  gets all schemas of passed database and returns their names

  :param database_connection: database_connection
  :return: names of all schemas of passed database
  """
  connection = connections['stadtbereichskatalog']
  with connection.cursor() as cursor:
    cursor.execute("""
      SELECT schema_name
       FROM information_schema.schemata
        WHERE schema_name NOT IN (
         'information_schema', 'pg_catalog', 'pg_toast'
        )
         ORDER BY schema_name
    """)
    return [row[0] for row in cursor.fetchall()]


def get_database_tables(database_connection, schema_name):
  """
  gets all tables of passed schema of passed database and returns their names

  :param database_connection: database_connection
  :param schema_name: name of schema
  :return: names of all tables of passed schema of passed database
  """
  connection = connections['stadtbereichskatalog']
  with connection.cursor() as cursor:
    cursor.execute(
      """
      SELECT table_name
       FROM information_schema.tables
        WHERE table_schema = %s
         ORDER BY table_name
    """,
      [schema_name],
    )
    return [row[0] for row in cursor.fetchall()]


def get_database_columns(database_connection, schema_name, table_name):
  """
  gets all columns of passed table within passed schema of passed database and returns their names

  :param database_connection: database_connection
  :param schema_name: name of schema
  :param table_name: name of table
  :return: names of all columns of passed table within passed schema of passed database
  """
  connection = connections['stadtbereichskatalog']
  with connection.cursor() as cursor:
    cursor.execute(
      """
      SELECT column_name
       FROM information_schema.columns
        WHERE table_schema = %s
        AND table_name = %s
         ORDER BY ordinal_position
    """,
      [schema_name, table_name],
    )
    return [row[0] for row in cursor.fetchall()]
