from angebotsdb.models.base import Law, OrgUnit, Provider, Tag, TargetGroup, Topic

from ..abstract import FormViewTestCase, ViewTestCase
from ..constant_vars import VALID_STRING_A, VALID_STRING_B
from ..functions import login_as_admin, login_no_role

HTML = 'text/html; charset=utf-8'


# ---------------------------------------------------------------------------
# Topic
# ---------------------------------------------------------------------------


class TopicListViewTest(ViewTestCase):
  """
  Testklasse für die Listen-Ansicht von Topic.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'topic_list', None, 200, HTML, 'Kategorie')

  def test_get_no_role(self):
    # Eingeloggt ohne Gruppe → kein is_angebotsdb_user → PermissionDenied in get_form_class
    # Die Liste selbst hat kein eigenes Permission-Gate in dispatch,
    # aber die Template-Darstellung zeigt je nach Rechten unterschiedliche Inhalte.
    # Wir prüfen nur, dass die Seite überhaupt gerendert wird.
    self.generic_get_test(login_no_role, 'topic_list', None, 200, HTML, '')


class TopicCreateViewTest(ViewTestCase):
  """
  Testklasse für die Erstell-Ansicht von Topic.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'topic_create', None, 200, HTML, 'Kategorie')

  def test_get_no_role_403(self):
    # GenericCreateView.get_form_class wirft PermissionDenied → 403
    self.generic_get_test(login_no_role, 'topic_create', None, 403, HTML, '')

  def test_post_success(self):
    self.generic_post_test(login_as_admin, 'topic_create', None, {'name': VALID_STRING_A}, 302)

  def test_post_error_missing_name(self):
    self.generic_post_test(login_as_admin, 'topic_create', None, {}, 200)


class TopicUpdateViewTest(FormViewTestCase):
  """
  Testklasse für die Bearbeitungs-Ansicht von Topic.
  """

  model = Topic
  attributes_values_db_initial = {'name': VALID_STRING_A}

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(
      login_as_admin, 'topic_update', {'pk': self.test_object.pk}, 200, HTML, VALID_STRING_A
    )

  def test_get_no_role_403(self):
    # GenericUpdateView.dispatch gibt HttpResponseForbidden zurück → 403
    self.generic_get_test(
      login_no_role, 'topic_update', {'pk': self.test_object.pk}, 403, HTML, ''
    )

  def test_post_success(self):
    self.generic_post_test(
      login_as_admin, 'topic_update', {'pk': self.test_object.pk}, {'name': VALID_STRING_B}, 302
    )

  def test_post_error_missing_name(self):
    self.generic_post_test(login_as_admin, 'topic_update', {'pk': self.test_object.pk}, {}, 200)


class TopicDeleteViewTest(FormViewTestCase):
  """
  Testklasse für die Lösch-Ansicht von Topic.
  """

  model = Topic
  attributes_values_db_initial = {'name': VALID_STRING_A}

  def setUp(self):
    self.init()

  def test_get_no_role_403(self):
    self.generic_get_test(
      login_no_role, 'topic_delete', {'pk': self.test_object.pk}, 403, HTML, ''
    )

  def test_post_success(self):
    self.generic_post_test(login_as_admin, 'topic_delete', {'pk': self.test_object.pk}, {}, 302)

  def test_post_ajax_delete_as_admin(self):
    self.generic_ajax_delete_test(
      login_as_admin, 'topic_delete', {'pk': self.test_object.pk}, True
    )


# ---------------------------------------------------------------------------
# Law
# ---------------------------------------------------------------------------


class LawListViewTest(ViewTestCase):
  """
  Testklasse für die Listen-Ansicht von Law.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'law_list', None, 200, HTML, 'Gesetz')


class LawCreateViewTest(ViewTestCase):
  """
  Testklasse für die Erstell-Ansicht von Law.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'law_create', None, 200, HTML, 'Gesetz')

  def test_get_no_role_403(self):
    self.generic_get_test(login_no_role, 'law_create', None, 403, HTML, '')

  def test_post_success(self):
    self.generic_post_test(
      login_as_admin, 'law_create', None, {'law_book': 'SGB VIII', 'paragraph': '8a'}, 302
    )

  def test_post_error_missing_fields(self):
    self.generic_post_test(login_as_admin, 'law_create', None, {}, 200)


