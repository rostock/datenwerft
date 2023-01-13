from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin import site as admin_site
from django.urls import include, path

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
  path('admin/', view=admin_site.urls),

  # Routen der API-URLs
  path('api/', include(api_urlpatterns)),

  # Routen der API-Authentifizierung
  path('api-auth/', view=include('rest_framework.urls')),

  # Routen der App Accounts
  path('accounts/', view=include('accounts.urls')),

  # Routen der App Toolbox
  path('toolbox/', view=include('toolbox.urls')),

  # Routen der App Datenmanagement
  path('datenmanagement/', view=include('datenmanagement.urls'))
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
