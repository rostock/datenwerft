from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from .apps import StadtbereichskatalogConfig as appConfig
from .views import (
  CategoryEditView,
  CategoryTableDataView,
  CategoryTableView,
  IndexView,
  IndicatorEditView,
  IndicatorTableDataView,
  IndicatorTableView,
  SourceEditView,
  SourceTableDataView,
  SourceTableView,
  TopicEditView,
  TopicTableDataView,
  TopicTableView,
  data_deletion,
  data_editing,
  data_export,
  data_import_mapping,
  database_columns,
  database_data,
  database_tables,
  distinct_areas,
  distinct_elections,
  distinct_years,
  execute_deletion,
  execute_import,
  export_csv_excel,
  export_csv_standard,
  export_excel,
  preview_csv,
)

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = appConfig.name

urlpatterns = [
  # main page
  path(
    route='',
    view=login_required(IndexView.as_view()),
    name='index',
  ),
  # composing table data out of instances of metadata model class:
  # Themenbereich
  path(
    route='metadata/topic/tabledata',
    view=login_required(TopicTableDataView.as_view()),
    name='topic_tabledata',
  ),
  # table page for instances of metadata model class:
  # Themenbereich
  path(
    route='metadata/topic/table',
    view=login_required(TopicTableView.as_view()),
    name='topic_table',
  ),
  # form page for editing an instance of metadata model class:
  # Themenbereich
  path(
    route='metadata/topic/edit/<pk>',
    view=login_required(
      TopicEditView.as_view(success_url=reverse_lazy(f'{app_name}:topic_table'))
    ),
    name='topic_edit',
  ),
  # composing table data out of instances of metadata model class:
  # Kategorie
  path(
    route='metadata/category/tabledata',
    view=login_required(CategoryTableDataView.as_view()),
    name='category_tabledata',
  ),
  # table page for instances of metadata model class:
  # Kategorie
  path(
    route='metadata/category/table',
    view=login_required(CategoryTableView.as_view()),
    name='category_table',
  ),
  # form page for editing an instance of metadata model class:
  # Kategorie
  path(
    route='metadata/category/edit/<pk>',
    view=login_required(
      CategoryEditView.as_view(success_url=reverse_lazy(f'{app_name}:category_table'))
    ),
    name='category_edit',
  ),
  # composing table data out of instances of metadata model class:
  # Quellenangabe
  path(
    route='metadata/source/tabledata',
    view=login_required(SourceTableDataView.as_view()),
    name='source_tabledata',
  ),
  # table page for instances of metadata model class:
  # Quellenangabe
  path(
    route='metadata/source/table',
    view=login_required(SourceTableView.as_view()),
    name='source_table',
  ),
  # form page for editing an instance of metadata model class:
  # Quellenangabe
  path(
    route='metadata/source/edit/<pk>',
    view=login_required(
      SourceEditView.as_view(success_url=reverse_lazy(f'{app_name}:source_table'))
    ),
    name='source_edit',
  ),
  # composing table data out of instances of metadata model class:
  # Indikator
  path(
    route='metadata/indicator/tabledata',
    view=login_required(IndicatorTableDataView.as_view()),
    name='indicator_tabledata',
  ),
  # table page for instances of metadata model class:
  # Indikator
  path(
    route='metadata/indicator/table',
    view=login_required(IndicatorTableView.as_view()),
    name='indicator_table',
  ),
  # form page for editing an instance of metadata model class:
  # Indikator
  path(
    route='metadata/indicator/edit/<pk>',
    view=login_required(
      IndicatorEditView.as_view(success_url=reverse_lazy(f'{app_name}:indicator_table'))
    ),
    name='indicator_edit',
  ),
  # page for exporting data
  path(
    route='data/export',
    view=login_required(data_export),
    name='data_export',
  ),
  # page for importing and mapping data
  path(
    route='data/import',
    view=login_required(data_import_mapping),
    name='data_import_mapping',
  ),
  # page for deleting data
  path(
    route='data/deletion',
    view=login_required(data_deletion),
    name='data_deletion',
  ),
  # page for editing data
  path(
    route='data/editing',
    view=login_required(data_editing),
    name='data_editing',
  ),
  # JSON with all columns of table within database schema
  path(
    route='data/action/get-database-columns',
    view=login_required(database_columns),
    name='get_database_columns',
  ),
  # JSON with all data of table within database schema
  path(
    route='data/action/get-database-data',
    view=login_required(database_data),
    name='get_database_data',
  ),
  # JSON with all tables of database schema
  path(
    route='data/action/get-database-tables',
    view=login_required(database_tables),
    name='get_database_tables',
  ),
  # JSON with all distinct areas of table within database schema
  path(
    route='data/action/get-distinct-areas',
    view=login_required(distinct_areas),
    name='get_distinct_areas',
  ),
  # JSON with all distinct elections of table within database schema
  path(
    route='data/action/get-distinct-elections',
    view=login_required(distinct_elections),
    name='get_distinct_elections',
  ),
  # JSON with all distinct years of table within database schema
  path(
    route='data/action/get-distinct-years',
    view=login_required(distinct_years),
    name='get_distinct_years',
  ),
  # executes deletion of data from table within database schema accoring to filters
  path(
    route='data/action/execute-deletion',
    view=login_required(execute_deletion),
    name='execute_deletion',
  ),
  # executes import of file into table within database schema accoring to mapping
  path(
    route='data/action/execute-import',
    view=login_required(execute_import),
    name='execute_import',
  ),
  # CSV (Excel friendly) with data of table within database schema
  path(
    route='data/action/export-csv-excel',
    view=login_required(export_csv_excel),
    name='export_csv_excel',
  ),
  # CSV (standard) with data of table within database schema
  path(
    route='data/action/export-csv-standard',
    view=login_required(export_csv_standard),
    name='export_csv_standard',
  ),
  # XLSX with data of table within database schema
  path(
    route='data/action/export-excel',
    view=login_required(export_excel),
    name='export_excel',
  ),
  # JSON with all headers and a preview of the first few rows of CSV file
  path(
    route='data/action/preview-csv',
    view=login_required(preview_csv),
    name='preview_csv',
  ),
]
