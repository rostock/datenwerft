import re

from django.apps import apps
from django.contrib.auth.decorators import login_required, \
    user_passes_test
from django.urls import re_path, reverse_lazy
from rest_framework import routers

from datenmanagement.views import form_views, functions, \
    helper_views, index_start_views, list_map_views, api


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
    return user_passes_test(lambda u: any(u.has_perm(perm) for perm in perms))


app_name = 'datenmanagement'
urlpatterns = [
    # IndexView
    # Liste der Datenthemen, die zur Verfügung stehen
    re_path(route=r'^$',
        view=index_start_views.IndexView.as_view(),
        name='index'),
    # OWSProxyView
    # Proxy für OGC Web Services (OWS)
    re_path(route=r'owsproxy',
        view=login_required(helper_views.OWSProxyView.as_view()),
        name='owsproxy'),
    # AddressSearchView
    # Adressen-/Straßensuche
    re_path(route=r'addresssearch$',
        view=login_required(helper_views.AddressSearchView.as_view()),
        name='addresssearch'),
    # ReverseSearchView
    # Suche nach Objekten in bestimmtem Radius um gegebene Koordinaten
    re_path(route=r'reversesearch$',
        view=login_required(helper_views.ReverseSearchView.as_view()),
        name='reversesearch'),
    # GPXtoGeoJSON
    # Übergabe einer GPX-Datei an FME Server
    # und Rückgabe des generierten GeoJSON
    re_path(
        route=r'gpxtogeojson/$',
        view=login_required()(helper_views.GPXtoGeoJSON.as_view()),
        name='gpxtogeojson'),
]

# Erzeuge Views für jedes Datenmodell
app_models = apps.get_app_config(app_name).get_models()
for model in app_models:
    model_name = model.__name__
    model_name_lower = model_name.lower()
    regex = r'^' + re.escape(model_name) + r'/'

    # StartView
    # Startansicht eines Datenthemas
    urlpatterns.append(re_path(
        route=regex + r'$',
        view=permission_required(
            'datenmanagement.add_' + model_name_lower,
            'datenmanagement.change_' + model_name_lower,
            'datenmanagement.delete_' + model_name_lower,
            'datenmanagement.view_' + model_name_lower
        )(index_start_views.StartView.as_view(
            model=model,
            template_name='datenmanagement/start.html'
        )),
        name=model_name + 'start'
    ))

    # DataView
    # bereitet Datenbankobjekte für Tabellenansicht auf
    urlpatterns.append(re_path(
        route=regex + r'data/$',
        view=login_required(list_map_views.DataView.as_view(
            model=model
        )),
        name=model_name + 'data'
    ))

    # DataListView
    # listet alle Datenbankobjekte eines Datensatzes in einer Tabelle auf
    urlpatterns.append(re_path(
        route=regex + r'list/$',
        view=permission_required(
            'datenmanagement.change_' + model_name_lower,
            'datenmanagement.delete_' + model_name_lower,
            'datenmanagement.view_' + model_name_lower
        )(list_map_views.DataListView.as_view(
            model=model,
            template_name='datenmanagement/list.html'
        )),
        name=model_name + 'list'
    ))

    # DataMapView
    # bereitet Datenbankobjekte für Tabellenansicht auf
    urlpatterns.append(re_path(
        route=regex + r'mapdata/$',
        view=login_required(list_map_views.DataMapView.as_view(
            model=model
        )),
        name=model_name + 'mapdata'
    ))

    # DataMapListView
    # zeigt alle Datenbankobjekte eines Datensatzes auf einer Karte an
    urlpatterns.append(re_path(
        route=regex + r'map/$',
        view=permission_required(
            'datenmanagement.change_' + model_name_lower,
            'datenmanagement.delete_' + model_name_lower,
            'datenmanagement.view_' + model_name_lower
        )(list_map_views.DataMapListView.as_view(
            model=model,
            template_name='datenmanagement/map.html'
        )),
        name=model_name + 'map'
    ))

    # DataAddView
    # erstellt ein neues Datenbankobjekt eines Datensatzes
    urlpatterns.append(re_path(
        route=regex + r'add/$',
        view=permission_required(
            'datenmanagement.add_' + model_name_lower
        )(form_views.DataAddView.as_view(
            model=model,
            template_name='datenmanagement/form.html',
            success_url=reverse_lazy('datenmanagement:' + model_name + 'start')
        )),
        name=model_name + 'add'
    ))

    # DataChangeView
    # ändert ein vorhandenes Datenbankobjekt eines Datensatzes
    urlpatterns.append(re_path(
        route=regex + r'change/(?P<pk>.*)/$',
        view=permission_required(
            'datenmanagement.change_' + model_name_lower,
            'datenmanagement.delete_' + model_name_lower,
            'datenmanagement.view_' + model_name_lower
        )(form_views.DataChangeView.as_view(
            model=model,
            template_name='datenmanagement/form.html',
            success_url=reverse_lazy('datenmanagement:' + model_name + 'start')
        )),
        name=model_name + 'change'
    ))

    # DataDeleteView
    # löscht ein vorhandenes Datenbankobjekt eines Datensatzes
    urlpatterns.append(re_path(
        route=regex + r'delete/(?P<pk>.*)/$',
        view=permission_required(
            'datenmanagement.delete_' + model_name_lower
        )(form_views.DataDeleteView.as_view(
            model=model,
            template_name='datenmanagement/delete.html',
            success_url=reverse_lazy('datenmanagement:' + model_name + 'start')
        )),
        name=model_name + 'delete'
    ))

    # löscht ein Objekt aus der Datenbank
    urlpatterns.append(re_path(
        route=regex + r'deleteimmediately/(?P<pk>.*)/$',
        view=permission_required(
            'datenmanagement.delete_' + model_name_lower
        )(functions.delete_object_immediately),
        name=model_name + 'deleteimmediately'
    ))

    # GeometryView
    # Abfrage von Geometrien bestimmter Modelle
    urlpatterns.append(re_path(
        route=regex + r'geometry/',
        view=login_required(helper_views.GeometryView.as_view(model=model)),
        name=model_name + 'geometry'
    ))
