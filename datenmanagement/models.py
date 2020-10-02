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
from django.db import connection
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


def delete_photo_after_emptied(sender, instance, created, **kwargs):
  if not instance.foto and not created:
    pre_save_instance = instance._pre_save_instance
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = settings.MEDIA_ROOT + '/' + pre_save_instance.foto.url[len(settings.MEDIA_URL):]
    else:
      BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      path = BASE_DIR + pre_save_instance.foto.url
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs == True:
      thumb = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      try:
        os.remove(thumb)
      except OSError:
        pass
    try:
      os.remove(path)
    except OSError:
      pass


def get_pre_save_instance(sender, instance, **kwargs):
  try:
    instance._pre_save_instance = sender.objects.get(pk=instance.uuid)
  except sender.DoesNotExist:
    instance._pre_save_instance = instance


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


def sequence_id(sequence_name):
  with connection.cursor() as cursor:
    cursor.execute("""SELECT nextval('""" + sequence_name + """')""")
    return cursor.fetchone()[0]


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


class PositiveIntegerMinField(models.PositiveIntegerField):
  def __init__(self, verbose_name=None, name=None, min_value=None, **kwargs):
    self.min_value = min_value
    models.PositiveIntegerField.__init__(self, verbose_name, name, **kwargs)
    
  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value}
    defaults.update(kwargs)
    return super(PositiveIntegerMinField, self).formfield(**defaults)


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

containerstellplaetze_id_regex = r'^[0-9]{2}-[0-9]{2}$'
containerstellplaetze_id_message = 'Die <strong><em>ID</em></strong> muss aus genau zwei Ziffern, gefolgt von genau einem Bindestrich und abermals genau zwei Ziffern bestehen.'
denksteine_nummer_regex = r'^[0-9]+[a-z]*$'
denksteine_nummer_message = 'Die <strong><em>Nummer</em></strong> muss mit einer Ziffer beginnen und mit einer Ziffer oder einem Kleinbuchstaben enden.'
haltestellenkataster_haltestellen_hst_hafas_id_regex = r'^[0-9]{8}$'
haltestellenkataster_haltestellen_hst_hafas_id_message = 'Die <strong><em>HAFAS-ID</em></strong> muss aus genau acht Ziffern bestehen.'
linien_linie_regex = r'^[A-Z0-9]+[A-Z0-9]*$'
linien_linie_message = 'Die <strong><em>Linie</em></strong> muss mit einer Ziffer oder einem Großbuchstaben beginnen, der bzw. dem optional weitere Ziffern und/oder Großbuchstaben folgen können.'
parkscheinautomaten_bewohnerparkgebiet_regex = r'^[A-Z][0-9]$'
parkscheinautomaten_bewohnerparkgebiet_message = 'Das <strong><em>Bewohnerparkgebiet</em></strong> muss aus genau einem Großbuchstaben sowie genau einer Ziffer bestehen.'
parkscheinautomaten_geraetenummer_regex = r'^[0-9]{2}_[0-9]{5}$'
parkscheinautomaten_geraetenummer_message = 'Die <strong><em>Gerätenummer</em></strong> muss aus genau zwei Ziffern, gefolgt von genau einem Unterstrich und abermals genau fünf Ziffern bestehen.'
uvp_vorhaben_registriernummer_bauamt_regex = r'^[0-9]{5}-[0-9]{2}$'
uvp_vorhaben_registriernummer_bauamt_message = 'Die <strong><em>Registriernummer des Bauamtes</em></strong> muss aus genau fünf Ziffern, gefolgt von genau einem Bindestrich und genau zwei Ziffern bestehen.'
zonen_parkscheinautomaten_zone_regex = r'^[A-Z]$'
zonen_parkscheinautomaten_zone_message = 'Die <strong><em>Zone</em></strong> muss aus genau einem Großbuchstaben bestehen.'



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


