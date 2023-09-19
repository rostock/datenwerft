from django.apps import apps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, reverse_lazy
from rest_framework.routers import DefaultRouter

from .views.api import DatenmanagementViewSet
from .views.functions import delete_object_immediately
from .views.views_form import DataAddView, DataChangeView, DataDeleteView
from .views.views_helpers import GeometryView, GISFiletoGeoJSON
from .views.views_index_start import IndexView, StartView
from .views.views_list_map import DataListView, DataMapListView, DataMapView, DataView


router = DefaultRouter()
app_models = apps.get_app_config('datenmanagement').get_models()
for model in app_models:
    model_name = model.__name__.lower()
    router.register(
        model_name,
        DatenmanagementViewSet.create_custom(model=model),
        basename=model_name
    )
api_urlpatterns = router.urls


def permission_required(*perms):
  """
  checks passed authorization(s)

  :param perms: authorization(s)
  :return: check of passed authorization(s)
  """
  return user_passes_test(lambda u: any(u.has_perm(perm) for perm in perms))


app_name = 'datenmanagement'

#
# general views
#

urlpatterns = [
  # main page
  path(
    '',
    view=login_required(IndexView.as_view()),
    name='index'
  ),
  # passes a file to FME Server and returns the generated GeoJSON
  path(
    'gisfiletogeojson',
    view=login_required(GISFiletoGeoJSON.as_view()),
    name='gisfiletogeojson'
  )
]

#
# views for each model
#

app_models = apps.get_app_config(app_name).get_models()
for model in app_models:
  model_name = model.__name__
  model_name_lower = model_name.lower()

  # entry page of a model
  urlpatterns.append(
    path(
      model_name,
      view=permission_required(
        'datenmanagement.add_' + model_name_lower,
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(StartView.as_view(
        model=model,
        template_name='datenmanagement/start.html'
      )),
      name=model_name + '_start'
    )
  )

  # table data composition of a model
  urlpatterns.append(
    path(
      model_name + '/data',
      view=permission_required(
        'datenmanagement.view_' + model_name_lower
      )(DataView.as_view(model=model)),
      name=model_name + '_data'
    )
  )

  # table data composition of a model:
  # filter by subset
  urlpatterns.append(
    path(
      model_name + '/data/subset/<subset_id>',
      view=permission_required(
        'datenmanagement.view_' + model_name_lower
      )(DataView.as_view(model=model)),
      name=model_name + '_data_subset'
    )
  )

  # table page of a model
  urlpatterns.append(
    path(
      model_name + '/list',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(DataListView.as_view(
        model=model,
        template_name='datenmanagement/list.html'
      )),
      name=model_name + '_list'
    )
  )

  # table page of a model:
  # filter by subset
  urlpatterns.append(
    path(
      model_name + '/list/subset/<subset_id>',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(DataListView.as_view(
        model=model,
        template_name='datenmanagement/list.html'
      )),
      name=model_name + '_list_subset'
    )
  )

  # map data composition of a model
  urlpatterns.append(
    path(
      model_name + '/mapdata',
      view=permission_required(
        'datenmanagement.view_' + model_name_lower
      )(DataMapView.as_view(model=model)),
      name=model_name + '_mapdata'
    )
  )

  # map data composition of a model:
  # filter by subset
  urlpatterns.append(
    path(
      model_name + '/mapdata/subset/<subset_id>',
      view=permission_required(
        'datenmanagement.view_' + model_name_lower
      )(DataMapView.as_view(model=model)),
      name=model_name + '_mapdata_subset'
    )
  )

  # map page of a model
  urlpatterns.append(
    path(
      model_name + '/map',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(DataMapListView.as_view(
        model=model,
        template_name='datenmanagement/map.html'
      )),
      name=model_name + '_map'
    )
  )

  # map page of a model:
  # filter by subset
  urlpatterns.append(
    path(
      model_name + '/map/subset/<subset_id>',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(DataMapListView.as_view(
        model=model,
        template_name='datenmanagement/map.html'
      )),
      name=model_name + '_map_subset'
    )
  )

  # form page for creating an object of a model
  urlpatterns.append(
    path(
      model_name + '/add',
      view=permission_required(
        'datenmanagement.add_' + model_name_lower
      )(DataAddView.as_view(
        model=model,
        template_name='datenmanagement/form.html',
        success_url=reverse_lazy('datenmanagement:' + model_name + '_start')
      )),
      name=model_name + '_add'
    )
  )

  # form page for updating an object of a model
  urlpatterns.append(
    path(
      model_name + '/change/<pk>',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(DataChangeView.as_view(
        model=model,
        template_name='datenmanagement/form.html',
        success_url=reverse_lazy('datenmanagement:' + model_name + '_start')
      )),
      name=model_name + '_change'
    )
  )

  # form page for deleting an object of a model
  urlpatterns.append(
    path(
      model_name + '/delete/<pk>',
      view=permission_required(
        'datenmanagement.delete_' + model_name_lower
      )(DataDeleteView.as_view(
        model=model,
        template_name='datenmanagement/delete.html',
        success_url=reverse_lazy('datenmanagement:' + model_name + '_start')
      )),
      name=model_name + '_delete'
    )
  )

  # deletes an object of a model directly from the database
  urlpatterns.append(
    path(
      model_name + '/deleteimmediately/<pk>',
      view=permission_required(
        'datenmanagement.delete_' + model_name_lower
      )(delete_object_immediately),
      name=model_name + '_deleteimmediately'
    )
  )

  # queries the geometries of a model
  urlpatterns.append(
    path(
      model_name + '/geometry',
      view=permission_required(
        'datenmanagement.view_' + model_name_lower
      )(GeometryView.as_view(model=model)),
      name=model_name + '_geometry'
    )
  )
