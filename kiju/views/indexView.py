import json
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from ..models.services import PreventionService

logger = logging.getLogger(__name__)


class IndexView(TemplateView):
  """
  View for the index page of KiJu.
  """

  template_name = 'kiju/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary containing the context data for the index page.
    Also retrieves the dashboard layout from the session.
    """
    context = super().get_context_data(**kwargs)
    context['dashboard_layout'] = self.request.session.get('dashboard_layout', [])

    # Leaflet configuration for the dashboard map
    context['LEAFLET_CONFIG'] = getattr(
      settings,
      'LEAFLET_CONFIG',
      {
        'DEFAULT_CENTER': (54.14775, 12.14945),
        'DEFAULT_ZOOM': 11,
        'MIN_ZOOM': 11,
        'MAX_ZOOM': 19,
      },
    )

    # Map data URL for PreventionService
    context['mapdata_url'] = reverse('kiju:preventionservice_mapdata')

    # Count of objects for the map
    context['preventionservice_count'] = (
      PreventionService.objects.filter(geometry__isnull=False)
      .exclude(geometry__equals='POINT(0 0)')
      .count()
    )

    return context


@login_required
@require_POST
def save_dashboard_layout(request):
  """
  Saves the dashboard layout order to the user's session.
  Expects a JSON body with a 'layout' key containing a list of item IDs.
  """
  try:
    data = json.loads(request.body)
    logger.info(f'Saving dashboard layout for user {request.user}: {data}')
    request.session['dashboard_layout'] = data
    request.session.modified = True
    return JsonResponse({'status': 'success'})
  except Exception as e:
    logger.error(f'Error saving dashboard layout: {e}')
    return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
