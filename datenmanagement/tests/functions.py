from django.contrib.contenttypes.models import ContentType
from django.db import connections
from pathlib import Path
from shutil import rmtree

from toolbox.models import Subsets


def clean_object_filter(model, object_filter):
  """
  cleans passed object filter and returns it

  :param model: model
  :param object_filter: object filter
  :return: cleaned version of passed object filter
  """
  cleaned_object_filter = object_filter.copy()
  # always remove geometry and file fields from passed object filter
  cleaned_object_filter = remove_file_attributes_from_object_filter(cleaned_object_filter)
  cleaned_object_filter.pop('geometrie', None)
  # if one of the attributes in the passed object filter is among those attributes
  # which shall be rendered as read-only in the form views of the passed model...
  if model.BasemodelMeta.readonly_fields:
    for attribute in object_filter:
      if attribute in model.BasemodelMeta.readonly_fields:
        # remove attribute from object filter
        # since otherwise it may happen that the object below is not found
        # (for example, with attributes that are manipulated at database level after saving)
        cleaned_object_filter.pop(attribute)
  return cleaned_object_filter


def create_test_subset(model, test_object):
  """
  returns a subset with the passed test object of the passed model

  :param model: model
  :param test_object: test object
  :return: subset with the passed test object of the passed model
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
  returns an object of the passed model from the database,
  to which the passed object filter fits

  :param model: model
  :param object_filter: object filter
  :return: an object of the passed model from the database, to which the passed object filter fits
  """
  return model.objects.get(**object_filter)


def load_sql_schema():
  """
  loads an SQL schema into a database
  """
  schema_file = open(Path(__file__).resolve().parent.parent / 'sql/schema.sql', 'r')
  schema_sql = schema_file.read()
  with connections['datenmanagement'].cursor() as cursor:
    cursor.execute(schema_sql)
  schema_file.close()


def remove_file_attributes_from_object_filter(object_filter):
  """
  returns the variant of the passed object filter that has been cleaned of file attributes

  :param object_filter: object filter
  :return: the variant of the passed object filter that has been cleaned of file attributes
  """
  object_filter.pop('foto', None)
  object_filter.pop('pdf', None)
  object_filter.pop('punktwolke', None)
  return object_filter


def remove_uploaded_test_files(path):
  """
  deletes directory with uploaded test files

  :param path: path of directory with uploaded test files
  """
  if path.exists():
    rmtree(path)
