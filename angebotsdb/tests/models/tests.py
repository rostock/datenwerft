from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse

from angebotsdb.models.base import (
  InboxMessage,
  Law,
  OrgUnit,
  OrgUnitServicePermission,
  Provider,
  ReviewTask,
  TargetGroup,
  Topic,
  UserProfile,
)
from angebotsdb.models.services import (
  ChildrenYouthAndFamilyService,
  WoftGService,
)

from ..abstract import DefaultTestCase, ModelTestCase
from ..constant_vars import (
  USERNAME_PROVIDER,
  USERNAME_REVIEWER,
  VALID_DATE_A,
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
      service_type='childrenyouthandfamilyservice',
    )
    cls.attributes_values_db_updated = {'service_type': 'woftgservice'}

  def setUp(self):
    self.init()

  def test_create(self):
    self.assertIsNotNone(self.test_object.pk)
    self.assertEqual(self.model.objects.count(), 1)

  def test_update(self):
    self.test_object.service_type = 'woftgservice'
    self.test_object.save()
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.service_type, 'woftgservice')

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


class ChildrenYouthAndFamilyServiceModelTest(ModelTestCase):
  """
  Testklasse für das Modell ChildrenYouthAndFamilyService.
  """

  model = ChildrenYouthAndFamilyService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    provider = Provider.objects.create(name=VALID_STRING_A)
    topic = Topic.objects.create(name=VALID_STRING_A)
    law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    cls.test_object = ChildrenYouthAndFamilyService.objects.create(
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
      service_type='childrenyouthandfamilyservice',
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
    self.assertIn('childrenyouthandfamilyservice', str(self.test_object))
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
      service_type='childrenyouthandfamilyservice',
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


class InboxMessageEmailTest(DefaultTestCase):
  """
  Testklasse für den E-Mail-Versand bei Erstellung von InboxMessages
  (post_save-Signal + angebotsdb.emails).
  """

  @classmethod
  def setUpTestData(cls):
    cls.provider_user = User.objects.create_user(username=USERNAME_PROVIDER)
    cls.reviewer_user = User.objects.create_user(username=USERNAME_REVIEWER)
    cls.org_unit = OrgUnit.objects.create(name=VALID_STRING_A)
    cls.provider = Provider.objects.create(name=VALID_STRING_B, email='traeger@example.org')
    cls.review_task = ReviewTask.objects.create(
      service_type='childrenyouthandfamilyservice',
      service_id=1,
      assigned_org_unit=cls.org_unit,
      created_by_user_id=999,
      task_status='pending',
    )

  def setUp(self):
    self.init()
    self.reviewer_user.email = 'reviewer@example.org'
    self.reviewer_user.save(update_fields=['email'])
    self.provider_user.email = 'einrichtung@example.org'
    self.provider_user.save(update_fields=['email'])

  def create_review_request(self):
    return InboxMessage.objects.create(
      message_type='review_request',
      review_task=self.review_task,
      target_org_unit=self.org_unit,
    )

  def create_revision_request(self):
    return InboxMessage.objects.create(
      message_type='revision_request',
      review_task=self.review_task,
      target_provider=self.provider,
    )

  def test_review_request_sends_mail_to_org_unit_users(self):
    UserProfile.objects.create(
      user_id=self.reviewer_user.id,
      organisational_unit=self.org_unit,
      receive_email_notifications=True,
    )
    self.create_review_request()
    self.assertEqual(len(mail.outbox), 1)
    self.assertEqual(mail.outbox[0].to, ['reviewer@example.org'])
    self.assertIn('Prüfauftrag', mail.outbox[0].subject)
    # kein Service mit ID 1 vorhanden → Fallback aus service_type und service_id
    self.assertIn('childrenyouthandfamilyservice (ID 1)', mail.outbox[0].subject)

  def test_revision_request_sends_mail_to_provider_users_only(self):
    UserProfile.objects.create(
      user_id=self.provider_user.id,
      provider=self.provider,
      receive_email_notifications=True,
    )
    self.create_revision_request()
    self.assertEqual(len(mail.outbox), 1)
    self.assertEqual(mail.outbox[0].to, ['einrichtung@example.org'])
    self.assertIn('Überarbeitung', mail.outbox[0].subject)
    # das E-Mail-Feld des Trägers selbst erhält keine Mail
    self.assertNotIn('traeger@example.org', mail.outbox[0].to)

  def test_no_opt_in_no_mail(self):
    UserProfile.objects.create(
      user_id=self.reviewer_user.id,
      organisational_unit=self.org_unit,
    )
    self.create_review_request()
    self.assertEqual(len(mail.outbox), 0)

  def test_user_without_email_no_mail(self):
    self.reviewer_user.email = ''
    self.reviewer_user.save(update_fields=['email'])
    UserProfile.objects.create(
      user_id=self.reviewer_user.id,
      organisational_unit=self.org_unit,
      receive_email_notifications=True,
    )
    self.create_review_request()
    self.assertEqual(len(mail.outbox), 0)

  def test_inactive_user_no_mail(self):
    self.reviewer_user.is_active = False
    self.reviewer_user.save(update_fields=['is_active'])
    UserProfile.objects.create(
      user_id=self.reviewer_user.id,
      organisational_unit=self.org_unit,
      receive_email_notifications=True,
    )
    self.create_review_request()
    self.assertEqual(len(mail.outbox), 0)

  def test_no_profiles_no_mail(self):
    self.create_review_request()
    self.assertEqual(len(mail.outbox), 0)

  def test_skip_email_flag_suppresses_mail(self):
    UserProfile.objects.create(
      user_id=self.reviewer_user.id,
      organisational_unit=self.org_unit,
      receive_email_notifications=True,
    )
    message = InboxMessage(
      message_type='review_request',
      review_task=self.review_task,
      target_org_unit=self.org_unit,
    )
    message._skip_email = True
    message.save()
    self.assertEqual(len(mail.outbox), 0)

  def test_update_sends_no_mail(self):
    UserProfile.objects.create(
      user_id=self.reviewer_user.id,
      organisational_unit=self.org_unit,
      receive_email_notifications=True,
    )
    message = self.create_review_request()
    mail.outbox.clear()
    message.is_read = True
    message.save()
    self.assertEqual(len(mail.outbox), 0)

  def test_inbox_link_in_body(self):
    UserProfile.objects.create(
      user_id=self.reviewer_user.id,
      organisational_unit=self.org_unit,
      receive_email_notifications=True,
    )
    message = InboxMessage(
      message_type='review_request',
      review_task=self.review_task,
      target_org_unit=self.org_unit,
    )
    # Basis-URL wird an den View-Erstellungsstellen aus dem Request abgeleitet
    message._base_url = 'http://testserver'
    message.save()
    self.assertEqual(len(mail.outbox), 1)
    self.assertIn(f'http://testserver{reverse("angebotsdb:inbox_list")}', mail.outbox[0].body)

  def test_no_link_without_base_url(self):
    UserProfile.objects.create(
      user_id=self.reviewer_user.id,
      organisational_unit=self.org_unit,
      receive_email_notifications=True,
    )
    self.create_review_request()
    self.assertEqual(len(mail.outbox), 1)
    self.assertNotIn('http', mail.outbox[0].body)
