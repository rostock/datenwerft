import re

from django.apps import apps
from django.conf.urls import url
from django.contrib.auth.decorators import login_required, \
    user_passes_test
from django.urls import reverse_lazy

from datenmanagement.views import dataform_views, datalist_views, \
    functions, helper_views, list_views



def permission_required(*perms):
    return user_passes_test(lambda u: any(u.has_perm(perm) for perm in perms))


app_name = 'datenmanagement'
urlpatterns = [
    # IndexView
    # Liste der Datenthemen, die zur Verfügung stehen
    url(regex=r'^$',
        view=list_views.IndexView.as_view(),
        name='index'),
    # OWSProxyView
    # Proxy für OGC Web Services (OWS)
    url(regex=r'owsproxy',
        view=login_required(helper_views.OWSProxyView.as_view()),
        name='owsproxy'),
    # AddressSearchView
    # Adressen-/Straßensuche
    url(regex=r'addresssearch$',
        view=login_required(helper_views.AddressSearchView.as_view()),
        name='addresssearch'),
    # ReverseSearchView
    # Suche nach Objekten in bestimmtem Radius um gegebene Koordinaten
    url(regex=r'reversesearch$',
        view=login_required(helper_views.ReverseSearchView.as_view()),
        name='reversesearch'),
    # GPXtoGeoJSON
    # Übergabe einer GPX-Datei an FME Server und Rückgabe des generierten GeoJSON
    url(
        regex=r'gpxtogeojson/$',
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
    urlpatterns.append(url(
        regex=regex + r'$',
        view=permission_required(
            'datenmanagement.add_' + model_name_lower,
            'datenmanagement.change_' + model_name_lower,
            'datenmanagement.delete_' + model_name_lower,
            'datenmanagement.view_' + model_name_lower
        )(list_views.StartView.as_view(
            model=model,
            template_name='datenmanagement/start.html'
        )),
        name=model_name + 'start'
    ))

    # DataView
    # bereitet Datenbankobjekte für Tabellenansicht auf
    urlpatterns.append(url(
        regex=regex + r'data/$',
        view=permission_required(
            'datenmanagement.change_' + model_name_lower,
            'datenmanagement.delete_' + model_name_lower,
            'datenmanagement.view_' + model_name_lower
        )(datalist_views.DataView.as_view(
            model=model
        )),
        name=model_name + 'data'
    ))

    # DataListView
    # listet alle Datenbankobjekte eines Datensatzes in einer Tabelle auf
    urlpatterns.append(url(
        regex=regex + r'list/$',
        view=permission_required(
            'datenmanagement.change_' + model_name_lower,
            'datenmanagement.delete_' + model_name_lower,
            'datenmanagement.view_' + model_name_lower
        )(datalist_views.DataListView.as_view(
            model=model,
            template_name='datenmanagement/datalist.html'
        )),
        name=model_name + 'list'
    ))

    # DataMapView
    # zeigt alle Datenbankobjekte eines Datensatzes auf einer Karte an
    urlpatterns.append(url(
        regex=regex + r'map/$',
        view=permission_required(
            'datenmanagement.change_' + model_name_lower,
            'datenmanagement.delete_' + model_name_lower,
            'datenmanagement.view_' + model_name_lower
        )(datalist_views.DataMapView.as_view(
            model=model,
            template_name='datenmanagement/datamap.html'
        )),
        name=model_name + 'map'
    ))

    # DataAddView
    # erstellt ein neues Datenbankobjekt eines Datensatzes
    urlpatterns.append(url(
        regex=regex + r'add/$',
        view=permission_required(
            'datenmanagement.add_' + model_name_lower
        )(dataform_views.DataAddView.as_view(
            model=model,
            template_name='datenmanagement/dataform.html',
            success_url=reverse_lazy('datenmanagement:' + model_name + 'start')
        )),
        name=model_name + 'add'
    ))

    # DataChangeView
    # ändert ein vorhandenes Datenbankobjekt eines Datensatzes
    urlpatterns.append(url(
        regex=regex + r'change/(?P<pk>.*)/$',
        view=permission_required(
            'datenmanagement.change_' + model_name_lower,
            'datenmanagement.delete_' + model_name_lower,
            'datenmanagement.view_' + model_name_lower
        )(dataform_views.DataChangeView.as_view(
            model=model,
            template_name='datenmanagement/dataform.html',
            success_url=reverse_lazy('datenmanagement:' + model_name + 'start')
        )),
        name=model_name + 'change'
    ))

    # DataDeleteView
    # löscht ein vorhandenes Datenbankobjekt eines Datensatzes
    urlpatterns.append(url(
        regex=regex + r'delete/(?P<pk>.*)/$',
        view=permission_required(
            'datenmanagement.delete_' + model_name_lower
        )(dataform_views.DataDeleteView.as_view(
            model=model,
            template_name='datenmanagement/datadelete.html',
            success_url=reverse_lazy('datenmanagement:' + model_name + 'start')
        )),
        name=model_name + 'delete'
    ))

    # löscht ein Objekt aus der Datenbank
    urlpatterns.append(url(
        regex=regex + r'deleteimmediately/(?P<pk>.*)/$',
        view=permission_required(
            'datenmanagement.delete_' + model_name_lower
        )(functions.delete_object_immediately),
        name=model_name + 'deleteimmediately'
    ))

    # GeometryView
    # Abfrage von Geometrien bestimmter Modelle
    urlpatterns.append(url(
        regex=regex + r'geometry/',
        view=login_required(helper_views.GeometryView.as_view(model=model)),
        name=model_name + 'geometry'
    ))
