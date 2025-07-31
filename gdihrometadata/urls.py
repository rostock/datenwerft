from django.apps import apps
from rest_framework.routers import DefaultRouter

from .views.api import GenericModelViewSet

router = DefaultRouter()

app_name = 'gdihrometadata'

models = apps.get_app_config(app_name).get_models()
for model in models:
  model_name = model.__name__.lower()
  # dynamically create a subclass of GenericModelViewSet with model assigned
  viewset = type(
    f"{model.__name__}ViewSet",
    (GenericModelViewSet,),
    {'model': model}
  )
  router.register(model_name, viewset=viewset, basename=model_name)

api_urlpatterns = router.urls

urlpatterns = []
