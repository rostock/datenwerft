from django.contrib.auth.decorators import login_required
from django.urls import path
from rest_framework import routers

from .views import AddSubsetView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'toolbox'
urlpatterns = [
  path(
    'subsetter/add',
    view=login_required(AddSubsetView.as_view()),
    name='add_subsetter'
  )
]
