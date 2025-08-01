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
  path('admin/', view=admin_site.urls),
  # ...Django API for Datenmanagement app
  path('api/datenmanagement/', include(datenmanagement_urls.api_urlpatterns)),
  # ...Django API for GDI.HRO Codelists app
  path('api/gdihrocodelists/', include(gdihrocodelists_urls.api_urlpatterns, namespace='gdihrocodelists')),
  # ...Django API for GDI.HRO Metadata app
  path('api/gdihrometadata/', include(gdihrometadata_urls.api_urlpatterns, namespace='gdihrometadata')),
  # ...Django API auth
  path('api-auth/', view=include('rest_framework.urls')),
  # ...Accounts app
  path('accounts/', view=include('accounts.urls')),
  # ...Toolbox app
  path('toolbox/', view=include('toolbox.urls')),
  # ...Datenmanagement app
  path('datenmanagement/', view=include('datenmanagement.urls')),
  # ...Antragsmanagement app
  path('antragsmanagement/', view=include('antragsmanagement.urls')),
  # ...BEMAS app
  path('bemas/', view=include('bemas.urls')),
  # ...FMM app
  path('fmm/', view=include('fmm.urls')),
  # ...GDI.HRO Codelists app
  path('gdihrocodelists/', view=include('gdihrocodelists.urls')),
  # ...GDI.HRO Metadata app
  path('gdihrometadata/', view=include('gdihrometadata.urls')),
  # ...Django-RQ
  path('django-rq/', view=include('django_rq.urls')),
  # ...main page
  path('', view=IndexView.as_view(), name='index'),
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
