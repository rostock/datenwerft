import re
import uuid

from datetime import date, datetime, timezone
from decimal import *
from django.conf import settings
from django.contrib.gis.db import models
from django.db.models import signals
from django.core.validators import EmailValidator, MaxValueValidator, \
  MinValueValidator, RegexValidator, URLValidator
from zoneinfo import ZoneInfo

from . import models_codelist, constants_vars, fields, functions, storage


# Abfallbehälter

class Abfallbehaelter(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField(
    'Außerbetriebstellung', blank=True, null=True)
  id = models.CharField('ID', max_length=8, default='00000000')
  typ = models.ForeignKey(
    models_codelist.Typen_Abfallbehaelter,
    verbose_name='Typ',
    on_delete=models.SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='typen+',
    blank=True,
    null=True)
  aufstellungsjahr = fields.PositiveSmallIntegerRangeField(
    'Aufstellungsjahr', max_value=functions.current_year(), blank=True, null=True)
  eigentuemer = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=models.RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='eigentuemer+')
  bewirtschafter = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=models.RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='bewirtschafter+')
  pflegeobjekt = models.CharField(
    'Pflegeobjekt',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  inventarnummer = models.CharField(
    'Inventarnummer',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.inventarnummer_regex,
        message=constants_vars.inventarnummer_message
      )
    ]
  )
  anschaffungswert = models.DecimalField(
    'Anschaffungswert (in €)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.'),
      MaxValueValidator(
        Decimal('9999.99'),
        'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 9.999,99 € betragen.')],
    blank=True,
    null=True)
  haltestelle = models.BooleanField(
    'Lage an einer Haltestelle?', blank=True, null=True)
  sommer_mo = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen montags im Sommer', min_value=1, blank=True, null=True)
  sommer_di = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen dienstags im Sommer',
    min_value=1,
    blank=True,
    null=True)
  sommer_mi = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen mittwochs im Sommer',
    min_value=1,
    blank=True,
    null=True)
  sommer_do = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen donnerstags im Sommer',
    min_value=1,
    blank=True,
    null=True)
  sommer_fr = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen freitags im Sommer',
    min_value=1,
    blank=True,
    null=True)
  sommer_sa = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen samstags im Sommer',
    min_value=1,
    blank=True,
    null=True)
  sommer_so = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen sonntags im Sommer',
    min_value=1,
    blank=True,
    null=True)
  winter_mo = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen montags im Winter',
    min_value=1,
    blank=True,
    null=True)
  winter_di = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen dienstags im Winter',
    min_value=1,
    blank=True,
    null=True)
  winter_mi = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen mittwochs im Winter',
    min_value=1,
    blank=True,
    null=True)
  winter_do = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen donnerstags im Winter',
    min_value=1,
    blank=True,
    null=True)
  winter_fr = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen freitags im Winter',
    min_value=1,
    blank=True,
    null=True)
  winter_sa = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen samstags im Winter',
    min_value=1,
    blank=True,
    null=True)
  winter_so = fields.PositiveSmallIntegerRangeField(
    'Anzahl Leerungen sonntags im Winter',
    min_value=1,
    blank=True,
    null=True)
  bemerkungen = models.CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'typ': 'typ',
      'eigentuemer': 'bezeichnung',
      'bewirtschafter': 'bezeichnung'
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
    as_overlay = True
    heavy_load_limit = 500

  def __str__(self):
    return self.id + (' [Typ: ' + str(self.typ) + ']' if self.typ else '')

  def save(self, *args, **kwargs):
    super(Abfallbehaelter, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Abfallbehaelter, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Abfallbehaelter)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Abfallbehaelter)


# Angelverbotsbereiche

class Angelverbotsbereiche(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )])
  beschreibung = fields.NullTextField(
    'Beschreibung',
    max_length=1000,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  geometrie = models.LineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"angelverbotsbereiche_hro'
    verbose_name = 'Angelverbotsbereich'
    verbose_name_plural = 'Angelverbotsbereiche'
    description = 'Angelverbotsbereiche der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    geometry_type = 'LineString'
    as_overlay = True

  def __str__(self):
    return (self.bezeichnung if self.bezeichnung else 'ohne Bezeichnung') + \
           (' [Beschreibung: ' + str(self.beschreibung) + ']' if self.beschreibung else '')

  def save(self, *args, **kwargs):
    super(Angelverbotsbereiche, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Angelverbotsbereiche, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Angelverbotsbereiche)
signals.post_delete.connect(
  functions.remove_permissions,
  sender=Angelverbotsbereiche)


# Aufteilungspläne nach Wohnungseigentumsgesetz

class Aufteilungsplaene_Wohnungseigentumsgesetz(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  aktenzeichen = models.CharField(
    'Aktenzeichen', max_length=255, blank=True, null=True, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex, message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex, message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message)])
  datum_abgeschlossenheitserklaerung = models.DateField(
    'Datum der Abgeschlossenheitserklärung', blank=True, null=True)
  bearbeiter = models.CharField(
    'Bearbeiter', max_length=255, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex, message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex, message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message)])
  bemerkungen = models.CharField(
    'Bemerkungen', max_length=255, blank=True, null=True, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex, message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex, message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  pdf = models.FileField(
    'PDF',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PDF_PATH_PREFIX_PRIVATE +
      'aufteilungsplaene_wohnungseigentumsgesetz'),
    max_length=255)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"aufteilungsplaene_wohnungseigentumsgesetz_hro'
    verbose_name = 'Aufteilungsplan nach Wohnungseigentumsgesetz'
    verbose_name_plural = 'Aufteilungspläne nach Wohnungseigentumsgesetz'
    description = 'Aufteilungspläne nach Wohnungseigentumsgesetz in der Hanse- und ' \
                  'Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'aktenzeichen': 'Aktenzeichen',
      'datum_abgeschlossenheitserklaerung': 'Datum der Abgeschlossenheitserklärung',
      'pdf': 'PDF',
      'datum': 'Datum'}
    list_fields_with_date = ['datum_abgeschlossenheitserklaerung', 'datum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_field = 'datum'
    map_filter_fields = {
      'aktenzeichen': 'Aktenzeichen',
      'datum_abgeschlossenheitserklaerung': 'Datum der Abgeschlossenheitserklärung',
      'datum': 'Datum'}
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'

  def __str__(self):
    return 'Abgeschlossenheitserklärung mit Datum ' + datetime.strptime(str(self.datum),
                                                                        '%Y-%m-%d').strftime(
      '%d.%m.%Y') + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    super(
      Aufteilungsplaene_Wohnungseigentumsgesetz,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Aufteilungsplaene_Wohnungseigentumsgesetz,
      self).delete(
      *args,
      **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Aufteilungsplaene_Wohnungseigentumsgesetz)

signals.post_delete.connect(
  functions.delete_pdf,
  sender=Aufteilungsplaene_Wohnungseigentumsgesetz)

signals.post_delete.connect(functions.remove_permissions,
                            sender=Aufteilungsplaene_Wohnungseigentumsgesetz)


# Baudenkmale

class Baudenkmale(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  art = models.ForeignKey(
    models_codelist.Arten_Baudenkmale,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  beschreibung = models.CharField(
    'Beschreibung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
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
      'adresse': 'adresse',
      'art': 'art'
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
    as_overlay = True

  def __str__(self):
    return self.beschreibung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    super(Baudenkmale, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Baudenkmale, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Baudenkmale)

signals.post_delete.connect(functions.remove_permissions, sender=Baudenkmale)


# Behinderteneinrichtungen

class Behinderteneinrichtungen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  traeger = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=models.RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='traeger+')
  plaetze = fields.PositiveSmallIntegerMinField(
    'Plätze', min_value=1, blank=True, null=True)
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
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
    return self.bezeichnung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    super(Behinderteneinrichtungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Behinderteneinrichtungen, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Behinderteneinrichtungen)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Behinderteneinrichtungen)


# Bildungsträger

class Bildungstraeger(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  betreiber = models.CharField(
    'Betreiber',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  schlagwoerter = fields.ChoiceArrayField(
    models.CharField(
      'Schlagwörter',
      max_length=255,
      choices=()),
    verbose_name='Schlagwörter')
  barrierefrei = models.BooleanField(' barrierefrei?', blank=True, null=True)
  zeiten = models.CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True)
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse'
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
    return self.bezeichnung + \
           (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    super(Bildungstraeger, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Bildungstraeger, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Bildungstraeger)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Bildungstraeger)


# Carsharing-Stationen

class Carsharing_Stationen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  anbieter = models.ForeignKey(
    models_codelist.Anbieter_Carsharing,
    verbose_name='Anbieter',
    on_delete=models.RESTRICT,
    db_column='anbieter',
    to_field='uuid',
    related_name='anbieter+')
  anzahl_fahrzeuge = fields.PositiveSmallIntegerMinField(
    'Anzahl der Fahrzeuge', min_value=1, blank=True, null=True)
  bemerkungen = fields.NullTextField(
    'Bemerkungen',
    max_length=500,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'anbieter': 'anbieter'
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
    return self.bezeichnung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Anbieter: ' + str(self.anbieter) + ']'

  def save(self, *args, **kwargs):
    super(Carsharing_Stationen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Carsharing_Stationen, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Carsharing_Stationen)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Carsharing_Stationen)


# Containerstellplätze

class Containerstellplaetze(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField(
    'Außerbetriebstellung', blank=True, null=True)
  id = models.CharField(
    'ID',
    max_length=5,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.cont_id_regex,
        message=constants_vars.cont_id_message)])
  privat = models.BooleanField(' privat?')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  bewirtschafter_grundundboden = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Grund und Boden',
    on_delete=models.SET_NULL,
    db_column='bewirtschafter_grundundboden',
    to_field='uuid',
    related_name='bewirtschafter_grundundboden+',
    blank=True,
    null=True)
  bewirtschafter_glas = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Glas',
    on_delete=models.SET_NULL,
    db_column='bewirtschafter_glas',
    to_field='uuid',
    related_name='bewirtschafter_glas+',
    blank=True,
    null=True)
  anzahl_glas = fields.PositiveSmallIntegerMinField(
    'Anzahl Glas normal', min_value=1, blank=True, null=True)
  anzahl_glas_unterflur = fields.PositiveSmallIntegerMinField(
    'Anzahl Glas unterflur', min_value=1, blank=True, null=True)
  bewirtschafter_papier = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Papier',
    on_delete=models.SET_NULL,
    db_column='bewirtschafter_papier',
    to_field='uuid',
    related_name='bewirtschafter_papier+',
    blank=True,
    null=True)
  anzahl_papier = fields.PositiveSmallIntegerMinField(
    'Anzahl Papier normal', min_value=1, blank=True, null=True)
  anzahl_papier_unterflur = fields.PositiveSmallIntegerMinField(
    'Anzahl Papier unterflur', min_value=1, blank=True, null=True)
  bewirtschafter_altkleider = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Altkleider',
    on_delete=models.SET_NULL,
    db_column='bewirtschafter_altkleider',
    to_field='uuid',
    related_name='bewirtschafter_altkleider+',
    blank=True,
    null=True)
  anzahl_altkleider = fields.PositiveSmallIntegerMinField(
    'Anzahl Altkleider', min_value=1, blank=True, null=True)
  inbetriebnahmejahr = fields.PositiveSmallIntegerRangeField(
    'Inbetriebnahmejahr', max_value=functions.current_year(), blank=True, null=True)
  inventarnummer = models.CharField(
    'Inventarnummer Stellplatz',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.inventarnummer_regex,
        message=constants_vars.inventarnummer_message)])
  inventarnummer_grundundboden = models.CharField(
    'Inventarnummer Grund und Boden',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.inventarnummer_regex,
        message=constants_vars.inventarnummer_message)])
  inventarnummer_zaun = models.CharField(
    'Inventarnummer Zaun',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.inventarnummer_regex,
        message=constants_vars.inventarnummer_message)])
  anschaffungswert = models.DecimalField(
    'Anschaffungswert (in €)',
    max_digits=7,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.'),
      MaxValueValidator(
        Decimal('99999.99'),
        'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 99.999,99 € betragen.')],
    blank=True,
    null=True)
  oeffentliche_widmung = models.BooleanField(
    ' öffentliche Widmung?', blank=True, null=True)
  bga = models.BooleanField(
    'Zuordnung BgA Stellplatz?',
    blank=True,
    null=True)
  bga_grundundboden = models.BooleanField(
    'Zuordnung BgA Grund und Boden?', blank=True, null=True)
  bga_zaun = models.BooleanField(
    'Zuordnung BgA Zaun?', blank=True, null=True)
  art_eigentumserwerb = models.CharField(
    'Art des Eigentumserwerbs Stellplatz',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  art_eigentumserwerb_zaun = models.CharField(
    'Art des Eigentumserwerbs Zaun',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  vertraege = models.CharField(
    'Verträge',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  winterdienst_a = models.BooleanField(
    'Winterdienst A?', blank=True, null=True)
  winterdienst_b = models.BooleanField(
    'Winterdienst B?', blank=True, null=True)
  winterdienst_c = models.BooleanField(
    'Winterdienst C?', blank=True, null=True)
  flaeche = models.DecimalField(
    'Fläche (in m²)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Fläche</em></strong> muss mindestens 0,01 m² betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Fläche</em></strong> darf höchstens 999,99 m² betragen.')],
    blank=True,
    null=True)
  bemerkungen = models.CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  foto = models.ImageField(
    'Foto',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE +
      'containerstellplaetze'),
    max_length=255,
    blank=True,
    null=True)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
    as_overlay = True

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Containerstellplaetze, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Containerstellplaetze, self).delete(*args, **kwargs)


