import os

from django import template
from django.apps import apps
from django.contrib.gis.forms import LineStringField, MultiLineStringField, MultiPolygonField, \
  PointField, PolygonField
from re import sub

register = template.Library()


@register.filter
def customize_error_message(value):
  """
  bereinigt übergebene Formularfehlermeldung

  :param value: Formularfehlermeldung
  :return: bereinigte übergebene Formularfehlermeldung oder allgemeine Fehlermeldung
  """
  if 'mit diesem' in value and 'existiert bereits' in value:
    value = sub(r' existiert bereits.*$', '!', value)
    value = sub(
      r'^.* mit diesem',
      'Es existiert bereits ein Datensatz mit den angegebenen Werten in den Attributen',
      value
    )
    return value
  elif 'existiert bereits' in value:
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
def get_field_verbose_name(field_name, model_name):
  """
  liefert Titel des übergebenen Feldes des übergebenen Datenmodells zurück

  :param field_name: Feldname des Datenmodells
  :param model_name: Klassenname des Datenmodells
  :return: Titel des übergebenen Feldes des übergebenen Datenmodells
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model._meta.get_field(field_name).verbose_name


@register.filter
def get_foreign_key_field_class_name(field_name, model_name):
  """
  liefert Klassenname des vom übergebenen Datenmodell
  im übergebenen Fremdschlüsselfeld referenzierten Datenmodells zurück

  :param field_name: Name des Fremdschlüsselfelds des Datenmodells
  :param model_name: Klassenname des Datenmodells
  :return: Klassenname des vom übergebenen Datenmodell
  im übergebenen Fremdschlüsselfeld referenzierten Datenmodells
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model._meta.get_field(field_name).remote_field.model.__name__


@register.filter
def get_foreign_key_object_pk(data_object, field_name):
  """
  liefert Primärschlüssel des im übergebenen Fremdschlüsselfeld
  des übergebenen Datenobjektes abgelegten Zielobjekts zurück

  :param data_object: Datenobjekt
  :param field_name: Name des Fremdschlüsselfelds
  :return: Primärschlüssel des im übergebenen Fremdschlüsselfeld
  des übergebenen Datenobjektes abgelegten Zielobjekts
  """
  return getattr(data_object, field_name).pk


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
  type_of_field = sub(
    r'\'>$', '', sub(
      r'^.*\.', '', str(model._meta.get_field(field_name).__class__)))
  return type_of_field


@register.filter
def get_value_of_field(data_object, field_name):
  """
  liefert Wert des übergebenen Feldes des übergebenen Datenobjektes zurück

  :param data_object: Datenobjekt
  :param field_name: Name des Feldes
  :return: Wert des übergebenen Feldes des übergebenen Datenobjektes
  """
  return_value = getattr(data_object, field_name)
  if isinstance(return_value, list):
    return ', '.join(return_value)
  else:
    return return_value


@register.filter
def has_model_geometry_field(model_name):
  """
  prüft, ob das übergebene Datenmodell ein Geometriefeld hat

  :param model_name: Klassenname des Datenmodells
  :return: hat übergebenes Datenmodell ein Geometriefeld?
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return True if hasattr(model._meta, 'geometry_type') else False


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
  if (field.field.__class__ == PointField or
      field.field.__class__ == LineStringField or
      field.field.__class__ == MultiLineStringField or
      field.field.__class__ == PolygonField or
      field.field.__class__ == MultiPolygonField):
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
  prüft, ob das übergebene Feld des übergebenen Datenmodells NULL-Werte enthalten darf

  :param field_name: Feldname des Datenmodells
  :param model_name: Klassenname des Datenmodells
  :return: darf das übergebene Feld des übergebenen Datenmodells NULL-Werte enthalten?
  """
  model = apps.get_app_config('datenmanagement').get_model(model_name)
  return model._meta.get_field(field_name).null


@register.filter
def replace(value, arg):
  """
  ersetzt Zeichenkette in übergebenem Wert

  :param value: Wert
  :param arg: Quell- und Zielzeichenkette
  :return: Wert mit ersetzter Zeichenkette
  """
  if len(arg.split('|')) != 2:
    return value
  source, target = arg.split('|')
  return value.replace(source, target)


@register.filter
def user_has_model_permission(user, obj):
  """
  prüft, ob der übergebene Nutzer generell Rechte am Datenmodell des übergebenen Datenobjekts hat

  :param user: Nutzer
  :param obj: Datenobjekt
  :return: hat der übergebene Nutzer generell Rechte am Datenmodell des übergebenen Datenobjekts?
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
  prüft, ob der übergebene Nutzer Rechte zum Hinzufügen von Datenobjekten
  im übergebenen Datenmodell hat

  :param user: Nutzer
  :param model_name_lower: Name des Datenmodells
  :return: hat der übergebene Nutzer Rechte zum Hinzufügen von Datenobjekten
  im übergebenen Datenmodell?
  """
  if user.has_perm('datenmanagement.add_' + model_name_lower):
    return True
  else:
    return False


@register.filter
def user_has_model_change_permission(user, model_name_lower):
  """
  prüft, ob der übergebene Nutzer Rechte zum Ändern von Datenobjekten
  im übergebenen Datenmodell hat

  :param user: Nutzer
  :param model_name_lower: Name des Datenmodells
  :return: hat der übergebene Nutzer Rechte zum Ändern von Datenobjekten
  im übergebenen Datenmodell?
  """
  if user.has_perm('datenmanagement.change_' + model_name_lower):
    return True
  else:
    return False


@register.filter
def user_has_model_delete_permission(user, model_name_lower):
  """
  prüft, ob der übergebene Nutzer Rechte zum Löschen von Datenobjekten
  im übergebenen Datenmodell hat

  :param user: Nutzer
  :param model_name_lower: Name des Datenmodells
  :return: hat der übergebene Nutzer Rechte zum Löschen von Datenobjekten
  im übergebenen Datenmodell?
  """
  if user.has_perm('datenmanagement.delete_' + model_name_lower):
    return True
  else:
    return False


@register.filter
def user_has_model_view_permission(user, model_name_lower):
  """
  prüft, ob der übergebene Nutzer Rechte zum Ansehen von Datenobjekten
  im übergebenen Datenmodell hat

  :param user: Nutzer
  :param model_name_lower: Name des Datenmodells
  :return: hat der übergebene Nutzer Rechte zum Ansehen von Datenobjekten
  im übergebenen Datenmodell?
  """
  if user.has_perm('datenmanagement.view_' + model_name_lower):
    return True
  else:
    return False
