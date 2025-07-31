from django.apps import apps
from django.urls import path
from rest_framework.routers import DefaultRouter

from .views.api import GenericModelViewSet, get_by_uuid

router = DefaultRouter()

for model in apps.get_app_config('gdihrometadata').get_models():
  model_name = model.__name__.lower()
  # dynamically create a subclass of GenericModelViewSet with model assigned
  viewset = type(f'{model.__name__}ViewSet', (GenericModelViewSet,), {'model': model})
  router.register(prefix=model_name, viewset=viewset, basename=model_name)

api_urlpatterns = router.urls

api_urlpatterns += [
  # main page
  path(
    'get-by-uuid/',
    view=get_by_uuid,
    name='get_by_uuid',
  ),
]

urlpatterns = []
