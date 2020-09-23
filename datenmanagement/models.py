import json
import os
import re
import requests
import uuid
from datenmanagement.storage import OverwriteStorage
from datetime import date, datetime
from decimal import *
from django import forms
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import options, signals
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator, RegexValidator, URLValidator
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text
from django_currentuser.middleware import get_current_authenticated_user
from guardian.shortcuts import assign_perm, remove_perm
from PIL import Image, ExifTags



#
# eigene Funktionen
#

def assign_permissions(sender, instance, created, **kwargs):
  model_name = instance.__class__.__name__.lower()
  user = getattr(instance, 'current_authenticated_user', None)
  if created:
    assign_perm('datenmanagement.change_' + model_name, user, instance)
    assign_perm('datenmanagement.delete_' + model_name, user, instance)
    if hasattr(instance.__class__._meta, 'admin_group') and Group.objects.filter(name = instance.__class__._meta.admin_group).exists():
      group = Group.objects.filter(name = instance.__class__._meta.admin_group)
      assign_perm('datenmanagement.change_' + model_name, group, instance)
      assign_perm('datenmanagement.delete_' + model_name, group, instance)
    else:
      for group in Group.objects.all():
        if group.permissions.filter(codename = 'change_' + model_name):
          assign_perm('datenmanagement.change_' + model_name, group, instance)
        if group.permissions.filter(codename = 'delete_' + model_name):
          assign_perm('datenmanagement.delete_' + model_name, group, instance)
  elif hasattr(instance.__class__._meta, 'group_with_users_for_choice_field') and Group.objects.filter(name = instance.__class__._meta.group_with_users_for_choice_field).exists():
    if user.groups.filter(name = instance.__class__._meta.group_with_users_for_choice_field).exists():
      mail = instance.ansprechpartner.split()[-1]
      mail = re.sub(r'\(', '', re.sub(r'\)', '', mail))
      if User.objects.filter(email__iexact = mail).exists():
        user = User.objects.get(email__iexact = mail)
        assign_perm('datenmanagement.change_' + model_name, user, instance)
        assign_perm('datenmanagement.delete_' + model_name, user, instance)


def current_year():
  return int(date.today().year)


def delete_pdf(sender, instance, **kwargs):
  if instance.pdf:
    instance.pdf.delete(False)


def delete_photo(sender, instance, **kwargs):
  if instance.foto:
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      if settings.MEDIA_ROOT and settings.MEDIA_URL:
        path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
      else:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = BASE_DIR + instance.foto.url
      thumb = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      try:
        os.remove(thumb)
      except OSError:
        pass
    instance.foto.delete(False)


def path_and_rename(path):
  def wrapper(instance, filename):
    if hasattr(instance, 'dateiname_original'):
      instance.dateiname_original = filename
    ext = filename.split('.')[-1]
    if hasattr(instance, 'uuid'):
      filename = '{0}.{1}'.format(str(instance.uuid), ext.lower())
    else:
      filename = '{0}.{1}'.format(str(uuid.uuid4()), ext.lower())
    return os.path.join(path, filename)
  return wrapper


def photo_post_processing(sender, instance, **kwargs):
  if instance.foto:
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
    else:
      BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      path = BASE_DIR + instance.foto.url
    rotate_image(path)
    # falls Foto(s) mit derselben UUID, aber unterschiedlichem Suffix, vorhanden: diese(s) löschen (und natürlich auch die entsprechenden Thumbnails)!
    filename = os.path.basename(path)
    ext = filename.split('.')[-1]
    filename_without_ext = os.path.splitext(filename)[0]
    for file in os.listdir(os.path.dirname(path)):
      if os.path.splitext(file)[0] == filename_without_ext and file.split('.')[-1] != ext:
        os.remove(os.path.dirname(path) + '/' + file)
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      thumb_path = os.path.dirname(path) + '/thumbs'
      if not os.path.exists(thumb_path):
        os.mkdir(thumb_path)
      thumb_path = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      thumb_image(path, thumb_path)
      filename = os.path.basename(thumb_path)
      ext = filename.split('.')[-1]
      filename_without_ext = os.path.splitext(filename)[0]
      for file in os.listdir(os.path.dirname(thumb_path)):
        if os.path.splitext(file)[0] == filename_without_ext and file.split('.')[-1] != ext:
          os.remove(os.path.dirname(thumb_path) + '/' + file)


def remove_permissions(sender, instance, **kwargs):
  model_name = instance.__class__.__name__.lower()
  user = getattr(instance, 'current_authenticated_user', None)
  for user in User.objects.all():
    remove_perm('datenmanagement.change_' + model_name, user, instance)
    remove_perm('datenmanagement.delete_' + model_name, user, instance)
  for group in Group.objects.all():
    remove_perm('datenmanagement.change_' + model_name, group, instance)
    remove_perm('datenmanagement.delete_' + model_name, group, instance)


def rotate_image(path):
  try:
    image = Image.open(path)
    for orientation in list(ExifTags.TAGS.keys()):
      if ExifTags.TAGS[orientation] == 'Orientation':
        break
    exif = dict(list(image._getexif().items()))
    if exif[orientation] == 3:
      image = image.rotate(180, expand=True)
    elif exif[orientation] == 6:
      image = image.rotate(270, expand=True)
    elif exif[orientation] == 8:
      image = image.rotate(90, expand=True)
    image.save(path)
    image.close()
  except (AttributeError, KeyError, IndexError):
    pass


def thumb_image(path, thumb_path):
  try:
    image = Image.open(path)
    image.thumbnail((70, 70), Image.ANTIALIAS)
    image.save(thumb_path, optimize=True, quality=20)
    image.close()
  except (AttributeError, KeyError, IndexError):
    pass



#
# eigene Felder
#

# Quelle :https://gist.github.com/danni/f55c4ce19598b2b345ef

class ChoiceArrayField(ArrayField):
  def formfield(self, **kwargs):
    defaults = {
      'form_class': forms.TypedMultipleChoiceField,
      'choices': self.base_field.choices,
    }
    defaults.update(kwargs)
    return super(ArrayField, self).formfield(**defaults)

  def to_python(self, value):
    res = super().to_python(value)
    if isinstance(res, list):
      value = [self.base_field.to_python(val) for val in res]
    else:
      value = None
    return value

  def validate(self, value, model_instance):
    if not self.editable:
      return
      
    if value is None or value in self.empty_values:
      return None

    if self.choices is not None and value not in self.empty_values:
      if set(value).issubset({option_key for option_key, _ in self.choices}):
        return
      raise exceptions.ValidationError(
        self.error_messages['invalid_choice'],
        code = 'invalid_choice',
        params = {
         'value': value
        },
      )

    if value is None and not self.null:
      raise exceptions.ValidationError(self.error_messages['null'], code='null')

    if not self.blank and value in self.empty_values:
      raise exceptions.ValidationError(self.error_messages['blank'], code='blank')


class NullTextField(models.TextField):
  def get_internal_type(self):
    return 'TextField'

  def to_python(self, value):
    if value is None or value in self.empty_values:
      return None
    elif isinstance(value, str):
      return value
    return str(value)

  def get_prep_value(self, value):
    value = super(NullTextField, self).get_prep_value(value)
    return self.to_python(value)

  def formfield(self, **kwargs):
    return super(NullTextField, self).formfield(**{
      'max_length': self.max_length,
      **({} if self.choices is not None else {'widget': forms.Textarea}),
      **kwargs,
    })


class PositiveIntegerRangeField(models.PositiveIntegerField):
  def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
    self.min_value, self.max_value = min_value, max_value
    models.PositiveIntegerField.__init__(self, verbose_name, name, **kwargs)
    
  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value, 'max_value': self.max_value}
    defaults.update(kwargs)
    return super(PositiveIntegerRangeField, self).formfield(**defaults)


class PositiveSmallIntegerMinField(models.PositiveSmallIntegerField):
  def __init__(self, verbose_name=None, name=None, min_value=None, **kwargs):
    self.min_value = min_value
    models.PositiveSmallIntegerField.__init__(self, verbose_name, name, **kwargs)
    
  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value}
    defaults.update(kwargs)
    return super(PositiveSmallIntegerMinField, self).formfield(**defaults)


class PositiveSmallIntegerRangeField(models.PositiveSmallIntegerField):
  def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
    self.min_value, self.max_value = min_value, max_value
    models.PositiveSmallIntegerField.__init__(self, verbose_name, name, **kwargs)
    
  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value, 'max_value': self.max_value}
    defaults.update(kwargs)
    return super(PositiveSmallIntegerRangeField, self).formfield(**defaults)



#
# eigene Meta-Attribute
#

options.DEFAULT_NAMES += (
  # LEGACY
  'list_fields_labels',
  
  'codelist',                               # optional ; Boolean        ; Handelt es sich um eine Codeliste, die dann für normale Benutzer in der Liste der verfügbaren Datenthemen nicht auftaucht (True)?
  'description',                            # Pflicht  ; Text           ; Beschreibung bzw. Langtitel des Datenthemas
  'choices_models_for_choices_fields',      # optional ; Textdictionary ; Namen der Felder (als Keys), denen Modelle (als Values) zugewiesen sind, die zur Befüllung entsprechender Auswahllisten herangezogen werden sollen
  'list_fields',                            # Pflicht  ; Textdictionary ; Namen der Felder (als Keys), die in genau dieser Reihenfolge in der Tabelle der Listenansicht als Spalten auftreten sollen, mit ihren Labels (als Values)
  'list_fields_with_number',                # optional ; Textliste      ; Liste mit den Namen der Felder aus list_fields, deren Werte von einem numerischen Datentyp sind
  'list_fields_with_date',                  # optional ; Textliste      ; Liste mit den Namen der Felder aus list_fields, deren Werte vom Datentyp Datum sind
  'list_fields_with_foreign_key',           # optional ; Textdictionary ; Namen der Felder (als Keys), die für die Tabelle der Listenansicht in Namen von Fremdschlüsselfeldern (als Values) umgewandelt werden sollen, damit sie in der jeweils referenzierten Tabelle auch gefunden werden
  'highlight_flag',                         # optional ; Text           ; Name des Boolean-Feldes, dessen Wert als Flag zum Highlighten entsprechender Zeilen herangezogen werden soll
  'readonly_fields',                        # optional ; Textliste      ; Namen der Felder, die in der Hinzufügen-/Änderungsansicht nur lesbar erscheinen sollen
  'object_title',                           # optional ; Text           ; Textbaustein für die Löschansicht (relevant nur bei Modellen mit Fremdschlüssel)
  'foreign_key_label',                      # optional ; Text           ; Titel des Feldes mit dem Fremdschlüssel (relevant nur bei Modellen mit Fremdschlüssel)
  'map_feature_tooltip_field',              # optional ; Text           ; Name des Feldes, dessen Werte in der Kartenansicht als Tooltip der Kartenobjekte angezeigt werden sollen
  'map_feature_tooltip_fields',             # optional ; Textliste      ; Namen der Felder, deren Werte in genau dieser Reihenfolge jeweils getrennt durch ein Leerzeichen zusammengefügt werden sollen, damit das Ergebnis in der Kartenansicht als Tooltip der Kartenobjekte angezeigt werden kann
  'map_rangefilter_fields',                 # optional ; Textdictionary ; Namen der Felder (als Keys), die in genau dieser Reihenfolge in der Kartenansicht als Intervallfilter auftreten sollen, mit ihren Titeln (als Values) – Achtung: Verarbeitung immer paarweise!
  'map_filter_fields',                      # optional ; Textdictionary ; Namen der Felder (als Keys), die in genau dieser Reihenfolge in der Kartenansicht als Filter auftreten sollen, mit ihren Titeln (als Values)
  'map_filter_fields_as_list',              # optional ; Textliste      ; Namen der Felder aus map_filter_fields, die als Listenfilter auftreten sollen
  'map_filter_boolean_fields_as_checkbox',  # optional ; Boolean        ; Sollen Boolean-Felder, die in der Kartenansicht als Filter auftreten sollen, als Checkboxen dargestellt werden (True)?
  'map_filter_hide_initial',                # optional ; Textdictionary ; Name des Feldes (als Key), dessen bestimmter Wert (als Value) dazu führen soll, Objekte initial nicht auf der Karte erscheinen, die in diesem Feld genau diesen bestimmten Wert aufweisen
  'address_type',                           # optional ; Text           ; Typ des Adressenbezugs: Adresse (Adresse) oder Straße (Straße)
  'address_mandatory',                      # optional ; Boolean        ; Soll die Adresse oder die Straße (je nach Typ des Adressenbezugs) eine Pflichtangabe sein (True)?
  'geometry_type',                          # optional ; Text           ; Geometrietyp
  'thumbs',                                 # optional ; Boolean        ; Sollen Thumbnails aus den hochgeladenen Fotos erzeugt werden (True)?
  'multi_foto_field',                       # optional ; Boolean        ; Sollen mehrere Fotos hochgeladen werden können (True)? Es werden dann automatisch mehrere Datensätze erstellt, und zwar jeweils einer pro Foto. Achtung: Es muss bei Verwendung dieser Option ein Pflichtfeld mit Namen foto existieren!
  'group_with_users_for_choice_field',      # optional ; Text           ; Name der Gruppe von Benutzern, die für das Feld Ansprechpartner/Bearbeiter in einer entsprechenden Auswahlliste genutzt werden sollen
  'admin_group'                             # optional ; Text           ; Name der Gruppe von Benutzern, die als Admin-Gruppe für dieses Datenthema gelten soll
)



#
# eigene Validatoren
#

# allgemein

akut_regex = r'^(?!.*´).*$'
akut_message = 'Der Text darf keine Akute (´) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.'
anfuehrungszeichen_regex = r'^(?!.*\").*$'
anfuehrungszeichen_message = 'Der Text darf keine doppelten Schreibmaschinensatz-Anführungszeichen (") enthalten. Stattdessen müssen die typographisch korrekten Anführungszeichen („“) verwendet werden.'
apostroph_regex = r'^(?!.*\').*$'
apostroph_message = 'Der Text darf keine einfachen Schreibmaschinensatz-Anführungszeichen (\') enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.'
bindestrich_leerzeichen_regex = r'^(?!.*- ).*$'
bindestrich_leerzeichen_message = 'Im Text darf nach einen Bindestrich kein Leerzeichen stehen.'
doppelleerzeichen_regex = r'^(?!.*  ).*$'
doppelleerzeichen_message = 'Der Text darf keine doppelten Leerzeichen enthalten.'
email_message = 'Die <strong><em>E-Mail-Adresse</em></strong> muss syntaktisch korrekt sein und daher folgendes Format aufweisen: abc-123.098_zyx@xyz-567.def.abc'
gravis_regex = r'^(?!.*`).*$'
gravis_message = 'Der Text darf keine Gravis (`) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.'
inventarnummer_regex = r'^[0-9]{8}$'
inventarnummer_message = 'Die <strong><em>Inventarnummer</em></strong> muss aus genau acht Ziffern bestehen.'
leerzeichen_bindestrich_regex = r'^(?!.* -).*$'
leerzeichen_bindestrich_message = 'Im Text darf vor einem Bindestrich kein Leerzeichen stehen.'
rufnummer_regex = r'^\+49 [1-9][0-9]{1,5} [0-9]{1,13}$'
rufnummer_message = 'Die Schreibweise von <strong><em>Rufnummern</em></strong> muss der Empfehlung E.123 der Internationalen Fernmeldeunion entsprechen und daher folgendes Format aufweisen: +49 381 3816256'
url_message = 'Die Adresse der <strong><em>Website</em></strong> muss syntaktisch korrekt sein und daher folgendes Format aufweisen: http[s]://abc-123.098_zyx.xyz-567/def/abc'


