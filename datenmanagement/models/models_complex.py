from datetime import date, datetime, timezone
from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator, \
  RegexValidator, URLValidator
from django.db.models import CASCADE, RESTRICT, SET_NULL, ForeignKey
from django.db.models.fields import BooleanField, CharField, DateField, DateTimeField, \
  DecimalField, PositiveIntegerField, PositiveSmallIntegerField
from django.db.models.fields.files import FileField, ImageField
from django.db.models.signals import post_delete, post_save
from re import sub
from zoneinfo import ZoneInfo

from .base import ComplexModel
from .constants_vars import ansprechpartner_validators, standard_validators, url_message, \
  durchlaesse_aktenzeichen_regex, durchlaesse_aktenzeichen_message, \
  haltestellenkataster_hafas_id_regex, haltestellenkataster_hafas_id_message, \
  parkscheinautomaten_bewohnerparkgebiet_regex, parkscheinautomaten_bewohnerparkgebiet_message, \
  parkscheinautomaten_geraetenummer_regex, parkscheinautomaten_geraetenummer_message, \
  uvp_registriernummer_bauamt_regex, uvp_registriernummer_bauamt_message
from .fields import bearbeiter_field, bemerkungen_field, bezeichnung_field, \
  ChoiceArrayField, NullTextField, PositiveIntegerMinField, PositiveIntegerRangeField, \
  PositiveSmallIntegerMinField, PositiveSmallIntegerRangeField, punkt_field, linie_field, \
  multilinie_field, flaeche_field, multiflaeche_field
from .functions import current_year, delete_pdf, delete_photo, path_and_rename, \
  photo_post_processing, sequence_id
from .models_codelist import Strassen, Arten_Durchlaesse, Arten_Fallwildsuchen_Kontrollen, \
  Arten_UVP_Vorpruefungen, Auftraggeber_Baustellen, Ausfuehrungen_Haltestellenkataster, \
  Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster, \
  Befestigungsarten_Warteflaeche_Haltestellenkataster, E_Anschluesse_Parkscheinautomaten, \
  Ergebnisse_UVP_Vorpruefungen, Fotomotive_Haltestellenkataster, Fundamenttypen_RSAG, \
  Genehmigungsbehoerden_UVP_Vorhaben, Mastkennzeichen_RSAG, Masttypen_RSAG, \
  Masttypen_Haltestellenkataster, Materialien_Durchlaesse, Rechtsgrundlagen_UVP_Vorhaben, \
  Schaeden_Haltestellenkataster, Sitzbanktypen_Haltestellenkataster, Status_Baustellen_geplant, \
  Status_Baustellen_Fotodokumentation_Fotos, Tierseuchen, DFI_Typen_Haltestellenkataster, \
  Fahrgastunterstandstypen_Haltestellenkataster, Fahrplanvitrinentypen_Haltestellenkataster, \
  Typen_Haltestellen, Typen_UVP_Vorhaben, Vorgangsarten_UVP_Vorhaben, Zeiteinheiten, \
  ZH_Typen_Haltestellenkataster, Zonen_Parkscheinautomaten, Zustandsbewertungen
from .storage import OverwriteStorage


#
# Baustellen-Fotodokumentation
#

