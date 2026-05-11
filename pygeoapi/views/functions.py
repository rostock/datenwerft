from pygeoapi.utils import create_database_connection


def get_database_schemas(database_connection):
  """
  gets all schemas of passed database and returns their names

  :param database_connection: database connection
  :return: names of all schemas of passed database
  """
  connection = create_database_connection(database_connection)
  if connection:
    with connection.cursor() as cursor:
      cursor.execute("""
        SELECT schema_name
         FROM information_schema.schemata
          WHERE schema_name NOT IN (
           'information_schema', 'pg_catalog', 'pg_toast'
          )
           ORDER BY schema_name
      """)
      result = [row[0] for row in cursor.fetchall()]
      connection.close()
      return result
  else:
    return []


def get_database_tables(database_connection, schema_name):
  """
  gets all tables of passed schema of passed database and returns their names

  :param database_connection: database connection
  :param schema_name: name of schema
  :return: names of all tables of passed schema of passed database
  """
  connection = create_database_connection(database_connection)
  if connection:
    with connection.cursor() as cursor:
      cursor.execute(
        """
        SELECT table_name
         FROM information_schema.tables
          WHERE table_schema = %s
        UNION ALL SELECT matviewname AS table_name
         FROM pg_matviews
          WHERE schemaname = %s
           ORDER BY table_name
      """,
        [schema_name, schema_name],
      )
      result = [row[0] for row in cursor.fetchall()]
      connection.close()
      return result
  else:
    return []


def get_database_columns(database_connection, schema_name, table_name):
  """
  gets all columns of passed table within passed schema of passed database and returns their names

  :param database_connection: database connection
  :param schema_name: name of schema
  :param table_name: name of table
  :return: names of all columns of passed table within passed schema of passed database
  """
  connection = create_database_connection(database_connection)
  if connection:
    with connection.cursor() as cursor:
      cursor.execute(
        """
        SELECT a.attname
         FROM pg_attribute a
         JOIN pg_class t on a.attrelid = t.oid
         JOIN pg_namespace s on t.relnamespace = s.oid
          WHERE a.attnum > 0
          AND NOT a.attisdropped
          AND s.nspname = %s
          AND t.relname = %s
           ORDER BY a.attnum
      """,
        [schema_name, table_name],
      )
      result = [row[0] for row in cursor.fetchall()]
      connection.close()
      return result
  else:
    return []
