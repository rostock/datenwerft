from django.contrib.auth.decorators import login_required
from django.urls import path
from rest_framework import routers

from .views import FmfCreateView, FmfDeleteView, FmfUpdateView, IndexView, TableView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'fmm'

urlpatterns = [
  # main page
  path(
    '',
    view=login_required(IndexView.as_view()),
    name='index',
  ),
  # table page
  path(
    'fmf/table',
    view=login_required(TableView.as_view()),
    name='table',
  ),
  # form page for creating a FMF instance
  path(
    'fmf/create',
    view=login_required(FmfCreateView.as_view()),
    name='fmf_create',
  ),
  # form page for updating a FMF instance
  path(
    'fmf/update/<pk>',
    view=login_required(FmfUpdateView.as_view()),
    name='fmf_update',
  ),
  # form page for deleting a FMF instance
  path(
    'fmf/delete/<pk>',
    view=login_required(FmfDeleteView.as_view()),
    name='fmf_delete',
  ),
]