signals.pre_save.connect(
  functions.get_pre_save_instance,
  sender=Containerstellplaetze)

signals.post_save.connect(
  functions.photo_post_processing,
  sender=Containerstellplaetze)

signals.post_save.connect(
  functions.delete_photo_after_emptied,
  sender=Containerstellplaetze)

signals.post_save.connect(
  functions.assign_permissions,
  sender=Containerstellplaetze)

signals.post_delete.connect(
  functions.delete_photo,
  sender=Containerstellplaetze)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Containerstellplaetze)


# Denkmalbereiche

class Denkmalbereiche(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  beschreibung = models.CharField(
    'Beschreibung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
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
    as_overlay = True

  def __str__(self):
    return self.bezeichnung + \
           ' [Beschreibung: ' + str(self.beschreibung) + ']'

  def save(self, *args, **kwargs):
    super(Denkmalbereiche, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Denkmalbereiche, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Denkmalbereiche)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Denkmalbereiche)


# Denksteine

class Denksteine(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  nummer = models.CharField(
    'Nummer',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.denk_nummer_regex,
        message=constants_vars.denk_nummer_message)])
  titel = models.ForeignKey(
    models_codelist.Personentitel,
    verbose_name='Titel',
    on_delete=models.SET_NULL,
    db_column='titel',
    to_field='uuid',
    related_name='titel+',
    blank=True,
    null=True)
  vorname = models.CharField(
    'Vorname',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message),
      RegexValidator(
        regex=constants_vars.bindestrich_leerzeichen_regex,
        message=constants_vars.bindestrich_leerzeichen_message),
      RegexValidator(
        regex=constants_vars.leerzeichen_bindestrich_regex,
        message=constants_vars.leerzeichen_bindestrich_message)])
  nachname = models.CharField(
    'Nachname',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message),
      RegexValidator(
        regex=constants_vars.bindestrich_leerzeichen_regex,
        message=constants_vars.bindestrich_leerzeichen_message),
      RegexValidator(
        regex=constants_vars.leerzeichen_bindestrich_regex,
        message=constants_vars.leerzeichen_bindestrich_message)])
  geburtsjahr = fields.PositiveSmallIntegerRangeField(
    'Geburtsjahr', min_value=1850, max_value=1945)
  sterbejahr = fields.PositiveSmallIntegerRangeField(
    'Sterbejahr', min_value=1933, max_value=1945, blank=True, null=True)
  text_auf_dem_stein = models.CharField(
    'Text auf dem Stein',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  ehemalige_adresse = models.CharField(
    ' ehemalige Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  material = models.ForeignKey(
    models_codelist.Materialien_Denksteine,
    verbose_name='Material',
    on_delete=models.RESTRICT,
    db_column='material',
    to_field='uuid',
    related_name='materialien+')
  erstes_verlegejahr = fields.PositiveSmallIntegerRangeField(
    ' erstes Verlegejahr', min_value=2002, max_value=functions.current_year())
  website = models.CharField(
    'Website',
    max_length=255,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'titel': 'bezeichnung'
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
    return (str(
      self.titel) + ' ' if self.titel else '') + self.vorname + ' ' + self.nachname + ' (* ' + str(
      self.geburtsjahr) + \
           (', † ' + str(self.sterbejahr) if self.sterbejahr else '') + ')' + (
             ' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    super(Denksteine, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Denksteine, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Denksteine)

signals.post_delete.connect(functions.remove_permissions, sender=Denksteine)


# Fair Trade

class FairTrade(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  art = models.ForeignKey(
    models_codelist.Arten_FairTrade,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  betreiber = models.CharField(
    'Betreiber',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  barrierefrei = models.BooleanField(' barrierefrei?', blank=True, null=True)
  zeiten = models.CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True)
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'art': 'art'
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
    return self.bezeichnung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    super(FairTrade, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(FairTrade, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=FairTrade)

signals.post_delete.connect(functions.remove_permissions, sender=FairTrade)


# Feldsportanlagen

class Feldsportanlagen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  art = models.ForeignKey(
    models_codelist.Arten_Feldsportanlagen,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  traeger = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=models.RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='traeger+')
  foto = models.ImageField(
    'Foto',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC +
      'feldsportanlagen'),
    max_length=255,
    blank=True,
    null=True)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"feldsportanlagen_hro'
    verbose_name = 'Feldsportanlage'
    verbose_name_plural = 'Feldsportanlagen'
    description = 'Feldsportanlagen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
      'foto': 'Foto'
    }
    list_fields_with_foreign_key = {
      'art': 'art',
      'traeger': 'bezeichnung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['art', 'traeger']
    geometry_type = 'Point'
    thumbs = True

  def __str__(self):
    return self.bezeichnung + ' [Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    super(Feldsportanlagen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Feldsportanlagen, self).delete(*args, **kwargs)


signals.pre_save.connect(
  functions.get_pre_save_instance,
  sender=Feldsportanlagen)

signals.post_save.connect(
  functions.photo_post_processing,
  sender=Feldsportanlagen)

signals.post_save.connect(
  functions.delete_photo_after_emptied,
  sender=Feldsportanlagen)

signals.post_save.connect(
  functions.assign_permissions,
  sender=Feldsportanlagen)

signals.post_delete.connect(functions.delete_photo, sender=Feldsportanlagen)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Feldsportanlagen)


# Feuerwachen

class Feuerwachen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  art = models.ForeignKey(
    models_codelist.Arten_Feuerwachen,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'art': 'art'
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
    return self.bezeichnung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    super(Feuerwachen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Feuerwachen, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Feuerwachen)

signals.post_delete.connect(functions.remove_permissions, sender=Feuerwachen)


# Fließgewässer

class Fliessgewaesser(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  nummer = models.CharField(
    'Nummer',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  art = models.ForeignKey(
    models_codelist.Arten_Fliessgewaesser,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  ordnung = models.ForeignKey(
    models_codelist.Ordnungen_Fliessgewaesser,
    verbose_name='Ordnung',
    on_delete=models.SET_NULL,
    db_column='ordnung',
    to_field='uuid',
    related_name='ordnungen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  nennweite = fields.PositiveSmallIntegerMinField(
    'Nennweite (in mm)', min_value=100, blank=True, null=True)
  laenge = models.PositiveIntegerField('Länge (in m)', default=0)
  laenge_in_hro = models.PositiveIntegerField(
    'Länge innerhalb Rostocks (in m)', blank=True, null=True)
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
      'art': 'art',
      'ordnung': 'ordnung'
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
    as_overlay = True
    heavy_load_limit = 500

  def __str__(self):
    return self.nummer + \
           ' [Art: ' + str(self.art) + (
             ', Ordnung: ' + str(self.ordnung) if self.ordnung else '') + ']'

  def save(self, *args, **kwargs):
    super(Fliessgewaesser, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Fliessgewaesser, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Fliessgewaesser)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Fliessgewaesser)


# Geh- und Radwegereinigung

class Geh_Radwegereinigung(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
  )
  aktiv = models.BooleanField(' aktiv?', default=True)
  id = models.CharField('ID', max_length=14, default='0000000000-000')
  strasse = models.ForeignKey(
    models_codelist.Strassen,
    verbose_name='Straße',
    on_delete=models.SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='strassen+',
    blank=True,
    null=True
  )
  inoffizielle_strasse = models.ForeignKey(
    models_codelist.Inoffizielle_Strassen,
    verbose_name=' inoffizielle Straße',
    on_delete=models.SET_NULL,
    db_column='inoffizielle_strasse',
    to_field='uuid',
    related_name='inoffizielle_strassen+',
    blank=True,
    null=True
  )
  nummer = models.CharField(
    'Nummer',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  beschreibung = models.CharField(
    'Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  wegeart = models.ForeignKey(
    models_codelist.Arten_Wege,
    verbose_name='Wegeart',
    on_delete=models.CASCADE,
    db_column='wegeart',
    to_field='uuid',
    related_name='wegearten+'
  )
  wegetyp = models.ForeignKey(
    models_codelist.Wegetypen_Strassenreinigungssatzung_HRO,
    verbose_name='Wegetyp',
    on_delete=models.CASCADE,
    db_column='wegetyp',
    to_field='uuid',
    related_name='wegetypen',
    blank=True,
    null=True
  )
  reinigungsklasse = models.ForeignKey(
    models_codelist.Wegereinigungsklassen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsklasse',
    on_delete=models.SET_NULL,
    db_column='reinigungsklasse',
    to_field='uuid',
    related_name='wegereinigungsklassen',
    blank=True,
    null=True
  )
  reinigungsrhythmus = models.ForeignKey(
    models_codelist.Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsrhythmus',
    on_delete=models.SET_NULL,
    db_column='reinigungsrhythmus',
    to_field='uuid',
    related_name='wegereinigungsrhythmen',
    blank=True,
    null=True
  )
  laenge = models.DecimalField(
    'Länge (in m)',
    max_digits=6,
    decimal_places=2,
    default=0)
  breite = models.ForeignKey(
    models_codelist.Wegebreiten_Strassenreinigungssatzung_HRO,
    verbose_name='Breite (in m)',
    on_delete=models.CASCADE,
    db_column='breite',
    to_field='uuid',
    related_name='wegebreiten',
    blank=True,
    null=True
  )
  reinigungsflaeche = models.DecimalField(
    'Reinigungsfläche (in m²)',
    max_digits=7,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Reinigungsfläche</em></strong> muss mindestens 0,01 m² betragen.'),
      MaxValueValidator(
        Decimal('99999.99'),
        'Die <strong><em>Reinigungsfläche</em></strong> darf höchstens 99.999,99 m² betragen.')],
    blank=True,
    null=True)
  winterdienst = models.BooleanField(
    'Winterdienst?',
    blank=True,
    null=True)
  raeumbreite = models.ForeignKey(
    models_codelist.Raeumbreiten_Strassenreinigungssatzung_HRO,
    verbose_name='Räumbreite im Winterdienst (in m)',
    on_delete=models.CASCADE,
    db_column='raeumbreite',
    to_field='uuid',
    related_name='raeumbreiten',
    blank=True,
    null=True
  )
  winterdienstflaeche = models.DecimalField(
    'Winterdienstfläche (in m²)',
    max_digits=7,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Winterdienstfläche</em></strong> muss mindestens 0,01 m² betragen.'),
      MaxValueValidator(
        Decimal('99999.99'),
        'Die <strong><em>Winterdienstfläche</em></strong> darf höchstens 99.999,99 m² betragen.')],
    blank=True,
    null=True)
  geometrie = models.MultiLineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten_strassenbezug\".\"geh_und_radwegereinigung_hro'
    verbose_name = 'Geh- und Radwegereinigung'
    verbose_name_plural = 'Geh- und Radwegereinigung'
    description = 'Geh- und Radwegereinigung der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'inoffizielle_strasse': 'inoffizielle Straße',
      'nummer': 'Nummer',
      'beschreibung': 'Beschreibung',
      'wegeart': 'Wegeart',
      'wegetyp': 'Wegetyp',
      'reinigungsklasse': 'Reinigungsklasse',
      'laenge': 'Länge (in m)',
      'breite': 'Breite (in m)',
      'winterdienst': 'Winterdienst?'
    }
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'inoffizielle_strasse': 'strasse',
      'wegeart': 'art',
      'wegetyp': 'wegetyp',
      'reinigungsklasse': 'code',
      'reinigungsrhythmus': 'reinigungsrhythmus',
      'breite': 'wegebreite'
    }
    list_fields_with_number = ['id', 'laenge']
    readonly_fields = ['id', 'laenge']
    map_feature_tooltip_field = 'id'
    map_filter_fields = {
      'id': 'ID',
      'strasse': 'Straße',
      'inoffizielle_strasse': 'inoffizielle Straße',
      'nummer': 'Nummer',
      'beschreibung': 'Beschreibung',
      'wegeart': 'Wegeart',
      'wegetyp': 'Wegetyp',
      'reinigungsklasse': 'Reinigungsklasse',
      'reinigungsrhythmus': 'Reinigungsrhythmus',
      'breite': 'Breite (in m)',
      'winterdienst': 'Winterdienst?',
    }
    map_filter_fields_as_list = [
      'strasse',
      'inoffizielle_strasse',
      'wegeart',
      'wegetyp',
      'reinigungsklasse',
      'reinigungsrhythmus',
      'breite',
      'winterdienst'
    ]
    additional_wms_layers = [
      {
        'title': 'Geh- und Radwegereinigung',
        'url': 'https://geo.sv.rostock.de/geodienste/geh_und_radwegereinigung/wms',
        'layers': 'hro.geh_und_radwegereinigung.geh_und_radwegereinigung'}]
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'MultiLineString'
    as_overlay = True

  def __str__(self):
    return str(self.id) + (', ' + str(self.nummer) if self.nummer else '') + (
      ', ' + str(self.beschreibung) if self.beschreibung else '') + (
             ', Wegeart ' + str(self.wegeart) if self.wegeart else '') + (
             ', Wegetyp ' + str(self.wegetyp) if self.wegetyp else '') + (
             ', Reinigungsklasse ' + str(self.reinigungsklasse) if self.reinigungsklasse else '') \
           + (
             ', mit Winterdienst' if self.winterdienst else '') + (
             ' [Straße: ' + str(self.strasse) + ']' if self.strasse else '') + (
             ' [inoffizielle Straße: ' + str(
               self.inoffizielle_strasse) + ']' if self.inoffizielle_strasse else '')

  def save(self, *args, **kwargs):
    super(Geh_Radwegereinigung, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Geh_Radwegereinigung, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Geh_Radwegereinigung)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Geh_Radwegereinigung)


# Gerätespielanlagen

class Geraetespielanlagen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  traeger = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=models.RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='traeger+')
  beschreibung = models.CharField(
    'Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  foto = models.ImageField(
    'Foto',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC +
      'geraetespielanlagen'),
    max_length=255,
    blank=True,
    null=True)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"geraetespielanlagen_hro'
    verbose_name = 'Gerätespielanlage'
    verbose_name_plural = 'Gerätespielanlagen'
    description = 'Gerätespielanlagen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
      'beschreibung': 'Beschreibung',
      'foto': 'Foto'
    }
    list_fields_with_foreign_key = {
      'traeger': 'bezeichnung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
      'beschreibung': 'Beschreibung'
    }
    map_filter_fields_as_list = ['traeger']
    geometry_type = 'Point'
    thumbs = True

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Geraetespielanlagen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Geraetespielanlagen, self).delete(*args, **kwargs)


