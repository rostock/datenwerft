from django.contrib.auth.decorators import login_required
from django.urls import path, re_path
from rest_framework import routers

from .views import AddressSearchView, AddSubsetView, OWSProxyView, ReverseSearchView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'toolbox'

urlpatterns = [
  # AddSubsetView:
  # adds a new subset
  path(
    'subset/add',
    view=login_required(AddSubsetView.as_view()),
    name='subset_add'
  ),
  # OWSProxyView:
  # proxy for OGC web services (OWS)
  re_path(
    route=r'owsproxy',
    view=login_required(OWSProxyView.as_view()),
    name='owsproxy'
  ),
  # AddressSearchView:
  # address search
  path(
    'addresssearch',
    view=login_required(AddressSearchView.as_view()),
    name='addresssearch'
  ),
  # ReverseSearchView:
  # search for objects in specified radius around given coordinates
  path(
    'reversesearch',
    view=login_required(ReverseSearchView.as_view()),
    name='reversesearch'
  )
]
