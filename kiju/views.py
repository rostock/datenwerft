from datetime import datetime

from django.views.generic import TemplateView

from .models.main_models import Ferienangebot


class IndexView(TemplateView):
  """
  View for the index page of KiJu.
  """

  template_name = 'kiju/index.html'

  def get_context_data(self, **kwargs):
    """
    returns a dictionary containing the context data for the index page.
    """
    context = super().get_context_data(**kwargs)
    # hole die 5 nächsten anstehenden Angebote. nutze das das feld "time"
    context['next_activities'] = Ferienangebot.objects.filter(time__gte=datetime.now()).order_by(
      'time'
    )[:5]
    return context
