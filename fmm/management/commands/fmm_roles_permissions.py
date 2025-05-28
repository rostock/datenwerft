from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from fmm.constants_vars import GROUP


class Command(BaseCommand):
  def handle(self, *args, **options):
    num_groups_existing, num_groups_created = 0, 0
    num_permissions_already_assigned, num_permissions_assigned = 0, 0
    app_label = 'fmm'
    # get relevant group name
    group_name = GROUP
    # create group if not existing yet
    group, created = Group.objects.get_or_create(name=group_name)
    if created:
      num_groups_created += 1
    else:
      num_groups_existing += 1
    # assign permissions if not assigned yet
    permissions = Permission.objects.filter(content_type__app_label=app_label)
    for permission in permissions:
      if group.permissions.filter(pk=permission.pk).exists():
        num_permissions_already_assigned += 1
      else:
        num_permissions_assigned += 1
        group.permissions.add(permission)
    self.stdout.write(
      self.style.SUCCESS(
        '{} group(s) already existing, {} group(s) created'.format(
          num_groups_existing, num_groups_created
        )
      )
    )
    self.stdout.write(
      self.style.SUCCESS(
        '{} permission(s) already assigned, {} permission(s) assigned'.format(
          num_permissions_already_assigned, num_permissions_assigned
        )
      )
    )
