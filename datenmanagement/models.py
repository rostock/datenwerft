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
from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
from django.db.models import options
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator, RegexValidator, URLValidator
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text
from PIL import Image, ExifTags



#
# eigene Funktionen
#

def current_year():
  return int(date.today().year)


def path_and_rename(path):
  def wrapper(instance, filename):
    if hasattr(instance, 'dateiname_original'):
      instance.dateiname_original = filename
    ext = filename.split('.')[-1]
    if hasattr(instance, 'uuid'):
      filename = '{0}.{1}'.format(str(instance.uuid), ext.lower())
    elif hasattr(instance, 'original_url'):
      filename = instance.original_url.split('/')[-1]
    elif hasattr(instance, 'parent'):
      filename = '{0}_{1}.{2}'.format(str(instance.parent.uuid), get_random_string(length=8), ext.lower())
    else:
      filename = '{0}.{1}'.format(str(uuid.uuid4()), ext.lower())
    return os.path.join(path, filename)
  return wrapper


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
  
  'codelist',                           # optional ; Boolean        ; Handelt es sich um eine Codeliste, die dann für normale Benutzer in der Liste der verfügbaren Datenthemen nicht auftaucht (True)?
  'description',                        # Pflicht  ; Text           ; Beschreibung bzw. Langtitel des Datenthemas
  'choices_models_for_choices_fields',  # optional ; Textdictionary ; Namen der Felder (als Keys), denen Modelle (als Values) zugewiesen sind, die zur Befüllung entsprechender Auswahllisten herangezogen werden sollen
  'list_fields',                        # Pflicht  ; Textdictionary ; Namen der Felder (als Keys), die in genau dieser Reihenfolge in der Tabelle der Listenansicht als Spalten auftreten sollen, mit ihren Labels (als Values)
  'list_fields_with_number',            # optional ; Textliste      ; Liste mit den Namen der Felder aus list_fields, deren Werte von einem numerischen Datentyp sind
  'list_fields_with_date',              # optional ; Textliste      ; Liste mit den Namen der Felder aus list_fields, deren Werte vom Datentyp Datum sind
  'list_fields_with_foreign_key',       # optional ; Textdictionary ; Namen der Felder (als Keys), die für die Tabelle der Listenansicht in Namen von Fremdschlüsselfeldern (als Values) umgewandelt werden sollen, damit sie in der jeweils referenzierten Tabelle auch gefunden werden
  'highlight_flag',                     # optional ; Text           ; Name des Boolean-Feldes, dessen Wert als Flag zum Highlighten entsprechender Zeilen herangezogen werden soll
  'readonly_fields',                    # optional ; Textliste      ; Namen der Felder, die in der Hinzufügen-/Änderungsansicht nur lesbar erscheinen sollen
  'object_title',                       # optional ; Text           ; Textbaustein für die Löschansicht (relevant nur bei Modellen mit Fremdschlüssel)
  'foreign_key_label',                  # optional ; Text           ; Titel des Feldes mit dem Fremdschlüssel (relevant nur bei Modellen mit Fremdschlüssel)
  'map_feature_tooltip_field',          # optional ; Text           ; Name des Feldes, dessen Werte in der Kartenansicht als Tooltip der Kartenobjekte angezeigt werden sollen
  'map_feature_tooltip_fields',         # optional ; Textliste      ; Namen der Felder, deren Werte in genau dieser Reihenfolge jeweils getrennt durch ein Leerzeichen zusammengefügt werden sollen, damit das Ergebnis in der Kartenansicht als Tooltip der Kartenobjekte angezeigt werden kann
  'map_rangefilter_fields',             # optional ; Textdictionary ; Namen der Felder (als Keys), die in genau dieser Reihenfolge in der Kartenansicht als Intervallfilter auftreten sollen, mit ihren Titeln (als Values) – Achtung: Verarbeitung immer paarweise!
  'map_filter_fields',                  # optional ; Textdictionary ; Namen der Felder (als Keys), die in genau dieser Reihenfolge in der Kartenansicht als Filter auftreten sollen, mit ihren Titeln (als Values)
  'map_filter_fields_as_list',          # optional ; Textliste      ; Namen der Felder aus map_filter_fields, die als Listenfilter auftreten sollen
  'map_filter_hide_initial',            # optional ; Textdictionary ; Name des Feldes (als Key), dessen bestimmter Wert (als Value) dazu führen soll, Objekte initial nicht auf der Karte erscheinen, die in diesem Feld genau diesen bestimmten Wert aufweisen
  'address_type',                       # optional ; Text           ; Typ des Adressenbezugs: Adresse (Adresse) oder Straße (Straße)
  'address_mandatory',                  # optional ; Boolean        ; Soll die Adresse oder die Straße (je nach Typ des Adressenbezugs) eine Pflichtangabe sein (True)?
  'geometry_type',                      # optional ; Text           ; Geometrietyp
  'thumbs',                             # optional ; Boolean        ; Sollen Thumbnails aus den hochgeladenen Fotos erzeugt werden (True)?
  'multi_foto_field',                   # optional ; Boolean        ; Sollen mehrere Fotos hochgeladen werden können (True)? Es werden dann automatisch mehrere Datensätze erstellt, und zwar jeweils einer pro Foto. Achtung: Es muss bei Verwendung dieser Option ein Pflichtfeld mit Namen foto existieren!
  'group_with_users_for_choice_field',  # optional ; Text           ; Name der Gruppe von Benutzern, die für das Feld Ansprechpartner/Bearbeiter in einer entsprechenden Auswahlliste genutzt werden sollen
  'admin_group'                         # optional ; Text           ; Name der Gruppe von Benutzern, die als Admin-Gruppe für dieses Datenthema gelten soll
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
doppelleerzeichen_regex = r'^(?!.*  ).*$'
doppelleerzeichen_message = 'Der Text darf keine doppelten Leerzeichen enthalten.'
gravis_regex = r'^(?!.*`).*$'
gravis_message = 'Der Text darf keine Gravis (`) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.'
bindestrich_leerzeichen_regex = r'^(?!.*- ).*$'
bindestrich_leerzeichen_message = 'Im Text darf nach einen Bindestrich kein Leerzeichen stehen.'
leerzeichen_bindestrich_regex = r'^(?!.* -).*$'
leerzeichen_bindestrich_message = 'Im Text darf vor einem Bindestrich kein Leerzeichen stehen.'


# speziell

geraetenummer_regex = r'^[0-9]{2}_[0-9]{5}$'
geraetenummer_message = 'Die Gerätenummer muss aus genau zwei Ziffern, gefolgt von genau einem Unterstrich und abermals genau fünf Ziffern bestehen.'
hafas_id_regex = r'^[0-9]{8}$'
hafas_id_message = 'Die HAFAS-ID muss aus genau acht Ziffern bestehen.'
id_containerstellplatz_regex = r'^[0-9]{2}-[0-9]{2}$'
id_containerstellplatz_message = 'Die ID des Containerstellplatzes muss aus genau zwei Ziffern, gefolgt von genau einem Bindestrich und abermals genau zwei Ziffern bestehen.'
inventarnummer_regex = r'^[0-9]{8}$'
inventarnummer_message = 'Die Inventarnummer muss aus genau acht Ziffern bestehen.'
postleitzahl_regex = r'^[0-9]{5}$'
postleitzahl_message = 'Eine Postleitzahl muss aus genau fünf Ziffern bestehen.'
registriernummer_bauamt_regex = r'^[0-9]{5}-[0-9]{2}$'
registriernummer_bauamt_message = 'Die Registriernummer des Bauamtes muss aus genau fünf Ziffern, gefolgt von genau einem Bindestrich und genau zwei Ziffern bestehen.'
rufnummer_regex = r'^\+49 [1-9][0-9]{1,5} [0-9]{1,13}$'
rufnummer_message = 'Die Schreibweise von Rufnummern muss der Empfehlung E.123 der Internationalen Fernmeldeunion entsprechen und daher folgendes Format aufweisen: +49 381 3816256'
email_message = 'Die E-Mail-Adresse muss syntaktisch korrekt sein und daher folgendes Format aufweisen: abc-123.098_zyx@xyz-567.ghi.abc'
url_message = 'Die Adresse der Website muss syntaktisch korrekt sein und daher folgendes Format aufweisen: http[s]://abc-123.098_zyx.xyz-567/ghi/abc'

















