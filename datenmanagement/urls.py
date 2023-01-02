from django.apps import apps
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import path, reverse_lazy
from rest_framework import routers

from datenmanagement.views import functions, views_form, views_helpers, \
  views_index_start, views_list_map, api


router = routers.DefaultRouter()
app_models = apps.get_app_config('datenmanagement').get_models()
for model in app_models:
    model_name = model.__name__.lower()
    router.register(
        model_name,
        api.DatenmanagementViewSet.create_custom(model=model),
        basename=model_name
    )
api_urlpatterns = router.urls


def permission_required(*perms):
  """
  prüft Berechtigung(en)

  :param perms: Berechtigung(en)
  :return: Prüfung der Berechtigung(en)
  """
  return user_passes_test(lambda u: any(u.has_perm(perm) for perm in perms))


app_name = 'datenmanagement'

# generelle Views
urlpatterns = [
  # IndexView:
  # Liste der Datenthemen, die zur Verfügung stehen
  path(
    '',
    view=views_index_start.IndexView.as_view(),
    name='index'
  ),
  # GPXtoGeoJSON:
  # Übergabe einer GPX-Datei an FME Server und Rückgabe des generierten GeoJSON
  path(
    'gpxtogeojson',
    view=login_required()(views_helpers.GPXtoGeoJSON.as_view()),
    name='gpxtogeojson'
  )
]

# erzeuge Views für jedes Datenmodell
app_models = apps.get_app_config(app_name).get_models()
for model in app_models:
  model_name = model.__name__
  model_name_lower = model_name.lower()

  # StartView:
  # Startansicht eines Datenmodells
  urlpatterns.append(
    path(
      model_name,
      view=permission_required(
        'datenmanagement.add_' + model_name_lower,
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(views_index_start.StartView.as_view(
        model=model,
        template_name='datenmanagement/start.html'
      )),
      name=model_name + '_start'
    )
  )

  # DataView:
  # bereitet Datenbankobjekte für Tabellenansicht auf
  urlpatterns.append(
    path(
      model_name + '/data',
      view=login_required(views_list_map.DataView.as_view(model=model)),
      name=model_name + '_data'
    )
  )
  urlpatterns.append(
    path(
      model_name + '/data/subset/<subset_id>',
      view=login_required(views_list_map.DataView.as_view(model=model)),
      name=model_name + '_data_subset'
    )
  )

  # DataListView:
  # listet alle Datenbankobjekte eines Datenmodells in einer Tabelle auf
  urlpatterns.append(
    path(
      model_name + '/list',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(views_list_map.DataListView.as_view(
        model=model,
        template_name='datenmanagement/list.html'
      )),
      name=model_name + '_list'
    )
  )
  urlpatterns.append(
    path(
      model_name + '/list/subset/<subset_id>',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(views_list_map.DataListView.as_view(
        model=model,
        template_name='datenmanagement/list.html'
      )),
      name=model_name + '_list_subset'
    )
  )

  # DataMapView:
  # bereitet Datenbankobjekte für Tabellenansicht auf
  urlpatterns.append(
    path(
      model_name + '/mapdata',
      view=login_required(views_list_map.DataMapView.as_view(model=model)),
      name=model_name + '_mapdata'
    )
  )
  urlpatterns.append(
    path(
      model_name + '/mapdata/subset/<subset_id>',
      view=login_required(views_list_map.DataMapView.as_view(model=model)),
      name=model_name + '_mapdata_subset'
    )
  )

  # DataMapListView:
  # zeigt alle Datenbankobjekte eines Datenmodells auf einer Karte an
  urlpatterns.append(
    path(
      model_name + '/map',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(views_list_map.DataMapListView.as_view(
        model=model,
        template_name='datenmanagement/map.html'
      )),
      name=model_name + '_map'
    )
  )
  urlpatterns.append(
    path(
      model_name + '/map/subset/<subset_id>',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(views_list_map.DataMapListView.as_view(
        model=model,
        template_name='datenmanagement/map.html'
      )),
      name=model_name + '_map_subset'
    )
  )

  # DataAddView:
  # erstellt ein neues Datenbankobjekt eines Datenmodells
  urlpatterns.append(
    path(
      model_name + '/add',
      view=permission_required(
        'datenmanagement.add_' + model_name_lower
      )(views_form.DataAddView.as_view(
        model=model,
        template_name='datenmanagement/form.html',
        success_url=reverse_lazy('datenmanagement:' + model_name + '_start')
      )),
      name=model_name + '_add'
    )
  )

  # DataChangeView:
  # ändert ein vorhandenes Datenbankobjekt eines Datenmodells
  urlpatterns.append(
    path(
      model_name + '/change/<pk>',
      view=permission_required(
        'datenmanagement.change_' + model_name_lower,
        'datenmanagement.delete_' + model_name_lower,
        'datenmanagement.view_' + model_name_lower
      )(views_form.DataChangeView.as_view(
        model=model,
        template_name='datenmanagement/form.html',
        success_url=reverse_lazy('datenmanagement:' + model_name + '_start')
      )),
      name=model_name + '_change'
    )
  )

  # DataDeleteView:
  # löscht ein vorhandenes Datenbankobjekt eines Datenmodells
  urlpatterns.append(
    path(
      model_name + '/delete/<pk>',
      view=permission_required(
        'datenmanagement.delete_' + model_name_lower
      )(views_form.DataDeleteView.as_view(
        model=model,
        template_name='datenmanagement/delete.html',
        success_url=reverse_lazy('datenmanagement:' + model_name + '_start')
      )),
      name=model_name + '_delete'
    )
  )

  # löscht ein Datenbankobjekt eines Datenmodells direkt aus der Datenbank
  urlpatterns.append(
    path(
      model_name + '/deleteimmediately/<pk>',
      view=permission_required(
        'datenmanagement.delete_' + model_name_lower
      )(functions.delete_object_immediately),
      name=model_name + '_deleteimmediately'
    )
  )

  # GeometryView:
  # Abfrage der Geometrien eines Datenmodells
  urlpatterns.append(
    path(
      model_name + '/geometry',
      view=login_required(views_helpers.GeometryView.as_view(model=model)),
      name=model_name + '_geometry'
    )
  )
