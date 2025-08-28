from django.contrib.auth.decorators import login_required
from django.urls import path
from rest_framework import routers

from .views import (
  FmfCreateView,
  FmfDeleteView,
  FmfUpdateView,
  IndexView,
  OverviewView,
  PaketUmweltCreateView,
  PaketUmweltDeleteView,
  PaketUmweltUpdateView,
  TableDataView,
  TableView,
)

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'fmm'

urlpatterns = [
  # main page
  path(
    route='',
    view=login_required(IndexView.as_view()),
    name='index',
  ),
  # composing table data
  path(
    route='tabledata',
    view=login_required(TableDataView.as_view()),
    name='tabledata',
  ),
  # table page
  path(
    route='table',
    view=login_required(TableView.as_view()),
    name='table',
  ),
  # overview page
  path(
    route='overview/<pk>',
    view=login_required(OverviewView.as_view()),
    name='overview',
  ),
  # form page for creating a FMF instance
  path(
    route='fmf/create',
    view=login_required(FmfCreateView.as_view()),
    name='fmf_create',
  ),
  # form page for updating a FMF instance
  path(
    route='fmf/update/<pk>',
    view=login_required(FmfUpdateView.as_view()),
    name='fmf_update',
  ),
  # form page for deleting a FMF instance
  path(
    route='fmf/delete/<pk>',
    view=login_required(FmfDeleteView.as_view()),
    name='fmf_delete',
  ),
  # form page for creating a Paket Umwelt instance
  path(
    route='paketumwelt/create/<fmf_pk>',
    view=login_required(PaketUmweltCreateView.as_view()),
    name='paketumwelt_create',
  ),
  # form page for updating a Paket Umwelt instance
  path(
    route='paketumwelt/update/<pk>',
    view=login_required(PaketUmweltUpdateView.as_view()),
    name='paketumwelt_update',
  ),
  # form page for deleting a Paket Umwelt instance
  path(
    route='paketumwelt/delete/<pk>',
    view=login_required(PaketUmweltDeleteView.as_view()),
    name='paketumwelt_delete',
  ),
]
