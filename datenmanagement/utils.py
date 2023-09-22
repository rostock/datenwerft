from datetime import date
from django.conf import settings
from django.contrib.gis.db.models.fields import LineStringField as ModelLineStringField
from django.contrib.gis.db.models.fields import MultiLineStringField as ModelMultiLineStringField
from django.contrib.gis.db.models.fields import MultiPolygonField as ModelMultiPolygonField
from django.contrib.gis.db.models.fields import PointField as ModelPointField
from django.contrib.gis.db.models.fields import PolygonField as ModelPolygonField
from django.contrib.gis.forms.fields import LineStringField as FormLineStringField
from django.contrib.gis.forms.fields import MultiLineStringField as FormMultiLineStringField
from django.contrib.gis.forms.fields import MultiPolygonField as FormMultiPolygonField
from django.contrib.gis.forms.fields import PointField as FormPointField
from django.contrib.gis.forms.fields import PolygonField as FormPolygonField
from pathlib import Path
from uuid import uuid4


def get_current_year():
  """
  returns current year as a number

  :return: current year as a number
  """
  return int(date.today().year)


def get_field_name_for_address_type(model, l10n=True):
  """
  returns name of address related field depending on address reference type of passed model

  :param model: model
  :param l10n: localized name version?
  :return: name of address related field depending on address reference type of passed model
  """
  if model.BasemodelMeta.address_type == 'Adresse':
    return 'adresse' if l10n else 'address'
  elif model.BasemodelMeta.address_type == 'Straße':
    return 'strasse' if l10n else 'street'
  elif model.BasemodelMeta.address_type == 'Gemeindeteil':
    return 'gemeindeteil' if l10n else 'district'
  return None


def get_path(url):
  """
  returns path related to passed URL

  :param url: URL
  :return: path related to passed URL
  """
  if settings.MEDIA_ROOT and settings.MEDIA_URL:
    path = Path(settings.MEDIA_ROOT) / url[len(settings.MEDIA_URL):]
  else:
    path = Path(settings.BASE_DIR) / url
  return path


def is_address_related_field(field):
  """
  checks if passed field is an address related field

  :param field: field
  :return: passed field is an address related field?
  """
  if field.name == 'adresse' or field.name == 'strasse' or field.name == 'gemeindeteil':
    return True
  else:
    return False


def is_geometry_field(field):
  """
  checks if passed field is a geometry related field

  :param field: field
  :return: passed field is a geometry related field?
  """
  if (
      issubclass(field, FormLineStringField)
      or issubclass(field, ModelLineStringField)
      or issubclass(field, FormMultiLineStringField)
      or issubclass(field, ModelMultiLineStringField)
      or issubclass(field, FormMultiPolygonField)
      or issubclass(field, ModelMultiPolygonField)
      or issubclass(field, FormPointField)
      or issubclass(field, ModelPointField)
      or issubclass(field, FormPolygonField)
      or issubclass(field, ModelPolygonField)
  ):
    return True
  else:
    return False


def path_and_rename(path):
  """
  cleans passed path and returns it

  :param path: path
  :return: cleaned version of passed path
  """
  def wrapper(instance, filename):
    """
    sets path based on passed object and passed file name and returns it

    :param instance: object
    :param filename: file name
    :return: path set based on passed object and passed file name
    """
    if hasattr(instance, 'dateiname_original'):
      instance.dateiname_original = filename
    ext = filename.split('.')[-1]
    if hasattr(instance, 'uuid'):
      filename = '{0}.{1}'.format(str(instance.uuid), ext.lower())
    else:
      filename = '{0}.{1}'.format(str(uuid4()), ext.lower())
    return Path(path) / filename
  return wrapper


def user_has_model_permissions_at_all(user, model):
  """
  checks whether the passed user has any rights on the passed model

  :param user: user
  :param model: model
  :return: has the passed user any rights on the passed model?
  """
  model_name_lower = model.__name__.lower()
  if (
      user.has_perm('datenmanagement.add_' + model_name_lower)
      or user.has_perm('datenmanagement.change_' + model_name_lower)
      or user.has_perm('datenmanagement.delete_' + model_name_lower)
      or user.has_perm('datenmanagement.view_' + model_name_lower)
  ):
    return True
  else:
    return False
