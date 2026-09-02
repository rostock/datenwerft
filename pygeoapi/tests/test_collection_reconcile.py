from django.db import connections
from django.test import TestCase
from django.test.utils import CaptureQueriesContext

from pygeoapi.models import (
  AttributeReadPermission,
  Collection,
  CollectionAttribute,
  DatabaseConnection,
  Role,
  StorageCrs,
)
from pygeoapi.services import reconcile_collection_inventory


class ReconcileCollectionInventoryTest(TestCase):
  """
  tests for the reconciliation of a collection's attribute inventory against a
  column list

  the service does not read the source itself; the column list reaches it
  validated from the form, which pygeoapi/tests/test_collection_admin.py covers
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
    self.role = Role.objects.create(identifier='gruen', label='Grünamt')

  def columns(self, *pairs):
    return [{'name': name, 'type': data_type} for name, data_type in pairs]

  def inventory(self):
    """
    the inventory of the collection as name -> (data type, present), read fresh
    from the database
    """
    return {
      attribute.name: (attribute.data_type, attribute.is_present)
      for attribute in self.collection.attributes.all()
    }

  def add(self, name, data_type='text', is_present=True, with_role=False):
    attribute = CollectionAttribute.objects.create(
      collection=self.collection, name=name, data_type=data_type, is_present=is_present
    )
    if with_role:
      AttributeReadPermission.objects.create(role=self.role, attribute=attribute)
    return attribute

  def test_a_missing_attribute_is_added_with_its_data_type(self):
    result = reconcile_collection_inventory(
      self.collection, self.columns(('id', 'integer'), ('baumart', 'character varying(50)'))
    )
    self.assertEqual(result.added, ['baumart', 'id'])
    self.assertEqual(
      self.inventory(),
      {'id': ('integer', True), 'baumart': ('character varying(50)', True)},
    )

  def test_a_new_attribute_gets_no_permission_of_its_own_accord(self):
    reconcile_collection_inventory(self.collection, self.columns(('baumart', 'text')))
    self.assertEqual(AttributeReadPermission.objects.count(), 0)

  def test_an_attribute_without_a_determinable_type_stays_empty(self):
    # no substitute value that pretends a type the source does not state
    reconcile_collection_inventory(self.collection, self.columns(('baumart', '')))
    self.assertEqual(self.inventory(), {'baumart': ('', True)})

  def test_a_repeated_reconcile_changes_nothing(self):
    columns = self.columns(('id', 'integer'), ('baumart', 'text'))
    reconcile_collection_inventory(self.collection, columns)
    before = {attribute.pk: attribute.name for attribute in self.collection.attributes.all()}
    result = reconcile_collection_inventory(self.collection, columns)
    self.assertFalse(result.has_changes)
    self.assertEqual(result.added, [])
    self.assertEqual(result.vanished, [])
    self.assertEqual(result.reappeared, [])
    self.assertEqual(result.retyped, [])
    after = {attribute.pk: attribute.name for attribute in self.collection.attributes.all()}
    # equal primary keys prove that nothing was deleted and created anew
    self.assertEqual(after, before)

  def test_a_vanished_attribute_is_flagged_and_not_deleted(self):
    attribute = self.add('strasse', with_role=True)
    result = reconcile_collection_inventory(self.collection, self.columns(('baumart', 'text')))
    self.assertEqual(result.vanished, ['strasse'])
    attribute.refresh_from_db()
    self.assertFalse(attribute.is_present)
    # the entry, its data type and the permission granted on it all stay
    self.assertEqual(attribute.data_type, 'text')
    self.assertEqual(
      list(AttributeReadPermission.objects.values_list('attribute_id', flat=True)),
      [attribute.pk],
    )

  def test_an_already_vanished_attribute_is_not_reported_again(self):
    self.add('strasse', is_present=False)
    result = reconcile_collection_inventory(self.collection, self.columns(('baumart', 'text')))
    self.assertEqual(result.vanished, [])
    self.assertEqual(result.added, ['baumart'])

  def test_a_reappearing_attribute_keeps_its_row_and_its_permissions(self):
    attribute = self.add('strasse', is_present=False, with_role=True)
    permission = AttributeReadPermission.objects.get()
    result = reconcile_collection_inventory(self.collection, self.columns(('strasse', 'text')))
    self.assertEqual(result.reappeared, ['strasse'])
    self.assertEqual(result.added, [])
    attribute.refresh_from_db()
    self.assertTrue(attribute.is_present)
    # same primary key: the attribute was unflagged, not created anew
    self.assertEqual(self.collection.attributes.count(), 1)
    self.assertEqual(self.collection.attributes.get().pk, attribute.pk)
    self.assertEqual(AttributeReadPermission.objects.get().pk, permission.pk)

  def test_a_changed_data_type_is_carried_forward_without_touching_permissions(self):
    attribute = self.add('baumart', data_type='text', with_role=True)
    permission = AttributeReadPermission.objects.get()
    result = reconcile_collection_inventory(
      self.collection, self.columns(('baumart', 'character varying(50)'))
    )
    self.assertEqual(result.retyped, ['baumart'])
    attribute.refresh_from_db()
    self.assertEqual(attribute.data_type, 'character varying(50)')
    self.assertEqual(AttributeReadPermission.objects.get().pk, permission.pk)

  def test_a_type_that_can_no_longer_be_determined_empties_the_field(self):
    attribute = self.add('baumart', data_type='text')
    result = reconcile_collection_inventory(self.collection, self.columns(('baumart', '')))
    self.assertEqual(result.retyped, ['baumart'])
    attribute.refresh_from_db()
    self.assertEqual(attribute.data_type, '')

  def test_reappearing_and_retyping_are_reported_separately(self):
    self.add('strasse', data_type='text', is_present=False)
    result = reconcile_collection_inventory(self.collection, self.columns(('strasse', 'integer')))
    # the categories are not mutually exclusive: both happened to this attribute
    self.assertEqual(result.reappeared, ['strasse'])
    self.assertEqual(result.retyped, ['strasse'])
    self.assertEqual(self.inventory(), {'strasse': ('integer', True)})

  def test_an_empty_column_list_leaves_the_inventory_untouched(self):
    self.add('strasse', with_role=True)
    self.add('baumart')
    result = reconcile_collection_inventory(self.collection, [])
    # never read as "every attribute vanished"
    self.assertFalse(result.has_changes)
    self.assertEqual(self.inventory(), {'strasse': ('text', True), 'baumart': ('text', True)})
    self.assertEqual(AttributeReadPermission.objects.count(), 1)

  def test_the_reconcile_covers_all_four_categories_in_one_go(self):
    self.add('strasse', with_role=True)
    self.add('hoehe', is_present=False)
    self.add('baumart', data_type='text')
    self.add('pflanzjahr', data_type='integer')
    result = reconcile_collection_inventory(
      self.collection,
      self.columns(
        ('id', 'integer'),
        ('hoehe', 'text'),
        ('baumart', 'character varying(50)'),
        ('pflanzjahr', 'integer'),
      ),
    )
    self.assertEqual(result.added, ['id'])
    self.assertEqual(result.vanished, ['strasse'])
    self.assertEqual(result.reappeared, ['hoehe'])
    self.assertEqual(result.retyped, ['baumart'])
    self.assertEqual(
      self.inventory(),
      {
        'id': ('integer', True),
        'strasse': ('text', False),
        'hoehe': ('text', True),
        'baumart': ('character varying(50)', True),
        'pflanzjahr': ('integer', True),
      },
    )

  def test_another_collection_is_not_touched(self):
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
    CollectionAttribute.objects.create(collection=other, name='strasse', data_type='text')
    reconcile_collection_inventory(self.collection, self.columns(('baumart', 'text')))
    self.assertEqual(list(other.attributes.values_list('name', 'is_present')), [('strasse', True)])

  def test_the_names_are_reported_independently_of_the_order_received(self):
    result = reconcile_collection_inventory(
      self.collection, self.columns(('strasse', 'text'), ('baumart', 'text'), ('id', 'integer'))
    )
    self.assertEqual(result.added, ['baumart', 'id', 'strasse'])

  def test_the_number_of_queries_does_not_grow_with_the_number_of_attributes(self):
    """
    the set-based write path: one read plus at most four writes, regardless of how
    many attributes are involved

    measured on a reconcile that triggers all four categories at once, otherwise
    the comparison would only cover the one query of the insert
    """
    small, small_columns = self.seed_for_every_category(service_id=3, per_category=1)
    large, large_columns = self.seed_for_every_category(service_id=4, per_category=25)
    with CaptureQueriesContext(connections['default']) as few_attributes:
      small_result = reconcile_collection_inventory(small, small_columns)
    with CaptureQueriesContext(connections['default']) as many_attributes:
      large_result = reconcile_collection_inventory(large, large_columns)
    self.assertEqual(len(many_attributes), len(few_attributes))
    # one read plus one write per category, instead of one per attribute
    self.assertLessEqual(len(self.statements(many_attributes)), 5)
    for result, count in ((small_result, 1), (large_result, 25)):
      with self.subTest(count=count):
        self.assertEqual(len(result.added), count)
        self.assertEqual(len(result.vanished), count)
        self.assertEqual(len(result.reappeared), count)
        self.assertEqual(len(result.retyped), count)

  def statements(self, captured):
    """
    the captured queries without the savepoints, which only exist because a
    TestCase wraps every test in a transaction of its own
    """
    return [
      query for query in captured.captured_queries if 'SAVEPOINT' not in query['sql'].upper()
    ]

  def seed_for_every_category(self, service_id, per_category):
    """
    a collection and a column list that make a single reconcile add, flag, unflag
    and retype ``per_category`` attributes each
    """
    collection = Collection.objects.create(
      deactivated=False,
      service_id=service_id,
      database_connection=self.connection,
      schema='public',
      table=f'table_{service_id}',
      id_field='id',
      title_field='name',
      geom_field='geom',
      storage_crs=StorageCrs.EPSG_25833,
    )
    columns = []
    for index in range(per_category):
      # vanishes: in the inventory, no longer in the source
      CollectionAttribute.objects.create(
        collection=collection, name=f'weg_{index}', data_type='text'
      )
      # reappears: flagged as gone, back in the source with an unchanged type
      CollectionAttribute.objects.create(
        collection=collection, name=f'zurueck_{index}', data_type='text', is_present=False
      )
      columns.append({'name': f'zurueck_{index}', 'type': 'text'})
      # retyped: in both, with another type in the source
      CollectionAttribute.objects.create(
        collection=collection, name=f'typ_{index}', data_type='text'
      )
      columns.append({'name': f'typ_{index}', 'type': 'integer'})
      # added: only in the source
      columns.append({'name': f'neu_{index}', 'type': 'text'})
    return collection, columns
