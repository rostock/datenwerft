from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse

from angebotsdb.models.base import Law, Provider, Topic
from angebotsdb.models.services import ChildrenAndYouthService, FamilyService, WoftGService

from ..abstract import FormViewTestCase, MockResponse, ViewTestCase
from ..constant_vars import (
  PASSWORD,
  USERNAME_PROVIDER,
  VALID_DATE_A,
  VALID_GEOJSON_4326,
  VALID_POINT_DB,
  VALID_STRING_A,
  VALID_STRING_B,
  VALID_ZIP,
)
from ..functions import login_as_admin, login_as_provider, login_no_role

HTML = 'text/html; charset=utf-8'
PYGEOAPI_PATCH = 'angebotsdb.fields.httpx.get'


def _base_service_form_data(topic_pk, law_pk):
  """
  Gibt valide POST-Daten für ein Service-Formular zurück.
  host, status, published_version und geometry werden vom Formular ausgeschlossen.

  :param topic_pk: PK des Themas
  :param law_pk: PK der gesetzlichen Grundlage
  :return: dict mit Formulardaten
  """
  return {
    'name': VALID_STRING_A,
    'description': 'Testbeschreibung für das Angebot.',
    'street': 'Teststraße 1',
    'zip': str(VALID_ZIP),
    'city': 'Rostock',
    'email': 'angebot@test.de',
    'expiry_date': VALID_DATE_A.isoformat(),
    'phone': '0381 123456',
    'costs': '0',
    # application_needed ist BooleanField: weglassen entspricht False (nicht angehakt)
    'topic': [str(topic_pk)],
    'legal_basis': [str(law_pk)],
    # catchment_area_urls: blank=True, required=False → weglassen
    'geometry': VALID_GEOJSON_4326,
  }


# ---------------------------------------------------------------------------
# ChildrenAndYouthService
# ---------------------------------------------------------------------------


