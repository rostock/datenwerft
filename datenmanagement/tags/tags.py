from django import template
from django.apps import apps
from django.contrib.gis import forms
from guardian.core import ObjectPermissionChecker
import os
import re

register = template.Library()


@register.filter
def customize_error_message(value):
  """
  bereinigt übergebene Formularfehlermeldung

  :param value: Formularfehlermeldung
  :return: bereinigte übergebene Formularfehlermeldung oder allgemeine Fehlermeldung
  """
  if 'existiert bereits' in value:
    return value[:-1]
  else:
    return 'Fehler bei der Eingabe'


@register.filter
def get_class_foreign_key_label(value):
  """
  liefert, falls vorhanden, Feld mit Fremdschlüssel zu übergebenem Datenmodell zurück

  :param value: Datenmodell
  :return: Feld mit Fremdschlüssel zu übergebenem Datenmodell oder nichts
  """
  if hasattr(value.__class__._meta, 'foreign_key_label'):
    return value.__class__._meta.foreign_key_label
  else:
    return None


@register.filter
def get_class_name(value):
  """
  liefert Klassenname des übergebenen Datenmodells zurück

  :param value: Datenmodell
  :return: Klassenname des übergebenen Datenmodells
  """
  return value.__class__.__name__


@register.filter
def get_class_object_title(value):
  """
  liefert, falls vorhanden, Textbaustein für die Löschansicht zu übergebenem Datenmodell zurück

  :param value: Datenmodell
  :return: Textbaustein für die Löschansicht zu übergebenem Datenmodell oder nichts
  """
  if hasattr(value.__class__._meta, 'object_title'):
    return value.__class__._meta.object_title
  else:
    return None


@register.filter
def get_class_verbose_name_plural(value):
  """
  liefert ausführliche Bezeichnung (im Plural) des übergebenen Datenmodells zurück

  :param value: Datenmodell
  :return: ausführliche Bezeichnung (im Plural) des übergebenen Datenmodells
  """
  return value.__class__._meta.verbose_name_plural


@register.filter
def get_dict_value_by_key(arg_dict, key):
  """
  liefert Wert des übergebenen Dictionaries am übergebenen Schlüssel zurück

  :param arg_dict: Dictionary
  :param key: Schlüssel
  :return: Wert des übergebenen Dictionaries am übergebenen Schlüssel
  """
  return arg_dict.get(key)


@register.filter
def get_foreign_key_field_class_name(field_name, model_name):
  """
  liefert Klassenname des vom übergebenen Datenmodells
  im übergebenen Feld referenzierten Datenmodells zurück

  :param field_name: Feldname des Datenmodells
  :param model_name: Klassenname des Datenmodells
  :return: Klassenname des vom übergebenen Datenmodell
  im übergebenen Feld referenzierten Datenmodells
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model._meta.get_field(field_name).remote_field.model.__name__


@register.filter
def get_list_item_by_index(arg_list, i):
  """
  liefert Inhalt der übergebenen Liste am übergebenen Index zurück

  :param arg_list: Liste
  :param i: Index
  :return: Inhalt der übergebenen Liste am übergebenen Index
  """
  return arg_list[i]


@register.filter
def get_thumb_url(value):
  """
  liefert Thumbnail-Pfad zum übergebenen Pfad zurück

  :param value: Pfad
  :return: Thumbnail-Pfad zum übergebenen Pfad
  """
  head, tail = os.path.split(value)
  return head + '/thumbs/' + tail


@register.filter
def get_type_of_field(field_name, model_name):
  """
  liefert Klassenname des übergebenen Feldes des übergebenen Datenmodells zurück

  :param field_name: Feldname des Datenmodells
  :param model_name: Klassenname des Datenmodells
  :return: Klassenname des übergebenen Feldes des übergebenen Datenmodells
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  type_of_field = re.sub(
    r'\'>$', '', re.sub(
      r'^.*\.', '', str(model._meta.get_field(field_name).__class__)))
  return type_of_field


@register.filter
def get_value_of_field(value, field):
  """
  liefert Wert des übergebenen Feldes des übergebenen Datenobjektes zurück

  :param value: Datenobjekt
  :param field: Feld
  :return: Wert des übergebenen Feldes des übergebenen Datenobjektes
  """
  return_value = getattr(value, field)
  if isinstance(return_value, list):
    return ', '.join(return_value)
  else:
    return return_value


@register.filter
def is_field_address_related_field(field):
  """
  prüft, ob das übergebene Feld einen Adressenbezug aufweist

  :param field: Feld
  :return: weist übergebenes Feld einen Adressenbezug auf?
  """
  if (field.name == 'adresse' or
      field.name == 'strasse' or
      field.name == 'gemeindeteil'):
    return True
  else:
    return False


@register.filter
def is_field_geometry_field(field):
  """
  prüft, ob das übergebene Feld ein Geometriefeld ist

  :param field: Feld
  :return: ist übergebenes Feld ein Geometriefeld?
  """
  if (field.field.__class__ == forms.PointField or
      field.field.__class__ == forms.LineStringField or
      field.field.__class__ == forms.MultiLineStringField or
      field.field.__class__ == forms.PolygonField or
      field.field.__class__ == forms.MultiPolygonField):
    return True
  else:
    return False


