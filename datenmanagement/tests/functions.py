from django.contrib.contenttypes.models import ContentType
from django.db import connections
from pathlib import Path
from shutil import rmtree
from toolbox.models import Subsets


def clean_object_filter(model, object_filter):
  """
  liefert die bereinigte Variante des übergebenen Objektfilters zurück

  :param model: Datenmodell
  :param object_filter: Objektfilter
  :return: bereinigte Variante des übergebenen Objektfilters
  """
  cleaned_object_filter = object_filter.copy()
  # falls eines der Attribute im Objektfilter unter jenen Attributen ist,
  # die in den Formularansichten des Datenmodells nur lesbar erscheinen sollen...
  if hasattr(model._meta, 'readonly_fields'):
    for attribute in object_filter:
      if attribute in model._meta.readonly_fields:
        # Attribut aus Objektfilter entfernen, da es ansonsten passieren kann,
        # dass das Objekt unten nicht gefunden wird
        # (etwa bei Attributen, die nach dem Speichern auf Datenbankebene manipuliert werden)
        cleaned_object_filter.pop(attribute)
  # "kritische" Attribute (Dateien, Geometrie) immer aus Objektfilter entfernen
  cleaned_object_filter = remove_file_attributes_from_object_filter(cleaned_object_filter)
  cleaned_object_filter.pop('geometrie', None)
  return cleaned_object_filter


def create_test_subset(model, test_object):
  """
  liefert ein Subset mit dem übergebenen Objekt des übergebenen Datenmodells zurück

  :param model: Datenmodell
  :param test_object: Objekt des übergebenen Datenmodells
  :return: Subset mit dem übergebenen Objekt des übergebenen Datenmodells
  """
  return Subsets.objects.create(
    model=ContentType.objects.filter(
      app_label='datenmanagement',
      model=model._meta.model_name
    ).first(),
    pk_field=model._meta.pk.name,
    pk_values=[
      test_object.pk
    ]
  )


def get_object(model, object_filter):
  """
  holt ein Objekt des übergebenen Datenmodells aus der Datenbank,
  auf den der übergebene Objektfilter passt, und liefert dieses zurück

  :param model: Datenmodell
  :param object_filter: Objektfilter
  :return: Objekt des übergebenen Datenmodells, auf den der übergebene Objektfilter passt
  """
  return model.objects.get(**object_filter)


def load_sql_schema():
  """
  lädt ein SQL-Schema in eine Datenbank
  """
  schema_file = open(Path(__file__).resolve().parent.parent / 'sql/schema.sql', 'r')
  schema_sql = schema_file.read()
  with connections['datenmanagement'].cursor() as cursor:
    cursor.execute(schema_sql)


def remove_file_attributes_from_object_filter(object_filter):
  """
  liefert die um Dateien-Attribute bereinigte Variante des übergebenen Objektfilters zurück

  :param object_filter: Objektfilter
  :return: um Dateien-Attribute bereinigte Variante des übergebenen Objektfilters
  """
  object_filter.pop('dokument', None)
  object_filter.pop('foto', None)
  object_filter.pop('pdf', None)
  return object_filter


def remove_uploaded_test_files(path):
  """
  löscht das Verzeichnis mit den hochgeladenen Testdateien

  :param path: Verzeichnis mit den hochgeladenen Testdateien
  """
  if path.exists():
    rmtree(path)