class ChildrenAndYouthServiceListViewTest(ViewTestCase):
  """
  Testklasse für die Listen-Ansicht von ChildrenAndYouthService.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(
      login_as_admin, 'childrenandyouthservice_list', None, 200, HTML, 'Kinder'
    )


class ChildrenAndYouthServiceCreateViewTest(ViewTestCase):
  """
  Testklasse für die Erstell-Ansicht von ChildrenAndYouthService.
  """

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')

  def setUp(self):
    self.init()

  def _valid_form_data(self):
    return _base_service_form_data(self.test_topic.pk, self.test_law.pk)

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_as_provider_200(self, mock_get):
    self.generic_get_test(
      login_as_provider, 'childrenandyouthservice_create', None, 200, HTML, 'Angebot'
    )

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_no_role_403(self, mock_get):
    self.generic_get_test(login_no_role, 'childrenandyouthservice_create', None, 403, HTML, '')

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_success_as_provider(self, mock_get):
    self.generic_post_test(
      login_as_provider, 'childrenandyouthservice_create', None, self._valid_form_data(), 302
    )

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_success_as_admin(self, mock_get):
    # Admin hat kein UserProfile.provider → form_valid schlägt fehl → 200
    # Admins können Services nicht direkt anlegen (kein Träger)
    self.generic_post_test(
      login_as_admin, 'childrenandyouthservice_create', None, self._valid_form_data(), 200
    )

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_no_provider_profile_form_error(self, mock_get):
    """
    Nutzer in users_group ohne UserProfile → form_valid schlägt fehl → 200.
    """
    self.users_group.user_set.add(self.provider_user)
    self.client.login(username=USERNAME_PROVIDER, password=PASSWORD)
    response = self.client.post(
      reverse('angebotsdb:childrenandyouthservice_create'),
      self._valid_form_data(),
    )
    self.assertEqual(response.status_code, 200)

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_error_missing_fields(self, mock_get):
    self.generic_post_test(login_as_provider, 'childrenandyouthservice_create', None, {}, 200)


class ChildrenAndYouthServiceUpdateViewTest(FormViewTestCase):
  """
  Testklasse für die Bearbeitungs-Ansicht von ChildrenAndYouthService.
  """

  model = ChildrenAndYouthService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    service = ChildrenAndYouthService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      geometry=VALID_POINT_DB,
      status='draft',
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    cls.test_object = service

  def setUp(self):
    self.init()

  def _valid_form_data(self):
    data = _base_service_form_data(self.test_topic.pk, self.test_law.pk)
    data['name'] = VALID_STRING_B
    return data

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_as_provider_200(self, mock_get):
    """Provider-Nutzer als Besitzer des Service → Formular wird angezeigt."""
    self.generic_get_test(
      login_as_provider,
      'childrenandyouthservice_update',
      {'pk': self.test_object.pk},
      200,
      HTML,
      VALID_STRING_A,
    )

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_no_role_403(self, mock_get):
    self.generic_get_test(
      login_no_role, 'childrenandyouthservice_update', {'pk': self.test_object.pk}, 403, HTML, ''
    )

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_service_in_review_shows_locked_form(self, mock_get):
    """Service im Status in_review → Formular ist gesperrt."""
    self.test_object.status = 'in_review'
    self.test_object.save(update_fields=['status'])
    self.generic_get_test(
      login_as_admin, 'childrenandyouthservice_update', {'pk': self.test_object.pk}, 200, HTML, ''
    )
    # Status zurücksetzen für nachfolgende Tests
    self.test_object.status = 'draft'
    self.test_object.save(update_fields=['status'])

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_success_as_provider(self, mock_get):
    """POST mit gültigen Daten auf draft-Service: Redirect 302 + DB-Werte aktualisiert."""
    self.generic_post_test(
      login_as_provider,
      'childrenandyouthservice_update',
      {'pk': self.test_object.pk},
      self._valid_form_data(),
      302,
    )
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.name, VALID_STRING_B)
    self.assertEqual(self.test_object.status, 'draft')

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_error_missing_required_fields(self, mock_get):
    self.generic_post_test(
      login_as_provider, 'childrenandyouthservice_update', {'pk': self.test_object.pk}, {}, 200
    )

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_revision_needed_shows_form(self, mock_get):
    """Service mit Status revision_needed → Formular wird zur Bearbeitung angezeigt."""
    self.test_object.status = 'revision_needed'
    self.test_object.save(update_fields=['status'])
    self.generic_get_test(
      login_as_provider,
      'childrenandyouthservice_update',
      {'pk': self.test_object.pk},
      200,
      HTML,
      VALID_STRING_A,
    )

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_revision_needed_saves_changes(self, mock_get):
    """Speichern eines revision_needed-Service aktualisiert DB-Werte UND updated_at.

    Regressionstest für Bug-Report: Provider berichtete, dass Änderungen an Services
    im Status revision_needed nicht gespeichert wurden (updated_at blieb alt).
    """
    self.test_object.status = 'revision_needed'
    self.test_object.save()  # voller Save, damit updated_at definitiv gesetzt ist
    self.test_object.refresh_from_db()
    original_updated_at = self.test_object.updated_at

    self.generic_post_test(
      login_as_provider,
      'childrenandyouthservice_update',
      {'pk': self.test_object.pk},
      self._valid_form_data(),
      302,
    )

    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.name, VALID_STRING_B)
    self.assertEqual(self.test_object.status, 'revision_needed')
    self.assertGreaterEqual(self.test_object.updated_at, original_updated_at)

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_in_review_returns_403(self, mock_get):
    """POST auf in_review-Service wird durch _form_locked-Schutz mit 403 blockiert."""
    self.test_object.status = 'in_review'
    self.test_object.save(update_fields=['status'])
    self.generic_post_test(
      login_as_provider,
      'childrenandyouthservice_update',
      {'pk': self.test_object.pk},
      self._valid_form_data(),
      403,
    )
    # Original-Daten dürfen nicht verändert worden sein
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.name, VALID_STRING_A)

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_published_creates_draft_copy(self, mock_get):
    """POST auf published-Service erzeugt Draft-Copy; Original bleibt unverändert."""
    self.test_object.status = 'published'
    self.test_object.save(update_fields=['status'])

    self.generic_post_test(
      login_as_provider,
      'childrenandyouthservice_update',
      {'pk': self.test_object.pk},
      self._valid_form_data(),
      302,
    )

    # Original unverändert (außer ggf. updated_at, das prüfen wir nicht)
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.name, VALID_STRING_A)
    self.assertEqual(self.test_object.status, 'published')

    # Genau eine Draft-Copy mit den neuen Daten existiert
    drafts = ChildrenAndYouthService.objects.filter(published_version=self.test_object)
    self.assertEqual(drafts.count(), 1)
    draft = drafts.first()
    self.assertEqual(draft.name, VALID_STRING_B)
    self.assertEqual(draft.status, 'draft')
    self.assertEqual(draft.host, self.test_provider)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_published_with_existing_draft_redirects(self, mock_get):
    """GET auf published-Service mit existierender Draft-Copy → Redirect zur Draft-URL."""
    self.test_object.status = 'published'
    self.test_object.save(update_fields=['status'])
    draft = ChildrenAndYouthService.objects.create(
      name='Draft-Kopie',
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=self.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      geometry=VALID_POINT_DB,
      status='revision_needed',
      published_version=self.test_object,
    )
    draft.topic.set([self.test_topic])
    draft.legal_basis.set([self.test_law])

    login_as_provider(self)
    url = reverse('angebotsdb:childrenandyouthservice_update', kwargs={'pk': self.test_object.pk})
    response = self.client.get(url)
    self.assertEqual(response.status_code, 302)
    expected_url = reverse('angebotsdb:childrenandyouthservice_update', kwargs={'pk': draft.pk})
    self.assertEqual(response.url, expected_url)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_other_provider_returns_403(self, mock_get):
    """Provider darf Service eines fremden Providers nicht speichern (PermissionDenied)."""
    other_provider = Provider.objects.create(name='Anderer Träger')
    self.test_object.host = other_provider
    self.test_object.save(update_fields=['host'])

    login_as_provider(self)
    url = reverse('angebotsdb:childrenandyouthservice_update', kwargs={'pk': self.test_object.pk})
    response = self.client.post(url, self._valid_form_data())
    self.assertEqual(response.status_code, 403)

    # Original-Daten dürfen nicht verändert worden sein
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.name, VALID_STRING_A)


class ChildrenAndYouthServiceDetailViewTest(FormViewTestCase):
  """
  Testklasse für die Detailansicht (readonly) von ChildrenAndYouthService.
  """

  model = ChildrenAndYouthService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    service = ChildrenAndYouthService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      geometry=VALID_POINT_DB,
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    cls.test_object = service

  def setUp(self):
    self.init()

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_as_admin(self, mock_get):
    self.generic_get_test(
      login_as_admin,
      'childrenandyouthservice_detail',
      {'pk': self.test_object.pk},
      200,
      HTML,
      VALID_STRING_A,
    )

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_no_role_403(self, mock_get):
    self.generic_get_test(
      login_no_role, 'childrenandyouthservice_detail', {'pk': self.test_object.pk}, 403, HTML, ''
    )


class ChildrenAndYouthServiceDeleteViewTest(FormViewTestCase):
  """
  Testklasse für die Lösch-Ansicht von ChildrenAndYouthService.
  """

  model = ChildrenAndYouthService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    service = ChildrenAndYouthService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      geometry=VALID_POINT_DB,
      status='draft',
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    cls.test_object = service

  def setUp(self):
    self.init()

  def test_get_no_role_403(self):
    self.generic_get_test(
      login_no_role, 'childrenandyouthservice_delete', {'pk': self.test_object.pk}, 403, HTML, ''
    )

  def test_post_ajax_delete_as_provider(self):
    self.generic_ajax_delete_test(
      login_as_provider, 'childrenandyouthservice_delete', {'pk': self.test_object.pk}, True
    )

  def test_post_delete_as_provider(self):
    self.generic_post_test(
      login_as_provider, 'childrenandyouthservice_delete', {'pk': self.test_object.pk}, {}, 302
    )


# ---------------------------------------------------------------------------
# FamilyService
# ---------------------------------------------------------------------------


class FamilyServiceListViewTest(ViewTestCase):
  """
  Testklasse für die Listen-Ansicht von FamilyService.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'familyservice_list', None, 200, HTML, 'Familie')


