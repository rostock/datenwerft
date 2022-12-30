from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path, path

from accounts import urls as accounts_urls
from toolbox import urls as toolbox_urls
from datenmanagement import urls as datenmanagement_urls

api_urlpatterns = []
api_urlpatterns += accounts_urls.api_urlpatterns
api_urlpatterns += toolbox_urls.api_urlpatterns
api_urlpatterns += datenmanagement_urls.api_urlpatterns

# Routen der URLs zu Views
urlpatterns = [
  # Routen der Django-Administration
  re_path(route=r'^admin/',
          view=admin.site.urls),

  # Routen der API-URLs
  path('api/', include(api_urlpatterns)),

  # Routen der API-Authentifizierung
  re_path(route=r'^api-auth/',
          view=include('rest_framework.urls')),

  # Routen der App Accounts
  re_path(route=r'^accounts/',
          view=include('accounts.urls')),

  # Routen der App Toolbox
  re_path(route=r'^toolbox/',
          view=include('toolbox.urls')),

  # Routen der App Datenmanagement
  re_path(route=r'^datenmanagement/',
          view=include('datenmanagement.urls'))
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