#
# LEGACY
#

ANBIETER_CARSHARING = (
  ('Flinkster (Deutsche Bahn AG)', 'Flinkster (Deutsche Bahn AG)'),
  ('Greenwheels GmbH', 'Greenwheels GmbH'),
  ('YourCar Rostock GmbH', 'YourCar Rostock GmbH'),
)

ANGEBOTE_MOBILPUNKTE = (
  ('Bus', 'Bus'),
  ('Carsharing', 'Carsharing'),
  ('E-Laden', 'E-Laden'),
  ('Fahrradparken', 'Fahrradparken'),
  ('Fahrradreparaturset', 'Fahrradreparaturset'),
  ('Lastenradverleih', 'Lastenradverleih'),
  ('Straßenbahn', 'Straßenbahn'),
)

ART_BAUDENKMALE_DENKMALBEREICHE = (
  ('bewegliches Denkmal', 'bewegliches Denkmal'),
  ('Denkmalbereich', 'Denkmalbereich'),
  ('Einzeldenkmal', 'Einzeldenkmal'),
)

ART_FAIRTRADE = (
  ('Bildungsträger', 'Bildungsträger'),
  ('Einzelhandel', 'Einzelhandel'),
  ('Gastronomie', 'Gastronomie'),
  ('Kirchengemeinde', 'Kirchengemeinde'),
  ('Schulweltladen', 'Schulweltladen'),
)

ART_FLIESSGEWAESSER = (
  ('Durchlass', 'Durchlass'),
  ('offen', 'offen'),
  ('Rohrleitung', 'Rohrleitung'),
)

ART_HUNDETOILETTE = (
  ('Beutelspender', 'Beutelspender'),
  ('Hundetoilette', 'Hundetoilette'),
)

ART_MELDEDIENST_FLAECHENHAFT = (
  ('Nutzungsart', 'Nutzungsart'),
  ('Topographie', 'Topographie'),
)

ART_MELDEDIENST_PUNKTHAFT = (
  ('Abriss', 'Abriss'),
  ('Gebäude', 'Gebäude'),
)

ART_PARKMOEGLICHKEITEN = (
  ('Parkhaus', 'Parkhaus'),
  ('Parkplatz', 'Parkplatz'),
  ('Tiefgarage', 'Tiefgarage'),
)

ART_PFLEGEEINRICHTUNGEN = (
  ('Ambulanter Pflegedienst', 'Ambulanter Pflegedienst'),
  ('Betreutes Wohnen', 'Betreutes Wohnen'),
  ('Kurzzeitpflegeeinrichtung', 'Kurzzeitpflegeeinrichtung'),
  ('Nachtpflegeeinrichtung', 'Nachtpflegeeinrichtung'),
  ('Tagespflegeeinrichtung', 'Tagespflegeeinrichtung'),
  ('Verhinderungspflegeeinrichtung', 'Verhinderungspflegeeinrichtung'),
  ('Vollstationäre Pflegeeinrichtung', 'Vollstationäre Pflegeeinrichtung'),
)

ART_UVP_VORPRUEFUNG = (
  ('allgemeine Vorprüfung', 'allgemeine Vorprüfung'),
  ('standortbezogene Vorprüfung', 'standortbezogene Vorprüfung'),
)