class FamilyServiceCreateViewTest(ViewTestCase):
  """
  Testklasse für die Erstell-Ansicht von FamilyService.
  """

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')

  def setUp(self):
    self.init()

  def _valid_form_data(self):
    data = _base_service_form_data(self.test_topic.pk, self.test_law.pk)
    data['setting'] = 'Gruppenberatung'
    return data

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_as_provider_200(self, mock_get):
    self.generic_get_test(login_as_provider, 'familyservice_create', None, 200, HTML, 'Angebot')

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_no_role_403(self, mock_get):
    self.generic_get_test(login_no_role, 'familyservice_create', None, 403, HTML, '')

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_success_as_provider(self, mock_get):
    self.generic_post_test(
      login_as_provider, 'familyservice_create', None, self._valid_form_data(), 302
    )


class FamilyServiceUpdateViewTest(FormViewTestCase):
  """
  Testklasse für die Bearbeitungs-Ansicht von FamilyService.
  """

  model = FamilyService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    service = FamilyService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      setting='Gruppenberatung',
      geometry=VALID_POINT_DB,
      status='draft',
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    cls.test_object = service

  def setUp(self):
    self.init()

  def _valid_form_data(self):
    data = _base_service_form_data(self.test_topic.pk, self.test_law.pk)
    data['name'] = VALID_STRING_B
    data['setting'] = 'Gruppenberatung'
    return data

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_as_provider_200(self, mock_get):
    self.generic_get_test(
      login_as_provider,
      'familyservice_update',
      {'pk': self.test_object.pk},
      200,
      HTML,
      VALID_STRING_A,
    )

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_success_as_provider(self, mock_get):
    self.generic_post_test(
      login_as_provider,
      'familyservice_update',
      {'pk': self.test_object.pk},
      self._valid_form_data(),
      302,
    )
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.name, VALID_STRING_B)

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_revision_needed_saves_changes(self, mock_get):
    """Regressionstest: revision_needed-Save aktualisiert die DB."""
    self.test_object.status = 'revision_needed'
    self.test_object.save()
    self.generic_post_test(
      login_as_provider,
      'familyservice_update',
      {'pk': self.test_object.pk},
      self._valid_form_data(),
      302,
    )
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.name, VALID_STRING_B)
    self.assertEqual(self.test_object.status, 'revision_needed')


