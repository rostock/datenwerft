from django.contrib.auth.decorators import login_required
from django.urls import path
from rest_framework import routers

from .views.views import IndexView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'bemas'


urlpatterns = [
  # IndexView:
  # main page
  path(
    '',
    view=login_required(IndexView.as_view()),
    name='index'
  )
]