class LawUpdateViewTest(FormViewTestCase):
  """
  Testklasse für die Bearbeitungs-Ansicht von Law.
  """

  model = Law
  attributes_values_db_initial = {'law_book': 'SGB VIII', 'paragraph': '8a'}

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(
      login_as_admin, 'law_update', {'pk': self.test_object.pk}, 200, HTML, 'SGB VIII'
    )

  def test_get_no_role_403(self):
    self.generic_get_test(login_no_role, 'law_update', {'pk': self.test_object.pk}, 403, HTML, '')

  def test_post_success(self):
    self.generic_post_test(
      login_as_admin,
      'law_update',
      {'pk': self.test_object.pk},
      {'law_book': 'BGB', 'paragraph': '123'},
      302,
    )

  def test_post_error_missing_fields(self):
    self.generic_post_test(login_as_admin, 'law_update', {'pk': self.test_object.pk}, {}, 200)


class LawDeleteViewTest(FormViewTestCase):
  """
  Testklasse für die Lösch-Ansicht von Law.
  """

  model = Law
  attributes_values_db_initial = {'law_book': 'SGB VIII', 'paragraph': '8a'}

  def setUp(self):
    self.init()

  def test_post_success(self):
    self.generic_post_test(login_as_admin, 'law_delete', {'pk': self.test_object.pk}, {}, 302)

  def test_post_ajax_delete_as_admin(self):
    self.generic_ajax_delete_test(login_as_admin, 'law_delete', {'pk': self.test_object.pk}, True)


# ---------------------------------------------------------------------------
# Provider (Träger)
# ---------------------------------------------------------------------------


class ProviderListViewTest(ViewTestCase):
  """
  Testklasse für die Listen-Ansicht von Provider.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'provider_list', None, 200, HTML, 'Träger')


class ProviderCreateViewTest(ViewTestCase):
  """
  Testklasse für die Erstell-Ansicht von Provider (nur Admin).
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'provider_create', None, 200, HTML, 'Träger')

  def test_get_no_role_403(self):
    self.generic_get_test(login_no_role, 'provider_create', None, 403, HTML, '')

  def test_post_success(self):
    self.generic_post_test(login_as_admin, 'provider_create', None, {'name': VALID_STRING_A}, 302)

  def test_post_error_missing_name(self):
    self.generic_post_test(login_as_admin, 'provider_create', None, {}, 200)


class ProviderUpdateViewTest(FormViewTestCase):
  """
  Testklasse für die Bearbeitungs-Ansicht von Provider.
  """

  model = Provider
  attributes_values_db_initial = {'name': VALID_STRING_A}

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(
      login_as_admin, 'provider_update', {'pk': self.test_object.pk}, 200, HTML, VALID_STRING_A
    )

  def test_get_no_role_403(self):
    self.generic_get_test(
      login_no_role, 'provider_update', {'pk': self.test_object.pk}, 403, HTML, ''
    )

  def test_post_success(self):
    self.generic_post_test(
      login_as_admin, 'provider_update', {'pk': self.test_object.pk}, {'name': VALID_STRING_B}, 302
    )


class ProviderDeleteViewTest(FormViewTestCase):
  """
  Testklasse für die Lösch-Ansicht von Provider.
  """

  model = Provider
  attributes_values_db_initial = {'name': VALID_STRING_A}

  def setUp(self):
    self.init()

  def test_post_success(self):
    self.generic_post_test(login_as_admin, 'provider_delete', {'pk': self.test_object.pk}, {}, 302)

  def test_post_ajax_delete_as_admin(self):
    self.generic_ajax_delete_test(
      login_as_admin, 'provider_delete', {'pk': self.test_object.pk}, True
    )


# ---------------------------------------------------------------------------
# OrgUnit
# ---------------------------------------------------------------------------


class OrgUnitListViewTest(ViewTestCase):
  """
  Testklasse für die Listen-Ansicht von OrgUnit.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'orgunit_list', None, 200, HTML, 'Organisationseinheit')


class OrgUnitCreateViewTest(ViewTestCase):
  """
  Testklasse für die Erstell-Ansicht von OrgUnit.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(
      login_as_admin, 'orgunit_create', None, 200, HTML, 'Organisationseinheit'
    )

  def test_get_no_role_403(self):
    self.generic_get_test(login_no_role, 'orgunit_create', None, 403, HTML, '')

  def test_post_success(self):
    self.generic_post_test(login_as_admin, 'orgunit_create', None, {'name': VALID_STRING_A}, 302)

  def test_post_error_missing_name(self):
    self.generic_post_test(login_as_admin, 'orgunit_create', None, {}, 200)


