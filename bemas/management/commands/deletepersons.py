from django.core.management.base import BaseCommand

from bemas.models import Complaint, Contact, Originator, Person
from bemas.utils import get_orphaned_persons
from bemas.views.functions import create_log_entry


class Command(BaseCommand):
  def handle(self, *args, **options):
    # get persons to be deleted
    # (i.e. persons not connected to any contacts, originators, or active complaints
    # and last edited last edited before "old" data deadline timestamp)
    persons_delete = get_orphaned_persons(Complaint, Contact, Originator, Person)
    num_deleted = 0
    for person_delete in persons_delete:
      object_pk, content = person_delete.pk, str(person_delete)
      person_delete.delete()
      create_log_entry(Person, object_pk, 'deleted', content, 'System')
      num_deleted += 1
    self.stdout.write(
      self.style.SUCCESS(
        '{} person(s) deleted which were not connected to any contacts, originators, '
        'or active complaints and which were last edited '
        'before "old" data deadline timestamp'.format(num_deleted)
      )
    )
