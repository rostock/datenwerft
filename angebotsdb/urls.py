from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.urls import path
from rest_framework import routers

from .models.services import Service
from .views.base import CombinedMapDataView, GenericMapDataView
from .views.forms import (
  GenericCreateView,
  GenericDeleteView,
  GenericUpdateView,
  ServiceImageDeleteView,
)
from .views.inbox import InboxListView
from .views.indexView import IndexView, save_dashboard_layout
from .views.listView import ListView
from .views.review import ReviewServiceView, SubmitForReviewView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'angebotsdb'

urlpatterns = [
  # main page
  path('', view=login_required(IndexView.as_view()), name='index'),
  path('save-layout/', view=save_dashboard_layout, name='save_layout'),
  # inbox
  path('inbox/', view=login_required(InboxListView.as_view()), name='inbox_list'),
  # review workflow
  path(
    'review/<int:task_id>/',
    view=login_required(ReviewServiceView.as_view()),
    name='review_service',
  ),
  path(
    '<str:service_type>/<int:service_id>/submit-review/',
    view=login_required(SubmitForReviewView.as_view()),
    name='submit_for_review',
  ),
  # Bild-Lösch-Endpoint (AJAX)
  path(
    'service-image/<int:pk>/delete/',
    view=login_required(ServiceImageDeleteView.as_view()),
    name='service_image_delete',
  ),
  # Kombinierte MapData-Ansicht für alle Services
  path(
    route='services/mapdata',
    view=login_required(CombinedMapDataView.as_view()),
    name='services_mapdata',
  ),
]

models = apps.get_app_config(app_name).get_models()
for model in models:
  if getattr(model, '_exclude_from_crud', False):
    continue
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
      route=f'{model_name}/<int:pk>/detail',
      view=login_required(GenericUpdateView.as_view(model=model, readonly=True)),
      name=f'{model_name}_detail',
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
  if not model._meta.abstract and issubclass(model, Service):
    urlpatterns.append(
      path(
        route=f'{model_name}/mapdata',
        view=login_required(GenericMapDataView.as_view(model=model)),
        name=f'{model_name}_mapdata',
      )
    )
