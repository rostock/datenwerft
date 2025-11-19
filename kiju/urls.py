from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.urls import path
from rest_framework import routers

from .views.base import GenericMapDataView, MapView
from .views.forms import GenericCreateView, GenericDeleteView, GenericUpdateView
from .views.indexView import IndexView
from .views.listView import ListView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'kiju'

urlpatterns = [
  # main page
  path('', view=login_required(IndexView.as_view()), name='index'),
  # map page
  path('map', view=login_required(MapView.as_view()), name='map'),
]

models = apps.get_app_config(app_name).get_models()
for model in models:
  model_name = model.__name__.lower()

  urlpatterns.append(
    path(
      route=model_name,
      view=login_required(ListView.as_view(model=model)),
      name=f'{model_name}_list',
    )
  )
  urlpatterns.append(
    path(
      route=f'{model_name}/create',
      view=login_required(GenericCreateView.as_view(model=model)),
      name=f'{model_name}_create',
    )
  )
  urlpatterns.append(
    path(
      route=f'{model_name}/<int:pk>/update',
      view=login_required(GenericUpdateView.as_view(model=model)),
      name=f'{model_name}_update',
    )
  )
  urlpatterns.append(
    path(
      route=f'{model_name}/<int:pk>/delete',
      view=login_required(GenericDeleteView.as_view(model=model)),
      name=f'{model_name}_delete',
    )
  )

  # Add map data URLs for models with geometry
  if model_name in ['service', 'holidayservice', 'preventionservice']:
    urlpatterns.append(
      path(
        route=f'{model_name}/mapdata',
        view=login_required(GenericMapDataView.as_view(model=model)),
        name=f'{model_name}_mapdata',
      )
    )
