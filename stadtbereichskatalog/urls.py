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
  data_export,
  data_import_mapping,
  database_columns,
  database_tables,
  distinct_areas,
  distinct_elections,
  distinct_years,
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
    route='topic/tabledata',
    view=login_required(TopicTableDataView.as_view()),
    name='topic_tabledata',
  ),
  # table page for instances of metadata model class:
  # Themenbereich
  path(
    route='topic/table',
    view=login_required(TopicTableView.as_view()),
    name='topic_table',
  ),
  # form page for editing an instance of metadata model class:
  # Themenbereich
  path(
    route='topic/edit/<pk>',
    view=login_required(
      TopicEditView.as_view(success_url=reverse_lazy(f'{app_name}:topic_table'))
    ),
    name='topic_edit',
  ),
  # composing table data out of instances of metadata model class:
  # Kategorie
  path(
    route='category/tabledata',
    view=login_required(CategoryTableDataView.as_view()),
    name='category_tabledata',
  ),
  # table page for instances of metadata model class:
  # Kategorie
  path(
    route='category/table',
    view=login_required(CategoryTableView.as_view()),
    name='category_table',
  ),
  # form page for editing an instance of metadata model class:
  # Kategorie
  path(
    route='category/edit/<pk>',
    view=login_required(
      CategoryEditView.as_view(success_url=reverse_lazy(f'{app_name}:category_table'))
    ),
    name='category_edit',
  ),
  # composing table data out of instances of metadata model class:
  # Quellenangabe
  path(
    route='source/tabledata',
    view=login_required(SourceTableDataView.as_view()),
    name='source_tabledata',
  ),
  # table page for instances of metadata model class:
  # Quellenangabe
  path(
    route='source/table',
    view=login_required(SourceTableView.as_view()),
    name='source_table',
  ),
  # form page for editing an instance of metadata model class:
  # Quellenangabe
  path(
    route='source/edit/<pk>',
    view=login_required(
      SourceEditView.as_view(success_url=reverse_lazy(f'{app_name}:source_table'))
    ),
    name='source_edit',
  ),
  # composing table data out of instances of metadata model class:
  # Indikator
  path(
    route='indicator/tabledata',
    view=login_required(IndicatorTableDataView.as_view()),
    name='indicator_tabledata',
  ),
  # table page for instances of metadata model class:
  # Indikator
  path(
    route='indicator/table',
    view=login_required(IndicatorTableView.as_view()),
    name='indicator_table',
  ),
  # form page for editing an instance of metadata model class:
  # Indikator
  path(
    route='indicator/edit/<pk>',
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
  # JSON with all distinct years of table within database schema
  path(
    route='get-distinct-years',
    view=login_required(distinct_years),
    name='get_distinct_years',
  ),
  # JSON with all distinct areas of table within database schema
  path(
    route='get-distinct-areas',
    view=login_required(distinct_areas),
    name='get_distinct_areas',
  ),
  # JSON with all distinct elections of table within database schema
  path(
    route='get-distinct-elections',
    view=login_required(distinct_elections),
    name='get_distinct_elections',
  ),
  # page for importing and mapping data
  path(
    route='data/import/mapping',
    view=login_required(data_import_mapping),
    name='data_import_mapping',
  ),
  # JSON with all tables of database schema
  path(
    route='get-database-tables',
    view=login_required(database_tables),
    name='get_database_tables',
  ),
  # JSON with all columns of table within database schema
  path(
    route='get-database-columns',
    view=login_required(database_columns),
    name='get_database_columns',
  ),
  # JSON with all headers and a preview of the first few rows of CSV file
  path(
    route='preview-csv',
    view=login_required(preview_csv),
    name='preview_csv',
  ),
]
