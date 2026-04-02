from django.contrib.auth.decorators import login_required
from django.urls import path, re_path
from rest_framework import routers

from .views import AddressSearchView, AddSubsetView, OWSProxyView, ReverseSearchView, renderpdf

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'toolbox'

urlpatterns = [
  # create a subset
  path('subset/add', view=login_required(AddSubsetView.as_view()), name='subset_add'),
  # proxy for OGC web services (OWS)
  re_path(route=r'owsproxy', view=login_required(OWSProxyView.as_view()), name='owsproxy'),
  # address search
  path('addresssearch', view=login_required(AddressSearchView.as_view()), name='addresssearch'),
  # search for objects in specified radius around passed coordinates
  path('reversesearch', view=login_required(ReverseSearchView.as_view()), name='reversesearch'),
  # render PDF files from templates and data
  path('renderpdf', view=login_required(renderpdf), name='renderpdf'),
]
