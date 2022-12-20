import re
import uuid

from datetime import date, datetime, timezone
from decimal import *
from django.conf import settings
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, \
  RegexValidator, URLValidator
from django.db.models import signals
from zoneinfo import ZoneInfo

from . import models_codelist, constants_vars, fields, functions, storage


#
# Baustellen-Fotodokumentation
#

# Baustellen

class Baustellen_Fotodokumentation_Baustellen(models.Model):
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
    null=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  verkehrliche_lagen = fields.ChoiceArrayField(
    models.CharField(
      ' verkehrliche Lage(n)',
      max_length=255,
      choices=()),
    verbose_name=' verkehrliche Lage(n)')
  sparten = fields.ChoiceArrayField(
    models.CharField(
      'Sparte(n)',
      max_length=255,
      choices=()),
    verbose_name='Sparte(n)')
  auftraggeber = models.ForeignKey(
    models_codelist.Auftraggeber_Baustellen,
    verbose_name='Auftraggeber',
    on_delete=models.RESTRICT,
    db_column='auftraggeber',
    to_field='uuid',
    related_name='auftraggeber+')
  ansprechpartner = models.CharField(
    'Ansprechpartner',
    max_length=255,
    validators=constants_vars.ansprechpartner_validators
  )
  bemerkungen = models.CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten_strassenbezug\".\"baustellen_fotodokumentation_baustellen_hro'
    verbose_name = 'Baustelle der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Baustellen der Baustellen-Fotodokumentation'
    description = 'Baustellen der Baustellen-Fotodokumentation in der Hanse- und ' \
                  'Universitätsstadt Rostock'
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
      'strasse': 'strasse',
      'auftraggeber': 'auftraggeber'
    }
    associated_models = {
      'Baustellen_Fotodokumentation_Fotos': 'baustellen_fotodokumentation_baustelle'}
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
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung + \
           (' [Straße: ' + str(self.strasse) + ']' if self.strasse else '')

  def save(self, *args, **kwargs):
    super(
      Baustellen_Fotodokumentation_Baustellen,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Baustellen_Fotodokumentation_Baustellen,
      self).delete(
      *args,
      **kwargs)


# Fotos

class Baustellen_Fotodokumentation_Fotos(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  baustellen_fotodokumentation_baustelle = models.ForeignKey(
    Baustellen_Fotodokumentation_Baustellen,
    verbose_name='Baustelle',
    on_delete=models.CASCADE,
    db_column='baustellen_fotodokumentation_baustelle',
    to_field='uuid',
    related_name='baustellen_fotodokumentation_baustellen+')
  status = models.ForeignKey(
    models_codelist.Status_Baustellen_Fotodokumentation_Fotos,
    verbose_name='Status',
    on_delete=models.RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='status+')
  aufnahmedatum = models.DateField('Aufnahmedatum', default=date.today)
  dateiname_original = models.CharField(
    'Original-Dateiname', max_length=255, default='ohne')
  foto = models.ImageField(
    'Foto',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE +
      'baustellen_fotodokumentation'),
    max_length=255)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"baustellen_fotodokumentation_fotos_hro'
    verbose_name = 'Foto der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Fotos der Baustellen-Fotodokumentation'
    description = 'Fotos der Baustellen-Fotodokumentation in der Hanse- und Universitätsstadt ' \
                  'Rostock'
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
      'baustellen_fotodokumentation_baustelle': 'bezeichnung',
      'status': 'status'
    }
    fields_with_foreign_key_to_linkify = [
      'baustellen_fotodokumentation_baustelle']
    object_title = 'das Foto'
    foreign_key_label = 'Baustelle'
    thumbs = True
    multi_foto_field = True

  def __str__(self):
    return str(self.baustellen_fotodokumentation_baustelle) + ' mit Status ' + str(self.status) + \
           ' und Aufnahmedatum ' + datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime(
      '%d.%m.%Y')

  def save(self, *args, **kwargs):
    super(Baustellen_Fotodokumentation_Fotos, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Baustellen_Fotodokumentation_Fotos, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.photo_post_processing,
  sender=Baustellen_Fotodokumentation_Fotos)

signals.post_delete.connect(
  functions.delete_photo,
  sender=Baustellen_Fotodokumentation_Fotos)


#
# Baustellen (geplant)
#

# Baustellen

class Baustellen_geplant(models.Model):
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
    null=True)
  projektbezeichnung = models.CharField(
    'Projektbezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  kurzbeschreibung = fields.NullTextField(
    'Kurzbeschreibung',
    max_length=500,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  lagebeschreibung = models.CharField(
    'Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  verkehrliche_lagen = fields.ChoiceArrayField(
    models.CharField(
      ' verkehrliche Lage(n)',
      max_length=255,
      choices=()),
    verbose_name=' verkehrliche Lage(n)')
  sparten = fields.ChoiceArrayField(
    models.CharField(
      'Sparte(n)',
      max_length=255,
      choices=()),
    verbose_name='Sparte(n)')
  beginn = models.DateField('Beginn')
  ende = models.DateField('Ende')
  auftraggeber = models.ForeignKey(
    models_codelist.Auftraggeber_Baustellen,
    verbose_name='Auftraggeber',
    on_delete=models.RESTRICT,
    db_column='auftraggeber',
    to_field='uuid',
    related_name='auftraggeber+')
  ansprechpartner = models.CharField(
    'Ansprechpartner',
    max_length=255,
    validators=constants_vars.ansprechpartner_validators
  )
  status = models.ForeignKey(
    models_codelist.Status_Baustellen_geplant,
    verbose_name='Status',
    on_delete=models.RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='status+')
  konflikt = models.BooleanField(
    'Konflikt?',
    blank=True,
    null=True,
    editable=False)
  konflikt_tolerieren = models.BooleanField(
    ' räumliche(n)/zeitliche(n) Konflikt(e) mit anderem/anderen Vorhaben tolerieren?',
    blank=True,
    null=True)
  geometrie = models.MultiPolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    complex = True
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
      'strasse': 'strasse',
      'auftraggeber': 'auftraggeber',
      'status': 'status'
    }
    associated_models = {
      'Baustellen_geplant_Dokumente': 'baustelle_geplant',
      'Baustellen_geplant_Links': 'baustelle_geplant'
    }
    highlight_flag = 'konflikt'
    map_feature_tooltip_field = 'bezeichnung'
    map_deadlinefilter_fields = ['beginn', 'ende']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'sparten': 'Sparte(n)',
      'auftraggeber': 'Auftraggeber',
      'status': 'Status'
    }
    map_filter_fields_as_list = ['auftraggeber']
    map_filter_fields_as_checkbox = ['status']
    map_filter_hide_initial = {
      'status': 'abgeschlossen'
    }
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'MultiPolygon'
    group_with_users_for_choice_field = 'baustellen_geplant_full'
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']
    as_overlay = True

  def __str__(self):
    return self.bezeichnung \
           + ' [' \
           + ('Straße: '
              + str(self.strasse)
              + ', ' if self.strasse else '') \
           + 'Beginn: ' \
           + datetime.strptime(str(self.beginn), '%Y-%m-%d').strftime('%d.%m.%Y') \
           + ', Ende: ' + datetime.strptime(str(self.ende), '%Y-%m-%d').strftime('%d.%m.%Y')\
           + ']'

  def save(self, *args, **kwargs):
    super(Baustellen_geplant, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Baustellen_geplant, self).delete(*args, **kwargs)


# Dokumente