class OrgUnitUpdateViewTest(FormViewTestCase):
  """
  Testklasse für die Bearbeitungs-Ansicht von OrgUnit.
  """

  model = OrgUnit
  attributes_values_db_initial = {'name': VALID_STRING_A}

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(
      login_as_admin, 'orgunit_update', {'pk': self.test_object.pk}, 200, HTML, VALID_STRING_A
    )

  def test_get_no_role_403(self):
    self.generic_get_test(
      login_no_role, 'orgunit_update', {'pk': self.test_object.pk}, 403, HTML, ''
    )

  def test_post_success(self):
    self.generic_post_test(
      login_as_admin, 'orgunit_update', {'pk': self.test_object.pk}, {'name': VALID_STRING_B}, 302
    )


class OrgUnitDeleteViewTest(FormViewTestCase):
  """
  Testklasse für die Lösch-Ansicht von OrgUnit.
  """

  model = OrgUnit
  attributes_values_db_initial = {'name': VALID_STRING_A}

  def setUp(self):
    self.init()

  def test_post_success(self):
    self.generic_post_test(login_as_admin, 'orgunit_delete', {'pk': self.test_object.pk}, {}, 302)

  def test_post_ajax_delete_as_admin(self):
    self.generic_ajax_delete_test(
      login_as_admin, 'orgunit_delete', {'pk': self.test_object.pk}, True
    )


# ---------------------------------------------------------------------------
# Tag
# ---------------------------------------------------------------------------


class TagListViewTest(ViewTestCase):
  """
  Testklasse für die Listen-Ansicht von Tag.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'tag_list', None, 200, HTML, 'Schlagwort')


class TagCreateViewTest(ViewTestCase):
  """
  Testklasse für die Erstell-Ansicht von Tag.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'tag_create', None, 200, HTML, 'Schlagwort')

  def test_get_no_role_403(self):
    self.generic_get_test(login_no_role, 'tag_create', None, 403, HTML, '')

  def test_post_success(self):
    self.generic_post_test(login_as_admin, 'tag_create', None, {'name': VALID_STRING_A}, 302)


class TagUpdateViewTest(FormViewTestCase):
  """
  Testklasse für die Bearbeitungs-Ansicht von Tag.
  """

  model = Tag
  attributes_values_db_initial = {'name': VALID_STRING_A}

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(
      login_as_admin, 'tag_update', {'pk': self.test_object.pk}, 200, HTML, VALID_STRING_A
    )

  def test_post_success(self):
    self.generic_post_test(
      login_as_admin, 'tag_update', {'pk': self.test_object.pk}, {'name': VALID_STRING_B}, 302
    )


# ---------------------------------------------------------------------------
# TargetGroup
# ---------------------------------------------------------------------------


class TargetGroupListViewTest(ViewTestCase):
  """
  Testklasse für die Listen-Ansicht von TargetGroup.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'targetgroup_list', None, 200, HTML, 'Zielgruppe')


class TargetGroupCreateViewTest(ViewTestCase):
  """
  Testklasse für die Erstell-Ansicht von TargetGroup.
  """

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(login_as_admin, 'targetgroup_create', None, 200, HTML, 'Zielgruppe')

  def test_get_no_role_403(self):
    self.generic_get_test(login_no_role, 'targetgroup_create', None, 403, HTML, '')

  def test_post_success(self):
    self.generic_post_test(
      login_as_admin, 'targetgroup_create', None, {'name': VALID_STRING_A}, 302
    )


class TargetGroupUpdateViewTest(FormViewTestCase):
  """
  Testklasse für die Bearbeitungs-Ansicht von TargetGroup.
  """

  model = TargetGroup
  attributes_values_db_initial = {'name': VALID_STRING_A}

  def setUp(self):
    self.init()

  def test_get_as_admin(self):
    self.generic_get_test(
      login_as_admin, 'targetgroup_update', {'pk': self.test_object.pk}, 200, HTML, VALID_STRING_A
    )

  def test_post_success(self):
    self.generic_post_test(
      login_as_admin,
      'targetgroup_update',
      {'pk': self.test_object.pk},
      {'name': VALID_STRING_B},
      302,
    )
