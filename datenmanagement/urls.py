from django.apps import apps
from django.conf.urls import url
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from . import views
import re

def permission_required(*perms):
    return user_passes_test(lambda u: any(u.has_perm(perm) for perm in perms))

app_name = 'datenmanagement'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name = 'index'),
    url(r'owsproxy', login_required(views.OWSProxyView.as_view()), name = 'owsproxy'),
    url(r'addresssearch$', login_required(views.AddressSearchView.as_view()), name = 'addresssearch'),
    url(r'reversesearch$', login_required(views.ReverseSearchView.as_view()), name = 'reversesearch'),
]

app_models = apps.get_app_config(app_name).get_models()
for model in app_models:
    model_name = model.__name__
    model_name_lower = model_name.lower()
    regex = r'^' + re.escape(model_name) + r'/'
    urlpatterns.append(url(regex + r'$', permission_required('datenmanagement.add_' + model_name_lower,'datenmanagement.change_' + model_name_lower, 'datenmanagement.delete_' + model_name_lower, 'datenmanagement.view_' + model_name_lower)(views.StartView.as_view(model = model, template_name = 'datenmanagement/start.html')), name = model_name + 'start'))
    urlpatterns.append(url(regex + r'data/$', permission_required('datenmanagement.change_' + model_name_lower, 'datenmanagement.delete_' + model_name_lower, 'datenmanagement.view_' + model_name_lower)(views.DataView.as_view(model = model)), name = model_name + 'data'))
    urlpatterns.append(url(regex + r'list/$', permission_required('datenmanagement.change_' + model_name_lower, 'datenmanagement.delete_' + model_name_lower, 'datenmanagement.view_' + model_name_lower)(views.DataListView.as_view(model = model, template_name = 'datenmanagement/datalist.html')), name = model_name + 'list'))
    urlpatterns.append(url(regex + r'map/$', permission_required('datenmanagement.change_' + model_name_lower, 'datenmanagement.delete_' + model_name_lower, 'datenmanagement.view_' + model_name_lower)(views.DataMapView.as_view(model = model, template_name = 'datenmanagement/datamap.html')), name = model_name + 'map'))
    urlpatterns.append(url(regex + r'add/$', permission_required('datenmanagement.add_' + model_name_lower)(views.DataAddView.as_view(model = model, template_name = 'datenmanagement/dataform.html', success_url = reverse_lazy('datenmanagement:' + model_name + 'start'))), name = model_name + 'add'))
    urlpatterns.append(url(regex + r'change/(?P<pk>\d+)/$', permission_required('datenmanagement.change_' + model_name_lower, 'datenmanagement.delete_' + model_name_lower)(views.DataChangeView.as_view(model = model, template_name = 'datenmanagement/dataform.html', success_url = reverse_lazy('datenmanagement:' + model_name + 'start'))), name = model_name + 'change'))
    urlpatterns.append(url(regex + r'delete/(?P<pk>\d+)/$', permission_required('datenmanagement.delete_' + model_name_lower)(views.DataDeleteView.as_view(model = model, template_name = 'datenmanagement/datadelete.html', success_url = reverse_lazy('datenmanagement:' + model_name + 'start'))), name = model_name + 'delete'))
    urlpatterns.append(url(regex + r'deleteimmediately/(?P<pk>\d+)/$', permission_required('datenmanagement.delete_' + model_name_lower)(views.delete_object_immediately), name = model_name + 'deleteimmediately'))