@register.filter
def is_field_hours_related_field(field):
  """
  prüft, ob das übergebene Feld Öffnungszeiten oder Ähnliches enthält

  :param field: Feld
  :return: enthält übergebenes Feld Öffnungszeiten oder Ähnliches?
  """
  if field.name.endswith('zeiten'):
    return True
  else:
    return False


@register.filter
def is_field_nullable(field_name, model_name):
  """
  prüft, ob das übergebenene Feld des übergebenen Datenmodells NULL-Werte enthalten darf

  :param field_name: Feldname des Datenmodells
  :param model_name: Klassenname des Datenmodells
  :return: darf das übergebenene Feld des übergebenen Datenmodells NULL-Werte enthalten?
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model._meta.get_field(field_name).null


@register.filter
def user_has_model_permission(user, obj):
  """
  prüft, ob der übergebenene Nutzer generell Rechte am Datenmodell des übergebenen Datenobjekts hat

  :param user: Nutzer
  :param obj: Datenobjekt
  :return: hat der übergebenene Nutzer generell Rechte am Datenmodell des übergebenen Datenobjekts?
  """
  permission_add = user.has_perm(
    'datenmanagement.add_' + obj.__class__.__name__.lower())
  permission_change = user.has_perm(
    'datenmanagement.change_' + obj.__class__.__name__.lower())
  permission_delete = user.has_perm(
    'datenmanagement.delete_' + obj.__class__.__name__.lower())
  permission_view = user.has_perm(
    'datenmanagement.view_' + obj.__class__.__name__.lower())
  if (permission_change or permission_add or
      permission_delete or permission_view):
    return True
  else:
    return False


@register.filter
def user_has_model_add_permission(user, model_name_lower):
  """
  prüft, ob der übergebenene Nutzer Rechte zum Hinzufügen von Datenobjekten
  im übergebenen Datenmodell hat

  :param user: Nutzer
  :param model_name_lower: Name des Datenmodells
  :return: hat der übergebenene Nutzer Rechte zum Hinzufügen von Datenobjekten
  im übergebenen Datenmodell?
  """
  if user.has_perm('datenmanagement.add_' + model_name_lower):
    return True
  else:
    return False


@register.filter
def user_has_model_change_permission(user, model_name_lower):
  """
  prüft, ob der übergebenene Nutzer Rechte zum Ändern von Datenobjekten
  im übergebenen Datenmodell hat

  :param user: Nutzer
  :param model_name_lower: Name des Datenmodells
  :return: hat der übergebenene Nutzer Rechte zum Ändern von Datenobjekten
  im übergebenen Datenmodell?
  """
  if user.has_perm('datenmanagement.change_' + model_name_lower):
    return True
  else:
    return False


@register.filter
def user_has_model_delete_permission(user, model_name_lower):
  """
  prüft, ob der übergebenene Nutzer Rechte zum Löschen von Datenobjekten
  im übergebenen Datenmodell hat

  :param user: Nutzer
  :param model_name_lower: Name des Datenmodells
  :return: hat der übergebenene Nutzer Rechte zum Löschen von Datenobjekten
  im übergebenen Datenmodell?
  """
  if user.has_perm('datenmanagement.delete_' + model_name_lower):
    return True
  else:
    return False


@register.filter
def user_has_model_view_permission(user, model_name_lower):
  """
  prüft, ob der übergebenene Nutzer Rechte zum Ansehen von Datenobjekten
  im übergebenen Datenmodell hat

  :param user: Nutzer
  :param model_name_lower: Name des Datenmodells
  :return: hat der übergebenene Nutzer Rechte zum Ansehen von Datenobjekten
  im übergebenen Datenmodell?
  """
  if user.has_perm('datenmanagement.view_' + model_name_lower):
    return True
  else:
    return False


@register.filter
def user_has_object_change_permission(user, obj):
  """
  prüft, ob der übergebenene Nutzer Rechte zum Ändern des übergebenen Datenobjekts hat

  :param user: Nutzer
  :param obj: Datenobjekt
  :return: hat der übergebenene Nutzer Rechte zum Ändern des übergebenen Datenobjekts?
  """
  if ObjectPermissionChecker(user).has_perm(
      'change_' + obj.__class__.__name__.lower(), obj):
    return True
  else:
    return False


@register.filter
def user_has_object_delete_permission(user, obj):
  """
  prüft, ob der übergebenene Nutzer Rechte zum Löschen des übergebenen Datenobjekts hat

  :param user: Nutzer
  :param obj: Datenobjekt
  :return: hat der übergebenene Nutzer Rechte zum Löschen des übergebenen Datenobjekts?
  """
  if ObjectPermissionChecker(user).has_perm(
      'delete_' + obj.__class__.__name__.lower(), obj):
    return True
  else:
    return False
