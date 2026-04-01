from angebotsdb.models.base import (
  InboxMessage,
  Law,
  OrgUnit,
  OrgUnitServicePermission,
  Provider,
  ReviewTask,
  Tag,
  TargetGroup,
  Topic,
  UserProfile,
)
from angebotsdb.models.services import (
  ChildrenAndYouthService,
  FamilyService,
  WoftGService,
)

from ..abstract import ModelTestCase
from ..constant_vars import (
  VALID_DATE_A,
  VALID_DATE_B,
  VALID_POINT_DB,
  VALID_STRING_A,
  VALID_STRING_B,
  VALID_ZIP,
)


# ---------------------------------------------------------------------------
# Einfache Stammdaten (keine FK-Abhängigkeiten)
# ---------------------------------------------------------------------------


class TopicModelTest(ModelTestCase):
  """
  Testklasse für das Modell Topic.
  """

  model = Topic
  attributes_values_db_initial = {'name': VALID_STRING_A}
  attributes_values_db_updated = {'name': VALID_STRING_B}

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    self.generic_string_representation_test(VALID_STRING_A)


class TagModelTest(ModelTestCase):
  """
  Testklasse für das Modell Tag.
  """

  model = Tag
  attributes_values_db_initial = {'name': VALID_STRING_A}
  attributes_values_db_updated = {'name': VALID_STRING_B}

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    self.generic_string_representation_test(VALID_STRING_A)


class TargetGroupModelTest(ModelTestCase):
  """
  Testklasse für das Modell TargetGroup.
  """

  model = TargetGroup
  attributes_values_db_initial = {'name': VALID_STRING_A}
  attributes_values_db_updated = {'name': VALID_STRING_B}

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    self.generic_string_representation_test(VALID_STRING_A)


class ProviderModelTest(ModelTestCase):
  """
  Testklasse für das Modell Provider.
  """

  model = Provider
  attributes_values_db_initial = {'name': VALID_STRING_A}
  attributes_values_db_updated = {'name': VALID_STRING_B}

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    self.generic_string_representation_test(VALID_STRING_A)


class OrgUnitModelTest(ModelTestCase):
  """
  Testklasse für das Modell OrgUnit.
  """

  model = OrgUnit
  attributes_values_db_initial = {'name': VALID_STRING_A}
  attributes_values_db_updated = {'name': VALID_STRING_B}

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    self.generic_string_representation_test(VALID_STRING_A)


class LawModelTest(ModelTestCase):
  """
  Testklasse für das Modell Law.
  """

  model = Law
  attributes_values_db_initial = {'law_book': 'SGB VIII', 'paragraph': '8a'}
  attributes_values_db_updated = {'law_book': 'BGB', 'paragraph': '123'}

  def setUp(self):
    self.init()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()

  def test_string_representation(self):
    self.generic_string_representation_test('§8a SGB VIII')


# ---------------------------------------------------------------------------
# Modelle mit FK-Abhängigkeiten
# ---------------------------------------------------------------------------


class OrgUnitServicePermissionModelTest(ModelTestCase):
  """
  Testklasse für das Modell OrgUnitServicePermission.
  """

  model = OrgUnitServicePermission
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    org_unit = OrgUnit.objects.create(name=VALID_STRING_A)
    cls.test_object = cls.model.objects.create(
      organisational_unit=org_unit,
      service_type='childrenandyouthservice',
    )
    cls.attributes_values_db_updated = {'service_type': 'familyservice'}

  def setUp(self):
    self.init()

  def test_create(self):
    self.assertIsNotNone(self.test_object.pk)
    self.assertEqual(self.model.objects.count(), 1)

  def test_update(self):
    self.test_object.service_type = 'familyservice'
    self.test_object.save()
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.service_type, 'familyservice')

  def test_delete(self):
    self.test_object.delete()
    self.assertEqual(self.model.objects.count(), 0)

  def test_string_representation(self):
    self.assertIn(VALID_STRING_A, str(self.test_object))


class UserProfileModelTest(ModelTestCase):
  """
  Testklasse für das Modell UserProfile (cross-DB: user_id als IntegerField).
  """

  model = UserProfile
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    # user_id als Platzhalter — echter User nicht nötig für Modell-Test
    cls.test_object = UserProfile.objects.create(
      user_id=999,
      provider=cls.test_provider,
    )

  def setUp(self):
    self.init()

  def test_create(self):
    self.assertIsNotNone(self.test_object.pk)
    self.assertEqual(self.model.objects.count(), 1)

  def test_update(self):
    other_provider = Provider.objects.create(name=VALID_STRING_B)
    self.test_object.provider = other_provider
    self.test_object.save()
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.provider, other_provider)

  def test_delete(self):
    self.test_object.delete()
    self.assertEqual(self.model.objects.count(), 0)


# ---------------------------------------------------------------------------
# Service-Modelle
# ---------------------------------------------------------------------------


