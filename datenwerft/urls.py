from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin import site as admin_site
from django.urls import include, path

from datenmanagement import urls as datenmanagement_urls
from gdihrocodelists import urls as gdihrocodelists_urls
from gdihrometadata import urls as gdihrometadata_urls

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

# routing...
urlpatterns = [
  # ...Django administration
  path(route='admin/', view=admin_site.urls),
  # ...Django API for Datenmanagement app
  path(
    route='api/datenmanagement/',
    view=include(datenmanagement_urls.api_urlpatterns),
  ),
  # ...Django API for GDI.HRO Codelists app
  path(
    route='api/gdihrocodelists/',
    view=include(gdihrocodelists_urls.api_urlpatterns),
  ),
  # ...Django API for GDI.HRO Metadata app
  path(
    route='api/gdihrometadata/',
    view=include(gdihrometadata_urls.api_urlpatterns),
  ),
  # ...Django API auth
  path(route='api-auth/', view=include('rest_framework.urls')),
  # ...Accounts app
  path(route='accounts/', view=include('accounts.urls')),
  # ...Toolbox app
  path(route='toolbox/', view=include('toolbox.urls')),
# ...d3 app
  path(route='d3/', view=include('d3.urls')),
  # ...Datenmanagement app
  path(route='datenmanagement/', view=include('datenmanagement.urls')),
  # ...Antragsmanagement app
  path(route='antragsmanagement/', view=include('antragsmanagement.urls')),
  # ...BEMAS app
  path(route='bemas/', view=include('bemas.urls')),
  # ...FMM app
  path(route='fmm/', view=include('fmm.urls')),
  # ...GDI.HRO Codelists app
  path(route='gdihrocodelists/', view=include('gdihrocodelists.urls')),
  # ...GDI.HRO Metadata app
  path(route='gdihrometadata/', view=include('gdihrometadata.urls')),
  # ...Django-RQ
  path(route='django-rq/', view=include('django_rq.urls')),
  # ...main page
  path(route='', view=IndexView.as_view(), name='index'),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
