from datetime import date, datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone as tz

from toolbox.utils import format_date_datetime

LOG_ACTIONS = {
  'created': 'neu angelegt',
  'deleted': 'gelöscht',
  'updated_complainers_organizations': 'Organisation(en) als Beschwerdeführerin(nen) geändert',
  'cleared_complainers_organizations': 'alle Organisationen als Beschwerdeführerinnen entfernt',
  'updated_complainers_persons': 'Person(en) als Beschwerdeführer:in(nen) geändert',
  'cleared_complainers_persons': 'alle Personen als Beschwerdeführer:innen entfernt',
  'updated_operator_organization': 'Organisation als Betreiberin geändert',
  'updated_operator_person': 'Person als Betreiber:in geändert',
  'updated_originator': 'Verursacher geändert',
  'updated_status': 'Bearbeitungsstatus geändert',
}


def generate_user_string(user):
  """
  generates a string out of passed user and returns it

  :param user: user
  :return: string out of passed user
  """
  if isinstance(user, str):
    return user
  elif isinstance(user, User):
    user = {
      'first_name': user.first_name if user.first_name else '',
      'last_name': user.last_name if user.first_name else '',
      'username': user.username,
    }
  if user['first_name'] and user['last_name']:
    return user['first_name'] + ' ' + user['last_name']
  else:
    return user['username']


def get_complaint_status_change_deadline_date(format_date=False):
  """
  returns complaint status change deadline date

  :param format_date: format date?
  :return: complaint status change deadline date
  """
  deadline_date = tz.now() - timedelta(days=settings.BEMAS_STATUS_CHANGE_DEADLINE_DAYS)
  return deadline_date.strftime('%d.%m.%Y') if format_date else deadline_date


def get_foreign_key_target_model(foreign_key_field):
  """
  returns target model of passed foreign key field

  :param foreign_key_field: foreign key field
  :return: target model of passed foreign key field
  """
  return foreign_key_field.remote_field.model


def get_foreign_key_target_object(source_object, foreign_key_field):
  """
  returns target object of passed foreign key field of passed source object

  :param source_object: source object
  :param foreign_key_field: foreign key field
  :return: target object of passed foreign key field of passed source object
  """
  return getattr(source_object, foreign_key_field.name)


def get_icon_from_settings(key):
  """
  returns icon (i.e. value) of passed key in icon dictionary

  :param key: key in icon dictionary
  :return: icon (i.e. value) of passed key in icon dictionary
  """
  return settings.BEMAS_ICONS.get(key, 'poo')


def get_json_data(curr_object, field, for_filters=False):
  """
  returns JSONesque value of passed field of passed object

  :param curr_object: object
  :param field: field
  :param for_filters: for filters?
  :return: JSONesque value of passed field of passed object
  """
  value = getattr(curr_object, field)
  if value:
    # format dates and datetimes
    if not for_filters and (isinstance(value, date) or isinstance(value, datetime)):
      value = format_date_datetime(value)
    # format originators
    elif field == 'originator':
      value = value.sector_and_operator()
    else:
      value = str(value)
  else:
    value = ''
  return value


def get_old_data_deadline_timestamp(format_timestamp=False):
  """
  returns deadline timestamp before which data is considered "old"

  :param format_timestamp: format timestamp?
  :return: deadline timestamp before which data is considered "old"
  """
  deadline_timestamp = tz.now() - timedelta(days=settings.BEMAS_DATA_CONSIDERED_OLD_AFTER_DAYS)
  return (
    deadline_timestamp.strftime('%d.%m.%Y, %H:%M Uhr') if format_timestamp else deadline_timestamp
  )


def get_orphaned_organizations(originator, complaint, organization):
  """
  returns orphaned organizations based on passed originator, complaint
  and organization object classes

  :return: orphaned organizations based on passed originator, complaint
  and organization object classes
  """
  # get all organizations connected to originators
  oris_orgs_ids = originator.objects.filter(operator_organization__isnull=False).values(
    'operator_organization'
  )
  # get all organizations connected to complaints
  cpls_orgs_ids = organization.objects.none().values('id')
  for cpl in complaint.objects.all():
    cpls_orgs_ids = cpls_orgs_ids | cpl.complainers_organizations.all().values('id')
  # get orphaned organizations
  # (i.e. organizations not connected to any originators and any complaints)
  return organization.objects.exclude(id__in=oris_orgs_ids).exclude(id__in=cpls_orgs_ids)


def get_orphaned_originators(complaint, originator):
  """
  returns orphaned originators based on passed complaint and originator object classes

  :return: orphaned originators based on passed complaint and originator object classes
  """
  # get all originators connected to complaints
  cpls_oris_ids = complaint.objects.all().values('originator')
  # get orphaned originators
  # (i.e. originators not connected to any complaints)
  return originator.objects.exclude(id__in=cpls_oris_ids)


def get_orphaned_persons(complaint, contact, originator, person):
  """
  returns orphaned persons based on passed complaint, contact and person object classes

  :return: orphaned persons based on passed complaint, contact and person object classes
  """
  # get active complaints
  # (i.e. complaints with latest status change after deadline date
  # or with status "less" than closed)
  act_cpls = complaint.objects.filter(
    status_updated_at__gt=get_complaint_status_change_deadline_date()
  ) | complaint.objects.filter(status__ordinal__lt=2)
  # get all persons connected to contacts
  con_ps_ids = contact.objects.all().values('person')
  # get all persons connected to originators
  oris_ps_ids = originator.objects.filter(operator_person__isnull=False).values('operator_person')
  # get all persons connected to active complaints
  act_cpls_ps_ids = person.objects.none().values('id')
  for act_cpl in act_cpls:
    act_cpls_ps_ids = act_cpls_ps_ids | act_cpl.complainers_persons.all().values('id')
  # get all persons considered "new"
  new_ps_ids = person.objects.filter(updated_at__gt=get_old_data_deadline_timestamp()).values('id')
  # get orphaned persons
  # (i.e. persons not connected to any contacts, originators, or active complaints
  # and last edited before "old" data deadline timestamp)
  return (
    person.objects.exclude(id__in=con_ps_ids)
    .exclude(id__in=oris_ps_ids)
    .exclude(id__in=act_cpls_ps_ids)
    .exclude(id__in=new_ps_ids)
  )


def is_bemas_admin(user):
  """
  checks if passed user is a BEMAS admin

  :param user: user
  :return: passed user is a BEMAS admin?
  """
  return user.groups.filter(name=settings.BEMAS_ADMIN_GROUP_NAME)


def is_bemas_user(user, only_bemas_user_check=False):
  """
  checks if passed user is a BEMAS user
  (and optionally checks if it is a BEMAS user only)

  :param user: user
  :param only_bemas_user_check: check if user is a BEMAS user only?
  :return: passed user is a BEMAS user (only)?
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


def shorten_string(string, max_chars=20, suspension_point=True):
  """
  shortens passed string and returns it

  :param string: string to be shortened
  :param max_chars: maximum number of characters
  :param suspension_point: add ellipsis at the end?
  :return: shortened string
  """
  if len(string) <= max_chars:
    return string
  else:
    string = string[0:max_chars].strip()
    if suspension_point:
      return string + '…' if len(string) < max_chars else string[:-1] + '…'
    else:
      return string
