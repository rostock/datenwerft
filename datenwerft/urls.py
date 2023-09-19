from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin import site as admin_site
from django.urls import include, path

from accounts import urls as accounts_urls
from toolbox import urls as toolbox_urls
from datenmanagement import urls as datenmanagement_urls
from bemas import urls as bemas_urls

from .views import IndexView

api_urlpatterns = []
api_urlpatterns += accounts_urls.api_urlpatterns
api_urlpatterns += toolbox_urls.api_urlpatterns
api_urlpatterns += datenmanagement_urls.api_urlpatterns
api_urlpatterns += bemas_urls.api_urlpatterns


# routing...
urlpatterns = [
  # ...Django administration
  path('admin/', view=admin_site.urls),

  # ...Django API
  path('api/', include(api_urlpatterns)),

  # ...Django API auth
  path('api-auth/', view=include('rest_framework.urls')),

  # ...Accounts app
  path('accounts/', view=include('accounts.urls')),

  # ...Toolbox app
  path('toolbox/', view=include('toolbox.urls')),

  # ...Datenmanagement app
  path('datenmanagement/', view=include('datenmanagement.urls')),

  # ...BEMAS app
  path('bemas/', view=include('bemas.urls')),

  # ...main page
  path('', view=IndexView.as_view(), name='index')
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
