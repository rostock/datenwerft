import json
import re
from io import StringIO
from unittest.mock import patch

from django.contrib import messages
from django.contrib.admin.models import LogEntry
from django.contrib.auth.models import Group, User
from django.contrib.messages import get_messages
from django.core.management import call_command
from django.db import connections
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from gdihrometadata.models import (
  Access,
  Charset,
  Language,
  Legal,
  License,
  Service,
  ServiceType,
)
from pygeoapi.constants_vars import GROUP
from pygeoapi.models import (
  AttributeReadPermission,
  Collection,
  CollectionAttribute,
  DatabaseConnection,
  Role,
  StorageCrs,
)

# one cell of a row of the attribute overview; the class names come from the
# field names of the inline, the paragraph from the read-only rendering
CELL = re.compile(r'<td class="field-(?P<name>[a-z_]+)">\s*<p>(?P<value>.*?)</p>', re.DOTALL)

INPUT = re.compile(r'<input[^>]*>')
INPUT_NAME = re.compile(r'name="([^"]+)"')
INPUT_VALUE = re.compile(r'value="([^"]*)"')

# the roles column is a select as soon as the assignment is editable; CELL only
# matches cells that are rendered read-only
SELECT = re.compile(r'<select(?P<attrs>[^>]*)>(?P<options>.*?)</select>', re.DOTALL)
OPTION = re.compile(
  r'<option value="(?P<value>[^"]*)"(?P<flags>[^>]*)>(?P<label>[^<]*)</option>',
)
DATA_ATTRIBUTE = re.compile(r'data-attribute="([^"]*)"')

# the controls of the search above the overview; matched by their class and not
# by a literal tag, whose attribute order is not a promised property
SEARCH_INPUT = re.compile(r'<input[^>]*class="attribute-filter-input"[^>]*>')
SEARCH_RESET = re.compile(r'<button[^>]*class="attribute-filter-reset"[^>]*>')
SEARCH_STATUS = re.compile(r'<p[^>]*class="attribute-filter-status"[^>]*>')
FILTER_GROUP = re.compile(r'<div class="attribute-filter" data-group="([^"]+)">')
NAME_ATTRIBUTE = re.compile(r'\bname\s*=')

# the controls of the reconcile above the overview, matched the same way
RECONCILE_BUTTON = re.compile(r'<button[^>]*class="attribute-reconcile-button"[^>]*>', re.DOTALL)
RECONCILE_STATUS = re.compile(r'<p[^>]*class="attribute-reconcile-status"[^>]*>')
COLUMNS_URL = re.compile(r'data-columns-url="([^"]*)"')
HIDDEN_FIELD = r'<input[^>]*id="id_{}"[^>]*>'


class CollectionAdminTestCase(TestCase):
  """
  common setup and page helpers for the tests of a collection's change page
  """

  # pygeoapi itself lives on the default database, but the collection form reads
  # the service metadata records, which DatabaseRouter routes to their own alias;
  # without it the page does not even render
  databases = {'default', 'gdihrometadata'}

  def setUp(self):
    # the same way test_roles_permissions_command.py establishes permissions,
    # instead of maintaining a list of codenames by hand
    call_command('pygeoapi_roles_permissions', stdout=StringIO())
    self.user = User.objects.create_user(username='maintainer', is_staff=True)
    self.user.groups.add(Group.objects.get(name=GROUP))
    # force_login() instead of login(): the project's LDAP backend expects a
    # request object, which login() does not provide (same as in accounts/tests.py)
    self.client.force_login(self.user)
    self.connection = DatabaseConnection.objects.create(
      host='localhost',
      port=5432,
      dbname='source',
      user='reader',
      password='secret',
    )
    # deliberately far outside the primary key range of the service metadata
    # records: the collection form hides every service already in use, so a
    # collision would silently make the form reject a perfectly valid choice
    self.collection = self.create_collection(service_id=90001)

  def create_collection(self, service_id, table='trees'):
    return Collection.objects.create(
      deactivated=False,
      service_id=service_id,
      database_connection=self.connection,
      schema='public',
      table=table,
      id_field='id',
      title_field='name',
      geom_field='geom',
      storage_crs=StorageCrs.EPSG_25833,
    )

  def change_url(self, collection=None):
    collection = collection or self.collection
    return reverse('admin:pygeoapi_collection_change', args=[collection.pk])

  def get_change_page(self, collection=None):
    return self.client.get(self.change_url(collection))

  def rows(self, response):
    """
    the rows of the attribute overview as dictionaries of their cells, in the
    order in which they appear in the page
    """
    result = []
    for row in response.content.decode().split('<tr class="form-row')[1:]:
      cells = {cell['name']: cell['value'] for cell in CELL.finditer(row)}
      select = self.role_select(row)
      if select:
        # the same key the read-only rendering produces, so that both ways of
        # rendering the column can be asserted the same way
        cells['roles'] = ', '.join(self.role_labels(select, selected_only=True))
        cells['role_options'] = self.role_labels(select)
        cells['roles_disabled'] = ' disabled' in select['attrs']
      result.append(cells)
    return result

  def role_select(self, markup):
    for select in SELECT.finditer(markup):
      if DATA_ATTRIBUTE.search(select['attrs']):
        return select
    return None

  def role_labels(self, select, selected_only=False):
    return [
      option['label']
      for option in OPTION.finditer(select['options'])
      if not selected_only or 'selected' in option['flags']
    ]

  def role_fields(self, response):
    """
    the name of the role form field of every attribute row, by attribute name
    """
    return {
      name: INPUT_NAME.search(attrs).group(1)
      for name, attrs in self.role_select_attrs(response).items()
      if INPUT_NAME.search(attrs)
    }

  def role_select_attrs(self, response):
    """
    the raw attributes of the role select of every attribute row, by attribute
    name; asserted against instead of a literal tag, whose attribute order would
    change with every added attribute
    """
    attrs = {}
    for select in SELECT.finditer(response.content.decode()):
      attribute = DATA_ATTRIBUTE.search(select['attrs'])
      if attribute:
        attrs[attribute.group(1)] = select['attrs']
    return attrs

  def fill_inventory(self, collection, number_of_attributes, roles):
    for index in range(number_of_attributes):
      # deliberately not bulk_create(): it skips save() and thus full_clean()
      attribute = CollectionAttribute.objects.create(
        collection=collection, name=f'attribut_{index:03d}', data_type='text'
      )
      for role in roles:
        AttributeReadPermission.objects.create(role=role, attribute=attribute)
    return collection

  def create_service(self, name):
    """
    a service metadata record the collection form accepts; it lives on its own
    database alias and drags in the code lists it references
    """
    return Service.objects.create(
      name=name,
      title=f'Dienst {name}',
      link='https://example.org/service',
      type=ServiceType.API_FEATURES,
      legal=Legal.objects.create(
        title=f'Rechtliches {name}',
        access=Access.objects.create(code=f'https://example.org/access/{name}', title='frei'),
        license=License.objects.create(code=f'https://example.org/license/{name}', title='CC BY'),
      ),
      language=Language.objects.create(code=f'https://example.org/lang/{name}', title='Deutsch'),
      charset=Charset.objects.create(code=f'https://example.org/charset/{name}', title='UTF-8'),
    )

  def formset_data(self, response):
    """
    the hidden management fields of the inline and the roles currently assigned,
    taken from the rendered page on purpose: the empty-inventory branch of the
    inline template has to render the management fields as well, otherwise saving
    the collection fails on the missing formset management data instead of
    writing anything
    """
    content = response.content.decode()
    data = {}
    for tag in INPUT.findall(content):
      name = INPUT_NAME.search(tag)
      if name and name.group(1).startswith('attributes-'):
        value = INPUT_VALUE.search(tag)
        data[name.group(1)] = value.group(1) if value else ''
    # the role selects are no input tags; without them every POST built from this
    # helper would send no role at all and would silently revoke every assignment
    for select in SELECT.finditer(content):
      name = INPUT_NAME.search(select['attrs'])
      if name and name.group(1).startswith('attributes-'):
        data[name.group(1)] = [
          option['value']
          for option in OPTION.finditer(select['options'])
          if 'selected' in option['flags']
        ]
    return data

  def post(self, url, data, patch_reload=True):
    # the pygeoapi instance is asked to reload its configuration; that host is not
    # reachable from the test run and is not what is under test here. A test that
    # counts the reload itself patches it and has to switch this off, otherwise
    # the inner patch would hide the call from the outer one.
    if not patch_reload:
      return self.client.post(url, data)
    with patch('pygeoapi.admin.reload_pygeoapi'):
      return self.client.post(url, data)

  def collection_form_data(self, service, **overrides):
    return {
      'service': service.pk,
      'database_connection': self.connection.pk,
      'schema': 'public',
      'table': 'trees',
      'id_field': 'id',
      'title_field': 'name',
      'geom_field': 'geom',
      'storage_crs': StorageCrs.EPSG_25833,
      **overrides,
    }

  def make_saveable(self, collection=None, name='main'):
    """
    the change form only accepts a service metadata record that really exists;
    the collections of setUp() deliberately carry an unused identifier

    the record is created once per collection: the collection form hides every
    service already in use, so a second one would not be selectable anyway
    """
    collection = collection or self.collection
    services = self.__dict__.setdefault('services', {})
    if collection.pk not in services:
      service = self.create_service(f'{name}-{collection.pk}')
      collection.service_id = service.pk
      collection.save()
      services[collection.pk] = service
    return services[collection.pk]

  def save_roles(self, roles, collection=None, patch_reload=True, **overrides):
    """
    posts the change page of a collection with the role assignments given per
    attribute name and everything else left as rendered
    """
    collection = collection or self.collection
    service = self.make_saveable(collection)
    url = self.change_url(collection)
    response = self.client.get(url)
    data = self.collection_form_data(service, table=collection.table, **overrides)
    data.update(self.formset_data(response))
    fields = self.role_fields(response)
    for attribute_name, assigned in roles.items():
      data[fields[attribute_name]] = [role.pk for role in assigned]
    return self.post(url, data, patch_reload=patch_reload)


