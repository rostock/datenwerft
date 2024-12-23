import logging
from datetime import date, datetime
from django.conf import settings
from locale import LC_ALL, format_string, setlocale
from pathlib import Path
from uuid import uuid4

logger = logging.getLogger('datenmanagement')


def get_current_year():
  """
  returns current year as a number

  :return: current year as a number
  """
  return int(date.today().year)


def get_data(curr_object, field):
  """
  returns the data of the passed model field for the passed object

  :param curr_object: object
  :param field: model field
  :return:  data of the passed model field for the passed object
  """
  data = getattr(curr_object, field)
  if isinstance(data, datetime):
    data = data.strftime('%Y-%m-%d %H:%M:%S')
  elif isinstance(data, date):
    data = data.strftime('%Y-%m-%d')
  return data


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


def get_thumb_url(url):
  """
  returns the associated thumbnail URL for the passed URL of a photo

  :param url: URL of a photo
  :return: associated thumbnail URL for the passed URL of a photo
  """
  path = Path(url)
  return str(path.parent / 'thumbs' / path.name)


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


def localize_number(value):
  """
  returns the passed numerical value localized

  :param value: numerical value
  :return: localized version of the passed numerical value
  """
  setlocale(LC_ALL, 'de_DE.UTF-8')
  return format_string('%.2f', value, grouping=True)


def path_and_rename(path, foreign_key_subdir_attr: str = ""):
  """
  cleans passed path and returns it

  :param path: path
  :param foreign_key_subdir_attr: use instance attribute as subdirectory
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
    if foreign_key_subdir_attr:
      subdir = str(getattr(instance, foreign_key_subdir_attr))
      return Path(path) / subdir / filename
    else:
      return Path(path) / filename
  return wrapper


def user_has_model_permissions_any(user, model):
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


def user_has_model_permissions_change_delete_view(user, model):
  """
  checks whether the passed user has change, delete or view rights on the passed model

  :param user: user
  :param model: model
  :return: has the passed user change, delete or view rights on the passed model?
  """
  model_name_lower = model.__name__.lower()
  if (
      user.has_perm('datenmanagement.change_' + model_name_lower)
      or user.has_perm('datenmanagement.delete_' + model_name_lower)
      or user.has_perm('datenmanagement.view_' + model_name_lower)
  ):
    return True
  else:
    return False
