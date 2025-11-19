import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from ..models.services import HolidayService


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
    # hole die 5 nächsten anstehenden Angebote. nutze das das feld "time"
    context['next_activities'] = HolidayService.objects.filter(time__gte=datetime.now()).order_by(
      'time'
    )[:5]
    context['dashboard_layout'] = self.request.session.get('dashboard_layout', [])
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
    layout = data.get('layout', [])
    request.session['dashboard_layout'] = layout
    return JsonResponse({'status': 'success'})
  except Exception as e:
    return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
