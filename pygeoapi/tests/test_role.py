from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.test import TestCase

from pygeoapi.models import Role


class RoleModelTest(TestCase):
  """
  tests for the role catalog model (uniqueness, inheritance, cycles, deletion)
  """

  # pygeoapi is not routed by DatabaseRouter, so it lives on the default database
  databases = {'default'}

  def test_identifier_is_unique(self):
    Role.objects.create(identifier='reader', label='Reader')
    with self.assertRaises(ValidationError):
      # save() -> full_clean() -> validate_unique() rejects the duplicate as a
      # ValidationError (not an IntegrityError)
      Role.objects.create(identifier='reader', label='Reader again')

  def test_role_without_parent_is_allowed(self):
    root = Role.objects.create(identifier='root', label='Root')
    self.assertIsNone(root.parent)

  def test_multi_level_inheritance_chain(self):
    grandparent = Role.objects.create(identifier='gp', label='Grandparent')
    parent = Role.objects.create(identifier='p', label='Parent', parent=grandparent)
    child = Role.objects.create(identifier='c', label='Child', parent=parent)
    self.assertEqual(child.parent, parent)
    self.assertEqual(child.parent.parent, grandparent)

  def test_role_cannot_be_its_own_parent(self):
    role = Role.objects.create(identifier='solo', label='Solo')
    role.parent = role
    with self.assertRaises(ValidationError):
      role.save()

  def test_immediate_cycle_is_rejected(self):
    a = Role.objects.create(identifier='a', label='A')
    b = Role.objects.create(identifier='b', label='B', parent=a)
    # closing the loop a -> b -> a
    a.parent = b
    with self.assertRaises(ValidationError):
      a.save()

  def test_multi_level_cycle_is_rejected(self):
    a = Role.objects.create(identifier='a', label='A')
    b = Role.objects.create(identifier='b', label='B', parent=a)
    c = Role.objects.create(identifier='c', label='C', parent=b)
    # closing the loop a -> c -> b -> a
    a.parent = c
    with self.assertRaises(ValidationError):
      a.save()

  def test_deleting_a_parent_role_is_protected(self):
    parent = Role.objects.create(identifier='p', label='Parent')
    Role.objects.create(identifier='c', label='Child', parent=parent)
    # PROTECT prevents deletion while children reference the role, so no child
    # is ever left pointing at a missing parent
    with self.assertRaises(ProtectedError):
      parent.delete()
    self.assertTrue(Role.objects.filter(pk=parent.pk).exists())

  def test_leaf_role_can_be_deleted(self):
    parent = Role.objects.create(identifier='p', label='Parent')
    child = Role.objects.create(identifier='c', label='Child', parent=parent)
    child.delete()
    self.assertFalse(Role.objects.filter(pk=child.pk).exists())
    self.assertTrue(Role.objects.filter(pk=parent.pk).exists())

  def test_public_base_role_is_an_ordinary_role(self):
    # the public base role is technically indistinguishable from any other role
    public = Role.objects.create(identifier='public', label='Öffentlich')
    self.assertIsNone(public.parent)
    self.assertEqual(Role.objects.get(identifier='public'), public)