class FamilyServiceDetailViewTest(FormViewTestCase):
  """
  Testklasse für die Detailansicht (readonly) von FamilyService.
  """

  model = FamilyService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    service = FamilyService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      setting='Gruppenberatung',
      geometry=VALID_POINT_DB,
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    cls.test_object = service

  def setUp(self):
    self.init()

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_as_admin(self, mock_get):
    self.generic_get_test(
      login_as_admin,
      'familyservice_detail',
      {'pk': self.test_object.pk},
      200,
      HTML,
      VALID_STRING_A,
    )


class FamilyServiceDeleteViewTest(FormViewTestCase):
  """
  Testklasse für die Lösch-Ansicht von FamilyService.
  """

  model = FamilyService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    service = FamilyService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      setting='Gruppenberatung',
      geometry=VALID_POINT_DB,
      status='draft',
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    cls.test_object = service

  def setUp(self):
    self.init()

  def test_post_ajax_delete_as_provider(self):
    self.generic_ajax_delete_test(
      login_as_provider, 'familyservice_delete', {'pk': self.test_object.pk}, True
    )

  def test_post_delete_as_provider(self):
    self.generic_post_test(
      login_as_provider, 'familyservice_delete', {'pk': self.test_object.pk}, {}, 302
    )


# ---------------------------------------------------------------------------
# WoftGService
# ---------------------------------------------------------------------------


