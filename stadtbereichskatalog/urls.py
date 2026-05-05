from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from .views import (
  IndexView,
  CategoryTableDataView,
  CategoryTableView,
  SourceTableDataView,
  SourceTableView,
)

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'stadtbereichskatalog'

urlpatterns = [
  # main page
  path(
    route='',
    view=login_required(IndexView.as_view()),
    name='index',
  ),
  # composing table data out of instances of object:
  # Themenbereich und/oder Kategorie
  path(
    route='category/tabledata',
    view=login_required(CategoryTableDataView.as_view()),
    name='category_tabledata',
  ),
  # table page for instances of object:
  # Themenbereich und/oder Kategorie
  path(
    route='category/table',
    view=login_required(CategoryTableView.as_view()),
    name='category_table',
  ),
  # form page for editing an instance of object:
  # Themenbereich und/oder Kategorie
  path(
    route='category/edit/<pk>',
    view=login_required(
      CategoryTableDataView.as_view()
    ),
    name='category_edit',
  ),
  # composing table data out of instances of object:
  # Quellenangabe
  path(
    route='source/tabledata',
    view=login_required(SourceTableDataView.as_view()),
    name='source_tabledata',
  ),
  # table page for instances of object:
  # Quellenangabe
  path(
    route='source/table',
    view=login_required(SourceTableView.as_view()),
    name='source_table',
  ),
  # form page for editing an instance of object:
  # Quellenangabe
  path(
    route='source/edit/<pk>',
    view=login_required(
      SourceTableDataView.as_view()
    ),
    name='source_edit',
  ),
]
