import logging

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from ..utils import (
  get_inbox_messages,
  get_service_instance,
  is_angebotsdb_user,
)
from .functions import add_permission_context_elements

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class InboxListView(View):
  """
  Zeigt alle offenen InboxMessages des aktuellen Nutzers.

  - OrgUnit-Nutzer sehen Prüfaufträge (review_request)
  - Provider-Nutzer sehen Überarbeitungsaufträge (revision_request)
  - Admins und Superuser sehen alle offenen Nachrichten
  """

  template_name = 'kiju/inbox.html'

  def get(self, request):
    if not (is_angebotsdb_user(request.user) or request.user.is_superuser):
      context = add_permission_context_elements({}, request.user)
      return render(request, self.template_name, context)

    messages = get_inbox_messages(request.user)

    # Jede Nachricht mit aufgelösten Service-Informationen anreichern
    inbox_items = []
    for msg in messages:
      review_task = msg.review_task
      service = get_service_instance(review_task.service_type, review_task.service_id)

      # Lesbaren Angebotstyp-Namen ermitteln
      service_verbose_name = '–'
      if service is not None:
        service_verbose_name = service._meta.verbose_name

      # Aktion-URL je nach Nachrichtentyp
      if msg.message_type == 'review_request':
        action_url = f'/kiju/review/{review_task.pk}/'
        action_label = 'Prüfen'
        action_icon = 'fa-solid fa-magnifying-glass'
      else:
        # revision_request → UpdateView des jeweiligen Service-Typs
        action_url = (
          f'/kiju/{review_task.service_type}/{review_task.service_id}/update'
          if service is not None
          else '#'
        )
        action_label = 'Bearbeiten'
        action_icon = 'fa-solid fa-pen-to-square'

      inbox_items.append(
        {
          'message': msg,
          'review_task': review_task,
          'service': service,
          'service_name': str(service) if service is not None else '(gelöscht)',
          'service_verbose_name': service_verbose_name,
          'action_url': action_url,
          'action_label': action_label,
          'action_icon': action_icon,
        }
      )

    context = add_permission_context_elements({}, request.user)
    context['inbox_items'] = inbox_items
    context['inbox_count'] = len(inbox_items)

    return render(request, self.template_name, context)
