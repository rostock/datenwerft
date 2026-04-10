from angebotsdb.models.base import UserProfile

from .constant_vars import PASSWORD, USERNAME, USERNAME_PROVIDER, USERNAME_REVIEWER


def get_object(model, object_filter):
  """
  Gibt das erste Objekt des übergebenen Modells zurück, das dem Filter entspricht.

  :param model: Modellklasse
  :param object_filter: Filter-Dict
  :return: Modell-Instanz oder None
  """
  return model.objects.filter(**object_filter).first()


def login_as_admin(test):
  """
  Loggt den Admin-Testnutzer ein und weist ihn der Admin-Gruppe zu.

  :param test: Testinstanz
  """
  test.admin_group.user_set.add(test.admin_user)
  test.client.login(username=USERNAME, password=PASSWORD)


def login_as_provider(test):
  """
  Loggt den Provider-Testnutzer ein, weist ihn der Users-Gruppe zu
  und verknüpft ihn per UserProfile mit test.test_provider.

  Setzt voraus, dass test.test_provider existiert (in setUpTestData angelegt).

  :param test: Testinstanz
  """
  test.users_group.user_set.add(test.provider_user)
  UserProfile.objects.create(
    user_id=test.provider_user.id,
    provider=test.test_provider,
  )
  test.client.login(username=USERNAME_PROVIDER, password=PASSWORD)


def login_as_reviewer(test):
  """
  Loggt den Reviewer-Testnutzer ein, weist ihn der Users-Gruppe zu
  und verknüpft ihn per UserProfile mit test.test_org_unit.

  Setzt voraus, dass test.test_org_unit existiert (in setUpTestData angelegt).

  :param test: Testinstanz
  """
  test.users_group.user_set.add(test.reviewer_user)
  UserProfile.objects.create(
    user_id=test.reviewer_user.id,
    organisational_unit=test.test_org_unit,
  )
  test.client.login(username=USERNAME_REVIEWER, password=PASSWORD)


def login_no_role(test):
  """
  Loggt einen Nutzer ein, der keine Gruppe und kein UserProfile hat.

  :param test: Testinstanz
  """
  test.client.login(username=USERNAME_PROVIDER, password=PASSWORD)
