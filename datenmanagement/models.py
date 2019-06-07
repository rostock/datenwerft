# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import date, datetime
from decimal import *
from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MinValueValidator, RegexValidator, URLValidator
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text, python_2_unicode_compatible
from multiselectfield import MultiSelectField
from PIL import Image, ExifTags
from datenmanagement.storage import OverwriteStorage

import os
import re
import uuid


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
      filename = '{0}.{1}'.format(str(uuid.uuid1()), ext.lower())
    return os.path.join(path, filename)
  return wrapper


def rotate_image(path):
  try:
    image = Image.open(path)
    for orientation in ExifTags.TAGS.keys():
      if ExifTags.TAGS[orientation] == 'Orientation':
        break
    exif = dict(image._getexif().items())
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


class NullCharField(models.CharField):
  def __init__(self, *args, **kwargs):
    super(NullCharField, self).__init__(*args, **kwargs)

  def to_python(self, value):
    if value in self.empty_values:
      return None
    value = force_text(value)
    value = value.strip()
    return value

  def widget_attrs(self, widget):
    attrs = super(NullCharField, self).widget_attrs(widget)
    if self.max_length is not None:
      attrs.update({'maxlength': str(self.max_length)})
    return attrs


class PositiveSmallIntegerRangeField(models.PositiveSmallIntegerField):
  def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
    self.min_value, self.max_value = min_value, max_value
    models.PositiveSmallIntegerField.__init__(self, verbose_name, name, **kwargs)
    
  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value, 'max_value': self.max_value}
    defaults.update(kwargs)
    return super(PositiveSmallIntegerRangeField, self).formfield(**defaults)


models.options.DEFAULT_NAMES += (
  'description',                    # Pflicht  ; Text      ; Beschreibung bzw. Langtitel des Datenthemas
  'list_fields',                    # Pflicht  ; Textliste ; Namen der Felder, die in genau dieser Reihenfolge in der Tabelle der Listenansicht als Spalten auftreten sollen
  'list_fields_with_number',        # optional ; Textliste ; Namen der Felder aus list_fields, deren Werte von einem numerischen Datentyp sind
  'list_fields_with_date',          # optional ; Textliste ; Namen der Felder aus list_fields, deren Werte vom Datentyp Datum sind
  'list_fields_labels',             # Pflicht  ; Textliste ; Titel der Felder, die in genau dieser Reihenfolge in der Tabelle der Listenansicht als Spaltentitel auftreten sollen
  'readonly_fields',                # optional ; Textliste ; Namen der Felder, die in der Hinzufügen-/Änderungsansicht nur lesbar erscheinen sollen
  'object_title',                   # optional ; Text      ; Textbaustein für die Löschansicht (relevant nur bei Modellen mit Fremdschlüssel)
  'foreign_key_label',              # optional ; Text      ; Titel des Feldes mit dem Fremdschlüssel (relevant nur bei Modellen mit Fremdschlüssel)
  'show_alkis',                     # optional ; Boolean   ; Soll die Liegenschaftskarte als Hintergrundkarte in der Karten-/Hinzufügen-/Änderungsansicht angeboten werden?
  'map_feature_tooltip_field',      # optional ; Text      ; Name des Feldes, dessen Werte in der Kartenansicht als Tooltip der Kartenobjekte angezeigt werden sollen
  'address',                        # optional ; Boolean   ; Soll die Adresse eine Pflichtangabe sein?
  'address_optional',               # optional ; Boolean   ; Soll die Hausnummer eine Pflichtangabe sein oder reicht der Straßenname?
  'geometry_type',                  # optional ; Text      ; Geometrietyp
  'thumbs',                         # optional ; Boolean   ; Sollen Thumbnails aus den hochgeladenen Fotos erzeugt werden?
  'multi_foto_field'                # optional ; Boolean   ; Sollen mehrere Fotos hochgeladen werden können? Es werden dann automatisch mehrere Datensätze erstellt, und zwar jeweils einer pro Foto. Achtung: Es muss bei Verwendung dieser Option ein Pflichtfeld mit Namen foto existieren!
)


doppelleerzeichen_regex = r'^(?!.*  ).*$'
doppelleerzeichen_message = 'Der Text darf keine doppelten Leerzeichen enthalten.'
anfuehrungszeichen_regex = r'^(?!.*\").*$'
anfuehrungszeichen_message = 'Der Text darf keine doppelten Schreibmaschinensatz-Anführungszeichen (") enthalten. Stattdessen müssen die typographisch korrekten Anführungszeichen („“) verwendet werden.'
apostroph_regex = r'^(?!.*\').*$'
apostroph_message = 'Der Text darf keine einfachen Schreibmaschinensatz-Anführungszeichen (\') enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.'
gravis_regex = r'^(?!.*`).*$'
gravis_message = 'Der Text darf keine Gravis (`) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.'
hafas_id_regex = r'^[0-9]{8}$'
hafas_id_message = 'Die HAFAS-ID muss aus genau acht Ziffern bestehen.'
id_containerstellplatz_regex = r'^[0-9]{2}-[0-9]{2}$'
id_containerstellplatz_message = 'Die ID des Containerstellplatzes muss aus genau zwei Ziffern, genau einem Bindestrich und abermals genau zwei Ziffern bestehen.'
inventarnummer_regex = r'^[0-9]{8}$'
inventarnummer_message = 'Die Inventarnummer muss aus genau acht Ziffern bestehen.'
postleitzahl_regex = r'^[0-9]{5}$'
postleitzahl_message = 'Eine Postleitzahl muss aus genau fünf Ziffern bestehen.'
rufnummer_regex = r'^\+49 [1-9][0-9]{1,5} [0-9]{1,13}$'
rufnummer_message = 'Die Schreibweise von Rufnummern muss der Empfehlung E.123 der Internationalen Fernmeldeunion entsprechen und daher folgendes Format aufweisen: +49 381 3816256'
email_message = 'Die E-Mail-Adresse muss syntaktisch korrekt sein und daher folgendes Format aufweisen: abc-123.098_zyx@xyz-567.ghi.abc'
url_message = 'Die Adresse der Website muss syntaktisch korrekt sein und daher folgendes Format aufweisen: http[s]://abc-123.098_zyx.xyz-567/ghi/abc'


ANBIETER_CARSHARING = (
  ('Flinkster (Deutsche Bahn AG)', 'Flinkster (Deutsche Bahn AG)'),
  ('Greenwheels GmbH', 'Greenwheels GmbH'),
  ('YourCar Rostock GmbH', 'YourCar Rostock GmbH'),
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
  ('Kurzzeitpflegeeinrichtung', 'Kurzzeitpflegeeinrichtung'),
  ('Nachtpflegeeinrichtung', 'Nachtpflegeeinrichtung'),
  ('Tagespflegeeinrichtung', 'Tagespflegeeinrichtung'),
  ('Verhinderungspflegeeinrichtung', 'Verhinderungspflegeeinrichtung'),
  ('Vollstationäre Pflegeeinrichtung', 'Vollstationäre Pflegeeinrichtung'),
)