signals.pre_save.connect(
  functions.get_pre_save_instance,
  sender=Geraetespielanlagen)

signals.post_save.connect(
  functions.photo_post_processing,
  sender=Geraetespielanlagen)

signals.post_save.connect(
  functions.delete_photo_after_emptied,
  sender=Geraetespielanlagen)

signals.post_save.connect(
  functions.assign_permissions,
  sender=Geraetespielanlagen)

signals.post_delete.connect(functions.delete_photo, sender=Geraetespielanlagen)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Geraetespielanlagen)


# Gutachterfotos

class Gutachterfotos(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bearbeiter = models.CharField(
    'Bearbeiter',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  bemerkungen = models.CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  aufnahmedatum = models.DateField('Aufnahmedatum', default=date.today)
  foto = models.ImageField(
    'Foto',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE +
      'gutachterfotos'),
    max_length=255)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse'
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
    heavy_load_limit = 800

  def __str__(self):
    return 'Gutachterfoto mit Aufnahmedatum ' + datetime.strptime(str(self.aufnahmedatum),
                                                                  '%Y-%m-%d').strftime(
      '%d.%m.%Y') + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    super(Gutachterfotos, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Gutachterfotos, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.photo_post_processing,
  sender=Gutachterfotos)

signals.post_save.connect(functions.assign_permissions, sender=Gutachterfotos)

signals.post_delete.connect(functions.delete_photo, sender=Gutachterfotos)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Gutachterfotos)


