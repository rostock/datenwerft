from django.conf import settings
from django.conf.urls.static import static
from django.contrib.admin import site as admin_site
from django.urls import include, path
from django.views.generic.base import TemplateView

from accounts import urls as accounts_urls
from toolbox import urls as toolbox_urls
from datenmanagement import urls as datenmanagement_urls
from bemas import urls as bemas_urls

api_urlpatterns = []
api_urlpatterns += accounts_urls.api_urlpatterns
api_urlpatterns += toolbox_urls.api_urlpatterns
api_urlpatterns += datenmanagement_urls.api_urlpatterns
api_urlpatterns += bemas_urls.api_urlpatterns


# routing...
urlpatterns = [
  # ...Django administration
  path('admin/', view=admin_site.urls),

  # ...API
  path('api/', include(api_urlpatterns)),

  # ...API auth
  path('api-auth/', view=include('rest_framework.urls')),

  # ...App Accounts
  path('accounts/', view=include('accounts.urls')),

  # ...App Toolbox
  path('toolbox/', view=include('toolbox.urls')),

  # ...App Datenmanagement
  path('datenmanagement/', view=include('datenmanagement.urls')),

  # ...App BEMAS
  path('bemas/', view=include('bemas.urls')),

  # ...main page
  path('', view=TemplateView.as_view(template_name='index.html'), name='index')
]

if settings.DEBUG:
  urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