AUFTRAGGEBER_BAUSTELLEN = (
  ('Deutsche Telekom AG', 'Deutsche Telekom AG'),
  ('Hanse- und Universitätsstadt Rostock', 'Hanse- und Universitätsstadt Rostock'),
  ('Nordwasser GmbH', 'Nordwasser GmbH'),
  ('Rostocker Straßenbahn AG', 'Rostocker Straßenbahn AG'),
  ('Stadtentsorgung Rostock GmbH', 'Stadtentsorgung Rostock GmbH'),
  ('Stadtwerke Rostock AG', 'Stadtwerke Rostock AG'),
  ('andere(r)/private(r)', 'andere(r)/private(r)'),
)

AUSFUEHRUNG_HALTESTELLEN = (
  ('Noppen', 'Noppen'),
  ('Rillenplatten', 'Rillenplatten'),
  ('Rippenplatten', 'Rippenplatten'),
)

BEFESTIGUNGSART_HALTESTELLEN = (
  ('Asphalt', 'Asphalt'),
  ('Beton', 'Beton'),
  ('Kleinpflaster', 'Kleinpflaster'),
  ('sonstige', 'sonstige'),
)

BEWIRTSCHAFTER_ABFALLBEHAELTER = (
  (67, 'Amt für Stadtgrün, Naturschutz und Landschaftspflege'),
  (73, 'Amt für Umweltschutz'),
  (66, 'Amt für Verkehrsanlagen'),
  (87, 'Tourismuszentrale Rostock und Warnemünde'),
  (2000, 'Rostocker Straßenbahn AG'),
)

BEWIRTSCHAFTER_HUNDETOILETTE = (
  (73, 'Amt für Umweltschutz'),
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
  (73, 'Amt für Umweltschutz'),
  (66, 'Amt für Verkehrsanlagen'),
)

BEWIRTSCHAFTER_PAPIER_CONTAINERSTELLPLAETZE = (
  (1, 'Veolia Umweltservice Nord GmbH'),
)

EIGENTUEMER_ABFALLBEHAELTER = (
  ('hro', 'Hanse- und Universitätsstadt Rostock'),
  ('rsag', 'Rostocker Straßenbahn AG'),
  ('sr', 'Stadtentsorgung Rostock GmbH'),
)

