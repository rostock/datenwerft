from django.urls import path
from rest_framework.routers import DefaultRouter

from pygeoapi.views.views import FetchModelDatabaseConfigRequestView

router = DefaultRouter()

app_name = 'pygeoapi'

api_urlpatterns = router.urls

urlpatterns = []

urlpatterns.append(
  path('model/database/config', view=FetchModelDatabaseConfigRequestView.as_view())
)
