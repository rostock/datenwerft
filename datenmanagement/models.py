# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from datetime import date, datetime
from decimal import *
from django.conf import settings
from django.contrib.gis.db import models
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator, MinValueValidator, RegexValidator, URLValidator
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from django.utils.encoding import force_text, python_2_unicode_compatible
#from select_multiple_field.models import SelectMultipleField
from multiselectfield import MultiSelectField
from PIL import Image, ExifTags

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


# Quelle: https://stackoverflow.com/questions/849142/how-to-limit-the-maximum-value-of-a-numeric-field-in-a-django-model    
class PositiveSmallIntegerRangeField(models.PositiveSmallIntegerField):
  def __init__(self, verbose_name=None, name=None, min_value=None, max_value=None, **kwargs):
    self.min_value, self.max_value = min_value, max_value
    models.PositiveSmallIntegerField.__init__(self, verbose_name, name, **kwargs)
    
  def formfield(self, **kwargs):
    defaults = {'min_value': self.min_value, 'max_value': self.max_value}
    defaults.update(kwargs)
    return super(PositiveSmallIntegerRangeField, self).formfield(**defaults)


models.options.DEFAULT_NAMES += ('description', 'list_fields', 'list_fields_labels', 'readonly_fields', 'object_title', 'foreign_key_label', 'show_alkis', 'map_feature_tooltip_field', 'address', 'address_optional', 'geometry_type', 'thumbs')


doppelleerzeichen_regex = r'^(?!.*  ).*$'
doppelleerzeichen_message = 'Der Text darf keine doppelten Leerzeichen enthalten.'
anfuehrungszeichen_regex = r'^(?!.*\").*$'
anfuehrungszeichen_message = 'Der Text darf keine doppelten Schreibmaschinensatz-Anführungszeichen (") enthalten. Stattdessen müssen die typographisch korrekten Anführungszeichen („“) verwendet werden.'
apostroph_regex = r'^(?!.*\').*$'
apostroph_message = 'Der Text darf keine einfachen Schreibmaschinensatz-Anführungszeichen (\') enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.'
gravis_regex = r'^(?!.*`).*$'
gravis_message = 'Der Text darf keine Gravis (`) enthalten. Stattdessen muss der typographisch korrekte Apostroph (’) verwendet werden.'
id_containerstellplatz_regex = r'^[0-9]{2}-[0-9]{2}$'
id_containerstellplatz_message = 'Die ID des Containerstellplatzes muss aus zwei Ziffern, einem Bindestrich und abermals zwei Ziffern bestehen.'
inventarnummer_regex = r'^[0-9]{8}$'
inventarnummer_message = 'Die Inventarnummer muss aus acht Ziffern bestehen.'
postleitzahl_regex = r'^[0-9]{5}$'
postleitzahl_message = 'Eine Postleitzahl muss immer aus genau fünf Ziffern bestehen.'
rufnummer_regex = r'^\+49 [1-9][0-9]{1,5} [0-9]{1,13}$'
rufnummer_message = 'Die Schreibweise von Rufnummern muss der Empfehlung E.123 der Internationalen Fernmeldeunion entsprechen und daher folgendes Format aufweisen: +49 381 3816256'
email_message = 'Die E-Mail-Adresse muss syntaktisch korrekt sein und daher folgendes Format aufweisen: abc-123.098_zyx@xyz-567.ghi.abc'
url_message = 'Die Adresse der Website muss syntaktisch korrekt sein und daher folgendes Format aufweisen: http[s]://abc-123.098_zyx.xyz-567/ghi/abc'


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

