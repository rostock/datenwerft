from io import StringIO

from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase

from pygeoapi.constants_vars import GROUP
from pygeoapi.models import AttributeReadPermission, CollectionAttribute, Role


class PygeoapiRolesPermissionsCommandTest(TestCase):
  """
  tests for the command assigning the pygeoapi permissions to the pygeoapi group
  """

  # pygeoapi is not routed by DatabaseRouter, so it lives on the default database
  databases = {'default'}

  # the models of the rights system; the group must hold all four default
  # permissions of each of them
  rights_system_models = (Role, CollectionAttribute, AttributeReadPermission)

  def run_command(self):
    out = StringIO()
    call_command('pygeoapi_roles_permissions', stdout=out)
    return out.getvalue()

  def expected_codenames(self):
    """
    the four default permission codenames of every model of the rights system,
    derived from the content types rather than hard-coded, so that a model added
    later is covered without touching this test
    """
    codenames = set()
    for model in self.rights_system_models:
      model_name = ContentType.objects.get_for_model(model).model
      codenames.update(f'{action}_{model_name}' for action in ('add', 'change', 'delete', 'view'))
    return codenames

  def assigned_codenames(self):
    group = Group.objects.get(name=GROUP)
    return set(group.permissions.values_list('codename', flat=True))

  def assignment_rows(self):
    """
    the primary keys of the rows connecting the group to its permissions;
    assigning an already assigned permission leaves the set of codenames
    untouched, so only the identity of these rows shows whether a second run
    rewrote the assignment
    """
    group = Group.objects.get(name=GROUP)
    return set(Group.permissions.through.objects.filter(group=group).values_list('pk', flat=True))

  def test_group_is_created_when_missing(self):
    Group.objects.filter(name=GROUP).delete()
    self.run_command()
    self.assertEqual(Group.objects.filter(name=GROUP).count(), 1)

  def test_all_permissions_of_the_rights_system_models_are_assigned(self):
    self.run_command()
    self.assertTrue(self.expected_codenames().issubset(self.assigned_codenames()))

  def test_second_run_leaves_the_assignment_untouched(self):
    self.run_command()
    after_first_run = self.assignment_rows()
    self.run_command()
    self.assertEqual(self.assignment_rows(), after_first_run)
    self.assertEqual(Group.objects.filter(name=GROUP).count(), 1)

  def test_command_reports_what_it_did(self):
    """
    the only test tied to the wording of the command's output; a reformulated
    message turns this test red on its own and no behaviour test with it. The
    counter is also the only place where "nothing was written on the second
    run" is observable at all - the stored state is by itself the same whether
    the command skipped an existing assignment or wrote it again
    """
    Group.objects.filter(name=GROUP).delete()
    first_output = self.run_command()
    second_output = self.run_command()
    self.assertIn('1 group(s) created', first_output)
    # the leading comma pins the assertion to the second counter; the first one
    # reads "... permission(s) already assigned"
    self.assertNotIn(', 0 permission(s) assigned', first_output)
    self.assertIn(', 0 permission(s) assigned', second_output)

  def test_membership_decides_access_to_the_rights_system_models(self):
    self.run_command()
    outsider = User.objects.create_user(username='outsider')
    self.assertFalse(outsider.has_perm('pygeoapi.view_attributereadpermission'))
    Group.objects.get(name=GROUP).user_set.add(outsider)
    # Django caches a user's permissions on the instance after the first
    # has_perm(); without re-reading the user from the database the assertions
    # below would run against that stale cache and prove nothing. Do not remove.
    member = User.objects.get(pk=outsider.pk)
    for codename in self.expected_codenames():
      self.assertTrue(member.has_perm(f'pygeoapi.{codename}'))
