from django.conf import settings
from django.contrib.gis.db.models.fields import PointField as ModelPointField
from django.contrib.gis.forms.fields import PointField as FormPointField


LOG_ACTIONS = {
  'created': 'neu angelegt',
  'deleted': 'gelöscht',
  'updated_complainers_organizations': 'Beschwerdeführerin(nen) geändert auf: <em>{}</em>',
  'cleared_complainers_organizations': 'alle Beschwerdeführerin(nen) entfernt',
  'updated_complainers_persons': 'Beschwerdeführer:in(nen) geändert auf: <em>{}</em>',
  'cleared_complainers_persons': 'alle Beschwerdeführer:in(nen) entfernt',
  'updated_operator': 'Betreiberin geändert auf: <em>{}</em>',
  'updated_originator': 'Verursacher geändert auf: <em>{}</em>',
  'updated_status': 'Bearbeitungsstatus geändert auf: <em>{}</em>'
}


def concat_address(street=None, house_number=None, postal_code=None, place=None):
  """
  concats given address string parts and returns address string

  :param street: street name
  :param house_number: house number
  :param postal_code: postal code
  :param place: place
  :return: address string
  """
  first_part = (street + ' ' if street else '') + (house_number if house_number else '')
  second_part = (postal_code + ' ' if postal_code else '') + (place if place else '')
  if first_part and second_part:
    return first_part.strip() + ', ' + second_part.strip()
  elif first_part:
    return first_part.strip()
  elif second_part:
    return second_part.strip()
  else:
    return None


def get_foreign_key_target_model(foreign_key_field):
  """
  returns target model of given foreign key field

  :param foreign_key_field: foreign key field
  :return: target model of given foreign key field
  """
  return foreign_key_field.remote_field.model


def get_foreign_key_target_object(source_object, foreign_key_field):
  """
  returns target object of given foreign key field of given source object

  :param source_object: source object
  :param foreign_key_field: foreign key field
  :return: target object of given foreign key field of given source object
  """
  return getattr(source_object, foreign_key_field.name)


def get_icon_from_settings(key):
  """
  returns icon (i.e. value) of given key in icon dictionary

  :param key: key in icon dictionary
  :return: icon (i.e. value) of given key in icon dictionary
  """
  return settings.BEMAS_ICONS.get(key, 'poo')


def is_bemas_admin(user):
  """
  checks if given user is a BEMAS admin

  :param user: user
  :return: given user is a BEMAS admin?
  """
  return user.groups.filter(name=settings.BEMAS_ADMIN_GROUP_NAME)


def is_bemas_user(user, only_bemas_user_check=False):
  """
  checks if given user is a BEMAS user
  (and optionally checks if it is a BEMAS user only)

  :param user: user
  :param only_bemas_user_check: check if user is a BEMAS user only?
  :return: given user is a BEMAS user (only)?
  """
  in_bemas_groups = user.groups.filter(
    name__in=[settings.BEMAS_ADMIN_GROUP_NAME, settings.BEMAS_USERS_GROUP_NAME]
  )
  if in_bemas_groups:
    if only_bemas_user_check:
      # if user is a BEMAS user only, he is not a member of any other group
      return in_bemas_groups.count() == user.groups.all().count()
    else:
      return True
  else:
    return False


def is_geometry_field(field):
  """
  checks if given field is a geometry related field

  :param field: field
  :return: given field is a geometry related field?
  """
  if issubclass(field, FormPointField) or issubclass(field, ModelPointField):
    return True
  else:
    return False


def shorten_string(string, max_chars=20, suspension_point=True):
  """
  shortens given string and returns it

  :param string: string to be shortened
  :param max_chars: maximum number of characters
  :param suspension_point: add ellipsis at the end?
  :return: shortened string
  """
  if len(string) <= max_chars:
    return string
  else:
    string = string[0:20].strip()
    if suspension_point:
      return string + '…' if len(string) < max_chars else string[:-1] + '…'
    else:
      return string