class CollectionAdminAttributeOverviewTest(CollectionAdminTestCase):
  """
  tests for the attribute overview on a collection's change page
  """

  def test_every_attribute_gets_one_row_with_all_its_roles(self):
    strasse = CollectionAttribute.objects.create(
      collection=self.collection, name='strasse', data_type='character varying(255)'
    )
    baumart = CollectionAttribute.objects.create(
      collection=self.collection, name='baumart', data_type='text'
    )
    for identifier, label in (('gruen', 'Grünamt'), ('tief', 'Tiefbauamt')):
      AttributeReadPermission.objects.create(
        role=Role.objects.create(identifier=identifier, label=label), attribute=strasse
      )
    rows = self.rows(self.get_change_page())
    self.assertEqual(len(rows), 2)
    self.assertEqual([row['name'] for row in rows], [baumart.name, strasse.name])
    self.assertEqual(rows[1]['data_type'], 'character varying(255)')
    # 'Bezeichnung (Bezeichner)': only the identifier is unique, two roles may
    # share a label
    self.assertEqual(rows[1]['roles'], 'Grünamt (gruen), Tiefbauamt (tief)')

  def test_attribute_without_assignment_shows_no_placeholder(self):
    CollectionAttribute.objects.create(collection=self.collection, name='strasse')
    row = self.rows(self.get_change_page())[0]
    # not merely "no role name": an admin-site placeholder such as a dash would
    # read like a role of that name
    self.assertEqual(row['roles'], '')

  def test_disappeared_attribute_stays_visible_with_its_roles(self):
    attribute = CollectionAttribute.objects.create(
      collection=self.collection, name='strasse', is_present=False
    )
    AttributeReadPermission.objects.create(
      role=Role.objects.create(identifier='gruen', label='Grünamt'), attribute=attribute
    )
    row = self.rows(self.get_change_page())[0]
    self.assertEqual(row['name'], 'strasse')
    self.assertIn('nicht mehr vorhanden', row['hint'])
    self.assertEqual(row['roles'], 'Grünamt (gruen)')

  def test_structural_attributes_are_marked(self):
    for name in ('id', 'name', 'geom'):
      CollectionAttribute.objects.create(collection=self.collection, name=name)
    hints = {row['name']: row['hint'] for row in self.rows(self.get_change_page())}
    self.assertIn('immer ausgeliefert', hints['id'])
    self.assertIn('immer ausgeliefert', hints['geom'])
    # a structural attribute has no role by design and is fine that way
    self.assertNotIn('von keiner Rolle lesbar', hints['id'])
    self.assertNotIn('von keiner Rolle lesbar', hints['geom'])
    # title_field is an ordinary properties attribute and is not delivered
    # without an explicitly granted read permission
    self.assertEqual(hints['name'], 'von keiner Rolle lesbar')

  def test_an_attribute_without_any_role_is_marked(self):
    role = Role.objects.create(identifier='gruen', label='Grünamt')
    CollectionAttribute.objects.create(collection=self.collection, name='baumart')
    AttributeReadPermission.objects.create(
      role=role,
      attribute=CollectionAttribute.objects.create(collection=self.collection, name='strasse'),
    )
    hints = {row['name']: row['hint'] for row in self.rows(self.get_change_page())}
    self.assertEqual(hints['baumart'], 'von keiner Rolle lesbar')
    # the other half of the criterion: the marking has to tell the two apart
    self.assertEqual(hints['strasse'], '')

  def test_a_disappeared_attribute_without_a_role_is_marked_as_both(self):
    CollectionAttribute.objects.create(
      collection=self.collection, name='strasse', is_present=False
    )
    row = self.rows(self.get_change_page())[0]
    self.assertIn('nicht mehr vorhanden', row['hint'])
    # marked, but deliberately not reported when saving; see
    # CollectionAdminMissingRolesTest
    self.assertIn('von keiner Rolle lesbar', row['hint'])

  def test_the_marking_follows_the_assignment(self):
    role = Role.objects.create(identifier='gruen', label='Grünamt')
    attribute = CollectionAttribute.objects.create(collection=self.collection, name='baumart')
    self.assertEqual(self.rows(self.get_change_page())[0]['hint'], 'von keiner Rolle lesbar')
    permission = AttributeReadPermission.objects.create(role=role, attribute=attribute)
    self.assertEqual(self.rows(self.get_change_page())[0]['hint'], '')
    # and back again once the last role is gone
    permission.delete()
    self.assertEqual(self.rows(self.get_change_page())[0]['hint'], 'von keiner Rolle lesbar')

  def test_empty_inventory_shows_the_pending_reconciliation(self):
    response = self.get_change_page()
    self.assertEqual(self.rows(response), [])
    self.assertContains(response, 'Noch kein Attributinventar')

  def test_add_page_shows_no_overview_but_a_hint(self):
    response = self.client.get(reverse('admin:pygeoapi_collection_add'))
    self.assertEqual(self.rows(response), [])
    self.assertNotContains(response, 'attributes-group')
    self.assertContains(response, 'Attribute erst nach dem Speichern.')

  def test_row_order_is_repeatable(self):
    for name in ('strasse', 'baumart', 'id', 'hoehe'):
      CollectionAttribute.objects.create(collection=self.collection, name=name)
    first = [row['name'] for row in self.rows(self.get_change_page())]
    second = [row['name'] for row in self.rows(self.get_change_page())]
    self.assertEqual(first, second)
    self.assertEqual(first, sorted(first))

  def test_the_overview_keeps_the_group_id_the_stylesheet_selects(self):
    # changeForm.css binds its corrections to #attributes-group; Django forms the
    # id from the related_name of the relation, so a rename there would silently
    # leave the stylesheet pointing at nothing
    self.assertContains(self.get_change_page(), 'id="attributes-group"')

  def test_number_of_queries_does_not_grow_with_the_data(self):
    roles = [
      Role.objects.create(identifier=f'role-{index}', label=f'Rolle {index}') for index in range(3)
    ]
    small = self.fill_inventory(self.create_collection(service_id=90002), 5, roles)
    large_collection = self.create_collection(service_id=90003, table='lamps')
    large = self.fill_inventory(large_collection, 100, roles)
    # the very first request of the test client also resolves session and user;
    # that one-off cost is not what is being measured here
    self.get_change_page(small)
    with CaptureQueriesContext(connections['default']) as few_attributes:
      self.get_change_page(small)
    with CaptureQueriesContext(connections['default']) as many_attributes:
      self.get_change_page(large)
    # an absolute number would be brittle; what is promised is that the number
    # does not grow with the amount of data
    self.assertEqual(len(many_attributes), len(few_attributes))

  def test_number_of_queries_does_not_grow_with_the_number_of_roles(self):
    few_roles = [
      Role.objects.create(identifier=f'few-{index}', label=f'Rolle {index}') for index in range(2)
    ]
    many_roles = [
      Role.objects.create(identifier=f'many-{index}', label=f'Rolle {index}')
      for index in range(40)
    ]
    small = self.fill_inventory(self.create_collection(service_id=90002), 5, few_roles)
    large = self.fill_inventory(self.create_collection(service_id=90003, table='lamps'), 5, [])
    self.get_change_page(small)
    with CaptureQueriesContext(connections['default']) as few:
      self.get_change_page(small)
    for attribute in large.attributes.all():
      for role in many_roles:
        AttributeReadPermission.objects.create(role=role, attribute=attribute)
    with CaptureQueriesContext(connections['default']) as many:
      self.get_change_page(large)
    self.assertEqual(len(many), len(few))

  def test_collection_can_still_be_changed_with_an_empty_inventory(self):
    service = self.create_service('empty')
    self.collection.service_id = service.pk
    self.collection.save()
    url = self.change_url()
    data = self.collection_form_data(service, table='lamps')
    data.update(self.formset_data(self.client.get(url)))
    self.assertEqual(self.post(url, data).status_code, 302)
    self.collection.refresh_from_db()
    self.assertEqual(self.collection.table, 'lamps')

  def test_collection_can_still_be_changed_with_a_filled_inventory(self):
    service = self.create_service('filled')
    self.collection.service_id = service.pk
    self.collection.save()
    CollectionAttribute.objects.create(collection=self.collection, name='strasse')
    url = self.change_url()
    data = self.collection_form_data(service, table='lamps')
    data.update(self.formset_data(self.client.get(url)))
    self.assertEqual(self.post(url, data).status_code, 302)
    self.collection.refresh_from_db()
    self.assertEqual(self.collection.table, 'lamps')
    # the overview must not touch the inventory it displays
    self.assertEqual(self.collection.attributes.count(), 1)

  def test_collection_can_still_be_added(self):
    service = self.create_service('added')
    url = reverse('admin:pygeoapi_collection_add')
    data = self.collection_form_data(service, table='benches')
    data.update(self.formset_data(self.client.get(url)))
    self.assertEqual(self.post(url, data).status_code, 302)
    self.assertEqual(Collection.objects.filter(service_id=service.pk).count(), 1)

  def test_membership_decides_access_to_the_overview(self):
    self.client.force_login(User.objects.create_user(username='outsider', is_staff=True))
    # superusers are exempt from this by Django's own rules, which is not a
    # finding but standard behaviour
    self.assertEqual(self.get_change_page().status_code, 403)


