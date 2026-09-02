from django.apps import apps
from django.db.migrations.autodetector import MigrationAutodetector
from django.db.migrations.loader import MigrationLoader
from django.db.migrations.questioner import NonInteractiveMigrationQuestioner
from django.db.migrations.state import ProjectState
from django.test import SimpleTestCase

APP_LABEL = 'pygeoapi'
INITIAL_MIGRATION = '0001_initial'
# the models the app already had before the rights system was introduced
PREEXISTING_MODELS = frozenset({'collection', 'databaseconnection'})


class PygeoapiMigrationsTest(SimpleTestCase):
  """
  guards against drift between the pygeoapi models and their migrations
  """

  # this is the same comparison "manage.py makemigrations pygeoapi --check" makes,
  # but run directly on the autodetector: the management command additionally
  # verifies the migration history of every configured database, and the test
  # runner only creates a test database for the aliases the tests declare.
  # Calling it here would either query the real databases of the other apps or
  # force all of them to be created for this single check.
  def test_models_and_migrations_are_in_sync(self):
    loader = MigrationLoader(None, ignore_no_migrations=True)
    autodetector = MigrationAutodetector(
      loader.project_state(),
      ProjectState.from_apps(apps),
      NonInteractiveMigrationQuestioner(specified_apps={APP_LABEL}, dry_run=True),
    )
    changes = autodetector.changes(
      graph=loader.graph,
      trim_to_apps={APP_LABEL},
      convert_apps={APP_LABEL},
    )
    self.assertNotIn(
      APP_LABEL,
      changes,
      'Die Modelle der App pygeoapi und ihre Migrationen laufen auseinander. '
      'Fix: "manage.py makemigrations pygeoapi" ausführen und die neue Migration '
      'mitcommitten.',
    )

  # README und docs/pygeoapi/rechtesystem.md sagen zu, dass die Einführung des
  # Rechtesystems bestehende Kollektionen und Datenbankverbindungen unberührt
  # lässt. Geprüft wird genau das und nicht der Operationstyp: eine additive
  # Änderung an einer der drei neuen Tabellen, etwa das AddField in 0005, hält
  # die Zusage und darf hier nicht anschlagen.
  def test_migrations_after_the_initial_one_leave_the_preexisting_tables_alone(self):
    loader = MigrationLoader(None, ignore_no_migrations=True)
    migrations = {
      name: migration
      for (app_label, name), migration in loader.disk_migrations.items()
      if app_label == APP_LABEL and name != INITIAL_MIGRATION
    }
    # guards against a green run on an empty selection
    self.assertTrue(migrations)
    for name, migration in sorted(migrations.items()):
      for operation in migration.operations:
        model = self.affected_model(operation)
        self.assertIsNotNone(
          model,
          f'Die Migration pygeoapi/{name} enthält die Operation '
          f'{type(operation).__name__}, die kein Modell benennt (etwa RunSQL '
          'oder RunPython). Welche Tabellen sie anfasst, ist hier nicht '
          'feststellbar, die Zusage aus README (Abschnitt "Einführung des '
          'Rechtesystems in bestehenden Instanzen") und '
          'docs/pygeoapi/rechtesystem.md also nicht mehr maschinell gedeckt.',
        )
        self.assertNotIn(
          model,
          PREEXISTING_MODELS,
          f'Die Migration pygeoapi/{name} verändert mit '
          f'{type(operation).__name__} das vorbestehende Modell {model}. Damit '
          'bleiben bestehende Kollektionen und Datenbankverbindungen nicht '
          'mehr unberührt. Ist das gewollt, sind README (Abschnitt "Einführung '
          'des Rechtesystems in bestehenden Instanzen") und '
          'docs/pygeoapi/rechtesystem.md anzupassen und dieser Test zu '
          'erweitern.',
        )

  def affected_model(self, operation):
    """
    the model an operation acts on, lowercased, or None if it names none

    operations on a model carry `name`, those on one of its fields, indexes or
    constraints carry `model_name`; `model_name` is read first because AddField
    and friends carry both, and their `name` is the field's, not the model's
    """
    name = getattr(operation, 'model_name', None) or getattr(operation, 'name', None)
    return name.lower() if name else None
