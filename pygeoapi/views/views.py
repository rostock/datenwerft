from django.http import JsonResponse

from .functions import (
  get_database_columns,
  get_database_schemas,
  get_database_tables,
)


def database_schemas(request):
  """
  creates and returns JSON with all schemas of passed database

  :param request: request object
  """

  db = request.GET.get('db')
  schemas = get_database_schemas(db)
  return JsonResponse(
    data={'schemas': schemas},
    json_dumps_params={'indent': 2, 'ensure_ascii': False},
    content_type='application/json; charset=utf-8',
  )


def database_tables(request):
  """
  creates and returns JSON with all tables of passed schema of passed database

  :param request: request object
  """

  db = request.GET.get('db')
  schema = request.GET.get('schema')
  tables = get_database_tables(db, schema)
  return JsonResponse(
    data={'tables': tables},
    json_dumps_params={'indent': 2, 'ensure_ascii': False},
    content_type='application/json; charset=utf-8',
  )


def database_columns(request):
  """
  creates and returns JSON with all columns of passed table within passed schema of passed database

  :param request: request object
  """

  db = request.GET.get('db')
  schema = request.GET.get('schema')
  table = request.GET.get('table')
  columns = get_database_columns(db, schema, table)
  return JsonResponse(
    data={'columns': columns},
    json_dumps_params={'indent': 2, 'ensure_ascii': False},
    content_type='application/json; charset=utf-8',
  )