KLASSEN_BILDUNGSTRAEGER = (
  ('Arbeit', 'Arbeit'),
  ('Computer', 'Computer'),
  ('Eltern', 'Eltern'),
  ('Gesundheit', 'Gesundheit'),
  ('Kultur', 'Kultur'),
  ('Nachhilfe', 'Nachhilfe'),
  ('Natur', 'Natur'),
  ('Pädagogik', 'Pädagogik'),
  ('Politik', 'Politik'),
  ('Recht', 'Recht'),
  ('Sozialkompetenz', 'Sozialkompetenz'),
  ('Sport', 'Sport'),
  ('Sprachen', 'Sprachen'),
  ('Technik', 'Technik'),
  ('Wirtschaft', 'Wirtschaft'),
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

SPARTEN_BAUSTELLEN = (
  ('Beleuchtung', 'Beleuchtung'),
  ('Fernwärme', 'Fernwärme'),
  ('Gas', 'Gas'),
  ('Grundstückserschließung', 'Grundstückserschließung'),
  ('Lichtsignalanlagen', 'Lichtsignalanlagen'),
  ('ÖPNV', 'ÖPNV'),
  ('Stadtgrün', 'Stadtgrün'),
  ('Straßenbau', 'Straßenbau'),
  ('Strom', 'Strom'),
  ('Telekommunikation', 'Telekommunikation'),
  ('Wasser/Abwasser', 'Wasser/Abwasser'),
)

STATUS_BAUSTELLEN_FOTODOKUMENTATION = (
  ('vor Baumaßnahme', 'vor Baumaßnahme'),
  ('während Baumaßnahme', 'während Baumaßnahme'),
  ('nach Baumaßnahme', 'nach Baumaßnahme'),
)

TRAEGER_ART = (
  ('betrieblich', 'betrieblich'),
  ('freie Wohlfahrtspflege', 'freie Wohlfahrtspflege'),
  ('gewerblich-privat', 'gewerblich-privat'),
  ('kirchlich', 'kirchlich'),
  ('kommerziell', 'kommerziell'),
  ('öffentlich', 'öffentlich'),
)

TYP_ABFALLBEHAELTER = (
  ('Dinova', 'Dinova'),
  ('Eisenjäger', 'Eisenjäger'),
  ('H&L', 'H&L'),
  ('Punto', 'Punto'),
  ('Wetz', 'Wetz'),
)

TYP_HALTESTELLEN = (
  ('Bushaltestelle (am Fahrbahnrand)', 'Bushaltestelle (am Fahrbahnrand)'),
  ('Bushaltestelle (Busbucht)', 'Bushaltestelle (Busbucht)'),
  ('Bushaltestelle (Buskap)', 'Bushaltestelle (Buskap)'),
  ('Doppelhaltestelle', 'Doppelhaltestelle'),
  ('Kombihaltestelle', 'Kombihaltestelle'),
  ('Straßenbahnhaltestelle', 'Straßenbahnhaltestelle'),
)

VERKEHRLICHE_LAGEN_BAUSTELLEN = (
  ('Fahrbahn', 'Fahrbahn'),
  ('Fußweg', 'Fußweg'),
  ('Radweg', 'Radweg'),
  ('Straße mit Begleitgrün', 'Straße mit Begleitgrün'),
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


@python_2_unicode_compatible
class Abfallbehaelter(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  id_abfallbehaelter = models.CharField('ID', default=settings.READONLY_FIELD_DEFAULT, max_length=8)
  gueltigkeit_bis = models.DateField('Außerbetriebstellung', blank=True)
  eigentuemer_id = models.CharField('Eigentümer', max_length=255, choices=EIGENTUEMER_ABFALLBEHAELTER)
  eigentuemer = models.CharField('Eigentümer', max_length=255, editable=False)
  bewirtschafter_id = models.PositiveSmallIntegerField('Bewirtschafter', choices=BEWIRTSCHAFTER_ABFALLBEHAELTER)
  bewirtschafter = models.CharField('Bewirtschafter', max_length=255, editable=False)
  pflegeobjekt = models.CharField('Pflegeobjekt', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  inventarnummer = NullCharField('Inventarnummer', max_length=8, blank=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  aufstellungsjahr = PositiveSmallIntegerRangeField('Aufstellungsjahr', min_value=1900, max_value=current_year(), blank=True)
  anschaffungswert = models.DecimalField('Anschaffungswert (in €)', max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Anschaffungswert muss mindestens 0,01 € betragen.')], blank=True)
  typ = NullCharField('Typ', max_length=255, choices=TYP_ABFALLBEHAELTER, blank=True)
  haltestelle = models.NullBooleanField('Lage an einer Haltestelle')
  sommer_mo = models.PositiveSmallIntegerField('Anzahl Leerungen montags im Sommer', blank=True)
  sommer_di = models.PositiveSmallIntegerField('Anzahl Leerungen dienstags im Sommer', blank=True)
  sommer_mi = models.PositiveSmallIntegerField('Anzahl Leerungen mittwochs im Sommer', blank=True)
  sommer_do = models.PositiveSmallIntegerField('Anzahl Leerungen donnerstags im Sommer', blank=True)
  sommer_fr = models.PositiveSmallIntegerField('Anzahl Leerungen freitags im Sommer', blank=True)
  sommer_sa = models.PositiveSmallIntegerField('Anzahl Leerungen samstags im Sommer', blank=True)
  sommer_so = models.PositiveSmallIntegerField('Anzahl Leerungen sonntags im Sommer', blank=True)
  winter_mo = models.PositiveSmallIntegerField('Anzahl Leerungen montags im Winter', blank=True)
  winter_di = models.PositiveSmallIntegerField('Anzahl Leerungen dienstags im Winter', blank=True)
  winter_mi = models.PositiveSmallIntegerField('Anzahl Leerungen mittwochs im Winter', blank=True)
  winter_do = models.PositiveSmallIntegerField('Anzahl Leerungen donnerstags im Winter', blank=True)
  winter_fr = models.PositiveSmallIntegerField('Anzahl Leerungen freitags im Winter', blank=True)
  winter_sa = models.PositiveSmallIntegerField('Anzahl Leerungen samstags im Winter', blank=True)
  winter_so = models.PositiveSmallIntegerField('Anzahl Leerungen sonntags im Winter', blank=True)
  bemerkungen = NullCharField('Bemerkungen', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'abfallbehaelter'
    verbose_name = 'Abfallbehälter'
    verbose_name_plural = 'Abfallbehälter'
    description = 'Abfallbehälter in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['gueltigkeit_bis', 'id_abfallbehaelter', 'typ', 'pflegeobjekt', 'adressanzeige', 'eigentuemer', 'bewirtschafter']
    list_fields_with_date = ['gueltigkeit_bis']
    list_fields_labels = ['Außerbetriebstellung', 'ID', 'Typ', 'Pflegeobjekt', 'Adresse', 'Eigentümer', 'Bewirtschafter']
    readonly_fields = ['id_abfallbehaelter', 'adressanzeige']
    show_alkis = True
    map_feature_tooltip_field = 'id_abfallbehaelter'
    address = False
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    return 'Abfallbehälter mit ID ' + self.id_abfallbehaelter + (', Typ ' + self.typ if self.typ else '') + ', im Pflegeobjekt ' + self.pflegeobjekt + (', ' + self.adressanzeige if self.adressanzeige else '') + ', mit Eigentümer ' + self.eigentuemer + ' und Bewirtschafter ' + self.bewirtschafter


@python_2_unicode_compatible
class Aufteilungsplaene_Wohnungseigentumsgesetz(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = NullCharField('Adresse/Straße', max_length=255, blank=True)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  aktenzeichen = NullCharField('Aktenzeichen', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  abgeschlossenheitserklaerungsdatum = models.DateField('Datum der Abgeschlossenheitserklärung', blank=True)
  bearbeiter = NullCharField('Bearbeiter', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkung = NullCharField('Bemerkung', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  pdf = models.FileField('PDF', storage=OverwriteStorage(), upload_to=path_and_rename(settings.PDF_PATH_PREFIX + 'aufteilungsplaene_wohnungseigentumsgesetz'), max_length=255)
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'aufteilungsplaene_wohnungseigentumsgesetz'
    verbose_name = 'Aufteilungsplan nach Wohnungseigentumsgesetz'
    verbose_name_plural = 'Aufteilungspläne nach Wohnungseigentumsgesetz'
    description = 'Aufteilungspläne nach Wohnungseigentumsgesetz in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'adressanzeige', 'bearbeiter', 'datum', 'abgeschlossenheitserklaerungsdatum']
    list_fields_with_date = ['datum', 'abgeschlossenheitserklaerungsdatum']
    list_fields_labels = ['UUID', 'Adresse', 'Bearbeiter', 'Datum', 'Datum der Abgeschlossenheitserklärung']
    readonly_fields = ['adressanzeige']
    show_alkis = True
    map_feature_tooltip_field = 'uuid'
    address = True
    address_optional = True
    geometry_type = 'Point'
  
  def __str__(self):
    return 'Abgeschlossenheitserklärung mit Datum ' + datetime.strptime(unicode(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + (', ' + self.adressanzeige if self.adressanzeige else '') + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Baustellen_Fotodokumentation_Baustellen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  sparte = MultiSelectField('Sparte(n)', max_length=255, choices=SPARTEN_BAUSTELLEN)
  verkehrliche_lage = MultiSelectField('Verkehrliche Lage(n)', max_length=255, choices=VERKEHRLICHE_LAGEN_BAUSTELLEN)
  auftraggeber = models.CharField('Auftraggeber', max_length=255, choices=AUFTRAGGEBER_BAUSTELLEN)
  auftraggeber_bemerkung = NullCharField('Bemerkung zum Auftraggeber', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ansprechpartner = models.CharField('Ansprechpartner', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'baustellen_fotodokumentation_baustellen'
    verbose_name = 'Baustellen-Fotodokumentation (Baustellen)'
    verbose_name_plural = 'Baustellen-Fotodokumentation (Baustellen)'
    description = 'Baustellen im Rahmen der Baustellen-Fotodokumentation in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung', 'auftraggeber', 'adressanzeige']
    list_fields_labels = ['Bezeichnung', 'Auftraggeber', 'Adresse']
    readonly_fields = ['adressanzeige']
    show_alkis = True
    map_feature_tooltip_field = 'bezeichnung'
    address = False
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + ' (Auftraggeber: ' + self.auftraggeber + ')'


@python_2_unicode_compatible
class Baustellen_Fotodokumentation_Fotos(models.Model):
  id = models.AutoField(primary_key=True)
  parent = models.ForeignKey(Baustellen_Fotodokumentation_Baustellen, on_delete=models.CASCADE, db_column='baustellen_fotodokumentation_baustelle', to_field='uuid')
  dateiname_original = models.CharField('Original-Dateiname', default=settings.READONLY_FIELD_DEFAULT, max_length=255)
  status = models.CharField('Status', max_length=255, choices=STATUS_BAUSTELLEN_FOTODOKUMENTATION)
  aufnahmedatum = models.DateField('Aufnahmedatum')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.FOTO_PATH_PREFIX + 'baustellen_fotodokumentation'), max_length=255)

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'baustellen_fotodokumentation_fotos'
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
    return unicode(self.parent) + ', ' + self.status + ', mit Aufnahmedatum ' + datetime.strptime(unicode(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y') 


@python_2_unicode_compatible
class Baustellen_geplant(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = NullCharField('Straße', max_length=255, blank=True)
  lagebeschreibung = NullCharField('Lagebeschreibung', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  kurzbeschreibung = models.CharField('Kurzbeschreibung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  projektbezeichnung = NullCharField('Projektbezeichnung', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  sparte = MultiSelectField('Sparte(n)', max_length=255, choices=SPARTEN_BAUSTELLEN)
  verkehrliche_lage = MultiSelectField('Verkehrliche Lage(n)', max_length=255, choices=VERKEHRLICHE_LAGEN_BAUSTELLEN)
  beginn = models.DateField('Beginn', default=date.today)
  ende = models.DateField('Ende', default=date.today)
  auftraggeber = NullCharField('Auftraggeber', max_length=255, choices=AUFTRAGGEBER_BAUSTELLEN, blank=True)
  ansprechpartner = models.CharField('Ansprechpartner', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.MultiPolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'baustellen_geplant'
    verbose_name = 'Baustellen (geplant)'
    verbose_name_plural = 'Baustellen (geplant)'
    description = 'Baustellen (geplant) in der Hanse- und Universitätsstadt Rostock und Umgebung'
    list_fields = ['uuid', 'bezeichnung', 'ansprechpartner']
    list_fields_labels = ['UUID', 'Bezeichnung', 'Ansprechpartner']
    show_alkis = True
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = True
    geometry_type = 'MultiPolygonField'
  
  def __str__(self):
    if self.strasse_name and self.lagebeschreibung:
      return self.bezeichnung + ', ' + self.strasse_name + ' – ' + self.lagebeschreibung + ' (UUID: ' + str(self.uuid) + ')'
    elif self.strasse_name:
      return self.bezeichnung + ', ' + self.strasse_name + ' (UUID: ' + str(self.uuid) + ')'
    elif self.lagebeschreibung:
      return self.bezeichnung + ' – ' + self.lagebeschreibung + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Begegnungszentren(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices=TRAEGER_ART)
  barrierefrei = models.NullBooleanField('barrierefrei')
  oeffnungszeiten = NullCharField('Öffnungszeiten', max_length=255, blank=True)
  telefon = NullCharField('Telefon', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  fax = NullCharField('Fax', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = NullCharField('E-Mail', max_length=255, blank=True, validators=[EmailValidator(message=email_message)])
  website = NullCharField('Website', max_length=255, blank=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'begegnungszentren'
    verbose_name = 'Begegnungszentrum'
    verbose_name_plural = 'Begegnungszentren'
    description = 'Begegnungszentren in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung']
    list_fields_labels = ['UUID', 'Bezeichnung']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'
      
      
@python_2_unicode_compatible
class Behinderteneinrichtungen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices=TRAEGER_ART)
  plaetze = models.PositiveSmallIntegerField('Plätze', blank=True)
  telefon = NullCharField('Telefon', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  fax = NullCharField('Fax', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = NullCharField('E-Mail', max_length=255, blank=True, validators=[EmailValidator(message=email_message)])
  website = NullCharField('Website', max_length=255, blank=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'behinderteneinrichtungen'
    verbose_name = 'Behinderteneinrichtung'
    verbose_name_plural = 'Behinderteneinrichtungen'
    description = 'Behinderteneinrichtungen in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung', 'traeger_bezeichnung']
    list_fields_labels = ['UUID', 'Bezeichnung', 'Träger']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Bildungstraeger(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  klassen = MultiSelectField('Klassen', max_length=255, choices=KLASSEN_BILDUNGSTRAEGER)
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices=TRAEGER_ART)
  barrierefrei = models.NullBooleanField('barrierefrei')
  oeffnungszeiten = NullCharField('Öffnungszeiten', max_length=255, blank=True)
  telefon = NullCharField('Telefon', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  fax = NullCharField('Fax', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = NullCharField('E-Mail', max_length=255, blank=True, validators=[EmailValidator(message=email_message)])
  website = NullCharField('Website', max_length=255, blank=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'bildungstraeger'
    verbose_name = 'Bildungsträger'
    verbose_name_plural = 'Bildungsträger'
    description = 'Bildungsträger in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung']
    list_fields_labels = ['UUID', 'Bezeichnung']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Carsharing_Stationen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  anzahl_fahrzeuge = models.PositiveSmallIntegerField('Anzahl der Fahrzeuge', blank=True)
  anbieter = models.CharField('Anbieter', max_length=255, choices=ANBIETER_CARSHARING)
  bemerkungen = NullCharField('Bemerkungen', max_length=500, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  telefon = NullCharField('Telefon', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  website = NullCharField('Website', max_length=255, blank=True, validators=[URLValidator(message=url_message)])
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'carsharing_stationen'
    verbose_name = 'Carsharing-Station'
    verbose_name_plural = 'Carsharing-Stationen'
    description = 'Carsharing-Stationen in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung', 'adressanzeige', 'anbieter']
    list_fields_labels = ['Bezeichnung', 'Adresse', 'Anbieter']
    readonly_fields = ['adressanzeige']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = False
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    return self.bezeichnung + (', ' + self.adressanzeige if self.adressanzeige else '') + ' (' + self.anbieter + ')'


@python_2_unicode_compatible
class Containerstellplaetze(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  gueltigkeit_bis = models.DateField('Außerbetriebstellung', blank=True)
  privat = models.NullBooleanField('privat')
  id_containerstellplatz = NullCharField('ID', max_length=5, validators=[RegexValidator(regex=id_containerstellplatz_regex, message=id_containerstellplatz_message)], blank=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  anzahl_glas = models.PositiveSmallIntegerField('Anzahl Glas normal', blank=True)
  anzahl_glas_unterflur = models.PositiveSmallIntegerField('Anzahl Glas unterflur', blank=True)
  bewirtschafter_id_glas = models.PositiveSmallIntegerField('Bewirtschafter Glas', choices=BEWIRTSCHAFTER_GLAS_CONTAINERSTELLPLAETZE, blank=True, null=True)
  bewirtschafter_glas = models.CharField('Bewirtschafter Glas', max_length=255, editable=False)
  anzahl_papier = models.PositiveSmallIntegerField('Anzahl Papier normal', blank=True)
  anzahl_papier_unterflur = models.PositiveSmallIntegerField('Anzahl Papier unterflur', blank=True)
  bewirtschafter_id_papier = models.PositiveSmallIntegerField('Bewirtschafter Papier', choices=BEWIRTSCHAFTER_PAPIER_CONTAINERSTELLPLAETZE, blank=True, null=True)
  bewirtschafter_papier = models.CharField('Bewirtschafter Papier', max_length=255, editable=False)
  anzahl_altkleider = models.PositiveSmallIntegerField('Anzahl Altkleider', blank=True)
  bewirtschafter_id_altkleider = models.PositiveSmallIntegerField('Bewirtschafter Altkleider', choices=BEWIRTSCHAFTER_ALTKLEIDER_CONTAINERSTELLPLAETZE, blank=True, null=True)
  bewirtschafter_altkleider = models.CharField('Bewirtschafter Altkleider', max_length=255, editable=False)
  inbetriebnahmejahr = PositiveSmallIntegerRangeField('Inbetriebnahmejahr', min_value=1900, max_value=current_year(), blank=True)
  flaeche = models.DecimalField('Stellplatzfläche (in m²)', max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Stellplatzfläche muss mindestens 0,01 m² groß sein.')], blank=True)
  inventarnummer_grundundboden = NullCharField('Inventarnummer Grund und Boden', max_length=8, blank=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  inventarnummer = NullCharField('Inventarnummer Stellplatz', max_length=8, blank=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  inventarnummer_zaun = NullCharField('Inventarnummer Zaun', max_length=8, blank=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  anschaffungswert = models.DecimalField('Anschaffungswert (in €)', max_digits=7, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Anschaffungswert muss mindestens 0,01 € betragen.')], blank=True)
  bewirtschafter_id_grundundboden = models.PositiveSmallIntegerField('Bewirtschafter Grund und Boden', choices=BEWIRTSCHAFTER_GRUNDUNDBODEN_CONTAINERSTELLPLAETZE, blank=True, null=True)
  bewirtschafter_grundundboden = models.CharField('Bewirtschafter Grund und Boden', max_length=255, editable=False)
  oeffentliche_widmung = models.NullBooleanField('öffentliche Widmung')
  art_eigentumserwerb = NullCharField('Art des Eigentumserwerbs Stellplatz', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art_eigentumserwerb_zaun = NullCharField('Art des Eigentumserwerbs Zaun', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  vertraege = NullCharField('Verträge', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bga_grundundboden = models.NullBooleanField('Zuordnung BgA Grund und Boden')
  bga = models.NullBooleanField('Zuordnung BgA Stellplatz')
  bga_zaun = models.NullBooleanField('Zuordnung BgA Zaun')
  winterdienst_a = models.NullBooleanField('Winterdienst A')
  winterdienst_b = models.NullBooleanField('Winterdienst B')
  winterdienst_c = models.NullBooleanField('Winterdienst C')
  bemerkungen = NullCharField('Bemerkungen', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.FOTO_PATH_PREFIX + 'containerstellplaetze'), max_length=255, blank=True)
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'containerstellplaetze'
    verbose_name = 'Containerstellplatz'
    verbose_name_plural = 'Containerstellplätze'
    description = 'Containerstellplätze in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['gueltigkeit_bis', 'privat', 'id_containerstellplatz', 'bezeichnung', 'adressanzeige']
    list_fields_with_date = ['gueltigkeit_bis']
    list_fields_labels = ['Außerbetriebstellung', 'privat', 'ID', 'Bezeichnung', 'Adresse']
    readonly_fields = ['adressanzeige']
    show_alkis = True
    map_feature_tooltip_field = 'id_containerstellplatz'
    address = False
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    return 'Containerstellplatz' + (' mit ID ' + self.id_containerstellplatz + ' und Bezeichnung ' if self.id_containerstellplatz else ' mit Bezeichnung ') + self.bezeichnung + (', ' + self.adressanzeige if self.adressanzeige else '')


@python_2_unicode_compatible
class Fairtrade(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art = models.CharField('Art', max_length=255, choices=ART_FAIRTRADE)
  betreiber = NullCharField('Betreiber', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  barrierefrei = models.NullBooleanField('barrierefrei')
  oeffnungszeiten = NullCharField('Öffnungszeiten', max_length=255, blank=True)
  telefon = NullCharField('Telefon', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  fax = NullCharField('Fax', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = NullCharField('E-Mail', max_length=255, blank=True, validators=[EmailValidator(message=email_message)])
  website = NullCharField('Website', max_length=255, blank=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'fairtrade'
    verbose_name = 'Fair Trade'
    verbose_name_plural = 'Fair Trade'
    description = 'Fair Trade in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'bezeichnung']
    list_fields_labels = ['UUID', 'Art', 'Bezeichnung']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Fliessgewaesser(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  nummer = models.CharField('Nummer', max_length=255)
  bezeichnung = NullCharField('Bezeichnung', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ordnung = PositiveSmallIntegerRangeField('Ordnung', min_value=1, max_value=2, blank=True)
  art = models.CharField('Art', max_length=255, choices=ART_FLIESSGEWAESSER)
  nennweite = models.PositiveIntegerField('Nennweite (in Millimetern)', blank=True)
  geometrie = models.LineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'fliessgewaesser'
    verbose_name = 'Fließgewässer'
    verbose_name_plural = 'Fließgewässer'
    description = 'Fließgewässer in der Hanse- und Universitätsstadt Rostock und Umgebung'
    list_fields = ['uuid', 'nummer', 'bezeichnung', 'ordnung', 'art']
    list_fields_labels = ['UUID', 'Nummer', 'Bezeichnung', 'Ordnung', 'Art']
    show_alkis = True
    map_feature_tooltip_field = 'nummer'
    address = False
    address_optional = False
    geometry_type = 'LineString'
  
  def __str__(self):
    if self.ordnung:
      output_ordnung = ', ' + str(self.ordnung) + '. Ordnung'
    else:
      output_ordnung = ''
    return self.art + output_ordnung + ', Nummer ' + self.nummer + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Gutachterfotos(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = NullCharField('Adresse/Straße', max_length=255, blank=True)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  bearbeiter = NullCharField('Bearbeiter', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkung = NullCharField('Bemerkung', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  aufnahmedatum = models.DateField('Aufnahmedatum')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.FOTO_PATH_PREFIX + 'gutachterfotos'), max_length=255)
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'gutachterfotos'
    verbose_name = 'Gutachterfoto'
    verbose_name_plural = 'Gutachterfotos'
    description = 'Gutachterfotos der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'adressanzeige', 'bearbeiter', 'datum', 'aufnahmedatum']
    list_fields_with_date = ['datum', 'aufnahmedatum']
    list_fields_labels = ['UUID', 'Adresse', 'Bearbeiter', 'Datum', 'Aufnahmedatum']
    readonly_fields = ['adressanzeige']
    show_alkis = True
    map_feature_tooltip_field = 'uuid'
    address = True
    address_optional = True
    geometry_type = 'Point'
  
  def __str__(self):
    return 'Gutachterfoto mit Aufnahmedatum ' + datetime.strptime(unicode(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y') + (', ' + self.adressanzeige if self.adressanzeige else '') + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Haltestellenkataster_Haltestellen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  gemeindeteil_name = NullCharField('Gemeindeteil', max_length=255, blank=True)
  hst_bezeichnung = models.CharField('Haltestellenbezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_hafas_id = NullCharField('HAFAS-ID', max_length=8, blank=True, validators=[RegexValidator(regex=hafas_id_regex, message=hafas_id_message)])
  hst_bus_bahnsteigbezeichnung = NullCharField('Bus-/Bahnsteigbezeichnung', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_richtung = NullCharField('Richtungsinformation', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_kategorie = NullCharField('Haltestellenkategorie', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  hst_linien = MultiSelectField('bedienende Linie(n)', max_length=255, choices=LINIEN_HALTESTELLEN, blank=True, null=True)
  hst_rsag = models.NullBooleanField('bedient durch Rostocker Straßenbahn AG?')
  hst_rebus = models.NullBooleanField('bedient durch rebus Regionalbus Rostock GmbH?')
  hst_nur_ausstieg = models.NullBooleanField('nur Ausstieg?')
  hst_nur_einstieg = models.NullBooleanField('nur Einstieg?')
  hst_verkehrsmittelklassen = MultiSelectField('Verkehrsmittelklasse(n)', max_length=255, choices=VERKEHRSMITTELKLASSEN_HALTESTELLEN)
  hst_fahrgastzahl = models.PositiveIntegerField('durchschnittliche Fahrgastzahl', blank=True)
  bau_typ = MultiSelectField('Typ', max_length=255, choices=TYP_HALTESTELLEN, blank=True, null=True)
  bau_wartebereich_laenge = models.DecimalField('Länge des Wartebereichs (in m)', max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Wartebereich muss mindestens 0,01 m lang sein.')], blank=True)
  bau_wartebereich_breite = models.DecimalField('Breite des Wartebereichs (in m)', max_digits=5, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Wartebereich muss mindestens 0,01 m breit sein.')], blank=True)
  bau_befestigungsart_aufstellflaeche_bus = NullCharField('Befestigungsart der Aufstellfläche Bus', max_length=255, choices=BEFESTIGUNGSART_HALTESTELLEN, blank=True)
  bau_zustand_aufstellflaeche_bus = NullCharField('Zustand der Aufstellfläche Bus', max_length=255, choices=SCHAEDEN_HALTESTELLEN, blank=True)
  bau_befestigungsart_warteflaeche = NullCharField('Befestigungsart der Wartefläche', max_length=255, choices=BEFESTIGUNGSART_HALTESTELLEN, blank=True)
  bau_zustand_warteflaeche = NullCharField('Zustand der Wartefläche', max_length=255, choices=SCHAEDEN_HALTESTELLEN, blank=True)
  bf_einstieg = models.NullBooleanField('barrierefreier Einstieg vorhanden?')
  bf_zu_abgaenge = models.NullBooleanField('barrierefreie Zu- und Abgänge vorhanden?')
  bf_bewegungsraum = models.NullBooleanField('barrierefreier Bewegungsraum vorhanden?')
  tl_auffindestreifen = models.NullBooleanField('Taktiles Leitsystem: Auffindestreifen vorhanden?')
  tl_auffindestreifen_ausfuehrung = NullCharField('Taktiles Leitsystem: Ausführung Auffindestreifen', max_length=255, choices=AUSFUEHRUNG_HALTESTELLEN, blank=True)
  tl_auffindestreifen_breite = models.PositiveIntegerField('Taktiles Leitsystem: Breite des Auffindestreifens (in cm)', blank=True)
  tl_einstiegsfeld = models.NullBooleanField('Taktiles Leitsystem: Einstiegsfeld vorhanden?')
  tl_einstiegsfeld_ausfuehrung = NullCharField('Taktiles Leitsystem: Ausführung Einstiegsfeld', max_length=255, choices=AUSFUEHRUNG_HALTESTELLEN, blank=True)
  tl_einstiegsfeld_breite = models.PositiveIntegerField('Taktiles Leitsystem: Breite des Einstiegsfelds (in cm)', blank=True)
  tl_leitstreifen = models.NullBooleanField('Taktiles Leitsystem: Leitstreifen vorhanden?')
  tl_leitstreifen_ausfuehrung = NullCharField('Taktiles Leitsystem: Ausführung Leitstreifen', max_length=255, choices=AUSFUEHRUNG_HALTESTELLEN, blank=True)
  tl_leitstreifen_laenge = models.PositiveIntegerField('Taktiles Leitsystem: Länge des Leitstreifens (in cm)', blank=True)
  tl_aufmerksamkeitsfeld = models.NullBooleanField('Aufmerksamkeitsfeld (1. Tür) vorhanden?')
  tl_bahnsteigkante_visuell = models.NullBooleanField('Bahnsteigkante visuell erkennbar?')
  tl_bahnsteigkante_taktil = models.NullBooleanField('Bahnsteigkante taktil erkennbar?')
  as_h_mast = models.NullBooleanField('Mast vorhanden?')
  as_papierkorb = models.NullBooleanField('Papierkorb vorhanden?')
  as_fahrgastunterstand = models.NullBooleanField('Fahrgastunterstand vorhanden?')
  as_sitzbank_mit_armlehne = models.NullBooleanField('Sitzbank mit Armlehne vorhanden?')
  as_sitzbank_ohne_armlehne = models.NullBooleanField('Sitzbank ohne Armlehne vorhanden?')
  as_gelaender = models.NullBooleanField('Geländer vorhanden?')
  as_fahrplanvitrine = models.NullBooleanField('Fahrplanvitrine vorhanden?')
  as_tarifinformation = models.NullBooleanField('Tarifinformation vorhanden?')
  as_liniennetzplan = models.NullBooleanField('Liniennetzplan vorhanden?')
  as_fahrplan = models.NullBooleanField('Fahrplan vorhanden?')
  as_fahrausweisautomat = models.NullBooleanField('Fahrausweisautomat vorhanden?')
  as_lautsprecher = models.NullBooleanField('Lautsprecher vorhanden?')
  as_dfi = models.NullBooleanField('Dynamisches Fahrgastinformationssystem vorhanden?')
  as_anfragetaster = models.NullBooleanField('Anfragetaster vorhanden?')
  as_blindenschrift = models.NullBooleanField('Haltestellen-/Linieninformationen in Blindenschrift vorhanden?')
  as_beleuchtung = models.NullBooleanField('Beleuchtung vorhanden?')
  as_hinweis_warnblinklicht_ein = models.NullBooleanField('Hinweis „Warnblinklicht ein“ vorhanden?')
  bfe_park_and_ride = models.NullBooleanField('P+R-Parkplatz in Umgebung vorhanden?')
  bfe_fahrradabstellmoeglichkeit = models.NullBooleanField('Fahrradabstellmöglichkeit in Umgebung vorhanden?')
  bfe_querungshilfe = models.NullBooleanField('Querungshilfe in Umgebung vorhanden?')
  bfe_fussgaengerueberweg = models.NullBooleanField('Fußgängerüberweg in Umgebung vorhanden?')
  bfe_seniorenheim = models.NullBooleanField('Seniorenheim in Umgebung vorhanden?')
  bfe_pflegeeinrichtung = models.NullBooleanField('Pflegeeinrichtung in Umgebung vorhanden?')
  bfe_medizinische_versorgungseinrichtung = models.NullBooleanField('Medizinische Versorgungseinrichtung in Umgebung vorhanden?')
  bemerkungen = models.TextField('Bemerkungen', max_length=500, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bearbeiter = models.CharField('Bearbeiter', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'haltestellenkataster_haltestellen'
    verbose_name = 'Haltestellenkataster (Haltestelle)'
    verbose_name_plural = 'Haltestellenkataster (Haltestellen)'
    description = 'Haltestellen im Rahmen des Haltestellenkatasters der Hanse- und Universitätsstadt Rostock'
    list_fields = ['id', 'gemeindeteil_name', 'hst_bezeichnung', 'hst_hafas_id', 'hst_bus_bahnsteigbezeichnung', 'bearbeiter']
    list_fields_labels = ['Haltestellennummer', 'Gemeindeteil', 'Haltestellenbezeichnung', 'HAFAS-ID', 'Bus-/Bahnsteigbezeichnung', 'Bearbeiter']
    list_fields_with_number = ['id']
    readonly_fields = ['gemeindeteil_name']
    show_alkis = True
    map_feature_tooltip_field = 'hst_bezeichnung'
    address = False
    address_optional = False
    geometry_type = 'Point'
  
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


@python_2_unicode_compatible
class Haltestellenkataster_Fotos(models.Model):
  id = models.AutoField(primary_key=True)
  parent = models.ForeignKey(Haltestellenkataster_Haltestellen, on_delete=models.CASCADE, db_column='haltestellenkataster_haltestelle', to_field='uuid')
  dateiname_original = models.CharField('Original-Dateiname', default=settings.READONLY_FIELD_DEFAULT, max_length=255)
  motiv = models.CharField('Motiv', max_length=255, choices=MOTIVE_HALTESTELLEN)
  aufnahmedatum = models.DateField('Aufnahmedatum')
  foto = models.ImageField('Foto', storage=OverwriteStorage(), upload_to=path_and_rename(settings.FOTO_PATH_PREFIX + 'haltestellenkataster'), max_length=255)

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'haltestellenkataster_fotos'
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
    return unicode(self.parent) + ', Motiv ' + self.motiv + ', mit Aufnahmedatum ' + datetime.strptime(unicode(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y') 


@python_2_unicode_compatible
class Hospize(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices=TRAEGER_ART)
  plaetze = models.PositiveSmallIntegerField('Plätze', blank=True)
  telefon = NullCharField('Telefon', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  fax = NullCharField('Fax', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = NullCharField('E-Mail', max_length=255, blank=True, validators=[EmailValidator(message=email_message)])
  website = NullCharField('Website', max_length=255, blank=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'hospize'
    verbose_name = 'Hospiz'
    verbose_name_plural = 'Hospize'
    description = 'Hospize in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung', 'traeger_bezeichnung']
    list_fields_labels = ['UUID', 'Bezeichnung', 'Träger']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Hundetoiletten(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  id_hundetoilette = models.CharField('ID', default=settings.READONLY_FIELD_DEFAULT, max_length=8)
  gueltigkeit_bis = models.DateField('Außerbetriebstellung', blank=True)
  art = models.CharField('Art', max_length=255, choices=ART_HUNDETOILETTE)
  bewirtschafter_id = models.PositiveSmallIntegerField('Bewirtschafter', choices=BEWIRTSCHAFTER_HUNDETOILETTE)
  bewirtschafter = models.CharField('Bewirtschafter', max_length=255, editable=False)
  pflegeobjekt = models.CharField('Pflegeobjekt', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  inventarnummer = NullCharField('Inventarnummer', max_length=8, blank=True, validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)])
  aufstellungsjahr = PositiveSmallIntegerRangeField('Aufstellungsjahr', min_value=1900, max_value=current_year(), blank=True)
  anschaffungswert = models.DecimalField('Anschaffungswert (in €)', max_digits=6, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Der Anschaffungswert muss mindestens 0,01 € betragen.')], blank=True)
  bemerkungen = NullCharField('Bemerkungen', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'hundetoiletten'
    verbose_name = 'Hundetoilette'
    verbose_name_plural = 'Hundetoiletten'
    description = 'Hundetoiletten im Eigentum der Hanse- und Universitätsstadt Rostock'
    list_fields = ['gueltigkeit_bis', 'id_hundetoilette', 'art', 'pflegeobjekt', 'adressanzeige', 'bewirtschafter']
    list_fields_with_date = ['gueltigkeit_bis']
    list_fields_labels = ['Außerbetriebstellung', 'ID', 'Art', 'Pflegeobjekt', 'Adresse', 'Bewirtschafter']
    readonly_fields = ['id_hundetoilette', 'adressanzeige']
    show_alkis = True
    map_feature_tooltip_field = 'id_hundetoilette'
    address = False
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    return 'Hundetoilette mit ID ' + self.id_hundetoilette + ', Art ' + self.art + ', im Pflegeobjekt ' + self.pflegeobjekt + (', ' + self.adressanzeige if self.adressanzeige else '') + ', mit Bewirtschafter ' + self.bewirtschafter


@python_2_unicode_compatible
class Kinderjugendbetreuung(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices=TRAEGER_ART)
  barrierefrei = models.NullBooleanField('barrierefrei')
  oeffnungszeiten = NullCharField('Öffnungszeiten', max_length=255, blank=True)
  telefon = NullCharField('Telefon', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  fax = NullCharField('Fax', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = NullCharField('E-Mail', max_length=255, blank=True, validators=[EmailValidator(message=email_message)])
  website = NullCharField('Website', max_length=255, blank=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'kinder_jugendbetreuung'
    verbose_name = 'Kinder- und Jugendbetreuung'
    verbose_name_plural = 'Kinder- und Jugendbetreuung'
    description = 'Kinder- und Jugendbetreuung in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung']
    list_fields_labels = ['UUID', 'Bezeichnung']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Kunstimoeffentlichenraum(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = NullCharField('Adresse/Straße', max_length=255, blank=True)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  ausfuehrung = NullCharField('Ausführung', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  schoepfer = NullCharField('Schöpfer', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  entstehungsjahr = PositiveSmallIntegerRangeField('Entstehungsjahr', min_value=1218, max_value=current_year(), blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'kunst_im_oeffentlichen_raum'
    verbose_name = 'Kunst im öffentlichen Raum'
    verbose_name_plural = 'Kunst im öffentlichen Raum'
    description = 'Kunst im öffentlichen Raum der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'bezeichnung', 'schoepfer', 'entstehungsjahr']
    list_fields_labels = ['UUID', 'Bezeichnung', 'Schöpfer', 'Entstehungsjahr']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = True
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


@python_2_unicode_compatible
class Meldedienst_flaechenhaft(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = NullCharField('Adresse/Straße', max_length=255, blank=True)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  art = models.CharField('Art', max_length=255, choices=ART_MELDEDIENST_FLAECHENHAFT)
  bearbeiter = models.CharField('Bearbeiter', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkung = NullCharField('Bemerkung', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  gueltigkeit_von = models.DateField(default=date.today, editable=False)
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'meldedienst_flaechenhaft'
    verbose_name = 'Meldedienst (flächenhaft)'
    verbose_name_plural = 'Meldedienst (flächenhaft)'
    description = 'Meldedienst (flächenhaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'adressanzeige', 'bearbeiter', 'gueltigkeit_von']
    list_fields_with_date = ['gueltigkeit_von']
    list_fields_labels = ['UUID', 'Art', 'Adresse', 'Bearbeiter', 'geändert']
    readonly_fields = ['adressanzeige']
    show_alkis = True
    map_feature_tooltip_field = 'uuid'
    address = True
    address_optional = True
    geometry_type = 'PolygonField'
  
  def __str__(self):
    return self.art + (', ' + self.adressanzeige if self.adressanzeige else '') + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Meldedienst_punkthaft(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = NullCharField('Adresse/Straße', max_length=255, blank=True)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  art = models.CharField('Art', max_length=255, choices=ART_MELDEDIENST_PUNKTHAFT)
  bearbeiter = models.CharField('Bearbeiter', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  bemerkung = NullCharField('Bemerkung', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  gueltigkeit_von = models.DateField(default=date.today, editable=False)
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'meldedienst_punkthaft'
    verbose_name = 'Meldedienst (punkthaft)'
    verbose_name_plural = 'Meldedienst (punkthaft)'
    description = 'Meldedienst (punkthaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'adressanzeige', 'bearbeiter', 'gueltigkeit_von']
    list_fields_with_date = ['gueltigkeit_von']
    list_fields_labels = ['UUID', 'Art', 'Adresse', 'Bearbeiter', 'geändert']
    readonly_fields = ['adressanzeige']
    show_alkis = True
    map_feature_tooltip_field = 'uuid'
    address = True
    address_optional = True
    geometry_type = 'Point'
  
  def __str__(self):
    return self.art + (', ' + self.adressanzeige if self.adressanzeige else '') + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Parkmoeglichkeiten(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = NullCharField('Adresse/Straße', max_length=255, blank=True)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  art = models.CharField('Art', max_length=255, choices=ART_PARKMOEGLICHKEITEN)
  standort = models.CharField('Standort', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  betreiber = NullCharField('Betreiber', max_length=255, blank=True, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  stellplaetze_pkw = models.PositiveSmallIntegerField('Pkw-Stellplätze', blank=True)
  stellplaetze_wohnmobil = models.PositiveSmallIntegerField('Wohnmobil-Stellplätze', blank=True)
  stellplaetze_bus = models.PositiveSmallIntegerField('Bus-Stellplätze', blank=True)
  gebuehren_halbe_stunde = models.DecimalField('Gebühren ½ h (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren je ½ h müssen mindestens 0,01 € betragen.')], blank=True)
  gebuehren_eine_stunde = models.DecimalField('Gebühren 1 h (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren je 1 h müssen mindestens 0,01 € betragen.')], blank=True)
  gebuehren_zwei_stunden = models.DecimalField('Gebühren 2 h (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren je 2 h müssen mindestens 0,01 € betragen.')], blank=True)
  gebuehren_ganztags = models.DecimalField('Gebühren ganztags (in €)', max_digits=3, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'), 'Die Gebühren ganztags müssen mindestens 0,01 € betragen.')], blank=True)
  gebuehren_anmerkungen = NullCharField('Anmerkungen zu den Gebühren', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'parkmoeglichkeiten'
    verbose_name = 'Parkmöglichkeit'
    verbose_name_plural = 'Parkmöglichkeiten'
    description = 'Parkmöglichkeiten in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'standort']
    list_fields_labels = ['UUID', 'Art', 'Standort']
    show_alkis = False
    map_feature_tooltip_field = 'standort'
    address = True
    address_optional = True
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


@python_2_unicode_compatible
class Pflegeeinrichtungen(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  art = models.CharField('Art', max_length=255, choices=ART_PFLEGEEINRICHTUNGEN)
  traeger_bezeichnung = models.CharField('Träger', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  traeger_art = models.CharField('Art des Trägers', max_length=255, choices=TRAEGER_ART)
  plaetze = models.PositiveSmallIntegerField('Plätze', blank=True)
  telefon = NullCharField('Telefon', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  fax = NullCharField('Fax', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = NullCharField('E-Mail', max_length=255, blank=True, validators=[EmailValidator(message=email_message)])
  website = NullCharField('Website', max_length=255, blank=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'pflegeeinrichtungen'
    verbose_name = 'Pflegeeinrichtung'
    verbose_name_plural = 'Pflegeeinrichtungen'
    description = 'Pflegeeinrichtungen in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'bezeichnung', 'traeger_bezeichnung']
    list_fields_labels = ['UUID', 'Art', 'Bezeichnung', 'Träger']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ' (' + self.art + '), ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'


@python_2_unicode_compatible
class Vereine(models.Model):
  id = models.AutoField(primary_key=True)
  uuid = models.UUIDField('UUID', default=uuid.uuid1, unique=True, editable=False)
  strasse_name = models.CharField('Adresse', max_length=255)
  hausnummer = NullCharField(max_length=4, blank=True)
  hausnummer_zusatz = NullCharField(max_length=2, blank=True)
  klassen = MultiSelectField('Kategorien', max_length=255, choices=KLASSEN_VEREINE)
  bezeichnung = models.CharField('Bezeichnung', max_length=255, validators=[RegexValidator(regex=doppelleerzeichen_regex, message=doppelleerzeichen_message), RegexValidator(regex=anfuehrungszeichen_regex, message=anfuehrungszeichen_message), RegexValidator(regex=apostroph_regex, message=apostroph_message), RegexValidator(regex=gravis_regex, message=gravis_message)])
  barrierefrei = models.NullBooleanField('barrierefrei')
  telefon = NullCharField('Telefon', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  fax = NullCharField('Fax', max_length=255, blank=True, validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)])
  email = NullCharField('E-Mail', max_length=255, blank=True, validators=[EmailValidator(message=email_message)])
  website = NullCharField('Website', max_length=255, blank=True, validators=[URLValidator(message=url_message)])
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = settings.DATABASE_TABLES_SCHEMA + '\".\"' + 'vereine'
    verbose_name = 'Verein'
    verbose_name_plural = 'Vereine'
    description = 'Vereine in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['bezeichnung', 'klassen']
    list_fields_labels = ['Bezeichnung', 'Kategorien']
    show_alkis = False
    map_feature_tooltip_field = 'bezeichnung'
    address = True
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    if self.hausnummer_zusatz:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + self.hausnummer_zusatz + ' (UUID: ' + str(self.uuid) + ')'
    else:
      return self.bezeichnung + ', ' + self.strasse_name + ' ' + self.hausnummer + ' (UUID: ' + str(self.uuid) + ')'

  def get_klassen_display(self):
    return ', '.join(self.klassen)


@receiver(post_delete, sender=Aufteilungsplaene_Wohnungseigentumsgesetz)
def aufteilungsplan_wohnungseigentumsgesetz_post_delete_handler(sender, instance, **kwargs):
  if instance.pdf:
    instance.pdf.delete(False)


@receiver(pre_save, sender=Baustellen_Fotodokumentation_Fotos)
def baustelle_fotodokumentation_pre_save_handler(sender, instance, **kwargs):
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
