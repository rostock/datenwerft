from django.core.exceptions import ValidationError
from django.test import TestCase

from pygeoapi.models import (
  AttributeReadPermission,
  Collection,
  CollectionAttribute,
  DatabaseConnection,
  Role,
  StorageCrs,
)


class AttributeReadPermissionModelTest(TestCase):
  """
  tests for the read permission data model (grant/revoke, uniqueness scope,
  deny-by-default, absent attributes, delete behaviour)
  """

  # pygeoapi is not routed by DatabaseRouter, so it lives on the default database
  databases = {'default'}

  def setUp(self):
    self.connection = DatabaseConnection.objects.create(
      host='localhost',
      port=5432,
      dbname='source',
      user='reader',
      password='secret',
    )
    self.collection = Collection.objects.create(
      deactivated=False,
      service_id=1,
      database_connection=self.connection,
      schema='public',
      table='trees',
      id_field='id',
      title_field='name',
      geom_field='geom',
      storage_crs=StorageCrs.EPSG_25833,
    )
    self.reader = Role.objects.create(identifier='reader', label='Reader')
    self.other = Role.objects.create(identifier='other', label='Other')
    self.id_attribute = CollectionAttribute.objects.create(collection=self.collection, name='id')
    self.geom_attribute = CollectionAttribute.objects.create(
      collection=self.collection, name='geom'
    )
    self.name_attribute = CollectionAttribute.objects.create(
      collection=self.collection, name='name'
    )
    self.species_attribute = CollectionAttribute.objects.create(
      collection=self.collection, name='baumart'
    )

  def create_other_collection(self):
    return Collection.objects.create(
      deactivated=False,
      service_id=2,
      database_connection=self.connection,
      schema='public',
      table='lamps',
      id_field='id',
      title_field='name',
      geom_field='geom',
      storage_crs=StorageCrs.EPSG_25833,
    )

  def test_grant_and_revoke_roundtrip(self):
    permission = AttributeReadPermission.objects.create(
      role=self.reader, attribute=self.species_attribute
    )
    self.assertTrue(AttributeReadPermission.objects.filter(pk=permission.pk).exists())
    permission.delete()
    self.assertFalse(AttributeReadPermission.objects.filter(pk=permission.pk).exists())
    # revoking touches the permission only, role and inventory entry remain
    self.assertTrue(Role.objects.filter(pk=self.reader.pk).exists())
    self.assertTrue(CollectionAttribute.objects.filter(pk=self.species_attribute.pk).exists())

  def test_role_and_attribute_are_unique_together(self):
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    with self.assertRaises(ValidationError):
      # save() -> full_clean() rejects the duplicate (role, attribute) as a
      # ValidationError, not an IntegrityError
      AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)

  def test_same_attribute_for_several_roles_is_allowed(self):
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    AttributeReadPermission.objects.create(role=self.other, attribute=self.species_attribute)
    self.assertEqual(
      AttributeReadPermission.objects.filter(attribute=self.species_attribute).count(), 2
    )

  def test_same_role_for_several_attributes_is_allowed(self):
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.name_attribute)
    self.assertEqual(AttributeReadPermission.objects.filter(role=self.reader).count(), 2)

  def test_permissions_are_scoped_per_collection(self):
    # the same attribute name in another collection is another inventory entry,
    # so a permission there is a separate right
    other_collection = self.create_other_collection()
    other_species = CollectionAttribute.objects.create(collection=other_collection, name='baumart')
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    AttributeReadPermission.objects.create(role=self.reader, attribute=other_species)
    self.assertEqual(AttributeReadPermission.objects.filter(role=self.reader).count(), 2)
    AttributeReadPermission.objects.filter(attribute=self.species_attribute).delete()
    self.assertTrue(
      AttributeReadPermission.objects.filter(role=self.reader, attribute=other_species).exists()
    )

  def test_unknown_role_is_rejected(self):
    missing_role_id = self.other.pk
    self.other.delete()
    with self.assertRaises(ValidationError):
      # save() -> full_clean() -> ForeignKey.validate() checks that the target
      # row exists, so a stale role reference never reaches the database
      AttributeReadPermission.objects.create(
        role_id=missing_role_id, attribute=self.species_attribute
      )

  def test_unknown_attribute_is_rejected(self):
    missing_attribute_id = self.species_attribute.pk
    self.species_attribute.delete()
    with self.assertRaises(ValidationError):
      AttributeReadPermission.objects.create(role=self.reader, attribute_id=missing_attribute_id)

  def test_role_without_permission_has_no_read_right(self):
    # deny-by-default: without a row there is no right, nothing has to be set
    self.assertFalse(AttributeReadPermission.objects.filter(role=self.reader).exists())
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    self.assertFalse(AttributeReadPermission.objects.filter(role=self.other).exists())

  def test_permission_row_is_the_read_right(self):
    # the existence of the row IS the right: no readable/granted flag that could
    # hold a permission row in a "denied" state
    field_names = {field.name for field in AttributeReadPermission._meta.concrete_fields}
    self.assertEqual(field_names, {'id', 'role', 'attribute'})

  def test_permission_on_absent_attribute_is_kept(self):
    permission = AttributeReadPermission.objects.create(
      role=self.reader, attribute=self.species_attribute
    )
    self.species_attribute.is_present = False
    self.species_attribute.save()
    self.assertTrue(AttributeReadPermission.objects.filter(pk=permission.pk).exists())

  def test_permission_on_absent_attribute_is_ineffective(self):
    permission = AttributeReadPermission.objects.create(
      role=self.reader, attribute=self.species_attribute
    )
    self.assertTrue(permission.is_effective)
    self.species_attribute.is_present = False
    self.species_attribute.save()
    permission.refresh_from_db()
    self.assertFalse(permission.is_effective)

  def test_returning_attribute_becomes_effective_again(self):
    self.species_attribute.is_present = False
    self.species_attribute.save()
    permission = AttributeReadPermission.objects.create(
      role=self.reader, attribute=self.species_attribute
    )
    self.assertFalse(permission.is_effective)
    self.species_attribute.is_present = True
    self.species_attribute.save()
    permission.refresh_from_db()
    self.assertTrue(permission.is_effective)

  def test_revoking_for_one_role_leaves_other_roles_untouched(self):
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    AttributeReadPermission.objects.create(role=self.other, attribute=self.species_attribute)
    AttributeReadPermission.objects.filter(role=self.reader).delete()
    self.assertFalse(AttributeReadPermission.objects.filter(role=self.reader).exists())
    self.assertTrue(AttributeReadPermission.objects.filter(role=self.other).exists())

  def test_deleting_a_role_deletes_its_permissions(self):
    # promised in hilfe/pygeoapi/rollenkatalog.md
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    AttributeReadPermission.objects.create(role=self.other, attribute=self.species_attribute)
    self.reader.delete()
    self.assertFalse(AttributeReadPermission.objects.filter(role_id=self.reader.pk).exists())
    self.assertTrue(AttributeReadPermission.objects.filter(role=self.other).exists())

  def test_deleting_an_attribute_deletes_its_permissions(self):
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.name_attribute)
    self.species_attribute.delete()
    self.assertFalse(
      AttributeReadPermission.objects.filter(attribute_id=self.species_attribute.pk).exists()
    )
    self.assertTrue(AttributeReadPermission.objects.filter(attribute=self.name_attribute).exists())

  def test_deleting_a_collection_deletes_the_permissions(self):
    # promised in hilfe/pygeoapi/attributinventar.md: the collection takes its
    # inventory and with it the permissions hanging off the inventory
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    self.collection.delete()
    self.assertEqual(AttributeReadPermission.objects.count(), 0)
    self.assertEqual(CollectionAttribute.objects.count(), 0)

  def test_granting_a_right_creates_no_further_rows(self):
    # granting one right creates exactly one row, in particular none for
    # id_field/geom_field: those are not subject to permission assignment, they
    # sit at GeoJSON root level and are always delivered (DH-67/DH-68). This
    # test fails if implicit permission rows are ever added.
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    self.assertEqual(AttributeReadPermission.objects.count(), 1)
    self.assertFalse(
      AttributeReadPermission.objects.filter(
        attribute__in=[self.id_attribute, self.geom_attribute]
      ).exists()
    )

  def test_inheritance_is_not_resolved_yet(self):
    # deliberate absence: the data model stores permissions per role only,
    # resolving them along Role.parent is DH-67
    child = Role.objects.create(identifier='child', label='Child', parent=self.reader)
    AttributeReadPermission.objects.create(role=self.reader, attribute=self.species_attribute)
    self.assertFalse(AttributeReadPermission.objects.filter(role=child).exists())
