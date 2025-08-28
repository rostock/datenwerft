from django.urls import path
from rest_framework.routers import DefaultRouter

from .models import Codelist, CodelistValue
from .views.api import (
  CodelistValueViewSet,
  CodelistViewSet,
  get_by_uuid,
  get_codelistvalue_by_codelist_and_uuid,
  get_codelistvalues_by_codelist,
)

router = DefaultRouter()
codelist_viewset = type('CodelistViewSet', (CodelistViewSet,), {'model': Codelist})
router.register(
  prefix='codelist',
  viewset=codelist_viewset,
  basename='codelist',
)
codelistvalue_viewset = type(
  'CodelistValueViewSet', (CodelistValueViewSet,), {'model': CodelistValue}
)
router.register(prefix='codelistvalue', viewset=codelistvalue_viewset, basename='codelistvalue')

api_urlpatterns = router.urls
api_urlpatterns += [
  # API function get_by_uuid()
  path(
    route='get-by-uuid/<uuid>',
    view=get_by_uuid,
    name='get_codelist_or_codelistvalue_by_uuid',
  ),
  # API function get_codelistvalue_by_codelist_and_uuid()
  path(
    route='get-codelistvalue-by-codelist-and-uuid/<codelist_name>/<codelistvalue_uuid>',
    view=get_codelistvalue_by_codelist_and_uuid,
    name='get_codelistvalue_by_codelist_and_uuid',
  ),
  # API function get_codelistvalues_by_codelist()
  path(
    route='get-codelistvalues-by-codelist/<codelist_name>',
    view=get_codelistvalues_by_codelist,
    name='get_codelistvalues_by_codelist',
  ),
]

app_name = 'gdihrocodelists'

urlpatterns = []
