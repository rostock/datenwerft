import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.urls import reverse

logger = logging.getLogger(__name__)


def get_notification_recipients(message) -> list[str]:
  """
  Ermittelt die E-Mail-Adressen der Nutzer, die über die übergebene InboxMessage
  benachrichtigt werden sollen.

  - ``review_request`` → Nutzer der Ziel-OrgUnit
  - ``revision_request`` → Einrichtungsnutzer des Ziel-Trägers

  Berücksichtigt werden nur Nutzer, die E-Mail-Benachrichtigungen aktiviert haben
  (Opt-in über ``UserProfile.receive_email_notifications``), aktiv sind und eine
  E-Mail-Adresse besitzen. Die Auflösung erfolgt cross-database über
  ``UserProfile.user_id`` gegen die Default-Datenbank.

  :param message: InboxMessage-Instanz
  :return: Liste von E-Mail-Adressen
  """
  if message.message_type == 'review_request' and message.target_org_unit_id:
    profiles = message.target_org_unit.admin_users.filter(receive_email_notifications=True)
  elif message.message_type == 'revision_request' and message.target_provider_id:
    profiles = message.target_provider.facility_users.filter(receive_email_notifications=True)
  else:
    return []
  user_ids = list(profiles.values_list('user_id', flat=True))
  if not user_ids:
    return []
  return list(
    User.objects.using('default')
    .filter(id__in=user_ids, is_active=True)
    .exclude(email='')
    .values_list('email', flat=True)
  )


def get_inbox_url(base_url: str) -> str:
  """
  Baut die absolute URL zur Inbox aus der übergebenen Basis-URL
  (zur Laufzeit aus dem Request abgeleitet, Muster wie in antragsmanagement).
  Gibt einen leeren String zurück, wenn keine Basis-URL vorliegt.

  :param base_url: Basis-URL der Anwendung, z.B. ``https://geo.rostock.de``
  :return: absolute Inbox-URL oder leerer String
  """
  if not base_url:
    return ''
  return f'{base_url.rstrip("/")}{reverse("angebotsdb:inbox_list")}'


def send_inbox_message_notification(message) -> None:
  """
  Versendet eine Benachrichtigungs-E-Mail für die übergebene InboxMessage an alle
  betroffenen Nutzer. Fehler beim Versand werden geloggt, aber nicht weitergereicht,
  damit der Review-Workflow nicht an einem SMTP-Problem scheitert.

  :param message: InboxMessage-Instanz
  """
  try:
    recipients = get_notification_recipients(message)
    if not recipients:
      logger.info('Keine E-Mail-Empfänger für InboxMessage #%s', message.pk)
      return
    review_task = message.review_task
    service = review_task.get_service_instance()
    service_name = (
      service.name if service else f'{review_task.service_type} (ID {review_task.service_id})'
    )
    if message.message_type == 'review_request':
      subject = f'Neuer Prüfauftrag: {service_name}'
      info = (
        f'für das Angebot „{service_name}“ liegt ein neuer Prüfauftrag '
        'in Ihrem Posteingang der Angebotsdatenbank vor.'
      )
    else:
      subject = f'Überarbeitung erforderlich: {service_name}'
      info = (
        f'für das Angebot „{service_name}“ liegt ein Überarbeitungsauftrag '
        'in Ihrem Posteingang der Angebotsdatenbank vor.'
      )
    body_lines = ['Guten Tag,', '', info, '']
    # Basis-URL wird an den View-Erstellungsstellen aus dem Request abgeleitet und als
    # transientes Attribut mitgegeben; ohne Request (z.B. Commands) entfällt der Link
    inbox_url = get_inbox_url(getattr(message, '_base_url', ''))
    if inbox_url:
      body_lines.extend([inbox_url, ''])
    body_lines.append(
      'Diese E-Mail wurde automatisch erzeugt. Bitte antworten Sie nicht auf diese Nachricht. '
      'Sie können die Benachrichtigungen in Ihren Einstellungen deaktivieren.'
    )
    send_mail(
      subject=subject,
      message='\n'.join(body_lines),
      from_email=settings.DEFAULT_FROM_EMAIL,
      recipient_list=recipients,
      fail_silently=False,
    )
  except Exception:
    logger.exception('E-Mail-Versand für InboxMessage #%s fehlgeschlagen', message.pk)