# speziell

denksteine_nummer_regex = r'^[0-9]+[a-z]*$'
denksteine_nummer_message = 'Die <strong><em>Nummer</em></strong> muss mit einer Ziffer beginnen und mit einer Ziffer oder einem Kleinbuchstaben enden.'
parkscheinautomaten_bewohnerparkgebiet_regex = r'^[A-Z][0-9]$'
parkscheinautomaten_bewohnerparkgebiet_message = 'Das <strong><em>Bewohnerparkgebiet</em></strong> muss aus genau einem Großbuchstaben sowie genau einer Ziffer bestehen.'
parkscheinautomaten_geraetenummer_regex = r'^[0-9]{2}_[0-9]{5}$'
parkscheinautomaten_geraetenummer_message = 'Die <strong><em>Gerätenummer</em></strong> muss aus genau zwei Ziffern, gefolgt von genau einem Unterstrich und abermals genau fünf Ziffern bestehen.'
uvp_vorhaben_registriernummer_bauamt_regex = r'^[0-9]{5}-[0-9]{2}$'
uvp_vorhaben_registriernummer_bauamt_message = 'Die <strong><em>Registriernummer des Bauamtes</em></strong> muss aus genau fünf Ziffern, gefolgt von genau einem Bindestrich und genau zwei Ziffern bestehen.'
zonen_parkscheinautomaten_zone_regex = r'^[A-Z]$'
zonen_parkscheinautomaten_zone_message = 'Die <strong><em>Zone</em></strong> muss aus genau einem Großbuchstaben bestehen.'


hafas_id_regex = r'^[0-9]{8}$'
hafas_id_message = 'Die <strong><em>HAFAS-ID</em></strong> muss aus genau acht Ziffern bestehen.'
id_containerstellplatz_regex = r'^[0-9]{2}-[0-9]{2}$'
id_containerstellplatz_message = 'Die <strong><em>ID</em></strong> muss aus genau zwei Ziffern, gefolgt von genau einem Bindestrich und abermals genau zwei Ziffern bestehen.'

















#
# LEGACY
#

ART_FLIESSGEWAESSER = (
  ('Durchlass', 'Durchlass'),
  ('offen', 'offen'),
  ('Rohrleitung', 'Rohrleitung'),
)

AUSFUEHRUNG_HALTESTELLEN = (
  ('Noppen', 'Noppen'),
  ('Rillenplatten', 'Rillenplatten'),
  ('Rippenplatten', 'Rippenplatten'),
)

BEFESTIGUNGSART_AUFSTELLFLAECHE_BUS_HALTESTELLEN = (
  ('Asphalt', 'Asphalt'),
  ('Beton', 'Beton'),
  ('Betonverbundpflaster', 'Betonverbundpflaster'),
  ('Großpflaster', 'Großpflaster'),
  ('halbstarre Decke', 'halbstarre Decke'),
  ('Natursteingroßpflaster', 'Natursteingroßpflaster'),
  ('sonstige', 'sonstige'),
)

BEFESTIGUNGSART_WARTEFLAECHE_HALTESTELLEN = (
  ('Asphalt', 'Asphalt'),
  ('Beton', 'Beton'),
  ('Betonpflaster', 'Betonpflaster'),
  ('Betonplatten', 'Betonplatten'),
  ('sonstige', 'sonstige'),
)

BEWIRTSCHAFTER_ALTKLEIDER_CONTAINERSTELLPLAETZE = (
  (3, 'Deutsches Rotes Kreuz Kreisverband Rostock e.V.'),
  (2, 'EAST-WEST Textilrecycling Kursun GmbH'),
  (8, 'FWS GmbH'),
  (5, 'Güstrower Werkstätten GmbH'),
  (9, 'HUMANA Kleidersammlung GmbH'),
  (4, 'Retextil Recycling International GmbH & Co. KG'),
  (6, 'Sibitex International'),
  (7, 'Textil-Recycling K. & A. Wenkhaus GmbH'),
  (1, 'Veolia Umweltservice Nord GmbH'),
  (10, 'VerSeRo GmbH'),
  (11, 'SOEX Collecting Germany GmbH'),
  (12, 'Malteser Hilfsdienst gGmbH und e.V.'),
)

BEWIRTSCHAFTER_GLAS_CONTAINERSTELLPLAETZE = (
  (1, 'Veolia Umweltservice Nord GmbH'),
)

BEWIRTSCHAFTER_GRUNDUNDBODEN_CONTAINERSTELLPLAETZE = (
  (62, 'Kataster-, Vermessungs- und Liegenschaftsamt'),
  (67, 'Amt für Stadtgrün, Naturschutz und Landschaftspflege'),
  (73, 'Amt für Umwelt- und Klimaschutz'),
  (66, 'Tiefbauamt'),
)

BEWIRTSCHAFTER_PAPIER_CONTAINERSTELLPLAETZE = (
  (1, 'Veolia Umweltservice Nord GmbH'),
)

DFI_TYPEN_HALTESTELLEN = (
  ('4-zeilig', '4-zeilig'),
  ('8-zeilig', '8-zeilig'),
)

FAHRGASTUNTERSTANDSTYPEN_HALTESTELLEN = (
  ('Beton-WH', 'Beton-WH'),
  ('Foster', 'Foster'),
  ('MURANO', 'MURANO'),
  ('Orion-Anlage', 'Orion-Anlage'),
  ('Trafic', 'Trafic'),
)

FAHRPLANVITRINENTYPEN_HALTESTELLEN = (
  ('Infovitrine 2xA3', 'Infovitrine 2xA3'),
  ('Infovitrine 3xA3', 'Infovitrine 3xA3'),
)

LINIEN_HALTESTELLEN = (
  ('1', '1'),
  ('2', '2'),
  ('3', '3'),
  ('4', '4'),
  ('5', '5'),
  ('6', '6'),
  ('16', '16'),
  ('17', '17'),
  ('18', '18'),
  ('19', '19'),
  ('22', '22'),
  ('23', '23'),
  ('25', '25'),
  ('26', '26'),
  ('27', '27'),
  ('28', '28'),
  ('30', '30'),
  ('30A', '30A'),
  ('31', '31'),
  ('34', '34'),
  ('35', '35'),
  ('36', '36'),
  ('37', '37'),
  ('38', '38'),
  ('39', '39'),
  ('45', '45'),
  ('45A', '45A'),
  ('49', '49'),
  ('102', '102'),
  ('106', '106'),
  ('112', '112'),
  ('113', '113'),
  ('118', '118'),
  ('119', '119'),
  ('120', '120'),
  ('121', '121'),
  ('122', '122'),
  ('123', '123'),
  ('127', '127'),
  ('128', '128'),
  ('129', '129'),
  ('137', '137'),
  ('140', '140'),
  ('284', '284'),
  ('304', '304'),
  ('F1', 'F1'),
  ('F1A', 'F1A'),
  ('F2', 'F2'),
  ('X41', 'X41'),
)

MASTTYPEN_HALTESTELLEN = (
  ('2H+7', '2H+7'),
  ('2H+8', '2H+8'),
  ('HB+2', 'HB+2'),
  ('HB+3', 'HB+3'),
  ('HB+4', 'HB+4'),
  ('HB+5', 'HB+5'),
  ('HB+6', 'HB+6'),
)

MOTIVE_HALTESTELLEN = (
  ('Mast', 'Mast'),
  ('Wartebereich von Stirnseite', 'Wartebereich von Stirnseite'),
  ('Wartebereich von vorne', 'Wartebereich von vorne'),
)

SCHAEDEN_HALTESTELLEN = (
  ('keine Schäden', 'keine Schäden'),
  ('leichte Schäden', 'leichte Schäden'),
  ('mittelschwere Schäden', 'mittelschwere Schäden'),
  ('schwere Schäden', 'schwere Schäden'),
)

SITZBANKTYPEN_HALTESTELLEN = (
  ('Holzlattung auf Waschbetonfüßen', 'Holzlattung auf Waschbetonfüßen'),
  ('Sitzbank mit Armlehne', 'Sitzbank mit Armlehne'),
  ('Sitzbank ohne Armlehne', 'Sitzbank ohne Armlehne'),
)

TYP_HALTESTELLEN = (
  ('Bushaltestelle (am Fahrbahnrand)', 'Bushaltestelle (am Fahrbahnrand)'),
  ('Bushaltestelle (Busbucht)', 'Bushaltestelle (Busbucht)'),
  ('Bushaltestelle (Buskap)', 'Bushaltestelle (Buskap)'),
  ('Doppelhaltestelle', 'Doppelhaltestelle'),
  ('Kombihaltestelle', 'Kombihaltestelle'),
  ('Straßenbahnhaltestelle', 'Straßenbahnhaltestelle'),
)

VERKEHRSMITTELKLASSEN_HALTESTELLEN = (
  ('alternative Bedienform', 'alternative Bedienform'),
  ('Autofähre', 'Autofähre'),
  ('Personenfähre', 'Personenfähre'),
  ('Regionalbus', 'Regionalbus'),
  ('Schienenersatzverkehr', 'Schienenersatzverkehr'),
  ('Stadtbus', 'Stadtbus'),
  ('Straßenbahn', 'Straßenbahn'),
)

ZH_TYPEN_HALTESTELLEN = (
  ('Haltestellenverteiler', 'Haltestellenverteiler'),
  ('Kabelverteilerschrank', 'Kabelverteilerschrank'),
  ('Zähleranschlusssäule', 'Zähleranschlusssäule'),
)















#
# Codelisten als abstrakte Modelle
#