class Baustellen_geplant_Dokumente(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  baustelle_geplant = models.ForeignKey(
    Baustellen_geplant,
    verbose_name='Baustelle (geplant)',
    on_delete=models.CASCADE,
    db_column='baustelle_geplant',
    to_field='uuid',
    related_name='baustellen_geplant+')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  dokument = models.FileField(
    'Dokument',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PDF_PATH_PREFIX_PUBLIC +
      'baustellen_geplant'),
    max_length=255)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"baustellen_geplant_dokumente'
    verbose_name = 'Dokument der Baustelle (geplant)'
    verbose_name_plural = 'Dokumente der Baustellen (geplant)'
    description = 'Dokumente der Baustellen (geplant) in der Hanse- und Universitätsstadt ' \
                  'Rostock und Umgebung'
    list_fields = {
      'aktiv': 'aktiv?',
      'baustelle_geplant': 'Baustelle (geplant)',
      'bezeichnung': 'Bezeichnung',
      'dokument': 'Dokument'
    }
    list_fields_with_foreign_key = {
      'baustelle_geplant': 'bezeichnung'
    }
    fields_with_foreign_key_to_linkify = ['baustelle_geplant']
    object_title = 'das Dokument'
    foreign_key_label = 'Baustelle (geplant)'

  def __str__(self):
    return str(self.baustelle_geplant) + \
           ' mit Bezeichnung ' + self.bezeichnung

  def save(self, *args, **kwargs):
    super(Baustellen_geplant_Dokumente, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Baustellen_geplant_Dokumente, self).delete(*args, **kwargs)


signals.post_delete.connect(
  functions.delete_pdf,
  sender=Baustellen_geplant_Dokumente)


# Links