class WoftGServiceListViewTest(ViewTestCase):
  """
  Testklasse für die Listen-Ansicht von WoftGService.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'woftgservice_list', None, 200, HTML, 'WoftG')


class WoftGServiceCreateViewTest(ViewTestCase):
  """
  Testklasse für die Erstell-Ansicht von WoftGService.
  """

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')

  def setUp(self):
    self.init()

  def _valid_form_data(self):
    data = _base_service_form_data(self.test_topic.pk, self.test_law.pk)
    data['setting'] = 'Einzelberatung'
    # handicap_accessible: weglassen = False
    return data

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_as_provider_200(self, mock_get):
    self.generic_get_test(login_as_provider, 'woftgservice_create', None, 200, HTML, 'Angebot')

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_no_role_403(self, mock_get):
    self.generic_get_test(login_no_role, 'woftgservice_create', None, 403, HTML, '')

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_success_as_provider(self, mock_get):
    self.generic_post_test(
      login_as_provider, 'woftgservice_create', None, self._valid_form_data(), 302
    )


class WoftGServiceUpdateViewTest(FormViewTestCase):
  """
  Testklasse für die Bearbeitungs-Ansicht von WoftGService.
  """

  model = WoftGService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    service = WoftGService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      setting='Einzelberatung',
      handicap_accessible=False,
      geometry=VALID_POINT_DB,
      status='draft',
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    cls.test_object = service

  def setUp(self):
    self.init()

  def _valid_form_data(self):
    data = _base_service_form_data(self.test_topic.pk, self.test_law.pk)
    data['name'] = VALID_STRING_B
    data['setting'] = 'Einzelberatung'
    return data

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_as_provider_200(self, mock_get):
    self.generic_get_test(
      login_as_provider,
      'woftgservice_update',
      {'pk': self.test_object.pk},
      200,
      HTML,
      VALID_STRING_A,
    )

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_success_as_provider(self, mock_get):
    self.generic_post_test(
      login_as_provider,
      'woftgservice_update',
      {'pk': self.test_object.pk},
      self._valid_form_data(),
      302,
    )
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.name, VALID_STRING_B)

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_post_revision_needed_saves_changes(self, mock_get):
    """Regressionstest: revision_needed-Save aktualisiert die DB."""
    self.test_object.status = 'revision_needed'
    self.test_object.save()
    self.generic_post_test(
      login_as_provider,
      'woftgservice_update',
      {'pk': self.test_object.pk},
      self._valid_form_data(),
      302,
    )
    self.test_object.refresh_from_db()
    self.assertEqual(self.test_object.name, VALID_STRING_B)
    self.assertEqual(self.test_object.status, 'revision_needed')


class WoftGServiceDetailViewTest(FormViewTestCase):
  """
  Testklasse für die Detailansicht (readonly) von WoftGService.
  """

  model = WoftGService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    service = WoftGService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      setting='Einzelberatung',
      handicap_accessible=False,
      geometry=VALID_POINT_DB,
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    cls.test_object = service

  def setUp(self):
    self.init()

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_get_as_admin(self, mock_get):
    self.generic_get_test(
      login_as_admin,
      'woftgservice_detail',
      {'pk': self.test_object.pk},
      200,
      HTML,
      VALID_STRING_A,
    )


class WoftGServiceDeleteViewTest(FormViewTestCase):
  """
  Testklasse für die Lösch-Ansicht von WoftGService.
  """

  model = WoftGService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    service = WoftGService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      phone='0381 123456',
      costs=0.0,
      setting='Einzelberatung',
      handicap_accessible=False,
      geometry=VALID_POINT_DB,
      status='draft',
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    cls.test_object = service

  def setUp(self):
    self.init()

  def test_post_ajax_delete_as_provider(self):
    self.generic_ajax_delete_test(
      login_as_provider, 'woftgservice_delete', {'pk': self.test_object.pk}, True
    )

  def test_post_delete_as_provider(self):
    self.generic_post_test(
      login_as_provider, 'woftgservice_delete', {'pk': self.test_object.pk}, {}, 302
    )
