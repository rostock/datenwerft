import logging

from django.core.exceptions import PermissionDenied
from django.http import HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from ..fields import resolve_pygeoapi_uris
from ..models.base import InboxMessage, OrgUnitServicePermission, ReviewTask
from ..utils import (
  apply_draft_to_published,
  authorized_to_edit,
  authorized_to_review,
  compute_diff,
  create_service_snapshot,
  get_service_instance,
  is_angebotsdb_admin,
  is_angebotsdb_user,
)
from .functions import add_permission_context_elements

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------


def _get_review_fields(service, review_task):
  """
  Baut die Liste der review_fields auf, die im Template dargestellt werden.

  Jedes Element ist ein Dict mit:
    - label       : Lesbarer Feldname (verbose_name)
    - field_name  : Interner Feldname
    - value       : Aktueller Wert des Felds (aus submitted_snapshot)
    - comment     : Vorhandener Kommentar des Reviewers (aus ReviewTask.comments)
    - has_diff    : True wenn sich der Wert seit der letzten Freigabe geändert hat
    - old_value   : Alter Wert (aus approved_snapshot), nur relevant wenn has_diff=True

  Felder die für den Review irrelevant sind (id, created_at, updated_at, host, status)
  werden ausgeblendet.
  """
  EXCLUDED_FIELDS = {
    'id',
    'created_at',
    'updated_at',
    'host',
    'status',
    'published_version',
    'geometry',
  }

  submitted = review_task.submitted_snapshot
  approved = review_task.approved_snapshot
  comments = review_task.comments

  # Diff berechnen (leer wenn noch keine Freigabe existiert)
  diff = compute_diff(approved, submitted) if approved else {}

  review_fields = []

  pygeoapi_fields = getattr(service, 'PYGEOAPI_FIELDS', {})

  # Konkrete Felder
  for field in service._meta.concrete_fields:
    if field.name in EXCLUDED_FIELDS:
      continue

    raw_value = submitted.get(field.name)

    pygeoapi_config = pygeoapi_fields.get(field.name)
    if pygeoapi_config and isinstance(raw_value, list):
      resolved = resolve_pygeoapi_uris(
        raw_value,
        pygeoapi_config['endpoint'],
        pygeoapi_config.get('params', {}),
        pygeoapi_config['label_property'],
      )
      display_value = ', '.join(resolved) if resolved else '–'
    else:
      display_value = _format_snapshot_value(raw_value)

    has_diff = field.name in diff
    old_raw = diff[field.name]['old'] if has_diff else None
    if has_diff and pygeoapi_config and isinstance(old_raw, list):
      old_resolved = resolve_pygeoapi_uris(
        old_raw,
        pygeoapi_config['endpoint'],
        pygeoapi_config.get('params', {}),
        pygeoapi_config['label_property'],
      )
      old_display = ', '.join(old_resolved) if old_resolved else '–'
    else:
      old_display = _format_snapshot_value(old_raw) if has_diff else None

    review_fields.append(
      {
        'label': getattr(field, 'verbose_name', field.name),
        'field_name': field.name,
        'value': display_value,
        'comment': comments.get(field.name, ''),
        'has_diff': has_diff,
        'old_value': old_display,
      }
    )

  # ManyToMany-Felder
  for field in service._meta.many_to_many:
    if field.name in EXCLUDED_FIELDS:
      continue

    raw_value = submitted.get(field.name, [])
    display_value = ', '.join(item.get('display', '') for item in raw_value) if raw_value else '–'

    has_diff = field.name in diff
    old_raw = diff[field.name]['old'] if has_diff else []
    old_display = (
      (', '.join(item.get('display', '') for item in old_raw) if old_raw else '–')
      if has_diff
      else None
    )

    review_fields.append(
      {
        'label': getattr(field, 'verbose_name', field.name),
        'field_name': field.name,
        'value': display_value,
        'comment': comments.get(field.name, ''),
        'has_diff': has_diff,
        'old_value': old_display,
      }
    )

  return review_fields


