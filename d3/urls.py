from django.apps import apps
from django.contrib.auth.decorators import user_passes_test
from django.urls import path
from rest_framework.routers import DefaultRouter

from d3.models import Vorgang
from d3.views.views_form import DataAddView

router = DefaultRouter()

app_name = 'd3'

api_urlpatterns = router.urls

def permission_required(*perms):
  """
  checks passed authorization(s)

  :param perms: authorization(s)
  :return: check of passed authorization(s)
  """
  return user_passes_test(lambda u: any(u.has_perm(perm) for perm in perms))

models = apps.get_app_config('datenmanagement').get_models()

urlpatterns = []

for model in models:
  model_name = model.__name__
  model_name_lower = model_name.lower()

  # form page for adding new d3 processes to a model
  urlpatterns.append(
    path(
      model_name + '/<str:pk>/process/add',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower,
      )(DataAddView.as_view(model=Vorgang, template_name='d3/vorgang-form.html', datenmanagement_model=model_name)),
      name=model_name + '_d3_add_process',
    )
  )