VERKEHRLICHE_LAGEN_BAUSTELLEN = (
  ('Fahrbahn', 'Fahrbahn'),
  ('Fußweg', 'Fußweg'),
  ('Radweg', 'Radweg'),
  ('Straße mit Begleitgrün', 'Straße mit Begleitgrün'),
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
    db_table = 'regis\".\"abfallbehaelter'
    verbose_name = 'Abfallbehälter'
    verbose_name_plural = 'Abfallbehälter'
    description = 'Abfallbehälter in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['gueltigkeit_bis', 'id_abfallbehaelter', 'typ', 'pflegeobjekt', 'adressanzeige', 'eigentuemer', 'bewirtschafter']
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
  pdf = models.FileField('PDF', upload_to=path_and_rename('pdf/aufteilungsplaene_wohnungseigentumsgesetz'), max_length=255)
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'regis\".\"aufteilungsplaene_wohnungseigentumsgesetz'
    verbose_name = 'Aufteilungsplan nach Wohnungseigentumsgesetz'
    verbose_name_plural = 'Aufteilungspläne nach Wohnungseigentumsgesetz'
    description = 'Aufteilungspläne nach Wohnungseigentumsgesetz in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'adressanzeige', 'bearbeiter', 'datum', 'abgeschlossenheitserklaerungsdatum']
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
    db_table = 'regis\".\"baustellen_fotodokumentation_baustellen'
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
  foto = models.ImageField('Foto', upload_to=path_and_rename('fotos/baustellen_fotodokumentation'), max_length=255)

  class Meta:
    managed = False
    db_table = 'regis\".\"baustellen_fotodokumentation_fotos'
    verbose_name = 'Baustellen-Fotodokumentation (Foto)'
    verbose_name_plural = 'Baustellen-Fotodokumentation (Fotos)'
    description = 'Fotos im Rahmen der Baustellen-Fotodokumentation in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['parent', 'status', 'aufnahmedatum', 'foto', 'dateiname_original']
    list_fields_labels = ['zu Baustelle', 'Status', 'Aufnahmedatum', 'Foto', 'Original-Dateiname']
    readonly_fields = ['dateiname_original']
    object_title = 'das Foto'
    foreign_key_label = 'Baustelle'
    thumbs = True
  
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
    db_table = 'regis\".\"baustellen_geplant'
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
    db_table = 'regis\".\"begegnungszentren'
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
    db_table = 'regis\".\"behinderteneinrichtungen'
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
    db_table = 'regis\".\"bildungstraeger'
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
  foto = models.ImageField('Foto', upload_to=path_and_rename('fotos/containerstellplaetze'), max_length=255, blank=True, null=True)
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'regis\".\"containerstellplaetze'
    verbose_name = 'Containerstellplatz'
    verbose_name_plural = 'Containerstellplätze'
    description = 'Containerstellplätze in der Hanse- und Universitätsstadt Rostock'
    list_fields = ['gueltigkeit_bis', 'privat', 'id_containerstellplatz', 'bezeichnung', 'adressanzeige']
    list_fields_labels = ['Außerbetriebstellung', 'privat', 'ID', 'Bezeichnung', 'Adresse']
    readonly_fields = ['adressanzeige']
    show_alkis = True
    map_feature_tooltip_field = 'id_containerstellplatz'
    address = False
    address_optional = False
    geometry_type = 'Point'
  
  def __str__(self):
    'Containerstellplatz' + (' mit ID ' + self.id_containerstellplatz + ' und Bezeichnung ' if self.id_containerstellplatz else ' mit Bezeichnung ') + self.bezeichnung + (', ' + self.adressanzeige if self.adressanzeige else '')


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
    db_table = 'regis\".\"fairtrade'
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
    db_table = 'regis\".\"fliessgewaesser'
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
  foto = models.ImageField('Foto', upload_to=path_and_rename('fotos/gutachterfotos'), max_length=255)
  adressanzeige = NullCharField('Adresse', max_length=255, blank=True)
  geometrie = models.PointField('Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'regis\".\"gutachterfotos'
    verbose_name = 'Gutachterfoto'
    verbose_name_plural = 'Gutachterfotos'
    description = 'Gutachterfotos der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'adressanzeige', 'bearbeiter', 'datum', 'aufnahmedatum']
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
    db_table = 'regis\".\"hospize'
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
    db_table = 'regis\".\"hundetoiletten'
    verbose_name = 'Hundetoilette'
    verbose_name_plural = 'Hundetoiletten'
    description = 'Hundetoiletten im Eigentum der Hanse- und Universitätsstadt Rostock'
    list_fields = ['gueltigkeit_bis', 'id_hundetoilette', 'art', 'pflegeobjekt', 'adressanzeige', 'bewirtschafter']
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
    db_table = 'regis\".\"kinder_jugendbetreuung'
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
    db_table = 'regis\".\"meldedienst_flaechenhaft'
    verbose_name = 'Meldedienst (flächenhaft)'
    verbose_name_plural = 'Meldedienst (flächenhaft)'
    description = 'Meldedienst (flächenhaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'adressanzeige', 'bearbeiter', 'gueltigkeit_von']
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
    db_table = 'regis\".\"meldedienst_punkthaft'
    verbose_name = 'Meldedienst (punkthaft)'
    verbose_name_plural = 'Meldedienst (punkthaft)'
    description = 'Meldedienst (punkthaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = ['uuid', 'art', 'adressanzeige', 'bearbeiter', 'gueltigkeit_von']
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
    db_table = 'regis\".\"parkmoeglichkeiten'
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
    db_table = 'regis\".\"pflegeeinrichtungen'
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
    db_table = 'regis\".\"vereine'
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


@receiver(post_save, sender=Baustellen_Fotodokumentation_Fotos)
def baustelle_fotodokumentation_post_save_handler(sender, instance, **kwargs):
  if instance.foto:
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
    else:
      BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      path = BASE_DIR + instance.foto.url
    rotate_image(path)
    if sender._meta.thumbs and sender._meta.thumbs == True:
      thumb_path = os.path.dirname(path) + '/thumbs'
      if not os.path.exists(thumb_path):
        os.mkdir(thumb_path)
      thumb_path = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      thumb_image(path, thumb_path)


@receiver(post_delete, sender=Baustellen_Fotodokumentation_Fotos)
def baustelle_fotodokumentation_post_delete_handler(sender, instance, **kwargs):
  if instance.foto:
    if sender._meta.thumbs and sender._meta.thumbs == True:
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


@receiver(post_save, sender=Containerstellplaetze)
def containerstellplatz_post_save_handler(sender, instance, **kwargs):
  if instance.foto:
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = settings.MEDIA_ROOT + '/' + instance.foto.url[len(settings.MEDIA_URL):]
    else:
      BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
      path = BASE_DIR + instance.foto.url
    rotate_image(path)
    if sender._meta.thumbs and sender._meta.thumbs == True:
      thumb_path = os.path.dirname(path) + '/thumbs'
      if not os.path.exists(thumb_path):
        os.mkdir(thumb_path)
      thumb_path = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      thumb_image(path, thumb_path)


@receiver(post_delete, sender=Containerstellplaetze)
def containerstellplatz_post_delete_handler(sender, instance, **kwargs):
  if instance.foto:
    if sender._meta.thumbs and sender._meta.thumbs == True:
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
    if sender._meta.thumbs and sender._meta.thumbs == True:
      thumb_path = os.path.dirname(path) + '/thumbs'
      if not os.path.exists(thumb_path):
        os.mkdir(thumb_path)
      thumb_path = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      thumb_image(path, thumb_path)


@receiver(post_delete, sender=Gutachterfotos)
def gutachterfoto_post_delete_handler(sender, instance, **kwargs):
  if instance.foto:
    if sender._meta.thumbs and sender._meta.thumbs == True:
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