# Hausnummern

class Hausnummern(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  strasse = models.ForeignKey(
    models_codelist.Strassen,
    verbose_name='Straße',
    on_delete=models.SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='strassen+',
    blank=True,
    null=True
  )
  deaktiviert = models.DateField(
    'Datum der Löschung', blank=True, null=True)
  loeschung_details = models.CharField(
    'Details zur Löschung', max_length=255, blank=True, null=True, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex, message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex, message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message)])
  vorherige_adresse = models.CharField(
    ' vorherige Adresse', max_length=255, blank=True, null=True, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex, message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex, message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message)])
  vorherige_antragsnummer = models.CharField(
    ' vorherige Antragsnummer',
    max_length=6,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.hnr_antragsnummer_regex,
        message=constants_vars.hnr_antragsnummer_message)])
  hausnummer = fields.PositiveSmallIntegerRangeField(
    'Hausnummer', min_value=1, max_value=999)
  hausnummer_zusatz = models.CharField(
    'Hausnummernzusatz',
    max_length=1,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.hausnummer_zusatz_regex,
        message=constants_vars.hausnummer_zusatz_message)])
  postleitzahl = models.CharField(
    'Postleitzahl',
    max_length=5,
    validators=[
      RegexValidator(
        regex=constants_vars.postleitzahl_regex,
        message=constants_vars.postleitzahl_message)])
  vergabe_datum = models.DateField(
    'Datum der Vergabe', default=date.today)
  antragsnummer = models.CharField(
    'Antragsnummer',
    max_length=6,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.hnr_antragsnummer_regex,
        message=constants_vars.hnr_antragsnummer_message)])
  gebaeude_bauweise = models.ForeignKey(
    models_codelist.Gebaeudebauweisen,
    verbose_name='Bauweise des Gebäudes',
    on_delete=models.SET_NULL,
    db_column='gebaeude_bauweise',
    to_field='uuid',
    related_name='gebaeude_bauweisen+',
    blank=True,
    null=True)
  gebaeude_funktion = models.ForeignKey(
    models_codelist.Gebaeudefunktionen,
    verbose_name='Funktion des Gebäudes',
    on_delete=models.SET_NULL,
    db_column='gebaeude_funktion',
    to_field='uuid',
    related_name='gebaeude_funktionen+',
    blank=True,
    null=True)
  hinweise_gebaeude = models.CharField(
    ' weitere Hinweise zum Gebäude', max_length=255, blank=True, null=True, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex, message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex, message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message)])
  bearbeiter = models.CharField(
    'Bearbeiter', max_length=255, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex, message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex, message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message)])
  bemerkungen = models.CharField(
    'Bemerkungen', max_length=255, blank=True, null=True, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex, message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex, message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_strassenbezug\".\"hausnummern_hro'
    verbose_name = 'Hausnummer'
    verbose_name_plural = 'Hausnummern'
    description = 'Hausnummern der Hanse- und Universitätsstadt Rostock'
    catalog_link_fields = {
      'gebaeude_bauweise': 'https://geo.sv.rostock.de/alkis-ok/31001/baw/',
      'gebaeude_funktion': 'https://geo.sv.rostock.de/alkis-ok/31001/gfk/'}
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Datum der Löschung',
      'strasse': 'Straße',
      'hausnummer': 'Hausnummer',
      'hausnummer_zusatz': 'Hausnummernzusatz',
      'postleitzahl': 'Postleitzahl',
      'vergabe_datum': 'Datum der Vergabe',
      'antragsnummer': 'Antragsnummer',
      'gebaeude_bauweise': 'Bauweise des Gebäudes',
      'gebaeude_funktion': 'Funktion des Gebäudes'
    }
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'gebaeude_bauweise': 'bezeichnung',
      'gebaeude_funktion': 'bezeichnung'
    }
    list_fields_with_date = [
      'deaktiviert',
      'vergabe_datum'
    ]
    list_fields_with_number = ['hausnummer']
    map_feature_tooltip_fields = [
      'strasse',
      'hausnummer',
      'hausnummer_zusatz'
    ]
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Datum der Löschung',
      'strasse': 'Straße',
      'hausnummer': 'Hausnummer',
      'hausnummer_zusatz': 'Hausnummernzusatz',
      'postleitzahl': 'Postleitzahl',
      'vergabe_datum': 'Datum der Vergabe',
      'antragsnummer': 'Antragsnummer',
      'gebaeude_bauweise': 'Bauweise des Gebäudes',
      'gebaeude_funktion': 'Funktion des Gebäudes'
    }
    map_filter_fields_as_list = [
      'strasse',
      'gebaeude_bauweise',
      'gebaeude_funktion'
    ]
    address_type = 'Straße'
    address_mandatory = True
    geometry_type = 'Point'
    postcode_assigner = 'postleitzahl'
    heavy_load_limit = 800

  def __str__(self):
    return str(self.strasse) + ' ' + str(self.hausnummer) + \
           (self.hausnummer_zusatz if self.hausnummer_zusatz else '') + \
           ' [Postleitzahl: ' + self.postleitzahl + ']'

  def save(self, *args, **kwargs):
    super(Hausnummern, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Hausnummern, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Hausnummern)

signals.post_delete.connect(functions.remove_permissions, sender=Hausnummern)


# Hospize

class Hospize(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  traeger = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=models.RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='traeger+')
  plaetze = fields.PositiveSmallIntegerMinField(
    'Plätze', min_value=1, blank=True, null=True)
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
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
    return self.bezeichnung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    super(Hospize, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Hospize, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Hospize)

signals.post_delete.connect(functions.remove_permissions, sender=Hospize)


# Hundetoiletten

class Hundetoiletten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField(
    'Außerbetriebstellung', blank=True, null=True)
  id = models.CharField('ID', max_length=8, default='00000000')
  art = models.ForeignKey(
    models_codelist.Arten_Hundetoiletten,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  aufstellungsjahr = fields.PositiveSmallIntegerRangeField(
    'Aufstellungsjahr', max_value=functions.current_year(), blank=True, null=True)
  bewirtschafter = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=models.RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='bewirtschafter+')
  pflegeobjekt = models.CharField(
    'Pflegeobjekt',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  inventarnummer = models.CharField(
    'Inventarnummer',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.inventarnummer_regex,
        message=constants_vars.inventarnummer_message)])
  anschaffungswert = models.DecimalField(
    'Anschaffungswert (in €)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.'),
      MaxValueValidator(
        Decimal('9999.99'),
        'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 9.999,99 € betragen.')],
    blank=True,
    null=True)
  bemerkungen = models.CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'art': 'art',
      'bewirtschafter': 'bezeichnung'
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
    as_overlay = True

  def __str__(self):
    return self.id + ' [Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    super(Hundetoiletten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Hundetoiletten, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Hundetoiletten)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Hundetoiletten)


# Hydranten

class Hydranten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.hyd_bezeichnung_regex,
        message=constants_vars.hyd_bezeichnung_message)])
  eigentuemer = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=models.RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='eigentuemer+')
  bewirtschafter = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=models.RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='bewirtschafter+')
  feuerloeschgeeignet = models.BooleanField(' feuerlöschgeeignet?')
  betriebszeit = models.ForeignKey(
    models_codelist.Betriebszeiten,
    verbose_name='Betriebszeit',
    on_delete=models.RESTRICT,
    db_column='betriebszeit',
    to_field='uuid',
    related_name='betriebszeiten+')
  entnahme = models.CharField(
    'Entnahme',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  hauptwasserzaehler = models.CharField(
    'Hauptwasserzähler',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"hydranten_hro'
    verbose_name = 'Hydrant'
    verbose_name_plural = 'Hydranten'
    description = 'Hydranten im Eigentum der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'eigentuemer': 'Eigentümer',
      'bewirtschafter': 'Bewirtschafter',
      'feuerloeschgeeignet': 'feuerlöschgeeignet?',
      'betriebszeit': 'Betriebszeit',
      'entnahme': 'Entnahme',
      'hauptwasserzaehler': 'Hauptwasserzähler'
    }
    list_fields_with_foreign_key = {
      'eigentuemer': 'bezeichnung',
      'bewirtschafter': 'bezeichnung',
      'betriebszeit': 'betriebszeit'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'eigentuemer': 'Eigentümer',
      'bewirtschafter': 'Bewirtschafter',
      'feuerloeschgeeignet': 'feuerlöschgeeignet?',
      'betriebszeit': 'Betriebszeit',
      'entnahme': 'Entnahme',
      'hauptwasserzaehler': 'Hauptwasserzähler'
    }
    map_filter_fields_as_list = [
      'eigentuemer', 'bewirtschafter', 'betriebszeit']
    geometry_type = 'Point'
    as_overlay = True

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Hydranten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Hydranten, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Hydranten)

