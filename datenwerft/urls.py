from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path, path

from datenmanagement import urls as datenmanagement_urls
from accounts import urls as accounts_urls

api_urlpatterns = []
api_urlpatterns += accounts_urls.api_urlpatterns
api_urlpatterns += datenmanagement_urls.api_urlpatterns


# Routen der URLs zu Views
urlpatterns = [
    # '' oder '/' -> Redirect auf 'datenmanagement'
    # re_path(route=r'^(\/?)$',
    #         view=RedirectView.as_view(url='datenmanagement')),

    # 'admin/' -> Django Adminpanel
    re_path(route=r'^admin/',
            view=admin.site.urls),

    re_path('accounts/', include(accounts_urls.urlpatterns)),

    # Routen von Api URLs
    path('api/', include(api_urlpatterns)),

    # Routen der Api Authentifizierung
    re_path(route=r'^api-auth/',
            view=include('rest_framework.urls')),

    #'datenmanagement' -> Datenmanagement App
    re_path(route=r'^datenmanagement/',
        view=include(datenmanagement_urls.urlpatterns))
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
