from datetime import timedelta
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from bemas.models import Complaint, Contact, Person
from bemas.views.functions import create_log_entry


class Command(BaseCommand):

  def handle(self, *args, **options):
    # get complaint status change deadline date
    deadline_date = timezone.now() - timedelta(days=settings.BEMAS_STATUS_CHANGE_DEADLINE_DAYS)
    # get active complaints
    # (i.e. complaints with latest status change after deadline date
    # or with status "less" than closed)
    act_cpls = Complaint.objects.filter(
      status_updated_at__gt=deadline_date) | Complaint.objects.filter(status__ordinal__lt=2)
    # get all persons connected to contacts
    con_ps_ids = Contact.objects.all().values('person')
    # get all persons connected to active complaints
    act_cpls_ps_ids = Person.objects.none().values('id')
    for act_cpl in act_cpls:
      act_cpls_ps_ids = act_cpls_ps_ids | act_cpl.complainers_persons.all().values('id')
    # get persons to be deleted
    # (i.e. persons not connected to contacts and active complaints)
    persons_delete = Person.objects.exclude(
      id__in=con_ps_ids).exclude(id__in=act_cpls_ps_ids)
    num_deleted = 0
    for person_delete in persons_delete:
      object_pk, object_str = person_delete.pk, str(person_delete)
      person_delete.delete()
      create_log_entry(Person, object_pk, object_str, 'deleted', 'System')
      num_deleted += 1
    self.stdout.write(
      self.style.SUCCESS(
        '{} person(s) not connected to contacts and active complaints deleted'.format(num_deleted)
        )
    )