class Baustellen_geplant_Links(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  baustelle_geplant = models.ForeignKey(
    Baustellen_geplant,
    verbose_name='Baustelle (geplant)',
    on_delete=models.CASCADE,
    db_column='baustelle_geplant',
    to_field='uuid',
    related_name='baustellen_geplant+')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  link = models.CharField(
    'Link', max_length=255, validators=[
      URLValidator(
        message=constants_vars.url_message)])

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"baustellen_geplant_links'
    verbose_name = 'Link der Baustelle (geplant)'
    verbose_name_plural = 'Links der Baustellen (geplant)'
    description = 'Links der Baustellen (geplant) in der Hanse- und Universitätsstadt Rostock ' \
                  'und Umgebung'
    list_fields = {
      'aktiv': 'aktiv?',
      'baustelle_geplant': 'Baustelle (geplant)',
      'bezeichnung': 'Bezeichnung',
      'link': 'Link'
    }
    list_fields_with_foreign_key = {
      'baustelle_geplant': 'bezeichnung'
    }
    fields_with_foreign_key_to_linkify = ['baustelle_geplant']
    object_title = 'der Link'
    foreign_key_label = 'Baustelle (geplant)'

  def __str__(self):
    return str(self.baustelle_geplant) + \
           ' mit Bezeichnung ' + self.bezeichnung

  def save(self, *args, **kwargs):
    super(Baustellen_geplant_Links, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Baustellen_geplant_Links, self).delete(*args, **kwargs)


#
# Durchlässe
#

# Durchlässe

class Durchlaesse_Durchlaesse(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  art = models.ForeignKey(
    models_codelist.Arten_Durchlaesse,
    verbose_name='Art',
    on_delete=models.SET_NULL,
    db_column='art',
    to_field='uuid',
    related_name='arten+',
    blank=True,
    null=True)
  aktenzeichen = models.CharField(
    'Aktenzeichen',
    max_length=255,
    unique=True,
    validators=[
      RegexValidator(
        regex=constants_vars.dl_aktenzeichen_regex,
        message=constants_vars.dl_aktenzeichen_message
      )
    ]
  )
  material = models.ForeignKey(
    models_codelist.Materialien_Durchlaesse,
    verbose_name='Material',
    on_delete=models.SET_NULL,
    db_column='material',
    to_field='uuid',
    related_name='materialien+',
    blank=True,
    null=True)
  baujahr = fields.PositiveSmallIntegerRangeField(
    'Baujahr', max_value=functions.current_year(), blank=True, null=True)
  nennweite = fields.PositiveSmallIntegerMinField(
    'Nennweite (in mm)', min_value=100, blank=True, null=True)
  laenge = models.DecimalField(
    'Länge (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Länge</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Länge</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  nebenanlagen = fields.NullTextField(
    'Nebenanlagen',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  zubehoer = fields.NullTextField(
    'Zubehör',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  zustand_durchlass = models.ForeignKey(
    models_codelist.Zustandsbewertungen,
    verbose_name='Zustand des Durchlasses',
    on_delete=models.SET_NULL,
    db_column='zustand_durchlass',
    to_field='uuid',
    related_name='zustaende_durchlaesse+',
    blank=True,
    null=True)
  zustand_nebenanlagen = models.ForeignKey(
    models_codelist.Zustandsbewertungen,
    verbose_name='Zustand der Nebenanlagen',
    on_delete=models.SET_NULL,
    db_column='zustand_nebenanlagen',
    to_field='uuid',
    related_name='zustaende_nebenanlagen+',
    blank=True,
    null=True)
  zustand_zubehoer = models.ForeignKey(
    models_codelist.Zustandsbewertungen,
    verbose_name='Zustand des Zubehörs',
    on_delete=models.SET_NULL,
    db_column='zustand_zubehoer',
    to_field='uuid',
    related_name='zustaende_zubehoer+',
    blank=True,
    null=True)
  kontrolle = models.DateField('Kontrolle', blank=True, null=True)
  bemerkungen = fields.NullTextField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  zustaendigkeit = models.CharField(
    'Zuständigkeit',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  bearbeiter = models.CharField(
    'Bearbeiter',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"durchlaesse_durchlaesse_hro'
    verbose_name = 'Durchlass'
    verbose_name_plural = 'Durchlässe'
    description = 'Durchlässe in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'aktenzeichen': 'Aktenzeichen',
      'material': 'Material',
      'baujahr': 'Baujahr',
      'nennweite': 'Nennweite (in mm)',
      'laenge': 'Länge (in m)',
      'zustaendigkeit': 'Zuständigkeit',
      'bearbeiter': 'Bearbeiter'
    }
    list_fields_with_foreign_key = {
      'art': 'art',
      'material': 'material'
    }
    list_fields_with_number = ['baujahr', 'nennweite', 'laenge']
    associated_models = {
      'Durchlaesse_Fotos': 'durchlaesse_durchlass'
    }
    map_feature_tooltip_field = 'aktenzeichen'
    map_filter_fields = {
      'art': 'Art',
      'aktenzeichen': 'Aktenzeichen',
      'material': 'Material',
      'zustaendigkeit': 'Zuständigkeit',
      'bearbeiter': 'Bearbeiter'
    }
    map_filter_fields_as_list = ['art', 'material']
    geometry_type = 'Point'
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['aktenzeichen']
    as_overlay = True

  def __str__(self):
    return self.aktenzeichen

  def save(self, *args, **kwargs):
    super(Durchlaesse_Durchlaesse, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Durchlaesse_Durchlaesse, self).delete(*args, **kwargs)


# Fotos

class Durchlaesse_Fotos(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  durchlaesse_durchlass = models.ForeignKey(
    Durchlaesse_Durchlaesse,
    verbose_name='Durchlass',
    on_delete=models.CASCADE,
    db_column='durchlaesse_durchlass',
    to_field='uuid',
    related_name='durchlaesse_durchlaesse+')
  aufnahmedatum = models.DateField(
    'Aufnahmedatum',
    default=date.today,
    blank=True,
    null=True)
  bemerkungen = fields.NullTextField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  dateiname_original = models.CharField(
    'Original-Dateiname', max_length=255, default='ohne')
  foto = models.ImageField(
    'Foto',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC +
      'durchlaesse'),
    max_length=255)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"durchlaesse_fotos_hro'
    verbose_name = 'Foto des Durchlasses'
    verbose_name_plural = 'Fotos der Durchlässe'
    description = 'Fotos der Durchlässe in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'durchlaesse_durchlass': 'Durchlass',
      'aufnahmedatum': 'Aufnahmedatum',
      'bemerkungen': 'Bemerkungen',
      'dateiname_original': 'Original-Dateiname',
      'foto': 'Foto'
    }
    readonly_fields = ['dateiname_original']
    list_fields_with_date = ['aufnahmedatum']
    list_fields_with_foreign_key = {
      'durchlaesse_durchlass': 'aktenzeichen'
    }
    fields_with_foreign_key_to_linkify = ['durchlaesse_durchlass']
    object_title = 'das Foto'
    foreign_key_label = 'Durchlass'
    thumbs = True
    multi_foto_field = True

  def __str__(self):
    return str(self.durchlaesse_durchlass) + (' mit Aufnahmedatum ' + datetime.strptime(
      str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y') if self.aufnahmedatum else '')

  def save(self, *args, **kwargs):
    super(Durchlaesse_Fotos, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Durchlaesse_Fotos, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.photo_post_processing,
  sender=Durchlaesse_Fotos)

signals.post_delete.connect(functions.delete_photo, sender=Durchlaesse_Fotos)


#
# Fallwildsuchen
#

# Kontrollgebiete

class Fallwildsuchen_Kontrollgebiete(models.Model):
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
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  geometrie = models.PolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"fallwildsuchen_kontrollgebiete_hro'
    verbose_name = 'Kontrollgebiet im Rahmen einer Fallwildsuche'
    verbose_name_plural = 'Kontrollgebiete im Rahmen von Fallwildsuchen'
    description = 'Kontrollgebiete im Rahmen von Fallwildsuchen in der Hanse- und ' \
                  'Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'tierseuche': 'Tierseuche',
      'bezeichnung': 'Bezeichnung'}
    list_fields_with_foreign_key = {
      'tierseuche': 'bezeichnung'
    }
    associated_models = {
      'Fallwildsuchen_Nachweise': 'kontrollgebiet'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'tierseuche': 'Tierseuche',
      'bezeichnung': 'Bezeichnung'}
    map_filter_fields_as_list = [
      'tierseuche']
    geometry_type = 'Polygon'
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']
    as_overlay = True

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Fallwildsuchen_Kontrollgebiete, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Fallwildsuchen_Kontrollgebiete, self).delete(*args, **kwargs)


# Nachweise

class Fallwildsuchen_Nachweise(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  kontrollgebiet = models.ForeignKey(
    Fallwildsuchen_Kontrollgebiete,
    verbose_name='Kontrollgebiet',
    on_delete=models.CASCADE,
    db_column='kontrollgebiet',
    to_field='uuid',
    related_name='kontrollgebiete+')
  art_kontrolle = models.ForeignKey(
    models_codelist.Arten_Fallwildsuchen_Kontrollen,
    verbose_name='Art der Kontrolle',
    on_delete=models.RESTRICT,
    db_column='art_kontrolle',
    to_field='uuid',
    related_name='arten_kontrolle+')
  startzeitpunkt = models.DateTimeField('Startzeitpunkt')
  endzeitpunkt = models.DateTimeField('Endzeitpunkt')
  geometrie = models.MultiLineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"fallwildsuchen_nachweise_hro'
    verbose_name = 'Nachweis im Rahmen einer Fallwildsuche'
    verbose_name_plural = 'Nachweise im Rahmen von Fallwildsuchen'
    description = 'Nachweise im Rahmen von Fallwildsuchen in der Hanse- und Universitätsstadt ' \
                  'Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'kontrollgebiet': 'Kontrollgebiet',
      'art_kontrolle': 'Art der Kontrolle',
      'startzeitpunkt': 'Startzeitpunkt',
      'endzeitpunkt': 'Endzeitpunkt'}
    list_fields_with_datetime = ['startzeitpunkt', 'endzeitpunkt']
    list_fields_with_foreign_key = {
      'kontrollgebiet': 'bezeichnung',
      'art_kontrolle': 'art'
    }
    map_feature_tooltip_field = 'art_kontrolle'
    map_rangefilter_fields = {
      'startzeitpunkt': 'Startzeitpunkt',
      'endzeitpunkt': 'Endzeitpunkt'
    }
    map_filter_fields = {
      'kontrollgebiet': 'Kontrollgebiet',
      'art_kontrolle': 'Art der Kontrolle'}
    map_filter_fields_as_list = [
      'kontrollgebiet', 'art_kontrolle']
    geometry_type = 'MultiLineString'
    fields_with_foreign_key_to_linkify = ['kontrollgebiet']
    object_title = 'der Nachweis im Rahmen einer Fallwildsuche'
    foreign_key_label = 'Kontrollgebiet'
    gpx_input = True
    as_overlay = True

  def __str__(self):
    local_tz = ZoneInfo(settings.TIME_ZONE)
    startzeitpunkt_str = re.sub(
      r'([+-][0-9]{2}):',
      '\\1',
      str(self.startzeitpunkt)
    )
    startzeitpunkt = datetime.strptime(
      startzeitpunkt_str,
      '%Y-%m-%d %H:%M:%S%z'
    ).replace(tzinfo=timezone.utc).astimezone(local_tz)
    startzeitpunkt_str = startzeitpunkt.strftime('%d.%m.%Y, %H:%M:%S Uhr,')
    endzeitpunkt_str = re.sub(
      r'([+-][0-9]{2}):',
      '\\1',
      str(self.endzeitpunkt)
    )
    endzeitpunkt = datetime.strptime(
      endzeitpunkt_str,
      '%Y-%m-%d %H:%M:%S%z'
    ).replace(tzinfo=timezone.utc).astimezone(local_tz)
    endzeitpunkt_str = endzeitpunkt.strftime('%d.%m.%Y, %H:%M:%S Uhr')
    return str(self.kontrollgebiet) + ' mit Startzeitpunkt ' \
                                    + startzeitpunkt_str \
                                    + ' und Endzeitpunkt ' \
                                    + endzeitpunkt_str \
                                    + ' [Art der Kontrolle: ' \
                                    + str(self.art_kontrolle) + ']'

  def save(self, *args, **kwargs):
    super(Fallwildsuchen_Nachweise, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Fallwildsuchen_Nachweise, self).delete(*args, **kwargs)


#
# Haltestellenkataster
#

# Haltestellen

class Haltestellenkataster_Haltestellen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  deaktiviert = models.DateField(
    'Außerbetriebstellung', blank=True, null=True)
  id = models.PositiveIntegerField('ID', default=functions.sequence_id(
    'fachdaten.haltestellenkataster_haltestellen_hro_id_seq'))
  hst_bezeichnung = models.CharField(
    'Haltestellenbezeichnung',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  hst_hafas_id = models.CharField(
    'HAFAS-ID',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.hst_hst_hafas_id_regex,
        message=constants_vars.hst_hst_hafas_id_message
      )
    ]
  )
  hst_bus_bahnsteigbezeichnung = models.CharField(
    'Bus-/Bahnsteigbezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  hst_richtung = models.CharField(
    'Richtungsinformation',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  hst_kategorie = models.CharField(
    'Haltestellenkategorie',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  hst_linien = fields.ChoiceArrayField(
    models.CharField(
      ' bedienende Linie(n)',
      max_length=4,
      choices=()),
    verbose_name=' bedienende Linie(n)',
    blank=True,
    null=True)
  hst_rsag = models.BooleanField(
    ' bedient durch Rostocker Straßenbahn AG?',
    blank=True,
    null=True)
  hst_rebus = models.BooleanField(
    ' bedient durch rebus Regionalbus Rostock GmbH?',
    blank=True,
    null=True)
  hst_nur_ausstieg = models.BooleanField(
    ' nur Ausstieg?', blank=True, null=True)
  hst_nur_einstieg = models.BooleanField(
    ' nur Einstieg?', blank=True, null=True)
  hst_verkehrsmittelklassen = fields.ChoiceArrayField(
    models.CharField(
      'Verkehrsmittelklasse(n)',
      max_length=255,
      choices=()),
    verbose_name='Verkehrsmittelklasse(n)')
  hst_abfahrten = fields.PositiveSmallIntegerMinField(
    ' durchschnittliche tägliche Zahl an Abfahrten',
    min_value=1,
    blank=True,
    null=True)
  hst_fahrgastzahl_einstieg = fields.PositiveSmallIntegerMinField(
    ' durchschnittliche tägliche Fahrgastzahl (Einstieg)',
    min_value=1,
    blank=True,
    null=True)
  hst_fahrgastzahl_ausstieg = fields.PositiveSmallIntegerMinField(
    ' durchschnittliche tägliche Fahrgastzahl (Ausstieg)',
    min_value=1,
    blank=True,
    null=True)
  bau_typ = models.ForeignKey(
    models_codelist.Typen_Haltestellen,
    verbose_name='Typ',
    on_delete=models.SET_NULL,
    db_column='bau_typ',
    to_field='uuid',
    related_name='bau_typen+',
    blank=True,
    null=True)
  bau_wartebereich_laenge = models.DecimalField(
    'Länge des Wartebereichs (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Wartebereich</em></strong> muss mindestens 0,01 m lang sein.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Der <strong><em>Wartebereich</em></strong> darf höchstens 999,99 m lang sein.')],
    blank=True,
    null=True)
  bau_wartebereich_breite = models.DecimalField(
    'Breite des Wartebereichs (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Wartebereich</em></strong> muss mindestens 0,01 m breit sein.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Der <strong><em>Wartebereich</em></strong> darf höchstens 999,99 m breit sein.')],
    blank=True,
    null=True)
  bau_befestigungsart_aufstellflaeche_bus = models.ForeignKey(
    models_codelist.Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster,
    verbose_name='Befestigungsart der Aufstellfläche Bus',
    on_delete=models.SET_NULL,
    db_column='bau_befestigungsart_aufstellflaeche_bus',
    to_field='uuid',
    related_name='bau_befestigungsarten_aufstellflaeche_bus+',
    blank=True,
    null=True)
  bau_zustand_aufstellflaeche_bus = models.ForeignKey(
    models_codelist.Schaeden_Haltestellenkataster,
    verbose_name='Zustand der Aufstellfläche Bus',
    on_delete=models.SET_NULL,
    db_column='bau_zustand_aufstellflaeche_bus',
    to_field='uuid',
    related_name='bau_zustaende_aufstellflaeche_bus+',
    blank=True,
    null=True)
  bau_befestigungsart_warteflaeche = models.ForeignKey(
    models_codelist.Befestigungsarten_Warteflaeche_Haltestellenkataster,
    verbose_name='Befestigungsart der Wartefläche',
    on_delete=models.SET_NULL,
    db_column='bau_befestigungsart_warteflaeche',
    to_field='uuid',
    related_name='bau_befestigungsarten_warteflaeche+',
    blank=True,
    null=True)
  bau_zustand_warteflaeche = models.ForeignKey(
    models_codelist.Schaeden_Haltestellenkataster,
    verbose_name='Zustand der Wartefläche',
    on_delete=models.SET_NULL,
    db_column='bau_zustand_warteflaeche',
    to_field='uuid',
    related_name='bau_zustaende_warteflaeche+',
    blank=True,
    null=True)
  bf_einstieg = models.BooleanField(
    ' barrierefreier Einstieg vorhanden?', blank=True, null=True)
  bf_zu_abgaenge = models.BooleanField(
    ' barrierefreie Zu- und Abgänge vorhanden?', blank=True, null=True)
  bf_bewegungsraum = models.BooleanField(
    ' barrierefreier Bewegungsraum vorhanden?', blank=True, null=True)
  tl_auffindestreifen = models.BooleanField(
    'Taktiles Leitsystem: Auffindestreifen vorhanden?', blank=True, null=True)
  tl_auffindestreifen_ausfuehrung = models.ForeignKey(
    models_codelist.Ausfuehrungen_Haltestellenkataster,
    verbose_name='Taktiles Leitsystem: Ausführung Auffindestreifen',
    on_delete=models.SET_NULL,
    db_column='tl_auffindestreifen_ausfuehrung',
    to_field='uuid',
    related_name='tl_auffindestreifen_ausfuehrungen+',
    blank=True,
    null=True)
  tl_auffindestreifen_breite = fields.PositiveIntegerMinField(
    'Taktiles Leitsystem: Breite des Auffindestreifens (in cm)',
    min_value=1,
    blank=True,
    null=True)
  tl_einstiegsfeld = models.BooleanField(
    'Taktiles Leitsystem: Einstiegsfeld vorhanden?', blank=True, null=True)
  tl_einstiegsfeld_ausfuehrung = models.ForeignKey(
    models_codelist.Ausfuehrungen_Haltestellenkataster,
    verbose_name='Taktiles Leitsystem: Ausführung Einstiegsfeld',
    on_delete=models.SET_NULL,
    db_column='tl_einstiegsfeld_ausfuehrung',
    to_field='uuid',
    related_name='tl_einstiegsfeld_ausfuehrungen+',
    blank=True,
    null=True)
  tl_einstiegsfeld_breite = fields.PositiveIntegerMinField(
    'Taktiles Leitsystem: Breite des Einstiegsfelds (in cm)',
    min_value=1,
    blank=True,
    null=True)
  tl_leitstreifen = models.BooleanField(
    'Taktiles Leitsystem: Leitstreifen vorhanden?', blank=True, null=True)
  tl_leitstreifen_ausfuehrung = models.ForeignKey(
    models_codelist.Ausfuehrungen_Haltestellenkataster,
    verbose_name='Taktiles Leitsystem: Ausführung Leitstreifen',
    on_delete=models.SET_NULL,
    db_column='tl_leitstreifen_ausfuehrung',
    to_field='uuid',
    related_name='tl_leitstreifen_ausfuehrungen+',
    blank=True,
    null=True)
  tl_leitstreifen_laenge = fields.PositiveIntegerMinField(
    'Taktiles Leitsystem: Länge des Leitstreifens (in cm)',
    min_value=1,
    blank=True,
    null=True)
  tl_aufmerksamkeitsfeld = models.BooleanField(
    'Aufmerksamkeitsfeld (1. Tür) vorhanden?', blank=True, null=True)
  tl_bahnsteigkante_visuell = models.BooleanField(
    'Bahnsteigkante visuell erkennbar?', blank=True, null=True)
  tl_bahnsteigkante_taktil = models.BooleanField(
    'Bahnsteigkante taktil erkennbar?', blank=True, null=True)
  as_zh_typ = models.ForeignKey(
    models_codelist.ZH_Typen_Haltestellenkataster,
    verbose_name='ZH-Typ',
    on_delete=models.SET_NULL,
    db_column='as_zh_typ',
    to_field='uuid',
    related_name='as_zh_typen+',
    blank=True,
    null=True)
  as_h_mast = models.BooleanField('Mast vorhanden?', blank=True, null=True)
  as_h_masttyp = models.ForeignKey(
    models_codelist.Masttypen_Haltestellenkataster,
    verbose_name='Masttyp',
    on_delete=models.SET_NULL,
    db_column='as_h_masttyp',
    to_field='uuid',
    related_name='as_h_masttypen+',
    blank=True,
    null=True)
  as_papierkorb = models.BooleanField(
    'Papierkorb vorhanden?', blank=True, null=True)
  as_fahrgastunterstand = models.BooleanField(
    'Fahrgastunterstand vorhanden?', blank=True, null=True)
  as_fahrgastunterstandstyp = models.ForeignKey(
    models_codelist.Fahrgastunterstandstypen_Haltestellenkataster,
    verbose_name='Typ des Fahrgastunterstand',
    on_delete=models.SET_NULL,
    db_column='as_fahrgastunterstandstyp',
    to_field='uuid',
    related_name='as_fahrgastunterstandstypen+',
    blank=True,
    null=True)
  as_sitzbank_mit_armlehne = models.BooleanField(
    'Sitzbank mit Armlehne vorhanden?', blank=True, null=True)
  as_sitzbank_ohne_armlehne = models.BooleanField(
    'Sitzbank ohne Armlehne vorhanden?', blank=True, null=True)
  as_sitzbanktyp = models.ForeignKey(
    models_codelist.Sitzbanktypen_Haltestellenkataster,
    verbose_name='Typ der Sitzbank',
    on_delete=models.SET_NULL,
    db_column='as_sitzbanktyp',
    to_field='uuid',
    related_name='as_sitzbanktypen+',
    blank=True,
    null=True)
  as_gelaender = models.BooleanField(
    'Geländer vorhanden?', blank=True, null=True)
  as_fahrplanvitrine = models.BooleanField(
    'Fahrplanvitrine vorhanden?', blank=True, null=True)
  as_fahrplanvitrinentyp = models.ForeignKey(
    models_codelist.Fahrplanvitrinentypen_Haltestellenkataster,
    verbose_name='Typ der Fahrplanvitrine',
    on_delete=models.SET_NULL,
    db_column='as_fahrplanvitrinentyp',
    to_field='uuid',
    related_name='as_fahrplanvitrinentypen+',
    blank=True,
    null=True)
  as_tarifinformation = models.BooleanField(
    'Tarifinformation vorhanden?', blank=True, null=True)
  as_liniennetzplan = models.BooleanField(
    'Liniennetzplan vorhanden?', blank=True, null=True)
  as_fahrplan = models.BooleanField(
    'Fahrplan vorhanden?', blank=True, null=True)
  as_fahrausweisautomat = models.BooleanField(
    'Fahrausweisautomat vorhanden?', blank=True, null=True)
  as_lautsprecher = models.BooleanField(
    'Lautsprecher vorhanden?', blank=True, null=True)
  as_dfi = models.BooleanField(
    'Dynamisches Fahrgastinformationssystem vorhanden?',
    blank=True,
    null=True)
  as_dfi_typ = models.ForeignKey(
    models_codelist.DFI_Typen_Haltestellenkataster,
    verbose_name='Typ des Dynamischen Fahrgastinformationssystems',
    on_delete=models.SET_NULL,
    db_column='as_dfi_typ',
    to_field='uuid',
    related_name='as_dfi_typen+',
    blank=True,
    null=True)
  as_anfragetaster = models.BooleanField(
    'Anfragetaster vorhanden?', blank=True, null=True)
  as_blindenschrift = models.BooleanField(
    'Haltestellen-/Linieninformationen in Blindenschrift vorhanden?',
    blank=True,
    null=True)
  as_beleuchtung = models.BooleanField(
    'Beleuchtung vorhanden?', blank=True, null=True)
  as_hinweis_warnblinklicht_ein = models.BooleanField(
    'Hinweis „Warnblinklicht ein“ vorhanden?', blank=True, null=True)
  bfe_park_and_ride = models.BooleanField(
    'P+R-Parkplatz in Umgebung vorhanden?', blank=True, null=True)
  bfe_fahrradabstellmoeglichkeit = models.BooleanField(
    'Fahrradabstellmöglichkeit in Umgebung vorhanden?', blank=True, null=True)
  bfe_querungshilfe = models.BooleanField(
    'Querungshilfe in Umgebung vorhanden?', blank=True, null=True)
  bfe_fussgaengerueberweg = models.BooleanField(
    'Fußgängerüberweg in Umgebung vorhanden?', blank=True, null=True)
  bfe_seniorenheim = models.BooleanField(
    'Seniorenheim in Umgebung vorhanden?', blank=True, null=True)
  bfe_pflegeeinrichtung = models.BooleanField(
    'Pflegeeinrichtung in Umgebung vorhanden?', blank=True, null=True)
  bfe_medizinische_versorgungseinrichtung = models.BooleanField(
    'Medizinische Versorgungseinrichtung in Umgebung vorhanden?', blank=True, null=True)
  bearbeiter = models.CharField(
    'Bearbeiter',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  bemerkungen = fields.NullTextField(
    'Bemerkungen',
    max_length=500,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"haltestellenkataster_haltestellen_hro'
    unique_together = ['hst_hafas_id', 'hst_bus_bahnsteigbezeichnung']
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
    associated_models = {
      'Haltestellenkataster_Fotos': 'haltestellenkataster_haltestelle'
    }
    readonly_fields = ['id']
    map_feature_tooltip_field = 'hst_bezeichnung'
    geometry_type = 'Point'
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['id']
    as_overlay = True

  def __str__(self):
    return self.hst_bezeichnung + ' [ID: ' + str(self.id) \
           + (', HAFAS-ID: '
              + self.hst_hafas_id if self.hst_hafas_id else '') \
           + (', Bus-/Bahnsteig: '
              + self.hst_bus_bahnsteigbezeichnung if self.hst_bus_bahnsteigbezeichnung else '') \
           + ']'

  def save(self, *args, **kwargs):
    super(Haltestellenkataster_Haltestellen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Haltestellenkataster_Haltestellen, self).delete(*args, **kwargs)


# Fotos

class Haltestellenkataster_Fotos(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  haltestellenkataster_haltestelle = models.ForeignKey(
    Haltestellenkataster_Haltestellen,
    verbose_name='Haltestelle',
    on_delete=models.CASCADE,
    db_column='haltestellenkataster_haltestelle',
    to_field='uuid',
    related_name='haltestellenkataster_haltestellen+')
  motiv = models.ForeignKey(
    models_codelist.Fotomotive_Haltestellenkataster,
    verbose_name='Motiv',
    on_delete=models.RESTRICT,
    db_column='motiv',
    to_field='uuid',
    related_name='motive+')
  aufnahmedatum = models.DateField('Aufnahmedatum', default=date.today)
  dateiname_original = models.CharField(
    'Original-Dateiname', max_length=255, default='ohne')
  foto = models.ImageField(
    'Foto',
    storage=storage.OverwriteStorage(),
    upload_to=functions.path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE +
      'haltestellenkataster'),
    max_length=255)

  class Meta:
    managed = False
    complex = True
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
      'haltestellenkataster_haltestelle': 'id',
      'motiv': 'fotomotiv'
    }
    fields_with_foreign_key_to_linkify = [
      'haltestellenkataster_haltestelle']
    object_title = 'das Foto'
    foreign_key_label = 'Haltestelle'
    thumbs = True
    multi_foto_field = True

  def __str__(self):
    return str(self.haltestellenkataster_haltestelle) + ' mit Motiv ' + str(self.motiv) + \
           ' und Aufnahmedatum ' + datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime(
      '%d.%m.%Y')

  def save(self, *args, **kwargs):
    super(Haltestellenkataster_Fotos, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Haltestellenkataster_Fotos, self).delete(*args, **kwargs)


signals.post_save.connect(
  functions.photo_post_processing,
  sender=Haltestellenkataster_Fotos)

signals.post_delete.connect(
  functions.delete_photo,
  sender=Haltestellenkataster_Fotos)


#
# Parkscheinautomaten
#

# Tarife

class Parkscheinautomaten_Tarife(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=constants_vars.standard_validators
  )
  zeiten = models.CharField('Bewirtschaftungszeiten', max_length=255)
  normaltarif_parkdauer_min = fields.PositiveSmallIntegerMinField(
    'Mindestparkdauer Normaltarif', min_value=1)
  normaltarif_parkdauer_min_einheit = models.ForeignKey(
    models_codelist.Zeiteinheiten,
    verbose_name='Einheit der Mindestparkdauer Normaltarif',
    on_delete=models.RESTRICT,
    db_column='normaltarif_parkdauer_min_einheit',
    to_field='uuid',
    related_name='normaltarif_parkdauer_min_einheiten+')
  normaltarif_parkdauer_max = fields.PositiveSmallIntegerMinField(
    'Maximalparkdauer Normaltarif', min_value=1)
  normaltarif_parkdauer_max_einheit = models.ForeignKey(
    models_codelist.Zeiteinheiten,
    verbose_name='Einheit der Maximalparkdauer Normaltarif',
    on_delete=models.RESTRICT,
    db_column='normaltarif_parkdauer_max_einheit',
    to_field='uuid',
    related_name='normaltarif_parkdauer_max_einheiten+')
  normaltarif_gebuehren_max = models.DecimalField(
    'Maximalgebühren Normaltarif (in €)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Maximalgebühren Normaltarif</strong></em> müssen mindestens 0,'
        '01 € betragen.'),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Maximalgebühren Normaltarif</em></strong> dürfen höchstens 99,'
        '99 € betragen.')],
    blank=True,
    null=True)
  normaltarif_gebuehren_pro_stunde = models.DecimalField(
    'Gebühren pro Stunde Normaltarif (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro Stunde Normaltarif</strong></em> müssen mindestens 0,'
        '01 € betragen.'),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro Stunde Normaltarif</em></strong> dürfen höchstens 9,'
        '99 € betragen.')],
    blank=True,
    null=True)
  normaltarif_gebuehrenschritte = models.CharField(
    'Gebührenschritte Normaltarif', max_length=255, blank=True, null=True)
  veranstaltungstarif_parkdauer_min = fields.PositiveSmallIntegerMinField(
    'Mindestparkdauer Veranstaltungstarif', min_value=1, blank=True, null=True)
  veranstaltungstarif_parkdauer_min_einheit = models.ForeignKey(
    models_codelist.Zeiteinheiten,
    verbose_name='Einheit der Mindestparkdauer Veranstaltungstarif',
    on_delete=models.SET_NULL,
    db_column='veranstaltungstarif_parkdauer_min_einheit',
    to_field='uuid',
    related_name='veranstaltungstarif_parkdauer_min_einheiten+',
    blank=True,
    null=True)
  veranstaltungstarif_parkdauer_max = fields.PositiveSmallIntegerMinField(
    'Maximalparkdauer Veranstaltungstarif', min_value=1, blank=True, null=True)
  veranstaltungstarif_parkdauer_max_einheit = models.ForeignKey(
    models_codelist.Zeiteinheiten,
    verbose_name='Einheit der Maximalparkdauer Veranstaltungstarif',
    on_delete=models.SET_NULL,
    db_column='veranstaltungstarif_parkdauer_max_einheit',
    to_field='uuid',
    related_name='veranstaltungstarif_parkdauer_max_einheiten+',
    blank=True,
    null=True)
  veranstaltungstarif_gebuehren_max = models.DecimalField(
    'Maximalgebühren Veranstaltungstarif (in €)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Maximalgebühren Veranstaltungstarif</strong></em> müssen mindestens 0,'
        '01 € betragen.'),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Maximalgebühren Veranstaltungstarif</em></strong> dürfen höchstens 99,'
        '99 € betragen.')],
    blank=True,
    null=True)
  veranstaltungstarif_gebuehren_pro_stunde = models.DecimalField(
    'Gebühren pro Stunde Veranstaltungstarif (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro Stunde Veranstaltungstarif</strong></em> müssen '
        'mindestens 0,01 € betragen.'),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro Stunde Veranstaltungstarif</em></strong> dürfen höchstens'
        '9,99 € betragen.')],
    blank=True,
    null=True)
  veranstaltungstarif_gebuehrenschritte = models.CharField(
    'Gebührenschritte Veranstaltungstarif', max_length=255, blank=True, null=True)
  zugelassene_muenzen = models.CharField(
    ' zugelassene Münzen', max_length=255)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"parkscheinautomaten_tarife_hro'
    verbose_name = 'Tarif der Parkscheinautomaten'
    verbose_name_plural = 'Tarife der Parkscheinautomaten'
    description = 'Tarife der Parkscheinautomaten der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'zeiten': 'Bewirtschaftungszeiten'
    }
    associated_models = {
      'Parkscheinautomaten_Parkscheinautomaten': 'parkscheinautomaten_tarif'}
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']
    as_overlay = False

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Parkscheinautomaten_Tarife, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Parkscheinautomaten_Tarife, self).delete(*args, **kwargs)