signals.post_delete.connect(functions.remove_permissions, sender=Hydranten)


# Kadaverfunde

class Kadaverfunde(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  zeitpunkt = models.DateTimeField('Zeitpunkt')
  tierseuche = models.ForeignKey(
    models_codelist.Tierseuchen,
    verbose_name='Tierseuche',
    on_delete=models.RESTRICT,
    db_column='tierseuche',
    to_field='uuid',
    related_name='tierseuchen+')
  geschlecht = models.ForeignKey(
    models_codelist.Geschlechter_Kadaverfunde,
    verbose_name='Geschlecht',
    on_delete=models.RESTRICT,
    db_column='geschlecht',
    to_field='uuid',
    related_name='geschlechter+')
  altersklasse = models.ForeignKey(
    models_codelist.Altersklassen_Kadaverfunde,
    verbose_name='Altersklasse',
    on_delete=models.RESTRICT,
    db_column='altersklasse',
    to_field='uuid',
    related_name='altersklassen+')
  gewicht = fields.PositiveSmallIntegerRangeField(
    ' geschätztes Gewicht (in kg)', min_value=1, blank=True, null=True)
  zustand = models.ForeignKey(
    models_codelist.Zustaende_Kadaverfunde,
    verbose_name='Zustand',
    on_delete=models.RESTRICT,
    db_column='zustand',
    to_field='uuid',
    related_name='zustaende+')
  art_auffinden = models.ForeignKey(
    models_codelist.Arten_Fallwildsuchen_Kontrollen,
    verbose_name='Art des Auffindens',
    on_delete=models.RESTRICT,
    db_column='art_auffinden',
    to_field='uuid',
    related_name='arten_auffinden+')
  witterung = models.CharField(
    'Witterung vor Ort',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  bemerkungen = fields.NullTextField(
    'Bemerkungen',
    max_length=500,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"kadaverfunde_hro'
    verbose_name = 'Kadaverfund'
    verbose_name_plural = 'Kadaverfunde'
    description = 'Kadaverfunde in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'tierseuche': 'Tierseuche',
      'geschlecht': 'Geschlecht',
      'altersklasse': 'Altersklasse',
      'gewicht': 'geschätztes Gewicht (in kg)',
      'zustand': 'Zustand',
      'art_auffinden': 'Art des Auffindens',
      'zeitpunkt': 'Zeitpunkt'
    }
    list_fields_with_datetime = ['zeitpunkt']
    list_fields_with_number = ['gewicht']
    list_fields_with_foreign_key = {
      'tierseuche': 'bezeichnung',
      'geschlecht': 'bezeichnung',
      'altersklasse': 'bezeichnung',
      'zustand': 'zustand',
      'art_auffinden': 'art'
    }
    map_feature_tooltip_field = 'tierseuche'
    map_filter_fields = {
      'tierseuche': 'Tierseuche',
      'geschlecht': 'Geschlecht',
      'altersklasse': 'Altersklasse',
      'zustand': 'Zustand',
      'art_auffinden': 'Art des Auffindens',
      'zeitpunkt': 'Zeitpunkt'
    }
    map_filter_fields_as_list = [
      'tierseuche',
      'geschlecht',
      'altersklasse',
      'zustand',
      'art_auffinden'
    ]
    geometry_type = 'Point'
    as_overlay = True

  def __str__(self):
    local_tz = ZoneInfo(settings.TIME_ZONE)
    zeitpunkt_str = re.sub(r'([+-][0-9]{2}):', '\\1', str(self.zeitpunkt))
    zeitpunkt = datetime.strptime(
      zeitpunkt_str,
      '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=timezone.utc).astimezone(local_tz)
    zeitpunkt_str = zeitpunkt.strftime('%d.%m.%Y, %H:%M:%S Uhr')
    return str(self.tierseuche) + ' mit Zeitpunkt ' + zeitpunkt_str + ', '

  def save(self, *args, **kwargs):
    super(Kadaverfunde, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Kadaverfunde, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Kadaverfunde)

signals.post_delete.connect(functions.remove_permissions, sender=Kadaverfunde)


# Kindertagespflegeeinrichtungen

class Kindertagespflegeeinrichtungen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  vorname = models.CharField(
    'Vorname',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message),
      RegexValidator(
        regex=constants_vars.bindestrich_leerzeichen_regex,
        message=constants_vars.bindestrich_leerzeichen_message),
      RegexValidator(
        regex=constants_vars.leerzeichen_bindestrich_regex,
        message=constants_vars.leerzeichen_bindestrich_message)])
  nachname = models.CharField(
    'Nachname',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message),
      RegexValidator(
        regex=constants_vars.bindestrich_leerzeichen_regex,
        message=constants_vars.bindestrich_leerzeichen_message),
      RegexValidator(
        regex=constants_vars.leerzeichen_bindestrich_regex,
        message=constants_vars.leerzeichen_bindestrich_message)])
  plaetze = fields.PositiveSmallIntegerMinField(
    'Plätze', min_value=1, blank=True, null=True)
  zeiten = models.CharField(
    'Betreuungszeiten',
    max_length=255,
    blank=True,
    null=True)
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"kindertagespflegeeinrichtungen_hro'
    verbose_name = 'Kindertagespflegeeinrichtung'
    verbose_name_plural = 'Kindertagespflegeeinrichtungen'
    description = 'Kindertagespflegeeinrichtungen (Tagesmütter und Tagesväter) in der Hanse- ' \
                  'und Universitätsstadt Rostock'
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
      'adresse': 'adresse'
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
    return self.vorname + ' ' + self.nachname + \
           (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    super(Kindertagespflegeeinrichtungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Kindertagespflegeeinrichtungen, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Kindertagespflegeeinrichtungen)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Kindertagespflegeeinrichtungen)


# Kinder- und Jugendbetreuung

class Kinder_Jugendbetreuung(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  traeger = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=models.RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='traeger+')
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
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
    return self.bezeichnung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    super(Kinder_Jugendbetreuung, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Kinder_Jugendbetreuung, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Kinder_Jugendbetreuung)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Kinder_Jugendbetreuung)


# Kunst im öffentlichen Raum

