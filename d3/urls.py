from django.apps import apps
from django.contrib.auth.decorators import user_passes_test
from django.urls import path
from rest_framework.routers import DefaultRouter

from d3.models import Vorgang
from d3.views.views import FetchMetaDataRequestView, ListeDateienView, DownloadView, DokumentenErstellenView, \
  DokumentenBearbeitenView
from d3.views.views_form import ErstelleVorgangView
from d3.views.views_process import TableProcessView

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

def datenmodel_permission_required(model_name_lower: str):
  return permission_required(
    'datenmanagement.change_' + model_name_lower,
    'datenmanagement.delete_' + model_name_lower,
    'datenmanagement.view_' + model_name_lower,
  )

models = apps.get_app_config('datenmanagement').get_models()

urlpatterns = []

for model in models:
  model_name = model.__name__
  model_name_lower = model_name.lower()

  # form page for adding new d3 processes to a model
  urlpatterns.append(
    path(
      model_name + '/<str:pk>/process/add',
      view=datenmodel_permission_required(model_name_lower)(ErstelleVorgangView.as_view(model=Vorgang, template_name='d3/vorgang-form.html', datenmanagement_model=model_name)),
      name=model_name + '_d3_add_process',
    )
  )

  # view to retrieve a list of files from a d3 process
  urlpatterns.append(
    path(
      model_name + '/<str:pk>/process/<int:id>/file',
      view=datenmodel_permission_required(model_name_lower)(ListeDateienView.as_view(datenmanagement_model=model_name)),
      name=model_name + '_d3_list_file',
    )
  )

  # view to download a file from a d3 process
  urlpatterns.append(
    path(
      model_name + '/<str:pk>/file/download/<str:file_id>',
      view=datenmodel_permission_required(model_name_lower)(DownloadView.as_view(datenmanagement_model=model_name)),
      name=model_name + '_file_download',
    )
  )

  # form page for adding new files to a d3 processes
  urlpatterns.append(
    path(
      model_name + '/<str:pk>/process/<int:vorgang_id>/file/create',
      view=datenmodel_permission_required(model_name_lower)(DokumentenErstellenView.as_view(datenmanagement_model=model_name)),
      name=model_name + '_d3_add_file',
    )
  )

  # form page for editing files if a d3 process
  urlpatterns.append(
    path(
      model_name + '/<str:pk>/process/<int:vorgang_id>/file/change/<str:file_id>',
      view=datenmodel_permission_required(model_name_lower)(DokumentenBearbeitenView.as_view(datenmanagement_model=model_name)),
      name=model_name + '_change_file',
    )
  )

  urlpatterns.append(
      path(
        model_name + '/<str:pk>/process/list',
        view=permission_required('datenmanagement.view_' + model_name_lower)(
              TableProcessView.as_view(model=model)
        ),
        name=model_name + '_fetch_process_list',
      )
    )

  urlpatterns.append(
    path(
      model_name + '/metadata/list',
      view=permission_required('datenmanagement.view_' + model_name_lower)(
        FetchMetaDataRequestView.as_view()
      ),
      name=model_name + '_fetch_metadata',
    )
  )