# Parkscheinautomaten

class Parkscheinautomaten_Parkscheinautomaten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  parkscheinautomaten_tarif = models.ForeignKey(
    Parkscheinautomaten_Tarife,
    verbose_name='Tarif',
    on_delete=models.CASCADE,
    db_column='parkscheinautomaten_tarif',
    to_field='uuid',
    related_name='parkscheinautomaten_tarife+')
  nummer = models.PositiveSmallIntegerField('Nummer')
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  zone = models.ForeignKey(
    models_codelist.Zonen_Parkscheinautomaten,
    verbose_name='Zone',
    on_delete=models.RESTRICT,
    db_column='zone',
    to_field='uuid',
    related_name='zonen+')
  handyparkzone = fields.PositiveIntegerRangeField(
    'Handyparkzone', min_value=100000, max_value=999999)
  bewohnerparkgebiet = models.CharField(
    'Bewohnerparkgebiet',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.psa_bewohnerparkgebiet_regex,
        message=constants_vars.psa_bewohnerparkgebiet_message
      )
    ]
  )
  geraetenummer = models.CharField(
    'Gerätenummer',
    max_length=8,
    validators=[
      RegexValidator(
        regex=constants_vars.psa_geraetenummer_regex,
        message=constants_vars.psa_geraetenummer_message
      )
    ]
  )
  inbetriebnahme = models.DateField('Inbetriebnahme', blank=True, null=True)
  e_anschluss = models.ForeignKey(
    models_codelist.E_Anschluesse_Parkscheinautomaten,
    verbose_name='E-Anschluss',
    on_delete=models.RESTRICT,
    db_column='e_anschluss',
    to_field='uuid',
    related_name='e_anschluesse+')
  stellplaetze_pkw = fields.PositiveSmallIntegerMinField(
    'Pkw-Stellplätze', min_value=1, blank=True, null=True)
  stellplaetze_bus = fields.PositiveSmallIntegerMinField(
    'Bus-Stellplätze', min_value=1, blank=True, null=True)
  haendlerkartennummer = fields.PositiveIntegerRangeField(
    'Händlerkartennummer',
    min_value=1000000000,
    max_value=9999999999,
    blank=True,
    null=True)
  laufzeit_geldkarte = models.DateField(
    'Laufzeit der Geldkarte', blank=True, null=True)
  geometrie = models.PointField(
    'Geometrie', srid=25833, default='POINT(0 0)')

  class Meta:
    managed = False
    complex = True
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
      'parkscheinautomaten_tarif': 'bezeichnung',
      'zone': 'zone'
    }
    fields_with_foreign_key_to_linkify = ['parkscheinautomaten_tarif']
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'parkscheinautomaten_tarif': 'Tarif',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'zone': 'Zone'
    }
    map_filter_fields_as_list = ['parkscheinautomaten_tarif', 'zone']
    geometry_type = 'Point'
    as_overlay = True

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(
      Parkscheinautomaten_Parkscheinautomaten,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Parkscheinautomaten_Parkscheinautomaten,
      self).delete(
      *args,
      **kwargs)


