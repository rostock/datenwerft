"""
Einmalige Bereinigung doppelter ReviewTasks.

Hintergrund: Vor dem Fix in SubmitForReviewView wurde pro zuständiger OrgUnit
ein eigener ReviewTask erstellt statt einem Task mit mehreren InboxMessages.
Dieses Kommando konsolidiert diese Duplikate.

Gruppierungskriterium: Gleiche (service_type, service_id) + Erstellungszeitpunkt
innerhalb von 1 Sekunde (= gleicher HTTP-Request).

Für jede Gruppe:
- Kanonischer Task: abgelehnt/genehmigt vor pending; bei Gleichstand niedrigste ID.
- Fehlende InboxMessages für den kanonischen Task werden neu erstellt.
- InboxMessages der Duplikate werden als erledigt markiert.
- Duplikate werden gelöscht.
"""
import logging
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction

from angebotsdb.models.base import InboxMessage, OrgUnitServicePermission, ReviewTask

logger = logging.getLogger(__name__)

STATUS_PRIORITY = {'approved': 0, 'rejected': 1, 'pending': 2}


def _canonical_task(tasks):
  """Gibt den kanonischen Task aus einer Duplikatgruppe zurück."""
  return min(tasks, key=lambda t: (STATUS_PRIORITY.get(t.task_status, 9), t.pk))


def _find_duplicate_groups():
  """
  Liefert eine Liste von Listen, jede enthält Task-Objekte aus demselben
  Einreichungs-Batch (gleiche service_type/service_id, ≤1 Sek. auseinander).
  """
  groups = []
  seen_pairs = set()

  all_tasks = list(ReviewTask.objects.order_by('service_type', 'service_id', 'created_at'))

  i = 0
  while i < len(all_tasks):
    task = all_tasks[i]
    pair = (task.service_type, task.service_id)

    if pair in seen_pairs:
      i += 1
      continue
    seen_pairs.add(pair)

    # Alle Tasks für dieses Paar sammeln
    pair_tasks = [t for t in all_tasks if (t.service_type, t.service_id) == pair]

    # In Batches unterteilen: Lücke > 1 Sekunde trennt Batches
    batch = [pair_tasks[0]]
    for task in pair_tasks[1:]:
      if task.created_at - batch[0].created_at <= timedelta(seconds=1):
        batch.append(task)
      else:
        if len(batch) > 1:
          groups.append(batch)
        batch = [task]
    if len(batch) > 1:
      groups.append(batch)

    i += 1

  return groups


def _process_groups(groups, dry_run, stdout, style):
  for group in groups:
    canonical = _canonical_task(group)
    duplicates = [t for t in group if t.pk != canonical.pk]

    service_type = canonical.service_type
    service_id = canonical.service_id

    stdout.write(
      f'\n{service_type} ID={service_id}: '
      f'Behalte Task #{canonical.pk} ({canonical.task_status}), '
      f'lösche Tasks {[t.pk for t in duplicates]}'
    )

    # Bereits vorhandene OrgUnit-Nachrichten für den kanonischen Task
    existing_org_units = set(
      InboxMessage.objects.filter(
        review_task=canonical,
        message_type='review_request',
      ).values_list('target_org_unit_id', flat=True)
    )

    # Fehlende InboxMessages für zuständige OrgUnits neu erstellen
    permissions = OrgUnitServicePermission.objects.filter(service_type=service_type)
    for perm in permissions:
      if perm.organisational_unit_id not in existing_org_units:
        stdout.write(
          f'  → Erstelle InboxMessage für OrgUnit #{perm.organisational_unit_id}'
        )
        if not dry_run:
          InboxMessage.objects.create(
            message_type='review_request',
            review_task=canonical,
            target_org_unit=perm.organisational_unit,
          )

    # assigned_org_unit des kanonischen Tasks auf erste Berechtigung setzen
    first_perm = permissions.first()
    if first_perm and canonical.assigned_org_unit_id != first_perm.organisational_unit_id:
      stdout.write(
        f'  → Setze assigned_org_unit auf OrgUnit #{first_perm.organisational_unit_id}'
      )
      if not dry_run:
        canonical.assigned_org_unit = first_perm.organisational_unit
        canonical.save(update_fields=['assigned_org_unit'])

    # Duplikate bereinigen
    for dup in duplicates:
      open_msgs = InboxMessage.objects.filter(review_task=dup, is_resolved=False).count()
      stdout.write(f'  → Lösche Task #{dup.pk}, löse {open_msgs} offene Nachricht(en) auf')
      if not dry_run:
        InboxMessage.objects.filter(review_task=dup).update(is_resolved=True)
        dup.delete()


class Command(BaseCommand):
  help = 'Bereinigt doppelte ReviewTasks (einmalige Ausführung nach dem Bugfix).'

  def add_arguments(self, parser):
    parser.add_argument(
      '--dry-run',
      action='store_true',
      help='Zeigt was getan würde, ohne Änderungen zu speichern.',
    )

  def handle(self, *args, **options):
    dry_run = options['dry_run']
    if dry_run:
      self.stdout.write(self.style.WARNING(
        'Dry-run-Modus: keine Änderungen werden gespeichert.\n'
      ))

    groups = _find_duplicate_groups()

    if not groups:
      self.stdout.write(self.style.SUCCESS('Keine Duplikate gefunden.'))
      return

    self.stdout.write(f'{len(groups)} Duplikatgruppe(n) gefunden.\n')

    if dry_run:
      _process_groups(groups, dry_run=True, stdout=self.stdout, style=self.style)
      self.stdout.write(self.style.WARNING('\nDry-run abgeschlossen. Keine Daten verändert.'))
    else:
      with transaction.atomic(using='angebotsdb'):
        _process_groups(groups, dry_run=False, stdout=self.stdout, style=self.style)
      self.stdout.write(self.style.SUCCESS('\nBereinigung abgeschlossen.'))
