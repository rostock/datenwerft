from json import loads

from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic.base import TemplateView

from stadtbereichskatalog.models import Category, Indicator, Source, Topic
from stadtbereichskatalog.utils import is_stadtbereichskatalog_user

from ..apps import StadtbereichskatalogConfig as appConfig
from .base import (
  MetadataEditView,
  MetadataTableDataView,
  MetadataTableView,
)
from .functions import (
  add_app_context_elements,
  add_permissions_context_elements,
  convert_value,
  data_to_csv,
  data_to_excel,
  delete_data,
  get_database_columns,
  get_database_schemas,
  get_database_tables,
  get_distinct_areas,
  get_distinct_elections,
  get_distinct_years,
  import_data,
  make_error,
  read_tabular_file,
)

#
# class-based views
#


class IndexView(TemplateView):
  """
  view for main page

  :param template_name: template name
  """

  template_name = 'stadtbereichskatalog/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary with all context elements for this view

    :param kwargs:
    :return: dictionary with all context elements for this view
    """
    context = super().get_context_data(**kwargs)
    # add global app related context elements
    context = add_app_context_elements(context)
    # add permissions related context elements
    context = add_permissions_context_elements(context, self.request.user)
    return context


class TopicTableDataView(MetadataTableDataView):
  """
  view for composing table data out of instances of metadata model class:
  Themenbereich

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Topic
  edit_view_name = f'{appConfig.name}:topic_edit'


class TopicTableView(MetadataTableView):
  """
  view for table page for instances of metadata model class:
  Themenbereich

  :param model: model
  :param table_data_view_name: name of view for composing table data
  :param icon_name: icon name
  """

  model = Topic
  table_data_view_name = f'{appConfig.name}:topic_tabledata'
  icon_name = 'topic'


class TopicEditView(MetadataEditView):
  """
  view for form page for editing an instance of metadata model class:
  Themenbereich

  :param model: model
  :param cancel_url: custom cancel URL
  """

  model = Topic
  cancel_url = f'{appConfig.name}:topic_table'


class CategoryTableDataView(MetadataTableDataView):
  """
  view for composing table data out of instances of metadata model class:
  Kategorie

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Category
  edit_view_name = f'{appConfig.name}:category_edit'


class CategoryTableView(MetadataTableView):
  """
  view for table page for instances of metadata model class:
  Kategorie

  :param model: model
  :param table_data_view_name: name of view for composing table data
  :param icon_name: icon name
  """

  model = Category
  table_data_view_name = f'{appConfig.name}:category_tabledata'
  icon_name = 'category'


class CategoryEditView(MetadataEditView):
  """
  view for form page for editing an instance of metadata model class:
  Kategorie

  :param model: model
  :param cancel_url: custom cancel URL
  """

  model = Category
  cancel_url = f'{appConfig.name}:category_table'


class SourceTableDataView(MetadataTableDataView):
  """
  view for composing table data out of instances of metadata model class:
  Quellenangabe

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Source
  edit_view_name = f'{appConfig.name}:source_edit'