#
# RSAG
#

# Gleise

class RSAG_Gleise(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  quelle = models.CharField(
    'Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  geometrie = models.LineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"rsag_gleise_hro'
    verbose_name = 'RSAG-Gleis'
    verbose_name_plural = 'RSAG-Gleise'
    description = 'Gleise innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'uuid': 'UUID',
      'aktiv': 'aktiv?',
      'quelle': 'Quelle'
    }
    map_feature_tooltip_field = 'uuid'
    map_filter_fields = {
      'uuid': 'UUID',
      'quelle': 'Quelle'
    }
    geometry_type = 'LineString'
    as_overlay = True
    heavy_load_limit = 800

  def __str__(self):
    return self.uuid

  def save(self, *args, **kwargs):
    super(RSAG_Gleise, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(RSAG_Gleise, self).delete(*args, **kwargs)


# Masten

class RSAG_Masten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  mastnummer = models.CharField(
    'Mastnummer',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  moment_am_fundament = fields.PositiveSmallIntegerRangeField(
    'Moment am Fundament (in kNm)',
    min_value=1,
    blank=True,
    null=True)
  spitzenzug_errechnet = models.DecimalField(
    'Spitzenzug P - Errechnet (in kN)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Spitzenzug P</em></strong> muss mindestens 0,01 kN betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Der <strong><em>Spitzenzug P</em></strong> darf höchstens 999,99 kN betragen.')],
    blank=True,
    null=True)
  spitzenzug_gewaehlt = models.DecimalField(
    'Spitzenzug P - Gewählt (in kN)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Spitzenzug P</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Der <strong><em>Spitzenzug P</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  gesamtlaenge = models.DecimalField(
    'Gesamtlänge L (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gesamtlänge L</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Gesamtlänge L</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  einsatztiefe = models.DecimalField(
    'Einsatztiefe T (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Einsatztiefe T</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Einsatztiefe T</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  so_bis_fundament = models.DecimalField(
    'Schienenoberkante bis Fundament e (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('-1.00'),
        'Die <strong><em>Höhendifferenz zwischen Schienenoberkante und Fundament '
        'e</em></strong> muss mindestens -1,00 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Höhendifferenz zwischen Schienenoberkante und Fundament '
        'e</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  boeschung = models.DecimalField(
    'Böschungshöhe z (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Böschungshöhe z</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Böschungshöhe z</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  freie_laenge = models.DecimalField(
    'Freie Länge H (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>freie Länge H</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>freie Länge H</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  masttyp = models.ForeignKey(
    models_codelist.Masttypen_RSAG,
    verbose_name='Masttyp',
    on_delete=models.RESTRICT,
    db_column='masttyp',
    to_field='uuid',
    related_name='masttypen+')
  nennmass_ueber_so = fields.PositiveSmallIntegerRangeField(
    'Nennmaß über Schienenoberkante (in mm)',
    min_value=1,
    blank=True,
    null=True)
  mastgewicht = fields.PositiveSmallIntegerRangeField(
    'Mastgewicht (in kg)',
    min_value=1,
    blank=True,
    null=True)
  fundamenttyp = models.ForeignKey(
    models_codelist.Fundamenttypen_RSAG,
    verbose_name='Fundamenttyp',
    on_delete=models.SET_NULL,
    db_column='fundamenttyp',
    to_field='uuid',
    related_name='fundamenttypen+',
    blank=True,
    null=True)
  fundamentlaenge = models.DecimalField(
    'Länge des Fundamentes t (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Länge des Fundaments t</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Länge des Fundaments t</em></strong> darf höchstens 999,99 m betragen.')],
    blank=True,
    null=True)
  fundamentdurchmesser = models.CharField(
    'Durchmesser des Fundaments',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  nicht_tragfaehiger_boden = models.DecimalField(
    'Tiefe des nicht tragfähiger Boden (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.00'),
        'Die <strong><em>Tiefe des nicht tragfähigen Bodens</em></strong> muss mindestens 0,'
        '00 m betragen.'),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Tiefe des nicht tragfähigen Bodens</em></strong> darf höchstens 999,'
        '99 m betragen.')],
    blank=True,
    null=True)
  mastkennzeichen_1 = models.ForeignKey(
    models_codelist.Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 1',
    on_delete=models.SET_NULL,
    db_column='mastkennzeichen_1',
    to_field='uuid',
    related_name='mastkennzeichen_1+',
    blank=True,
    null=True)
  mastkennzeichen_2 = models.ForeignKey(
    models_codelist.Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 2',
    on_delete=models.SET_NULL,
    db_column='mastkennzeichen_2',
    to_field='uuid',
    related_name='mastkennzeichen_2+',
    blank=True,
    null=True)
  mastkennzeichen_3 = models.ForeignKey(
    models_codelist.Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 3',
    on_delete=models.SET_NULL,
    db_column='mastkennzeichen_3',
    to_field='uuid',
    related_name='mastkennzeichen_3+',
    blank=True,
    null=True)
  mastkennzeichen_4 = models.ForeignKey(
    models_codelist.Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 4',
    on_delete=models.SET_NULL,
    db_column='mastkennzeichen_4',
    to_field='uuid',
    related_name='mastkennzeichen_4+',
    blank=True,
    null=True)
  quelle = models.CharField(
    'Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  dgm_hoehe = models.DecimalField(
    'Höhenwert des Durchstoßpunktes auf dem DGM (in m)',
    max_digits=5,
    decimal_places=2,
    blank=True,
    null=True,
    editable=False
  )
  geometrie = models.PointField('Geometrie', srid=25833)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"rsag_masten_hro'
    verbose_name = 'RSAG-Mast'
    verbose_name_plural = 'RSAG-Masten'
    description = 'Masten innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'mastnummer': 'Mastnummer',
      'gesamtlaenge': 'Gesamtlänge L',
      'masttyp': 'Masttyp',
      'fundamenttyp': 'Fundamenttyp',
      'mastkennzeichen_1': 'Mastkennzeichen 1',
      'mastkennzeichen_2': 'Mastkennzeichen 2',
      'mastkennzeichen_3': 'Mastkennzeichen 3',
      'mastkennzeichen_4': 'Mastkennzeichen 4',
      'quelle': 'Quelle'
    }
    list_fields_with_number = [
      'gesamtlaenge'
    ]
    list_fields_with_foreign_key = {
      'masttyp': 'typ',
      'fundamenttyp': 'typ',
      'mastkennzeichen_1': 'kennzeichen',
      'mastkennzeichen_2': 'kennzeichen',
      'mastkennzeichen_3': 'kennzeichen',
      'mastkennzeichen_4': 'kennzeichen'
    }
    map_feature_tooltip_field = 'mastnummer'
    map_filter_fields = {
      'uuid': 'UUID',
      'mastnummer': 'Mastnummer',
      'masttyp': 'Masttyp',
      'fundamenttyp': 'Fundamenttyp',
      'mastkennzeichen_1': 'Mastkennzeichen 1',
      'mastkennzeichen_2': 'Mastkennzeichen 2',
      'mastkennzeichen_3': 'Mastkennzeichen 3',
      'mastkennzeichen_4': 'Mastkennzeichen 4',
      'quelle': 'Quelle'
    }
    map_filter_fields_as_list = [
      'masttyp',
      'fundamenttyp',
      'mastkennzeichen_1',
      'mastkennzeichen_2',
      'mastkennzeichen_3',
      'mastkennzeichen_4'
    ]
    associated_models = {
      'RSAG_Quertraeger': 'mast',
      'RSAG_Spanndraehte': 'mast'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['mastnummer']
    geometry_type = 'Point'
    as_overlay = True

  def __str__(self):
    return self.mastnummer

  def save(self, *args, **kwargs):
    super(RSAG_Masten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(RSAG_Masten, self).delete(*args, **kwargs)


# Oberleitungen

class RSAG_Leitungen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  geometrie = models.LineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"rsag_leitungen_hro'
    verbose_name = 'RSAG-Oberleitung'
    verbose_name_plural = 'RSAG-Oberleitungen'
    description = 'Oberleitungen innerhalb der Straßenbahninfrastruktur der Rostocker ' \
                  'Straßenbahn AG in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'uuid': 'UUID',
      'aktiv': 'aktiv?'
    }
    map_feature_tooltip_field = 'uuid'
    map_filter_fields = {
      'uuid': 'UUID'
    }
    geometry_type = 'LineString'
    as_overlay = True

  def __str__(self):
    return self.uuid

  def save(self, *args, **kwargs):
    super(RSAG_Leitungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(RSAG_Leitungen, self).delete(*args, **kwargs)


# Querträger

class RSAG_Quertraeger(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  mast = models.ForeignKey(
    RSAG_Masten,
    verbose_name='Mast',
    on_delete=models.RESTRICT,
    db_column='mast',
    to_field='uuid',
    related_name='mast+')
  quelle = models.CharField(
    'Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  geometrie = models.LineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"rsag_quertraeger_hro'
    verbose_name = 'RSAG-Querträger'
    verbose_name_plural = 'RSAG-Querträger'
    description = 'Querträger innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn ' \
                  'AG in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'uuid': 'UUID',
      'aktiv': 'aktiv?',
      'mast': 'Mast',
      'quelle': 'Quelle'
    }
    list_fields_with_foreign_key = {
      'mast': 'mastnummer'
    }
    fields_with_foreign_key_to_linkify = ['mast']
    map_feature_tooltip_field = 'uuid'
    map_filter_fields = {
      'uuid': 'UUID',
      'mast': 'Mast',
      'quelle': 'Quelle'
    }
    map_filter_fields_as_list = [
      'mast'
    ]
    geometry_type = 'LineString'
    as_overlay = True

  def __str__(self):
    return str(self.uuid)

  def save(self, *args, **kwargs):
    super(RSAG_Quertraeger, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(RSAG_Quertraeger, self).delete(*args, **kwargs)


# Spanndrähte

class RSAG_Spanndraehte(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  mast = models.ForeignKey(
    RSAG_Masten,
    verbose_name='Mast',
    on_delete=models.SET_NULL,
    db_column='mast',
    to_field='uuid',
    related_name='mast+',
    blank=True,
    null=True)
  quelle = models.CharField(
    'Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  geometrie = models.LineStringField('Geometrie', srid=25833)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"rsag_spanndraehte_hro'
    verbose_name = 'RSAG-Spanndraht'
    verbose_name_plural = 'RSAG-Spanndrähte'
    description = 'Spanndrähte innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn' \
                  ' AG in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'uuid': 'UUID',
      'aktiv': 'aktiv?',
      'mast': 'Mast',
      'quelle': 'Quelle'
    }
    list_fields_with_foreign_key = {
      'mast': 'mastnummer'
    }
    fields_with_foreign_key_to_linkify = ['mast']
    map_feature_tooltip_field = 'uuid'
    map_filter_fields = {
      'uuid': 'UUID',
      'mast': 'Mast',
      'quelle': 'Quelle'
    }
    map_filter_fields_as_list = [
      'mast'
    ]
    geometry_type = 'LineString'
    as_overlay = True

  def __str__(self):
    return str(self.uuid)

  def save(self, *args, **kwargs):
    super(RSAG_Spanndraehte, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(RSAG_Spanndraehte, self).delete(*args, **kwargs)


#
# UVP
#

# Vorhaben

class UVP_Vorhaben(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  bezeichnung = models.CharField(
    'Bezeichnung',
    max_length=255,
    validators=constants_vars.standard_validators
  )
  vorgangsart = models.ForeignKey(
    models_codelist.Vorgangsarten_UVP_Vorhaben,
    verbose_name='Vorgangsart',
    on_delete=models.RESTRICT,
    db_column='vorgangsart',
    to_field='uuid',
    related_name='vorgangsarten+')
  genehmigungsbehoerde = models.ForeignKey(
    models_codelist.Genehmigungsbehoerden_UVP_Vorhaben,
    verbose_name='Genehmigungsbehörde',
    on_delete=models.RESTRICT,
    db_column='genehmigungsbehoerde',
    to_field='uuid',
    related_name='genehmigungsbehoerden+')
  datum_posteingang_genehmigungsbehoerde = models.DateField(
    'Datum des Posteingangs bei der Genehmigungsbehörde')
  registriernummer_bauamt = models.CharField(
    'Registriernummer des Bauamtes',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=constants_vars.uvp_vh_registriernummer_bauamt_regex,
        message=constants_vars.uvp_vh_registriernummer_bauamt_message
      )
    ]
  )
  aktenzeichen = models.CharField(
    'Aktenzeichen',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )
  rechtsgrundlage = models.ForeignKey(
    models_codelist.Rechtsgrundlagen_UVP_Vorhaben,
    verbose_name='Rechtsgrundlage',
    on_delete=models.RESTRICT,
    db_column='rechtsgrundlage',
    to_field='uuid',
    related_name='rechtsgrundlagen+')
  typ = models.ForeignKey(
    models_codelist.Typen_UVP_Vorhaben,
    verbose_name='Typ',
    on_delete=models.RESTRICT,
    db_column='typ',
    to_field='uuid',
    related_name='typen+')
  geometrie = models.PolygonField('Geometrie', srid=25833)

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"uvp_vorhaben_hro'
    verbose_name = 'UVP-Vorhaben'
    verbose_name_plural = 'UVP-Vorhaben'
    description = 'Vorhaben, auf die sich Vorprüfungen der Hanse- und Universitätsstadt Rostock' \
                  ' zur Feststellung der UVP-Pflicht gemäß UVPG und LUVPG M-V beziehen'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'vorgangsart': 'Vorgangsart',
      'genehmigungsbehoerde': 'Genehmigungsbehörde',
      'datum_posteingang_genehmigungsbehoerde': 'Datum des Posteingangs bei der '
                                                'Genehmigungsbehörde',
      'rechtsgrundlage': 'Rechtsgrundlage',
      'typ': 'Typ'}
    list_fields_with_foreign_key = {
      'vorgangsart': 'vorgangsart',
      'genehmigungsbehoerde': 'genehmigungsbehoerde',
      'rechtsgrundlage': 'rechtsgrundlage',
      'typ': 'typ'
    }
    list_fields_with_date = ['datum_posteingang_genehmigungsbehoerde']
    associated_models = {
      'UVP_Vorpruefungen': 'uvp_vorhaben'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'vorgangsart': 'Vorgangsart',
      'genehmigungsbehoerde': 'Genehmigungsbehörde',
      'datum_posteingang_genehmigungsbehoerde': 'Datum des Posteingangs bei der '
                                                'Genehmigungsbehörde',
      'rechtsgrundlage': 'Rechtsgrundlage',
      'typ': 'Typ'}
    map_filter_fields_as_list = [
      'vorgangsart',
      'genehmigungsbehoerde',
      'rechtsgrundlage',
      'typ']
    geometry_type = 'Polygon'
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']
    as_overlay = True

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(UVP_Vorhaben, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(UVP_Vorhaben, self).delete(*args, **kwargs)


# Vorprüfungen

class UVP_Vorpruefungen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  aktiv = models.BooleanField(' aktiv?', default=True)
  uvp_vorhaben = models.ForeignKey(
    UVP_Vorhaben,
    verbose_name='Vorhaben',
    on_delete=models.CASCADE,
    db_column='uvp_vorhaben',
    to_field='uuid',
    related_name='uvp_vorhaben+')
  art = models.ForeignKey(
    models_codelist.Arten_UVP_Vorpruefungen,
    verbose_name='Art',
    on_delete=models.RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='arten+')
  datum_posteingang = models.DateField('Datum des Posteingangs')
  datum = models.DateField('Datum', default=date.today)
  ergebnis = models.ForeignKey(
    models_codelist.Ergebnisse_UVP_Vorpruefungen,
    verbose_name='Ergebnis',
    on_delete=models.RESTRICT,
    db_column='ergebnis',
    to_field='uuid',
    related_name='ergebnisse+')
  datum_bekanntmachung = models.DateField(
    'Datum Bekanntmachung „Städtischer Anzeiger“', blank=True, null=True)
  datum_veroeffentlichung = models.DateField(
    'Datum Veröffentlichung UVP-Portal', blank=True, null=True)
  pruefprotokoll = models.CharField(
    'Prüfprotokoll',
    max_length=255,
    blank=True,
    null=True,
    validators=constants_vars.standard_validators
  )

  class Meta:
    managed = False
    complex = True
    db_table = 'fachdaten\".\"uvp_vorpruefungen_hro'
    verbose_name = 'UVP-Vorprüfung'
    verbose_name_plural = 'UVP-Vorprüfungen'
    description = 'Vorprüfungen der Hanse- und Universitätsstadt Rostock zur Feststellung der ' \
                  'UVP-Pflicht gemäß UVPG und LUVPG M-V'
    list_fields = {
      'aktiv': 'aktiv?',
      'uvp_vorhaben': 'Vorhaben',
      'art': 'Art',
      'datum_posteingang': 'Datum des Posteingangs',
      'datum': 'Datum',
      'ergebnis': 'Ergebnis'
    }
    list_fields_with_date = ['datum_posteingang', 'datum']
    list_fields_with_foreign_key = {
      'uvp_vorhaben': 'bezeichnung',
      'art': 'art',
      'ergebnis': 'ergebnis'
    }
    fields_with_foreign_key_to_linkify = ['uvp_vorhaben']
    object_title = 'die UVP-Vorprüfung'
    foreign_key_label = 'Vorhaben'

  def __str__(self):
    return str(self.uvp_vorhaben) + ' mit Datum ' + datetime.strptime(
      str(self.datum),
      '%Y-%m-%d'
    ).strftime('%d.%m.%Y') + ' [Art: ' + str(self.art) + ']'

  def save(self, *args, **kwargs):
    super(UVP_Vorpruefungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(UVP_Vorpruefungen, self).delete(*args, **kwargs)
