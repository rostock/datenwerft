from contextlib import contextmanager
from unittest.mock import patch

from django.test import SimpleTestCase

from pygeoapi.views.functions import get_database_columns


class FakeCursor:
  """
  answers the catalog query with rows handed in by the test
  """

  def __init__(self, rows):
    self.rows = rows

  def execute(self, statement, parameters=None):
    pass

  def fetchall(self):
    return self.rows


class FakeConnection:
  def __init__(self, rows):
    self.rows = rows
    self.closed = False

  @contextmanager
  def cursor(self):
    yield FakeCursor(self.rows)

  def close(self):
    self.closed = True


class GetDatabaseColumnsTest(SimpleTestCase):
  """
  tests for the data type get_database_columns() reports per column

  the source database is not reachable from the test suite, so the answer of the
  catalog query is handed in
  """

  def columns(self, rows):
    with patch('pygeoapi.views.functions.create_database_connection') as connect:
      connect.return_value = FakeConnection(rows)
      return get_database_columns('any connection', 'public', 'trees')

  def test_a_column_reports_name_and_data_type(self):
    self.assertEqual(
      self.columns([('strasse', 'character varying(50)')]),
      [{'name': 'strasse', 'type': 'character varying(50)'}],
    )

  def test_an_unresolvable_data_type_stays_empty(self):
    # '???' is a valid string and would otherwise be stored as if it were a type
    self.assertEqual(
      self.columns([('strasse', '???')]),
      [{'name': 'strasse', 'type': ''}],
    )

  def test_a_missing_data_type_stays_empty(self):
    self.assertEqual(
      self.columns([('strasse', None)]),
      [{'name': 'strasse', 'type': ''}],
    )

  def test_an_unreachable_source_yields_no_columns(self):
    with patch('pygeoapi.views.functions.create_database_connection') as connect:
      connect.return_value = None
      self.assertEqual(get_database_columns('any connection', 'public', 'trees'), [])