class Kunst_im_oeffentlichen_Raum(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  ausfuehrung = models.CharField(
    'Ausführung',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  schoepfer = models.CharField(
    'Schöpfer',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  entstehungsjahr = fields.PositiveSmallIntegerRangeField(
    'Entstehungsjahr', max_value=functions.current_year(), blank=True, null=True)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
    super(Kunst_im_oeffentlichen_Raum, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Kunst_im_oeffentlichen_Raum, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Kunst_im_oeffentlichen_Raum)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Kunst_im_oeffentlichen_Raum)


# Ladestationen für Elektrofahrzeuge

class Ladestationen_Elektrofahrzeuge(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  geplant = models.BooleanField(' geplant?')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  betreiber = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=models.SET_NULL,
    db_column='betreiber',
    to_field='uuid',
    related_name='betreiber+',
    blank=True,
    null=True)
  verbund = models.ForeignKey(
    models_codelist.Verbuende_Ladestationen_Elektrofahrzeuge,
    verbose_name='Verbund',
    on_delete=models.SET_NULL,
    db_column='verbund',
    to_field='uuid',
    related_name='verbuende+',
    blank=True,
    null=True)
  betriebsart = models.ForeignKey(
    models_codelist.Betriebsarten,
    verbose_name='Betriebsart',
    on_delete=models.RESTRICT,
    db_column='betriebsart',
    to_field='uuid',
    related_name='betriebsarten+')
  anzahl_ladepunkte = fields.PositiveSmallIntegerMinField(
    'Anzahl an Ladepunkten', min_value=1, blank=True, null=True)
  arten_ladepunkte = models.CharField(
    'Arten der Ladepunkte',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  ladekarten = fields.ChoiceArrayField(
    models.CharField(
      'Ladekarten',
      max_length=255,
      choices=()),
    verbose_name='Ladekarten',
    blank=True,
    null=True)
  kosten = models.CharField(
    'Kosten',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  zeiten = models.CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True)
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'betreiber': 'bezeichnung',
      'verbund': 'verbund',
      'betriebsart': 'betriebsart'
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
    return self.bezeichnung + \
           (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    super(Ladestationen_Elektrofahrzeuge, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Ladestationen_Elektrofahrzeuge, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Ladestationen_Elektrofahrzeuge)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Ladestationen_Elektrofahrzeuge)


# Meldedienst (flächenhaft)

class Meldedienst_flaechenhaft(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  art = models.ForeignKey(
    models_codelist.Arten_Meldedienst_flaechenhaft,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  bearbeiter = models.CharField(
    'Bearbeiter',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  bemerkungen = models.CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
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
      'art': 'art'
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
    return str(self.art) + ' [Datum: ' + datetime.strptime(
      str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + ']'

  def save(self, *args, **kwargs):
    super(Meldedienst_flaechenhaft, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Meldedienst_flaechenhaft, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Meldedienst_flaechenhaft)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Meldedienst_flaechenhaft)


# Meldedienst (punkthaft)

class Meldedienst_punkthaft(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField(
    'Zurückstellung', blank=True, null=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  art = models.ForeignKey(
    models_codelist.Arten_Meldedienst_punkthaft,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  bearbeiter = models.CharField(
    'Bearbeiter',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  bemerkungen = models.CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  datum = models.DateField('Datum', default=date.today)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"meldedienst_punkthaft_hro'
    verbose_name = 'Meldedienst (punkthaft)'
    verbose_name_plural = 'Meldedienst (punkthaft)'
    description = 'Meldedienst (punkthaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Zurückstellung',
      'adresse': 'Adresse',
      'art': 'Art',
      'bearbeiter': 'Bearbeiter',
      'bemerkungen': 'Bemerkungen',
      'datum': 'Datum'
    }
    list_fields_with_date = ['deaktiviert', 'datum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'art': 'art'
    }
    readonly_fields = ['deaktiviert']
    map_feature_tooltip_field = 'art'
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bearbeiter': 'Bearbeiter',
      'datum': 'Datum'
    }
    map_filter_fields_as_list = ['art']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    as_overlay = True
    heavy_load_limit = 600

  def __str__(self):
    return str(self.art) + ' [Datum: ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime(
      '%d.%m.%Y') + (', Adresse: ' + str(self.adresse) if self.adresse else '') + ']'

  def save(self, *args, **kwargs):
    super(Meldedienst_punkthaft, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Meldedienst_punkthaft, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Meldedienst_punkthaft)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Meldedienst_punkthaft)


# Mobilpunkte

class Mobilpunkte(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  angebote = fields.ChoiceArrayField(
    models.CharField(
      'Angebote',
      max_length=255,
      choices=()),
    verbose_name='Angebote')
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
    super(Mobilpunkte, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Mobilpunkte, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Mobilpunkte)

signals.post_delete.connect(functions.remove_permissions, sender=Mobilpunkte)


# Parkmöglichkeiten

class Parkmoeglichkeiten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  art = models.ForeignKey(
    models_codelist.Arten_Parkmoeglichkeiten,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  standort = models.CharField(
    'Standort',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  betreiber = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=models.SET_NULL,
    db_column='betreiber',
    to_field='uuid',
    related_name='betreiber+',
    blank=True,
    null=True)
  stellplaetze_pkw = fields.PositiveSmallIntegerMinField(
    'Pkw-Stellplätze', min_value=1, blank=True, null=True)
  stellplaetze_wohnmobil = fields.PositiveSmallIntegerMinField(
    'Wohnmobilstellplätze', min_value=1, blank=True, null=True)
  stellplaetze_bus = fields.PositiveSmallIntegerMinField(
    'Busstellplätze', min_value=1, blank=True, null=True)
  gebuehren_halbe_stunde = models.DecimalField(
    'Gebühren pro ½ h (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro ½ h</em></strong> müssen mindestens 0,01 € betragen.'),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro ½ h</em></strong> dürfen höchstens 9,99 € betragen.')],
    blank=True,
    null=True)
  gebuehren_eine_stunde = models.DecimalField(
    'Gebühren pro 1 h (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro 1 h</em></strong> müssen mindestens 0,01 € betragen.'),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro 1 h</em></strong> dürfen höchstens 9,99 € betragen.')],
    blank=True,
    null=True)
  gebuehren_zwei_stunden = models.DecimalField(
    'Gebühren pro 2 h (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro 2 h</em></strong> müssen mindestens 0,01 € betragen.'),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro 2 h</em></strong> dürfen höchstens 9,99 € betragen.')],
    blank=True,
    null=True)
  gebuehren_ganztags = models.DecimalField(
    'Gebühren ganztags (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren ganztags</em></strong> müssen mindestens 0,01 € betragen.'),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren ganztags</em></strong> dürfen höchstens 9,99 € betragen.')],
    blank=True,
    null=True)
  bemerkungen = models.CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'art': 'art',
      'betreiber': 'bezeichnung'
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
    return str(self.art) + ' ' + self.standort + \
           (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    super(Parkmoeglichkeiten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Parkmoeglichkeiten, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Parkmoeglichkeiten)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Parkmoeglichkeiten)


# Pflegeeinrichtungen

class Pflegeeinrichtungen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  art = models.ForeignKey(
    models_codelist.Arten_Pflegeeinrichtungen,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  betreiber = models.CharField(
    'Betreiber',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  plaetze = fields.PositiveSmallIntegerMinField(
    'Plätze', min_value=1, blank=True, null=True)
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'art': 'art'
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
    return self.bezeichnung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    super(Pflegeeinrichtungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Pflegeeinrichtungen, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Pflegeeinrichtungen)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Pflegeeinrichtungen)


# Poller

class Poller(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  art = models.ForeignKey(
    models_codelist.Arten_Poller,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  nummer = models.CharField(
    'Nummer',
    max_length=3,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.poll_nummer_regex,
        message=constants_vars.poll_nummer_message)])
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  status = models.ForeignKey(
    models_codelist.Status_Poller,
    verbose_name='Status',
    on_delete=models.RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='status+')
  zeiten = models.CharField(
    'Lieferzeiten',
    max_length=255,
    blank=True,
    null=True)
  hersteller = models.ForeignKey(
    models_codelist.Hersteller_Poller,
    verbose_name='Hersteller',
    on_delete=models.SET_NULL,
    db_column='hersteller',
    to_field='uuid',
    related_name='hersteller+',
    blank=True,
    null=True)
  typ = models.ForeignKey(
    models_codelist.Typen_Poller,
    verbose_name='Typ',
    on_delete=models.SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='typen+',
    blank=True,
    null=True)
  anzahl = fields.PositiveSmallIntegerMinField('Anzahl', min_value=1)
  schliessungen = fields.ChoiceArrayField(
    models.CharField(
      'Schließungen',
      max_length=255,
      choices=()),
    verbose_name='Schließungen',
    blank=True,
    null=True)
  bemerkungen = models.CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"poller_hro'
    verbose_name = 'Poller'
    verbose_name_plural = 'Poller'
    description = 'Poller in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'schliessungen': 'Schliessungen_Poller'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'status': 'Status',
      'hersteller': 'Hersteller',
      'typ': 'Typ',
      'anzahl': 'Anzahl',
      'schliessungen': 'Schließungen'
    }
    list_fields_with_number = ['anzahl']
    list_fields_with_foreign_key = {
      'art': 'art',
      'status': 'status',
      'hersteller': 'bezeichnung',
      'typ': 'typ'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'art': 'Art',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'status': 'Status',
      'hersteller': 'Hersteller',
      'typ': 'Typ',
      'anzahl': 'Anzahl',
      'schliessungen': 'Schließungen'
    }
    map_filter_fields_as_list = ['art', 'status', 'hersteller', 'typ']
    geometry_type = 'Point'
    as_overlay = True

  def __str__(self):
    return (self.nummer + ', ' if self.nummer else '') + \
           self.bezeichnung + ' [Status: ' + str(self.status) + ']'

  def save(self, *args, **kwargs):
    super(Poller, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Poller, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Poller)

signals.post_delete.connect(functions.remove_permissions, sender=Poller)


# Rettungswachen

class Rettungswachen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  traeger = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=models.RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='traeger+')
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
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
    return self.bezeichnung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    super(Rettungswachen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Rettungswachen, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Rettungswachen)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Rettungswachen)


# Schiffsliegeplätze

class Schiffsliegeplaetze(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  hafen = models.ForeignKey(
    models_codelist.Haefen,
    verbose_name='Hafen',
    on_delete=models.CASCADE,
    db_column='hafen',
    to_field='uuid',
    related_name='haefen+')
  liegeplatznummer = models.CharField(
    'Liegeplatz',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  liegeplatzlaenge = models.DecimalField(
    'Liegeplatzlänge (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Liegeplatzlänge</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Liegeplatzlänge</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  zulaessiger_tiefgang = models.DecimalField(
    'zulässiger Tiefgang (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>zulässige Tiefgang</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('99.99'),
        'Der <strong><em>zulässige Tiefgang</em></strong> darf höchstens 99,99 m betragen.')],
    blank=True,
    null=True)
  zulaessige_schiffslaenge = models.DecimalField(
    'zulässige Schiffslänge (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>zulässige Schiffslänge</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>zulässige Schiffslänge</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  kaihoehe = models.DecimalField(
    'Kaihöhe (in m)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Kaihöhe</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Kaihöhe</em></strong> darf höchstens 9,99 m betragen.')],
    blank=True,
    null=True)
  pollerzug = models.CharField(
    'Pollerzug',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  poller_von = models.CharField(
    'Poller (von)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  poller_bis = models.CharField(
    'Poller (bis)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message),
      RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message),
      RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message),
      RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message),
      RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message)])
  geometrie = models.PolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"schiffsliegeplaetze_hro'
    verbose_name = 'Schiffsliegeplatz'
    verbose_name_plural = 'Schiffsliegeplätze'
    description = 'Schiffsliegeplätze der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'hafen': 'Hafen',
      'liegeplatznummer': 'Liegeplatz',
      'bezeichnung': 'Bezeichnung',
      'zulaessiger_tiefgang': 'zulässiger Tiefgang (in m)'
    }
    list_fields_with_foreign_key = {
      'hafen': 'bezeichnung'
    }
    list_fields_with_number = ['zulaessiger_tiefgang']
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'hafen': 'Hafen',
      'liegeplatznummer': 'Liegeplatz',
      'bezeichnung': 'Bezeichnung',
    }
    map_filter_fields_as_list = ['hafen']
    geometry_type = 'Polygon'
    as_overlay = True

  def __str__(self):
    return self.liegeplatznummer + ', ' + \
           self.bezeichnung + ' [Hafen: ' + str(self.hafen) + ']'

  def save(self, *args, **kwargs):
    super(Schiffsliegeplaetze, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Schiffsliegeplaetze, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Schiffsliegeplaetze)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Schiffsliegeplaetze)


