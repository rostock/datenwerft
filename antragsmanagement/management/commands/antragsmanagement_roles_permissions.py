from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from antragsmanagement.constants_vars import ADMINS, AUTHORITIES, REQUESTERS


class Command(BaseCommand):
  def handle(self, *args, **options):
    num_groups_existing, num_groups_created = 0, 0
    num_permissions_already_assigned, num_permissions_assigned = 0, 0
    app_label = 'antragsmanagement'
    # set permission codenames
    permission_codenames_requester = [
      'view_requester',
      'add_requester',
      'change_requester',
      'view_cleanupeventrequest',
      'add_cleanupeventrequest',
      'view_cleanupeventcontainer',
      'add_cleanupeventcontainer',
      'view_cleanupeventdetails',
      'add_cleanupeventdetails',
      'view_cleanupeventdump',
      'view_cleanupeventevent',
      'add_cleanupeventevent',
      'view_cleanupeventvenue',
      'add_cleanupeventvenue',
    ]
    permission_codenames_authority = [
      'view_cleanupeventrequest',
      'change_cleanupeventrequest',
      'view_cleanupeventcontainer',
      'add_cleanupeventcontainer',
      'change_cleanupeventcontainer',
      'delete_cleanupeventcontainer',
      'view_cleanupeventdetails',
      'change_cleanupeventdetails',
      'view_cleanupeventdump',
      'add_cleanupeventdump',
      'change_cleanupeventdump',
      'delete_cleanupeventdump',
      'view_cleanupeventevent',
      'change_cleanupeventevent',
      'view_cleanupeventvenue',
      'change_cleanupeventvenue',
    ]
    permission_codenames_admin = [
      'view_authority',
      'change_authority',
      'view_email',
      'change_email',
      'view_cleanupeventrequest',
      'view_cleanupeventcontainer',
      'view_cleanupeventdetails',
      'view_cleanupeventdump',
      'view_cleanupeventevent',
      'view_cleanupeventvenue',
    ]
    # get all relevant group names
    group_names = list(AUTHORITIES)
    group_names.extend([ADMINS, REQUESTERS])
    for group_name in group_names:
      # create group if not existing yet
      group, created = Group.objects.get_or_create(name=group_name)
      if created:
        num_groups_created += 1
      else:
        num_groups_existing += 1
      # assign permissions if not assigned yet
      permission_codenames = list(permission_codenames_requester)
      if group_name in AUTHORITIES:
        permission_codenames = list(permission_codenames_authority)
      elif group_name == ADMINS:
        permission_codenames = list(permission_codenames_admin)
      for permission_codename in permission_codenames:
        permission = Permission.objects.get(
          content_type__app_label=app_label, codename=permission_codename
        )
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