def _format_snapshot_value(raw_value) -> str:
  """
  Wandelt einen rohen Snapshot-Wert in einen lesbaren Display-String um.

  - None / leere Liste → '–'
  - Dict mit 'display'-Key (ForeignKey) → display-Wert
  - Liste von Dicts (ManyToMany) → kommaseparierter String der display-Werte
  - Alles andere → str()
  """
  if raw_value is None:
    return '–'
  if isinstance(raw_value, dict) and 'display' in raw_value:
    return raw_value['display']
  if isinstance(raw_value, list):
    if not raw_value:
      return '–'
    return ', '.join(
      item.get('display', str(item)) if isinstance(item, dict) else str(item) for item in raw_value
    )
  if isinstance(raw_value, bool):
    return 'Ja' if raw_value else 'Nein'
  return str(raw_value)


# ---------------------------------------------------------------------------
# Phase 3.1 – SubmitForReviewView
# ---------------------------------------------------------------------------


class SubmitForReviewView(View):
  """
  Versetzt einen Service in den Status 'in_review', erstellt einen ReviewTask
  und benachrichtigt alle zuständigen OrgUnits per InboxMessage.

  Nur erreichbar per POST. Zugang nur für den Provider des Service oder Admins.
  """

  def post(self, request, service_type: str, service_id: int):
    # ── Berechtigung ────────────────────────────────────────────────────────
    if not (is_angebotsdb_user(request.user) or request.user.is_superuser):
      return HttpResponseForbidden('Kein Zugriff.')

    # ── Service laden ───────────────────────────────────────────────────────
    service = get_service_instance(service_type, service_id)
    if service is None:
      return HttpResponseBadRequest('Service nicht gefunden.')

    if not authorized_to_edit(request.user, service):
      raise PermissionDenied(
        'Sie haben keine Berechtigung, diesen Service zur Prüfung freizugeben.'
      )

    # ── Statusprüfung ───────────────────────────────────────────────────────
    if service.status not in ('draft', 'revision_needed'):
      return HttpResponseBadRequest(
        f'Service kann nicht zur Prüfung freigegeben werden '
        f'(aktueller Status: {service.get_status_display()}).'
      )

    # ── Snapshot der aktuellen Einreichung erstellen ─────────────────────────
    submitted_snapshot = create_service_snapshot(service)

    # ── Approved-Snapshot aus dem letzten freigegebenen ReviewTask übernehmen ─
    last_approved = (
      ReviewTask.objects.filter(
        service_type=service_type,
        service_id=service_id,
        task_status='approved',
      )
      .order_by('-created_at')
      .first()
    )
    approved_snapshot = last_approved.approved_snapshot if last_approved else {}

    # ── Zuständige OrgUnit(s) ermitteln ─────────────────────────────────────
    responsible_org_units = OrgUnitServicePermission.objects.filter(
      service_type=service_type,
    ).select_related('organisational_unit')

    if not responsible_org_units.exists():
      logger.warning(
        'Kein OrgUnit für service_type=%s gefunden. '
        'ReviewTask wird trotzdem erstellt, aber keine InboxMessage verschickt.',
        service_type,
      )

    # ── Eventuell noch offene ReviewTasks für diesen Service abschließen ────
    # Alte offene Tasks werden als 'rejected' geschlossen und ihre InboxMessages
    # als erledigt markiert, bevor ein neuer Task erstellt wird.
    old_pending_tasks = ReviewTask.objects.filter(
      service_type=service_type,
      service_id=service_id,
      task_status='pending',
    )
    for old_task in old_pending_tasks:
      InboxMessage.objects.filter(review_task=old_task).update(is_resolved=True)
    old_pending_tasks.update(task_status='rejected')

    # ── Offene revision_request-Nachrichten von Ablehnungen auflösen ─────────
    old_rejected_tasks = ReviewTask.objects.filter(
      service_type=service_type,
      service_id=service_id,
      task_status='rejected',
    )
    InboxMessage.objects.filter(
      review_task__in=old_rejected_tasks,
      message_type='revision_request',
      is_resolved=False,
    ).update(is_resolved=True)

    # ── ReviewTask erstellen ─────────────────────────────────────────────────
    # Falls mehrere OrgUnits zuständig sind, erstellen wir einen Task pro OrgUnit.
    service.status = 'in_review'
    service.save(update_fields=['status'])

    for permission in responsible_org_units:
      review_task = ReviewTask.objects.create(
        service_type=service_type,
        service_id=service_id,
        assigned_org_unit=permission.organisational_unit,
        created_by_user_id=request.user.id,
        task_status='pending',
        submitted_snapshot=submitted_snapshot,
        approved_snapshot=approved_snapshot,
      )

      InboxMessage.objects.create(
        message_type='review_request',
        review_task=review_task,
        target_org_unit=permission.organisational_unit,
      )

      logger.info(
        'ReviewTask #%s erstellt für service_type=%s service_id=%s OrgUnit=%s',
        review_task.pk,
        service_type,
        service_id,
        permission.organisational_unit,
      )

    # ── Redirect zurück zur Listen-Ansicht ───────────────────────────────────
    list_url = reverse(f'angebotsdb:{service_type}_list')
    return redirect(list_url)

  def get(self, request, service_type: str, service_id: int):
    """GET-Anfragen werden zur Listen-Ansicht umgeleitet."""
    return redirect(reverse(f'angebotsdb:{service_type}_list'))