ART_VORGANG_UVP_VORHABEN = (
  ('Bauantrag', 'Bauantrag'),
  ('externe Genehmigungsplanung', 'externe Genehmigungsplanung'),
  ('Genehmigungsplanung der Hanse- und Universitätsstadt Rostock', 'Genehmigungsplanung der Hanse- und Universitätsstadt Rostock'),
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

BETRIEBSART_LADESTATIONEN_ELEKTROFAHRZEUGE = (
  ('halböffentlich', 'halböffentlich'),
  ('öffentlich', 'öffentlich'),
  ('privat', 'privat'),
)

BEWIRTSCHAFTER_HUNDETOILETTE = (
  (73, 'Amt für Umwelt- und Klimaschutz'),
  (87, 'Tourismuszentrale Rostock und Warnemünde'),
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

E_ANSCHLUSS_PARKSCHEINAUTOMATEN_PARKSCHEINAUTOMATEN = (
  ('Dauerstrom', 'Dauerstrom'),
  ('Solarpanel', 'Solarpanel'),
  ('Straßenbeleuchtung', 'Straßenbeleuchtung'),
)

EINHEIT_PARKDAUER_PARKSCHEINAUTOMATEN_TARIFE = (
  ('min', 'Minuten'),
  ('h', 'Stunden'),
  ('d', 'Tage'),
)

ERGEBNIS_UVP_VORPRUEFUNG = (
  ('in Bearbeitung', 'in Bearbeitung'),
  ('UVP-Pflicht', 'UVP-Pflicht'),
  ('keine UVP-Pflicht', 'keine UVP-Pflicht'),
  ('freiwillige UVP', 'freiwillige UVP'),
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

GEBUEHRENSCHRITTE_PARKSCHEINAUTOMATEN_TARIFE = (
  ('2 min = 0,10 €', '2 min = 0,10 €'),
  ('3 min = 0,10 €', '3 min = 0,10 €'),
  ('4 min = 0,10 €', '4 min = 0,10 €'),
  ('6 min = 0,10 €', '6 min = 0,10 €'),
  ('6 min = 0,50 €', '6 min = 0,50 €'),
  ('10 min = 0,10 €', '10 min = 0,10 €'),
  ('12 min = 0,10 €', '12 min = 0,10 €'),
)

GENEHMIGUNGSBEHOERDE_UVP_VORHABEN = (
  ('Hafen- und Seemannsamt der Hanse- und Universitätsstadt Rostock', 'Hafen- und Seemannsamt der Hanse- und Universitätsstadt Rostock'),
  ('Ministerium für Energie, Infrastruktur und Digitalisierung Mecklenburg-Vorpommern', 'Ministerium für Energie, Infrastruktur und Digitalisierung Mecklenburg-Vorpommern'),
  ('Staatliches Amt für Landwirtschaft und Umwelt Mittleres Mecklenburg', 'Staatliches Amt für Landwirtschaft und Umwelt Mittleres Mecklenburg'),
  ('Tiefbauamt der Hanse- und Universitätsstadt Rostock', 'Tiefbauamt der Hanse- und Universitätsstadt Rostock'),
  ('Untere Bauaufsichtsbehörde der Hanse- und Universitätsstadt Rostock', 'Untere Bauaufsichtsbehörde der Hanse- und Universitätsstadt Rostock'),
  ('Untere Wasserbehörde der Hanse- und Universitätsstadt Rostock', 'Untere Wasserbehörde der Hanse- und Universitätsstadt Rostock'),
)

KLASSEN_VEREINE = (
  ('Arbeit', 'Arbeit'),
  ('Bildung und Wissenschaft', 'Bildung und Wissenschaft'),
  ('Denkmalpflege', 'Denkmalpflege'),
  ('Gesundheit', 'Gesundheit'),
  ('Gewerbe', 'Gewerbe'),
  ('Geschichte', 'Geschichte'),
  ('Hilfe', 'Hilfe'),
  ('Familie', 'Familie'),
  ('Freizeit', 'Freizeit'),
  ('Interessenvertretung', 'Interessenvertretung'),
  ('Kinder und Jugend', 'Kinder und Jugend'),
  ('Kunst und Kultur', 'Kunst und Kultur'),
  ('Militär', 'Militär'),
  ('Senioren', 'Senioren'),
  ('Selbsthilfe', 'Selbsthilfe'),
  ('Sport', 'Sport'),
  ('Tiere', 'Tiere'),
  ('Tradition', 'Tradition'),
  ('Umwelt', 'Umwelt'),
  ('Verbraucher', 'Verbraucher'),
)

LADEKARTEN_LADESTATIONEN_ELEKTROFAHRZEUGE = (
  ('ADAC e-Charge', 'ADAC e-Charge'),
  ('beliebige RFID-Ladekarten', 'beliebige RFID-Ladekarten'),
  ('EinfachStromLaden', 'EinfachStromLaden'),
  ('EnBW mobility+', 'EnBW mobility+'),
  ('EWE', 'EWE'),
  ('GET CHARGE', 'GET CHARGE'),
  ('HAMBURG ENERGIE', 'HAMBURG ENERGIE'),
  ('LeasePlan', 'LeasePlan'),
  ('ohne Authentifizierung', 'ohne Authentifizierung'),
  ('Plugsurfing', 'Plugsurfing'),
  ('Shell Recharge', 'Shell Recharge'),
  ('SMATRICS NET', 'SMATRICS NET'),
  ('Spontanladen', 'Spontanladen'),
  ('Stadtwerke Rostock', 'Stadtwerke Rostock'),
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

MATERIAL_DENKSTEINE = (
  ('Metall', 'Metall'),
  ('Stein', 'Stein'),
)

MOTIVE_HALTESTELLEN = (
  ('Mast', 'Mast'),
  ('Wartebereich von Stirnseite', 'Wartebereich von Stirnseite'),
  ('Wartebereich von vorne', 'Wartebereich von vorne'),
)

RECHTSGRUNDLAGE_UVP_VORHABEN = (
  ('Gesetz über die Umweltverträglichkeitsprüfung (UVPG)', 'Gesetz über die Umweltverträglichkeitsprüfung (UVPG)'),
  ('Gesetz über die Umweltverträglichkeitsprüfung in Mecklenburg-Vorpommern (LUVPG M-V)', 'Gesetz über die Umweltverträglichkeitsprüfung in Mecklenburg-Vorpommern (LUVPG M-V)'),
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

STATUS_BAUSTELLEN_FOTODOKUMENTATION = (
  ('vor Baumaßnahme', 'vor Baumaßnahme'),
  ('während Baumaßnahme', 'während Baumaßnahme'),
  ('nach Baumaßnahme', 'nach Baumaßnahme'),
)

TITEL_DENKSTEINE = (
  ('Dr.', 'Dr.'),
  ('Prof.', 'Prof.'),
  ('Prof. Dr.', 'Prof. Dr.'),
)

TYP_HALTESTELLEN = (
  ('Bushaltestelle (am Fahrbahnrand)', 'Bushaltestelle (am Fahrbahnrand)'),
  ('Bushaltestelle (Busbucht)', 'Bushaltestelle (Busbucht)'),
  ('Bushaltestelle (Buskap)', 'Bushaltestelle (Buskap)'),
  ('Doppelhaltestelle', 'Doppelhaltestelle'),
  ('Kombihaltestelle', 'Kombihaltestelle'),
  ('Straßenbahnhaltestelle', 'Straßenbahnhaltestelle'),
)

TYP_UVP_VORHABEN = (
  ('Nr. 13.12', 'Nr. 13.12'),
  ('Nr. 13.18', 'Nr. 13.18'),
  ('Nr. 13.18.1', 'Nr. 13.18.1'),
  ('Nr. 13.18.2', 'Nr. 13.18.2'),
  ('Nr. 23', 'Nr. 23'),
  ('Nr. 30', 'Nr. 30'),
)

VERBUND_LADESTATIONEN_ELEKTROFAHRZEUGE = (
  ('Allego', 'Allego'),
  ('E.ON', 'E.ON'),
  ('IKEA', 'IKEA'),
  ('NewMotion', 'NewMotion'),
  ('Stadtwerke Rostock', 'Stadtwerke Rostock'),
  ('StromTicket', 'StromTicket'),
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

ZONE_PARKSCHEINAUTOMATEN_PARKSCHEINAUTOMATEN = (
  ('A', 'A'),
  ('B', 'B'),
  ('C', 'C'),
  ('D', 'D'),
  ('W', 'W'),
  ('X', 'X'),
)

ZUGELASSENE_MUENZEN_PARKSCHEINAUTOMATEN_TARIFE = (
  ('0,10 € – 1,00 €', '0,10 € – 1,00 €'),
  ('0,10 € – 2,00 €', '0,10 € – 2,00 €'),
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

# Arten von Feuerwachen

class Arten_Feuerwachen(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_feuerwachen'
    verbose_name = 'Art einer Feuerwache'
    verbose_name_plural = 'Arten von Feuerwachen'
    description = 'Arten von Feuerwachen'


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


# Schlagwörter für Bildungsträger

class Schlagwoerter_Bildungstraeger(Schlagwort):
  class Meta(Schlagwort.Meta):
    db_table = 'codelisten\".\"schlagwoerter_bildungstraeger'
    verbose_name = 'Schlagwort für einen Bildungsträger'
    verbose_name_plural = 'Schlagwörter für Bildungsträger'
    description = 'Schlagwörter für Bildungsträger'


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



#
# Datenthemen
#

# Abfallbehälter

class Abfallbehaelter(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField('Außerbetriebstellung', blank=True, null=True)
  id = models.CharField('ID', max_length=8, default=settings.READONLY_FIELD_DEFAULT)
  typ = models.ForeignKey(Typen_Abfallbehaelter, verbose_name='Typ', on_delete=models.SET_NULL, db_column='typ', to_field='uuid', related_name='typen+', blank=True, null=True)
  aufstellungsjahr = PositiveSmallIntegerRangeField('Aufstellungsjahr', max_value=current_year(), blank=True, null=True)
  eigentuemer = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Eigentümer', on_delete=models.RESTRICT, db_column='eigentuemer', to_field='uuid', related_name='eigentuemer+')
  bewirtschafter = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Bewirtschafter', on_delete=models.RESTRICT, db_column='bewirtschafter', to_field='uuid', related_name='bewirtschafter+')
  pflegeobjekt = models.CharField('Pflegeobjekt', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  inventarnummer = models.CharField('Inventarnummer', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  anschaffungswert = models.DecimalField('Anschaffungswert (in €)', max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Anschaffungswert muss mindestens 0,01 € betragen.')], blank=True, null=True)
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
    list_fields_with_foreign_key = {
      'typ': 'typ__typ',
      'eigentuemer': 'eigentuemer__bezeichnung',
      'bewirtschafter': 'bewirtschafter__bezeichnung'
    }
    readonly_fields = ['deaktiviert', 'id']
    map_feature_tooltip_field = 'id'
    map_filter_fields = {
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
  pdf = models.FileField('PDF', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PDF_PATH_PREFIX_PUBLIC + 'aufteilungsplaene_wohnungseigentumsgesetz'), max_length=40)
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

@receiver(post_delete, sender=Aufteilungsplaene_Wohnungseigentumsgesetz)
def aufteilungsplan_wohnungseigentumsgesetz_post_delete_handler(sender, instance, **kwargs):
  if instance.pdf:
    instance.pdf.delete(False)


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
    geometry_type = 'MultiPolygonField'
    group_with_users_for_choice_field = 'baustellen_geplant_add_delete_view'
    admin_group = 'baustellen_geplant_full'
  
  def __str__(self):
    return self.bezeichnung + ' [' + ('Straße: ' + str(self.strasse) + ', ' if self.strasse else '') + 'Beginn: ' + datetime.strptime(str(self.beginn), '%Y-%m-%d').strftime('%d.%m.%Y') + ', Ende: ' + datetime.strptime(str(self.ende), '%Y-%m-%d').strftime('%d.%m.%Y') + ']'


# Behinderteneinrichtungen

class Behinderteneinrichtungen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger = models.ForeignKey(Bewirtschafter_Betreiber_Traeger_Eigentuemer, verbose_name='Träger', on_delete=models.RESTRICT, db_column='traeger', to_field='uuid', related_name='traeger+')
  plaetze = models.PositiveSmallIntegerField('Plätze', blank=True, null=True)
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


# Kindertagespflegeeinrichtungen

class Kindertagespflegeeinrichtungen(models.Model):
  uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(Adressen, verbose_name='Adresse', on_delete=models.SET_NULL, db_column='adresse', to_field='uuid', related_name='adressen+', blank=True, null=True)
  vorname = models.CharField('Vorname', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message), RegexValidator(regex=bindestrich_leerzeichen_regex, message=bindestrich_leerzeichen_message), RegexValidator(regex=leerzeichen_bindestrich_regex, message=leerzeichen_bindestrich_message)])
  nachname = models.CharField('Nachname', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message), RegexValidator(regex=bindestrich_leerzeichen_regex, message=bindestrich_leerzeichen_message), RegexValidator(regex=leerzeichen_bindestrich_regex, message=leerzeichen_bindestrich_message)])
  plaetze = models.PositiveSmallIntegerField('Plätze')
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
    return self.vorname + ' ' + self.nachname + (', ' + self.adressanzeige if self.adressanzeige else '')





# isi2
class Baudenkmale_Denkmalbereiche(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse/Straße', max_length=255, blank=True, null=True)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  art = models.CharField('Art', max_length=255, choices=ART_BAUDENKMALE_DENKMALBEREICHE)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  beschreibung = models.CharField('Beschreibung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  gueltigkeit_von = models.DateField(default=date.today, editable=False)
  adressanzeige = models.CharField('Adresse', max_length=255, blank=True, null=True)
  geometrie = models.MultiPolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'daten\".\"baudenkmale'
    verbose_name = 'Baudenkmal oder Denkmalbereich'
    verbose_name_plural = 'Baudenkmale und Denkmalbereiche'
    description = 'Baudenkmale und Denkmalbereiche der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'adressanzeige', 'bezeichnung', 'beschreibung']
    list_fields_labels = ['UUID', 'Art', 'Adresse', 'Bezeichnung', 'Beschreibung']
    readonly_fields = ['adressanzeige']
    map_feature_tooltip_field = 'beschreibung'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'MultiPolygonField'
  
  def __str__(self):
    return self.art + (', ' + self.adressanzeige if self.adressanzeige else '') + (', ' + self.bezeichnung if self.bezeichnung else '') + ', ' + self.beschreibung + ' (UUID: ' + str(self.uuid) + ')'


class Baustellen_Fotodokumentation_Baustellen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  sparte = models.CharField('Sparte(n)', max_length=255, choices='')
  verkehrliche_lage = models.CharField('Verkehrliche Lage(n)', max_length=255, choices='')
  auftraggeber = models.CharField('Auftraggeber', max_length=255, choices='')
  auftraggeber_bemerkung = models.CharField('Bemerkung zum Auftraggeber', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ansprechpartner = models.CharField('Ansprechpartner', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  adressanzeige = models.CharField('Adresse', max_length=255, blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"baustellen_fotodokumentation_baustellen'
    verbose_name = 'Baustellen-Fotodokumentation (Baustelle)'
    verbose_name_plural = 'Baustellen-Fotodokumentation (Baustellen)'
    description = 'Baustellen im Rahmen der Baustellen-Fotodokumentation in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung', 'auftraggeber', 'adressanzeige']
    list_fields_labels = ['Bezeichnung', 'Auftraggeber', 'Adresse']
    readonly_fields = ['adressanzeige']
    map_feature_tooltip_field = 'bezeichnung'
    geometry_type = 'Point'
    ordering = ['bezeichnung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.bezeichnung + ' (Auftraggeber: ' + self.auftraggeber + ')'


class Baustellen_Fotodokumentation_Fotos(models.Model):
  id = models.AutoField(primary_key=True)
  parent = models.ForeignKey(Baustellen_Fotodokumentation_Baustellen, on_delete=models.CASCADE, db_column='baustellen_fotodokumentation_baustelle', to_field='uuid')
  dateiname_original = models.CharField('Original-Dateiname', default=settings.READONLY_FIELD_DEFAULT, max_length=255)
  status = models.CharField('Status', max_length=255, choices=STATUS_BAUSTELLEN_FOTODOKUMENTATION)
  aufnahmedatum = models.DateField('Aufnahmedatum')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PUBLIC + 'baustellen_fotodokumentation'), max_length=255)

  class Meta:
    managed = False
    db_table = 'daten\".\"baustellen_fotodokumentation_fotos'
    verbose_name = 'Baustellen-Fotodokumentation (Foto)'
    verbose_name_plural = 'Baustellen-Fotodokumentation (Fotos)'
    description = 'Fotos im Rahmen der Baustellen-Fotodokumentation in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['parent', 'status', 'aufnahmedatum', 'foto', 'dateiname_original']
    list_fields_with_date = ['aufnahmedatum']
    list_fields_labels = ['zu Baustelle', 'Status', 'Aufnahmedatum', 'Foto', 'Original-Dateiname']
    readonly_fields = ['dateiname_original']
    object_title = 'das Foto'
    foreign_key_label = 'Baustelle'
    thumbs = True
    multi_foto_field = True
  
  def __str__(self):
    return str(self.parent) + ', ' + self.status + ', mit Aufnahmedatum ' + datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')


# isi1
class Carsharing_Stationen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  anzahl_fahrzeuge = models.PositiveSmallIntegerField('Anzahl der Fahrzeuge', blank=True, null=True)
  anbieter = models.CharField('Anbieter', max_length=255, choices=ANBIETER_CARSHARING)
  bemerkungen = models.CharField('Bemerkungen', max_length=500, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  telefon = models.CharField('Telefon', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  adressanzeige = models.CharField('Adresse', max_length=255, blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"carsharing_stationen'
    verbose_name = 'Carsharing-Station'
    verbose_name_plural = 'Carsharing-Stationen'
    description = 'Carsharing-Stationen in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung', 'adressanzeige', 'anbieter']
    list_fields_labels = ['Bezeichnung', 'Adresse', 'Anbieter']
    readonly_fields = ['adressanzeige']
    map_feature_tooltip_field = 'bezeichnung'
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + (', ' + self.adressanzeige if self.adressanzeige else '') + ' (' + self.anbieter + ')'


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
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PUBLIC + 'containerstellplaetze'), max_length=255, blank=True, null=True)
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


# isi1
class Denksteine(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  nummer = models.CharField('Nummer', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  titel = models.CharField('Titel', max_length=255, choices=TITEL_DENKSTEINE, blank=True, null=True)
  vorname = models.CharField('Vorname', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  nachname = models.CharField('Nachname', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  namensanzeige = models.CharField('Name', max_length=255, blank=True, null=True)
  geburtsjahr = PositiveSmallIntegerRangeField('Geburtsjahr', min_value=1850, max_value=1945)
  sterbejahr = PositiveSmallIntegerRangeField('Sterbejahr', min_value=1933, max_value=1945, blank=True, null=True)
  text_auf_dem_stein = models.CharField('Text auf dem Stein', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ehemalige_adresse = models.CharField(' ehemalige Adresse', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  erstes_verlegejahr = PositiveSmallIntegerRangeField(' erstes Verlegejahr', min_value=2002, max_value=current_year())
  material = models.CharField('Material', max_length=255, choices=MATERIAL_DENKSTEINE)
  website = models.CharField('Website', max_length=255, validators=[URLValidator(message=url_message)])
  adressanzeige = models.CharField('Adresse', max_length=255, blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"denksteine'
    verbose_name = 'Denkstein'
    verbose_name_plural = 'Denksteine'
    description = 'Denksteine in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'nummer', 'namensanzeige', 'adressanzeige']
    list_fields_labels = ['UUID', 'Nummer', 'Name', 'Adresse']
    readonly_fields = ['namensanzeige', 'adressanzeige']
    map_feature_tooltip_field = 'namensanzeige'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.nummer + ', ' + self.namensanzeige + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.nummer + ', ' + self.namensanzeige + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


# isi1
class FairTrade(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art = models.CharField('Art', max_length=255, choices=ART_FAIRTRADE)
  betreiber = models.CharField('Betreiber', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  barrierefrei = models.BooleanField(' barrierefrei', blank=True, null=True)
  oeffnungszeiten = models.CharField('Öffnungszeiten', max_length=255, blank=True, null=True)
  telefon = models.CharField('Telefon', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"fairtrade'
    verbose_name = 'Fair Trade'
    verbose_name_plural = 'Fair Trade'
    description = 'Fair Trade in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'bezeichnung']
    list_fields_labels = ['UUID', 'Art', 'Bezeichnung']
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


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
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PUBLIC + 'gutachterfotos'), max_length=255)
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
  dateiname_original = models.CharField('Original-Dateiname', default=settings.READONLY_FIELD_DEFAULT, max_length=255)
  motiv = models.CharField('Motiv', max_length=255, choices=MOTIVE_HALTESTELLEN)
  aufnahmedatum = models.DateField('Aufnahmedatum')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PUBLIC + 'haltestellenkataster'), max_length=255)

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


# isi1
class Hospize(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices='')
  plaetze = models.PositiveSmallIntegerField('Plätze', blank=True, null=True)
  telefon = models.CharField('Telefon', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"hospize'
    verbose_name = 'Hospiz'
    verbose_name_plural = 'Hospize'
    description = 'Hospize in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung', 'traeger_bezeichnung']
    list_fields_labels = ['UUID', 'Bezeichnung', 'Träger']
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


# isi2
class Hundetoiletten(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  id_hundetoilette = models.CharField('ID', default=settings.READONLY_FIELD_DEFAULT, max_length=8)
  gueltigkeit_bis = models.DateField('Außerbetriebstellung', blank=True, null=True)
  art = models.CharField('Art', max_length=255, choices=ART_HUNDETOILETTE)
  bewirtschafter_id = models.PositiveSmallIntegerField('Bewirtschafter', choices=BEWIRTSCHAFTER_HUNDETOILETTE)
  bewirtschafter = models.CharField('Bewirtschafter', max_length=255, editable=False)
  pflegeobjekt = models.CharField('Pflegeobjekt', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  inventarnummer = models.CharField('Inventarnummer', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  aufstellungsjahr = PositiveSmallIntegerRangeField('Aufstellungsjahr', min_value=1900, max_value=current_year(), blank=True, null=True)
  anschaffungswert = models.DecimalField('Anschaffungswert (in €)', max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Anschaffungswert muss mindestens 0,01 € betragen.')], blank=True, null=True)
  bemerkungen = models.CharField('Bemerkungen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  adressanzeige = models.CharField('Adresse', max_length=255, blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"hundetoiletten'
    verbose_name = 'Hundetoilette'
    verbose_name_plural = 'Hundetoiletten'
    description = 'Hundetoiletten im Eigentum der Hanse- und Universitätsstadt Rostock'
    list_fields = ['gueltigkeit_bis', 'id_hundetoilette', 'art', 'pflegeobjekt', 'adressanzeige', 'bewirtschafter']
    list_fields_with_date = ['gueltigkeit_bis']
    list_fields_labels = ['Außerbetriebstellung', 'ID', 'Art', 'Pflegeobjekt', 'Adresse', 'Bewirtschafter']
    readonly_fields = ['id_hundetoilette', 'adressanzeige']
    map_feature_tooltip_field = 'id_hundetoilette'
    geometry_type = 'Point'
  
  def __str__(self):
    return 'Hundetoilette mit ID ' + self.id_hundetoilette + ', Art ' + self.art + ', im Pflegeobjekt ' + self.pflegeobjekt + (', ' + self.adressanzeige if self.adressanzeige else '') + ', mit Bewirtschafter ' + self.bewirtschafter


# isi1
class Kinderjugendbetreuung(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices='')
  barrierefrei = models.BooleanField(' barrierefrei', blank=True, null=True)
  oeffnungszeiten = models.CharField('Öffnungszeiten', max_length=255, blank=True, null=True)
  telefon = models.CharField('Telefon', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"kinder_jugendbetreuung'
    verbose_name = 'Kinder- und Jugendbetreuung'
    verbose_name_plural = 'Kinder- und Jugendbetreuung'
    description = 'Kinder- und Jugendbetreuung in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung']
    list_fields_labels = ['UUID', 'Bezeichnung']
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


# isi1
class Kunstimoeffentlichenraum(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse/Straße', max_length=255, blank=True, null=True)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ausfuehrung = models.CharField('Ausführung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  schoepfer = models.CharField('Schöpfer', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  entstehungsjahr = PositiveSmallIntegerRangeField('Entstehungsjahr', min_value=1218, max_value=current_year(), blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"kunst_im_oeffentlichen_raum'
    verbose_name = 'Kunst im öffentlichen Raum'
    verbose_name_plural = 'Kunst im öffentlichen Raum'
    description = 'Kunst im öffentlichen Raum der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung', 'schoepfer', 'entstehungsjahr']
    list_fields_labels = ['UUID', 'Bezeichnung', 'Schöpfer', 'Entstehungsjahr']
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.strasse_name:
      if self.hausnummer:
        if self.hausnummer_zusatz:
          return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
        else:
          return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'
      else:
        return self.bezeichnung + ', ' + self.strasse_name + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ' (UUID: ' + str(self.uuid) + ')'


# isi1
class Ladestationen_Elektrofahrzeuge(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  geplant = models.BooleanField(' geplant', blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  betriebsart = models.CharField('Betriebsart', max_length=255, choices=BETRIEBSART_LADESTATIONEN_ELEKTROFAHRZEUGE)
  betreiber = models.CharField('Betreiber', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  verbund = models.CharField('Verbund', max_length=255, choices=VERBUND_LADESTATIONEN_ELEKTROFAHRZEUGE, blank=True, null=True)
  anzahl_ladepunkte = models.PositiveSmallIntegerField('Anzahl an Ladepunkten')
  arten_ladepunkte = models.CharField('Arten der Ladepunkte', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ladekarten = models.CharField('Ladekarten', max_length=255, choices=LADEKARTEN_LADESTATIONEN_ELEKTROFAHRZEUGE, blank=True, null=True)
  kosten = models.CharField('Kosten', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  oeffnungszeiten = models.CharField('Öffnungszeiten', max_length=255, blank=True, null=True)
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"ladestationen_elektrofahrzeuge'
    verbose_name = 'Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Ladestationen für Elektrofahrzeuge'
    description = 'Ladestationen für Elektrofahrzeuge in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung', 'betriebsart', 'betreiber', 'verbund', 'geplant']
    list_fields_labels = ['Bezeichnung', 'Betriebsart', 'Betreiber', 'Verbund', 'geplant']
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (' + self.betreiber + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (' + self.betreiber + ')'


# isi2
class Meldedienst_flaechenhaft(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse/Straße', max_length=255, blank=True, null=True)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  art = models.CharField('Art', max_length=255, choices=ART_MELDEDIENST_FLAECHENHAFT)
  bearbeiter = models.CharField('Bearbeiter', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkung = models.CharField('Bemerkung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  gueltigkeit_von = models.DateField(default=date.today, editable=False)
  adressanzeige = models.CharField('Adresse', max_length=255, blank=True, null=True)
  geometrie = models.PolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'daten\".\"meldedienst_flaechenhaft'
    verbose_name = 'Meldedienst (flächenhaft)'
    verbose_name_plural = 'Meldedienst (flächenhaft)'
    description = 'Meldedienst (flächenhaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'adressanzeige', 'bearbeiter', 'gueltigkeit_von']
    list_fields_with_date = ['gueltigkeit_von']
    list_fields_labels = ['UUID', 'Art', 'Adresse', 'Bearbeiter', 'geändert']
    readonly_fields = ['adressanzeige']
    map_feature_tooltip_field = 'uuid'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'PolygonField'
  
  def __str__(self):
    return self.art + (', ' + self.adressanzeige if self.adressanzeige else '') + ' (UUID: ' + str(self.uuid) + ')'


# isi2
class Meldedienst_punkthaft(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse/Straße', max_length=255, blank=True, null=True)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  art = models.CharField('Art', max_length=255, choices=ART_MELDEDIENST_PUNKTHAFT)
  bearbeiter = models.CharField('Bearbeiter', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkung = models.CharField('Bemerkung', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  gueltigkeit_von = models.DateField(default=date.today, editable=False)
  adressanzeige = models.CharField('Adresse', max_length=255, blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"meldedienst_punkthaft'
    verbose_name = 'Meldedienst (punkthaft)'
    verbose_name_plural = 'Meldedienst (punkthaft)'
    description = 'Meldedienst (punkthaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'adressanzeige', 'bearbeiter', 'gueltigkeit_von']
    list_fields_with_date = ['gueltigkeit_von']
    list_fields_labels = ['UUID', 'Art', 'Adresse', 'Bearbeiter', 'geändert']
    readonly_fields = ['adressanzeige']
    map_feature_tooltip_field = 'uuid'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
  
  def __str__(self):
    return self.art + (', ' + self.adressanzeige if self.adressanzeige else '') + ' (UUID: ' + str(self.uuid) + ')'


# isi1
class Mobilpunkte(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  bezeichnung = models.CharField('Bezeichnung', max_length=500, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  angebote = models.CharField('Angebote', max_length=255, choices=ANGEBOTE_MOBILPUNKTE)
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"mobilpunkte'
    verbose_name = 'Mobilpunkt'
    verbose_name_plural = 'Mobilpunkte'
    description = 'Mobilpunkte in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung']
    list_fields_labels = ['Bezeichnung']
    map_feature_tooltip_field = 'bezeichnung'
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung


# isi1
class Parkmoeglichkeiten(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse/Straße', max_length=255, blank=True, null=True)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  art = models.CharField('Art', max_length=255, choices=ART_PARKMOEGLICHKEITEN)
  standort = models.CharField('Standort', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  betreiber = models.CharField('Betreiber', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  stellplaetze_pkw = models.PositiveSmallIntegerField('Pkw-Stellplätze', blank=True, null=True)
  stellplaetze_wohnmobil = models.PositiveSmallIntegerField('Wohnmobil-Stellplätze', blank=True, null=True)
  stellplaetze_bus = models.PositiveSmallIntegerField('Bus-Stellplätze', blank=True, null=True)
  gebuehren_halbe_stunde = models.DecimalField('Gebühren ½ h (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren je ½ h müssen mindestens 0,01 € betragen.')], blank=True, null=True)
  gebuehren_eine_stunde = models.DecimalField('Gebühren 1 h (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren je 1 h müssen mindestens 0,01 € betragen.')], blank=True, null=True)
  gebuehren_zwei_stunden = models.DecimalField('Gebühren 2 h (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren je 2 h müssen mindestens 0,01 € betragen.')], blank=True, null=True)
  gebuehren_ganztags = models.DecimalField('Gebühren ganztags (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren ganztags müssen mindestens 0,01 € betragen.')], blank=True, null=True)
  gebuehren_anmerkungen = models.CharField('Anmerkungen zu den Gebühren', max_length=255, blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"parkmoeglichkeiten'
    verbose_name = 'Parkmöglichkeit'
    verbose_name_plural = 'Parkmöglichkeiten'
    description = 'Parkmöglichkeiten in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'standort']
    list_fields_labels = ['UUID', 'Art', 'Standort']
    map_feature_tooltip_field = 'standort'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.strasse_name:
      if self.hausnummer:
        if self.hausnummer_zusatz:
          return self.standort + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
        else:
          return self.standort + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'
      else:
        return self.standort + ' (' + self.art + '), ' + self.strasse_name + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.standort + ' (' + self.art + '), ' + ' (UUID: ' + str(self.uuid) + ')'


class Parkscheinautomaten_Tarife(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bewirtschaftungszeiten = models.CharField('Bewirtschaftungszeiten', max_length=255)
  normaltarif_parkdauer_min = models.PositiveSmallIntegerField('Mindestparkdauer Normaltarif')
  normaltarif_parkdauer_min_einheit = models.CharField('Einheit der Mindestparkdauer Normaltarif', max_length=255, choices=EINHEIT_PARKDAUER_PARKSCHEINAUTOMATEN_TARIFE)
  normaltarif_parkdauer_max = models.PositiveSmallIntegerField('Maximalparkdauer Normaltarif')
  normaltarif_parkdauer_max_einheit = models.CharField('Einheit der Maximalparkdauer Normaltarif', max_length=255, choices=EINHEIT_PARKDAUER_PARKSCHEINAUTOMATEN_TARIFE)
  normaltarif_gebuehren_max = models.DecimalField('Maximalgebühren Normaltarif (in €)', max_digits=4, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Maximalgebühren Normaltarif müssen mindestens 0,01 € betragen.')], blank=True, null=True)
  normaltarif_gebuehren_pro_stunde = models.DecimalField('Gebühren pro Stunde Normaltarif (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren pro Stunde Normaltarif müssen mindestens 0,01 € betragen.')], blank=True, null=True)
  normaltarif_gebuehrenschritte = models.CharField('Gebührenschritte Normaltarif', max_length=255, choices=GEBUEHRENSCHRITTE_PARKSCHEINAUTOMATEN_TARIFE, blank=True, null=True)
  veranstaltungstarif_parkdauer_min = models.PositiveSmallIntegerField('Mindestparkdauer Veranstaltungstarif', blank=True, null=True)
  veranstaltungstarif_parkdauer_min_einheit = models.CharField('Einheit der Mindestparkdauer Veranstaltungstarif', max_length=255, choices=EINHEIT_PARKDAUER_PARKSCHEINAUTOMATEN_TARIFE, blank=True, null=True)
  veranstaltungstarif_parkdauer_max = models.PositiveSmallIntegerField('Maximalparkdauer Veranstaltungstarif', blank=True, null=True)
  veranstaltungstarif_parkdauer_max_einheit = models.CharField('Einheit der Maximalparkdauer Veranstaltungstarif', max_length=255, choices=EINHEIT_PARKDAUER_PARKSCHEINAUTOMATEN_TARIFE, blank=True, null=True)
  veranstaltungstarif_gebuehren_max = models.DecimalField('Maximalgebühren Veranstaltungstarif (in €)', max_digits=4, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Maximalgebühren Veranstaltungstarif müssen mindestens 0,01 € betragen.')], blank=True, null=True)
  veranstaltungstarif_gebuehren_pro_stunde = models.DecimalField('Gebühren pro Stunde Veranstaltungstarif (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren pro Stunde Veranstaltungstarif müssen mindestens 0,01 € betragen.')], blank=True, null=True)
  veranstaltungstarif_gebuehrenschritte = models.CharField('Gebührenschritte Veranstaltungstarif', max_length=255, choices=GEBUEHRENSCHRITTE_PARKSCHEINAUTOMATEN_TARIFE, blank=True, null=True)
  zugelassene_muenzen = models.CharField('zugelassene Münzen', max_length=255, choices=ZUGELASSENE_MUENZEN_PARKSCHEINAUTOMATEN_TARIFE)

  class Meta:
    managed = False
    db_table = 'daten\".\"parkscheinautomaten_tarife'
    verbose_name = 'Parkscheinautomaten (Tarif)'
    verbose_name_plural = 'Parkscheinautomaten (Tarife)'
    description = 'Tarife für die Parkscheinautomaten der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung', 'bewirtschaftungszeiten']
    list_fields_labels = ['Bezeichnung', 'Bewirtschaftungszeiten']
    ordering = ['bezeichnung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.bezeichnung + ' (Bewirtschaftungszeiten: ' + self.bewirtschaftungszeiten + ')'


class Parkscheinautomaten_Parkscheinautomaten(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  parent = models.ForeignKey(Parkscheinautomaten_Tarife, on_delete=models.PROTECT, db_column='parkscheinautomaten_tarif', to_field='uuid')
  nummer = models.PositiveSmallIntegerField('Nummer')
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  strasse_name = models.CharField('Adresse/Straße', max_length=255, blank=True, null=True)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  zone = models.CharField('Zone', blank=False, max_length=255, choices=ZONE_PARKSCHEINAUTOMATEN_PARKSCHEINAUTOMATEN)
  handyparkzone = models.PositiveIntegerField('Handyparkzone', validators=[MinValueValidator(100000, 'Die Handyparkzone muss einen Wert größer gleich 100000 aufweisen.'), MaxValueValidator(999999, 'Die Handyparkzone muss einen Wert kleiner gleich 999999 aufweisen.')])
  bewohnerparkgebiet = models.CharField('Bewohnerparkgebiet', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geraetenummer = models.CharField('Gerätenummer', max_length=8, validators=[RegexValidator(regex=geraetenummer_regex, message=geraetenummer_message)])
  inbetriebnahme = models.DateField('Inbetriebnahme', blank=True, null=True)
  e_anschluss = models.CharField('E-Anschluss', max_length=255, choices=E_ANSCHLUSS_PARKSCHEINAUTOMATEN_PARKSCHEINAUTOMATEN)
  stellplaetze_pkw = models.PositiveSmallIntegerField('Pkw-Stellplätze', blank=True, null=True)
  stellplaetze_bus = models.PositiveSmallIntegerField('Bus-Stellplätze', blank=True, null=True)
  haendlerkartennummer = models.PositiveIntegerField('Händlerkartennummer', blank=True, null=True, validators=[MinValueValidator(1000000000, 'Die Händlerkartennummer muss einen Wert größer gleich 1000000000 aufweisen.'), MaxValueValidator(9999999999, 'Die Händlerkartennummer muss einen Wert kleiner gleich 9999999999 aufweisen.')])
  laufzeit_geldkarte = models.DateField('Laufzeit der Geldkarte', blank=True, null=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"parkscheinautomaten_parkscheinautomaten'
    verbose_name = 'Parkscheinautomaten (Parkscheinautomat)'
    verbose_name_plural = 'Parkscheinautomaten (Parkscheinautomaten)'
    description = 'Parkscheinautomaten der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung', 'nummer', 'zone', 'parent']
    list_fields_labels = ['Bezeichnung', 'Nummer', 'Zone', 'Tarif']
    object_title = 'der Parkscheinautomat'
    foreign_key_label = 'Tarif'
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
  
  def __str__(self):
    return str(self.parent) + ', ' + self.bezeichnung + ', mit Nummer ' + str(self.nummer) + ', in Zone ' + self.zone


# isi1
class Pflegeeinrichtungen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art = models.CharField('Art', max_length=255, choices=ART_PFLEGEEINRICHTUNGEN)
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices='')
  plaetze = models.PositiveSmallIntegerField('Plätze', blank=True, null=True)
  telefon = models.CharField('Telefon', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"pflegeeinrichtungen'
    verbose_name = 'Pflegeeinrichtung'
    verbose_name_plural = 'Pflegeeinrichtungen'
    description = 'Pflegeeinrichtungen in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'bezeichnung', 'traeger_bezeichnung']
    list_fields_labels = ['UUID', 'Art', 'Bezeichnung', 'Träger']
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


# isi1
class Rettungswachen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices='')
  telefon = models.CharField('Telefon', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"rettungswachen'
    verbose_name = 'Rettungswache'
    verbose_name_plural = 'Rettungswachen'
    description = 'Rettungswachen in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung', 'traeger_bezeichnung']
    list_fields_labels = ['UUID', 'Bezeichnung', 'Träger']
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


# isi1
class Begegnungszentren(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices='')
  barrierefrei = models.BooleanField(' barrierefrei', blank=True, null=True)
  oeffnungszeiten = models.CharField('Öffnungszeiten', max_length=255, blank=True, null=True)
  telefon = models.CharField('Telefon', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"begegnungszentren'
    verbose_name = 'Stadtteil- und/oder Begegnungszentrum'
    verbose_name_plural = 'Stadtteil- und Begegnungszentren'
    description = 'Stadtteil- und Begegnungszentren in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung']
    list_fields_labels = ['UUID', 'Bezeichnung']
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


class Uvp_Vorhaben(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art_vorgang = models.CharField('Art des Vorgangs', max_length=255, choices=ART_VORGANG_UVP_VORHABEN)
  genehmigungsbehoerde = models.CharField('Genehmigungsbehörde', max_length=255, choices=GENEHMIGUNGSBEHOERDE_UVP_VORHABEN)
  datum_posteingang_genehmigungsbehoerde = models.DateField('Datum des Posteingangs bei der Genehmigungsbehörde', default=date.today)
  registriernummer_bauamt = models.CharField('Registriernummer des Bauamtes', max_length=8, blank=True, null=True, validators=[RegexValidator(regex=registriernummer_bauamt_regex, message=registriernummer_bauamt_message)])
  aktenzeichen = models.CharField('Aktenzeichen', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  rechtsgrundlage = models.CharField('Rechtsgrundlage', max_length=255, choices=RECHTSGRUNDLAGE_UVP_VORHABEN)
  typ = models.CharField('Typ', max_length=255, choices=TYP_UVP_VORHABEN)
  geometrie = models.PolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'daten\".\"uvp_vorhaben'
    verbose_name = 'Vorhaben (UVP)'
    verbose_name_plural = 'Vorhaben (UVP)'
    description = 'Vorhaben, auf die sich Vorprüfungen der Hanse- und Universitätsstadt Rostock zur Feststellung der UVP-Pflicht gemäß UVPG und LUVPG M-V beziehen'
    list_fields = ['bezeichnung', 'art_vorgang', 'genehmigungsbehoerde', 'datum_posteingang_genehmigungsbehoerde', 'rechtsgrundlage', 'typ']
    list_fields_with_date = ['datum_posteingang_genehmigungsbehoerde']
    list_fields_labels = ['Bezeichnung', 'Art des Vorgangs', 'Genehmigungsbehörde', 'Datum des Posteingangs bei der Genehmigungsbehörde', 'Rechtsgrundlage', 'Typ']
    map_feature_tooltip_field = 'bezeichnung'
    geometry_type = 'PolygonField'
    ordering = ['bezeichnung'] # wichtig, denn nur so werden Drop-down-Einträge in Formularen von Kindtabellen sortiert aufgelistet
  
  def __str__(self):
    return self.bezeichnung


class Uvp_Vorpruefung(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  parent = models.ForeignKey(Uvp_Vorhaben, on_delete=models.PROTECT, db_column='uvp_vorhaben', to_field='uuid')
  datum_posteingang = models.DateField('Datum des Posteingangs', default=date.today)
  art = models.CharField('Art', max_length=255, choices=ART_UVP_VORPRUEFUNG)
  datum = models.DateField('Datum', default=date.today)
  ergebnis = models.CharField('Ergebnis', max_length=255, choices=ERGEBNIS_UVP_VORPRUEFUNG)
  datum_bekanntmachung = models.DateField('Datum Bekanntmachung „Städtischer Anzeiger“', blank=True, null=True)
  datum_veroeffentlichung = models.DateField('Datum Veröffentlichung UVP-Portal', blank=True, null=True)
  pruefprotokoll = models.CharField('Prüfprotokoll', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])

  class Meta:
    managed = False
    db_table = 'daten\".\"uvp_vorpruefungen'
    verbose_name = 'UVP-Vorprüfung'
    verbose_name_plural = 'UVP-Vorprüfungen'
    description = 'Vorprüfungen der Hanse- und Universitätsstadt Rostock zur Feststellung der UVP-Pflicht gemäß UVPG und LUVPG M-V'
    list_fields = ['parent', 'datum_posteingang', 'art', 'datum', 'ergebnis']
    list_fields_with_date = ['datum_posteingang', 'datum']
    list_fields_labels = ['Vorhaben', 'Datum des Posteingangs', 'Art', 'Datum', 'Ergebnis']
    object_title = 'die UVP-Vorprüfung'
    foreign_key_label = 'Vorhaben'
  
  def __str__(self):
    return str(self.parent) + ' (Datum des Posteingangs: ' + datetime.strptime(str(self.datum_posteingang), '%Y-%m-%d').strftime('%d.%m.%Y') + ', Art: ' + self.art + ', Datum: ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + ', Ergebnis: ' + self.ergebnis + ')'


# isi1
class Vereine(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid4, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = models.CharField(max_length=4, blank=True, null=True)
  hausnummer_zusatz = models.CharField(max_length=2, blank=True, null=True)
  klassen = models.CharField('Kategorien', max_length=255, choices=KLASSEN_VEREINE)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=akut_regex, message=akut_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  barrierefrei = models.BooleanField(' barrierefrei', blank=True, null=True)
  telefon = models.CharField('Telefon', max_length=255, blank=True, null=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = models.CharField('E-Mail', max_length=255, blank=True, null=True, validators=[EmailValidator(message=email_message)])
  website = models.CharField('Website', max_length=255, blank=True, null=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'daten\".\"vereine'
    verbose_name = 'Verein'
    verbose_name_plural = 'Vereine'
    description = 'Vereine in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung', 'klassen']
    list_fields_labels = ['Bezeichnung', 'Kategorien']
    map_feature_tooltip_field = 'bezeichnung'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'

  def get_klassen_display(self):
    return ', '.join(self.klassen)


@receiver(pre_save, sender=Baustellen_Fotodokumentation_Fotos)
def baustelle_fotodokumentation_pre_save_handler(sender, instance, **kwargs):
  # ab hier in Funktion B auslagern
  try:
    old = Baustellen_Fotodokumentation_Fotos.objects.get(pk=instance.pk)
    if old and old.foto and old.foto.name:
      instance.original_url = old.foto.name
  except Baustellen_Fotodokumentation_Fotos.DoesNotExist:
    pass


@receiver(post_save, sender=Baustellen_Fotodokumentation_Fotos)
def baustelle_fotodokumentation_post_save_handler(sender, instance, **kwargs):
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


@receiver(post_delete, sender=Baustellen_Fotodokumentation_Fotos)
def baustelle_fotodokumentation_post_delete_handler(sender, instance, **kwargs):
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


@receiver(pre_save, sender=Containerstellplaetze)
def containerstellplatz_pre_save_handler(sender, instance, **kwargs):
  # ab hier in Funktion B auslagern
  try:
    old = Containerstellplaetze.objects.get(pk=instance.pk)
    if old and old.foto and old.foto.url:
      instance.original_url = old.foto.url
  except Containerstellplaetze.DoesNotExist:
    pass


@receiver(post_save, sender=Containerstellplaetze)
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


@receiver(post_delete, sender=Containerstellplaetze)
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


@receiver(post_save, sender=Gutachterfotos)
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


@receiver(post_delete, sender=Gutachterfotos)
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


@receiver(pre_save, sender=Haltestellenkataster_Fotos)
def haltestellenkataster_pre_save_handler(sender, instance, **kwargs):
  # ab hier in Funktion B auslagern
  try:
    old = Haltestellenkataster_Fotos.objects.get(pk=instance.pk)
    if old and old.foto and old.foto.name:
      instance.original_url = old.foto.name
  except Haltestellenkataster_Fotos.DoesNotExist:
    pass


@receiver(post_save, sender=Haltestellenkataster_Fotos)
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


@receiver(post_delete, sender=Haltestellenkataster_Fotos)
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
