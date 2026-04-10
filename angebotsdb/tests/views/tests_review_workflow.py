from angebotsdb.models.base import (
  InboxMessage,
  Law,
  OrgUnit,
  OrgUnitServicePermission,
  Provider,
  ReviewTask,
  Topic,
)
from angebotsdb.models.services import ChildrenAndYouthService

from ..abstract import FormViewTestCase
from ..constant_vars import (
  VALID_DATE_A,
  VALID_POINT_DB,
  VALID_STRING_A,
  VALID_ZIP,
)
from ..functions import login_as_provider, login_as_reviewer, login_no_role

HTML = 'text/html; charset=utf-8'


def _create_service_with_deps(provider, topic, law, status='draft'):
  """
  Erstellt einen ChildrenAndYouthService mit allen Pflichtfeldern.

  :param provider: Provider-Instanz
  :param topic: Topic-Instanz
  :param law: Law-Instanz
  :param status: Initialstatus des Service
  :return: ChildrenAndYouthService-Instanz
  """
  service = ChildrenAndYouthService.objects.create(
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
    status=status,
  )
  service.topic.set([topic])
  service.legal_basis.set([law])
  return service


# ---------------------------------------------------------------------------
# SubmitForReviewView
# ---------------------------------------------------------------------------


class SubmitForReviewViewTest(FormViewTestCase):
  """
  Testklasse für SubmitForReviewView (POST only).
  """

  model = ChildrenAndYouthService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_org_unit = OrgUnit.objects.create(name=VALID_STRING_A)
    topic = Topic.objects.create(name=VALID_STRING_A)
    law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    OrgUnitServicePermission.objects.create(
      organisational_unit=cls.test_org_unit,
      service_type='childrenandyouthservice',
    )
    cls.test_object = _create_service_with_deps(cls.test_provider, topic, law, status='draft')

  def setUp(self):
    self.init()

  def _view_args(self):
    return {
      'service_type': 'childrenandyouthservice',
      'service_id': self.test_object.pk,
    }

  def test_post_as_provider_success(self):
    """Provider-Nutzer (Besitzer des Service) kann Service zur Prüfung einreichen."""
    self.generic_post_test(login_as_provider, 'submit_for_review', self._view_args(), {}, 302)
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.status, 'in_review')
    self.assertEqual(
      ReviewTask.objects.filter(
        service_type='childrenandyouthservice',
        service_id=self.test_object.pk,
        task_status='pending',
      ).count(),
      1,
    )
    self.assertEqual(
      InboxMessage.objects.filter(
        target_org_unit=self.test_org_unit,
        message_type='review_request',
        is_resolved=False,
      ).count(),
      1,
    )

  def test_post_no_role_403(self):
    """Nutzer ohne Gruppe erhält 403."""
    self.generic_post_test(login_no_role, 'submit_for_review', self._view_args(), {}, 403)

  def test_post_invalid_status_400(self):
    """Service mit Status in_review kann nicht erneut eingereicht werden."""
    self.test_object.status = 'in_review'
    self.test_object.save(update_fields=['status'])
    self.generic_post_test(login_as_provider, 'submit_for_review', self._view_args(), {}, 400)
    # Status zurücksetzen
    self.test_object.status = 'draft'
    self.test_object.save(update_fields=['status'])

  def test_get_redirects_to_list(self):
    """GET-Anfragen werden zur Listen-Ansicht weitergeleitet."""
    self.generic_get_test(login_as_provider, 'submit_for_review', self._view_args(), 302, HTML, '')


# ---------------------------------------------------------------------------
# ReviewServiceView
# ---------------------------------------------------------------------------