# Schutzzäune gegen Tierseuchen

class Schutzzaeune_Tierseuchen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  tierseuche = models.ForeignKey(
    models_codelist.Tierseuchen,
    verbose_name='Tierseuche',
    on_delete=models.RESTRICT,
    db_column='tierseuche',
    to_field='uuid',
    related_name='tierseuchen+')
  zustand = models.ForeignKey(
    models_codelist.Zustaende_Schutzzaeune_Tierseuchen,
    verbose_name='Zustand',
    on_delete=models.RESTRICT,
    db_column='zustand',
    to_field='uuid',
    related_name='zustaende+')
  laenge = models.PositiveIntegerField('Länge (in m)', default=0)
  geometrie = models.MultiLineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"schutzzaeune_tierseuchen_hro'
    verbose_name = 'Schutzzaun gegen eine Tierseuche'
    verbose_name_plural = 'Schutzzäune gegen Tierseuchen'
    description = 'Schutzzäune gegen Tierseuchen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'tierseuche': 'Tierseuche',
      'laenge': 'Länge (in m)',
      'zustand': 'Zustand'}
    list_fields_with_foreign_key = {
      'tierseuche': 'bezeichnung',
      'zustand': 'zustand'
    }
    list_fields_with_number = ['laenge']
    readonly_fields = ['laenge']
    map_feature_tooltip_field = 'zustand'
    map_filter_fields = {
      'tierseuche': 'Tierseuche',
      'zustand': 'Zustand'}
    map_filter_fields_as_list = [
      'tierseuche', 'zustand']
    geometry_type = 'MultiLineString'
    as_overlay = True

  def __str__(self):
    return str(self.tierseuche) + ', ' + str(self.zustand)

  def save(self, *args, **kwargs):
    super(Schutzzaeune_Tierseuchen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Schutzzaeune_Tierseuchen, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Schutzzaeune_Tierseuchen)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Schutzzaeune_Tierseuchen)


# Sporthallen

class Sporthallen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  traeger = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=models.RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='traeger+')
  sportart = models.ForeignKey(
    models_codelist.Sportarten,
    verbose_name='Sportart',
    on_delete=models.RESTRICT,
    db_column='sportart',
    to_field='uuid',
    related_name='sportarten+')
  barrierefrei = models.BooleanField(' barrierefrei?', blank=True, null=True)
  zeiten = models.CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True)
  foto = models.ImageField(
    'Foto',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC +
      'sporthallen'),
    max_length=255,
    blank=True,
    null=True)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"sporthallen_hro'
    verbose_name = 'Sporthalle'
    verbose_name_plural = 'Sporthallen'
    description = 'Sporthallen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
      'sportart': 'Sportart',
      'foto': 'Foto'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'traeger': 'bezeichnung',
      'sportart': 'bezeichnung'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
      'sportart': 'Sportart'
    }
    map_filter_fields_as_list = ['traeger', 'sportart']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    thumbs = True

  def __str__(self):
    return self.bezeichnung + ' [' + (
      'Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
           'Träger: ' + str(self.traeger) + ', Sportart: ' + str(self.sportart) + ']'

  def save(self, *args, **kwargs):
    super(Sporthallen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Sporthallen, self).delete(*args, **kwargs)


signals.pre_save.connect(functions.get_pre_save_instance, sender=Sporthallen)

signals.post_save.connect(functions.photo_post_processing, sender=Sporthallen)

signals.post_save.connect(
  functions.delete_photo_after_emptied,
  sender=Sporthallen)

signals.post_save.connect(functions.assign_permissions, sender=Sporthallen)

signals.post_delete.connect(functions.delete_photo, sender=Sporthallen)

signals.post_delete.connect(functions.remove_permissions, sender=Sporthallen)


# Stadtteil- und Begegnungszentren

class Stadtteil_Begegnungszentren(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  traeger = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=models.RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='traeger+')
  barrierefrei = models.BooleanField(' barrierefrei?', blank=True, null=True)
  zeiten = models.CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True)
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
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
    return self.bezeichnung + ' [' + ('Adresse: ' + str(
      self.adresse) + ', ' if self.adresse else '') + 'Träger: ' + str(self.traeger) + ']'

  def save(self, *args, **kwargs):
    super(Stadtteil_Begegnungszentren, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Stadtteil_Begegnungszentren, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Stadtteil_Begegnungszentren)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Stadtteil_Begegnungszentren)


# Straßenreinigung

class Strassenreinigung(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False
  )
  aktiv = models.BooleanField(' aktiv?', default=True)
  id = models.CharField('ID', max_length=14, default='0000000000-000')
  strasse = models.ForeignKey(
    models_codelist.Strassen,
    verbose_name='Straße',
    on_delete=models.SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='strassen+',
    blank=True,
    null=True
  )
  inoffizielle_strasse = models.ForeignKey(
    models_codelist.Inoffizielle_Strassen,
    verbose_name=' inoffizielle Straße',
    on_delete=models.SET_NULL,
    db_column='inoffizielle_strasse',
    to_field='uuid',
    related_name='inoffizielle_strassen+',
    blank=True,
    null=True
  )
  beschreibung = models.CharField(
    'Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )])
  ausserhalb = models.BooleanField(' außerhalb geschlossener Ortslage?')
  reinigungsklasse = models.ForeignKey(
    models_codelist.Reinigungsklassen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsklasse',
    on_delete=models.SET_NULL,
    db_column='reinigungsklasse',
    to_field='uuid',
    related_name='reinigungsklassen+',
    blank=True,
    null=True
  )
  reinigungsrhythmus = models.ForeignKey(
    models_codelist.Reinigungsrhythmen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsrhythmus',
    on_delete=models.SET_NULL,
    db_column='reinigungsrhythmus',
    to_field='uuid',
    related_name='reinigungsrhythmen+',
    blank=True,
    null=True
  )
  fahrbahnwinterdienst = models.ForeignKey(
    models_codelist.Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO,
    verbose_name='Fahrbahnwinterdienst',
    on_delete=models.SET_NULL,
    db_column='fahrbahnwinterdienst',
    to_field='uuid',
    related_name='fahrbahnwinterdienste+',
    blank=True,
    null=True
  )
  laenge = models.DecimalField(
    'Länge (in m)',
    max_digits=6,
    decimal_places=2,
    default=0
  )
  geometrie = models.MultiLineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten_strassenbezug\".\"strassenreinigung_hro'
    verbose_name = 'Straßenreinigung'
    verbose_name_plural = 'Straßenreinigung'
    description = 'Straßenreinigung der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'inoffizielle_strasse': 'inoffizielle Straße',
      'beschreibung': 'Beschreibung',
      'ausserhalb': 'außerhalb geschlossener Ortslage?',
      'reinigungsklasse': 'Reinigungsklasse',
      'reinigungsrhythmus': 'Reinigungsrhythmus',
      'fahrbahnwinterdienst': 'Fahrbahnwinterdienst',
      'laenge': 'Länge (in m)'
    }
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'inoffizielle_strasse': 'strasse',
      'reinigungsklasse': 'code',
      'reinigungsrhythmus': 'reinigungsrhythmus',
      'fahrbahnwinterdienst': 'code'
    }
    list_fields_with_number = ['id', 'laenge']
    readonly_fields = ['id', 'laenge']
    map_feature_tooltip_field = 'id'
    map_filter_fields = {
      'id': 'ID',
      'strasse': 'Straße',
      'inoffizielle_strasse': 'inoffizielle Straße',
      'beschreibung': 'Beschreibung',
      'ausserhalb': 'außerhalb geschlossener Ortslage?',
      'reinigungsklasse': 'Reinigungsklasse',
      'reinigungsrhythmus': 'Reinigungsrhythmus',
      'fahrbahnwinterdienst': 'Fahrbahnwinterdienst'
    }
    map_filter_fields_as_list = [
      'strasse',
      'inoffizielle_strasse',
      'reinigungsklasse',
      'reinigungsrhythmus',
      'fahrbahnwinterdienst'
    ]
    additional_wms_layers = [{'title': 'Straßenreinigung',
                              'url': 'https://geo.sv.rostock.de/geodienste/strassenreinigung/wms',
                              'layers': 'hro.strassenreinigung.strassenreinigung'}]
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'MultiLineString'
    as_overlay = True

  def __str__(self):
    return str(self.id) + (', ' + str(self.beschreibung) if self.beschreibung else '') + (
        ', außerhalb geschlossener Ortslage' if self.ausserhalb else '') + (
        ', Reinigungsklasse '
        + str(self.reinigungsklasse) if self.reinigungsklasse else '') + (
        ', Fahrbahnwinterdienst '
        + str(self.fahrbahnwinterdienst) if self.fahrbahnwinterdienst else '') + (
        ' [Straße: ' + str(self.strasse) + ']' if self.strasse else '') + (
        ' [inoffizielle Straße: '
        + str(self.inoffizielle_strasse) + ']' if self.inoffizielle_strasse else '')

  def save(self, *args, **kwargs):
    super(Strassenreinigung, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Strassenreinigung, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Strassenreinigung)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Strassenreinigung)