class Baustellen_Fotodokumentation_Baustellen(ComplexModel):
  """
  Baustellen-Fotodokumentation:
  Baustellen
  """

  strasse = ForeignKey(
    Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True
  )
  bezeichnung = bezeichnung_field
  verkehrliche_lagen = ChoiceArrayField(
    CharField(
      ' verkehrliche Lage(n)',
      max_length=255,
      choices=()
    ),
    verbose_name=' verkehrliche Lage(n)'
  )
  sparten = ChoiceArrayField(
    CharField(
      'Sparte(n)',
      max_length=255,
      choices=()
    ),
    verbose_name='Sparte(n)'
  )
  auftraggeber = ForeignKey(
    Auftraggeber_Baustellen,
    verbose_name='Auftraggeber',
    on_delete=RESTRICT,
    db_column='auftraggeber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_auftraggeber'
  )
  ansprechpartner = CharField(
    'Ansprechpartner:in',
    max_length=255,
    validators=ansprechpartner_validators
  )
  bemerkungen = bemerkungen_field
  geometrie = punkt_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten_strassenbezug\".\"baustellen_fotodokumentation_baustellen_hro'
    verbose_name = 'Baustelle der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Baustellen der Baustellen-Fotodokumentation'
    description = 'Baustellen der Baustellen-Fotodokumentation ' \
                  'in der Hanse- und Universitätsstadt Rostock'
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
      'ansprechpartner': 'Ansprechpartner:in',
      'bemerkungen': 'Bemerkungen'
    }
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'auftraggeber': 'auftraggeber'
    }
    associated_models = {
      'Baustellen_Fotodokumentation_Fotos': 'baustellen_fotodokumentation_baustelle'
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
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung + (' [Straße: ' + str(self.strasse) + ']' if self.strasse else '')


class Baustellen_Fotodokumentation_Fotos(ComplexModel):
  """
  Baustellen-Fotodokumentation:
  Fotos
  """

  baustellen_fotodokumentation_baustelle = ForeignKey(
    Baustellen_Fotodokumentation_Baustellen,
    verbose_name='Baustelle',
    on_delete=CASCADE,
    db_column='baustellen_fotodokumentation_baustelle',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_baustellen_fotodokumentation_baustellen'
  )
  status = ForeignKey(
    Status_Baustellen_Fotodokumentation_Fotos,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
  aufnahmedatum = DateField(
    'Aufnahmedatum',
    default=date.today
  )
  dateiname_original = CharField(
    'Original-Dateiname',
    max_length=255,
    default='ohne'
  )
  foto = ImageField(
    'Foto(s)',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE + 'baustellen_fotodokumentation'
    ),
    max_length=255
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"baustellen_fotodokumentation_fotos_hro'
    verbose_name = 'Foto der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Fotos der Baustellen-Fotodokumentation'
    description = 'Fotos der Baustellen-Fotodokumentation ' \
                  'in der Hanse- und Universitätsstadt Rostock'
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
    fields_with_foreign_key_to_linkify = ['baustellen_fotodokumentation_baustelle']
    object_title = 'das Foto'
    foreign_key_label = 'Baustelle'
    thumbs = True
    multi_foto_field = True

  def __str__(self):
    return str(self.baustellen_fotodokumentation_baustelle) + \
      ' mit Status ' + str(self.status) + ' und Aufnahmedatum ' + \
      datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')


post_save.connect(photo_post_processing, sender=Baustellen_Fotodokumentation_Fotos)

post_delete.connect(delete_photo, sender=Baustellen_Fotodokumentation_Fotos)


#
# Baustellen (geplant)
#

class Baustellen_geplant(ComplexModel):
  """
  Baustellen (geplant):
  Baustellen
  """

  strasse = ForeignKey(
    Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True
  )
  projektbezeichnung = CharField(
    'Projektbezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  bezeichnung = bezeichnung_field
  kurzbeschreibung = NullTextField(
    'Kurzbeschreibung',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators
  )
  lagebeschreibung = CharField(
    'Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  verkehrliche_lagen = ChoiceArrayField(
    CharField(
      ' verkehrliche Lage(n)',
      max_length=255,
      choices=()
    ),
    verbose_name=' verkehrliche Lage(n)'
  )
  sparten = ChoiceArrayField(
    CharField(
      'Sparte(n)',
      max_length=255,
      choices=()
    ),
    verbose_name='Sparte(n)'
  )
  beginn = DateField('Beginn')
  ende = DateField('Ende')
  auftraggeber = ForeignKey(
    Auftraggeber_Baustellen,
    verbose_name='Auftraggeber',
    on_delete=RESTRICT,
    db_column='auftraggeber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_auftraggeber'
  )
  ansprechpartner = CharField(
    'Ansprechpartner:in',
    max_length=255,
    validators=ansprechpartner_validators
  )
  status = ForeignKey(
    Status_Baustellen_geplant,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
  konflikt = BooleanField(
    'Konflikt?',
    blank=True,
    null=True,
    editable=False
  )
  konflikt_tolerieren = BooleanField(
    ' räumliche(n)/zeitliche(n) Konflikt(e) mit anderem/anderen Vorhaben tolerieren?',
    blank=True,
    null=True
  )
  geometrie = multiflaeche_field

  class Meta(ComplexModel.Meta):
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
      'ansprechpartner': 'Ansprechpartner:in',
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
    map_one_click_filters = True
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
    ordering = ['bezeichnung']
    as_overlay = True

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Straße: ' + str(self.strasse) + ', ' if self.strasse else '') + 'Beginn: ' + \
      datetime.strptime(str(self.beginn), '%Y-%m-%d').strftime('%d.%m.%Y') + ', Ende: ' + \
      datetime.strptime(str(self.ende), '%Y-%m-%d').strftime('%d.%m.%Y') + ']'


class Baustellen_geplant_Dokumente(ComplexModel):
  """
  Baustellen (geplant):
  Dokumente
  """

  baustelle_geplant = ForeignKey(
    Baustellen_geplant,
    verbose_name='Baustelle (geplant)',
    on_delete=CASCADE,
    db_column='baustelle_geplant',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_baustellen_geplant'
  )
  bezeichnung = bezeichnung_field
  dokument = FileField(
    'Dokument',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PDF_PATH_PREFIX_PUBLIC + 'baustellen_geplant'
    ),
    max_length=255
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"baustellen_geplant_dokumente'
    verbose_name = 'Dokument der Baustelle (geplant)'
    verbose_name_plural = 'Dokumente der Baustellen (geplant)'
    description = 'Dokumente der Baustellen (geplant) ' \
                  'in der Hanse- und Universitätsstadt Rostock und Umgebung'
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
    return str(self.baustelle_geplant) + ' mit Bezeichnung ' + self.bezeichnung


post_delete.connect(delete_pdf, sender=Baustellen_geplant_Dokumente)


class Baustellen_geplant_Links(ComplexModel):
  """
  Baustellen (geplant):
  Links
  """

  baustelle_geplant = ForeignKey(
    Baustellen_geplant,
    verbose_name='Baustelle (geplant)',
    on_delete=CASCADE,
    db_column='baustelle_geplant',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_baustellen_geplant'
  )
  bezeichnung = bezeichnung_field
  link = CharField(
    'Link',
    max_length=255,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"baustellen_geplant_links'
    verbose_name = 'Link der Baustelle (geplant)'
    verbose_name_plural = 'Links der Baustellen (geplant)'
    description = 'Links der Baustellen (geplant) ' \
                  'in der Hanse- und Universitätsstadt Rostock und Umgebung'
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
    return str(self.baustelle_geplant) + ' mit Bezeichnung ' + self.bezeichnung


#
# Durchlässe
#

class Durchlaesse_Durchlaesse(ComplexModel):
  """
  Durchlässe:
  Durchlässe
  """

  art = ForeignKey(
    Arten_Durchlaesse,
    verbose_name='Art',
    on_delete=SET_NULL,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
    blank=True,
    null=True
  )
  aktenzeichen = CharField(
    'Aktenzeichen',
    max_length=255,
    unique=True,
    validators=[
      RegexValidator(
        regex=durchlaesse_aktenzeichen_regex,
        message=durchlaesse_aktenzeichen_message
      )
    ]
  )
  material = ForeignKey(
    Materialien_Durchlaesse,
    verbose_name='Material',
    on_delete=SET_NULL,
    db_column='material',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_materialien',
    blank=True,
    null=True
  )
  baujahr = PositiveSmallIntegerRangeField(
    'Baujahr',
    max_value=current_year(),
    blank=True,
    null=True
  )
  nennweite = PositiveSmallIntegerMinField(
    'Nennweite (in mm)',
    min_value=100,
    blank=True,
    null=True
  )
  laenge = DecimalField(
    'Länge (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Länge</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Länge</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  nebenanlagen = NullTextField(
    'Nebenanlagen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  zubehoer = NullTextField(
    'Zubehör',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  zustand_durchlass = ForeignKey(
    Zustandsbewertungen,
    verbose_name='Zustand des Durchlasses',
    on_delete=SET_NULL,
    db_column='zustand_durchlass',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende_durchlass',
    blank=True,
    null=True
  )
  zustand_nebenanlagen = ForeignKey(
    Zustandsbewertungen,
    verbose_name='Zustand der Nebenanlagen',
    on_delete=SET_NULL,
    db_column='zustand_nebenanlagen',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende_nebenanlagen',
    blank=True,
    null=True
  )
  zustand_zubehoer = ForeignKey(
    Zustandsbewertungen,
    verbose_name='Zustand des Zubehörs',
    on_delete=SET_NULL,
    db_column='zustand_zubehoer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende_zubehoer',
    blank=True,
    null=True
  )
  kontrolle = DateField(
    'Kontrolle',
    blank=True,
    null=True
  )
  bemerkungen = NullTextField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  zustaendigkeit = CharField(
    'Zuständigkeit',
    max_length=255,
    validators=standard_validators
  )
  bearbeiter = bearbeiter_field
  geometrie = punkt_field

  class Meta(ComplexModel.Meta):
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
      'bearbeiter': 'Bearbeiter:in'
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
      'baujahr': 'Baujahr',
      'nennweite': 'Nennweite (in mm)',
      'laenge': 'Länge (in m)',
      'zustaendigkeit': 'Zuständigkeit',
      'bearbeiter': 'Bearbeiter:in'
    }
    map_filter_fields_as_list = ['art', 'material']
    geometry_type = 'Point'
    ordering = ['aktenzeichen']
    as_overlay = True

  def __str__(self):
    return self.aktenzeichen


class Durchlaesse_Fotos(ComplexModel):
  """
  Durchlässe:
  Fotos
  """

  durchlaesse_durchlass = ForeignKey(
    Durchlaesse_Durchlaesse,
    verbose_name='Durchlass',
    on_delete=CASCADE,
    db_column='durchlaesse_durchlass',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_durchlaesse_durchlaesse'
  )
  aufnahmedatum = DateField(
    'Aufnahmedatum',
    default=date.today,
    blank=True,
    null=True
  )
  bemerkungen = NullTextField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  dateiname_original = CharField(
    'Original-Dateiname',
    max_length=255,
    default='ohne'
  )
  foto = ImageField(
    'Foto(s)',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC + 'durchlaesse'
    ),
    max_length=255
  )

  class Meta(ComplexModel.Meta):
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
    return str(self.durchlaesse_durchlass) + \
      (' mit Aufnahmedatum ' +
       datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')
       if self.aufnahmedatum else '')


post_save.connect(photo_post_processing, sender=Durchlaesse_Fotos)

post_delete.connect(delete_photo, sender=Durchlaesse_Fotos)


#
# Fallwildsuchen
#

class Fallwildsuchen_Kontrollgebiete(ComplexModel):
  """
  Fallwildsuchen:
  Kontrollgebiete
  """

  tierseuche = ForeignKey(
    Tierseuchen,
    verbose_name='Tierseuche',
    on_delete=RESTRICT,
    db_column='tierseuche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tierseuchen'
  )
  bezeichnung = bezeichnung_field
  geometrie = flaeche_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"fallwildsuchen_kontrollgebiete_hro'
    verbose_name = 'Kontrollgebiet im Rahmen einer Fallwildsuche'
    verbose_name_plural = 'Kontrollgebiete im Rahmen von Fallwildsuchen'
    description = 'Kontrollgebiete im Rahmen von Fallwildsuchen ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'tierseuche': 'Tierseuche',
      'bezeichnung': 'Bezeichnung'
    }
    list_fields_with_foreign_key = {
      'tierseuche': 'bezeichnung'
    }
    associated_models = {
      'Fallwildsuchen_Nachweise': 'kontrollgebiet'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'tierseuche': 'Tierseuche',
      'bezeichnung': 'Bezeichnung'
    }
    map_filter_fields_as_list = ['tierseuche']
    geometry_type = 'Polygon'
    ordering = ['bezeichnung']
    as_overlay = True

  def __str__(self):
    return self.bezeichnung


class Fallwildsuchen_Nachweise(ComplexModel):
  """
  Fallwildsuchen:
  Nachweise
  """

  kontrollgebiet = ForeignKey(
    Fallwildsuchen_Kontrollgebiete,
    verbose_name='Kontrollgebiet',
    on_delete=CASCADE,
    db_column='kontrollgebiet',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_kontrollgebiete'
  )
  art_kontrolle = ForeignKey(
    Arten_Fallwildsuchen_Kontrollen,
    verbose_name='Art der Kontrolle',
    on_delete=RESTRICT,
    db_column='art_kontrolle',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten_kontrolle'
  )
  startzeitpunkt = DateTimeField('Startzeitpunkt')
  endzeitpunkt = DateTimeField('Endzeitpunkt')
  geometrie = multilinie_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"fallwildsuchen_nachweise_hro'
    verbose_name = 'Nachweis im Rahmen einer Fallwildsuche'
    verbose_name_plural = 'Nachweise im Rahmen von Fallwildsuchen'
    description = 'Nachweise im Rahmen von Fallwildsuchen ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'kontrollgebiet': 'Kontrollgebiet',
      'art_kontrolle': 'Art der Kontrolle',
      'startzeitpunkt': 'Startzeitpunkt',
      'endzeitpunkt': 'Endzeitpunkt'
    }
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
      'art_kontrolle': 'Art der Kontrolle'
    }
    map_filter_fields_as_list = ['kontrollgebiet', 'art_kontrolle']
    geometry_type = 'MultiLineString'
    fields_with_foreign_key_to_linkify = ['kontrollgebiet']
    object_title = 'der Nachweis im Rahmen einer Fallwildsuche'
    foreign_key_label = 'Kontrollgebiet'
    gpx_input = True
    as_overlay = True

  def __str__(self):
    local_tz = ZoneInfo(settings.TIME_ZONE)
    startzeitpunkt_str = sub(r'([+-][0-9]{2}):', '\\1', str(self.startzeitpunkt))
    startzeitpunkt = datetime.strptime(startzeitpunkt_str, '%Y-%m-%d %H:%M:%S%z').\
      replace(tzinfo=timezone.utc).astimezone(local_tz)
    startzeitpunkt_str = startzeitpunkt.strftime('%d.%m.%Y, %H:%M:%S Uhr,')
    endzeitpunkt_str = sub(r'([+-][0-9]{2}):', '\\1', str(self.endzeitpunkt))
    endzeitpunkt = datetime.strptime(endzeitpunkt_str, '%Y-%m-%d %H:%M:%S%z').\
      replace(tzinfo=timezone.utc).astimezone(local_tz)
    endzeitpunkt_str = endzeitpunkt.strftime('%d.%m.%Y, %H:%M:%S Uhr')
    return str(self.kontrollgebiet) + ' mit Startzeitpunkt ' + startzeitpunkt_str + \
      ' und Endzeitpunkt ' + endzeitpunkt_str + ' [Art der Kontrolle: ' \
      + str(self.art_kontrolle) + ']'