class ChildrenAndYouthServiceModelTest(ModelTestCase):
  """
  Testklasse für das Modell ChildrenAndYouthService.
  """

  model = ChildrenAndYouthService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    provider = Provider.objects.create(name=VALID_STRING_A)
    topic = Topic.objects.create(name=VALID_STRING_A)
    law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    cls.test_object = ChildrenAndYouthService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      geometry=VALID_POINT_DB,
    )
    cls.test_object.topic.set([topic])
    cls.test_object.legal_basis.set([law])
    cls.attributes_values_db_updated = {'name': VALID_STRING_B}

  def setUp(self):
    self.init()

  def test_create(self):
    self.assertIsNotNone(self.test_object.pk)
    self.assertEqual(self.model.objects.count(), 1)

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.test_object.delete()
    self.assertEqual(self.model.objects.count(), 0)

  def test_string_representation(self):
    self.generic_string_representation_test(VALID_STRING_A)


class FamilyServiceModelTest(ModelTestCase):
  """
  Testklasse für das Modell FamilyService.
  """

  model = FamilyService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    provider = Provider.objects.create(name=VALID_STRING_A)
    topic = Topic.objects.create(name=VALID_STRING_A)
    law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    cls.test_object = FamilyService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      setting='Gruppenberatung',
      geometry=VALID_POINT_DB,
    )
    cls.test_object.topic.set([topic])
    cls.test_object.legal_basis.set([law])
    cls.attributes_values_db_updated = {'name': VALID_STRING_B}

  def setUp(self):
    self.init()

  def test_create(self):
    self.assertIsNotNone(self.test_object.pk)
    self.assertEqual(self.model.objects.count(), 1)

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.test_object.delete()
    self.assertEqual(self.model.objects.count(), 0)

  def test_string_representation(self):
    self.generic_string_representation_test(VALID_STRING_A)


class WoftGServiceModelTest(ModelTestCase):
  """
  Testklasse für das Modell WoftGService.
  """

  model = WoftGService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    provider = Provider.objects.create(name=VALID_STRING_A)
    topic = Topic.objects.create(name=VALID_STRING_A)
    law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    cls.test_object = WoftGService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      setting='Einzelberatung',
      handicap_accessible=False,
      geometry=VALID_POINT_DB,
    )
    cls.test_object.topic.set([topic])
    cls.test_object.legal_basis.set([law])
    cls.attributes_values_db_updated = {'name': VALID_STRING_B}

  def setUp(self):
    self.init()

  def test_create(self):
    self.assertIsNotNone(self.test_object.pk)
    self.assertEqual(self.model.objects.count(), 1)

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.test_object.delete()
    self.assertEqual(self.model.objects.count(), 0)

  def test_string_representation(self):
    self.generic_string_representation_test(VALID_STRING_A)


# ---------------------------------------------------------------------------
# Workflow-Modelle
# ---------------------------------------------------------------------------


class ReviewTaskModelTest(ModelTestCase):
  """
  Testklasse für das Modell ReviewTask.
  """

  model = ReviewTask
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    org_unit = OrgUnit.objects.create(name=VALID_STRING_A)
    cls.test_object = ReviewTask.objects.create(
      service_type='childrenandyouthservice',
      service_id=1,
      assigned_org_unit=org_unit,
      created_by_user_id=999,
      task_status='pending',
    )
    cls.attributes_values_db_updated = {'task_status': 'approved'}

  def setUp(self):
    self.init()

  def test_create(self):
    self.assertIsNotNone(self.test_object.pk)
    self.assertEqual(self.model.objects.count(), 1)

  def test_update(self):
    self.test_object.task_status = 'approved'
    self.test_object.save()
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.task_status, 'approved')

  def test_delete(self):
    self.test_object.delete()
    self.assertEqual(self.model.objects.count(), 0)

  def test_string_representation(self):
    self.assertIn('childrenandyouthservice', str(self.test_object))
    self.assertIn(str(self.test_object.pk), str(self.test_object))


class InboxMessageModelTest(ModelTestCase):
  """
  Testklasse für das Modell InboxMessage.
  """

  model = InboxMessage
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    org_unit = OrgUnit.objects.create(name=VALID_STRING_A)
    review_task = ReviewTask.objects.create(
      service_type='childrenandyouthservice',
      service_id=1,
      assigned_org_unit=org_unit,
      created_by_user_id=999,
      task_status='pending',
    )
    cls.test_object = InboxMessage.objects.create(
      message_type='review_request',
      review_task=review_task,
      target_org_unit=org_unit,
    )

  def setUp(self):
    self.init()

  def test_create(self):
    self.assertIsNotNone(self.test_object.pk)
    self.assertEqual(self.model.objects.count(), 1)

  def test_update(self):
    self.test_object.is_read = True
    self.test_object.save()
    self.test_object.refresh_from_db()
    self.assertTrue(self.test_object.is_read)

  def test_delete(self):
    self.test_object.delete()
    self.assertEqual(self.model.objects.count(), 0)

  def test_string_representation(self):
    self.assertIn(VALID_STRING_A, str(self.test_object))