# Thalasso-Kurwege

class Thalasso_Kurwege(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField(
    'Bezeichnung', max_length=255, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  streckenbeschreibung = models.CharField(
    'Streckenbeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  barrierefrei = models.BooleanField(' barrierefrei?', default=False)
  farbe = models.CharField('Farbe', max_length=7)
  beschriftung = models.CharField(
    'Beschriftung', max_length=255, blank=True, null=True, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  laenge = models.PositiveIntegerField('Länge (in m)', default=0)
  geometrie = models.LineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"thalasso_kurwege_hro'
    verbose_name = 'Thalasso-Kurweg'
    verbose_name_plural = 'Thalasso-Kurwege'
    description = 'Thalasso-Kurwege in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'streckenbeschreibung': 'Streckenbeschreibung',
      'barrierefrei': 'barrierefrei?',
      'farbe': 'Farbe',
      'beschriftung': 'Beschriftung',
      'laenge': 'Länge (in m)'
    }
    list_fields_with_number = ['laenge']
    readonly_fields = ['laenge']
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'streckenbeschreibung': 'Streckenbeschreibung',
      'barrierefrei': 'barrierefrei?'}
    geometry_type = 'LineString'

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Thalasso_Kurwege, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Thalasso_Kurwege, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Thalasso_Kurwege)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Thalasso_Kurwege)


# Toiletten

class Toiletten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  art = models.ForeignKey(
    models_codelist.Arten_Toiletten,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  bewirtschafter = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=models.SET_NULL,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='bewirtschafter+',
    blank=True,
    null=True)
  behindertengerecht = models.BooleanField(' behindertengerecht?')
  duschmoeglichkeit = models.BooleanField('Duschmöglichkeit vorhanden?')
  wickelmoeglichkeit = models.BooleanField('Wickelmöglichkeit vorhanden?')
  zeiten = models.CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"toiletten_hro'
    verbose_name = 'Toilette'
    verbose_name_plural = 'Toiletten'
    description = 'Toiletten in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'behindertengerecht': 'behindertengerecht?',
      'duschmoeglichkeit': 'Duschmöglichkeit vorhanden?',
      'wickelmoeglichkeit': 'Wickelmöglichkeit?',
      'zeiten': 'Öffnungszeiten'
    }
    list_fields_with_foreign_key = {
      'art': 'art',
      'bewirtschafter': 'bezeichnung'
    }
    map_feature_tooltip_field = 'art'
    map_filter_fields = {
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'behindertengerecht': 'behindertengerecht?',
      'duschmoeglichkeit': 'Duschmöglichkeit vorhanden?',
      'wickelmoeglichkeit': 'Wickelmöglichkeit?'
    }
    map_filter_fields_as_list = ['art', 'bewirtschafter']
    geometry_type = 'Point'
    as_overlay = True

  def __str__(self):
    return str(self.art) + ((' [Bewirtschafter: '
                             + str(self.bewirtschafter) + ']'
                             if self.bewirtschafter else '')) \
           + ((' mit Öffnungszeiten ' + self.zeiten + ']'
               if self.zeiten else ''))

  def save(self, *args, **kwargs):
    super(Toiletten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Toiletten, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Toiletten)

signals.post_delete.connect(functions.remove_permissions, sender=Toiletten)


# Trinkwassernotbrunnen

class Trinkwassernotbrunnen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  nummer = models.CharField(
    'Nummer',
    max_length=12,
    validators=[
      RegexValidator(
        regex=constants_vars.twnb_nummer_regex,
        message=constants_vars.twnb_nummer_message)])
  bezeichnung = models.CharField(
    'Bezeichnung', max_length=255, validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )])
  eigentuemer = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=models.SET_NULL,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='eigentuemer+',
    blank=True,
    null=True)
  betreiber = models.ForeignKey(
    models_codelist.Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=models.RESTRICT,
    db_column='betreiber',
    to_field='uuid',
    related_name='betreiber+')
  betriebsbereit = models.BooleanField(' betriebsbereit?')
  bohrtiefe = models.DecimalField(
    'Bohrtiefe (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Bohrtiefe</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Bohrtiefe</em></strong> darf höchstens 99,99 m betragen.')])
  ausbautiefe = models.DecimalField(
    'Ausbautiefe (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Ausbautiefe</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Ausbautiefe</em></strong> darf höchstens 99,99 m betragen.')])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten\".\"trinkwassernotbrunnen_hro'
    verbose_name = 'Trinkwassernotbrunnen'
    verbose_name_plural = 'Trinkwassernotbrunnen'
    description = 'Trinkwassernotbrunnen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'eigentuemer': 'Eigentümer',
      'betreiber': 'Betreiber',
      'betriebsbereit': 'betriebsbereit?',
      'bohrtiefe': 'Bohrtiefe (in m)',
      'ausbautiefe': 'Ausbautiefe (in m)'
    }
    list_fields_with_number = ['bohrtiefe', 'ausbautiefe']
    list_fields_with_foreign_key = {
      'eigentuemer': 'bezeichnung',
      'betreiber': 'bezeichnung'
    }
    map_feature_tooltip_field = 'nummer'
    map_filter_fields = {
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'eigentuemer': 'Eigentümer',
      'betreiber': 'Betreiber',
      'betriebsbereit': 'betriebsbereit?'
    }
    map_filter_fields_as_list = ['eigentuemer', 'betreiber']
    geometry_type = 'Point'

  def __str__(self):
    return self.nummer

  def save(self, *args, **kwargs):
    super(Trinkwassernotbrunnen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Trinkwassernotbrunnen, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.assign_permissions,
  sender=Trinkwassernotbrunnen)

signals.post_delete.connect(
  functions.remove_permissions,
  sender=Trinkwassernotbrunnen)


# Vereine

class Vereine(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  vereinsregister_id = fields.PositiveSmallIntegerMinField(
    'ID im Vereinsregister',
    min_value=1,
    unique=True,
    blank=True,
    null=True
  )
  vereinsregister_datum = models.DateField(
    'Datum des Eintrags im Vereinsregister', blank=True, null=True)
  schlagwoerter = fields.ChoiceArrayField(
    models.CharField(
      'Schlagwörter',
      max_length=255,
      choices=()),
    verbose_name='Schlagwörter')
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

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
      'adresse': 'adresse'
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
    return self.bezeichnung + \
           (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    super(Vereine, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Vereine, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions, sender=Vereine)

signals.post_delete.connect(functions.remove_permissions, sender=Vereine)


# Verkaufstellen für Angelberechtigungen

class Verkaufstellen_Angelberechtigungen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  adresse = models.ForeignKey(
    models_codelist.Adressen,
    verbose_name='Adresse',
    on_delete=models.SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='adressen+',
    blank=True,
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=[
      RegexValidator(
        regex=constants_vars.akut_regex,
        message=constants_vars.akut_message
      ), RegexValidator(
        regex=constants_vars.anfuehrungszeichen_regex,
        message=constants_vars.anfuehrungszeichen_message
      ), RegexValidator(
        regex=constants_vars.apostroph_regex,
        message=constants_vars.apostroph_message
      ), RegexValidator(
        regex=constants_vars.doppelleerzeichen_regex,
        message=constants_vars.doppelleerzeichen_message
      ), RegexValidator(
        regex=constants_vars.gravis_regex,
        message=constants_vars.gravis_message
      )
    ]
  )
  berechtigungen = fields.ChoiceArrayField(
    models.CharField(
      'verkaufte Berechtigung(en)',
      max_length=255,
      choices=()),
    verbose_name='verkaufte Berechtigung(en)',
    blank=True,
    null=True)
  barrierefrei = models.BooleanField(' barrierefrei?', blank=True, null=True)
  zeiten = models.CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True)
  telefon_festnetz = models.CharField(
    'Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  telefon_mobil = models.CharField(
    'Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.rufnummer_regex,
        message=constants_vars.rufnummer_message)])
  email = models.CharField(
    'E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=constants_vars.email_message)])
  website = models.CharField(
    'Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=constants_vars.url_message)])
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    db_table = 'fachdaten_adressbezug\".\"verkaufstellen_angelberechtigungen_hro'
    verbose_name = 'Verkaufstelle für Angelberechtigungen'
    verbose_name_plural = 'Verkaufstellen für Angelberechtigungen'
    description = 'Verkaufstellen für Angelberechtigungen in der Hanse- und Universitätsstadt ' \
                  'Rostock'
    choices_models_for_choices_fields = {
      'berechtigungen': 'Angelberechtigungen'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'berechtigungen': 'verkaufte Berechtigung(en)'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'berechtigungen': 'verkaufte Berechtigung(en)'
    }
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'

  def __str__(self):
    return self.bezeichnung + \
           (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')

  def save(self, *args, **kwargs):
    super(Verkaufstellen_Angelberechtigungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Verkaufstellen_Angelberechtigungen, self).delete(*args, **kwargs)


signals.post_save.connect(functions.assign_permissions,
                          sender=Verkaufstellen_Angelberechtigungen)

signals.post_delete.connect(functions.remove_permissions,
                            sender=Verkaufstellen_Angelberechtigungen)
