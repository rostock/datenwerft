from csv import DictReader
from io import TextIOWrapper

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
  get_database_columns,
  get_database_schemas,
  get_database_tables,
  get_distinct_areas,
  get_distinct_years,
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


def distinct_years(request):
  """
  creates and returns JSON with all distinct years of passed table within passed database schema

  :param request: request object
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


def distinct_areas(request):
  """
  creates and returns JSON with all distinct areas of passed table within passed database schema

  :param request: request object
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


def database_tables(request):
  """
  creates and returns JSON with all tables of passed database schema

  :param request: request object
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


def database_columns(request):
  """
  creates and returns JSON with all columns of passed table within passed database schema

  :param request: request object
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


def preview_csv(request):
  """
  creates and returns JSON with all headers and a preview of the first few rows
  of passed CSV file

  :param request: request object
  """

  if request.user.is_superuser or is_stadtbereichskatalog_user(request.user):
    if request.method != 'POST':
      return JsonResponse(data={'error': 'POST required'}, status=400)
    uploaded_file = request.FILES.get('file')
    if not uploaded_file:
      return JsonResponse(data={'error': 'No file uploaded'}, status=400)
    decoded_file = TextIOWrapper(uploaded_file.file, encoding='utf-8')
    reader = DictReader(decoded_file)
    rows = list(reader)
    preview_rows = rows[:5]
    return JsonResponse(
      data={'headers': reader.fieldnames, 'preview_rows': preview_rows},
      json_dumps_params={'indent': 2, 'ensure_ascii': False},
      content_type='application/json; charset=utf-8',
    )

  return JsonResponse(
    data={'has_necessary_permissions': False},
  )