class Befestigungsart(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  befestigungsart = models.CharField('Befestigungsart', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
     'befestigungsart': 'Befestigungsart'
    }
    ordering = ['befestigungsart'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.befestigungsart


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


class Status(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  status = models.CharField('Status', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
     'status': 'Status'
    }
    ordering = ['status'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.status


class Typ(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  typ = models.CharField('Typ', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
     'typ': 'Typ'
    }
    ordering = ['typ'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.typ



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


# Arten von Fließgewässern

class Arten_Fliessgewaesser(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fliessgewaesser'
    verbose_name = 'Art eines Fließgewässers'
    verbose_name_plural = 'Arten von Fließgewässern'
    description = 'Arten von Fließgewässern'


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


# Ausführungen innerhalb eines Haltestellenkatasters

class Ausfuehrungen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  ausfuehrung = models.CharField('Ausführung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"ausfuehrungen_haltestellenkataster'
    verbose_name = 'Ausführung innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Ausführungen innerhalb eines Haltestellenkatasters'
    description = 'Ausführungen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'ausfuehrung': 'Ausführung'
    }
    ordering = ['ausfuehrung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.ausfuehrung


# Befestigungsarten der Aufstellfläche Bus innerhalb eines Haltestellenkatasters

class Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster(Befestigungsart):
  class Meta(Befestigungsart.Meta):
    db_table = 'codelisten\".\"befestigungsarten_aufstellflaeche_bus_haltestellenkataster'
    verbose_name = 'Befestigungsart der Aufstellfläche Bus innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Befestigungsarten der Aufstellfläche Bus innerhalb eines Haltestellenkatasters'
    description = 'Befestigungsarten der Aufstellfläche Bus innerhalb eines Haltestellenkatasters'


# Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters

class Befestigungsarten_Warteflaeche_Haltestellenkataster(Befestigungsart):
  class Meta(Befestigungsart.Meta):
    db_table = 'codelisten\".\"befestigungsarten_warteflaeche_haltestellenkataster'
    verbose_name = 'Befestigungsart der Wartefläche innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters'
    description = 'Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters'


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


# Typen von Dynamischen Fahrgastinformationssystemen innerhalb eines Haltestellenkatasters

class DFI_Typen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  dfi_typ = models.CharField('DFI-Typ', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"dfi_typen_haltestellenkataster'
    verbose_name = 'Typ eines Dynamischen Fahrgastinformationssystems innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Dynamischen Fahrgastinformationssystemen innerhalb eines Haltestellenkatasters'
    description = 'Typen von Dynamischen Fahrgastinformationssystemen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'dfi_typ': 'DFI-Typ'
    }
    ordering = ['dfi_typ'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.dfi_typ


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


# Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters

class Fahrgastunterstandstypen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  fahrgastunterstandstyp = models.CharField('Fahrgastunterstandstyp', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"fahrgastunterstandstypen_haltestellenkataster'
    verbose_name = 'Typ eines Fahrgastunterstands innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters'
    description = 'Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fahrgastunterstandstyp': 'Fahrgastunterstandstyp'
    }
    ordering = ['fahrgastunterstandstyp'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.fahrgastunterstandstyp


# Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters

class Fahrplanvitrinentypen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  fahrplanvitrinentyp = models.CharField('Fahrplanvitrinentyp', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"fahrplanvitrinentypen_haltestellenkataster'
    verbose_name = 'Typ einer Fahrplanvitrine innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters'
    description = 'Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fahrplanvitrinentyp': 'Fahrplanvitrinentyp'
    }
    ordering = ['fahrplanvitrinentyp'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.fahrplanvitrinentyp


# Fotomotive innerhalb eines Haltestellenkatasters

class Fotomotive_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  fotomotiv = models.CharField('Fotomotiv', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"fotomotive_haltestellenkataster'
    verbose_name = 'Fotomotiv innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Fotomotive innerhalb eines Haltestellenkatasters'
    description = 'Fotomotive innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fotomotiv': 'Fotomotiv'
    }
    ordering = ['fotomotiv'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.fotomotiv


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


# Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH

class Linien(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  linie = models.CharField('Linie', max_length=4, validators=[RegexValidator(regex=linien_linie_regex, message=linien_linie_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"linien'
    verbose_name = 'Linie der Rostocker Straßenbahn AG und/oder der Regionalbus Rostock GmbH'
    verbose_name_plural = 'Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH'
    description = 'Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH'
    list_fields = {
      'linie': 'Linie'
    }
    ordering = ['linie'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.linie


# Masttypen innerhalb eines Haltestellenkatasters

class Masttypen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  masttyp = models.CharField('Masttyp', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"masttypen_haltestellenkataster'
    verbose_name = 'Masttyp innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Masttypen innerhalb eines Haltestellenkatasters'
    description = 'Masttypen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'masttyp': 'Masttyp'
    }
    ordering = ['masttyp'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.masttyp


# Materialien von Denksteinen

class Materialien_Denksteine(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  material = models.CharField('Material', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"materialien_denksteine'
    verbose_name = 'Material eines Denksteins'
    verbose_name_plural = 'Materialien von Denksteinen'
    description = 'Materialien von Denksteinen'
    list_fields = {
     'material': 'Material'
    }
    ordering = ['material'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.material


# Ordnungen von Fließgewässern

class Ordnungen_Fliessgewaesser(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  ordnung = PositiveSmallIntegerMinField('Ordnung', min_value=1)

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"ordnungen_fliessgewaesser'
    verbose_name = 'Ordnung eines Fließgewässers'
    verbose_name_plural = 'Ordnungen von Fließgewässern'
    description = 'Ordnungen von Fließgewässern'
    list_fields = {
      'ordnung': 'Ordnung'
    }
    list_fields_with_number = ['ordnung']
    ordering = ['ordnung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return str(self.ordnung)


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


# Schäden innerhalb eines Haltestellenkatasters

class Schaeden_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  schaden = models.CharField('Schaden', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"schaeden_haltestellenkataster'
    verbose_name = 'Schaden innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Schäden innerhalb eines Haltestellenkatasters'
    description = 'Schäden innerhalb eines Haltestellenkatasters'
    list_fields = {
      'schaden': 'Schaden'
    }
    ordering = ['schaden'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.schaden


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


# Sitzbanktypen innerhalb eines Haltestellenkatasters

class Sitzbanktypen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  sitzbanktyp = models.CharField('Sitzbanktyp', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"sitzbanktypen_haltestellenkataster'
    verbose_name = 'Sitzbanktyp innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Sitzbanktypen innerhalb eines Haltestellenkatasters'
    description = 'Sitzbanktypen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'sitzbanktyp': 'Sitzbanktyp'
    }
    ordering = ['sitzbanktyp'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.sitzbanktyp


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


# Status von Baustellen (geplant)

class Status_Baustellen_geplant(Status):
  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_baustellen_geplant'
    verbose_name = 'Status einer Baustelle (geplant)'
    verbose_name_plural = 'Status von Baustellen (geplant)'
    description = 'Status von Baustellen (geplant)'


# Status von Fotos der Baustellen-Fotodokumentation

class Status_Baustellen_Fotodokumentation_Fotos(Status):
  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_baustellen_fotodokumentation_fotos'
    verbose_name = 'Status eines Fotos der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Status von Fotos der Baustellen-Fotodokumentation'
    description = 'Status von Fotos der Baustellen-Fotodokumentation'


# Typen von Abfallbehältern

class Typen_Abfallbehaelter(Typ):
  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_abfallbehaelter'
    verbose_name = 'Typ eines Abfallbehälters'
    verbose_name_plural = 'Typen von Abfallbehältern'
    description = 'Typen von Abfallbehältern'


# Typen von Haltestellen

class Typen_Haltestellen(Typ):
  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_haltestellen'
    verbose_name = 'Typ einer Haltestelle'
    verbose_name_plural = 'Typen von Haltestellen'
    description = 'Typen von Haltestellen'


# Typen von UVP-Vorhaben

class Typen_UVP_Vorhaben(Typ):
  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_uvp_vorhaben'
    verbose_name = 'Typ eines UVP-Vorhabens'
    verbose_name_plural = 'Typen von UVP-Vorhaben'
    description = 'Typen von UVP-Vorhaben'


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


# Verkehrsmittelklassen

class Verkehrsmittelklassen(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  verkehrsmittelklasse = models.CharField('Verkehrsmittelklasse', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"verkehrsmittelklassen'
    verbose_name = 'Verkehrsmittelklasse'
    verbose_name_plural = 'Verkehrsmittelklassen'
    description = 'Verkehrsmittelklassen'
    list_fields = {
      'verkehrsmittelklasse': 'Verkehrsmittelklasse'
    }
    ordering = ['verkehrsmittelklasse'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.verkehrsmittelklasse


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


# ZH-Typen innerhalb eines Haltestellenkatasters

class ZH_Typen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(primary_key=True, editable=False)
  zh_typ = models.CharField('ZH-Typ', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"zh_typen_haltestellenkataster'
    verbose_name = 'ZH-Typ innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'ZH-Typen innerhalb eines Haltestellenkatasters'
    description = 'ZH-Typen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'zh_typ': 'ZH-Typ'
    }
    ordering = ['zh_typ'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.zh_typ


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
  haltestelle = models.BooleanField('Lage an einer Haltestelle?', blank=True, null=True)
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


# Containerstellplätze

class Containerstellplaetze(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField('Außerbetriebstellung', blank=True, null=True)
  id = models.CharField('ID', max_length=5, blank=True, null=True, validators=[RegexValidator(regex=containerstellplaetze_id_regex, message=containerstellplaetze_id_message)])
  privat = models.BooleanField(' privat?')
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bewirtschafter_grundundboden = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Bewirtschafter Grund und Boden', on_delete=models.SET_NULL, db_column='bewirtschafter_grundundboden', to_field='uuid', related_name='bewirtschafter_grundundboden+', blank=True, null=True)
  bewirtschafter_glas = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Bewirtschafter Glas', on_delete=models.SET_NULL, db_column='bewirtschafter_glas', to_field='uuid', related_name='bewirtschafter_glas+', blank=True, null=True)
  anzahl_glas = PositiveSmallIntegerMinField('Anzahl Glas normal', min_value=1, blank=True, null=True)
  anzahl_glas_unterflur = PositiveSmallIntegerMinField('Anzahl Glas unterflur', min_value=1, blank=True, null=True)
  bewirtschafter_papier = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Bewirtschafter Papier', on_delete=models.SET_NULL, db_column='bewirtschafter_papier', to_field='uuid', related_name='bewirtschafter_papier+', blank=True, null=True)
  anzahl_papier = PositiveSmallIntegerMinField('Anzahl Papier normal', min_value=1, blank=True, null=True)
  anzahl_papier_unterflur = PositiveSmallIntegerMinField('Anzahl Papier unterflur', min_value=1, blank=True, null=True)
  bewirtschafter_altkleider = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Bewirtschafter Altkleider', on_delete=models.SET_NULL, db_column='bewirtschafter_altkleider', to_field='uuid', related_name='bewirtschafter_altkleider+', blank=True, null=True)
  anzahl_altkleider = PositiveSmallIntegerMinField('Anzahl Altkleider', min_value=1, blank=True, null=True)
  inbetriebnahmejahr = PositiveSmallIntegerRangeField('Inbetriebnahmejahr', max_value=current_year(), blank=True, null=True)
  inventarnummer = models.CharField('Inventarnummer Stellplatz', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  inventarnummer_grundundboden = models.CharField('Inventarnummer Grund und Boden', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  inventarnummer_zaun = models.CharField('Inventarnummer Zaun', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  anschaffungswert = models.DecimalField('Anschaffungswert (in €)', max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.'), MaxValueValidator(Decimal('99999.99'), 'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 99.999,99 € betragen.')], blank=True, null=True)
  oeffentliche_widmung = models.BooleanField(' öffentliche Widmung?', blank=True, null=True)
  bga = models.BooleanField('Zuordnung BgA Stellplatz?', blank=True, null=True)
  bga_grundundboden = models.BooleanField('Zuordnung BgA Grund und Boden?', blank=True, null=True)
  bga_zaun = models.BooleanField('Zuordnung BgA Zaun?', blank=True, null=True)
  art_eigentumserwerb = models.CharField('Art des Eigentumserwerbs Stellplatz', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art_eigentumserwerb_zaun = models.CharField('Art des Eigentumserwerbs Zaun', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  vertraege = models.CharField('Verträge', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  winterdienst_a = models.BooleanField('Winterdienst A?', blank=True, null=True)
  winterdienst_b = models.BooleanField('Winterdienst B?', blank=True, null=True)
  winterdienst_c = models.BooleanField('Winterdienst C?', blank=True, null=True)
  flaeche = models.DecimalField('Fläche (in m²)', max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die <strong><em>Fläche</em></strong> muss mindestens 0,01 m² betragen.'), MaxValueValidator(Decimal('999.99'), 'Die <strong><em>Fläche</em></strong> darf höchstens 999,99 m² betragen.')], blank=True, null=True)
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'containerstellplaetze'), max_length=255, blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"containerstellplaetze_hro'
    verbose_name = 'Containerstellplatz'
    verbose_name_plural = 'Containerstellplätze'
    description = 'Containerstellplätze in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Außerbetriebstellung',
      'id': 'ID',
      'privat': 'privat?',
      'bezeichnung': 'Bezeichnung',
      'foto': 'Foto'
    }
    list_fields_with_date = ['deaktiviert']
    readonly_fields = ['deaktiviert']
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'id': 'ID',
      'privat': 'privat?',
      'bezeichnung': 'Bezeichnung'
    }
    geometry_type = 'Point'
    thumbs = True

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Containerstellplaetze, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Containerstellplaetze, self).delete(*args, **kwargs)

signals.pre_save.connect(get_pre_save_instance, sender=Containerstellplaetze)

signals.post_save.connect(photo_post_processing, sender=Containerstellplaetze)

signals.post_save.connect(delete_photo_after_emptied, sender=Containerstellplaetze)

signals.post_save.connect(assign_permissions, sender=Containerstellplaetze)

signals.post_delete.connect(delete_photo, sender=Containerstellplaetze)

signals.post_delete.connect(remove_permissions, sender=Containerstellplaetze)


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


# Fließgewässer

class Fliessgewaesser(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  nummer = models.CharField('Nummer', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art = models.ForeignKey(Arten_Fliessgewaesser, verbose_name='Art', on_delete=models.RESTRICT, db_column='art', to_field='uuid', related_name='arten+')
  ordnung = models.ForeignKey(Ordnungen_Fliessgewaesser, verbose_name='Ordnung', on_delete=models.SET_NULL, db_column='ordnung', to_field='uuid', related_name='ordnungen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  nennweite = PositiveSmallIntegerMinField('Nennweite (in mm)', min_value=50, blank=True, null=True)
  laenge = models.PositiveIntegerField('Länge (in m)', default=0)
  laenge_in_hro = models.PositiveIntegerField('Länge innerhalb Rostocks (in m)', blank=True, null=True)
  geometrie = models.LineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"fliessgewaesser_hro'
    verbose_name = 'Fließgewässer'
    verbose_name_plural = 'Fließgewässer'
    description = 'Fließgewässer in der Hanse- und Universitätsstadt Rostock und Umgebung'
    list_fields = {
      'aktiv': 'aktiv?',
      'nummer': 'Nummer',
      'art': 'Art',
      'ordnung': 'Ordnung',
      'bezeichnung': 'Bezeichnung',
      'laenge': 'Länge (in m)',
      'laenge_in_hro': 'Länge innerhalb Rostocks (in m)'
    }
    list_fields_with_foreign_key = {
      'art': 'art__art',
      'ordnung': 'ordnung__ordnung'
    }
    list_fields_with_number = ['laenge', 'laenge_in_hro']
    readonly_fields = ['laenge', 'laenge_in_hro']
    map_feature_tooltip_field = 'nummer'
    map_filter_fields = {
      'nummer': 'Nummer',
      'art': 'Art',
      'ordnung': 'Ordnung',
      'bezeichnung': 'Bezeichnung'
    }
    map_filter_fields_as_list = ['art', 'ordnung']
    geometry_type = 'LineString'

  def __str__(self):
    return self.nummer + ' [Art: ' + str(self.art) + (', Ordnung: ' + str(self.ordnung) if self.ordnung else '') + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Fliessgewaesser, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Fliessgewaesser, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Fliessgewaesser)

signals.post_delete.connect(remove_permissions, sender=Fliessgewaesser)


# Gutachterfotos

class Gutachterfotos(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bearbeiter = models.CharField('Bearbeiter', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  aufnahmedatum = models.DateField('Aufnahmedatum')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'gutachterfotos'), max_length=255)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"gutachterfotos_hro'
    verbose_name = 'Gutachterfoto'
    verbose_name_plural = 'Gutachterfotos'
    description = 'Gutachterfotos der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bearbeiter': 'Bearbeiter',
      'datum': 'Datum',
      'aufnahmedatum': 'Aufnahmedatum',
      'foto': 'Foto'
    }
    list_fields_with_date = ['datum', 'aufnahmedatum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse__adresse'
    }
    map_feature_tooltip_field = 'datum'
    map_filter_fields = {
      'datum': 'Datum',
      'aufnahmedatum': 'Aufnahmedatum'
    }
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    thumbs = True

  def __str__(self):
    return 'Gutachterfoto mit Aufnahmedatum ' + datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y') + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Gutachterfotos, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Gutachterfotos, self).delete(*args, **kwargs)

signals.post_save.connect(photo_post_processing, sender=Gutachterfotos)

signals.post_save.connect(assign_permissions, sender=Gutachterfotos)

signals.post_delete.connect(delete_photo, sender=Gutachterfotos)

signals.post_delete.connect(remove_permissions, sender=Gutachterfotos)


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


# Haltestellen des Haltestellenkatasters

class Haltestellenkataster_Haltestellen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField('Außerbetriebstellung', blank=True, null=True)
  id = models.PositiveIntegerField('ID', default=sequence_id('fachdaten.haltestellenkataster_haltestellen_hro_id_seq'))
  hst_bezeichnung = models.CharField('Haltestellenbezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_hafas_id = models.CharField('HAFAS-ID', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=haltestellenkataster_haltestellen_hst_hafas_id_regex, message=haltestellenkataster_haltestellen_hst_hafas_id_message)])
  hst_bus_bahnsteigbezeichnung = models.CharField('Bus-/Bahnsteigbezeichnung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_richtung = models.CharField('Richtungsinformation', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_kategorie = models.CharField('Haltestellenkategorie', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_linien = ChoiceArrayField(models.CharField(' bedienende Linie(n)', max_length=4, choices=()), verbose_name=' bedienende Linie(n)', blank=True, null=True)
  hst_rsag = models.BooleanField(' bedient durch Rostocker Straßenbahn AG?', blank=True, null=True)
  hst_rebus = models.BooleanField(' bedient durch rebus Regionalbus Rostock GmbH?', blank=True, null=True)
  hst_nur_ausstieg = models.BooleanField(' nur Ausstieg?', blank=True, null=True)
  hst_nur_einstieg = models.BooleanField(' nur Einstieg?', blank=True, null=True)
  hst_verkehrsmittelklassen = ChoiceArrayField(models.CharField('Verkehrsmittelklasse(n)', max_length=255, choices=()), verbose_name='Verkehrsmittelklasse(n)')
  hst_fahrgastzahl = PositiveIntegerMinField(' durchschnittliche Fahrgastzahl', min_value=1, blank=True, null=True)
  bau_typ = models.ForeignKey(Typen_Haltestellen, verbose_name='Typ', on_delete=models.SET_NULL, db_column='bau_typ', to_field='uuid', related_name='bau_typen+', blank=True, null=True)
  bau_wartebereich_laenge = models.DecimalField('Länge des Wartebereichs (in m)', max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der <strong><em>Wartebereich</em></strong> muss mindestens 0,01 m lang sein.'), MaxValueValidator(Decimal('999.99'), 'Der <strong><em>Wartebereich</em></strong> darf höchstens 999,99 m lang sein.')], blank=True, null=True)
  bau_wartebereich_breite = models.DecimalField('Breite des Wartebereichs (in m)', max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der <strong><em>Wartebereich</em></strong> muss mindestens 0,01 m breit sein.'), MaxValueValidator(Decimal('999.99'), 'Der <strong><em>Wartebereich</em></strong> darf höchstens 999,99 m breit sein.')], blank=True, null=True)
  bau_befestigungsart_aufstellflaeche_bus = models.ForeignKey(Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster, verbose_name='Befestigungsart der Aufstellfläche Bus', on_delete=models.SET_NULL, db_column='bau_befestigungsart_aufstellflaeche_bus', to_field='uuid', related_name='bau_befestigungsarten_aufstellflaeche_bus+', blank=True, null=True)
  bau_zustand_aufstellflaeche_bus = models.ForeignKey(Schaeden_Haltestellenkataster, verbose_name='Zustand der Aufstellfläche Bus', on_delete=models.SET_NULL, db_column='bau_zustand_aufstellflaeche_bus', to_field='uuid', related_name='bau_zustaende_aufstellflaeche_bus+', blank=True, null=True)
  bau_befestigungsart_warteflaeche = models.ForeignKey(Befestigungsarten_Warteflaeche_Haltestellenkataster, verbose_name='Befestigungsart der Wartefläche', on_delete=models.SET_NULL, db_column='bau_befestigungsart_warteflaeche', to_field='uuid', related_name='bau_befestigungsarten_warteflaeche+', blank=True, null=True)
  bau_befestigungsart_warteflaeche = models.ForeignKey(Schaeden_Haltestellenkataster, verbose_name='Zustand der Wartefläche', on_delete=models.SET_NULL, db_column='bau_befestigungsart_warteflaeche', to_field='uuid', related_name='bau_befestigungsarten_warteflaeche+', blank=True, null=True)
  bf_einstieg = models.BooleanField(' barrierefreier Einstieg vorhanden?', blank=True, null=True)
  bf_zu_abgaenge = models.BooleanField(' barrierefreie Zu- und Abgänge vorhanden?', blank=True, null=True)
  bf_bewegungsraum = models.BooleanField(' barrierefreier Bewegungsraum vorhanden?', blank=True, null=True)
  tl_auffindestreifen = models.BooleanField('Taktiles Leitsystem: Auffindestreifen vorhanden?', blank=True, null=True)
  tl_auffindestreifen_ausfuehrung = models.ForeignKey(Ausfuehrungen_Haltestellenkataster, verbose_name='Taktiles Leitsystem: Ausführung Auffindestreifen', on_delete=models.SET_NULL, db_column='tl_auffindestreifen_ausfuehrung', to_field='uuid', related_name='tl_auffindestreifen_ausfuehrungen+', blank=True, null=True)
  tl_auffindestreifen_breite = PositiveIntegerMinField('Taktiles Leitsystem: Breite des Auffindestreifens (in cm)', min_value=1, blank=True, null=True)
  tl_einstiegsfeld = models.BooleanField('Taktiles Leitsystem: Einstiegsfeld vorhanden?', blank=True, null=True)
  tl_einstiegsfeld_ausfuehrung = models.ForeignKey(Ausfuehrungen_Haltestellenkataster, verbose_name='Taktiles Leitsystem: Ausführung Einstiegsfeld', on_delete=models.SET_NULL, db_column='tl_einstiegsfeld_ausfuehrung', to_field='uuid', related_name='tl_einstiegsfeld_ausfuehrungen+', blank=True, null=True)
  tl_einstiegsfeld_breite = PositiveIntegerMinField('Taktiles Leitsystem: Breite des Einstiegsfelds (in cm)', min_value=1, blank=True, null=True)
  tl_leitstreifen = models.BooleanField('Taktiles Leitsystem: Leitstreifen vorhanden?', blank=True, null=True)
  tl_leitstreifen_ausfuehrung = models.ForeignKey(Ausfuehrungen_Haltestellenkataster, verbose_name='Taktiles Leitsystem: Ausführung Leitstreifen', on_delete=models.SET_NULL, db_column='tl_leitstreifen_ausfuehrung', to_field='uuid', related_name='tl_leitstreifen_ausfuehrungen+', blank=True, null=True)
  tl_leitstreifen_laenge = PositiveIntegerMinField('Taktiles Leitsystem: Länge des Leitstreifens (in cm)', min_value=1, blank=True, null=True)
  tl_aufmerksamkeitsfeld = models.BooleanField('Aufmerksamkeitsfeld (1. Tür) vorhanden?', blank=True, null=True)
  tl_bahnsteigkante_visuell = models.BooleanField('Bahnsteigkante visuell erkennbar?', blank=True, null=True)
  tl_bahnsteigkante_taktil = models.BooleanField('Bahnsteigkante taktil erkennbar?', blank=True, null=True)
  as_zh_typ = models.ForeignKey(ZH_Typen_Haltestellenkataster, verbose_name='ZH-Typ', on_delete=models.SET_NULL, db_column='as_zh_typ', to_field='uuid', related_name='as_zh_typen+', blank=True, null=True)
  as_h_mast = models.BooleanField('Mast vorhanden?', blank=True, null=True)
  as_h_masttyp = models.ForeignKey(Masttypen_Haltestellenkataster, verbose_name='Masttyp', on_delete=models.SET_NULL, db_column='as_h_masttyp', to_field='uuid', related_name='as_h_masttypen+', blank=True, null=True)
  as_papierkorb = models.BooleanField('Papierkorb vorhanden?', blank=True, null=True)
  as_fahrgastunterstand = models.BooleanField('Fahrgastunterstand vorhanden?', blank=True, null=True)
  as_fahrgastunterstandstyp = models.ForeignKey(Fahrgastunterstandstypen_Haltestellenkataster, verbose_name='Typ des Fahrgastunterstand', on_delete=models.SET_NULL, db_column='as_fahrgastunterstandstyp', to_field='uuid', related_name='as_fahrgastunterstandstypen+', blank=True, null=True)
  as_sitzbank_mit_armlehne = models.BooleanField('Sitzbank mit Armlehne vorhanden?', blank=True, null=True)
  as_sitzbank_ohne_armlehne = models.BooleanField('Sitzbank ohne Armlehne vorhanden?', blank=True, null=True)
  as_sitzbanktyp = models.ForeignKey(Sitzbanktypen_Haltestellenkataster, verbose_name='Typ der Sitzbank', on_delete=models.SET_NULL, db_column='as_sitzbanktyp', to_field='uuid', related_name='as_sitzbanktypen+', blank=True, null=True)
  as_gelaender = models.BooleanField('Geländer vorhanden?', blank=True, null=True)
  as_fahrplanvitrine = models.BooleanField('Fahrplanvitrine vorhanden?', blank=True, null=True)
  as_fahrplanvitrinentyp = models.ForeignKey(Fahrplanvitrinentypen_Haltestellenkataster, verbose_name='Typ der Fahrplanvitrine', on_delete=models.SET_NULL, db_column='as_fahrplanvitrinentyp', to_field='uuid', related_name='as_fahrplanvitrinentypen+', blank=True, null=True)
  as_tarifinformation = models.BooleanField('Tarifinformation vorhanden?', blank=True, null=True)
  as_liniennetzplan = models.BooleanField('Liniennetzplan vorhanden?', blank=True, null=True)
  as_fahrplan = models.BooleanField('Fahrplan vorhanden?', blank=True, null=True)
  as_fahrausweisautomat = models.BooleanField('Fahrausweisautomat vorhanden?', blank=True, null=True)
  as_lautsprecher = models.BooleanField('Lautsprecher vorhanden?', blank=True, null=True)
  as_dfi = models.BooleanField('Dynamisches Fahrgastinformationssystem vorhanden?', blank=True, null=True)
  as_dfi_typ = models.ForeignKey(DFI_Typen_Haltestellenkataster, verbose_name='Typ des Dynamischen Fahrgastinformationssystems', on_delete=models.SET_NULL, db_column='as_dfi_typ', to_field='uuid', related_name='as_dfi_typen+', blank=True, null=True)
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
  bearbeiter = models.CharField('Bearbeiter', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkungen = NullTextField('Bemerkungen', max_length=500, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"haltestellenkataster_haltestellen_hro'
    verbose_name = 'Haltestelle des Haltestellenkatasters'
    verbose_name_plural = 'Haltestellen des Haltestellenkatasters'
    description = 'Haltestellen des Haltestellenkatasters der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'hst_linien': 'Linien',
      'hst_verkehrsmittelklassen': 'Verkehrsmittelklassen'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Außerbetriebstellung',
      'id': 'ID',
      'hst_bezeichnung': 'Haltestellenbezeichnung',
      'hst_hafas_id': 'HAFAS-ID',
      'hst_bus_bahnsteigbezeichnung': 'Bus-/Bahnsteigbezeichnung'
    }
    list_fields_with_number = ['id']
    readonly_fields = ['id']
    map_feature_tooltip_field = 'hst_bezeichnung'
    geometry_type = 'Point'
    ordering = ['id'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.hst_bezeichnung + ' [ID: ' + str(self.id) + (', HAFAS-ID: ' + self.hst_hafas_id if self.hst_hafas_id else '') + (', Bus-/Bahnsteig: ' + self.hst_bus_bahnsteigbezeichnung if self.hst_bus_bahnsteigbezeichnung else '') + ']'

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Haltestellenkataster_Haltestellen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Haltestellenkataster_Haltestellen, self).delete(*args, **kwargs)

signals.post_save.connect(assign_permissions, sender=Haltestellenkataster_Haltestellen)

signals.post_delete.connect(remove_permissions, sender=Haltestellenkataster_Haltestellen)


# Fotos des Haltestellenkatasters

class Haltestellenkataster_Fotos(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  haltestellenkataster_haltestelle = models.ForeignKey(Haltestellenkataster_Haltestellen, verbose_name='Haltestelle', on_delete=models.CASCADE, db_column='haltestellenkataster_haltestelle', to_field='uuid', related_name='haltestellenkataster_haltestellen+')
  motiv = models.ForeignKey(Fotomotive_Haltestellenkataster, verbose_name='Motiv', on_delete=models.RESTRICT, db_column='motiv', to_field='uuid', related_name='motive+')
  aufnahmedatum = models.DateField('Aufnahmedatum', default=date.today)
  dateiname_original = models.CharField('Original-Dateiname', max_length=255, default='ohne')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'haltestellenkataster'), max_length=255)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"haltestellenkataster_fotos_hro'
    verbose_name = 'Foto des Haltestellenkatasters'
    verbose_name_plural = 'Fotos des Haltestellenkatasters'
    description = 'Fotos des Haltestellenkatasters der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'haltestellenkataster_haltestelle': 'Haltestelle',
      'motiv': 'Motiv',
      'aufnahmedatum': 'Aufnahmedatum',
      'dateiname_original': 'Original-Dateiname',
      'foto': 'Foto'
    }
    readonly_fields = ['dateiname_original']
    list_fields_with_date = ['aufnahmedatum']
    list_fields_with_foreign_key = {
      'haltestellenkataster_haltestelle': 'haltestellenkataster_haltestelle__id',
      'motiv': 'motiv__fotomotiv'
    }
    object_title = 'das Foto'
    foreign_key_label = 'Haltestelle'
    thumbs = True
    multi_foto_field = True
  
  def __str__(self):
    return str(self.haltestellenkataster_haltestelle) + ' mit Motiv ' + str(self.motiv) + ' und Aufnahmedatum ' + datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')

  def save(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Haltestellenkataster_Fotos, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    self.current_authenticated_user = get_current_authenticated_user()
    super(Haltestellenkataster_Fotos, self).delete(*args, **kwargs)

signals.post_save.connect(photo_post_processing, sender=Haltestellenkataster_Fotos)

signals.post_save.connect(assign_permissions, sender=Haltestellenkataster_Fotos)

signals.post_delete.connect(delete_photo, sender=Haltestellenkataster_Fotos)

signals.post_delete.connect(remove_permissions, sender=Haltestellenkataster_Fotos)


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