class SourceTableView(MetadataTableView):
  """
  view for table page for instances of metadata model class:
  Quellenangabe

  :param model: model
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = Source
  table_data_view_name = f'{appConfig.name}:source_tabledata'
  icon_name = 'source'


class SourceEditView(MetadataEditView):
  """
  view for form page for editing an instance of metadata model class:
  Quellenangabe

  :param model: model
  :param cancel_url: custom cancel URL
  """

  model = Source
  cancel_url = f'{appConfig.name}:source_table'


class IndicatorTableDataView(MetadataTableDataView):
  """
  view for composing table data out of instances of metadata model class:
  Indikator

  :param model: model
  :param edit_view_name: name of view for form page for editing
  """

  model = Indicator
  edit_view_name = f'{appConfig.name}:indicator_edit'


class IndicatorTableView(MetadataTableView):
  """
  view for table page for instances of metadata model class:
  Indikator

  :param model: model
  :param table_data_view_name: name of view for composing table data out of instances
  :param icon_name: icon name
  """

  model = Indicator
  table_data_view_name = f'{appConfig.name}:indicator_tabledata'
  icon_name = 'indicator'


class IndicatorEditView(MetadataEditView):
  """
  view for form page for editing an instance of metadata model class:
  Indikator

  :param model: model
  :param cancel_url: custom cancel URL
  """

  model = Indicator
  cancel_url = f'{appConfig.name}:indicator_table'


#
# function-based views
#


def data_deletion(request):
  """
  creates and returns view for page for deleting data

  :param request: request object
  :return: view for page for deleting data
  """

  # add global app related context elements
  context = add_app_context_elements({})
  # add permissions related context elements
  context = add_permissions_context_elements(context, request.user)
  # add to context: schemas
  schemas = get_database_schemas()
  context['schemas'] = schemas
  return render(
    request,
    template_name='stadtbereichskatalog/data_deletion.html',
    context=context,
  )


def data_export(request):
  """
  creates and returns view for page for exporting data

  :param request: request object
  :return: view for page for exporting data
  """

  # add global app related context elements
  context = add_app_context_elements({})
  # add permissions related context elements
  context = add_permissions_context_elements(context, request.user)
  # add to context: schemas
  schemas = get_database_schemas()
  context['schemas'] = schemas
  return render(
    request,
    template_name='stadtbereichskatalog/data_export.html',
    context=context,
  )


def data_import_mapping(request):
  """
  creates and returns view for page for importing and mapping data

  :param request: request object
  :return: view for page for importing and mapping data
  """

  # add global app related context elements
  context = add_app_context_elements({})
  # add permissions related context elements
  context = add_permissions_context_elements(context, request.user)
  # add to context: schemas
  schemas = get_database_schemas()
  context['schemas'] = schemas
  return render(
    request,
    template_name='stadtbereichskatalog/data_import_mapping.html',
    context=context,
  )


def database_columns(request):
  """
  creates and returns JSON with all columns of passed table within passed database schema

  :param request: request object
  :return: JSON with all columns of passed table within passed database schema
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    schema = request.GET.get('schema')
    table = request.GET.get('table')
    columns = get_database_columns(schema, table)
    return JsonResponse(
      data={'columns': columns},
      json_dumps_params={'indent': 2, 'ensure_ascii': False},
      content_type='application/json; charset=utf-8',
    )

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def database_tables(request):
  """
  creates and returns JSON with all tables of passed database schema

  :param request: request object
  :return: JSON with all tables of passed database schema
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    schema = request.GET.get('schema')
    tables = get_database_tables(schema)
    return JsonResponse(
      data={'tables': tables},
      json_dumps_params={'indent': 2, 'ensure_ascii': False},
      content_type='application/json; charset=utf-8',
    )
  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def distinct_areas(request):
  """
  creates and returns JSON with all distinct areas of passed table within passed database schema

  :param request: request object
  :return: JSON with all distinct areas of passed table within passed database schema
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    schema = request.GET.get('schema')
    table = request.GET.get('table')
    areas = get_distinct_areas(schema, table)
    return JsonResponse(
      data={'areas': areas},
      json_dumps_params={'indent': 2, 'ensure_ascii': False},
      content_type='application/json; charset=utf-8',
    )

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def distinct_elections(request):
  """
  creates and returns JSON with all distinct elections
  of passed table within passed database schema

  :param request: request object
  :return: JSON with all distinct elections of passed table within passed database schema
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    schema = request.GET.get('schema')
    table = request.GET.get('table')
    elections = get_distinct_elections(schema, table)
    return JsonResponse(
      data={'elections': elections},
      json_dumps_params={'indent': 2, 'ensure_ascii': False},
      content_type='application/json; charset=utf-8',
    )

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def distinct_years(request):
  """
  creates and returns JSON with all distinct years of passed table within passed database schema

  :param request: request object
  :return: JSON with all distinct years of passed table within passed database schema
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    schema = request.GET.get('schema')
    table = request.GET.get('table')
    years = get_distinct_years(schema, table)
    return JsonResponse(
      data={'years': years},
      json_dumps_params={'indent': 2, 'ensure_ascii': False},
      content_type='application/json; charset=utf-8',
    )

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def execute_import(request):
  """
  executes import of passed file into passed table within passed database schema
  accoring to passed mapping

  :param request: request object
  :return: JSON with import result
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    if request.method != 'POST':
      return JsonResponse(
        data={'success': False, 'errors': [{'row': 0, 'message': 'POST required'}]}, status=400
      )
    schema = request.POST.get('schema')
    table = request.POST.get('table')
    mappings = loads(request.POST.get('mappings', '{}'))
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
      return JsonResponse(
        data={'success': False, 'errors': [{'row': 0, 'message': 'No file uploaded'}]}, status=400
      )
    headers, rows = read_tabular_file(uploaded_file)
    insert_columns = list(mappings.keys())
    columns = {item['name']: item for item in get_database_columns(schema, table)}
    rows_to_insert, errors = [], []
    for row_number, source_row in enumerate(rows, start=2):
      insert_row, row_errors = [], []
      try:
        for target_column in insert_columns:
          source_column = mappings[target_column]
          pg_type = columns.get(target_column, {}).get('type')
          raw_value = source_row.get(source_column)
          # type conversion
          try:
            converted_value = convert_value(raw_value, pg_type)
            insert_row.append(converted_value)
          except Exception as e:
            row_errors.append(
              make_error(
                row_number=row_number,
                target_column=target_column,
                source_column=source_column,
                value=raw_value,
                target_type=pg_type,
                error_type='type_conversion',
                message=str(e),
              )
            )
            insert_row.append(None)
        if row_errors:
          errors.extend(row_errors)
          continue
        rows_to_insert.append(tuple(insert_row))
      except Exception as e:
        errors.append(
          make_error(
            row_number=row_number,
            target_column=None,
            source_column=None,
            value=None,
            target_type=None,
            error_type='row_processing',
            message=str(e),
          )
        )
    if errors:
      return JsonResponse(data={'success': False, 'errors': errors}, status=400)
    import_process = import_data(schema, table, insert_columns, rows_to_insert)
    if import_process['success']:
      return JsonResponse(data=import_process, status=200)
    return JsonResponse(data=import_process, status=400)

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def execute_deletion(request):
  """
  executes deletion of data from passed table within passed database schema
  accoring to passed filters

  :param request: request object
  :return: JSON with import result
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    if request.method != 'POST':
      return JsonResponse(
        data={'success': False, 'errors': [{'row': 0, 'message': 'POST required'}]}, status=400
      )
    schema = request.POST.get('schema')
    table = request.POST.get('table')
    year = request.POST.get('year')
    election = request.POST.get('election')
    if not year and not election:
      return JsonResponse(
        data={'success': False, 'errors': [{'row': 0, 'message': 'No filters set'}]}, status=400
      )
    deletion_process = delete_data(schema, table, year, election)
    if deletion_process['success']:
      return JsonResponse(data=deletion_process, status=200)
    return JsonResponse(data=deletion_process, status=400)

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def export_csv_excel(request):
  """
  creates and returns Excel friendly CSV with data from a query
  based on passed table within passed database schema
  (and, optionally, passed filters)

  :param request: request object
  :return: Excel friendly CSV with data from a query based on passed table
  within passed database schema (and, optionally, passed filters)
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    schema = request.GET.get('schema')
    table = request.GET.get('table')
    year = request.GET.get('year')
    area = request.GET.get('area')
    election = request.GET.get('election')
    return data_to_csv(schema, table, year, area, election, standard=False)

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def export_csv_standard(request):
  """
  creates and returns standard CSV with data from a query
  based on passed table within passed database schema
  (and, optionally, passed filters)

  :param request: request object
  :return: standard CSV with data from a query based on passed table within passed database schema
  (and, optionally, passed filters)
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    schema = request.GET.get('schema')
    table = request.GET.get('table')
    year = request.GET.get('year')
    area = request.GET.get('area')
    election = request.GET.get('election')
    return data_to_csv(schema, table, year, area, election, standard=True)

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def export_excel(request):
  """
  creates and returns XLSX with data from a query
  based on passed table within passed database schema
  (and, optionally, passed filters)

  :param request: request object
  :return: XLSX with data from a query based on passed table
  within passed database schema (and, optionally, passed filters)
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    schema = request.GET.get('schema')
    table = request.GET.get('table')
    year = request.GET.get('year')
    area = request.GET.get('area')
    election = request.GET.get('election')
    return data_to_excel(schema, table, year, area, election)

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )


def preview_csv(request):
  """
  creates and returns JSON with all headers and a preview of the first few rows
  of passed CSV file

  :param request: request object
  :return: JSON with all headers and a preview of the first few rows of passed CSV file
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    if request.method != 'POST':
      return JsonResponse(data={'error': 'POST required'}, status=400)
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
      return JsonResponse(data={'error': 'No file uploaded'}, status=400)
    headers, rows = read_tabular_file(uploaded_file)
    return JsonResponse(
      data={
        'headers': headers,
        'preview_rows': rows[:5],
      },
      json_dumps_params={'indent': 2, 'ensure_ascii': False},
      content_type='application/json; charset=utf-8',
    )

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )
