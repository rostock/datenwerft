import json
import logging

from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from ..dashboard import DASHBOARD_CONTAINERS
from ..models.services import Service
from ..utils import get_inbox_count
from .functions import add_permission_context_elements

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
    context = add_permission_context_elements(context, self.request.user)
    context['dashboard_layout'] = self.request.session.get('dashboard_layout', [])
    context['inbox_count'] = get_inbox_count(self.request.user)
    context['LEAFLET_CONFIG'] = settings.LEAFLET_CONFIG
    context['mapdata_url'] = reverse('kiju:services_mapdata')

    total = 0
    tiles = []
    containers = {}  # Schlüssel -> {'config': ..., 'buttons': []}

    for model in apps.get_app_config('kiju').get_models():
      if model._meta.abstract:
        continue
      if issubclass(model, Service):
        total += (
          model.objects.filter(status='published').exclude(geometry__equals='POINT(0 0)').count()
        )
      mode = getattr(model, 'dashboard_mode', None)
      if mode == 'tile':
        tiles.append(
          {
            'type': 'tile',
            'model_name': model.__name__.lower(),
            'verbose_name': model._meta.verbose_name_plural,
            'icon': getattr(model, 'icon', ''),
            'color': getattr(model, 'dashboard_color', 'primary'),
            'admin_only': getattr(model, 'dashboard_admin_only', False),
          }
        )
      elif mode == 'container_button':
        container_key = getattr(model, 'dashboard_container', '')
        if container_key not in containers:
          config = DASHBOARD_CONTAINERS.get(container_key, {})
          containers[container_key] = {'config': config, 'buttons': []}
          tiles.append({'type': '_placeholder', 'key': container_key})
        containers[container_key]['buttons'].append(
          {
            'model_name': model.__name__.lower(),
            'verbose_name': model._meta.verbose_name_plural,
            'icon': getattr(model, 'icon', ''),
          }
        )

    context['published_services_count'] = total
    context['dashboard_tiles'] = [
      {
        'type': 'container',
        'key': t['key'],
        'title': containers[t['key']]['config'].get('verbose_name', t['key']),
        'icon': containers[t['key']]['config'].get('icon', ''),
        'color': containers[t['key']]['config'].get('color', 'primary'),
        'admin_only': containers[t['key']]['config'].get('admin_only', False),
        'buttons': containers[t['key']]['buttons'],
      }
      if t['type'] == '_placeholder'
      else t
      for t in tiles
    ]

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
