import re

from django.apps import apps
from django.conf.urls import url
from django.contrib.auth.decorators import login_required, \
    user_passes_test
from django.urls import reverse_lazy

from .views import dataform_views, datalist_views, functions, \
    helper_views, list_views



def permission_required(*perms):
    return user_passes_test(lambda u: any(u.has_perm(perm) for perm in perms))


app_name = 'datenmanagement'
urlpatterns = [
    # IndexView
    url(regex=r'^$',
        view=list_views.IndexView.as_view(),
        name='index'),
    # OWSProxyView
    url(regex=r'owsproxy',
        view=login_required(helper_views.OWSProxyView.as_view()),
        name='owsproxy'),
    # AddressSearchView
    url(regex=r'addresssearch$',
        view=login_required(helper_views.AddressSearchView.as_view()),
        name='addresssearch'),
    # ReverseSearchView
    url(regex=r'reversesearch$',
        view=login_required(helper_views.ReverseSearchView.as_view()),
        name='reversesearch'),
    # GPXtoGeoJSON
    url(
        regex=r'gpxtogeojson/$',
        view=login_required()(helper_views.GPXtoGeoJSON.as_view()),
        name='gpxtogeojson'),
]

# Erzeuge Views für jedes Model
app_models = apps.get_app_config(app_name).get_models()
for model in app_models:
    model_name = model.__name__
    model_name_lower = model_name.lower()
    regex = r'^' + re.escape(model_name) + r'/'

    # StartView (Auswahl der Möglichkeiten nach Kategorie-Auswahl)
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

    # DataView (BaseDatatableView)
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

    # DataListView (ListView)
    # Liste eines Datenthemas anzeigen
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

    # DataMapView (ListView)
    # Informationen zu Datenthema auf Karte anzeigen
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

    # DataAddView (CreateView)
    # Formular um neuen Datensatz hinzuzufügen
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

    # DataChangeView (UpdateView)
    # Formular um Datensatz zu bearbeiten
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

    # DeleteView
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

    #
    urlpatterns.append(url(
        regex=regex + r'deleteimmediately/(?P<pk>.*)/$',
        view=permission_required(
            'datenmanagement.delete_' + model_name_lower
        )(functions.delete_object_immediately),
        name=model_name + 'deleteimmediately'
    ))

    urlpatterns.append(url(
        regex=regex + r'geometry/',
        view=login_required(helper_views.GeometryView.as_view(model=model)),
        name=model_name + 'geometry'
    ))
