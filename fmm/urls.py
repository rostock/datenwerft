from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy
from rest_framework import routers

from .views import FmfCreateView, FmfUpdateView, IndexView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'fmm'

urlpatterns = [
  # main page
  path('', view=login_required(IndexView.as_view()), name='index'),
  # form page for creating a FMF instance
  path(
    'fmf/create',
    view=login_required(FmfCreateView.as_view(success_url=reverse_lazy('fmm:index'))),
    name='fmf_create',
  ),
  # form page for updating a FMF instance
  path(
    'fmf/update/<pk>',
    view=login_required(FmfUpdateView.as_view(success_url=reverse_lazy('fmm:index'))),
    name='fmf_update',
  ),
]
