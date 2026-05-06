"""
Behebt falschen Zustand nach dem dedup_review_tasks-Lauf:

Der dedup-Command hat review_request-InboxMessages auch für bereits abgelehnte
ReviewTasks erstellt. Diese Tasks haben bereits eine unaufgelöste revision_request
(→ warten auf Provider-Überarbeitung) und dürfen keine offenen review_requests haben.

Dieses Kommando markiert alle betroffenen review_request-Messages als erledigt.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from angebotsdb.models.base import InboxMessage


class Command(BaseCommand):
  help = 'Löst falsche review_request-Messages auf abgelehnten Tasks auf.'

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

    # Tasks die eine offene revision_request haben (= abgelehnt, warten auf Provider)
    rejected_task_ids = (
      InboxMessage.objects.filter(
        message_type='revision_request',
        is_resolved=False,
      ).values_list('review_task_id', flat=True)
    )

    # review_requests auf diesen Tasks die fälschlicherweise noch offen sind
    spurious = InboxMessage.objects.filter(
      review_task_id__in=rejected_task_ids,
      message_type='review_request',
      is_resolved=False,
    )

    count = spurious.count()
    if count == 0:
      self.stdout.write(self.style.SUCCESS('Keine betroffenen Messages gefunden.'))
      return

    self.stdout.write(f'{count} fehlerhafte review_request-Message(s) gefunden:')
    for msg in spurious:
      self.stdout.write(
        f'  id={msg.id}, review_task_id={msg.review_task_id}, '
        f'target_org_unit_id={msg.target_org_unit_id}'
      )

    if not dry_run:
      with transaction.atomic(using='angebotsdb'):
        spurious.update(is_resolved=True)
      self.stdout.write(self.style.SUCCESS(f'\n{count} Message(s) als erledigt markiert.'))
    else:
      self.stdout.write(self.style.WARNING('\nDry-run abgeschlossen. Keine Daten verändert.'))
