from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):

  def handle(self, *args, **options):
    num_groups_existing, num_groups_created = 0, 0
    num_permissions_already_assigned, num_permissions_assigned = 0, 0
    app_label = 'bemas'
    # set permission codenames
    permission_codenames_user = [
      'add_complaint',
      'change_complaint',
      'delete_complaint',
      'view_complaint',
      'add_logentry',
      'view_logentry',
      'add_organization',
      'change_organization',
      'delete_organization',
      'view_organization',
      'add_person',
      'change_person',
      'delete_person',
      'view_person',
      'view_sector',
      'view_status',
      'view_typeofevent',
      'view_typeofimmission',
      'add_originator',
      'change_originator',
      'delete_originator',
      'view_originator',
      'add_event',
      'change_event',
      'delete_event',
      'view_event',
      'add_contact',
      'change_contact',
      'delete_contact',
      'view_contact'
    ]
    permission_codenames_admin = list(permission_codenames_user)
    permission_codenames_admin.extend([
      'add_sector',
      'change_sector',
      'delete_sector',
      'add_status',
      'change_status',
      'delete_status',
      'add_typeofevent',
      'change_typeofevent',
      'delete_typeofevent',
      'add_typeofimmission',
      'change_typeofimmission',
      'delete_typeofimmission'
    ])
    # get all relevant group names
    group_names = list([settings.BEMAS_ADMIN_GROUP_NAME, settings.BEMAS_USERS_GROUP_NAME])
    for group_name in group_names:
      # create group if not existing yet
      if Group.objects.filter(name=group_name).exists():
        num_groups_existing += 1
      else:
        Group.objects.create(name=group_name)
        num_groups_created += 1
      # assign permissions if not assigned yet
      group = Group.objects.get(name=group_name)
      permission_codenames = list(permission_codenames_user)
      if group_name == settings.BEMAS_ADMIN_GROUP_NAME:
        permission_codenames = list(permission_codenames_admin)
      for permission_codename in permission_codenames:
        permission = Permission.objects.get(
          content_type__app_label=app_label, codename=permission_codename)
        if group.permissions.filter(id=permission.id).exists():
          num_permissions_already_assigned += 1
        else:
          num_permissions_assigned += 1
          group.permissions.add(permission)
    self.stdout.write(
      self.style.SUCCESS(
        '{} group(s) already existing, {} group(s) created'.format(
          num_groups_existing, num_groups_created)
        )
    )
    self.stdout.write(
      self.style.SUCCESS(
        '{} permission(s) already assigned, {} permission(s) assigned'.format(
          num_permissions_already_assigned, num_permissions_assigned)
        )
    )
