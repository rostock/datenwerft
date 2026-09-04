from django.core.exceptions import ValidationError
from django.test import TestCase

from pygeoapi.models import Collection, CollectionAttribute, DatabaseConnection, StorageCrs


class CollectionAttributeModelTest(TestCase):
  """
  tests for the attribute inventory data model (uniqueness scope, deny-by-default)
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

  def test_name_is_unique_per_collection(self):
    CollectionAttribute.objects.create(collection=self.collection, name='id')
    with self.assertRaises(ValidationError):
      # save() -> full_clean() rejects the duplicate (collection, name) as a
      # ValidationError, not an IntegrityError
      CollectionAttribute.objects.create(collection=self.collection, name='id')

  def test_same_name_allowed_in_different_collections(self):
    other = Collection.objects.create(
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
    CollectionAttribute.objects.create(collection=self.collection, name='id')
    CollectionAttribute.objects.create(collection=other, name='id')
    self.assertEqual(CollectionAttribute.objects.filter(name='id').count(), 2)

  def test_inventory_carries_no_read_right(self):
    # deny-by-default is structural: the model has no readable/permission field,
    # so being inventoried alone grants access to no role (rights: DH-65/DH-74).
    # concrete_fields instead of get_fields(): the latter also lists reverse
    # relations, which now include the permissions pointing here (DH-65)
    field_names = {field.name for field in CollectionAttribute._meta.concrete_fields}
    self.assertEqual(field_names, {'id', 'collection', 'name', 'data_type', 'is_present'})