# ---------------------------------------------------------------------------
# Phase 3.2 – ReviewServiceView
# ---------------------------------------------------------------------------


class ReviewServiceView(View):
  """
  Zeigt den Review-Auftrag für einen ReviewTask.

  GET: Tabellarische Darstellung aller Service-Felder mit Kommentar-Eingabe
       und optionaler Diff-Anzeige.
  POST: Speichert Kommentare und führt Freigabe oder Zurückweisung durch.
  """

  template_name = 'angebotsdb/review.html'

  def _load_task_and_service(self, task_id: int):
    """Lädt ReviewTask und die zugehörige Service-Instanz. Gibt (task, service) zurück."""
    review_task = get_object_or_404(ReviewTask, pk=task_id)
    service = review_task.get_service_instance()
    return review_task, service

  def _check_permission(self, request, review_task):
    """
    Prüft ob der User berechtigt ist, diesen ReviewTask zu bearbeiten.
    Erlaubt: Superuser, Admins, User der zugewiesenen OrgUnit.
    """
    if request.user.is_superuser or is_angebotsdb_admin(request.user):
      return True

    service = review_task.get_service_instance()
    if service is None:
      return False

    return authorized_to_review(request.user, service)

  def get(self, request, task_id: int):
    review_task, service = self._load_task_and_service(task_id)

    if not self._check_permission(request, review_task):
      raise PermissionDenied('Sie haben keine Berechtigung, diesen Prüfauftrag einzusehen.')

    if service is None:
      return HttpResponseBadRequest('Der zugehörige Service wurde nicht gefunden.')

    review_fields = _get_review_fields(service, review_task)
    has_comments = bool(review_task.comments)

    context = add_permission_context_elements({}, request.user)
    context.update(
      {
        'review_task': review_task,
        'service': service,
        'service_verbose_name': service._meta.verbose_name,
        'service_type': review_task.service_type,
        'review_fields': review_fields,
        'has_comments': has_comments,
        'has_diff': review_task.approved_snapshot != {},
      }
    )

    return render(request, self.template_name, context)

  def post(self, request, task_id: int):
    review_task, service = self._load_task_and_service(task_id)

    if not self._check_permission(request, review_task):
      raise PermissionDenied('Sie haben keine Berechtigung, diesen Prüfauftrag zu bearbeiten.')

    if service is None:
      return HttpResponseBadRequest('Der zugehörige Service wurde nicht gefunden.')

    if review_task.task_status != 'pending':
      return HttpResponseBadRequest('Dieser Prüfauftrag ist bereits abgeschlossen.')

    # ── Debug-Logging ─────────────────────────────────────────────────────────
    logger.warning(
      'ReviewServiceView.post: task_id=%s POST-Keys=%s', task_id, list(request.POST.keys())
    )
    logger.warning('ReviewServiceView.post: action=%r', request.POST.get('action'))
    for key, value in request.POST.items():
      if key.startswith('comment_'):
        logger.warning('ReviewServiceView.post: %s=%r', key, value)

    # ── Kommentare aus dem Formular lesen ────────────────────────────────────
    comments = {}
    for key, value in request.POST.items():
      if key.startswith('comment_'):
        field_name = key[len('comment_') :]
        stripped = value.strip()
        if stripped:
          comments[field_name] = stripped

    # ── Aktion auslesen ──────────────────────────────────────────────────────
    action = request.POST.get('action')
    logger.warning('ReviewServiceView.post: comments=%s action=%r', comments, action)

    if action == 'approve':
      if comments:
        # Sicherheitscheck: Freigabe darf nicht erfolgen wenn Kommentare vorhanden
        return HttpResponseBadRequest('Freigabe nicht möglich solange Kommentare vorhanden sind.')
      self._approve(review_task, service)

    elif action == 'reject':
      if not comments:
        return HttpResponseBadRequest('Zurückweisung erfordert mindestens einen Kommentar.')
      review_task.comments = comments
      review_task.save(update_fields=['comments'])
      self._reject(review_task, service, request.user.id)

    else:
      # Nur Kommentare speichern (Zwischenspeichern ohne Aktion)
      review_task.comments = comments
      review_task.save(update_fields=['comments'])
      return redirect('angbotsdb:review_service', task_id=task_id)

    return redirect('angebotsdb:inbox_list')

  def _approve(self, review_task: ReviewTask, service):
    """
    Gibt den Service frei.

    Wenn der Service eine Draft-Copy ist (published_version_id gesetzt):
    - Überträgt alle Felder der Draft-Copy auf den Original-Datensatz
      via apply_draft_to_published() (löscht die Draft-Copy).
    - Zeigt den ReviewTask auf die PK des Originals um.

    Wenn der Service ein normaler Draft ist:
    - Setzt service.status = 'published' direkt.

    In beiden Fällen:
    - approved_snapshot ← submitted_snapshot (Basis für nächsten Diff)
    - Alle InboxMessages dieses Tasks als erledigt markieren
    """

    is_draft_copy = getattr(service, 'published_version_id', None) is not None

    if is_draft_copy:
      published = service.published_version

      if published is not None:
        # Felder übertragen, Draft-Copy löschen
        apply_draft_to_published(draft=service, published=published)

        # ReviewTask auf Original-Service umzeigen
        review_task.service_id = published.pk
        review_task.task_status = 'approved'
        review_task.comments = {}
        review_task.approved_snapshot = review_task.submitted_snapshot
        review_task.save(
          update_fields=[
            'task_status',
            'comments',
            'approved_snapshot',
            'service_id',
          ]
        )

        InboxMessage.objects.filter(review_task=review_task).update(is_resolved=True)

        logger.info(
          'ReviewTask #%s freigegeben (Draft-Copy) – Original service_type=%s service_id=%s',
          review_task.pk,
          review_task.service_type,
          published.pk,
        )
        return

      else:
        # Fallback: Original wurde inzwischen gelöscht →
        # Draft-Copy wird selbst zum neuen published Service
        logger.warning(
          'ReviewTask #%s: published_version wurde gelöscht. '
          'Draft-Copy #%s wird direkt als published behandelt.',
          review_task.pk,
          service.pk,
        )
        # Fallthrough in normalen Approve-Flow

    # Normaler Approve-Flow (kein Draft-Copy oder Fallback)
    service.published_version = None  # sicherstellen dass kein verwaister FK bleibt
    service.status = 'published'
    service.save(update_fields=['status', 'published_version'])

    review_task.task_status = 'approved'
    review_task.comments = {}
    review_task.approved_snapshot = review_task.submitted_snapshot
    review_task.save(update_fields=['task_status', 'comments', 'approved_snapshot'])

    InboxMessage.objects.filter(review_task=review_task).update(is_resolved=True)

    logger.info(
      'ReviewTask #%s freigegeben – service_type=%s service_id=%s',
      review_task.pk,
      review_task.service_type,
      review_task.service_id,
    )

  def _reject(self, review_task: ReviewTask, service, user_id: int):
    """
    Weist den Service zurück:
    - Service-Status → 'revision_needed'
    - ReviewTask-Status → 'rejected'
    - Alle InboxMessages dieses Tasks (OrgUnit-Seite) als erledigt markieren
    - Neue InboxMessage → Provider des Service
    """
    service.status = 'revision_needed'
    service.save(update_fields=['status'])

    review_task.task_status = 'rejected'
    review_task.reviewed_by_user_id = user_id
    review_task.save(update_fields=['task_status', 'reviewed_by_user_id'])

    # OrgUnit-Nachrichten als erledigt markieren
    InboxMessage.objects.filter(
      review_task=review_task,
      message_type='review_request',
    ).update(is_resolved=True)

    # Neue Nachricht an den Provider
    InboxMessage.objects.create(
      message_type='revision_request',
      review_task=review_task,
      target_provider=service.host,
    )

    logger.info(
      'ReviewTask #%s abgelehnt – service_type=%s service_id=%s provider=%s',
      review_task.pk,
      review_task.service_type,
      review_task.service_id,
      service.host,
    )
