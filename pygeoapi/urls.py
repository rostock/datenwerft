from django.urls import path
from rest_framework.routers import DefaultRouter
from views import (
  database_columns,
  database_schemas,
  database_tables,
)

router = DefaultRouter()

app_name = 'pygeoapi'

api_urlpatterns = router.urls

urlpatterns = [
  path(
    route='get-database-schemas',
    view=database_schemas,
    name='get_database_schemas',
  ),
  path(
    route='get-database-tables',
    view=database_tables,
    name='get_database_tables',
  ),
  path(
    route='get-database-columns',
    view=database_columns,
    name='get_database_columns',
  ),
]
