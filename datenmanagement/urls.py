import re
from django.apps import apps
from django.conf.urls import url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from . import views



def permission_required(*perms):
    return user_passes_test(lambda u: any(u.has_perm(perm) for perm in perms))


app_name = 'datenmanagement'
urlpatterns = [
    # IndexView
    url(regex=r'^$',
        view=views.IndexView.as_view(),
        name='index'),
    # OWSProxyView
    url(regex=r'owsproxy',
        view=login_required(views.OWSProxyView.as_view()),
        name='owsproxy'),
    # AddressSearchView
    url(regex=r'addresssearch$',
        view=login_required(views.AddressSearchView.as_view()),
        name='addresssearch'),
    # ReverseSearchView
    url(regex=r'reversesearch$',
        view=login_required(views.ReverseSearchView.as_view()),
        name='reversesearch'),
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
        )(views.StartView.as_view(
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
        )(views.DataView.as_view(
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
        )(views.DataListView.as_view(
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
        )(views.DataMapView.as_view(
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
        )(views.DataAddView.as_view(
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
        )(views.DataChangeView.as_view(
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
        )(views.DataDeleteView.as_view(
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
        )(views.delete_object_immediately),
        name=model_name + 'deleteimmediately'
    ))

    urlpatterns.append(url(
        regex=regex + r'geometry/$',
        view=permission_required(
            'datenmanagement.view_' + model_name_lower
        )(views.GeometryView.as_view(
            model=model
        )),
        name=model_name + 'geometry'
    ))