#
# Haltestellenkataster
#

class Haltestellenkataster_Haltestellen(ComplexModel):
  """
  Haltestellenkataster:
  Haltestellen
  """

  deaktiviert = DateField(
    'Außerbetriebstellung',
    blank=True,
    null=True
  )
  id = PositiveIntegerField(
    'ID',
    default=sequence_id('fachdaten.haltestellenkataster_haltestellen_hro_id_seq')
  )
  hst_bezeichnung = CharField(
    'Haltestellenbezeichnung',
    max_length=255,
    validators=standard_validators
  )
  hst_hafas_id = CharField(
    'HAFAS-ID',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=haltestellenkataster_hafas_id_regex,
        message=haltestellenkataster_hafas_id_message
      )
    ]
  )
  hst_bus_bahnsteigbezeichnung = CharField(
    'Bus-/Bahnsteigbezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  hst_richtung = CharField(
    'Richtungsinformation',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  hst_kategorie = CharField(
    'Haltestellenkategorie',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  hst_linien = ChoiceArrayField(
    CharField(
      ' bedienende Linie(n)',
      max_length=4,
      choices=()
    ),
    verbose_name=' bedienende Linie(n)',
    blank=True,
    null=True
  )
  hst_rsag = BooleanField(
    ' bedient durch Rostocker Straßenbahn AG?',
    blank=True,
    null=True
  )
  hst_rebus = BooleanField(
    ' bedient durch rebus Regionalbus Rostock GmbH?',
    blank=True,
    null=True
  )
  hst_nur_ausstieg = BooleanField(
    ' nur Ausstieg?',
    blank=True,
    null=True
  )
  hst_nur_einstieg = BooleanField(
    ' nur Einstieg?',
    blank=True,
    null=True
  )
  hst_verkehrsmittelklassen = ChoiceArrayField(
    CharField(
      'Verkehrsmittelklasse(n)',
      max_length=255,
      choices=()
    ),
    verbose_name='Verkehrsmittelklasse(n)'
  )
  hst_abfahrten = PositiveSmallIntegerMinField(
    ' durchschnittliche tägliche Zahl an Abfahrten',
    min_value=1,
    blank=True,
    null=True
  )
  hst_fahrgastzahl_einstieg = PositiveSmallIntegerMinField(
    ' durchschnittliche tägliche Fahrgastzahl (Einstieg)',
    min_value=1,
    blank=True,
    null=True
  )
  hst_fahrgastzahl_ausstieg = PositiveSmallIntegerMinField(
    ' durchschnittliche tägliche Fahrgastzahl (Ausstieg)',
    min_value=1,
    blank=True,
    null=True
  )
  bau_typ = ForeignKey(
    Typen_Haltestellen,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='bau_typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_typen',
    blank=True,
    null=True
  )
  bau_wartebereich_laenge = DecimalField(
    'Länge des Wartebereichs (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Wartebereich</em></strong> muss mindestens 0,01 m lang sein.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Der <strong><em>Wartebereich</em></strong> darf höchstens 999,99 m lang sein.'
      )
    ],
    blank=True,
    null=True
  )
  bau_wartebereich_breite = DecimalField(
    'Breite des Wartebereichs (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Wartebereich</em></strong> muss mindestens 0,01 m breit sein.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Der <strong><em>Wartebereich</em></strong> darf höchstens 999,99 m breit sein.'
      )
    ],
    blank=True,
    null=True
  )
  bau_befestigungsart_aufstellflaeche_bus = ForeignKey(
    Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster,
    verbose_name='Befestigungsart der Aufstellfläche Bus',
    on_delete=SET_NULL,
    db_column='bau_befestigungsart_aufstellflaeche_bus',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_befestigungsarten_aufstellflaeche_bus',
    blank=True,
    null=True
  )
  bau_zustand_aufstellflaeche_bus = ForeignKey(
    Schaeden_Haltestellenkataster,
    verbose_name='Zustand der Aufstellfläche Bus',
    on_delete=SET_NULL,
    db_column='bau_zustand_aufstellflaeche_bus',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_zustaende_aufstellflaeche_bus',
    blank=True,
    null=True
  )
  bau_befestigungsart_warteflaeche = ForeignKey(
    Befestigungsarten_Warteflaeche_Haltestellenkataster,
    verbose_name='Befestigungsart der Wartefläche',
    on_delete=SET_NULL,
    db_column='bau_befestigungsart_warteflaeche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_befestigungsarten_warteflaeche',
    blank=True,
    null=True
  )
  bau_zustand_warteflaeche = ForeignKey(
    Schaeden_Haltestellenkataster,
    verbose_name='Zustand der Wartefläche',
    on_delete=SET_NULL,
    db_column='bau_zustand_warteflaeche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_zustaende_warteflaeche',
    blank=True,
    null=True
  )
  bf_einstieg = BooleanField(
    ' barrierefreier Einstieg vorhanden?',
    blank=True,
    null=True
  )
  bf_zu_abgaenge = BooleanField(
    ' barrierefreie Zu- und Abgänge vorhanden?',
    blank=True,
    null=True
  )
  bf_bewegungsraum = BooleanField(
    ' barrierefreier Bewegungsraum vorhanden?',
    blank=True,
    null=True
  )
  tl_auffindestreifen = BooleanField(
    'Taktiles Leitsystem: Auffindestreifen vorhanden?',
    blank=True,
    null=True
  )
  tl_auffindestreifen_ausfuehrung = ForeignKey(
    Ausfuehrungen_Haltestellenkataster,
    verbose_name='Taktiles Leitsystem: Ausführung Auffindestreifen',
    on_delete=SET_NULL,
    db_column='tl_auffindestreifen_ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tl_auffindestreifen_ausfuehrungen',
    blank=True,
    null=True
  )
  tl_auffindestreifen_breite = PositiveIntegerMinField(
    'Taktiles Leitsystem: Breite des Auffindestreifens (in cm)',
    min_value=1,
    blank=True,
    null=True
  )
  tl_einstiegsfeld = BooleanField(
    'Taktiles Leitsystem: Einstiegsfeld vorhanden?',
    blank=True,
    null=True
  )
  tl_einstiegsfeld_ausfuehrung = ForeignKey(
    Ausfuehrungen_Haltestellenkataster,
    verbose_name='Taktiles Leitsystem: Ausführung Einstiegsfeld',
    on_delete=SET_NULL,
    db_column='tl_einstiegsfeld_ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tl_einstiegsfeld_ausfuehrungen',
    blank=True,
    null=True
  )
  tl_einstiegsfeld_breite = PositiveIntegerMinField(
    'Taktiles Leitsystem: Breite des Einstiegsfelds (in cm)',
    min_value=1,
    blank=True,
    null=True
  )
  tl_leitstreifen = BooleanField(
    'Taktiles Leitsystem: Leitstreifen vorhanden?',
    blank=True,
    null=True
  )
  tl_leitstreifen_ausfuehrung = ForeignKey(
    Ausfuehrungen_Haltestellenkataster,
    verbose_name='Taktiles Leitsystem: Ausführung Leitstreifen',
    on_delete=SET_NULL,
    db_column='tl_leitstreifen_ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tl_leitstreifen_ausfuehrungen',
    blank=True,
    null=True
  )
  tl_leitstreifen_laenge = PositiveIntegerMinField(
    'Taktiles Leitsystem: Länge des Leitstreifens (in cm)',
    min_value=1,
    blank=True,
    null=True
  )
  tl_aufmerksamkeitsfeld = BooleanField(
    'Aufmerksamkeitsfeld (1. Tür) vorhanden?',
    blank=True,
    null=True
  )
  tl_bahnsteigkante_visuell = BooleanField(
    'Bahnsteigkante visuell erkennbar?',
    blank=True,
    null=True
  )
  tl_bahnsteigkante_taktil = BooleanField(
    'Bahnsteigkante taktil erkennbar?',
    blank=True,
    null=True
  )
  as_zh_typ = ForeignKey(
    ZH_Typen_Haltestellenkataster,
    verbose_name='ZH-Typ',
    on_delete=SET_NULL,
    db_column='as_zh_typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_zh_typen',
    blank=True,
    null=True
  )
  as_h_mast = BooleanField(
    'Mast vorhanden?',
    blank=True,
    null=True
  )
  as_h_masttyp = ForeignKey(
    Masttypen_Haltestellenkataster,
    verbose_name='Masttyp',
    on_delete=SET_NULL,
    db_column='as_h_masttyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_h_masttypen',
    blank=True,
    null=True
  )
  as_papierkorb = BooleanField(
    'Papierkorb vorhanden?',
    blank=True,
    null=True
  )
  as_fahrgastunterstand = BooleanField(
    'Fahrgastunterstand vorhanden?',
    blank=True,
    null=True
  )
  as_fahrgastunterstandstyp = ForeignKey(
    Fahrgastunterstandstypen_Haltestellenkataster,
    verbose_name='Typ des Fahrgastunterstand',
    on_delete=SET_NULL,
    db_column='as_fahrgastunterstandstyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_fahrgastunterstandstypen',
    blank=True,
    null=True
  )
  as_sitzbank_mit_armlehne = BooleanField(
    'Sitzbank mit Armlehne vorhanden?',
    blank=True,
    null=True
  )
  as_sitzbank_ohne_armlehne = BooleanField(
    'Sitzbank ohne Armlehne vorhanden?',
    blank=True,
    null=True
  )
  as_sitzbanktyp = ForeignKey(
    Sitzbanktypen_Haltestellenkataster,
    verbose_name='Typ der Sitzbank',
    on_delete=SET_NULL,
    db_column='as_sitzbanktyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_sitzbanktypen',
    blank=True,
    null=True
  )
  as_gelaender = BooleanField(
    'Geländer vorhanden?',
    blank=True,
    null=True
  )
  as_fahrplanvitrine = BooleanField(
    'Fahrplanvitrine vorhanden?',
    blank=True,
    null=True
  )
  as_fahrplanvitrinentyp = ForeignKey(
    Fahrplanvitrinentypen_Haltestellenkataster,
    verbose_name='Typ der Fahrplanvitrine',
    on_delete=SET_NULL,
    db_column='as_fahrplanvitrinentyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_fahrplanvitrinentypen',
    blank=True,
    null=True
  )
  as_tarifinformation = BooleanField(
    'Tarifinformation vorhanden?',
    blank=True,
    null=True
  )
  as_liniennetzplan = BooleanField(
    'Liniennetzplan vorhanden?',
    blank=True,
    null=True
  )
  as_fahrplan = BooleanField(
    'Fahrplan vorhanden?',
    blank=True,
    null=True
  )
  as_fahrausweisautomat = BooleanField(
    'Fahrausweisautomat vorhanden?',
    blank=True,
    null=True
  )
  as_lautsprecher = BooleanField(
    'Lautsprecher vorhanden?',
    blank=True,
    null=True
  )
  as_dfi = BooleanField(
    'Dynamisches Fahrgastinformationssystem vorhanden?',
    blank=True,
    null=True
  )
  as_dfi_typ = ForeignKey(
    DFI_Typen_Haltestellenkataster,
    verbose_name='Typ des Dynamischen Fahrgastinformationssystems',
    on_delete=SET_NULL,
    db_column='as_dfi_typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_dfi_typen',
    blank=True,
    null=True
  )
  as_anfragetaster = BooleanField(
    'Anfragetaster vorhanden?',
    blank=True,
    null=True
  )
  as_blindenschrift = BooleanField(
    'Haltestellen-/Linieninformationen in Blindenschrift vorhanden?',
    blank=True,
    null=True
  )
  as_beleuchtung = BooleanField(
    'Beleuchtung vorhanden?',
    blank=True,
    null=True
  )
  as_hinweis_warnblinklicht_ein = BooleanField(
    'Hinweis „Warnblinklicht ein“ vorhanden?',
    blank=True,
    null=True
  )
  bfe_park_and_ride = BooleanField(
    'P+R-Parkplatz in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_fahrradabstellmoeglichkeit = BooleanField(
    'Fahrradabstellmöglichkeit in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_querungshilfe = BooleanField(
    'Querungshilfe in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_fussgaengerueberweg = BooleanField(
    'Fußgängerüberweg in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_seniorenheim = BooleanField(
    'Seniorenheim in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_pflegeeinrichtung = BooleanField(
    'Pflegeeinrichtung in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_medizinische_versorgungseinrichtung = BooleanField(
    'Medizinische Versorgungseinrichtung in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bearbeiter = CharField(
    'Bearbeiter:in',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  bemerkungen = NullTextField(
    'Bemerkungen',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = punkt_field

  class Meta(ComplexModel.Meta):
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
    ordering = ['id']
    as_overlay = True

  def __str__(self):
    return self.hst_bezeichnung + ' [ID: ' + str(self.id) + \
      (', HAFAS-ID: ' + self.hst_hafas_id if self.hst_hafas_id else '') + \
      (', Bus-/Bahnsteig: ' +
       self.hst_bus_bahnsteigbezeichnung if self.hst_bus_bahnsteigbezeichnung else '') + ']'


class Haltestellenkataster_Fotos(ComplexModel):
  """
  Haltestellenkataster:
  Fotos
  """

  haltestellenkataster_haltestelle = ForeignKey(
    Haltestellenkataster_Haltestellen,
    verbose_name='Haltestelle',
    on_delete=CASCADE,
    db_column='haltestellenkataster_haltestelle',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_haltestellenkataster_haltestellen'
  )
  motiv = ForeignKey(
    Fotomotive_Haltestellenkataster,
    verbose_name='Motiv',
    on_delete=RESTRICT,
    db_column='motiv',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_motive'
  )
  aufnahmedatum = DateField(
    'Aufnahmedatum',
    default=date.today
  )
  dateiname_original = CharField(
    'Original-Dateiname',
    max_length=255,
    default='ohne'
  )
  foto = ImageField(
    'Foto(s)',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE + 'haltestellenkataster'
    ),
    max_length=255
  )

  class Meta(ComplexModel.Meta):
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
    fields_with_foreign_key_to_linkify = ['haltestellenkataster_haltestelle']
    object_title = 'das Foto'
    foreign_key_label = 'Haltestelle'
    thumbs = True
    multi_foto_field = True

  def __str__(self):
    return str(self.haltestellenkataster_haltestelle) + ' mit Motiv ' + str(self.motiv) + \
      ' und Aufnahmedatum ' + \
      datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')


post_save.connect(photo_post_processing, sender=Haltestellenkataster_Fotos)

post_delete.connect(delete_photo, sender=Haltestellenkataster_Fotos)


#
# Parkscheinautomaten
#

class Parkscheinautomaten_Tarife(ComplexModel):
  """
  Parkscheinautomaten:
  Tarife
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  zeiten = CharField(
    'Bewirtschaftungszeiten',
    max_length=255
  )
  normaltarif_parkdauer_min = PositiveSmallIntegerMinField(
    'Mindestparkdauer Normaltarif',
    min_value=1
  )
  normaltarif_parkdauer_min_einheit = ForeignKey(
    Zeiteinheiten,
    verbose_name='Einheit der Mindestparkdauer Normaltarif',
    on_delete=RESTRICT,
    db_column='normaltarif_parkdauer_min_einheit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_normaltarif_parkdauer_min_einheiten'
  )
  normaltarif_parkdauer_max = PositiveSmallIntegerMinField(
    'Maximalparkdauer Normaltarif',
    min_value=1
  )
  normaltarif_parkdauer_max_einheit = ForeignKey(
    Zeiteinheiten,
    verbose_name='Einheit der Maximalparkdauer Normaltarif',
    on_delete=RESTRICT,
    db_column='normaltarif_parkdauer_max_einheit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_normaltarif_parkdauer_max_einheiten'
  )
  normaltarif_gebuehren_max = DecimalField(
    'Maximalgebühren Normaltarif (in €)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Maximalgebühren Normaltarif</strong></em> müssen mindestens 0,'
        '01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Maximalgebühren Normaltarif</em></strong> dürfen höchstens 99,'
        '99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  normaltarif_gebuehren_pro_stunde = DecimalField(
    'Gebühren pro Stunde Normaltarif (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro Stunde Normaltarif</strong></em> müssen mindestens 0,'
        '01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro Stunde Normaltarif</em></strong> dürfen höchstens 9,'
        '99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  normaltarif_gebuehrenschritte = CharField(
    'Gebührenschritte Normaltarif', max_length=255,
    blank=True,
    null=True
  )
  veranstaltungstarif_parkdauer_min = PositiveSmallIntegerMinField(
    'Mindestparkdauer Veranstaltungstarif', min_value=1,
    blank=True,
    null=True
  )
  veranstaltungstarif_parkdauer_min_einheit = ForeignKey(
    Zeiteinheiten,
    verbose_name='Einheit der Mindestparkdauer Veranstaltungstarif',
    on_delete=SET_NULL,
    db_column='veranstaltungstarif_parkdauer_min_einheit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_veranstaltungstarif_parkdauer_min_einheiten',
    blank=True,
    null=True
  )
  veranstaltungstarif_parkdauer_max = PositiveSmallIntegerMinField(
    'Maximalparkdauer Veranstaltungstarif', min_value=1,
    blank=True,
    null=True
  )
  veranstaltungstarif_parkdauer_max_einheit = ForeignKey(
    Zeiteinheiten,
    verbose_name='Einheit der Maximalparkdauer Veranstaltungstarif',
    on_delete=SET_NULL,
    db_column='veranstaltungstarif_parkdauer_max_einheit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_veranstaltungstarif_parkdauer_max_einheiten',
    blank=True,
    null=True
  )
  veranstaltungstarif_gebuehren_max = DecimalField(
    'Maximalgebühren Veranstaltungstarif (in €)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Maximalgebühren Veranstaltungstarif</strong></em> müssen mindestens 0,'
        '01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Maximalgebühren Veranstaltungstarif</em></strong> dürfen höchstens 99,'
        '99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  veranstaltungstarif_gebuehren_pro_stunde = DecimalField(
    'Gebühren pro Stunde Veranstaltungstarif (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro Stunde Veranstaltungstarif</strong></em> müssen '
        'mindestens 0,01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro Stunde Veranstaltungstarif</em></strong> dürfen höchstens'
        '9,99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  veranstaltungstarif_gebuehrenschritte = CharField(
    'Gebührenschritte Veranstaltungstarif',
    max_length=255,
    blank=True,
    null=True
  )
  zugelassene_muenzen = CharField(
    ' zugelassene Münzen',
    max_length=255
  )

  class Meta(ComplexModel.Meta):
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
      'Parkscheinautomaten_Parkscheinautomaten': 'parkscheinautomaten_tarif'
    }
    ordering = ['bezeichnung']
    as_overlay = False

  def __str__(self):
    return self.bezeichnung


class Parkscheinautomaten_Parkscheinautomaten(ComplexModel):
  """
  Parkscheinautomaten:
  Parkscheinautomaten
  """

  parkscheinautomaten_tarif = ForeignKey(
    Parkscheinautomaten_Tarife,
    verbose_name='Tarif',
    on_delete=CASCADE,
    db_column='parkscheinautomaten_tarif',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_parkscheinautomaten_tarife'
  )
  nummer = PositiveSmallIntegerField('Nummer')
  bezeichnung = bezeichnung_field
  zone = ForeignKey(
    Zonen_Parkscheinautomaten,
    verbose_name='Zone',
    on_delete=RESTRICT,
    db_column='zone',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zonen'
  )
  handyparkzone = PositiveIntegerRangeField(
    'Handyparkzone',
    min_value=100000,
    max_value=999999
  )
  bewohnerparkgebiet = CharField(
    'Bewohnerparkgebiet',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=parkscheinautomaten_bewohnerparkgebiet_regex,
        message=parkscheinautomaten_bewohnerparkgebiet_message
      )
    ]
  )
  geraetenummer = CharField(
    'Gerätenummer',
    max_length=8,
    validators=[
      RegexValidator(
        regex=parkscheinautomaten_geraetenummer_regex,
        message=parkscheinautomaten_geraetenummer_message
      )
    ]
  )
  inbetriebnahme = DateField(
    'Inbetriebnahme',
    blank=True,
    null=True
  )
  e_anschluss = ForeignKey(
    E_Anschluesse_Parkscheinautomaten,
    verbose_name='E-Anschluss',
    on_delete=RESTRICT,
    db_column='e_anschluss',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_e_anschluesse'
  )
  stellplaetze_pkw = PositiveSmallIntegerMinField(
    'Pkw-Stellplätze', min_value=1,
    blank=True,
    null=True
  )
  stellplaetze_bus = PositiveSmallIntegerMinField(
    'Bus-Stellplätze', min_value=1,
    blank=True,
    null=True
  )
  haendlerkartennummer = PositiveIntegerRangeField(
    'Händlerkartennummer',
    min_value=1000000000,
    max_value=9999999999,
    blank=True,
    null=True
  )
  laufzeit_geldkarte = DateField(
    'Laufzeit der Geldkarte',
    blank=True,
    null=True
  )
  geometrie = punkt_field

  class Meta(ComplexModel.Meta):
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


#
# RSAG
#

class RSAG_Gleise(ComplexModel):
  """
  RSAG:
  Gleise
  """

  quelle = CharField(
    'Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = linie_field

  class Meta(ComplexModel.Meta):
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


class RSAG_Masten(ComplexModel):
  """
  RSAG:
  Masten
  """

  mastnummer = CharField(
    'Mastnummer',
    max_length=255,
    validators=standard_validators
  )
  moment_am_fundament = PositiveSmallIntegerRangeField(
    'Moment am Fundament (in kNm)',
    min_value=1,
    blank=True,
    null=True
  )
  spitzenzug_errechnet = DecimalField(
    'Spitzenzug P - Errechnet (in kN)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Spitzenzug P</em></strong> muss mindestens 0,01 kN betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Der <strong><em>Spitzenzug P</em></strong> darf höchstens 999,99 kN betragen.'
      )
    ],
    blank=True,
    null=True
  )
  spitzenzug_gewaehlt = DecimalField(
    'Spitzenzug P - Gewählt (in kN)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Spitzenzug P</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Der <strong><em>Spitzenzug P</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  gesamtlaenge = DecimalField(
    'Gesamtlänge L (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gesamtlänge L</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Gesamtlänge L</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  einsatztiefe = DecimalField(
    'Einsatztiefe T (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Einsatztiefe T</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Einsatztiefe T</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  so_bis_fundament = DecimalField(
    'Schienenoberkante bis Fundament e (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('-1.00'),
        'Die <strong><em>Höhendifferenz zwischen Schienenoberkante und Fundament '
        'e</em></strong> muss mindestens -1,00 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Höhendifferenz zwischen Schienenoberkante und Fundament '
        'e</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  boeschung = DecimalField(
    'Böschungshöhe z (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Böschungshöhe z</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Böschungshöhe z</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  freie_laenge = DecimalField(
    'Freie Länge H (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>freie Länge H</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>freie Länge H</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  masttyp = ForeignKey(
    Masttypen_RSAG,
    verbose_name='Masttyp',
    on_delete=RESTRICT,
    db_column='masttyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_masttypen'
  )
  nennmass_ueber_so = PositiveSmallIntegerRangeField(
    'Nennmaß über Schienenoberkante (in mm)',
    min_value=1,
    blank=True,
    null=True
  )
  mastgewicht = PositiveSmallIntegerRangeField(
    'Mastgewicht (in kg)',
    min_value=1,
    blank=True,
    null=True
  )
  fundamenttyp = ForeignKey(
    Fundamenttypen_RSAG,
    verbose_name='Fundamenttyp',
    on_delete=SET_NULL,
    db_column='fundamenttyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_fundamenttypen',
    blank=True,
    null=True
  )
  fundamentlaenge = DecimalField(
    'Länge des Fundamentes t (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Länge des Fundaments t</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Länge des Fundaments t</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  fundamentdurchmesser = CharField(
    'Durchmesser des Fundaments',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  nicht_tragfaehiger_boden = DecimalField(
    'Tiefe des nicht tragfähiger Boden (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.00'),
        'Die <strong><em>Tiefe des nicht tragfähigen Bodens</em></strong> muss mindestens 0,'
        '00 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Tiefe des nicht tragfähigen Bodens</em></strong> darf höchstens 999,'
        '99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  mastkennzeichen_1 = ForeignKey(
    Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 1',
    on_delete=SET_NULL,
    db_column='mastkennzeichen_1',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_mastkennzeichen_1',
    blank=True,
    null=True
  )
  mastkennzeichen_2 = ForeignKey(
    Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 2',
    on_delete=SET_NULL,
    db_column='mastkennzeichen_2',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_mastkennzeichen_2',
    blank=True,
    null=True
  )
  mastkennzeichen_3 = ForeignKey(
    Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 3',
    on_delete=SET_NULL,
    db_column='mastkennzeichen_3',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_mastkennzeichen_3',
    blank=True,
    null=True
  )
  mastkennzeichen_4 = ForeignKey(
    Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 4',
    on_delete=SET_NULL,
    db_column='mastkennzeichen_4',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_mastkennzeichen_4',
    blank=True,
    null=True
  )
  quelle = CharField(
    'Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  dgm_hoehe = DecimalField(
    'Höhenwert des Durchstoßpunktes auf dem DGM (in m)',
    max_digits=5,
    decimal_places=2,
    blank=True,
    null=True,
    editable=False
  )
  geometrie = punkt_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"rsag_masten_hro'
    verbose_name = 'RSAG-Mast'
    verbose_name_plural = 'RSAG-Masten'
    description = 'Masten innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'mastnummer': 'Mastnummer',
      'gesamtlaenge': 'Gesamtlänge L (in m)',
      'masttyp': 'Masttyp',
      'fundamenttyp': 'Fundamenttyp',
      'mastkennzeichen_1': 'Mastkennzeichen 1',
      'mastkennzeichen_2': 'Mastkennzeichen 2',
      'mastkennzeichen_3': 'Mastkennzeichen 3',
      'mastkennzeichen_4': 'Mastkennzeichen 4',
      'quelle': 'Quelle'
    }
    list_fields_with_number = ['gesamtlaenge']
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
    ordering = ['mastnummer']
    geometry_type = 'Point'
    as_overlay = True

  def __str__(self):
    return self.mastnummer


class RSAG_Leitungen(ComplexModel):
  """
  RSAG:
  Oberleitungen
  """

  geometrie = linie_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"rsag_leitungen_hro'
    verbose_name = 'RSAG-Oberleitung'
    verbose_name_plural = 'RSAG-Oberleitungen'
    description = 'Oberleitungen innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG in der Hanse- und Universitätsstadt Rostock'
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


class RSAG_Quertraeger(ComplexModel):
  """
  RSAG:
  Querträger
  """

  mast = ForeignKey(
    RSAG_Masten,
    verbose_name='Mast',
    on_delete=RESTRICT,
    db_column='mast',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_masten'
  )
  quelle = CharField(
    'Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = linie_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"rsag_quertraeger_hro'
    verbose_name = 'RSAG-Querträger'
    verbose_name_plural = 'RSAG-Querträger'
    description = 'Querträger innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG in der Hanse- und Universitätsstadt Rostock'
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
    map_filter_fields_as_list = ['mast']
    geometry_type = 'LineString'
    as_overlay = True

  def __str__(self):
    return str(self.uuid)


class RSAG_Spanndraehte(ComplexModel):
  """
  RSAG:
  Spanndrähte
  """

  mast = ForeignKey(
    RSAG_Masten,
    verbose_name='Mast',
    on_delete=SET_NULL,
    db_column='mast',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_masten',
    blank=True,
    null=True
  )
  quelle = CharField(
    'Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = linie_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"rsag_spanndraehte_hro'
    verbose_name = 'RSAG-Spanndraht'
    verbose_name_plural = 'RSAG-Spanndrähte'
    description = 'Spanndrähte innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG in der Hanse- und Universitätsstadt Rostock'
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
    map_filter_fields_as_list = ['mast']
    geometry_type = 'LineString'
    as_overlay = True

  def __str__(self):
    return str(self.uuid)


#
# UVP
#

class UVP_Vorhaben(ComplexModel):
  """
  UVP:
  Vorhaben
  """

  bezeichnung = bezeichnung_field
  vorgangsart = ForeignKey(
    Vorgangsarten_UVP_Vorhaben,
    verbose_name='Vorgangsart',
    on_delete=RESTRICT,
    db_column='vorgangsart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_vorgangsarten'
  )
  genehmigungsbehoerde = ForeignKey(
    Genehmigungsbehoerden_UVP_Vorhaben,
    verbose_name='Genehmigungsbehörde',
    on_delete=RESTRICT,
    db_column='genehmigungsbehoerde',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_genehmigungsbehoerden'
  )
  datum_posteingang_genehmigungsbehoerde = DateField(
    'Datum des Posteingangs bei der Genehmigungsbehörde'
  )
  registriernummer_bauamt = CharField(
    'Registriernummer des Bauamtes',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=uvp_registriernummer_bauamt_regex,
        message=uvp_registriernummer_bauamt_message
      )
    ]
  )
  aktenzeichen = CharField(
    'Aktenzeichen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  rechtsgrundlage = ForeignKey(
    Rechtsgrundlagen_UVP_Vorhaben,
    verbose_name='Rechtsgrundlage',
    on_delete=RESTRICT,
    db_column='rechtsgrundlage',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_rechtsgrundlagen'
  )
  typ = ForeignKey(
    Typen_UVP_Vorhaben,
    verbose_name='Typ',
    on_delete=RESTRICT,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen'
  )
  geometrie = flaeche_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"uvp_vorhaben_hro'
    verbose_name = 'UVP-Vorhaben'
    verbose_name_plural = 'UVP-Vorhaben'
    description = 'Vorhaben, auf die sich Vorprüfungen der Hanse- und Universitätsstadt Rostock ' \
                  'zur Feststellung der UVP-Pflicht gemäß UVPG und LUVPG M-V beziehen'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'vorgangsart': 'Vorgangsart',
      'genehmigungsbehoerde': 'Genehmigungsbehörde',
      'datum_posteingang_genehmigungsbehoerde':
        'Datum des Posteingangs bei der Genehmigungsbehörde',
      'rechtsgrundlage': 'Rechtsgrundlage',
      'typ': 'Typ'
    }
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
      'datum_posteingang_genehmigungsbehoerde':
        'Datum des Posteingangs bei der Genehmigungsbehörde',
      'rechtsgrundlage': 'Rechtsgrundlage',
      'typ': 'Typ'
    }
    map_filter_fields_as_list = [
      'vorgangsart',
      'genehmigungsbehoerde',
      'rechtsgrundlage',
      'typ'
    ]
    geometry_type = 'Polygon'
    ordering = ['bezeichnung']
    as_overlay = True

  def __str__(self):
    return self.bezeichnung


class UVP_Vorpruefungen(ComplexModel):
  """
  UVP:
  Vorprüfungen
  """

  uvp_vorhaben = ForeignKey(
    UVP_Vorhaben,
    verbose_name='Vorhaben',
    on_delete=CASCADE,
    db_column='uvp_vorhaben',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_uvp_vorhaben'
  )
  art = ForeignKey(
    Arten_UVP_Vorpruefungen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  datum_posteingang = DateField('Datum des Posteingangs')
  datum = DateField(
    'Datum',
    default=date.today
  )
  ergebnis = ForeignKey(
    Ergebnisse_UVP_Vorpruefungen,
    verbose_name='Ergebnis',
    on_delete=RESTRICT,
    db_column='ergebnis',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ergebnisse'
  )
  datum_bekanntmachung = DateField(
    'Datum Bekanntmachung „Städtischer Anzeiger“',
    blank=True,
    null=True
  )
  datum_veroeffentlichung = DateField(
    'Datum Veröffentlichung UVP-Portal',
    blank=True,
    null=True
  )
  pruefprotokoll = CharField(
    'Prüfprotokoll',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"uvp_vorpruefungen_hro'
    verbose_name = 'UVP-Vorprüfung'
    verbose_name_plural = 'UVP-Vorprüfungen'
    description = 'Vorprüfungen der Hanse- und Universitätsstadt Rostock ' \
                  'zur Feststellung der UVP-Pflicht gemäß UVPG und LUVPG M-V'
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
    return str(self.uvp_vorhaben) + ' mit Datum ' + \
      datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + \
      ' [Art: ' + str(self.art) + ']'