class CollectionAdminRoleAssignmentTest(CollectionAdminTestCase):
  """
  tests for assigning and revoking roles per attribute on a collection's change
  page
  """

  def setUp(self):
    super().setUp()
    self.gruen = Role.objects.create(identifier='gruen', label='Grünamt')
    self.tief = Role.objects.create(identifier='tief', label='Tiefbauamt')
    self.strasse = CollectionAttribute.objects.create(
      collection=self.collection, name='strasse', data_type='text'
    )
    self.baumart = CollectionAttribute.objects.create(
      collection=self.collection, name='baumart', data_type='text'
    )

  def permissions_of(self, attribute):
    return {
      permission.role.identifier: permission.pk
      for permission in attribute.read_permissions.select_related('role')
    }

  def test_every_row_offers_the_whole_role_catalog_as_a_search_list(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    response = self.get_change_page()
    rows = {row['name']: row for row in self.rows(response)}
    # a free text entry cannot create a role: the options are the catalog
    self.assertEqual(rows['baumart']['role_options'], ['Grünamt (gruen)', 'Tiefbauamt (tief)'])
    self.assertEqual(rows['baumart']['roles'], '')
    self.assertEqual(rows['strasse']['roles'], 'Grünamt (gruen)')
    self.assertEqual(self.role_fields(response)['strasse'], 'attributes-1-roles')
    # select2 turns the field into a search list with one chip per assigned role
    attrs = self.role_select_attrs(response)['strasse']
    self.assertIn('class="select2"', attrs)
    self.assertIn('multiple', attrs)
    self.assertIn('Rolle zuweisen', attrs)

  def test_an_assigned_role_creates_exactly_one_permission(self):
    self.assertEqual(self.save_roles({'strasse': [self.gruen]}).status_code, 302)
    self.assertEqual(AttributeReadPermission.objects.count(), 1)
    permission = AttributeReadPermission.objects.get()
    self.assertEqual(permission.role, self.gruen)
    self.assertEqual(permission.attribute, self.strasse)

  def test_several_roles_at_several_attributes_are_saved_in_one_go(self):
    response = self.save_roles(
      {'strasse': [self.gruen, self.tief], 'baumart': [self.tief]},
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(set(self.permissions_of(self.strasse)), {'gruen', 'tief'})
    self.assertEqual(set(self.permissions_of(self.baumart)), {'tief'})

  def test_a_revoked_role_deletes_exactly_that_permission(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    AttributeReadPermission.objects.create(role=self.tief, attribute=self.strasse)
    self.assertEqual(self.save_roles({'strasse': [self.tief]}).status_code, 302)
    self.assertEqual(set(self.permissions_of(self.strasse)), {'tief'})

  def test_assigning_and_revoking_happen_in_the_same_save(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    response = self.save_roles({'strasse': [self.tief], 'baumart': [self.gruen]})
    self.assertEqual(response.status_code, 302)
    self.assertEqual(set(self.permissions_of(self.strasse)), {'tief'})
    self.assertEqual(set(self.permissions_of(self.baumart)), {'gruen'})

  def test_an_unchanged_row_keeps_the_primary_keys_of_its_permissions(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    before = self.permissions_of(self.strasse)
    # no role assignment given: the helper posts the page exactly as rendered
    self.assertEqual(self.save_roles({}).status_code, 302)
    # equal primary keys prove that nothing was deleted and created anew
    self.assertEqual(self.permissions_of(self.strasse), before)

  def test_a_revocation_leaves_other_roles_and_attributes_untouched(self):
    for attribute in (self.strasse, self.baumart):
      for role in (self.gruen, self.tief):
        AttributeReadPermission.objects.create(role=role, attribute=attribute)
    untouched = self.permissions_of(self.baumart)
    remaining = self.permissions_of(self.strasse)['tief']
    self.assertEqual(self.save_roles({'strasse': [self.tief]}).status_code, 302)
    self.assertEqual(self.permissions_of(self.strasse), {'tief': remaining})
    self.assertEqual(self.permissions_of(self.baumart), untouched)

  def test_the_same_role_key_twice_creates_exactly_one_permission(self):
    service = self.make_saveable()
    url = self.change_url()
    response = self.client.get(url)
    data = self.collection_form_data(service)
    data.update(self.formset_data(response))
    data[self.role_fields(response)['strasse']] = [self.gruen.pk, self.gruen.pk]
    self.assertEqual(self.post(url, data).status_code, 302)
    self.assertEqual(AttributeReadPermission.objects.count(), 1)

  def test_saving_an_assigned_role_again_changes_nothing(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    before = self.permissions_of(self.strasse)
    entries = LogEntry.objects.count()
    self.assertEqual(self.save_roles({'strasse': [self.gruen]}).status_code, 302)
    self.assertEqual(self.permissions_of(self.strasse), before)
    # the collection itself was saved, but no permission changed, so the history
    # carries no entry about a role
    self.assertNotIn('Rolle', LogEntry.objects.latest('id').get_change_message())
    self.assertEqual(LogEntry.objects.count(), entries + 1)

  def test_the_role_field_of_a_structural_attribute_is_disabled(self):
    for name in ('id', 'geom'):
      CollectionAttribute.objects.create(collection=self.collection, name=name)
    rows = {row['name']: row for row in self.rows(self.get_change_page())}
    self.assertTrue(rows['id']['roles_disabled'])
    self.assertTrue(rows['geom']['roles_disabled'])
    # an ordinary attribute stays assignable
    self.assertFalse(rows['strasse']['roles_disabled'])

  def test_a_forged_post_cannot_assign_a_role_to_a_structural_attribute(self):
    identifier = CollectionAttribute.objects.create(collection=self.collection, name='id')
    service = self.make_saveable()
    url = self.change_url()
    response = self.client.get(url)
    data = self.collection_form_data(service)
    data.update(self.formset_data(response))
    data[self.role_fields(response)['id']] = [self.gruen.pk]
    self.assertEqual(self.post(url, data).status_code, 302)
    self.assertEqual(identifier.read_permissions.count(), 0)

  def test_a_right_on_a_structural_attribute_stays_and_is_marked(self):
    # arises when id_field is renamed afterwards and a right granted regularly
    # before thereby falls onto a structural row
    identifier = CollectionAttribute.objects.create(collection=self.collection, name='id')
    AttributeReadPermission.objects.create(role=self.gruen, attribute=identifier)
    before = self.permissions_of(identifier)
    row = {row['name']: row for row in self.rows(self.get_change_page())}['id']
    self.assertIn('immer ausgeliefert', row['hint'])
    self.assertIn('wirkungsloses Recht', row['hint'])
    self.assertEqual(self.save_roles({}).status_code, 302)
    self.assertEqual(self.permissions_of(identifier), before)

  def test_an_unknown_role_key_is_reported_as_a_field_error(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    before = self.permissions_of(self.strasse)
    service = self.make_saveable()
    url = self.change_url()
    response = self.client.get(url)
    data = self.collection_form_data(service)
    data.update(self.formset_data(response))
    data[self.role_fields(response)['strasse']] = [self.gruen.pk, 999999]
    result = self.post(url, data)
    # the form is rendered again with a message, not a server error
    self.assertEqual(result.status_code, 200)
    self.assertContains(result, 'errorlist')
    self.assertEqual(self.permissions_of(self.strasse), before)

  def test_the_reload_happens_once_per_save_regardless_of_the_changes(self):
    for number_of_changed_rows, assignment in (
      (1, {'strasse': [self.gruen]}),
      (2, {'strasse': [self.tief], 'baumart': [self.gruen, self.tief]}),
      (0, {}),
    ):
      with self.subTest(changed_rows=number_of_changed_rows):
        # the callback of on_commit() never runs inside a TestCase, which never
        # commits; without capturing it the counter would always stay at zero
        with patch('pygeoapi.admin.reload_pygeoapi') as reload_pygeoapi:
          with self.captureOnCommitCallbacks(execute=True):
            response = self.save_roles(assignment, patch_reload=False)
            self.assertEqual(response.status_code, 302)
            # still inside the transaction: a reload started here would read the
            # database over its own connection and could not see the uncommitted
            # permissions. Without this assertion the test would stay green even
            # if reload_pygeoapi were called directly instead of via on_commit.
            reload_pygeoapi.assert_not_called()
        reload_pygeoapi.assert_called_once()

  def test_a_failed_save_leaves_the_permissions_untouched(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    before = self.permissions_of(self.strasse)
    entries = LogEntry.objects.count()
    service = self.make_saveable()
    url = self.change_url()
    response = self.client.get(url)
    data = self.collection_form_data(service)
    data.update(self.formset_data(response))
    # an empty service makes the collection form itself invalid
    data['service'] = ''
    data[self.role_fields(response)['strasse']] = [self.tief.pk]
    with patch('pygeoapi.admin.reload_pygeoapi') as reload_pygeoapi:
      with self.captureOnCommitCallbacks(execute=True):
        result = self.client.post(url, data)
    self.assertEqual(result.status_code, 200)
    self.assertEqual(self.permissions_of(self.strasse), before)
    self.assertEqual(AttributeReadPermission.objects.count(), 1)
    self.assertEqual(LogEntry.objects.count(), entries)
    reload_pygeoapi.assert_not_called()

  def test_the_object_history_names_attribute_role_and_direction(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    self.assertEqual(
      self.save_roles({'strasse': [self.tief], 'baumart': [self.gruen]}).status_code, 302
    )
    entry = LogEntry.objects.latest('id')
    message = entry.get_change_message()
    self.assertIn('strasse', message)
    self.assertIn('baumart', message)
    self.assertIn('Grünamt (gruen)', message)
    self.assertIn('Tiefbauamt (tief)', message)
    self.assertIn('zugewiesen', message)
    self.assertIn('entzogen', message)
    self.assertEqual(entry.user, self.user)
    self.assertIsNotNone(entry.action_time)

  def test_membership_decides_whether_roles_can_be_assigned(self):
    service = self.make_saveable()
    url = self.change_url()
    response = self.client.get(url)
    data = self.collection_form_data(service)
    data.update(self.formset_data(response))
    data[self.role_fields(response)['strasse']] = [self.gruen.pk]
    self.client.force_login(User.objects.create_user(username='outsider', is_staff=True))
    self.assertEqual(self.client.get(url).status_code, 403)
    self.assertEqual(self.post(url, data).status_code, 403)
    self.assertEqual(AttributeReadPermission.objects.count(), 0)

  def test_without_the_change_permission_the_roles_are_shown_as_text(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    self.client.force_login(self.reader())
    rows = {row['name']: row for row in self.rows(self.get_change_page())}
    # the display fallback of the inline, not the form field: the column carries
    # the role labels as text and offers no way to change them
    self.assertEqual(rows['strasse']['roles'], 'Grünamt')
    self.assertNotIn('role_options', rows['strasse'])
    self.assertEqual(rows['baumart']['roles'], '')

  def reader(self):
    """
    a user who may see the collection but not change its attributes; the
    permissions come from the group of the maintainer minus the single one that
    decides whether the roles column is a form field
    """
    reader = User.objects.create_user(username='reader', is_staff=True)
    reader.user_permissions.set(
      Group.objects.get(name=GROUP).permissions.exclude(codename='change_collectionattribute')
    )
    return reader

  def test_number_of_queries_when_saving_does_not_grow_with_the_number_of_roles(self):
    few_roles = [
      Role.objects.create(identifier=f'few-{index}', label=f'Rolle {index}') for index in range(2)
    ]
    many_roles = [
      Role.objects.create(identifier=f'many-{index}', label=f'Rolle {index}')
      for index in range(40)
    ]
    small = self.create_collection(service_id=90002)
    self.fill_inventory(small, 10, [])
    large = self.create_collection(service_id=90003, table='lamps')
    self.fill_inventory(large, 10, [])
    # both collections are saved once beforehand: the first request of the test
    # client also resolves session and user, and the service metadata record is
    # created on the first save
    self.save_roles({}, collection=small)
    self.save_roles({}, collection=large)
    with CaptureQueriesContext(connections['default']) as few:
      self.save_roles({'attribut_000': few_roles}, collection=small)
    with CaptureQueriesContext(connections['default']) as many:
      self.save_roles({'attribut_000': many_roles}, collection=large)
    # the catalog is loaded once per request and the difference is written with
    # one bulk_create and one delete, no matter how many roles are involved
    self.assertEqual(len(many), len(few))

  def test_writing_the_permissions_costs_the_same_for_one_and_for_many_rows(self):
    roles = [
      Role.objects.create(identifier=f'role-{index}', label=f'Rolle {index}') for index in range(3)
    ]
    collection = self.create_collection(service_id=90002)
    self.fill_inventory(collection, 20, [])
    self.save_roles({}, collection=collection)
    with CaptureQueriesContext(connections['default']) as one_row:
      self.save_roles({'attribut_000': roles}, collection=collection)
    with CaptureQueriesContext(connections['default']) as ten_rows:
      self.save_roles(
        {f'attribut_{index:03d}': roles for index in range(1, 11)}, collection=collection
      )
    # comparing the numbers instead of asserting an absolute one: an absolute
    # value would be brittle and would not check what is promised. What is
    # promised here is that the permissions are written with a constant number of
    # queries; the number of rows the formset itself costs is Django's own and
    # unchanged (see docs/pygeoapi/rechtesystem.md).
    self.assertEqual(len(ten_rows), len(one_row))


class CollectionAdminAttributeSearchTest(CollectionAdminTestCase):
  """
  tests for the search above the attribute overview on a collection's change page

  asserted here is the markup contract the browser-side module relies on; its
  behaviour is covered by pygeoapi/tests/js/attributeFilter.test.js
  """

  def setUp(self):
    super().setUp()
    self.gruen = Role.objects.create(identifier='gruen', label='Grünamt')
    self.tief = Role.objects.create(identifier='tief', label='Tiefbauamt')

  def search_block(self, response):
    """
    the controls of the search block, by their role in it; a missing one is absent
    from the result, so that a whole missing block is one assertion
    """
    content = response.content.decode()
    found = {}
    for key, pattern in (
      ('input', SEARCH_INPUT),
      ('reset', SEARCH_RESET),
      ('status', SEARCH_STATUS),
    ):
      match = pattern.search(content)
      if match:
        found[key] = match.group(0)
    return found

  def test_the_block_offers_a_search_field_a_reset_and_a_status(self):
    CollectionAttribute.objects.create(collection=self.collection, name='strasse')
    block = self.search_block(self.get_change_page())
    self.assertEqual(set(block), {'input', 'reset', 'status'})
    self.assertIn('type="search"', block['input'])
    # the default value submit would save the collection instead of resetting
    self.assertIn('type="button"', block['reset'])
    # without it the hint on an empty result is not announced
    self.assertIn('role="status"', block['status'])

  def test_neither_control_reaches_the_post_of_the_change_page(self):
    CollectionAttribute.objects.create(collection=self.collection, name='strasse')
    block = self.search_block(self.get_change_page())
    # with a name attribute both would land in the POST as foreign keys
    for key in ('input', 'reset'):
      with self.subTest(control=key):
        self.assertIsNone(NAME_ATTRIBUTE.search(block[key]))

  def test_the_block_names_the_group_whose_rows_it_filters(self):
    CollectionAttribute.objects.create(collection=self.collection, name='strasse')
    response = self.get_change_page()
    group = FILTER_GROUP.search(response.content.decode())
    self.assertIsNotNone(group)
    # the module resolves the rows through this id; Django forms it from the
    # related_name of the relation
    self.assertContains(response, f'id="{group.group(1)}"')

  def test_every_row_offers_the_name_cell_the_filter_reads(self):
    names = ['strasse', 'baumart', 'hoehe']
    for name in names:
      CollectionAttribute.objects.create(collection=self.collection, name=name)
    rows = self.rows(self.get_change_page())
    # CELL matches exactly the selector the module reads the name from. The
    # bracket to the jsdom fixture: a Django upgrade changing the shape of a
    # readonly cell turns this red instead of only breaking the filtering.
    self.assertEqual(sorted(row['name'] for row in rows), sorted(names))

  def test_an_empty_inventory_shows_no_search_block(self):
    response = self.get_change_page()
    self.assertContains(response, 'Noch kein Attributinventar')
    self.assertEqual(self.search_block(response), {})

  def test_the_add_page_shows_no_search_block(self):
    response = self.client.get(reverse('admin:pygeoapi_collection_add'))
    self.assertEqual(self.search_block(response), {})

  def test_the_block_costs_no_query_and_is_there_at_a_hundred_attributes(self):
    roles = [self.gruen, self.tief]
    small = self.fill_inventory(self.create_collection(service_id=90002), 5, roles)
    large = self.fill_inventory(
      self.create_collection(service_id=90003, table='lamps'), 100, roles
    )
    # the very first request of the test client also resolves session and user
    self.get_change_page(small)
    with CaptureQueriesContext(connections['default']) as few_attributes:
      self.get_change_page(small)
    with CaptureQueriesContext(connections['default']) as many_attributes:
      response = self.get_change_page(large)
    # the block is static markup and reads no data, so the promise of the overview
    # still holds: the number does not grow with the data
    self.assertEqual(len(many_attributes), len(few_attributes))
    self.assertEqual(set(self.search_block(response)), {'input', 'reset', 'status'})
    self.assertEqual(len(self.rows(response)), 100)

  def test_a_post_of_the_rendered_state_changes_no_right(self):
    """
    the server-side half of the criterion "saving with an active filter": a hidden
    row keeps its fields in the DOM, so the browser posts the rendered state –
    which is this POST
    """
    attributes = {
      name: CollectionAttribute.objects.create(
        collection=self.collection, name=name, data_type='text'
      )
      for name in ('baumart', 'hoehe', 'strasse', 'strassenname')
    }
    # a mixed starting point: two roles, one role and none at all
    AttributeReadPermission.objects.create(role=self.gruen, attribute=attributes['strasse'])
    AttributeReadPermission.objects.create(role=self.tief, attribute=attributes['strasse'])
    AttributeReadPermission.objects.create(role=self.gruen, attribute=attributes['baumart'])
    before = {
      permission.pk: (permission.attribute_id, permission.role_id)
      for permission in AttributeReadPermission.objects.all()
    }
    entries = LogEntry.objects.count()
    self.assertEqual(self.save_roles({}).status_code, 302)
    after = {
      permission.pk: (permission.attribute_id, permission.role_id)
      for permission in AttributeReadPermission.objects.all()
    }
    # equal primary keys prove that nothing was deleted and created anew
    self.assertEqual(after, before)
    # Django logs every successful change POST; no role may appear in it
    self.assertEqual(LogEntry.objects.count(), entries + 1)
    self.assertNotIn('Rolle', LogEntry.objects.latest('id').get_change_message())


class CollectionAdminMissingRolesTest(CollectionAdminTestCase):
  """
  tests for the report of the attributes no role may read, on saving a collection
  """

  def setUp(self):
    super().setUp()
    self.gruen = Role.objects.create(identifier='gruen', label='Grünamt')
    self.strasse = CollectionAttribute.objects.create(
      collection=self.collection, name='strasse', data_type='text'
    )
    self.baumart = CollectionAttribute.objects.create(
      collection=self.collection, name='baumart', data_type='text'
    )

  def warnings(self, response):
    """
    the warnings of a POST response

    read from the response and not from its body: the successful case is a 302
    with an empty body, so an assertNotContains on it would be green for free.
    Deliberately no override_settings(MESSAGE_STORAGE=CookieStorage) either,
    although five other apps use that pattern: pure CookieStorage discards
    silently on overflow, where in production the session fallback steps in.
    """
    return [
      str(message)
      for message in get_messages(response.wsgi_request)
      if message.level == messages.WARNING
    ]

  def test_the_message_names_the_attributes_in_table_order_and_their_number(self):
    response = self.save_roles({})
    self.assertEqual(response.status_code, 302)
    warning = self.warnings(response)
    self.assertEqual(len(warning), 1)
    self.assertIn('2 Attribute', warning[0])
    # the order of the overview, not the order of creation
    self.assertIn('baumart, strasse', warning[0])
    self.assertIn('von keiner Rolle gelesen werden', warning[0])

  def test_no_warning_when_every_attribute_has_a_role(self):
    response = self.save_roles({'strasse': [self.gruen], 'baumart': [self.gruen]})
    self.assertEqual(response.status_code, 302)
    self.assertEqual(self.warnings(response), [])

  def test_the_collection_is_saved_despite_the_warning(self):
    response = self.save_roles({}, title_field='bezeichnung')
    self.assertEqual(len(self.warnings(response)), 1)
    self.collection.refresh_from_db()
    self.assertEqual(self.collection.title_field, 'bezeichnung')

  def test_assigning_the_last_role_silences_the_warning_in_the_same_save(self):
    # the regression test against the stale prefetch: computing from
    # read_permissions.all() instead of cleaned_data would still name 'strasse'
    response = self.save_roles({'strasse': [self.gruen], 'baumart': [self.gruen]})
    self.assertEqual(self.warnings(response), [])
    self.assertEqual(AttributeReadPermission.objects.count(), 2)

  def test_revoking_the_last_role_warns_in_the_same_save(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.baumart)
    response = self.save_roles({'strasse': []})
    warning = self.warnings(response)
    self.assertEqual(len(warning), 1)
    self.assertIn('strasse', warning[0])
    self.assertNotIn('baumart', warning[0])

  def test_a_newly_added_attribute_is_reported_without_any_action(self):
    """
    an attribute the reconciliation (DH-77) adds is free of rights by design and
    is reported on the next save without anyone touching it
    """
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.baumart)
    CollectionAttribute.objects.create(collection=self.collection, name='hoehe')
    warning = self.warnings(self.save_roles({}))
    self.assertEqual(len(warning), 1)
    self.assertIn('Ein Attribut', warning[0])
    self.assertIn('hoehe', warning[0])
    # and it is not given a role of its own accord
    self.assertEqual(AttributeReadPermission.objects.filter(attribute__name='hoehe').count(), 0)

  def test_a_disappeared_attribute_does_not_warn(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.baumart)
    CollectionAttribute.objects.create(collection=self.collection, name='hoehe', is_present=False)
    # marked in the overview, but without effect anyway and therefore nothing to act on
    self.assertEqual(self.warnings(self.save_roles({})), [])

  def test_structural_attributes_do_not_warn(self):
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.strasse)
    AttributeReadPermission.objects.create(role=self.gruen, attribute=self.baumart)
    for name in ('id', 'geom'):
      CollectionAttribute.objects.create(collection=self.collection, name=name)
    self.assertEqual(self.warnings(self.save_roles({})), [])

  def test_the_message_is_capped_and_still_gives_the_total_number(self):
    collection = self.create_collection(service_id=90002, table='lamps')
    self.fill_inventory(collection, 12, [])
    warning = self.warnings(self.save_roles({}, collection=collection))
    self.assertEqual(len(warning), 1)
    self.assertIn('12 Attribute', warning[0])
    self.assertIn('attribut_009', warning[0])
    self.assertNotIn('attribut_010', warning[0])
    self.assertIn('und 2 weitere', warning[0])

  def test_a_deactivated_collection_warns_as_well(self):
    # the statement is true regardless of whether the collection is delivered
    response = self.save_roles({}, deactivated='on')
    self.assertEqual(len(self.warnings(response)), 1)
    self.collection.refresh_from_db()
    self.assertTrue(self.collection.deactivated)

  def test_an_empty_inventory_does_not_warn(self):
    collection = self.create_collection(service_id=90002, table='lamps')
    self.assertEqual(self.warnings(self.save_roles({}, collection=collection)), [])

  def test_the_add_page_does_not_warn(self):
    service = self.create_service('added')
    url = reverse('admin:pygeoapi_collection_add')
    data = self.collection_form_data(service, table='benches')
    data.update(self.formset_data(self.client.get(url)))
    response = self.post(url, data)
    self.assertEqual(response.status_code, 302)
    self.assertEqual(self.warnings(response), [])

  def test_a_failed_save_does_not_warn(self):
    service = self.make_saveable()
    url = self.change_url()
    data = self.collection_form_data(service)
    data.update(self.formset_data(self.client.get(url)))
    # an empty service makes the collection form itself invalid
    data['service'] = ''
    response = self.post(url, data)
    self.assertEqual(response.status_code, 200)
    self.assertEqual(self.warnings(response), [])

  def test_the_warning_does_not_appear_in_the_object_history(self):
    entries = LogEntry.objects.count()
    self.assertEqual(len(self.warnings(self.save_roles({}, title_field='bezeichnung'))), 1)
    self.assertEqual(LogEntry.objects.count(), entries + 1)
    self.assertNotIn('keiner Rolle', LogEntry.objects.latest('id').get_change_message())

  def test_an_attribute_name_is_escaped_in_the_message_band(self):
    CollectionAttribute.objects.create(
      collection=self.collection, name='<script>alert(1)</script>'
    )
    response = self.save_roles({})
    self.assertIn('<script>alert(1)</script>', self.warnings(response)[0])
    # the only place where asserting on rendered HTML is warranted: the message
    # band is where the name reaches the page
    changelist = self.client.get(response['Location'])
    self.assertNotContains(changelist, '<script>alert(1)</script>')
    self.assertContains(changelist, '&lt;script&gt;alert(1)&lt;/script&gt;')

  def test_the_number_of_queries_of_the_page_does_not_grow_with_the_data(self):
    few = self.fill_inventory(self.create_collection(service_id=90002), 5, [])
    many = self.fill_inventory(self.create_collection(service_id=90003, table='lamps'), 100, [])
    # an inventory entirely without rights, which no existing test covers
    self.get_change_page(few)
    with CaptureQueriesContext(connections['default']) as few_attributes:
      self.get_change_page(few)
    with CaptureQueriesContext(connections['default']) as many_attributes:
      self.get_change_page(many)
    self.assertEqual(len(many_attributes), len(few_attributes))

  def test_the_number_of_queries_when_saving_does_not_depend_on_the_rights(self):
    role = Role.objects.create(identifier='alle', label='Alle')
    without = self.create_collection(service_id=90002)
    self.fill_inventory(without, 10, [])
    complete = self.create_collection(service_id=90003, table='lamps')
    self.fill_inventory(complete, 10, [role])
    # both runs carry the same number of attributes and differ only in the rights;
    # with an unequal number this would measure Django's pre-existing query per
    # formset row instead of the new check
    self.save_roles({}, collection=without)
    self.save_roles({}, collection=complete)
    with CaptureQueriesContext(connections['default']) as none_with_a_role:
      self.save_roles({}, collection=without)
    with CaptureQueriesContext(connections['default']) as all_with_a_role:
      self.save_roles({}, collection=complete)
    self.assertEqual(len(none_with_a_role), len(all_with_a_role))


class CollectionAdminReconcileTest(CollectionAdminTestCase):
  """
  tests for triggering the reconciliation of the attribute inventory from a
  collection's change page

  asserted here is the markup contract the browser-side module relies on and the
  behaviour of the whole POST; the module itself is covered by
  pygeoapi/tests/js/attributeReconcile.test.js, the reconcile logic by
  pygeoapi/tests/test_collection_reconcile.py
  """

  def setUp(self):
    super().setUp()
    self.gruen = Role.objects.create(identifier='gruen', label='Grünamt')

  def columns(self, *pairs):
    return [{'name': name, 'type': data_type} for name, data_type in pairs]

  def reconcile(self, columns=None, collection=None, raw=None, marker='1', **overrides):
    """
    posts the change page the way the button does: everything as rendered, plus
    the marker and the column list as JSON
    """
    collection = collection or self.collection
    service = self.make_saveable(collection)
    url = self.change_url(collection)
    response = self.client.get(url)
    data = self.collection_form_data(service, table=collection.table, **overrides)
    data.update(self.formset_data(response))
    data['reconcile'] = marker
    data['reconcile_columns'] = raw if raw is not None else json.dumps(columns or [])
    # the browser adds it so that the overview shows the new state right away
    data['_continue'] = '1'
    return self.post(url, data)

  def notes(self, response, level=messages.INFO):
    return [
      str(message) for message in get_messages(response.wsgi_request) if message.level == level
    ]

  def inventory(self, collection=None):
    collection = collection or self.collection
    return {
      attribute.name: (attribute.data_type, attribute.is_present)
      for attribute in collection.attributes.all()
    }

  def test_the_button_carries_the_url_of_the_column_information(self):
    response = self.get_change_page()
    button = RECONCILE_BUTTON.search(response.content.decode())
    self.assertIsNotNone(button)
    # the default value submit would save the collection instead of fetching first
    self.assertIn('type="button"', button.group(0))
    # with a name attribute the button would land in the POST as a foreign key
    self.assertIsNone(NAME_ATTRIBUTE.search(button.group(0)))
    url = COLUMNS_URL.search(button.group(0))
    self.assertIsNotNone(url)
    self.assertEqual(url.group(1), reverse('pygeoapi:get_database_columns'))
    self.assertIsNotNone(RECONCILE_STATUS.search(response.content.decode()))

  def test_the_button_names_that_it_saves_along(self):
    # the reconcile saves the whole form; the label alone reads like a pure read
    button = RECONCILE_BUTTON.search(self.get_change_page().content.decode())
    self.assertIn('title="Der Abgleich sichert die Kollektion mit allen offenen', button.group(0))

  def test_the_button_is_there_in_both_branches_of_the_overview(self):
    empty = self.get_change_page()
    self.assertContains(empty, 'Noch kein Attributinventar')
    self.assertIsNotNone(RECONCILE_BUTTON.search(empty.content.decode()))
    CollectionAttribute.objects.create(collection=self.collection, name='strasse')
    filled = self.get_change_page()
    self.assertIsNotNone(RECONCILE_BUTTON.search(filled.content.decode()))

  def test_the_add_page_offers_no_reconcile(self):
    content = self.client.get(reverse('admin:pygeoapi_collection_add')).content.decode()
    # nothing to reconcile before the source of the collection is saved
    self.assertIsNone(RECONCILE_BUTTON.search(content))
    for field in ('reconcile', 'reconcile_columns'):
      with self.subTest(field=field):
        self.assertIsNone(re.search(HIDDEN_FIELD.format(field), content))

  def test_the_change_page_carries_both_hidden_fields_inside_the_form(self):
    content = self.get_change_page().content.decode()
    for field in ('reconcile', 'reconcile_columns'):
      with self.subTest(field=field):
        tag = re.search(HIDDEN_FIELD.format(field), content)
        self.assertIsNotNone(tag)
        self.assertIn('type="hidden"', tag.group(0))
        self.assertIn(f'name="{field}"', tag.group(0))
    # inside the change form and not inside the logout form of the header
    form = content.split('id="collection_form"', 1)[1].split('</form>', 1)[0]
    self.assertIn('id="id_reconcile"', form)
    self.assertIn('id="id_reconcile_columns"', form)

  def test_a_reconcile_fills_the_inventory_and_the_table_shows_it(self):
    response = self.reconcile(self.columns(('id', 'integer'), ('baumart', 'text')))
    self.assertEqual(response.status_code, 302)
    # _continue leads back to the change page, so the overview shows the new state
    self.assertEqual(response['Location'], self.change_url())
    rows = {row['name']: row for row in self.rows(self.client.get(response['Location']))}
    self.assertEqual(set(rows), {'id', 'baumart'})
    self.assertEqual(rows['baumart']['data_type'], 'text')
    self.assertEqual(rows['id']['data_type'], 'integer')

  def test_the_message_names_all_four_numbers(self):
    CollectionAttribute.objects.create(
      collection=self.collection, name='strasse', data_type='text'
    )
    CollectionAttribute.objects.create(
      collection=self.collection, name='hoehe', data_type='text', is_present=False
    )
    CollectionAttribute.objects.create(
      collection=self.collection, name='baumart', data_type='text'
    )
    response = self.reconcile(
      self.columns(('id', 'integer'), ('hoehe', 'text'), ('baumart', 'integer'))
    )
    note = self.notes(response)
    self.assertEqual(len(note), 1)
    self.assertIn('1 Attribut neu aufgenommen', note[0])
    self.assertIn('1 als „nicht mehr vorhanden“ gekennzeichnet', note[0])
    self.assertIn('1 wieder aufgetaucht', note[0])
    self.assertIn('1 Datentyp aktualisiert', note[0])

  def test_a_repeated_reconcile_reports_no_change_and_changes_nothing(self):
    columns = self.columns(('id', 'integer'), ('baumart', 'text'))
    self.reconcile(columns)
    before = {
      attribute.pk: (attribute.name, attribute.data_type, attribute.is_present)
      for attribute in self.collection.attributes.all()
    }
    response = self.reconcile(columns)
    self.assertEqual(self.notes(response), ['Der Abgleich hat keine Änderung ergeben.'])
    after = {
      attribute.pk: (attribute.name, attribute.data_type, attribute.is_present)
      for attribute in self.collection.attributes.all()
    }
    # equal primary keys prove that nothing was deleted and created anew
    self.assertEqual(after, before)

  def test_a_marker_without_columns_warns_and_leaves_the_inventory_untouched(self):
    CollectionAttribute.objects.create(
      collection=self.collection, name='strasse', data_type='text'
    )
    response = self.reconcile([])
    # 'strasse' has no role, so the warning of DH-75 accompanies this save
    warning = [
      message for message in self.notes(response, messages.WARNING) if 'Spaltenliste' in message
    ]
    self.assertEqual(len(warning), 1)
    self.assertIn('ohne Spaltenliste an', warning[0])
    self.assertIn('bleibt unverändert', warning[0])
    # an empty result is never read as "every attribute vanished"
    self.assertEqual(self.inventory(), {'strasse': ('text', True)})

  def test_an_ordinary_save_without_the_marker_reconciles_nothing(self):
    CollectionAttribute.objects.create(collection=self.collection, name='strasse')
    response = self.reconcile(self.columns(('baumart', 'text')), marker='')
    self.assertEqual(response.status_code, 302)
    self.assertEqual(self.notes(response), [])
    self.assertEqual(set(self.inventory()), {'strasse'})

  def test_the_reconcile_opens_no_connection_to_the_source(self):
    # the columns come from the browser; the source is not touched at reconcile time
    with patch('pygeoapi.views.functions.create_database_connection') as connect:
      self.reconcile(self.columns(('baumart', 'text')))
    connect.assert_not_called()

  def test_permissions_survive_vanishing_and_reappearing_through_the_mask(self):
    self.reconcile(self.columns(('strasse', 'text')))
    attribute = self.collection.attributes.get(name='strasse')
    permission = AttributeReadPermission.objects.create(role=self.gruen, attribute=attribute)
    self.reconcile(self.columns(('baumart', 'text')))
    attribute.refresh_from_db()
    self.assertFalse(attribute.is_present)
    self.assertEqual(AttributeReadPermission.objects.get().pk, permission.pk)
    response = self.reconcile(self.columns(('strasse', 'text'), ('baumart', 'text')))
    self.assertIn('1 wieder aufgetaucht', self.notes(response)[0])
    attribute.refresh_from_db()
    self.assertTrue(attribute.is_present)
    # same permission row on the same attribute row: nothing came back free of rights
    self.assertEqual(AttributeReadPermission.objects.get().pk, permission.pk)
    self.assertEqual(self.collection.attributes.get(name='strasse').pk, attribute.pk)

  def test_a_column_list_that_is_no_json_is_rejected(self):
    response = self.reconcile(raw='keine Liste')
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'nicht lesbar')
    self.assertEqual(self.inventory(), {})

  def test_a_column_list_that_is_no_list_is_rejected(self):
    response = self.reconcile(raw=json.dumps({'name': 'baumart'}))
    self.assertContains(response, 'muss eine Liste sein')
    self.assertEqual(self.inventory(), {})

  def test_an_entry_without_a_name_is_rejected(self):
    response = self.reconcile(raw=json.dumps([{'type': 'text'}]))
    self.assertContains(response, 'keinen Namen')
    self.assertEqual(self.inventory(), {})

  def test_a_name_that_is_too_long_is_rejected(self):
    response = self.reconcile(self.columns(('a' * 101, 'text')))
    self.assertContains(response, 'länger als die zugelassenen 100 Zeichen')
    self.assertEqual(self.inventory(), {})

  def test_a_duplicate_name_is_rejected_understandably(self):
    # the duplicate is named, not left to the unique constraint of the model
    response = self.reconcile(self.columns(('baumart', 'text'), ('baumart', 'integer')))
    self.assertContains(response, 'baumart')
    self.assertContains(response, 'mehrfach vor')
    self.assertEqual(self.inventory(), {})

  def test_a_column_list_beyond_the_limit_is_rejected(self):
    columns = self.columns(*((f'attribut_{index:03d}', 'text') for index in range(101)))
    response = self.reconcile(columns)
    self.assertContains(response, 'mehr als die zugelassenen 100')
    self.assertEqual(self.inventory(), {})

  def test_a_list_at_the_limit_is_accepted(self):
    columns = self.columns(*((f'attribut_{index:03d}', 'text') for index in range(100)))
    self.assertEqual(self.reconcile(columns).status_code, 302)
    self.assertEqual(self.collection.attributes.count(), 100)

  @override_settings(PYGEOAPI_MAX_COLUMNS=120)
  def test_a_raised_limit_lets_a_wider_source_through(self):
    columns = self.columns(*((f'attribut_{index:03d}', 'text') for index in range(110)))
    self.assertEqual(self.reconcile(columns).status_code, 302)
    self.assertEqual(self.collection.attributes.count(), 110)

  @override_settings(PYGEOAPI_MAX_COLUMNS=2)
  def test_a_lowered_limit_names_its_own_number(self):
    response = self.reconcile(self.columns(('a', 'text'), ('b', 'text'), ('c', 'text')))
    self.assertContains(response, 'mehr als die zugelassenen 2')
    self.assertEqual(self.inventory(), {})

  def test_a_rejected_reconcile_saves_nothing_at_all(self):
    response = self.reconcile(raw='{', title_field='bezeichnung')
    self.assertEqual(response.status_code, 200)
    self.collection.refresh_from_db()
    # the whole form is invalid: neither the inventory nor the collection changed
    self.assertEqual(self.collection.title_field, 'name')
    self.assertEqual(self.inventory(), {})

  def test_a_data_type_that_is_too_long_leaves_the_field_empty(self):
    response = self.reconcile(self.columns(('baumart', 'x' * 101)))
    self.assertEqual(response.status_code, 302)
    # not shortened: a cut value would pretend a type the source does not state
    self.assertEqual(self.inventory(), {'baumart': ('', True)})

  def test_the_reload_happens_once_per_reconcile(self):
    with patch('pygeoapi.admin.reload_pygeoapi') as reload_pygeoapi:
      with self.captureOnCommitCallbacks(execute=True):
        service = self.make_saveable()
        url = self.change_url()
        data = self.collection_form_data(service)
        data.update(self.formset_data(self.client.get(url)))
        data['reconcile'] = '1'
        data['reconcile_columns'] = json.dumps(self.columns(('id', 'integer')))
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        reload_pygeoapi.assert_not_called()
    reload_pygeoapi.assert_called_once()

  def test_the_object_history_names_the_inventory(self):
    CollectionAttribute.objects.create(
      collection=self.collection, name='strasse', data_type='text'
    )
    self.reconcile(self.columns(('baumart', 'text')))
    message = LogEntry.objects.latest('id').get_change_message()
    self.assertIn('Attributinventar', message)
    # lowered, because Django capitalises the first of the listed fields
    self.assertIn('aufgenommen: baumart', message.lower())
    self.assertIn('nicht mehr vorhanden: strasse', message)
    # the technical carrier fields of the reconcile do not belong in here
    self.assertNotIn('Spaltenliste', message)

  def test_a_reconcile_without_a_change_writes_no_inventory_entry(self):
    columns = self.columns(('baumart', 'text'))
    self.reconcile(columns)
    entries = LogEntry.objects.count()
    self.reconcile(columns)
    # Django logs every successful change POST; the inventory must not appear in it
    self.assertEqual(LogEntry.objects.count(), entries + 1)
    self.assertNotIn('Attributinventar', LogEntry.objects.latest('id').get_change_message())

  def test_a_marker_forged_into_the_add_page_is_harmless(self):
    """
    the add page renders neither the button nor the two fields, but a hand-made
    POST can carry them; pinned here because the outcome is reachable anyway

    whoever may add a collection may reconcile it right afterwards, so the
    reconcile is carried out instead of refused – and it lands on the collection
    that was just created, not on another one
    """
    service = self.create_service('added')
    url = reverse('admin:pygeoapi_collection_add')
    data = self.collection_form_data(service, table='benches')
    data.update(self.formset_data(self.client.get(url)))
    data['reconcile'] = '1'
    data['reconcile_columns'] = json.dumps(self.columns(('baumart', 'text')))
    response = self.post(url, data)
    self.assertEqual(response.status_code, 302)
    added = Collection.objects.get(table='benches')
    self.assertEqual(
      list(added.attributes.values_list('name', 'data_type')), [('baumart', 'text')]
    )
    self.assertEqual(self.inventory(), {})

  def test_membership_decides_whether_a_reconcile_can_be_triggered(self):
    service = self.make_saveable()
    url = self.change_url()
    data = self.collection_form_data(service)
    data.update(self.formset_data(self.client.get(url)))
    data['reconcile'] = '1'
    data['reconcile_columns'] = json.dumps(self.columns(('baumart', 'text')))
    self.client.force_login(User.objects.create_user(username='outsider', is_staff=True))
    self.assertEqual(self.client.get(url).status_code, 403)
    self.assertEqual(self.post(url, data).status_code, 403)
    self.assertEqual(CollectionAttribute.objects.count(), 0)
