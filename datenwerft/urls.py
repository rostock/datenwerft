from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin import site as admin_site
from django.urls import include, path

from accounts import urls as accounts_urls
from antragsmanagement import urls as antragsmanagement_urls
from bemas import urls as bemas_urls
from datenmanagement import urls as datenmanagement_urls
from gdihrometadata import urls as gdihrometadata_urls
from toolbox import urls as toolbox_urls
from .views import (
  IndexView,
  error_400,
  error_403,
  error_404,
  error_405,
  error_410,
  error_500,
  error_501,
  error_502,
  error_503,
)

handler400 = error_400
handler403 = error_403
handler404 = error_404
handler405 = error_405
handler410 = error_410
handler500 = error_500
handler501 = error_501
handler502 = error_502
handler503 = error_503

api_urlpatterns = []
api_urlpatterns += accounts_urls.api_urlpatterns
api_urlpatterns += toolbox_urls.api_urlpatterns
api_urlpatterns += datenmanagement_urls.api_urlpatterns
api_urlpatterns += antragsmanagement_urls.api_urlpatterns
api_urlpatterns += bemas_urls.api_urlpatterns
api_urlpatterns += gdihrometadata_urls.api_urlpatterns

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
# ...d3 app
  path('d3/', view=include('d3.urls')),
  # ...Datenmanagement app
  path('datenmanagement/', view=include('datenmanagement.urls')),
  # ...Antragsmanagement app
  path('antragsmanagement/', view=include('antragsmanagement.urls')),
  # ...BEMAS app
  path('bemas/', view=include('bemas.urls')),
  # ...GDI.HRO Metadata app
  path('gdihrometadata/', view=include('gdihrometadata.urls')),
  # ...Django-RQ
  path('django-rq/', view=include('django_rq.urls')),
  # ...main page
  path('', view=IndexView.as_view(), name='index'),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
