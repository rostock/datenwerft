from django.apps import apps
from django.conf.urls import url
from django.contrib.auth.decorators import permission_required
from django.core.urlresolvers import reverse_lazy
from . import views
import re


app_name = 'datenmanagement'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name = 'index'),
    url(r'addresssearch$', views.AddressSearchView.as_view(), name = 'addresssearch'),
    url(r'reversesearch$', views.ReverseSearchView.as_view(), name = 'reversesearch'),
]

app_models = apps.get_app_config(app_name).get_models()
for model in app_models:
    model_name = model.__name__
    regex = r'^' + re.escape(model_name) + r'/'
    urlpatterns.append(url(regex + r'$', views.StartView.as_view(model = model, template_name = 'datenmanagement/start.html'), name = model_name + 'start'))
    urlpatterns.append(url(regex + r'data/$', views.DataView.as_view(model = model), name = model_name + 'data'))
    urlpatterns.append(url(regex + r'list/$', permission_required('datenmanagement.change_' + model_name.lower())(views.DataListView.as_view(model = model, template_name = 'datenmanagement/datalist.html')), name = model_name + 'list'))
    urlpatterns.append(url(regex + r'map/$', permission_required('datenmanagement.change_' + model_name.lower())(views.DataMapView.as_view(model = model, template_name = 'datenmanagement/datamap.html')), name = model_name + 'map'))
    urlpatterns.append(url(regex + r'add/$', permission_required('datenmanagement.add_' + model_name.lower())(views.DataAddView.as_view(model = model, template_name = 'datenmanagement/dataform.html', success_url = reverse_lazy('datenmanagement:' + model_name + 'start'))), name = model_name + 'add'))
    urlpatterns.append(url(regex + r'change/(?P<pk>\d+)/$', views.DataChangeView.as_view(model = model, template_name = 'datenmanagement/dataform.html', success_url = reverse_lazy('datenmanagement:' + model_name + 'start')), name = model_name + 'change'))
    urlpatterns.append(url(regex + r'delete/(?P<pk>\d+)/$', views.DataDeleteView.as_view(model = model, template_name = 'datenmanagement/datadelete.html', success_url = reverse_lazy('datenmanagement:' + model_name + 'start')), name = model_name + 'delete'))