class ReviewServiceViewTest(FormViewTestCase):
  """
  Testklasse für ReviewServiceView (GET + POST).
  """

  model = ChildrenAndYouthService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_org_unit = OrgUnit.objects.create(name=VALID_STRING_A)
    topic = Topic.objects.create(name=VALID_STRING_A)
    law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    OrgUnitServicePermission.objects.create(
      organisational_unit=cls.test_org_unit,
      service_type='childrenandyouthservice',
    )
    cls.test_object = _create_service_with_deps(cls.test_provider, topic, law, status='in_review')
    cls.test_review_task = ReviewTask.objects.create(
      service_type='childrenandyouthservice',
      service_id=cls.test_object.pk,
      assigned_org_unit=cls.test_org_unit,
      created_by_user_id=999,
      task_status='pending',
      submitted_snapshot={},
    )

  def setUp(self):
    self.init()

  def _view_args(self):
    return {'task_id': self.test_review_task.pk}

  def test_get_as_reviewer_200(self):
    """Reviewer kann den Prüfauftrag einsehen."""
    self.generic_get_test(
      login_as_reviewer, 'review_service', self._view_args(), 200, HTML, 'Pr\xfcfauftrag'
    )

  def test_get_no_role_403(self):
    """Nutzer ohne Reviewerrechte erhält 403."""
    self.generic_get_test(login_no_role, 'review_service', self._view_args(), 403, HTML, '')

  def test_post_approve(self):
    """Reviewer kann Service ohne Kommentare freigeben."""
    self.generic_post_test(
      login_as_reviewer, 'review_service', self._view_args(), {'action': 'approve'}, 302
    )
    self.test_review_task.refresh_from_db()
    self.assertEqual(self.test_review_task.task_status, 'approved')
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.status, 'published')

  def test_post_reject_with_comment(self):
    """Reviewer kann Service mit Kommentar zurückweisen."""
    # ReviewTask muss für diesen Test wieder auf pending sein
    self.test_review_task.task_status = 'pending'
    self.test_review_task.save(update_fields=['task_status'])
    self.test_object.status = 'in_review'
    self.test_object.save(update_fields=['status'])

    self.generic_post_test(
      login_as_reviewer,
      'review_service',
      self._view_args(),
      {'action': 'reject', 'comment_name': 'Bitte Bezeichnung ändern.'},
      302,
    )
    self.test_review_task.refresh_from_db()
    self.assertEqual(self.test_review_task.task_status, 'rejected')
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.status, 'revision_needed')
    # InboxMessage an Provider muss erstellt worden sein
    self.assertEqual(
      InboxMessage.objects.filter(
        review_task=self.test_review_task,
        message_type='revision_request',
        target_provider=self.test_provider,
        is_resolved=False,
      ).count(),
      1,
    )

  def test_post_reject_without_comment_400(self):
    """Zurückweisung ohne Kommentar ist nicht erlaubt."""
    self.test_review_task.task_status = 'pending'
    self.test_review_task.save(update_fields=['task_status'])

    self.generic_post_test(
      login_as_reviewer, 'review_service', self._view_args(), {'action': 'reject'}, 400
    )

  def test_post_approve_with_comment_400(self):
    """Freigabe mit Kommentaren ist nicht erlaubt."""
    self.test_review_task.task_status = 'pending'
    self.test_review_task.save(update_fields=['task_status'])
    self.test_review_task.comments = {}
    self.test_review_task.save(update_fields=['comments'])

    self.generic_post_test(
      login_as_reviewer,
      'review_service',
      self._view_args(),
      {'action': 'approve', 'comment_name': 'Kommentar'},
      400,
    )

  def test_post_already_closed_task_400(self):
    """Bereits abgeschlossener ReviewTask kann nicht nochmals bearbeitet werden."""
    self.test_review_task.task_status = 'approved'
    self.test_review_task.save(update_fields=['task_status'])

    self.generic_post_test(
      login_as_reviewer, 'review_service', self._view_args(), {'action': 'approve'}, 400
    )
    # Zurücksetzen für andere Tests
    self.test_review_task.task_status = 'pending'
    self.test_review_task.save(update_fields=['task_status'])
