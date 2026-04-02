from re import sub

from django import template
from django.apps import apps
from django.template.defaultfilters import stringfilter
from django.urls import reverse

from datenmanagement.utils import is_address_related_field

register = template.Library()


@register.filter
def build_change_link(model_name, object_id):
  """
  builds link to form page for updating object with passed ID of passed model and returns it

  :param model_name: model name
  :param object_id: object ID
  :return: link to form page for updating object with passed ID of passed model
  """
  return reverse('datenmanagement:' + model_name + '_change', args=[object_id])


@register.filter
def build_geometry_link(model_name):
  """
  builds link for querying the geometries of passed model and returns it

  :param model_name: model name
  :return: link for querying the geometries of passed model
  """
  return reverse('datenmanagement:' + model_name + '_geometry')


@register.filter
@stringfilter
def clean_error_message(value):
  """
  cleans passed form error message and returns it

  :param value: form error message
  :return: cleaned version of the passed form error message
  """
  if 'mit diesem' in value and 'existiert bereits' in value:
    value = sub(r' existiert bereits.*$', '!', value)
    value = sub(
      r'^.* mit diesem',
      'Es existiert bereits ein Datensatz mit den angegebenen Werten in den Attributen',
      value,
    )
    value = sub(r'Wert für das Feld ', '', value)
    return value
  elif 'existiert bereits' in value:
    return value[:-1]
  else:
    return 'Fehler bei der Eingabe'


@register.filter
def get_class_name(value):
  """
  returns class name of passed model

  :param value: model
  :return: class name of passed model
  """
  return value.__class__.__name__


@register.filter
def get_distinct_field_values(field_name, model_name):
  """
  returns distinct values of passed field of passed model

  :param field_name: field name
  :param model_name: model class name
  :return: distinct values of passed field of passed model
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)

  # get all related objects via foreign key
  # (use select_related to avoid N+1 queries)
  objects = model.objects.select_related(field_name).all()
  # build a set of distinct string representations
  distinct_values = {str(getattr(obj, field_name)) for obj in objects}
  # convert to a sorted list
  distinct_values_list = sorted(distinct_values)
  return distinct_values_list


@register.filter
@stringfilter
def get_field_verbose_name(field_name, model_name):
  """
  returns title of passed field of passed model

  :param field_name: field name
  :param model_name: model class name
  :return: title of passed field of passed model
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model._meta.get_field(field_name).verbose_name


@register.filter
@stringfilter
def get_foreign_key_field_class_name(field_name, model_name):
  """
  returns class name of model referenced by passed model in passed foreign key field

  :param field_name: foreign key field name
  :param model_name: model class name
  :return: class name of model referenced by passed model in passed foreign key field
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model._meta.get_field(field_name).remote_field.model.__name__


@register.filter
def get_foreign_key_object_pk(data_object, field_name):
  """
  returns primary key of target object referenced via passed foreign key field of passed object

  :param data_object: object
  :param field_name: foreign key field name
  :return: primary key of target object referenced via passed foreign key field of passed object
  """
  return getattr(data_object, field_name).pk


@register.filter
def get_list_item_by_index(arg_list, i):
  """
  returns content of passed list at passed index

  :param arg_list: list
  :param i: index
  :return: content of passed list at passed index
  """
  return arg_list[i]


@register.filter
@stringfilter
def get_type_of_field(field_name, model_name):
  """
  returns class name of passed field of passed model

  :param field_name: field name
  :param model_name: model class name
  :return: class name of passed field of passed model
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model._meta.get_field(field_name).__class__.__name__


@register.filter
def get_value_of_field(data_object, field_name):
  """
  returns value of passed field of passed object

  :param data_object: object
  :param field_name: field name
  :return: value of passed field of passed object
  """
  return_value = getattr(data_object, field_name)
  if isinstance(return_value, list):
    return ', '.join(return_value)
  else:
    return return_value


@register.filter
def has_model_geometry_field(model_name):
  """
  checks if passed model has a geometry related field

  :param model_name: model class name
  :return: passed model has a geometry related field?
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return True if model.BasemodelMeta.geometry_type else False


@register.filter
def is_field_address_related_field(field):
  """
  checks if passed field is an address related field

  :param field: field
  :return: passed field is an address related field?
  """
  return is_address_related_field(field)


@register.filter
def is_field_hours_related_field(field):
  """
  checks if passed field is an (opening) hours related field

  :param field: field
  :return: passed field is an (opening) hours related field?
  """
  return field.name.endswith('zeiten')


@register.filter
def is_field_nullable(field_name, model_name):
  """
  checks if passed field of passed model may contain NULL values

  :param field_name: field name
  :param model_name: model class name
  :return: passed field of passed model may contain NULL values?
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model._meta.get_field(field_name).null


@register.filter
def is_model_editable(model_name):
  """
  checks if passed model is editable

  :param model_name: model class name
  :return: passed model is editable?
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model.BasemodelMeta.editable


@register.filter
def user_has_model_add_permission(user, model_name_lower):
  """
  checks whether the passed user has creation rights on the passed model

  :param user: user
  :param model_name_lower: model name
  :return: has the passed user creation rights on the passed model?
  """
  return user.has_perm('datenmanagement.add_' + model_name_lower)


@register.filter
def user_has_model_change_permission(user, model_name_lower):
  """
  checks whether the passed user has update rights on the passed model

  :param user: user
  :param model_name_lower: model name
  :return: has the passed user update rights on the passed model?
  """
  return user.has_perm('datenmanagement.change_' + model_name_lower)


@register.filter
def user_has_model_delete_permission(user, model_name_lower):
  """
  checks whether the passed user has deletion rights on the passed model

  :param user: user
  :param model_name_lower: model name
  :return: has the passed user deletion rights on the passed model?
  """
  return user.has_perm('datenmanagement.delete_' + model_name_lower)


@register.filter
def user_has_model_view_permission(user, model_name_lower):
  """
  checks whether the passed user has view rights on the passed model

  :param user: user
  :param model_name_lower: model name
  :return: has the passed user view rights on the passed model?
  """
  return user.has_perm('datenmanagement.view_' + model_name_lower)