class Art(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  art = models.CharField('Art', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
     'art': 'Art'
    }
    ordering = ['art'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.art


class Material(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  material = models.CharField('Material', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
     'material': 'Material'
    }
    ordering = ['material'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.material


class Schlagwort(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  schlagwort = models.CharField('Schlagwort', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
     'schlagwort': 'Schlagwort'
    }
    ordering = ['schlagwort'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.schlagwort



#
# Adressen
#

class Adressen(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  adresse = models.CharField('Adresse', max_length=255, editable=False)

  class Meta:
    managed = False
    codelist = True
    db_table = 'basisdaten\".\"adressenliste_datenerfassung'
    verbose_name = 'Adresse'
    verbose_name_plural = 'Adressen'
    description = 'Adressen in Mecklenburg-Vorpommern'
    list_fields = {
     'adresse': 'Adresse'
    }
    ordering = ['adresse'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.adresse



#
# Straßen
#

class Strassen(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  strasse = models.CharField('Straße', max_length=255, editable=False)

  class Meta:
    managed = False
    codelist = True
    db_table = 'basisdaten\".\"strassenliste_datenerfassung'
    verbose_name = 'Straße'
    verbose_name_plural = 'Straßen'
    description = 'Straßen in Mecklenburg-Vorpommern'
    list_fields = {
     'strasse': 'Straße'
    }
    ordering = ['strasse'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.strasse



#
# Codelisten
#

# Arten von Baudenkmalen

class Arten_Baudenkmale(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_baudenkmale'
    verbose_name = 'Art eines Baudenkmals'
    verbose_name_plural = 'Arten von Baudenkmalen'
    description = 'Arten von Baudenkmalen'


# Arten von Fair-Trade-Einrichtungen

class Arten_FairTrade(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fairtrade'
    verbose_name = 'Art einer Fair-Trade-Einrichtung'
    verbose_name_plural = 'Arten von Fair-Trade-Einrichtungen'
    description = 'Arten von Fair-Trade-Einrichtungen'


# Arten von Feuerwachen

class Arten_Feuerwachen(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_feuerwachen'
    verbose_name = 'Art einer Feuerwache'
    verbose_name_plural = 'Arten von Feuerwachen'
    description = 'Arten von Feuerwachen'


# Arten von Hundetoiletten

class Arten_Hundetoiletten(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_hundetoiletten'
    verbose_name = 'Art einer Hundetoilette'
    verbose_name_plural = 'Arten von Hundetoiletten'
    description = 'Arten von Hundetoiletten'


# Arten von Meldediensten (flächenhaft)

class Arten_Meldedienst_flaechenhaft(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_meldedienst_flaechenhaft'
    verbose_name = 'Art eines Meldedienstes (flächenhaft)'
    verbose_name_plural = 'Arten von Meldediensten (flächenhaft)'
    description = 'Arten von Meldediensten (flächenhaft)'


# Arten von Meldediensten (punkthaft)

class Arten_Meldedienst_punkthaft(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_meldedienst_punkthaft'
    verbose_name = 'Art eines Meldedienstes (punkthaft)'
    verbose_name_plural = 'Arten von Meldediensten (punkthaft)'
    description = 'Arten von Meldediensten (punkthaft)'


# Arten von Parkmöglichkeiten

class Arten_Parkmoeglichkeiten(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_parkmoeglichkeiten'
    verbose_name = 'Art einer Parkmöglichkeit'
    verbose_name_plural = 'Arten von Parkmöglichkeiten'
    description = 'Arten von Parkmöglichkeiten'


# Arten von Pflegeeinrichtungen

class Arten_Pflegeeinrichtungen(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_pflegeeinrichtungen'
    verbose_name = 'Art einer Pflegeeinrichtung'
    verbose_name_plural = 'Arten von Pflegeeinrichtungen'
    description = 'Arten von Pflegeeinrichtungen'


# Arten von UVP-Vorprüfungen

class Arten_UVP_Vorpruefungen(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_uvp_vorpruefungen'
    verbose_name = 'Art einer UVP-Vorprüfung'
    verbose_name_plural = 'Arten von UVP-Vorprüfungen'
    description = 'Arten von UVP-Vorprüfungen'


# Carsharing-Anbieter

class Anbieter_Carsharing(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  anbieter = models.CharField('Anbieter', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"anbieter_carsharing'
    verbose_name = 'Carsharing-Anbieter'
    verbose_name_plural = 'Carsharing-Anbieter'
    description = 'Carsharing-Anbieter'
    list_fields = {
      'anbieter': 'Anbieter'
    }
    ordering = ['anbieter'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.anbieter


# Angebote bei Mobilpunkten

class Angebote_Mobilpunkte(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  angebot = models.CharField('Angebot', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"angebote_mobilpunkte'
    verbose_name = 'Angebot bei einem Mobilpunkt'
    verbose_name_plural = 'Angebote bei Mobilpunkten'
    description = 'Angebote bei Mobilpunkten'
    list_fields = {
      'angebot': 'Angebot'
    }
    ordering = ['angebot'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.angebot


# Auftraggeber von Baustellen

class Auftraggeber_Baustellen(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  auftraggeber = models.CharField('Auftraggeber', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"auftraggeber_baustellen'
    verbose_name = 'Auftraggeber einer Baustelle'
    verbose_name_plural = 'Auftraggeber von Baustellen'
    description = 'Auftraggeber von Baustellen'
    list_fields = {
      'auftraggeber': 'Auftraggeber'
    }
    ordering = ['auftraggeber'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.auftraggeber


# Betriebsarten

class Betriebsarten(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  betriebsart = models.CharField('Betriebsart', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"betriebsarten'
    verbose_name = 'Betriebsart'
    verbose_name_plural = 'Betriebsarten'
    description = 'Betriebsarten'
    list_fields = {
      'betriebsart': 'Betriebsart'
    }
    ordering = ['betriebsart'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.betriebsart


# Bewirtschafter, Betreiber, Träger, Eigentümer etc.

class Bewirtschafter_Betreiber_Traeger_Eigentuemer(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art = models.CharField('Art', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"bewirtschafter_betreiber_traeger_eigentuemer'
    verbose_name = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    verbose_name_plural = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    description = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'art': 'Art'
    }
    ordering = ['bezeichnung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.bezeichnung


# E-Anschlüsse für Parkscheinautomaten

class E_Anschluesse_Parkscheinautomaten(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  e_anschluss = models.CharField('E-Anschluss', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"e_anschluesse_parkscheinautomaten'
    verbose_name = 'E-Anschluss für einen Parkscheinautomaten'
    verbose_name_plural = 'E-Anschlüsse für Parkscheinautomaten'
    description = 'E-Anschlüsse für Parkscheinautomaten'
    list_fields = {
      'e_anschluss': 'E-Anschluss'
    }
    ordering = ['e_anschluss'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.e_anschluss


# Ergebnisse von UVP-Vorprüfungen

class Ergebnisse_UVP_Vorpruefungen(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  ergebnis = models.CharField('Ergebnis', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"ergebnisse_uvp_vorpruefungen'
    verbose_name = 'Ergebnis einer UVP-Vorprüfung'
    verbose_name_plural = 'Ergebnisse von UVP-Vorprüfungen'
    description = 'Ergebnisse von UVP-Vorprüfungen'
    list_fields = {
      'ergebnis': 'Ergebnis'
    }
    ordering = ['ergebnis'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.ergebnis


# Genehmigungsbehörden von UVP-Vorhaben

class Genehmigungsbehoerden_UVP_Vorhaben(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  genehmigungsbehoerde = models.CharField('Genehmigungsbehörde', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"genehmigungsbehoerden_uvp_vorhaben'
    verbose_name = 'Genehmigungsbehörde eines UVP-Vorhabens'
    verbose_name_plural = 'Genehmigungsbehörden von UVP-Vorhaben'
    description = 'Genehmigungsbehörden von UVP-Vorhaben'
    list_fields = {
      'genehmigungsbehoerde': 'Genehmigungsbehörde'
    }
    ordering = ['genehmigungsbehoerde'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.genehmigungsbehoerde


# Ladekarten für Ladestationen für Elektrofahrzeuge

class Ladekarten_Ladestationen_Elektrofahrzeuge(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  ladekarte = models.CharField('Ladekarte', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"ladekarten_ladestationen_elektrofahrzeuge'
    verbose_name = 'Ladekartenfür eine Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Ladekarten für Ladestationen für Elektrofahrzeuge'
    description = 'Ladekarten für Ladestationen für Elektrofahrzeuge'
    list_fields = {
      'ladekarte': 'Ladekarte'
    }
    ordering = ['ladekarte'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.ladekarte


# Materialien von Denksteinen

class Materialien_Denksteine(Material):
  class Meta(Material.Meta):
    db_table = 'codelisten\".\"materialien_denksteine'
    verbose_name = 'Material eines Denksteins'
    verbose_name_plural = 'Materialien von Denksteinen'
    description = 'Materialien von Denksteinen'


# Personentitel

class Personentitel(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"personentitel'
    verbose_name = 'Personentitel'
    verbose_name_plural = 'Personentitel'
    description = 'Personentitel'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }
    ordering = ['bezeichnung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.bezeichnung


# Rechtsgrundlagen von UVP-Vorhaben

class Rechtsgrundlagen_UVP_Vorhaben(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  rechtsgrundlage = models.CharField('Rechtsgrundlage', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"rechtsgrundlagen_uvp_vorhaben'
    verbose_name = 'Rechtsgrundlage eines UVP-Vorhabens'
    verbose_name_plural = 'Rechtsgrundlagen von UVP-Vorhaben'
    description = 'Rechtsgrundlagen von UVP-Vorhaben'
    list_fields = {
      'rechtsgrundlage': 'Rechtsgrundlage'
    }
    ordering = ['rechtsgrundlage'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.rechtsgrundlage


# Schlagwörter für Bildungsträger

class Schlagwoerter_Bildungstraeger(Schlagwort):
  class Meta(Schlagwort.Meta):
    db_table = 'codelisten\".\"schlagwoerter_bildungstraeger'
    verbose_name = 'Schlagwort für einen Bildungsträger'
    verbose_name_plural = 'Schlagwörter für Bildungsträger'
    description = 'Schlagwörter für Bildungsträger'


# Schlagwörter für Vereine

class Schlagwoerter_Vereine(Schlagwort):
  class Meta(Schlagwort.Meta):
    db_table = 'codelisten\".\"schlagwoerter_vereine'
    verbose_name = 'Schlagwort für einen Verein'
    verbose_name_plural = 'Schlagwörter für Vereine'
    description = 'Schlagwörter für Vereine'


# Sparten von Baustellen

class Sparten_Baustellen(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  sparte = models.CharField('Sparte', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"sparten_baustellen'
    verbose_name = 'Sparte einer Baustelle'
    verbose_name_plural = 'Sparten von Baustellen'
    description = 'Sparten von Baustellen'
    list_fields = {
      'sparte': 'Sparte'
    }
    ordering = ['sparte'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.sparte


# Status von Baustellen

class Status_Baustellen_geplant(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  status = models.CharField('Status', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"status_baustellen_geplant'
    verbose_name = 'Status einer Baustelle (geplant)'
    verbose_name_plural = 'Status von Baustellen (geplant)'
    description = 'Status von Baustellen (geplant)'
    list_fields = {
      'status': 'Status'
    }
    ordering = ['status'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.status


# Status von Fotos der Baustellen-Fotodokumentation

class Status_Baustellen_Fotodokumentation_Fotos(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  status = models.CharField('Status', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"status_baustellen_fotodokumentation_fotos'
    verbose_name = 'Status eines Fotos der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Status von Fotos der Baustellen-Fotodokumentation'
    description = 'Status von Fotos der Baustellen-Fotodokumentation'
    list_fields = {
      'status': 'Status'
    }
    ordering = ['status'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.status


# Typen von Abfallbehältern

class Typen_Abfallbehaelter(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  typ = models.CharField('Typ', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"typen_abfallbehaelter'
    verbose_name = 'Typ eines Abfallbehälters'
    verbose_name_plural = 'Typen von Abfallbehältern'
    description = 'Typen von Abfallbehältern'
    list_fields = {
      'typ': 'Typ'
    }
    ordering = ['typ'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.typ


# Typen von UVP-Vorhaben

class Typen_UVP_Vorhaben(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  typ = models.CharField('Typ', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"typen_uvp_vorhaben'
    verbose_name = 'Typ eines UVP-Vorhabens'
    verbose_name_plural = 'Typen von UVP-Vorhaben'
    description = 'Typen von UVP-Vorhaben'
    list_fields = {
      'typ': 'Typ'
    }
    ordering = ['typ'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.typ


# Verbünde von Ladestationen für Elektrofahrzeuge

class Verbuende_Ladestationen_Elektrofahrzeuge(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  verbund = models.CharField('Verbund', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"verbuende_ladestationen_elektrofahrzeuge'
    verbose_name = 'Verbund einer Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Verbünde von Ladestationen für Elektrofahrzeuge'
    description = 'Verbünde von Ladestationen für Elektrofahrzeuge'
    list_fields = {
      'verbund': 'Verbund'
    }
    ordering = ['verbund'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.verbund


# Verkehrliche Lagen von Baustellen

class Verkehrliche_Lagen_Baustellen(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  verkehrliche_lage = models.CharField(' verkehrliche Lage', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"verkehrliche_lagen_baustellen'
    verbose_name = 'Verkehrliche Lage einer Baustelle'
    verbose_name_plural = 'Verkehrliche Lagen von Baustellen'
    description = 'Verkehrliche Lagen von Baustellen'
    list_fields = {
      'verkehrliche_lage': 'verkehrliche Lage'
    }
    ordering = ['verkehrliche_lage'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.verkehrliche_lage


# Vorgangsarten von UVP-Vorhaben

class Vorgangsarten_UVP_Vorhaben(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  vorgangsart = models.CharField('Vorgangsart', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"vorgangsarten_uvp_vorhaben'
    verbose_name = 'Vorgangsart eines UVP-Vorhabens'
    verbose_name_plural = 'Vorgangsarten von UVP-Vorhaben'
    description = 'Vorgangsarten von UVP-Vorhaben'
    list_fields = {
      'vorgangsart': 'Vorgangsart'
    }
    ordering = ['vorgangsart'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.vorgangsart


# Zeiteinheiten

class Zeiteinheiten(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  zeiteinheit = models.CharField('Zeiteinheit', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  erlaeuterung = models.CharField('Erläuterung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"zeiteinheiten'
    verbose_name = 'Zeiteinheit'
    verbose_name_plural = 'Zeiteinheiten'
    description = 'Zeiteinheiten'
    list_fields = {
      'zeiteinheit': 'Zeiteinheit',
      'erlaeuterung': 'Erläuterung'
    }
    ordering = ['erlaeuterung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.erlaeuterung


# Zonen für Parkscheinautomaten

class Zonen_Parkscheinautomaten(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  zone = models.CharField('Zone', max_length=1, validators=[RegexValidator(regex=zonen_parkscheinautomaten_zone_regex, message=zonen_parkscheinautomaten_zone_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"zonen_parkscheinautomaten'
    verbose_name = 'Zone für einen Parkscheinautomaten'
    verbose_name_plural = 'Zonen für Parkscheinautomaten'
    description = 'Zonen für Parkscheinautomaten'
    list_fields = {
      'zone': 'Zone'
    }
    ordering = ['zone'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.zone



#
# Datenthemen
#

# Abfallbehälter

class Abfallbehaelter(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField('Außerbetriebstellung', blank=True, null=True)
  id = models.CharField('ID', max_length=8, default='00000000')
  typ = models.ForeignKey(Typen_Abfallbehaelter, verbose_name='Typ', on_delete=models.SET_NULL, db_column='typ', to_field='uuid', related_name='typen+', blank=True, null=True)
  aufstellungsjahr = PositiveSmallIntegerRangeField('Aufstellungsjahr', max_value=current_year(), blank=True, null=True)
  eigentuemer = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Eigentümer', on_delete=models.RESTRICT, db_column='eigentuemer', to_field='uuid', related_name='eigentuemer+')
  bewirtschafter = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Bewirtschafter', on_delete=models.RESTRICT, db_column='bewirtschafter', to_field='uuid', related_name='bewirtschafter+')
  pflegeobjekt = models.CharField('Pflegeobjekt', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  inventarnummer = models.CharField('Inventarnummer', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  anschaffungswert = models.DecimalField('Anschaffungswert (in €)', max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9999.99'), 'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 9.999,99 € betragen.')], blank=True, null=True)
  haltestelle = models.BooleanField('Lage an einer Haltestelle', blank=True, null=True)
  sommer_mo = PositiveSmallIntegerRangeField('Anzahl Leerungen montags im Sommer', min_value=1, blank=True, null=True)
  sommer_di = PositiveSmallIntegerRangeField('Anzahl Leerungen dienstags im Sommer', min_value=1, blank=True, null=True)
  sommer_mi = PositiveSmallIntegerRangeField('Anzahl Leerungen mittwochs im Sommer', min_value=1, blank=True, null=True)
  sommer_do = PositiveSmallIntegerRangeField('Anzahl Leerungen donnerstags im Sommer', min_value=1, blank=True, null=True)
  sommer_fr = PositiveSmallIntegerRangeField('Anzahl Leerungen freitags im Sommer', min_value=1, blank=True, null=True)
  sommer_sa = PositiveSmallIntegerRangeField('Anzahl Leerungen samstags im Sommer', min_value=1, blank=True, null=True)
  sommer_so = PositiveSmallIntegerRangeField('Anzahl Leerungen sonntags im Sommer', min_value=1, blank=True, null=True)
  winter_mo = PositiveSmallIntegerRangeField('Anzahl Leerungen montags im Winter', min_value=1, blank=True, null=True)
  winter_di = PositiveSmallIntegerRangeField('Anzahl Leerungen dienstags im Winter', min_value=1, blank=True, null=True)
  winter_mi = PositiveSmallIntegerRangeField('Anzahl Leerungen mittwochs im Winter', min_value=1, blank=True, null=True)
  winter_do = PositiveSmallIntegerRangeField('Anzahl Leerungen donnerstags im Winter', min_value=1, blank=True, null=True)
  winter_fr = PositiveSmallIntegerRangeField('Anzahl Leerungen freitags im Winter', min_value=1, blank=True, null=True)
  winter_sa = PositiveSmallIntegerRangeField('Anzahl Leerungen samstags im Winter', min_value=1, blank=True, null=True)
  winter_so = PositiveSmallIntegerRangeField('Anzahl Leerungen sonntags im Winter', min_value=1, blank=True, null=True)
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"abfallbehaelter_hro'
    verbose_name = 'Abfallbehälter'
    verbose_name_plural = 'Abfallbehälter'
    description = 'Abfallbehälter in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Außerbetriebstellung',
      'id': 'ID',
      'typ': 'Typ',
      'eigentuemer': 'Eigentümer',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt'
    }
    list_fields_with_date = ['deaktiviert']
    list_fields_with_number = ['id']
    list_fields_with_foreign_key = {
      'typ': 'typ__typ',
      'eigentuemer': 'eigentuemer__bezeichnung',
      'bewirtschafter': 'bewirtschafter__bezeichnung'
    }
    readonly_fields = ['deaktiviert', 'id']
    map_feature_tooltip_field = 'id'
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'typ': 'Typ',
      'eigentuemer': 'Eigentümer',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt'
    }
    map_filter_fields_as_list = ['typ', 'eigentuemer', 'bewirtschafter']
    geometry_type = 'Point'
  
  def __str__(self):
    return self.id + (' [Typ: ' + str(self.typ) + ']' if self.typ else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Abfallbehaelter, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Abfallbehaelter, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Abfallbehaelter)

signals.post_delete.connect(remove_permissions, sender=Abfallbehaelter)


# Aufteilungspläne nach Wohnungseigentumsgesetz

class Aufteilungsplaene_Wohnungseigentumsgesetz(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  aktenzeichen = models.CharField('Aktenzeichen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum_abgeschlossenheitserklaerung = models.DateField('Datum der Abgeschlossenheitserklärung', blank=True, null=True)
  bearbeiter = models.CharField('Bearbeiter', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  pdf = models.FileField('PDF', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PDF_PATH_PREFIX_PRIVATE + 'aufteilungsplaene_wohnungseigentumsgesetz'), max_length=255)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"aufteilungsplaene_wohnungseigentumsgesetz_hro'
    verbose_name = 'Aufteilungsplan nach Wohnungseigentumsgesetz'
    verbose_name_plural = 'Aufteilungspläne nach Wohnungseigentumsgesetz'
    description = 'Aufteilungspläne nach Wohnungseigentumsgesetz in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'aktenzeichen': 'Aktenzeichen',
      'datum_abgeschlossenheitserklaerung': 'Datum der Abgeschlossenheitserklärung',
      'datum': 'Datum'
    }
    list_fields_with_date = ['datum_abgeschlossenheitserklaerung', 'datum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse'
    }
    map_feature_tooltip_field = 'datum'
    map_filter_fields = {
      'aktenzeichen': 'Aktenzeichen',
      'datum_abgeschlossenheitserklaerung': 'Datum der Abgeschlossenheitserklärung',
      'datum': 'Datum'
    }
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'

  def __str__(self):
    return 'Abgeschlossenheitserklärung mit Datum ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Aufteilungsplaene_Wohnungseigentumsgesetz, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Aufteilungsplaene_Wohnungseigentumsgesetz, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Aufteilungsplaene_Wohnungseigentumsgesetz)

signals.post_delete.connect(delete_pdf, sender=Aufteilungsplaene_Wohnungseigentumsgesetz)

signals.post_delete.connect(remove_permissions, sender=Aufteilungsplaene_Wohnungseigentumsgesetz)


# Baudenkmale

class Baudenkmale(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  art = models.ForeignKey(Arten_Baudenkmale, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  bezeichnung = models.CharField('Bezeichnung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  beschreibung = models.CharField('Beschreibung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.MultiPolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"baudenkmale_hro'
    verbose_name = 'Baudenkmal'
    verbose_name_plural = 'Baudenkmale'
    description = 'Baudenkmale der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'art': 'art__art'
    }
    map_feature_tooltip_field = 'beschreibung'
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung'
    }
    map_filter_fields_as_list = ['art']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'MultiPolygon'

  def __str__(self):
    return self.beschreibung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Baudenkmale, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Baudenkmale, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Baudenkmale)

signals.post_delete.connect(remove_permissions, sender=Baudenkmale)


# Baustellen der Baustellen-Fotodokumentation

class Baustellen_Fotodokumentation_Baustellen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  strasse = models.ForeignKey(Strassen, verbose_name='Straße', on_delete=models.SET_NULL, db_column='strasse', to_field='uuid', related_name='strassen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  verkehrliche_lagen = ChoiceArrayField(models.CharField(' verkehrliche Lage(n)', max_length=255, choices=()), verbose_name=' verkehrliche Lage(n)')
  sparten = ChoiceArrayField(models.CharField('Sparte(n)', max_length=255, choices=()), verbose_name='Sparte(n)')
  auftraggeber = models.ForeignKey(Auftraggeber_Baustellen, verbose_name='Auftraggeber', on_delete=models.RESTRICT, db_column='auftraggeber', to_field='uuid', related_name='auftraggeber+')
  ansprechpartner = models.CharField('Ansprechpartner', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_strassenbezug\".\"baustellen_fotodokumentation_baustellen_hro'
    verbose_name = 'Baustelle der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Baustellen der Baustellen-Fotodokumentation'
    description = 'Baustellen der Baustellen-Fotodokumentation in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'verkehrliche_lagen': 'Verkehrliche_Lagen_Baustellen',
      'sparten': 'Sparten_Baustellen'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'strasse': 'Straße',
      'bezeichnung': 'Bezeichnung',
      'verkehrliche_lagen': 'verkehrliche Lage(n)',
      'sparten': 'Sparte(n)',
      'auftraggeber': 'Auftraggeber',
      'ansprechpartner': 'Ansprechpartner',
      'bemerkungen': 'Bemerkungen'
    }
    list_fields_with_foreign_key = {
      'strasse': 'strasse__strasse',
      'auftraggeber': 'auftraggeber__auftraggeber'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'sparten': 'Sparte(n)',
      'auftraggeber': 'Auftraggeber'
    }
    map_filter_fields_as_list = ['auftraggeber']
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'Point'
    ordering = ['bezeichnung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.bezeichnung + (' [Straße: ' + str(self.strasse) + ']' if self.strasse else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Baustellen_Fotodokumentation_Baustellen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Baustellen_Fotodokumentation_Baustellen, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Baustellen_Fotodokumentation_Baustellen)

signals.post_delete.connect(remove_permissions, sender=Baustellen_Fotodokumentation_Baustellen)


# Fotos der Baustellen-Fotodokumentation

class Baustellen_Fotodokumentation_Fotos(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  baustellen_fotodokumentation_baustelle = models.ForeignKey(Baustellen_Fotodokumentation_Baustellen, verbose_name='Baustelle', on_delete=models.CASCADE, db_column='baustellen_fotodokumentation_baustelle', to_field='uuid', related_name='baustellen_fotodokumentation_baustellen+')
  status = models.ForeignKey(Status_Baustellen_Fotodokumentation_Fotos, verbose_name='Status', on_delete=models.RESTRICT, db_column='status', to_field='uuid', related_name='status+')
  aufnahmedatum = models.DateField('Aufnahmedatum', default=date.today)
  dateiname_original = models.CharField('Original-Dateiname', max_length=255, default='ohne')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'baustellen_fotodokumentation'), max_length=255)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"baustellen_fotodokumentation_fotos_hro'
    verbose_name = 'Foto der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Fotos der Baustellen-Fotodokumentation'
    description = 'Fotos der Baustellen-Fotodokumentation in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'verkehrliche_lagen': 'Verkehrliche_Lagen_Baustellen',
      'sparten': 'Sparten_Baustellen'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'baustellen_fotodokumentation_baustelle': 'Baustelle',
      'status': 'Status',
      'aufnahmedatum': 'Aufnahmedatum',
      'dateiname_original': 'Original-Dateiname',
      'foto': 'Foto'
    }
    readonly_fields = ['dateiname_original']
    list_fields_with_date = ['aufnahmedatum']
    list_fields_with_foreign_key = {
      'baustellen_fotodokumentation_baustelle': 'baustellen_fotodokumentation_baustelle__bezeichnung',
      'status': 'status__status'
    }
    object_title = 'das Foto'
    foreign_key_label = 'Baustelle'
    thumbs = True
    multi_foto_field = True
  
  def __str__(self):
    return str(self.baustellen_fotodokumentation_baustelle) + ' mit Status ' + str(self.status) + ' und Aufnahmedatum ' + datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Baustellen_Fotodokumentation_Fotos, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Baustellen_Fotodokumentation_Fotos, self).delete(*args, **kwargs)

signals.post_save.connect(photo_post_processing, sender=Baustellen_Fotodokumentation_Fotos)

signals.post_save.connect(assign_permissions, sender=Baustellen_Fotodokumentation_Fotos)

signals.post_delete.connect(delete_photo, sender=Baustellen_Fotodokumentation_Fotos)

signals.post_delete.connect(remove_permissions, sender=Baustellen_Fotodokumentation_Fotos)


# Baustellen (geplant)

class Baustellen_geplant(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  strasse = models.ForeignKey(Strassen, verbose_name='Straße', on_delete=models.SET_NULL, db_column='strasse', to_field='uuid', related_name='strassen+', blank=True, null=True)
  projektbezeichnung = models.CharField('Projektbezeichnung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  kurzbeschreibung = NullTextField('Kurzbeschreibung', max_length=500, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  lagebeschreibung = models.CharField('Lagebeschreibung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  verkehrliche_lagen = ChoiceArrayField(models.CharField(' verkehrliche Lage(n)', max_length=255, choices=()), verbose_name=' verkehrliche Lage(n)')
  sparten = ChoiceArrayField(models.CharField('Sparte(n)', max_length=255, choices=()), verbose_name='Sparte(n)')
  beginn = models.DateField('Beginn')
  ende = models.DateField('Ende')
  auftraggeber = models.ForeignKey(Auftraggeber_Baustellen, verbose_name='Auftraggeber', on_delete=models.RESTRICT, db_column='auftraggeber', to_field='uuid', related_name='auftraggeber+')
  ansprechpartner = models.CharField('Ansprechpartner', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  status = models.ForeignKey(Status_Baustellen_geplant, verbose_name='Status', on_delete=models.RESTRICT, db_column='status', to_field='uuid', related_name='status+')
  konflikt = models.BooleanField('Konflikt?', blank=True, null=True, editable=False)
  konflikt_tolerieren = models.BooleanField(' räumliche(n)/zeitliche(n) Konflikt(e) mit anderem/anderen Vorhaben tolerieren?', blank=True, null=True)
  geometrie = models.MultiPolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten_strassenbezug\".\"baustellen_geplant'
    verbose_name = 'Baustelle (geplant)'
    verbose_name_plural = 'Baustellen (geplant)'
    description = 'Baustellen (geplant) in der Hanse- und Universitätsstadt Rostock und Umgebung'
    choices_models_for_choices_fields = {
      'verkehrliche_lagen': 'Verkehrliche_Lagen_Baustellen',
      'sparten': 'Sparten_Baustellen'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'strasse': 'Straße',
      'bezeichnung': 'Bezeichnung',
      'verkehrliche_lagen': 'verkehrliche Lage(n)',
      'sparten': 'Sparte(n)',
      'beginn': 'Beginn',
      'ende': 'Ende',
      'auftraggeber': 'Auftraggeber',
      'ansprechpartner': 'Ansprechpartner',
      'status': 'Status',
      'konflikt': 'Konflikt(e)?',
      'konflikt_tolerieren': 'Konflikt(e) tolerieren?'
    }
    list_fields_with_date = ['beginn', 'ende']
    list_fields_with_foreign_key = {
      'strasse': 'strasse__strasse',
      'auftraggeber': 'auftraggeber__auftraggeber',
      'status': 'status__status'
    }
    highlight_flag = 'konflikt'
    map_feature_tooltip_field = 'bezeichnung'
    map_rangefilter_fields = {
      'beginn': 'Beginn',
      'ende': 'Ende'
    }
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'sparten': 'Sparte(n)',
      'auftraggeber': 'Auftraggeber',
      'status': 'Status'
    }
    map_filter_fields_as_list = ['auftraggeber', 'status']
    map_filter_hide_initial = {
      'status': 'abgeschlossen'
    }
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'MultiPolygon'
    group_with_users_for_choice_field = 'baustellen_geplant_add_delete_view'
    admin_group = 'baustellen_geplant_full'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Straße: ' + str(self.strasse) + ', ' if self.strasse else '') + 'Beginn: ' + datetime.strptime(str(self.beginn), '%Y-%m-%d').strftime('%d.%m.%Y') + ', Ende: ' + datetime.strptime(str(self.ende), '%Y-%m-%d').strftime('%d.%m.%Y') + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Baustellen_geplant, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Baustellen_geplant, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Baustellen_geplant)

signals.post_delete.connect(remove_permissions, sender=Baustellen_geplant)


# Behinderteneinrichtungen

class Behinderteneinrichtungen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Träger', on_delete=models.RESTRICT, db_column='traeger', to_field='uuid', related_name='traeger+')
  plaetze = PositiveSmallIntegerMinField('Plätze', min_value=1, blank=True, null=True)
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"behinderteneinrichtungen_hro'
    verbose_name = 'Behinderteneinrichtung'
    verbose_name_plural = 'Behinderteneinrichtungen'
    description = 'Behinderteneinrichtungen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'traeger': 'traeger__bezeichnung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Behinderteneinrichtungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Behinderteneinrichtungen, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Behinderteneinrichtungen)

signals.post_delete.connect(remove_permissions, sender=Behinderteneinrichtungen)


# Bildungsträger

class Bildungstraeger(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  betreiber = models.CharField('Betreiber', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  schlagwoerter = ChoiceArrayField(models.CharField('Schlagwörter', max_length=255, choices=()), verbose_name='Schlagwörter')
  barrierefrei = models.BooleanField(' barrierefrei?', blank=True, null=True)
  zeiten = models.CharField('Öffnungszeiten', max_length=255, blank=True, null=True)
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"bildungstraeger_hro'
    verbose_name = 'Bildungsträger'
    verbose_name_plural = 'Bildungsträger'
    description = 'Bildungsträger in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'schlagwoerter': 'Schlagwoerter_Bildungstraeger'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter'
    }
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Bildungstraeger, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Bildungstraeger, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Bildungstraeger)

signals.post_delete.connect(remove_permissions, sender=Bildungstraeger)


# Carsharing-Stationen

class Carsharing_Stationen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  anbieter = models.ForeignKey(Anbieter_Carsharing, verbose_name='Anbieter', on_delete=models.RESTRICT, db_column='anbieter', to_field='uuid', related_name='anbieter+')
  anzahl_fahrzeuge = PositiveSmallIntegerMinField('Anzahl der Fahrzeuge', min_value=1, blank=True, null=True)
  bemerkungen = NullTextField('Bemerkungen', max_length=500, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"carsharing_stationen_hro'
    verbose_name = 'Carsharing-Station'
    verbose_name_plural = 'Carsharing-Stationen'
    description = 'Carsharing-Stationen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'anbieter': 'Anbieter',
      'anzahl_fahrzeuge': 'Anzahl der Fahrzeuge'
    }
    list_fields_with_number = ['anzahl_fahrzeuge']
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'anbieter': 'anbieter__anbieter'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'anbieter': 'Anbieter'
    }
    map_filter_fields_as_list = ['anbieter']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Anbieter: ' + str(self.anbieter) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Carsharing_Stationen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Carsharing_Stationen, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Carsharing_Stationen)

signals.post_delete.connect(remove_permissions, sender=Carsharing_Stationen)


# Denkmalbereiche

class Denkmalbereiche(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  beschreibung = models.CharField('Beschreibung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.MultiPolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"denkmalbereiche_hro'
    verbose_name = 'Denkmalbereich'
    verbose_name_plural = 'Denkmalbereiche'
    description = 'Denkmalbereiche der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung'
    }
    geometry_type = 'MultiPolygon'

  def __str__(self):
    return self.bezeichnung + ' [Beschreibung: ' + str(self.beschreibung) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Denkmalbereiche, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Denkmalbereiche, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Denkmalbereiche)

signals.post_delete.connect(remove_permissions, sender=Denkmalbereiche)


# Denksteine

class Denksteine(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  nummer = models.CharField('Nummer', max_length=255, validators=[RegexValidator(regex=denksteine_nummer_regex, message=denksteine_nummer_message)])
  titel = models.ForeignKey(Personentitel, verbose_name='Titel', on_delete=models.SET_NULL, db_column='titel', to_field='uuid', related_name='titel+', blank=True, null=True)
  vorname = models.CharField('Vorname', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message), RegexValidator(regex=bindestrich_leerzeichen_regex, message=bindestrich_leerzeichen_message), RegexValidator(regex=leerzeichen_bindestrich_regex, message=leerzeichen_bindestrich_message)])
  nachname = models.CharField('Nachname', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message), RegexValidator(regex=bindestrich_leerzeichen_regex, message=bindestrich_leerzeichen_message), RegexValidator(regex=leerzeichen_bindestrich_regex, message=leerzeichen_bindestrich_message)])
  geburtsjahr = PositiveSmallIntegerRangeField('Geburtsjahr', min_value=1850, max_value=1945)
  sterbejahr = PositiveSmallIntegerRangeField('Sterbejahr', min_value=1933, max_value=1945, blank=True, null=True)
  text_auf_dem_stein = models.CharField('Text auf dem Stein', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ehemalige_adresse = models.CharField(' ehemalige Adresse', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  material = models.ForeignKey(Materialien_Denksteine, verbose_name='Material', on_delete=models.RESTRICT, db_column='material', to_field='uuid', related_name='materialien+')
  erstes_verlegejahr = PositiveSmallIntegerRangeField(' erstes Verlegejahr', min_value=2002, max_value=current_year())
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"denksteine_hro'
    verbose_name = 'Denkstein'
    verbose_name_plural = 'Denksteine'
    description = 'Denksteine in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'nummer': 'Nummer',
      'titel': 'Titel',
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'geburtsjahr': 'Geburtsjahr',
      'sterbejahr': 'Sterbejahr'
    }
    list_fields_with_number = ['geburtsjahr', 'sterbejahr']
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'titel': 'titel__bezeichnung'
    }
    map_feature_tooltip_fields = ['titel', 'vorname', 'nachname']
    map_filter_fields = {
      'nummer': 'Nummer',
      'titel': 'Titel',
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'geburtsjahr': 'Geburtsjahr',
      'sterbejahr': 'Sterbejahr'
    }
    map_filter_fields_as_list = ['titel']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return (str(self.titel) + ' ' if self.titel else '') + self.vorname + ' ' + self.nachname + ' (* ' + str(self.geburtsjahr) + (', † ' + str(self.sterbejahr) if self.sterbejahr else '') + ')' + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Denksteine, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Denksteine, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Denksteine)

signals.post_delete.connect(remove_permissions, sender=Denksteine)


# Fair Trade

class FairTrade(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  art = models.ForeignKey(Arten_FairTrade, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  betreiber = models.CharField('Betreiber', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  barrierefrei = models.BooleanField(' barrierefrei?', blank=True, null=True)
  zeiten = models.CharField('Öffnungszeiten', max_length=255, blank=True, null=True)
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"fairtrade_hro'
    verbose_name = 'Fair Trade'
    verbose_name_plural = 'Fair Trade'
    description = 'Fair Trade in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'art': 'art__art'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung'
    }
    map_filter_fields_as_list = ['art']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(FairTrade, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(FairTrade, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=FairTrade)

signals.post_delete.connect(remove_permissions, sender=FairTrade)


# Feuerwachen

class Feuerwachen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  art = models.ForeignKey(Arten_Feuerwachen, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"feuerwachen_hro'
    verbose_name = 'Feuerwache'
    verbose_name_plural = 'Feuerwachen'
    description = 'Feuerwachen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'art': 'art__art'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung'
    }
    map_filter_fields_as_list = ['art']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Feuerwachen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Feuerwachen, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Feuerwachen)

signals.post_delete.connect(remove_permissions, sender=Feuerwachen)


# Hospize

class Hospize(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Träger', on_delete=models.RESTRICT, db_column='traeger', to_field='uuid', related_name='traeger+')
  plaetze = PositiveSmallIntegerMinField('Plätze', min_value=1, blank=True, null=True)
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"hospize_hro'
    verbose_name = 'Hospiz'
    verbose_name_plural = 'Hospize'
    description = 'Hospize in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'traeger': 'traeger__bezeichnung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Hospize, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Hospize, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Hospize)

signals.post_delete.connect(remove_permissions, sender=Hospize)


# Hundetoiletten

class Hundetoiletten(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField('Außerbetriebstellung', blank=True, null=True)
  id = models.CharField('ID', max_length=8, default='00000000')
  art = models.ForeignKey(Arten_Hundetoiletten, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  aufstellungsjahr = PositiveSmallIntegerRangeField('Aufstellungsjahr', max_value=current_year(), blank=True, null=True)
  bewirtschafter = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Bewirtschafter', on_delete=models.RESTRICT, db_column='bewirtschafter', to_field='uuid', related_name='bewirtschafter+')
  pflegeobjekt = models.CharField('Pflegeobjekt', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  inventarnummer = models.CharField('Inventarnummer', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  anschaffungswert = models.DecimalField('Anschaffungswert (in €)', max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9999.99'), 'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 9.999,99 € betragen.')], blank=True, null=True)
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"hundetoiletten_hro'
    verbose_name = 'Hundetoilette'
    verbose_name_plural = 'Hundetoiletten'
    description = 'Hundetoiletten im Eigentum der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Außerbetriebstellung',
      'id': 'ID',
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt'
    }
    list_fields_with_date = ['deaktiviert']
    list_fields_with_number = ['id']
    list_fields_with_foreign_key = {
      'art': 'art__art',
      'bewirtschafter': 'bewirtschafter__bezeichnung'
    }
    readonly_fields = ['deaktiviert', 'id']
    map_feature_tooltip_field = 'id'
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt'
    }
    map_filter_fields_as_list = ['art', 'bewirtschafter']
    geometry_type = 'Point'
  
  def __str__(self):
    return self.id + ' [Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Hundetoiletten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Hundetoiletten, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Hundetoiletten)

signals.post_delete.connect(remove_permissions, sender=Hundetoiletten)


# Kindertagespflegeeinrichtungen

class Kindertagespflegeeinrichtungen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  vorname = models.CharField('Vorname', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message), RegexValidator(regex=bindestrich_leerzeichen_regex, message=bindestrich_leerzeichen_message), RegexValidator(regex=leerzeichen_bindestrich_regex, message=leerzeichen_bindestrich_message)])
  nachname = models.CharField('Nachname', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message), RegexValidator(regex=bindestrich_leerzeichen_regex, message=bindestrich_leerzeichen_message), RegexValidator(regex=leerzeichen_bindestrich_regex, message=leerzeichen_bindestrich_message)])
  plaetze = PositiveSmallIntegerMinField('Plätze', min_value=1)
  zeiten = models.CharField('Betreuungszeiten', max_length=255)
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"kindertagespflegeeinrichtungen_hro'
    verbose_name = 'Kindertagespflegeeinrichtung'
    verbose_name_plural = 'Kindertagespflegeeinrichtungen'
    description = 'Kindertagespflegeeinrichtungen (Tagesmütter und Tagesväter) in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'plaetze': 'Plätze',
      'zeiten': 'Betreuungszeiten'
    }
    list_fields_with_number = ['plaetze']
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse'
    }
    map_feature_tooltip_fields = ['vorname', 'nachname']
    map_filter_fields = {
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'plaetze': 'Plätze'
    }
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.vorname + ' ' + self.nachname + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Kindertagespflegeeinrichtungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Kindertagespflegeeinrichtungen, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Kindertagespflegeeinrichtungen)

signals.post_delete.connect(remove_permissions, sender=Kindertagespflegeeinrichtungen)


# Kinder- und Jugendbetreuung

class Kinder_Jugendbetreuung(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Träger', on_delete=models.RESTRICT, db_column='traeger', to_field='uuid', related_name='traeger+')
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"kinder_jugendbetreuung_hro'
    verbose_name = 'Kinder- und/oder Jugendbetreuung'
    verbose_name_plural = 'Kinder- und Jugendbetreuung'
    description = 'Kinder- und Jugendbetreuung in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'traeger': 'traeger__bezeichnung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Kinder_Jugendbetreuung, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Kinder_Jugendbetreuung, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Kinder_Jugendbetreuung)

signals.post_delete.connect(remove_permissions, sender=Kinder_Jugendbetreuung)


# Kunst im öffentlichen Raum

class Kunst_im_oeffentlichen_Raum(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ausfuehrung = models.CharField('Ausführung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  schoepfer = models.CharField('Schöpfer', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  entstehungsjahr = PositiveSmallIntegerRangeField('Entstehungsjahr', max_value=current_year(), blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"kunst_im_oeffentlichen_raum_hro'
    verbose_name = 'Kunst im öffentlichen Raum'
    verbose_name_plural = 'Kunst im öffentlichen Raum'
    description = 'Kunst im öffentlichen Raum der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'ausfuehrung': 'Ausführung',
      'schoepfer': 'Schöpfer',
      'entstehungsjahr': 'Entstehungsjahr'
    }
    list_fields_with_number = ['entstehungsjahr']
    map_feature_tooltip_field = 'bezeichnung'
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Kunst_im_oeffentlichen_Raum, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Kunst_im_oeffentlichen_Raum, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Kunst_im_oeffentlichen_Raum)

signals.post_delete.connect(remove_permissions, sender=Kunst_im_oeffentlichen_Raum)


# Ladestationen für Elektrofahrzeuge

class Ladestationen_Elektrofahrzeuge(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  geplant = models.BooleanField(' geplant?')
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  betreiber = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Betreiber', on_delete=models.SET_NULL, db_column='betreiber', to_field='uuid', related_name='betreiber+', blank=True, null=True)
  verbund = models.ForeignKey(Verbuende_Ladestationen_Elektrofahrzeuge, verbose_name='Verbund', on_delete=models.SET_NULL, db_column='verbund', to_field='uuid', related_name='verbuende+', blank=True, null=True)
  betriebsart = models.ForeignKey(Betriebsarten, verbose_name='Betriebsart', on_delete=models.RESTRICT, db_column='betriebsart', to_field='uuid', related_name='betriebsarten+')
  anzahl_ladepunkte = PositiveSmallIntegerMinField('Anzahl an Ladepunkten', min_value=1, blank=True, null=True)
  arten_ladepunkte = models.CharField('Arten der Ladepunkte', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ladekarten = ChoiceArrayField(models.CharField('Ladekarten', max_length=255, choices=()), verbose_name='Ladekarten', blank=True, null=True)
  kosten = models.CharField('Kosten', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  zeiten = models.CharField('Öffnungszeiten', max_length=255, blank=True, null=True)
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"ladestationen_elektrofahrzeuge_hro'
    verbose_name = 'Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Ladestationen für Elektrofahrzeuge'
    description = 'Ladestationen für Elektrofahrzeuge in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'ladekarten': 'Ladekarten_Ladestationen_Elektrofahrzeuge'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'geplant': 'geplant?',
      'bezeichnung': 'Bezeichnung',
      'betreiber': 'Betreiber',
      'verbund': 'Verbund',
      'betriebsart': 'Betriebsart',
      'anzahl_ladepunkte': 'Anzahl an Ladepunkten',
      'ladekarten': 'Ladekarten'
    }
    list_fields_with_number = ['anzahl_ladepunkte']
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'betreiber': 'betreiber__bezeichnung',
      'verbund': 'verbund__verbund',
      'betriebsart': 'betriebsart__betriebsart'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'geplant': 'geplant?',
      'bezeichnung': 'Bezeichnung',
      'betreiber': 'Betreiber',
      'verbund': 'Verbund',
      'betriebsart': 'Betriebsart',
      'anzahl_ladepunkte': 'Anzahl an Ladepunkten',
      'ladekarten': 'Ladekarten'
    }
    map_filter_fields_as_list = ['betreiber', 'verbund', 'betriebsart']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Ladestationen_Elektrofahrzeuge, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Ladestationen_Elektrofahrzeuge, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Ladestationen_Elektrofahrzeuge)

signals.post_delete.connect(remove_permissions, sender=Ladestationen_Elektrofahrzeuge)


# Meldedienst (flächenhaft)

class Meldedienst_flaechenhaft(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  art = models.ForeignKey(Arten_Meldedienst_flaechenhaft, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  bearbeiter = models.CharField('Bearbeiter', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  geometrie = models.PolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"meldedienst_flaechenhaft_hro'
    verbose_name = 'Meldedienst (flächenhaft)'
    verbose_name_plural = 'Meldedienst (flächenhaft)'
    description = 'Meldedienst (flächenhaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bearbeiter': 'Bearbeiter',
      'bemerkungen': 'Bemerkungen',
      'datum': 'Datum'
    }
    list_fields_with_date = ['datum']
    list_fields_with_foreign_key = {
      'art': 'art__art'
    }
    map_feature_tooltip_field = 'art'
    map_filter_fields = {
      'art': 'Art',
      'bearbeiter': 'Bearbeiter',
      'datum': 'Datum'
    }
    map_filter_fields_as_list = ['art']
    geometry_type = 'Polygon'

  def __str__(self):
    return str(self.art) + ' [Datum: ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Meldedienst_flaechenhaft, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Meldedienst_flaechenhaft, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Meldedienst_flaechenhaft)

signals.post_delete.connect(remove_permissions, sender=Meldedienst_flaechenhaft)


# Meldedienst (punkthaft)

class Meldedienst_punkthaft(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  art = models.ForeignKey(Arten_Meldedienst_punkthaft, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  bearbeiter = models.CharField('Bearbeiter', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"meldedienst_punkthaft_hro'
    verbose_name = 'Meldedienst (punkthaft)'
    verbose_name_plural = 'Meldedienst (punkthaft)'
    description = 'Meldedienst (punkthaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'bearbeiter': 'Bearbeiter',
      'bemerkungen': 'Bemerkungen',
      'datum': 'Datum'
    }
    list_fields_with_date = ['datum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'art': 'art__art'
    }
    map_feature_tooltip_field = 'art'
    map_filter_fields = {
      'art': 'Art',
      'bearbeiter': 'Bearbeiter',
      'datum': 'Datum'
    }
    map_filter_fields_as_list = ['art']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'

  def __str__(self):
    return str(self.art) + ' [Datum: ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + (', Adresse: ' + str(self.adresse) if self.adresse else '') + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Meldedienst_punkthaft, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Meldedienst_punkthaft, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Meldedienst_punkthaft)

signals.post_delete.connect(remove_permissions, sender=Meldedienst_punkthaft)


# Mobilpunkte

class Mobilpunkte(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  angebote = ChoiceArrayField(models.CharField('Angebote', max_length=255, choices=()), verbose_name='Angebote')
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"mobilpunkte_hro'
    verbose_name = 'Mobilpunkt'
    verbose_name_plural = 'Mobilpunkte'
    description = 'Mobilpunkte in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'angebote': 'Angebote_Mobilpunkte'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'angebote': 'Angebote',
      'website': 'Website'
    }
    map_feature_tooltip_field = 'bezeichnung'
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Mobilpunkte, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Mobilpunkte, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Mobilpunkte)

signals.post_delete.connect(remove_permissions, sender=Mobilpunkte)


# Parkmöglichkeiten

class Parkmoeglichkeiten(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  art = models.ForeignKey(Arten_Parkmoeglichkeiten, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  standort = models.CharField('Standort', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  betreiber = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Betreiber', on_delete=models.SET_NULL, db_column='betreiber', to_field='uuid', related_name='betreiber+', blank=True, null=True)
  stellplaetze_pkw = PositiveSmallIntegerMinField('Pkw-Stellplätze', min_value=1, blank=True, null=True)
  stellplaetze_wohnmobil = PositiveSmallIntegerMinField('Wohnmobilstellplätze', min_value=1, blank=True, null=True)
  stellplaetze_bus = PositiveSmallIntegerMinField('Busstellplätze', min_value=1, blank=True, null=True)
  gebuehren_halbe_stunde = models.DecimalField('Gebühren pro ½ h (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die <strong><em>Gebühren pro ½ h</em></strong> müssen mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9.99'), 'Die <strong><em>Gebühren pro ½ h</em></strong> dürfen höchstens 9,99 € betragen.')], blank=True, null=True)
  gebuehren_eine_stunde = models.DecimalField('Gebühren pro 1 h (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die <strong><em>Gebühren pro 1 h</em></strong> müssen mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9.99'), 'Die <strong><em>Gebühren pro 1 h</em></strong> dürfen höchstens 9,99 € betragen.')], blank=True, null=True)
  gebuehren_zwei_stunden = models.DecimalField('Gebühren pro 2 h (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die <strong><em>Gebühren pro 2 h</em></strong> müssen mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9.99'), 'Die <strong><em>Gebühren pro 2 h</em></strong> dürfen höchstens 9,99 € betragen.')], blank=True, null=True)
  gebuehren_ganztags = models.DecimalField('Gebühren ganztags (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die <strong><em>Gebühren ganztags</em></strong> müssen mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9.99'), 'Die <strong><em>Gebühren ganztags</em></strong> dürfen höchstens 9,99 € betragen.')], blank=True, null=True)
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"parkmoeglichkeiten_hro'
    verbose_name = 'Parkmöglichkeit'
    verbose_name_plural = 'Parkmöglichkeiten'
    description = 'Parkmöglichkeiten in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'standort': 'Standort',
      'betreiber': 'Betreiber'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'art': 'art__art',
      'betreiber': 'betreiber__bezeichnung'
    }
    map_feature_tooltip_fields = ['art', 'standort']
    map_filter_fields = {
      'art': 'Art',
      'standort': 'Standort',
      'betreiber': 'Betreiber'
    }
    map_filter_fields_as_list = ['art', 'betreiber']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
  
  def __str__(self):
    return str(self.art) + ' ' + self.standort + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Parkmoeglichkeiten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Parkmoeglichkeiten, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Parkmoeglichkeiten)

signals.post_delete.connect(remove_permissions, sender=Parkmoeglichkeiten)


# Tarife der Parkscheinautomaten

class Parkscheinautomaten_Tarife(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  zeiten = models.CharField('Bewirtschaftungszeiten', max_length=255)
  normaltarif_parkdauer_min = PositiveSmallIntegerMinField('Mindestparkdauer Normaltarif', min_value=1)
  normaltarif_parkdauer_min_einheit = models.ForeignKey(Zeiteinheiten, verbose_name='Einheit der Mindestparkdauer Normaltarif', on_delete=models.RESTRICT, db_column='normaltarif_parkdauer_min_einheit', to_field='uuid', related_name='normaltarif_parkdauer_min_einheiten+')
  normaltarif_parkdauer_max = PositiveSmallIntegerMinField('Maximalparkdauer Normaltarif', min_value=1)
  normaltarif_parkdauer_max_einheit = models.ForeignKey(Zeiteinheiten, verbose_name='Einheit der Maximalparkdauer Normaltarif', on_delete=models.RESTRICT, db_column='normaltarif_parkdauer_max_einheit', to_field='uuid', related_name='normaltarif_parkdauer_max_einheiten+')
  normaltarif_gebuehren_max = models.DecimalField('Maximalgebühren Normaltarif (in €)', max_digits=4, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die <strong><em>Maximalgebühren Normaltarif</strong></em> müssen mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9.99'), 'Die <strong><em>Maximalgebühren Normaltarif</em></strong> dürfen höchstens 99,99 € betragen.')], blank=True, null=True)
  normaltarif_gebuehren_pro_stunde = models.DecimalField('Gebühren pro Stunde Normaltarif (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die <strong><em>Gebühren pro Stunde Normaltarif</strong></em> müssen mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9.99'), 'Die <strong><em>Gebühren pro Stunde Normaltarif</em></strong> dürfen höchstens 9,99 € betragen.')], blank=True, null=True)
  normaltarif_gebuehrenschritte = models.CharField('Gebührenschritte Normaltarif', max_length=255, blank=True, null=True)
  veranstaltungstarif_parkdauer_min = PositiveSmallIntegerMinField('Mindestparkdauer Veranstaltungstarif', min_value=1, blank=True, null=True)
  veranstaltungstarif_parkdauer_min_einheit = models.ForeignKey(Zeiteinheiten, verbose_name='Einheit der Mindestparkdauer Veranstaltungstarif', on_delete=models.SET_NULL, db_column='veranstaltungstarif_parkdauer_min_einheit', to_field='uuid', related_name='veranstaltungstarif_parkdauer_min_einheiten+', blank=True, null=True)
  veranstaltungstarif_parkdauer_max = PositiveSmallIntegerMinField('Maximalparkdauer Veranstaltungstarif', min_value=1, blank=True, null=True)
  veranstaltungstarif_parkdauer_max_einheit = models.ForeignKey(Zeiteinheiten, verbose_name='Einheit der Maximalparkdauer Veranstaltungstarif', on_delete=models.SET_NULL, db_column='veranstaltungstarif_parkdauer_max_einheit', to_field='uuid', related_name='veranstaltungstarif_parkdauer_max_einheiten+', blank=True, null=True)
  veranstaltungstarif_gebuehren_max = models.DecimalField('Maximalgebühren Veranstaltungstarif (in €)', max_digits=4, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die <strong><em>Maximalgebühren Veranstaltungstarif</strong></em> müssen mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9.99'), 'Die <strong><em>Maximalgebühren Veranstaltungstarif</em></strong> dürfen höchstens 99,99 € betragen.')], blank=True, null=True)
  veranstaltungstarif_gebuehren_pro_stunde = models.DecimalField('Gebühren pro Stunde Veranstaltungstarif (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die <strong><em>Gebühren pro Stunde Veranstaltungstarif</strong></em> müssen mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('9.99'), 'Die <strong><em>Gebühren pro Stunde Veranstaltungstarif</em></strong> dürfen höchstens 9,99 € betragen.')], blank=True, null=True)
  veranstaltungstarif_gebuehrenschritte = models.CharField('Gebührenschritte Veranstaltungstarif', max_length=255, blank=True, null=True)
  zugelassene_muenzen = models.CharField(' zugelassene Münzen', max_length=255)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"parkscheinautomaten_tarife_hro'
    verbose_name = 'Tarif der Parkscheinautomaten'
    verbose_name_plural = 'Tarife der Parkscheinautomaten'
    description = 'Tarife der Parkscheinautomaten der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'zeiten': 'Bewirtschaftungszeiten'
    }
    ordering = ['bezeichnung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Parkscheinautomaten_Tarife, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Parkscheinautomaten_Tarife, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Parkscheinautomaten_Tarife)

signals.post_delete.connect(remove_permissions, sender=Parkscheinautomaten_Tarife)


# Parkscheinautomaten

class Parkscheinautomaten_Parkscheinautomaten(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  parkscheinautomaten_tarif = models.ForeignKey(Parkscheinautomaten_Tarife, verbose_name='Tarif', on_delete=models.CASCADE, db_column='parkscheinautomaten_tarif', to_field='uuid', related_name='parkscheinautomaten_tarife+')
  nummer = models.PositiveSmallIntegerField('Nummer')
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  zone = models.ForeignKey(Zonen_Parkscheinautomaten, verbose_name='Zone', on_delete=models.RESTRICT, db_column='zone', to_field='uuid', related_name='zonen+')
  handyparkzone = PositiveIntegerRangeField('Handyparkzone', min_value=100000, max_value=999999)
  bewohnerparkgebiet = models.CharField('Bewohnerparkgebiet', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=parkscheinautomaten_bewohnerparkgebiet_regex, message=parkscheinautomaten_bewohnerparkgebiet_message)])
  geraetenummer = models.CharField('Gerätenummer', max_length=8, validators=[RegexValidator(regex=parkscheinautomaten_geraetenummer_regex, message=parkscheinautomaten_geraetenummer_message)])
  inbetriebnahme = models.DateField('Inbetriebnahme', blank=True, null=True)
  e_anschluss = models.ForeignKey(E_Anschluesse_Parkscheinautomaten, verbose_name='E-Anschluss', on_delete=models.RESTRICT, db_column='e_anschluss', to_field='uuid', related_name='e_anschluesse+')
  stellplaetze_pkw = PositiveSmallIntegerMinField('Pkw-Stellplätze', min_value=1, blank=True, null=True)
  stellplaetze_bus = PositiveSmallIntegerMinField('Bus-Stellplätze', min_value=1, blank=True, null=True)
  haendlerkartennummer = PositiveIntegerRangeField('Händlerkartennummer', min_value=1000000000, max_value=9999999999, blank=True, null=True)
  laufzeit_geldkarte = models.DateField('Laufzeit der Geldkarte', blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"parkscheinautomaten_parkscheinautomaten_hro'
    verbose_name = 'Parkscheinautomat'
    verbose_name_plural = 'Parkscheinautomaten'
    description = 'Parkscheinautomaten der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'parkscheinautomaten_tarif': 'Tarif',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'zone': 'Zone'
    }
    list_fields_with_foreign_key = {
      'parkscheinautomaten_tarif': 'parkscheinautomaten_tarif__bezeichnung',
      'zone': 'zone__zone'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'parkscheinautomaten_tarif': 'Tarif',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'zone': 'Zone'
    }
    map_filter_fields_as_list = ['parkscheinautomaten_tarif', 'zone']
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Parkscheinautomaten_Parkscheinautomaten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Parkscheinautomaten_Parkscheinautomaten, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Parkscheinautomaten_Parkscheinautomaten)

signals.post_delete.connect(remove_permissions, sender=Parkscheinautomaten_Parkscheinautomaten)


# Pflegeeinrichtungen

class Pflegeeinrichtungen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  art = models.ForeignKey(Arten_Pflegeeinrichtungen, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  betreiber = models.CharField('Betreiber', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  plaetze = PositiveSmallIntegerMinField('Plätze', min_value=1, blank=True, null=True)
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"pflegeeinrichtungen_hro'
    verbose_name = 'Pflegeeinrichtung'
    verbose_name_plural = 'Pflegeeinrichtungen'
    description = 'Pflegeeinrichtungen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'betreiber': 'Betreiber'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'art': 'art__art'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'betreiber': 'Betreiber'
    }
    map_filter_fields_as_list = ['art']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Pflegeeinrichtungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Pflegeeinrichtungen, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Pflegeeinrichtungen)

signals.post_delete.connect(remove_permissions, sender=Pflegeeinrichtungen)


# Rettungswachen

class Rettungswachen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Träger', on_delete=models.RESTRICT, db_column='traeger', to_field='uuid', related_name='traeger+')
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"rettungswachen_hro'
    verbose_name = 'Rettungswache'
    verbose_name_plural = 'Rettungswachen'
    description = 'Rettungswachen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'traeger': 'traeger__bezeichnung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Rettungswachen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Rettungswachen, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Rettungswachen)

signals.post_delete.connect(remove_permissions, sender=Rettungswachen)


# Stadtteil- und Begegnungszentren

class Stadtteil_Begegnungszentren(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Träger', on_delete=models.RESTRICT, db_column='traeger', to_field='uuid', related_name='traeger+')
  barrierefrei = models.BooleanField(' barrierefrei?', blank=True, null=True)
  zeiten = models.CharField('Öffnungszeiten', max_length=255, blank=True, null=True)
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"stadtteil_begegnungszentren_hro'
    verbose_name = 'Stadtteil- und/oder Begegnungszentrum'
    verbose_name_plural = 'Stadtteil- und Begegnungszentren'
    description = 'Stadtteil- und Begegnungszentren in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse',
      'traeger': 'traeger__bezeichnung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Stadtteil_Begegnungszentren, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Stadtteil_Begegnungszentren, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Stadtteil_Begegnungszentren)

signals.post_delete.connect(remove_permissions, sender=Stadtteil_Begegnungszentren)


# UVP-Vorhaben

class UVP_Vorhaben(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  vorgangsart = models.ForeignKey(Vorgangsarten_UVP_Vorhaben, verbose_name='Vorgangsart', on_delete=models.RESTRICT, db_column='vorgangsart', to_field='uuid', related_name='vorgangsarten+')
  genehmigungsbehoerde = models.ForeignKey(Genehmigungsbehoerden_UVP_Vorhaben, verbose_name='Genehmigungsbehörde', on_delete=models.RESTRICT, db_column='genehmigungsbehoerde', to_field='uuid', related_name='genehmigungsbehoerden+')
  datum_posteingang_genehmigungsbehoerde = models.DateField('Datum des Posteingangs bei der Genehmigungsbehörde')
  registriernummer_bauamt = models.CharField('Registriernummer des Bauamtes', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=uvp_vorhaben_registriernummer_bauamt_regex, message=uvp_vorhaben_registriernummer_bauamt_message)])
  aktenzeichen = models.CharField('Aktenzeichen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  rechtsgrundlage = models.ForeignKey(Rechtsgrundlagen_UVP_Vorhaben, verbose_name='Rechtsgrundlage', on_delete=models.RESTRICT, db_column='rechtsgrundlage', to_field='uuid', related_name='rechtsgrundlagen+')
  typ = models.ForeignKey(Typen_UVP_Vorhaben, verbose_name='Typ', on_delete=models.RESTRICT, db_column='typ', to_field='uuid', related_name='typen+')
  geometrie = models.PolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"uvp_vorhaben_hro'
    verbose_name = 'UVP-Vorhaben'
    verbose_name_plural = 'UVP-Vorhaben'
    description = 'Vorhaben, auf die sich Vorprüfungen der Hanse- und Universitätsstadt Rostock zur Feststellung der UVP-Pflicht gemäß UVPG und LUVPG M-V beziehen'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'vorgangsart': 'Vorgangsart',
      'genehmigungsbehoerde': 'Genehmigungsbehörde',
      'datum_posteingang_genehmigungsbehoerde': 'Datum des Posteingangs bei der Genehmigungsbehörde',
      'rechtsgrundlage': 'Rechtsgrundlage',
      'typ': 'Typ'
    }
    list_fields_with_foreign_key = {
      'vorgangsart': 'vorgangsart__vorgangsart',
      'genehmigungsbehoerde': 'genehmigungsbehoerde__genehmigungsbehoerde',
      'rechtsgrundlage': 'rechtsgrundlage__rechtsgrundlage',
      'typ': 'typ__typ'
    }
    list_fields_with_date = ['datum_posteingang_genehmigungsbehoerde']
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'vorgangsart': 'Vorgangsart',
      'genehmigungsbehoerde': 'Genehmigungsbehörde',
      'datum_posteingang_genehmigungsbehoerde': 'Datum des Posteingangs bei der Genehmigungsbehörde',
      'rechtsgrundlage': 'Rechtsgrundlage',
      'typ': 'Typ'
    }
    map_filter_fields_as_list = ['vorgangsart', 'genehmigungsbehoerde', 'rechtsgrundlage', 'typ']
    geometry_type = 'Polygon'
    ordering = ['bezeichnung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(UVP_Vorhaben, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(UVP_Vorhaben, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=UVP_Vorhaben)

signals.post_delete.connect(remove_permissions, sender=UVP_Vorhaben)


# UVP-Vorprüfungen

class UVP_Vorpruefungen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  uvp_vorhaben = models.ForeignKey(UVP_Vorhaben, verbose_name='Vorhaben', on_delete=models.CASCADE, db_column='uvp_vorhaben', to_field='uuid', related_name='uvp_vorhaben+')
  art = models.ForeignKey(Arten_UVP_Vorpruefungen, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  datum_posteingang = models.DateField('Datum des Posteingangs')
  datum = models.DateField('Datum', default=date.today)
  ergebnis = models.ForeignKey(Ergebnisse_UVP_Vorpruefungen, verbose_name='Ergebnis', on_delete=models.RESTRICT, db_column='ergebnis', to_field='uuid', related_name='ergebnisse+')
  datum_bekanntmachung = models.DateField('Datum Bekanntmachung „Städtischer Anzeiger“', blank=True, null=True)
  datum_veroeffentlichung = models.DateField('Datum Veröffentlichung UVP-Portal', blank=True, null=True)
  pruefprotokoll = models.CharField('Prüfprotokoll', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"uvp_vorpruefungen_hro'
    verbose_name = 'UVP-Vorprüfungen'
    verbose_name_plural = 'UVP-Vorprüfungen'
    description = 'Vorprüfungen der Hanse- und Universitätsstadt Rostock zur Feststellung der UVP-Pflicht gemäß UVPG und LUVPG M-V'
    list_fields = {
      'aktiv': 'aktiv?',
      'uvp_vorhaben': 'Vorhaben',
      'art': 'Art',
      'datum_posteingang': 'Datum des Posteingangs',
      'datum': 'Datum',
      'ergebnis': 'Ergebnis'
    }
    list_fields_with_foreign_key = {
      'uvp_vorhaben': 'uvp_vorhaben__bezeichnung',
      'art': 'art__art',
      'ergebnis': 'ergebnis__ergebnis'
    }
    list_fields_with_date = ['datum_posteingang', 'datum']
    object_title = 'die UVP-Vorprüfung'
    foreign_key_label = 'Vorhaben'

  def __str__(self):
    return str(self.uvp_vorhaben) + ' mit Datum ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + ' [Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(UVP_Vorpruefungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(UVP_Vorpruefungen, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=UVP_Vorpruefungen)

signals.post_delete.connect(remove_permissions, sender=UVP_Vorpruefungen)


# Vereine

class Vereine(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  vereinsregister_id = PositiveSmallIntegerMinField('ID im Vereinsregister', min_value=1, unique=True, blank=True, null=True)
  vereinsregister_datum = models.DateField('Datum des Eintrags im Vereinsregister', blank=True, null=True)
  schlagwoerter = ChoiceArrayField(models.CharField('Schlagwörter', max_length=255, choices=()), verbose_name='Schlagwörter')
  telefon_festnetz = models.CharField('Telefon (Festnetz)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  telefon_mobil = models.CharField('Telefon (mobil)', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail-Adresse', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"vereine_hro'
    verbose_name = 'Verein'
    verbose_name_plural = 'Vereine'
    description = 'Vereine in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'schlagwoerter': 'Schlagwoerter_Vereine'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter'
    }
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Vereine, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Vereine, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Vereine)

signals.post_delete.connect(remove_permissions, sender=Vereine)






# isi3
class Containerstellplaetze(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  gueltigkeit_bis = models.DateField('Außerbetriebstellung', blank=True, null=True)
  privat = models.BooleanField(' privat', blank=True, null=True)
  id_containerstellplatz = models.CharField('ID', max_length=5, validators=[RegexValidator(regex=id_containerstellplatz_regex, message=id_containerstellplatz_message)], blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  anzahl_glas = models.PositiveSmallIntegerField('Anzahl Glas normal', blank=True, null=True)
  anzahl_glas_unterflur = models.PositiveSmallIntegerField('Anzahl Glas unterflur', blank=True, null=True)
  bewirtschafter_id_glas = models.PositiveSmallIntegerField('Bewirtschafter Glas', choices=BEWIRTSCHAFTER_GLAS_CONTAINERSTELLPLAETZE, blank=True, null=True)
  bewirtschafter_glas = models.CharField('Bewirtschafter Glas', max_length=255, editable=False)
  anzahl_papier = models.PositiveSmallIntegerField('Anzahl Papier normal', blank=True, null=True)
  anzahl_papier_unterflur = models.PositiveSmallIntegerField('Anzahl Papier unterflur', blank=True, null=True)
  bewirtschafter_id_papier = models.PositiveSmallIntegerField('Bewirtschafter Papier', choices=BEWIRTSCHAFTER_PAPIER_CONTAINERSTELLPLAETZE, blank=True, null=True)
  bewirtschafter_papier = models.CharField('Bewirtschafter Papier', max_length=255, editable=False)
  anzahl_altkleider = models.PositiveSmallIntegerField('Anzahl Altkleider', blank=True, null=True)
  bewirtschafter_id_altkleider = models.PositiveSmallIntegerField('Bewirtschafter Altkleider', choices=BEWIRTSCHAFTER_ALTKLEIDER_CONTAINERSTELLPLAETZE, blank=True, null=True)
  bewirtschafter_altkleider = models.CharField('Bewirtschafter Altkleider', max_length=255, editable=False)
  inbetriebnahmejahr = PositiveSmallIntegerRangeField('Inbetriebnahmejahr', min_value=1900, max_value=current_year(), blank=True, null=True)
  flaeche = models.DecimalField('Stellplatzfläche (in m²)', max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Stellplatzfläche muss mindestens 0,01 m² groß sein.')], blank=True, null=True)
  inventarnummer_grundundboden = models.CharField('Inventarnummer Grund und Boden', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  inventarnummer = models.CharField('Inventarnummer Stellplatz', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  inventarnummer_zaun = models.CharField('Inventarnummer Zaun', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  anschaffungswert = models.DecimalField('Anschaffungswert (in €)', max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Anschaffungswert muss mindestens 0,01 € betragen.')], blank=True, null=True)
  bewirtschafter_id_grundundboden = models.PositiveSmallIntegerField('Bewirtschafter Grund und Boden', choices=BEWIRTSCHAFTER_GRUNDUNDBODEN_CONTAINERSTELLPLAETZE, blank=True, null=True)
  bewirtschafter_grundundboden = models.CharField('Bewirtschafter Grund und Boden', max_length=255, editable=False)
  oeffentliche_widmung = models.BooleanField('öffentliche Widmung', blank=True, null=True)
  art_eigentumserwerb = models.CharField('Art des Eigentumserwerbs Stellplatz', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art_eigentumserwerb_zaun = models.CharField('Art des Eigentumserwerbs Zaun', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  vertraege = models.CharField('Verträge', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bga_grundundboden = models.BooleanField('Zuordnung BgA Grund und Boden', blank=True, null=True)
  bga = models.BooleanField('Zuordnung BgA Stellplatz', blank=True, null=True)
  bga_zaun = models.BooleanField('Zuordnung BgA Zaun', blank=True, null=True)
  winterdienst_a = models.BooleanField('Winterdienst A', blank=True, null=True)
  winterdienst_b = models.BooleanField('Winterdienst B', blank=True, null=True)
  winterdienst_c = models.BooleanField('Winterdienst C', blank=True, null=True)
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'containerstellplaetze'), max_length=255, blank=True, null=True)
  adressanzeige = models.CharField('Adresse', max_length=255, blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"containerstellplaetze'
    verbose_name = 'Containerstellplatz'
    verbose_name_plural = 'Containerstellplätze'
    description = 'Containerstellplätze in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['gueltigkeit_bis', 'privat', 'id_containerstellplatz', 'bezeichnung', 'adressanzeige']
    list_fields_with_date = ['gueltigkeit_bis']
    list_fields_labels = ['Außerbetriebstellung', 'privat', 'ID', 'Bezeichnung', 'Adresse']
    readonly_fields = ['adressanzeige']
    map_feature_tooltip_field = 'id_containerstellplatz'
    geometry_type = 'Point'
  
  def __str__(self):
    return 'Containerstellplatz' + (' mit ID ' + self.id_containerstellplatz + ' und Bezeichnung ' if self.id_containerstellplatz else ' mit Bezeichnung ') + self.bezeichnung + (', ' + self.adressanzeige if self.adressanzeige else '')


# isi2
class Fliessgewaesser(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  nummer = models.CharField('Nummer', max_length=255)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ordnung = PositiveSmallIntegerRangeField('Ordnung', min_value=1, max_value=2, blank=True, null=True)
  art = models.CharField('Art', max_length=255, choices=ART_FLIESSGEWAESSER)
  nennweite = models.PositiveIntegerField('Nennweite (in Millimetern)', blank=True, null=True)
  geometrie = models.LineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'daten\".\"fliessgewaesser'
    verbose_name = 'Fließgewässer'
    verbose_name_plural = 'Fließgewässer'
    description = 'Fließgewässer in der Hanse- und Universitätsstadt Rostock und Umgebung'
    list_fields = ['uuid', 'nummer', 'bezeichnung', 'ordnung', 'art']
    list_fields_labels = ['UUID', 'Nummer', 'Bezeichnung', 'Ordnung', 'Art']
    map_feature_tooltip_field = 'nummer'
    geometry_type = 'LineString'
  
  def __str__(self):
    if self.ordnung:
      output_ordnung = ', ' + str(self.ordnung) + '. Ordnung'
    else:
      output_ordnung = ''
    return self.art + output_ordnung + ', Nummer ' + self.nummer + ' (UUID: ' + str(self.uuid) + ')'


class Gutachterfotos(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse/Straße', max_length=255, blank=True, null=True)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  bearbeiter = models.CharField('Bearbeiter', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkung = models.CharField('Bemerkung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  aufnahmedatum = models.DateField('Aufnahmedatum')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'gutachterfotos'), max_length=255)
  adressanzeige = models.CharField('Adresse', max_length=255, blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"gutachterfotos'
    verbose_name = 'Gutachterfoto'
    verbose_name_plural = 'Gutachterfotos'
    description = 'Gutachterfotos der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'adressanzeige', 'bearbeiter', 'datum', 'aufnahmedatum']
    list_fields_with_date = ['datum', 'aufnahmedatum']
    list_fields_labels = ['UUID', 'Adresse', 'Bearbeiter', 'Datum', 'Aufnahmedatum']
    readonly_fields = ['adressanzeige']
    map_feature_tooltip_field = 'uuid'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
  
  def __str__(self):
    return 'Gutachterfoto mit Aufnahmedatum ' + datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y') + (', ' + self.adressanzeige if self.adressanzeige else '') + ' (UUID: ' + str(self.uuid) + ')'


class Haltestellenkataster_Haltestellen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  gemeindeteilanzeige = models.CharField('Gemeindeteil', max_length=255, blank=True, null=True)
  hst_bezeichnung = models.CharField('Haltestellenbezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_hafas_id = models.CharField('HAFAS-ID', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=hafas_id_regex, message=hafas_id_message)])
  hst_bus_bahnsteigbezeichnung = models.CharField('Bus-/Bahnsteigbezeichnung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_richtung = models.CharField('Richtungsinformation', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_kategorie = models.CharField('Haltestellenkategorie', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_linien = models.CharField(' bedienende Linie(n)', max_length=255, choices=LINIEN_HALTESTELLEN, blank=True, null=True)
  hst_rsag = models.BooleanField(' bedient durch Rostocker Straßenbahn AG?', blank=True, null=True)
  hst_rebus = models.BooleanField(' bedient durch rebus Regionalbus Rostock GmbH?', blank=True, null=True)
  hst_nur_ausstieg = models.BooleanField(' nur Ausstieg?', blank=True, null=True)
  hst_nur_einstieg = models.BooleanField(' nur Einstieg?', blank=True, null=True)
  hst_verkehrsmittelklassen = models.CharField('Verkehrsmittelklasse(n)', max_length=255, choices=VERKEHRSMITTELKLASSEN_HALTESTELLEN)
  hst_fahrgastzahl = models.PositiveIntegerField(' durchschnittliche Fahrgastzahl', blank=True, null=True)
  bau_typ = models.CharField('Typ', max_length=255, choices=TYP_HALTESTELLEN, blank=True, null=True)
  bau_wartebereich_laenge = models.DecimalField('Länge des Wartebereichs (in m)', max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Wartebereich muss mindestens 0,01 m lang sein.')], blank=True, null=True)
  bau_wartebereich_breite = models.DecimalField('Breite des Wartebereichs (in m)', max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Wartebereich muss mindestens 0,01 m breit sein.')], blank=True, null=True)
  bau_befestigungsart_aufstellflaeche_bus = models.CharField('Befestigungsart der Aufstellfläche Bus', max_length=255, choices=BEFESTIGUNGSART_AUFSTELLFLAECHE_BUS_HALTESTELLEN, blank=True, null=True)
  bau_zustand_aufstellflaeche_bus = models.CharField('Zustand der Aufstellfläche Bus', max_length=255, choices=SCHAEDEN_HALTESTELLEN, blank=True, null=True)
  bau_befestigungsart_warteflaeche = models.CharField('Befestigungsart der Wartefläche', max_length=255, choices=BEFESTIGUNGSART_WARTEFLAECHE_HALTESTELLEN, blank=True, null=True)
  bau_zustand_warteflaeche = models.CharField('Zustand der Wartefläche', max_length=255, choices=SCHAEDEN_HALTESTELLEN, blank=True, null=True)
  bf_einstieg = models.BooleanField(' barrierefreier Einstieg vorhanden?', blank=True, null=True)
  bf_zu_abgaenge = models.BooleanField(' barrierefreie Zu- und Abgänge vorhanden?', blank=True, null=True)
  bf_bewegungsraum = models.BooleanField(' barrierefreier Bewegungsraum vorhanden?', blank=True, null=True)
  tl_auffindestreifen = models.BooleanField('Taktiles Leitsystem: Auffindestreifen vorhanden?', blank=True, null=True)
  tl_auffindestreifen_ausfuehrung = models.CharField('Taktiles Leitsystem: Ausführung Auffindestreifen', max_length=255, choices=AUSFUEHRUNG_HALTESTELLEN, blank=True, null=True)
  tl_auffindestreifen_breite = models.PositiveIntegerField('Taktiles Leitsystem: Breite des Auffindestreifens (in cm)', blank=True, null=True)
  tl_einstiegsfeld = models.BooleanField('Taktiles Leitsystem: Einstiegsfeld vorhanden?', blank=True, null=True)
  tl_einstiegsfeld_ausfuehrung = models.CharField('Taktiles Leitsystem: Ausführung Einstiegsfeld', max_length=255, choices=AUSFUEHRUNG_HALTESTELLEN, blank=True, null=True)
  tl_einstiegsfeld_breite = models.PositiveIntegerField('Taktiles Leitsystem: Breite des Einstiegsfelds (in cm)', blank=True, null=True)
  tl_leitstreifen = models.BooleanField('Taktiles Leitsystem: Leitstreifen vorhanden?', blank=True, null=True)
  tl_leitstreifen_ausfuehrung = models.CharField('Taktiles Leitsystem: Ausführung Leitstreifen', max_length=255, choices=AUSFUEHRUNG_HALTESTELLEN, blank=True, null=True)
  tl_leitstreifen_laenge = models.PositiveIntegerField('Taktiles Leitsystem: Länge des Leitstreifens (in cm)', blank=True, null=True)
  tl_aufmerksamkeitsfeld = models.BooleanField('Aufmerksamkeitsfeld (1. Tür) vorhanden?', blank=True, null=True)
  tl_bahnsteigkante_visuell = models.BooleanField('Bahnsteigkante visuell erkennbar?', blank=True, null=True)
  tl_bahnsteigkante_taktil = models.BooleanField('Bahnsteigkante taktil erkennbar?', blank=True, null=True)
  as_zh_typ = models.CharField('ZH-Typ', max_length=255, choices=ZH_TYPEN_HALTESTELLEN, blank=True, null=True)
  as_h_mast = models.BooleanField('Mast vorhanden?', blank=True, null=True)
  as_h_masttyp = models.CharField('Typ des Mastes', max_length=255, choices=MASTTYPEN_HALTESTELLEN, blank=True, null=True)
  as_papierkorb = models.BooleanField('Papierkorb vorhanden?', blank=True, null=True)
  as_fahrgastunterstand = models.BooleanField('Fahrgastunterstand vorhanden?', blank=True, null=True)
  as_fahrgastunterstandstyp = models.CharField('Typ des Fahrgastunterstands', max_length=255, choices=FAHRGASTUNTERSTANDSTYPEN_HALTESTELLEN, blank=True, null=True)
  as_sitzbank_mit_armlehne = models.BooleanField('Sitzbank mit Armlehne vorhanden?', blank=True, null=True)
  as_sitzbank_ohne_armlehne = models.BooleanField('Sitzbank ohne Armlehne vorhanden?', blank=True, null=True)
  as_sitzbanktyp = models.CharField('Typ der Sitzbank', max_length=255, choices=SITZBANKTYPEN_HALTESTELLEN, blank=True, null=True)
  as_gelaender = models.BooleanField('Geländer vorhanden?', blank=True, null=True)
  as_fahrplanvitrine = models.BooleanField('Fahrplanvitrine vorhanden?', blank=True, null=True)
  as_fahrplanvitrinentyp = models.CharField('Typ der Fahrplanvitrine', max_length=255, choices=FAHRPLANVITRINENTYPEN_HALTESTELLEN, blank=True, null=True)
  as_tarifinformation = models.BooleanField('Tarifinformation vorhanden?', blank=True, null=True)
  as_liniennetzplan = models.BooleanField('Liniennetzplan vorhanden?', blank=True, null=True)
  as_fahrplan = models.BooleanField('Fahrplan vorhanden?', blank=True, null=True)
  as_fahrausweisautomat = models.BooleanField('Fahrausweisautomat vorhanden?', blank=True, null=True)
  as_lautsprecher = models.BooleanField('Lautsprecher vorhanden?', blank=True, null=True)
  as_dfi = models.BooleanField('Dynamisches Fahrgastinformationssystem vorhanden?', blank=True, null=True)
  as_dfi_typ = models.CharField('Typ des Dynamischen Fahrgastinformationssystems', max_length=255, choices=DFI_TYPEN_HALTESTELLEN, blank=True, null=True)
  as_anfragetaster = models.BooleanField('Anfragetaster vorhanden?', blank=True, null=True)
  as_blindenschrift = models.BooleanField('Haltestellen-/Linieninformationen in Blindenschrift vorhanden?', blank=True, null=True)
  as_beleuchtung = models.BooleanField('Beleuchtung vorhanden?', blank=True, null=True)
  as_hinweis_warnblinklicht_ein = models.BooleanField('Hinweis „Warnblinklicht ein“ vorhanden?', blank=True, null=True)
  bfe_park_and_ride = models.BooleanField('P+R-Parkplatz in Umgebung vorhanden?', blank=True, null=True)
  bfe_fahrradabstellmoeglichkeit = models.BooleanField('Fahrradabstellmöglichkeit in Umgebung vorhanden?', blank=True, null=True)
  bfe_querungshilfe = models.BooleanField('Querungshilfe in Umgebung vorhanden?', blank=True, null=True)
  bfe_fussgaengerueberweg = models.BooleanField('Fußgängerüberweg in Umgebung vorhanden?', blank=True, null=True)
  bfe_seniorenheim = models.BooleanField('Seniorenheim in Umgebung vorhanden?', blank=True, null=True)
  bfe_pflegeeinrichtung = models.BooleanField('Pflegeeinrichtung in Umgebung vorhanden?', blank=True, null=True)
  bfe_medizinische_versorgungseinrichtung = models.BooleanField('Medizinische Versorgungseinrichtung in Umgebung vorhanden?', blank=True, null=True)
  bemerkungen = NullTextField('Bemerkungen', max_length=500, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bearbeiter = models.CharField('Bearbeiter', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"haltestellenkataster_haltestellen'
    verbose_name = 'Haltestellenkataster (Haltestelle)'
    verbose_name_plural = 'Haltestellenkataster (Haltestellen)'
    description = 'Haltestellen im Rahmen des Haltestellenkatasters der Hanse- und Universitätsstadt Rostock'
    list_fields = ['id', 'gemeindeteilanzeige', 'hst_bezeichnung', 'hst_hafas_id', 'hst_bus_bahnsteigbezeichnung', 'bearbeiter']
    list_fields_labels = ['Haltestellennummer', 'Gemeindeteil', 'Haltestellenbezeichnung', 'HAFAS-ID', 'Bus-/Bahnsteigbezeichnung', 'Bearbeiter']
    list_fields_with_number = ['id']
    readonly_fields = ['gemeindeteilanzeige']
    map_feature_tooltip_field = 'hst_bezeichnung'
    geometry_type = 'Point'
    ordering = ['id'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    if self.hst_hafas_id:
      if self.hst_bus_bahnsteigbezeichnung:
        return 'Haltestelle ' + str(self.id) + ' (' + self.hst_bezeichnung + ' – HAFAS-ID ' + self.hst_hafas_id + ' – Bus-/Bahnsteig ' + self.hst_bus_bahnsteigbezeichnung + ')'
      else:
        return 'Haltestelle ' + str(self.id) + ' (' + self.hst_bezeichnung + ' – HAFAS-ID ' + self.hst_hafas_id + ')'
    elif self.hst_bus_bahnsteigbezeichnung:
      return 'Haltestelle ' + str(self.id) + ' (' + self.hst_bezeichnung + ' – Bus-/Bahnsteig ' + self.hst_bus_bahnsteigbezeichnung + ')'
    else:
      return 'Haltestelle ' + str(self.id) + ' (' + self.hst_bezeichnung + ')'


class Haltestellenkataster_Fotos(models.Model):
  id = models.AutoField(primary_key=True)
  parent = models.ForeignKey(Haltestellenkataster_Haltestellen, on_delete=models.CASCADE, db_column='haltestellenkataster_haltestelle', to_field='uuid')
  dateiname_original = models.CharField('Original-Dateiname', default='', max_length=255)
  motiv = models.CharField('Motiv', max_length=255, choices=MOTIVE_HALTESTELLEN)
  aufnahmedatum = models.DateField('Aufnahmedatum')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'haltestellenkataster'), max_length=255)

  class Meta:
    managed = False
    db_table = 'daten\".\"haltestellenkataster_fotos'
    verbose_name = 'Haltestellenkataster (Foto)'
    verbose_name_plural = 'Haltestellenkataster (Fotos)'
    description = 'Fotos im Rahmen des Haltestellenkatasters der Hanse- und Universitätsstadt Rostock'
    list_fields = ['parent', 'motiv', 'aufnahmedatum', 'foto', 'dateiname_original']
    list_fields_with_date = ['aufnahmedatum']
    list_fields_labels = ['zu Haltestelle', 'Motiv', 'Aufnahmedatum', 'Foto', 'Original-Dateiname']
    readonly_fields = ['dateiname_original']
    object_title = 'das Foto'
    foreign_key_label = 'Haltestelle'
    thumbs = True
    multi_foto_field = True
  
  def __str__(self):
    return str(self.parent) + ', Motiv ' + self.motiv + ', mit Aufnahmedatum ' + datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')
 


@receiver(signals.pre_save, sender=Containerstellplaetze)
def containerstellplatz_pre_save_handler(sender, instance, **kwargs):
  # ab hier in Funktion B auslagern
  try:
    old = Containerstellplaetze.objects.get(pk=instance.pk)
    if old and old.foto and old.foto.url:
      instance.original_url = old.foto.url
  except Containerstellplaetze.DoesNotExist:
    pass


@receiver(signals.post_save, sender=Containerstellplaetze)
def containerstellplatz_post_save_handler(sender, instance, **kwargs):
  if instance.foto:
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
    else:
      BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      path = BASE_DIR + instance.foto.url
    rotate_image(path)
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      thumb_path = os.path.dirname(path) + '/thumbs'
      if not os.path.exists(thumb_path):
        os.mkdir(thumb_path)
      thumb_path = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      thumb_image(path, thumb_path)
  elif instance.original_url:
    instance.foto = None
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = settings.MEDIA_ROOT + '/' + instance.original_url[len(settings.MEDIA_URL):]
    else:
      path = instance.original_url
    try:
      os.remove(path)
    except OSError:
      pass
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      thumb = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      try:
        os.remove(thumb)
      except OSError:
        pass


@receiver(signals.post_delete, sender=Containerstellplaetze)
def containerstellplatz_post_delete_handler(sender, instance, **kwargs):
  # ab hier in Funktion A auslagern
  if instance.foto:
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      if settings.MEDIA_ROOT and settings.MEDIA_URL:
        path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
      else:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = BASE_DIR + instance.foto.url
      thumb = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      try:
        os.remove(thumb)
      except OSError:
        pass
    instance.foto.delete(False)


@receiver(signals.post_save, sender=Gutachterfotos)
def gutachterfoto_post_save_handler(sender, instance, **kwargs):
  if instance.foto:
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
    else:
      BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      path = BASE_DIR + instance.foto.url
    rotate_image(path)
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      thumb_path = os.path.dirname(path) + '/thumbs'
      if not os.path.exists(thumb_path):
        os.mkdir(thumb_path)
      thumb_path = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      thumb_image(path, thumb_path)


@receiver(signals.post_delete, sender=Gutachterfotos)
def gutachterfoto_post_delete_handler(sender, instance, **kwargs):
  # ab hier in Funktion A auslagern
  if instance.foto:
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      if settings.MEDIA_ROOT and settings.MEDIA_URL:
        path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
      else:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = BASE_DIR + instance.foto.url
      thumb = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      try:
        os.remove(thumb)
      except OSError:
        pass
    instance.foto.delete(False)


@receiver(signals.pre_save, sender=Haltestellenkataster_Fotos)
def haltestellenkataster_pre_save_handler(sender, instance, **kwargs):
  # ab hier in Funktion B auslagern
  try:
    old = Haltestellenkataster_Fotos.objects.get(pk=instance.pk)
    if old and old.foto and old.foto.name:
      instance.original_url = old.foto.name
  except Haltestellenkataster_Fotos.DoesNotExist:
    pass


@receiver(signals.post_save, sender=Haltestellenkataster_Fotos)
def haltestellenkataster_post_save_handler(sender, instance, **kwargs):
  if instance.foto:
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
    else:
      BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      path = BASE_DIR + instance.foto.url
    rotate_image(path)
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      thumb_path = os.path.dirname(path) + '/thumbs'
      if not os.path.exists(thumb_path):
        os.mkdir(thumb_path)
      thumb_path = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      thumb_image(path, thumb_path)


@receiver(signals.post_delete, sender=Haltestellenkataster_Fotos)
def haltestellenkataster_post_delete_handler(sender, instance, **kwargs):
  if instance.foto:
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      if settings.MEDIA_ROOT and settings.MEDIA_URL:
        path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
      else:
        BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        path = BASE_DIR + instance.foto.url
      thumb = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      try:
        os.remove(thumb)
      except OSError:
        pass
    instance.foto.delete(False)
