from datetime import date, datetime, timezone
from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MaxValueValidator, MinValueValidator, \
  RegexValidator, URLValidator, FileExtensionValidator
from django.db.models import CASCADE, RESTRICT, SET_NULL, ForeignKey
from django.db.models.fields import BooleanField, CharField, DateField, DateTimeField, \
  DecimalField, PositiveIntegerField, PositiveSmallIntegerField
from django.db.models.fields.files import FileField, ImageField
from django.db.models.signals import post_delete, post_save, pre_save
from re import sub
from zoneinfo import ZoneInfo
from datenmanagement.utils import get_current_year, path_and_rename
from toolbox.constants_vars import ansprechpartner_validators, standard_validators, url_message
from toolbox.fields import NullTextField
from .base import ComplexModel
from .constants_vars import durchlaesse_aktenzeichen_regex, durchlaesse_aktenzeichen_message, \
  haltestellenkataster_hafas_id_regex, haltestellenkataster_hafas_id_message, \
  parkscheinautomaten_bewohnerparkgebiet_regex, parkscheinautomaten_bewohnerparkgebiet_message, \
  parkscheinautomaten_geraetenummer_regex, parkscheinautomaten_geraetenummer_message, \
  strassen_schluessel_regex, strassen_schluessel_message, uvp_registriernummer_bauamt_regex, \
  uvp_registriernummer_bauamt_message, wikipedia_regex, wikipedia_message
from .fields import ChoiceArrayField, PositiveIntegerMinField, \
  PositiveIntegerRangeField, PositiveSmallIntegerMinField, PositiveSmallIntegerRangeField, \
  point_field, line_field, multiline_field, polygon_field, multipolygon_field
from .functions import delete_pdf, delete_photo, photo_post_processing, \
  delete_pointcloud, set_pre_save_instance, delete_photo_after_emptied
from .models_codelist import Adressen, Gemeindeteile, Strassen, Inoffizielle_Strassen, \
  Gruenpflegeobjekte, Arten_Adressunsicherheiten, Arten_Durchlaesse, \
  Arten_Fallwildsuchen_Kontrollen, Arten_UVP_Vorpruefungen, Arten_Wege, Auftraggeber_Baustellen, \
  Ausfuehrungen_Haltestellenkataster, Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster, \
  Befestigungsarten_Warteflaeche_Haltestellenkataster, E_Anschluesse_Parkscheinautomaten, \
  Ergebnisse_UVP_Vorpruefungen, Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO, \
  Fotomotive_Haltestellenkataster, Fundamenttypen_RSAG, \
  Genehmigungsbehoerden_UVP_Vorhaben, Kabeltypen_Lichtwellenleiterinfrastruktur, \
  Kategorien_Strassen, Mastkennzeichen_RSAG, Masttypen_RSAG, \
  Masttypen_Haltestellenkataster, Materialien_Durchlaesse, \
  Objektarten_Lichtwellenleiterinfrastruktur, Raeumbreiten_Strassenreinigungssatzung_HRO, \
  Rechtsgrundlagen_UVP_Vorhaben, Reinigungsklassen_Strassenreinigungssatzung_HRO, \
  Reinigungsrhythmen_Strassenreinigungssatzung_HRO, Schaeden_Haltestellenkataster, \
  Sitzbanktypen_Haltestellenkataster, Status_Baustellen_geplant, \
  Status_Baustellen_Fotodokumentation_Fotos, Tierseuchen, DFI_Typen_Haltestellenkataster, \
  Fahrgastunterstandstypen_Haltestellenkataster, Fahrplanvitrinentypen_Haltestellenkataster, \
  Typen_Feuerwehrzufahrten_Schilder, Typen_Haltestellen, Typen_UVP_Vorhaben, \
  Vorgangsarten_UVP_Vorhaben, Wegebreiten_Strassenreinigungssatzung_HRO, \
  Wegereinigungsklassen_Strassenreinigungssatzung_HRO, \
  Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO, Wegetypen_Strassenreinigungssatzung_HRO, \
  Zeiteinheiten, ZH_Typen_Haltestellenkataster, Zonen_Parkscheinautomaten, Zustandsbewertungen
from .storage import OverwriteStorage


#
# Adressunsicherheiten
#

class Adressunsicherheiten(ComplexModel):
  """
  Adressunsicherheiten:
  Adressunsicherheiten
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  art = ForeignKey(
    to=Arten_Adressunsicherheiten,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  beschreibung = CharField(
    verbose_name='Beschreibung',
    max_length=255,
    validators=standard_validators
  )
  geometrie = point_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"adressunsicherheiten_hro'
    ordering = ['adresse', 'art']
    verbose_name = 'Adressunsicherheit'
    verbose_name_plural = 'Adressunsicherheiten'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Adressunsicherheiten in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    associated_models = {
      'Adressunsicherheiten_Fotos': 'adressunsicherheit'
    }
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'beschreibung': 'Beschreibung'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'art': 'art'
    }
    list_actions_assign = [
      {
        'action_name': 'adressunsicherheiten-art',
        'action_title': 'ausgewählten Datensätzen Art direkt zuweisen',
        'field': 'art',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['art']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'beschreibung': 'Beschreibung'
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return str(self.art) + (' ' + str(self.adresse) if self.adresse else '')


class Adressunsicherheiten_Fotos(ComplexModel):
  """
  Adressunsicherheiten:
  Fotos
  """

  adressunsicherheit = ForeignKey(
    to=Adressunsicherheiten,
    verbose_name='Adressunsicherheit',
    on_delete=CASCADE,
    db_column='adressunsicherheit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressunsicherheiten'
  )
  aufnahmedatum = DateField(
    verbose_name='Aufnahmedatum',
    default=date.today
  )
  dateiname_original = CharField(
    verbose_name='Original-Dateiname',
    max_length=255,
    default='ohne'
  )
  foto = ImageField(
    verbose_name='Foto(s)',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE + 'adressunsicherheiten'
    ),
    max_length=255
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"adressunsicherheiten_fotos_hro'
    verbose_name = 'Foto einer Adressunsicherheit'
    verbose_name_plural = 'Fotos der Adressunsicherheiten'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Fotos der Adressunsicherheiten ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    short_name = 'Foto'
    readonly_fields = ['dateiname_original']
    fields_with_foreign_key_to_linkify = ['adressunsicherheit']
    multi_photos = True
    list_fields = {
      'aktiv': 'aktiv?',
      'adressunsicherheit': 'Adressunsicherheit',
      'aufnahmedatum': 'Aufnahmedatum',
      'dateiname_original': 'Original-Dateiname',
      'foto': 'Foto'
    }
    list_fields_with_date = ['aufnahmedatum']
    list_fields_with_foreign_key = {
      'adressunsicherheit': 'adresse'
    }

  def __str__(self):
    return str(self.adressunsicherheit) + \
      ' mit Aufnahmedatum ' + \
      datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')


post_save.connect(photo_post_processing, sender=Adressunsicherheiten_Fotos)

post_delete.connect(delete_photo, sender=Adressunsicherheiten_Fotos)


#
# Baustellen-Fotodokumentation
#

class Baustellen_Fotodokumentation_Baustellen(ComplexModel):
  """
  Baustellen-Fotodokumentation:
  Baustellen
  """

  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  verkehrliche_lagen = ChoiceArrayField(
    CharField(
      verbose_name=' verkehrliche Lage(n)',
      max_length=255,
      choices=()
    ),
    verbose_name=' verkehrliche Lage(n)'
  )
  sparten = ChoiceArrayField(
    CharField(
      verbose_name='Sparte(n)',
      max_length=255,
      choices=()
    ),
    verbose_name='Sparte(n)'
  )
  auftraggeber = ForeignKey(
    to=Auftraggeber_Baustellen,
    verbose_name='Auftraggeber',
    on_delete=RESTRICT,
    db_column='auftraggeber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_auftraggeber'
  )
  ansprechpartner = CharField(
    verbose_name='Ansprechpartner:in',
    max_length=255,
    validators=ansprechpartner_validators
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = point_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten_strassenbezug\".\"baustellen_fotodokumentation_baustellen_hro'
    ordering = ['bezeichnung']
    verbose_name = 'Baustelle der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Baustellen der Baustellen-Fotodokumentation'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Baustellen der Baustellen-Fotodokumentation ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    associated_models = {
      'Baustellen_Fotodokumentation_Fotos': 'baustellen_fotodokumentation_baustelle'
    }
    choices_models_for_choices_fields = {
      'verkehrliche_lagen': 'Verkehrliche_Lagen_Baustellen',
      'sparten': 'Sparten_Baustellen'
    }
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'Point'
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
    list_actions_assign = [
      {
        'action_name': 'baustellen_fotodokumentation_baustellen-auftraggeber',
        'action_title': 'ausgewählten Datensätzen Auftraggeber direkt zuweisen',
        'field': 'auftraggeber',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'sparten': 'Sparte(n)',
      'auftraggeber': 'Auftraggeber'
    }
    map_filter_fields_as_list = ['auftraggeber']

  def __str__(self):
    return self.bezeichnung + (' [Straße: ' + str(self.strasse) + ']' if self.strasse else '')


class Baustellen_Fotodokumentation_Fotos(ComplexModel):
  """
  Baustellen-Fotodokumentation:
  Fotos
  """

  baustellen_fotodokumentation_baustelle = ForeignKey(
    to=Baustellen_Fotodokumentation_Baustellen,
    verbose_name='Baustelle',
    on_delete=CASCADE,
    db_column='baustellen_fotodokumentation_baustelle',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_baustellen_fotodokumentation_baustellen'
  )
  status = ForeignKey(
    to=Status_Baustellen_Fotodokumentation_Fotos,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
  aufnahmedatum = DateField(
    verbose_name='Aufnahmedatum',
    default=date.today
  )
  dateiname_original = CharField(
    verbose_name='Original-Dateiname',
    max_length=255,
    default='ohne'
  )
  foto = ImageField(
    verbose_name='Foto(s)',
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

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Fotos der Baustellen-Fotodokumentation ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    short_name = 'Foto'
    readonly_fields = ['dateiname_original']
    fields_with_foreign_key_to_linkify = ['baustellen_fotodokumentation_baustelle']
    multi_photos = True
    list_fields = {
      'aktiv': 'aktiv?',
      'baustellen_fotodokumentation_baustelle': 'Baustelle',
      'status': 'Status',
      'aufnahmedatum': 'Aufnahmedatum',
      'dateiname_original': 'Original-Dateiname',
      'foto': 'Foto'
    }
    list_fields_with_date = ['aufnahmedatum']
    list_fields_with_foreign_key = {
      'baustellen_fotodokumentation_baustelle': 'bezeichnung',
      'status': 'status'
    }
    list_actions_assign = [
      {
        'action_name': 'baustellen_fotodokumentation_fotos-status',
        'action_title': 'ausgewählten Datensätzen Status direkt zuweisen',
        'field': 'status',
        'type': 'foreignkey'
      },
      {
        'action_name': 'baustellen_fotodokumentation_fotos-aufnahmedatum',
        'action_title': 'ausgewählten Datensätzen Aufnahmedatum direkt zuweisen',
        'field': 'aufnahmedatum',
        'type': 'date',
        'value_required': True
      }
    ]

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
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True
  )
  projektbezeichnung = CharField(
    verbose_name='Projektbezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  kurzbeschreibung = NullTextField(
    verbose_name='Kurzbeschreibung',
    blank=True,
    null=True
  )
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  verkehrliche_lagen = ChoiceArrayField(
    CharField(
      verbose_name=' verkehrliche Lage(n)',
      max_length=255,
      choices=()
    ),
    verbose_name=' verkehrliche Lage(n)'
  )
  sparten = ChoiceArrayField(
    CharField(
      verbose_name='Sparte(n)',
      max_length=255,
      choices=()
    ),
    verbose_name='Sparte(n)'
  )
  beginn = DateField('Beginn')
  ende = DateField('Ende')
  auftraggeber = ForeignKey(
    to=Auftraggeber_Baustellen,
    verbose_name='Auftraggeber',
    on_delete=RESTRICT,
    db_column='auftraggeber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_auftraggeber'
  )
  ansprechpartner = CharField(
    verbose_name='Ansprechpartner:in',
    max_length=255,
    validators=ansprechpartner_validators
  )
  status = ForeignKey(
    to=Status_Baustellen_geplant,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
  konflikt = BooleanField(
    verbose_name='Konflikt?',
    blank=True,
    null=True,
    editable=False
  )
  konflikt_tolerieren = BooleanField(
    verbose_name=' räumliche(n)/zeitliche(n) Konflikt(e) mit anderem/anderen Vorhaben tolerieren?',
    blank=True,
    null=True
  )
  geometrie = multipolygon_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten_strassenbezug\".\"baustellen_geplant'
    ordering = ['bezeichnung']
    verbose_name = 'Baustelle (geplant)'
    verbose_name_plural = 'Baustellen (geplant)'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Baustellen (geplant) in der Hanse- und Universitätsstadt Rostock und Umgebung'
    as_overlay = True
    associated_models = {
      'Baustellen_geplant_Dokumente': 'baustelle_geplant',
      'Baustellen_geplant_Links': 'baustelle_geplant'
    }
    choices_models_for_choices_fields = {
      'verkehrliche_lagen': 'Verkehrliche_Lagen_Baustellen',
      'sparten': 'Sparten_Baustellen'
    }
    group_with_users_for_choice_field = 'datenmanagement_baustellen_geplant_full'
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'MultiPolygon'
    geojson_input = True
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
    list_actions_assign = [
      {
        'action_name': 'baustellen_geplant-auftraggeber',
        'action_title': 'ausgewählten Datensätzen Auftraggeber direkt zuweisen',
        'field': 'auftraggeber',
        'type': 'foreignkey'
      },
      {
        'action_name': 'baustellen_geplant-status',
        'action_title': 'ausgewählten Datensätzen Status direkt zuweisen',
        'field': 'status',
        'type': 'foreignkey'
      }
    ]
    highlight_flag = 'konflikt'
    map_feature_tooltip_fields = ['bezeichnung']
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
    to=Baustellen_geplant,
    verbose_name='Baustelle (geplant)',
    on_delete=CASCADE,
    db_column='baustelle_geplant',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_baustellen_geplant'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  dokument = FileField(
    verbose_name='Dokument',
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

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Dokumente der Baustellen (geplant) ' \
                  'in der Hanse- und Universitätsstadt Rostock und Umgebung'
    short_name = 'Dokument'
    fields_with_foreign_key_to_linkify = ['baustelle_geplant']
    list_fields = {
      'aktiv': 'aktiv?',
      'baustelle_geplant': 'Baustelle (geplant)',
      'bezeichnung': 'Bezeichnung',
      'dokument': 'Dokument'
    }
    list_fields_with_foreign_key = {
      'baustelle_geplant': 'bezeichnung'
    }

  def __str__(self):
    return str(self.baustelle_geplant) + ' mit Bezeichnung ' + self.bezeichnung


post_delete.connect(delete_pdf, sender=Baustellen_geplant_Dokumente)


class Baustellen_geplant_Links(ComplexModel):
  """
  Baustellen (geplant):
  Links
  """

  baustelle_geplant = ForeignKey(
    to=Baustellen_geplant,
    verbose_name='Baustelle (geplant)',
    on_delete=CASCADE,
    db_column='baustelle_geplant',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_baustellen_geplant'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  link = CharField(
    verbose_name='Link',
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

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Links der Baustellen (geplant) ' \
                  'in der Hanse- und Universitätsstadt Rostock und Umgebung'
    short_name = 'Link'
    fields_with_foreign_key_to_linkify = ['baustelle_geplant']
    list_fields = {
      'aktiv': 'aktiv?',
      'baustelle_geplant': 'Baustelle (geplant)',
      'bezeichnung': 'Bezeichnung',
      'link': 'Link'
    }
    list_fields_with_foreign_key = {
      'baustelle_geplant': 'bezeichnung'
    }

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
    to=Arten_Durchlaesse,
    verbose_name='Art',
    on_delete=SET_NULL,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
    blank=True,
    null=True
  )
  aktenzeichen = CharField(
    verbose_name='Aktenzeichen',
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
    to=Materialien_Durchlaesse,
    verbose_name='Material',
    on_delete=SET_NULL,
    db_column='material',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_materialien',
    blank=True,
    null=True
  )
  baujahr = PositiveSmallIntegerRangeField(
    verbose_name='Baujahr',
    max_value=get_current_year(),
    blank=True,
    null=True
  )
  nennweite = PositiveSmallIntegerMinField(
    verbose_name='Nennweite (in mm)',
    min_value=100,
    blank=True,
    null=True
  )
  laenge = DecimalField(
    verbose_name='Länge (in m)',
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
    verbose_name='Nebenanlagen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  zubehoer = NullTextField(
    verbose_name='Zubehör',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  zustand_durchlass = ForeignKey(
    to=Zustandsbewertungen,
    verbose_name='Zustand des Durchlasses',
    on_delete=SET_NULL,
    db_column='zustand_durchlass',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende_durchlass',
    blank=True,
    null=True
  )
  zustand_nebenanlagen = ForeignKey(
    to=Zustandsbewertungen,
    verbose_name='Zustand der Nebenanlagen',
    on_delete=SET_NULL,
    db_column='zustand_nebenanlagen',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende_nebenanlagen',
    blank=True,
    null=True
  )
  zustand_zubehoer = ForeignKey(
    to=Zustandsbewertungen,
    verbose_name='Zustand des Zubehörs',
    on_delete=SET_NULL,
    db_column='zustand_zubehoer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende_zubehoer',
    blank=True,
    null=True
  )
  kontrolle = DateField(
    verbose_name='Kontrolle',
    blank=True,
    null=True
  )
  bemerkungen = NullTextField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  zustaendigkeit = CharField(
    verbose_name='Zuständigkeit',
    max_length=255,
    validators=standard_validators
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
    max_length=255,
    validators=standard_validators
  )
  geometrie = point_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"durchlaesse_durchlaesse_hro'
    ordering = ['aktenzeichen']
    verbose_name = 'Durchlass'
    verbose_name_plural = 'Durchlässe'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Durchlässe in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    associated_models = {
      'Durchlaesse_Fotos': 'durchlaesse_durchlass'
    }
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'aktenzeichen': 'Aktenzeichen',
      'material': 'Material',
      'baujahr': 'Baujahr',
      'nennweite': 'Nennweite (in mm)',
      'laenge': 'Länge (in m)',
      'kontrolle': 'Kontrolle',
      'zustaendigkeit': 'Zuständigkeit',
      'bearbeiter': 'Bearbeiter:in'
    }
    list_fields_with_date = ['kontrolle']
    list_fields_with_decimal = ['laenge']
    list_fields_with_foreign_key = {
      'art': 'art',
      'material': 'material'
    }
    list_actions_assign = [
      {
        'action_name': 'durchlaesse_durchlaesse-kontrolle',
        'action_title': 'ausgewählten Datensätzen Kontrolle direkt zuweisen',
        'field': 'kontrolle',
        'type': 'date'
      }
    ]
    map_feature_tooltip_fields = ['aktenzeichen']
    map_filter_fields = {
      'art': 'Art',
      'aktenzeichen': 'Aktenzeichen',
      'material': 'Material',
      'baujahr': 'Baujahr',
      'nennweite': 'Nennweite (in mm)',
      'laenge': 'Länge (in m)',
      'kontrolle': 'Kontrolle',
      'zustaendigkeit': 'Zuständigkeit',
      'bearbeiter': 'Bearbeiter:in'
    }
    map_filter_fields_as_list = ['art', 'material']

  def __str__(self):
    return self.aktenzeichen


class Durchlaesse_Fotos(ComplexModel):
  """
  Durchlässe:
  Fotos
  """

  durchlaesse_durchlass = ForeignKey(
    to=Durchlaesse_Durchlaesse,
    verbose_name='Durchlass',
    on_delete=CASCADE,
    db_column='durchlaesse_durchlass',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_durchlaesse_durchlaesse'
  )
  aufnahmedatum = DateField(
    verbose_name='Aufnahmedatum',
    default=date.today,
    blank=True,
    null=True
  )
  bemerkungen = NullTextField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  dateiname_original = CharField(
    verbose_name='Original-Dateiname',
    max_length=255,
    default='ohne'
  )
  foto = ImageField(
    verbose_name='Foto(s)',
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

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Fotos der Durchlässe in der Hanse- und Universitätsstadt Rostock'
    short_name = 'Foto'
    readonly_fields = ['dateiname_original']
    fields_with_foreign_key_to_linkify = ['durchlaesse_durchlass']
    multi_photos = True
    list_fields = {
      'aktiv': 'aktiv?',
      'durchlaesse_durchlass': 'Durchlass',
      'aufnahmedatum': 'Aufnahmedatum',
      'bemerkungen': 'Bemerkungen',
      'dateiname_original': 'Original-Dateiname',
      'foto': 'Foto'
    }
    list_fields_with_date = ['aufnahmedatum']
    list_fields_with_foreign_key = {
      'durchlaesse_durchlass': 'aktenzeichen'
    }
    list_actions_assign = [
      {
        'action_name': 'durchlaesse_fotos-aufnahmedatum',
        'action_title': 'ausgewählten Datensätzen Aufnahmedatum direkt zuweisen',
        'field': 'aufnahmedatum',
        'type': 'date'
      }
    ]

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
    to=Tierseuchen,
    verbose_name='Tierseuche',
    on_delete=RESTRICT,
    db_column='tierseuche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tierseuchen'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  geometrie = polygon_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"fallwildsuchen_kontrollgebiete_hro'
    ordering = ['bezeichnung']
    verbose_name = 'Kontrollgebiet im Rahmen einer Fallwildsuche'
    verbose_name_plural = 'Kontrollgebiete im Rahmen von Fallwildsuchen'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Kontrollgebiete im Rahmen von Fallwildsuchen ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    associated_models = {
      'Fallwildsuchen_Nachweise': 'kontrollgebiet'
    }
    geometry_type = 'Polygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'tierseuche': 'Tierseuche',
      'bezeichnung': 'Bezeichnung'
    }
    list_fields_with_foreign_key = {
      'tierseuche': 'bezeichnung'
    }
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'tierseuche': 'Tierseuche',
      'bezeichnung': 'Bezeichnung'
    }
    map_filter_fields_as_list = ['tierseuche']

  def __str__(self):
    return self.bezeichnung


class Fallwildsuchen_Nachweise(ComplexModel):
  """
  Fallwildsuchen:
  Nachweise
  """

  kontrollgebiet = ForeignKey(
    to=Fallwildsuchen_Kontrollgebiete,
    verbose_name='Kontrollgebiet',
    on_delete=CASCADE,
    db_column='kontrollgebiet',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_kontrollgebiete'
  )
  art_kontrolle = ForeignKey(
    to=Arten_Fallwildsuchen_Kontrollen,
    verbose_name='Art der Kontrolle',
    on_delete=RESTRICT,
    db_column='art_kontrolle',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten_kontrolle'
  )
  startzeitpunkt = DateTimeField('Startzeitpunkt')
  endzeitpunkt = DateTimeField('Endzeitpunkt')
  geometrie = multiline_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"fallwildsuchen_nachweise_hro'
    verbose_name = 'Nachweis im Rahmen einer Fallwildsuche'
    verbose_name_plural = 'Nachweise im Rahmen von Fallwildsuchen'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Nachweise im Rahmen von Fallwildsuchen ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    short_name = 'Nachweis'
    as_overlay = True
    fields_with_foreign_key_to_linkify = ['kontrollgebiet']
    geometry_type = 'MultiLineString'
    gpx_input = True
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
    map_feature_tooltip_fields = ['art_kontrolle']
    map_intervalfilter_fields = {
      'startzeitpunkt': 'Startzeitpunkt',
      'endzeitpunkt': 'Endzeitpunkt'
    }
    map_filter_fields = {
      'kontrollgebiet': 'Kontrollgebiet',
      'art_kontrolle': 'Art der Kontrolle'
    }
    map_filter_fields_as_list = ['kontrollgebiet', 'art_kontrolle']

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
# Feuerwehrzufahrten
#

class Feuerwehrzufahrten_Feuerwehrzufahrten(ComplexModel):
  """
  Feuerwehrzufahrten:
  Feuerwehrzufahrten
  """

  registriernummer = PositiveSmallIntegerField(
    verbose_name='Registriernummer',
    unique=True,
    blank=True,
    null=True
  )
  bauvorhaben_aktenzeichen_bauamt = ArrayField(
    CharField(
      verbose_name='Bauvorhaben (Aktenzeichen Bauamt)',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators
    ),
    verbose_name='Bauvorhaben (Aktenzeichen Bauamt)',
    blank=True,
    null=True
  )
  bauvorhaben_adressen = ArrayField(
    CharField(
      verbose_name='Bauvorhaben (Adressen)',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators
    ),
    verbose_name='Bauvorhaben (Adressen)',
    blank=True,
    null=True
  )
  erreichbare_objekte = ArrayField(
    CharField(
      verbose_name=' erreichbare Objekte',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators
    ),
    verbose_name=' erreichbare Objekte',
    blank=True,
    null=True
  )
  flaechen_feuerwehrzufahrt = BooleanField(
    verbose_name='Flächen für Feuerwehrzufahrt?',
    blank=True,
    null=True
  )
  feuerwehraufstellflaechen_hubrettungsfahrzeug = BooleanField(
    verbose_name='Aufstellflächen für Hubrettungsfahrzeug?',
    blank=True,
    null=True
  )
  feuerwehrbewegungsflaechen = BooleanField(
    verbose_name='Feuerwehrbewegungsflächen?',
    blank=True,
    null=True
  )
  amtlichmachung = DateField(
    verbose_name='Amtlichmachung',
    blank=True,
    null=True
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"feuerwehrzufahrten_hro'
    ordering = ['registriernummer', 'bemerkungen', 'uuid']
    verbose_name = 'Feuerwehrzufahrt'
    verbose_name_plural = 'Feuerwehrzufahrten'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Feuerwehrzufahrten in der Hanse- und Universitätsstadt Rostock'
    associated_models = {
      'Feuerwehrzufahrten_Schilder': 'feuerwehrzufahrt'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'registriernummer': 'Registriernummer',
      'flaechen_feuerwehrzufahrt': 'Flächen für Feuerwehrzufahrt?',
      'feuerwehraufstellflaechen_hubrettungsfahrzeug': 'Aufstellflächen für Hubrettungsfahrzeug?',
      'feuerwehrbewegungsflaechen': 'Feuerwehrbewegungsflächen?',
      'amtlichmachung': 'Amtlichmachung',
      'bemerkungen': 'Bemerkungen'
    }
    list_fields_with_date = ['amtlichmachung']

  def __str__(self):
    if self.registriernummer:
      return str(self.registriernummer)
    elif self.bemerkungen:
      return 'ohne Registriernummer – ' + self.bemerkungen
    else:
      return 'ohne Registriernummer – ohne Bemerkungen'


class Feuerwehrzufahrten_Schilder(ComplexModel):
  """
  Feuerwehrzufahrten:
  Schilder
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  feuerwehrzufahrt = ForeignKey(
    to=Feuerwehrzufahrten_Feuerwehrzufahrten,
    verbose_name='Feuerwehrzufahrt',
    on_delete=CASCADE,
    db_column='feuerwehrzufahrt',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_feuerwehrzufahrten'
  )
  typ = ForeignKey(
    to=Typen_Feuerwehrzufahrten_Schilder,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
    blank=True,
    null=True
  )
  hinweise_aufstellort = CharField(
    verbose_name='Hinweise zum Aufstellort',
    max_length=255,
    validators=standard_validators
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE + 'feuerwehrzufahrten_schilder'
    ),
    max_length=255,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"feuerwehrzufahrten_schilder_hro'
    verbose_name = 'Schild einer Feuerwehrzufahrt'
    verbose_name_plural = 'Schilder der Feuerwehrzufahrten'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Schilder der Feuerwehrzufahrten in der Hanse- und Universitätsstadt Rostock'
    as_overlay = False
    fields_with_foreign_key_to_linkify = ['feuerwehrzufahrt']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'feuerwehrzufahrt': 'Feuerwehrzufahrt',
      'typ': 'Typ',
      'hinweise_aufstellort': 'Hinweise zum Aufstellort',
      'bemerkungen': 'Bemerkungen',
      'foto': 'Foto'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'feuerwehrzufahrt': 'bemerkungen',
      'typ': 'typ'
    }
    map_feature_tooltip_fields = ['hinweise_aufstellort']
    map_filter_fields = {
      'feuerwehrzufahrt': 'Feuerwehrzufahrt',
      'typ': 'Typ',
      'hinweise_aufstellort': 'Hinweise zum Aufstellort',
      'bemerkungen': 'Bemerkungen'
    }
    map_filter_fields_as_list = ['feuerwehrzufahrt', 'typ']

  def __str__(self):
    return self.hinweise_aufstellort


pre_save.connect(set_pre_save_instance, sender=Feuerwehrzufahrten_Schilder)

post_save.connect(photo_post_processing, sender=Feuerwehrzufahrten_Schilder)

post_save.connect(delete_photo_after_emptied, sender=Feuerwehrzufahrten_Schilder)

post_delete.connect(delete_photo, sender=Feuerwehrzufahrten_Schilder)


#
# Freizeitsport
#

class Freizeitsport(ComplexModel):
  """
  Freizeitsport:
  Freizeitsport
  """

  gruenpflegeobjekt = ForeignKey(
    to=Gruenpflegeobjekte,
    verbose_name='Grünpflegeobjekt',
    on_delete=SET_NULL,
    db_column='gruenpflegeobjekt',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gruenpflegeobjekte',
    blank=True,
    null=True
  )
  staedtisch = BooleanField(
    verbose_name=' städtisch?',
    default=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  bodenarten = ChoiceArrayField(
    CharField(
      verbose_name='Bodenarten',
      max_length=255,
      choices=()
    ),
    verbose_name='Bodenarten',
    blank=True,
    null=True
  )
  sportarten = ChoiceArrayField(
    CharField(
      verbose_name='Sportarten',
      max_length=255,
      choices=()
    ),
    verbose_name='Sportarten'
  )
  besonderheiten = ChoiceArrayField(
    CharField(
      verbose_name='Besonderheiten',
      max_length=255,
      choices=()
    ),
    verbose_name='Besonderheiten',
    blank=True,
    null=True
  )
  freizeitsport = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False
  )
  geometrie = point_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"freizeitsport_hro'
    ordering = ['staedtisch', 'gruenpflegeobjekt', 'bezeichnung']
    verbose_name = 'Freizeitsport'
    verbose_name_plural = 'Freizeitsport'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Freizeitsport in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'bodenarten': 'Bodenarten_Freizeitsport',
      'sportarten': 'Freizeitsportarten',
      'besonderheiten': 'Besonderheiten_Freizeitsport'
    }
    associated_models = {
      'Freizeitsport_Fotos': 'freizeitsport'
    }
    fields_with_foreign_key_to_linkify = ['gruenpflegeobjekt']
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'gruenpflegeobjekt': 'Grünpflegeobjekt',
      'staedtisch': 'städtisch?',
      'bezeichnung': 'Bezeichnung',
      'bodenarten': 'Bodenarten',
      'sportarten': 'Sportarten',
      'besonderheiten': 'Besonderheiten'
    }
    list_fields_with_foreign_key = {
      'gruenpflegeobjekt': 'gruenpflegeobjekt'
    }
    map_feature_tooltip_fields = ['gruenpflegeobjekt', 'bezeichnung']
    map_filter_fields = {
      'gruenpflegeobjekt': 'Grünpflegeobjekt',
      'staedtisch': 'städtisch?',
      'bezeichnung': 'Bezeichnung',
      'bodenarten': 'Bodenarten',
      'sportarten': 'Sportarten',
      'besonderheiten': 'Besonderheiten'
    }
    map_filter_fields_as_list = ['gruenpflegeobjekt']

  def string_representation(self):
    gruenpflegeobjekt_str = str(self.gruenpflegeobjekt) + ', ' if self.gruenpflegeobjekt else ''
    bezeichnung_str = self.bezeichnung + ', ' if self.bezeichnung else ''
    staedtisch_str = 'städtisch' if self.staedtisch else 'nicht städtisch'
    return gruenpflegeobjekt_str + bezeichnung_str + staedtisch_str

  def __str__(self):
    return self.string_representation()

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
    # store search content in designated field
    self.freizeitsport = self.string_representation()
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )


class Freizeitsport_Fotos(ComplexModel):
  """
  Freizeitsport:
  Fotos
  """

  freizeitsport = ForeignKey(
    to=Freizeitsport,
    verbose_name='Freizeitsport',
    on_delete=CASCADE,
    db_column='freizeitsport',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_freizeitsport'
  )
  oeffentlich_sichtbar = BooleanField(
    verbose_name=' öffentlich sichtbar?',
    default=True
  )
  aufnahmedatum = DateField(
    verbose_name='Aufnahmedatum',
    default=date.today,
    blank=True,
    null=True
  )
  bemerkungen = NullTextField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  dateiname_original = CharField(
    verbose_name='Original-Dateiname',
    max_length=255,
    default='ohne'
  )
  foto = ImageField(
    verbose_name='Foto(s)',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC + 'freizeitsport'
    ),
    max_length=255
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"freizeitsport_fotos_hro'
    verbose_name = 'Foto des Freizeitsports'
    verbose_name_plural = 'Fotos des Freizeitsports'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Fotos des Freizeitsports in der Hanse- und Universitätsstadt Rostock'
    short_name = 'Foto'
    readonly_fields = ['dateiname_original']
    fields_with_foreign_key_to_linkify = ['freizeitsport']
    multi_photos = True
    list_fields = {
      'aktiv': 'aktiv?',
      'freizeitsport': 'Freizeitsport',
      'oeffentlich_sichtbar': 'öffentlich sichtbar?',
      'aufnahmedatum': 'Aufnahmedatum',
      'bemerkungen': 'Bemerkungen',
      'dateiname_original': 'Original-Dateiname',
      'foto': 'Foto'
    }
    list_fields_with_foreign_key = {
      'freizeitsport': 'freizeitsport'
    }
    list_fields_with_date = ['aufnahmedatum']
    list_actions_assign = [
      {
        'action_name': 'freizeitsport_fotos-aufnahmedatum',
        'action_title': 'ausgewählten Datensätzen Aufnahmedatum direkt zuweisen',
        'field': 'aufnahmedatum',
        'type': 'date'
      }
    ]

  def __str__(self):
    if self.oeffentlich_sichtbar:
      oeffentlich_sichtbar_str = ' (öffentlich sichtbar)'
    else:
      oeffentlich_sichtbar_str = ' (nicht öffentlich sichtbar)'
    if self.aufnahmedatum:
      aufnahmedatum_str = ' mit Aufnahmedatum ' + datetime.strptime(
        str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')
    else:
      aufnahmedatum_str = ''
    return str(self.freizeitsport) + aufnahmedatum_str + oeffentlich_sichtbar_str


post_save.connect(photo_post_processing, sender=Freizeitsport_Fotos)

post_delete.connect(delete_photo, sender=Freizeitsport_Fotos)


#
# Geh- und Radwegereinigung
#

class Geh_Radwegereinigung(ComplexModel):
  """
  Geh- und Radwegereinigung:
  Geh- und Radwegereinigung
  """

  id = CharField(
    verbose_name='ID',
    max_length=14,
    default='0000000000-000'
  )
  gemeindeteil = ForeignKey(
    to=Gemeindeteile,
    verbose_name='Gemeindeteil',
    on_delete=RESTRICT,
    db_column='gemeindeteil',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gemeindeteile',
    default='00000000-0000-0000-0000-000000000000'
  )
  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True
  )
  inoffizielle_strasse = ForeignKey(
    to=Inoffizielle_Strassen,
    verbose_name=' inoffizielle Straße',
    on_delete=SET_NULL,
    db_column='inoffizielle_strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_inoffizielle_strassen',
    blank=True,
    null=True
  )
  nummer = CharField(
    verbose_name='Nummer',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  beschreibung = CharField(
    verbose_name='Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  wegeart = ForeignKey(
    to=Arten_Wege,
    verbose_name='Wegeart',
    on_delete=RESTRICT,
    db_column='wegeart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_wegearten'
  )
  wegetyp = ForeignKey(
    to=Wegetypen_Strassenreinigungssatzung_HRO,
    verbose_name='Wegetyp',
    on_delete=RESTRICT,
    db_column='wegetyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_wegetypen',
    blank=True,
    null=True
  )
  reinigungsklasse = ForeignKey(
    to=Wegereinigungsklassen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsklasse',
    on_delete=SET_NULL,
    db_column='reinigungsklasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_reinigungsklassen',
    blank=True,
    null=True
  )
  reinigungsrhythmus = ForeignKey(
    to=Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsrhythmus',
    on_delete=SET_NULL,
    db_column='reinigungsrhythmus',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_reinigungsrhythmen',
    blank=True,
    null=True
  )
  laenge = DecimalField(
    verbose_name='Länge (in m)',
    max_digits=7,
    decimal_places=2,
    default=0
  )
  breite = ForeignKey(
    to=Wegebreiten_Strassenreinigungssatzung_HRO,
    verbose_name='Breite (in m)',
    on_delete=RESTRICT,
    db_column='breite',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_breiten',
    blank=True,
    null=True
  )
  reinigungsflaeche = DecimalField(
    verbose_name='Reinigungsfläche (in m²)',
    max_digits=7,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Reinigungsfläche</em></strong> muss mindestens 0,01 m² betragen.'
      ),
      MaxValueValidator(
        Decimal('99999.99'),
        'Die <strong><em>Reinigungsfläche</em></strong> darf höchstens 99.999,99 m² betragen.'
      )
    ],
    blank=True,
    null=True
  )
  winterdienst = BooleanField(
    verbose_name='Winterdienst?',
    blank=True,
    null=True
  )
  raeumbreite = ForeignKey(
    to=Raeumbreiten_Strassenreinigungssatzung_HRO,
    verbose_name='Räumbreite im Winterdienst (in m)',
    on_delete=RESTRICT,
    db_column='raeumbreite',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_raeumbreiten',
    blank=True,
    null=True
  )
  winterdienstflaeche = DecimalField(
    verbose_name='Winterdienstfläche (in m²)',
    max_digits=7,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Winterdienstfläche</em></strong> muss mindestens 0,01 m² betragen.'
      ),
      MaxValueValidator(
        Decimal('99999.99'),
        'Die <strong><em>Winterdienstfläche</em></strong> darf höchstens 99.999,99 m² betragen.'
      )
    ],
    blank=True,
    null=True
  )
  geometrie = multiline_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten_strassenbezug\".\"geh_und_radwegereinigung_hro'
    ordering = ['id']
    verbose_name = 'Geh- und Radwegereinigung'
    verbose_name_plural = 'Geh- und Radwegereinigung'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Geh- und Radwegereinigung der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    associated_models = {
      'Geh_Radwegereinigung_Flaechen': 'geh_und_radwegereinigung'
    }
    readonly_fields = ['id', 'gemeindeteil', 'laenge']
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'MultiLineString'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'gemeindeteil': 'Gemeindeteil',
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
    list_fields_with_decimal = ['laenge', 'breite']
    list_fields_with_foreign_key = {
      'gemeindeteil': 'gemeindeteil',
      'strasse': 'strasse',
      'inoffizielle_strasse': 'strasse',
      'wegeart': 'art',
      'wegetyp': 'wegetyp',
      'reinigungsklasse': 'code',
      'reinigungsrhythmus': 'reinigungsrhythmus',
      'breite': 'wegebreite'
    }
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'id': 'ID',
      'gemeindeteil': 'Gemeindeteil',
      'strasse': 'Straße',
      'inoffizielle_strasse': 'inoffizielle Straße',
      'nummer': 'Nummer',
      'beschreibung': 'Beschreibung',
      'wegeart': 'Wegeart',
      'wegetyp': 'Wegetyp',
      'reinigungsklasse': 'Reinigungsklasse',
      'reinigungsrhythmus': 'Reinigungsrhythmus',
      'breite': 'Breite (in m)',
      'winterdienst': 'Winterdienst?'
    }
    map_filter_fields_as_list = [
      'strasse',
      'gemeindeteil',
      'inoffizielle_strasse',
      'wegeart',
      'wegetyp',
      'reinigungsklasse',
      'reinigungsrhythmus',
      'breite'
    ]
    additional_wms_layers = [
      {
        'title': 'Reinigungsreviere',
        'url': 'https://geo.sv.rostock.de/geodienste/reinigungsreviere/wms',
        'layers': 'hro.reinigungsreviere.reinigungsreviere'
      }, {
        'title': 'Geh- und Radwegereinigung',
        'url': 'https://geo.sv.rostock.de/geodienste/geh_und_radwegereinigung/wms',
        'layers': 'hro.geh_und_radwegereinigung.geh_und_radwegereinigung'
      }, {
        'title': 'Straßenreinigung',
        'url': 'https://geo.sv.rostock.de/geodienste/strassenreinigung/wms',
        'layers': 'hro.strassenreinigung.strassenreinigung'
      }
    ]

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


class Geh_Radwegereinigung_Flaechen(ComplexModel):
  """
  Geh- und Radwegereinigung:
  Flächen
  """

  geh_und_radwegereinigung = ForeignKey(
    to=Geh_Radwegereinigung,
    verbose_name='Geh- und Radwegereinigung',
    on_delete=CASCADE,
    db_column='geh_und_radwegereinigung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_geh_und_radwegereinigung'
  )
  geometrie = multipolygon_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"geh_und_radwegereinigung_flaechen_hro'
    verbose_name = 'Fläche zur Geh- und Radwegereinigung'
    verbose_name_plural = 'Flächen zur Geh- und Radwegereinigung'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Flächen zur Geh- und Radwegereinigung der Hanse- und Universitätsstadt Rostock'
    short_name = 'Fläche'
    as_overlay = True
    fields_with_foreign_key_to_linkify = ['geh_und_radwegereinigung']
    geometry_type = 'MultiPolygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'geh_und_radwegereinigung': 'Geh- und Radwegereinigung'
    }
    list_fields_with_foreign_key = {
      'geh_und_radwegereinigung': 'id'
    }
    map_feature_tooltip_fields = ['geh_und_radwegereinigung']

  def __str__(self):
    return str(self.geh_und_radwegereinigung)


#
# Haltestellenkataster
#

class Haltestellenkataster_Haltestellen(ComplexModel):
  """
  Haltestellenkataster:
  Haltestellen
  """

  deaktiviert = DateField(
    verbose_name='Außerbetriebstellung',
    blank=True,
    null=True
  )
  id = PositiveIntegerField(
    verbose_name='ID',
    unique=True,
    default=0
  )
  hst_bezeichnung = CharField(
    verbose_name='Haltestellenbezeichnung',
    max_length=255,
    validators=standard_validators
  )
  hst_hafas_id = CharField(
    verbose_name='HAFAS-ID',
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
    verbose_name='Bus-/Bahnsteigbezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  hst_richtung = CharField(
    verbose_name='Richtungsinformation',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  hst_kategorie = CharField(
    verbose_name='Haltestellenkategorie',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  hst_linien = ChoiceArrayField(
    CharField(
      verbose_name=' bedienende Linie(n)',
      max_length=4,
      choices=()
    ),
    verbose_name=' bedienende Linie(n)',
    blank=True,
    null=True
  )
  hst_rsag = BooleanField(
    verbose_name=' bedient durch Rostocker Straßenbahn AG?',
    blank=True,
    null=True
  )
  hst_rebus = BooleanField(
    verbose_name=' bedient durch rebus Regionalbus Rostock GmbH?',
    blank=True,
    null=True
  )
  hst_nur_ausstieg = BooleanField(
    verbose_name=' nur Ausstieg?',
    blank=True,
    null=True
  )
  hst_nur_einstieg = BooleanField(
    verbose_name=' nur Einstieg?',
    blank=True,
    null=True
  )
  hst_verkehrsmittelklassen = ChoiceArrayField(
    CharField(
      verbose_name='Verkehrsmittelklasse(n)',
      max_length=255,
      choices=()
    ),
    verbose_name='Verkehrsmittelklasse(n)'
  )
  hst_abfahrten = PositiveSmallIntegerMinField(
    verbose_name=' durchschnittliche tägliche Zahl an Abfahrten',
    min_value=1,
    blank=True,
    null=True
  )
  hst_fahrgastzahl_einstieg = PositiveSmallIntegerMinField(
    verbose_name=' durchschnittliche tägliche Fahrgastzahl (Einstieg)',
    min_value=1,
    blank=True,
    null=True
  )
  hst_fahrgastzahl_ausstieg = PositiveSmallIntegerMinField(
    verbose_name=' durchschnittliche tägliche Fahrgastzahl (Ausstieg)',
    min_value=1,
    blank=True,
    null=True
  )
  bau_typ = ForeignKey(
    to=Typen_Haltestellen,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='bau_typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_typen',
    blank=True,
    null=True
  )
  bau_wartebereich_laenge = DecimalField(
    verbose_name='Länge des Wartebereichs (in m)',
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
    verbose_name='Breite des Wartebereichs (in m)',
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
    to=Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster,
    verbose_name='Befestigungsart der Aufstellfläche Bus',
    on_delete=SET_NULL,
    db_column='bau_befestigungsart_aufstellflaeche_bus',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_befestigungsarten_aufstellflaeche_bus',
    blank=True,
    null=True
  )
  bau_zustand_aufstellflaeche_bus = ForeignKey(
    to=Schaeden_Haltestellenkataster,
    verbose_name='Zustand der Aufstellfläche Bus',
    on_delete=SET_NULL,
    db_column='bau_zustand_aufstellflaeche_bus',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_zustaende_aufstellflaeche_bus',
    blank=True,
    null=True
  )
  bau_befestigungsart_warteflaeche = ForeignKey(
    to=Befestigungsarten_Warteflaeche_Haltestellenkataster,
    verbose_name='Befestigungsart der Wartefläche',
    on_delete=SET_NULL,
    db_column='bau_befestigungsart_warteflaeche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_befestigungsarten_warteflaeche',
    blank=True,
    null=True
  )
  bau_zustand_warteflaeche = ForeignKey(
    to=Schaeden_Haltestellenkataster,
    verbose_name='Zustand der Wartefläche',
    on_delete=SET_NULL,
    db_column='bau_zustand_warteflaeche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bau_zustaende_warteflaeche',
    blank=True,
    null=True
  )
  bf_einstieg = BooleanField(
    verbose_name=' barrierefreier Einstieg vorhanden?',
    blank=True,
    null=True
  )
  bf_zu_abgaenge = BooleanField(
    verbose_name=' barrierefreie Zu- und Abgänge vorhanden?',
    blank=True,
    null=True
  )
  bf_bewegungsraum = BooleanField(
    verbose_name=' barrierefreier Bewegungsraum vorhanden?',
    blank=True,
    null=True
  )
  tl_auffindestreifen = BooleanField(
    verbose_name='Taktiles Leitsystem: Auffindestreifen vorhanden?',
    blank=True,
    null=True
  )
  tl_auffindestreifen_ausfuehrung = ForeignKey(
    to=Ausfuehrungen_Haltestellenkataster,
    verbose_name='Taktiles Leitsystem: Ausführung Auffindestreifen',
    on_delete=SET_NULL,
    db_column='tl_auffindestreifen_ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tl_auffindestreifen_ausfuehrungen',
    blank=True,
    null=True
  )
  tl_auffindestreifen_breite = PositiveIntegerMinField(
    verbose_name='Taktiles Leitsystem: Breite des Auffindestreifens (in cm)',
    min_value=1,
    blank=True,
    null=True
  )
  tl_einstiegsfeld = BooleanField(
    verbose_name='Taktiles Leitsystem: Einstiegsfeld vorhanden?',
    blank=True,
    null=True
  )
  tl_einstiegsfeld_ausfuehrung = ForeignKey(
    to=Ausfuehrungen_Haltestellenkataster,
    verbose_name='Taktiles Leitsystem: Ausführung Einstiegsfeld',
    on_delete=SET_NULL,
    db_column='tl_einstiegsfeld_ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tl_einstiegsfeld_ausfuehrungen',
    blank=True,
    null=True
  )
  tl_einstiegsfeld_breite = PositiveIntegerMinField(
    verbose_name='Taktiles Leitsystem: Breite des Einstiegsfelds (in cm)',
    min_value=1,
    blank=True,
    null=True
  )
  tl_leitstreifen = BooleanField(
    verbose_name='Taktiles Leitsystem: Leitstreifen vorhanden?',
    blank=True,
    null=True
  )
  tl_leitstreifen_ausfuehrung = ForeignKey(
    to=Ausfuehrungen_Haltestellenkataster,
    verbose_name='Taktiles Leitsystem: Ausführung Leitstreifen',
    on_delete=SET_NULL,
    db_column='tl_leitstreifen_ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tl_leitstreifen_ausfuehrungen',
    blank=True,
    null=True
  )
  tl_leitstreifen_laenge = PositiveIntegerMinField(
    verbose_name='Taktiles Leitsystem: Länge des Leitstreifens (in cm)',
    min_value=1,
    blank=True,
    null=True
  )
  tl_aufmerksamkeitsfeld = BooleanField(
    verbose_name='Aufmerksamkeitsfeld (1. Tür) vorhanden?',
    blank=True,
    null=True
  )
  tl_bahnsteigkante_visuell = BooleanField(
    verbose_name='Bahnsteigkante visuell erkennbar?',
    blank=True,
    null=True
  )
  tl_bahnsteigkante_taktil = BooleanField(
    verbose_name='Bahnsteigkante taktil erkennbar?',
    blank=True,
    null=True
  )
  as_zh_typ = ForeignKey(
    to=ZH_Typen_Haltestellenkataster,
    verbose_name='ZH-Typ',
    on_delete=SET_NULL,
    db_column='as_zh_typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_zh_typen',
    blank=True,
    null=True
  )
  as_h_mast = BooleanField(
    verbose_name='Mast vorhanden?',
    blank=True,
    null=True
  )
  as_h_masttyp = ForeignKey(
    to=Masttypen_Haltestellenkataster,
    verbose_name='Masttyp',
    on_delete=SET_NULL,
    db_column='as_h_masttyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_h_masttypen',
    blank=True,
    null=True
  )
  as_papierkorb = BooleanField(
    verbose_name='Papierkorb vorhanden?',
    blank=True,
    null=True
  )
  as_fahrgastunterstand = BooleanField(
    verbose_name='Fahrgastunterstand vorhanden?',
    blank=True,
    null=True
  )
  as_fahrgastunterstandstyp = ForeignKey(
    to=Fahrgastunterstandstypen_Haltestellenkataster,
    verbose_name='Typ des Fahrgastunterstand',
    on_delete=SET_NULL,
    db_column='as_fahrgastunterstandstyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_fahrgastunterstandstypen',
    blank=True,
    null=True
  )
  as_sitzbank_mit_armlehne = BooleanField(
    verbose_name='Sitzbank mit Armlehne vorhanden?',
    blank=True,
    null=True
  )
  as_sitzbank_ohne_armlehne = BooleanField(
    verbose_name='Sitzbank ohne Armlehne vorhanden?',
    blank=True,
    null=True
  )
  as_sitzbanktyp = ForeignKey(
    to=Sitzbanktypen_Haltestellenkataster,
    verbose_name='Typ der Sitzbank',
    on_delete=SET_NULL,
    db_column='as_sitzbanktyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_sitzbanktypen',
    blank=True,
    null=True
  )
  as_gelaender = BooleanField(
    verbose_name='Geländer vorhanden?',
    blank=True,
    null=True
  )
  as_fahrplanvitrine = BooleanField(
    verbose_name='Fahrplanvitrine vorhanden?',
    blank=True,
    null=True
  )
  as_fahrplanvitrinentyp = ForeignKey(
    to=Fahrplanvitrinentypen_Haltestellenkataster,
    verbose_name='Typ der Fahrplanvitrine',
    on_delete=SET_NULL,
    db_column='as_fahrplanvitrinentyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_fahrplanvitrinentypen',
    blank=True,
    null=True
  )
  as_tarifinformation = BooleanField(
    verbose_name='Tarifinformation vorhanden?',
    blank=True,
    null=True
  )
  as_liniennetzplan = BooleanField(
    verbose_name='Liniennetzplan vorhanden?',
    blank=True,
    null=True
  )
  as_fahrplan = BooleanField(
    verbose_name='Fahrplan vorhanden?',
    blank=True,
    null=True
  )
  as_fahrausweisautomat = BooleanField(
    verbose_name='Fahrausweisautomat vorhanden?',
    blank=True,
    null=True
  )
  as_lautsprecher = BooleanField(
    verbose_name='Lautsprecher vorhanden?',
    blank=True,
    null=True
  )
  as_dfi = BooleanField(
    verbose_name='Dynamisches Fahrgastinformationssystem vorhanden?',
    blank=True,
    null=True
  )
  as_dfi_typ = ForeignKey(
    to=DFI_Typen_Haltestellenkataster,
    verbose_name='Typ des Dynamischen Fahrgastinformationssystems',
    on_delete=SET_NULL,
    db_column='as_dfi_typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_as_dfi_typen',
    blank=True,
    null=True
  )
  as_anfragetaster = BooleanField(
    verbose_name='Anfragetaster vorhanden?',
    blank=True,
    null=True
  )
  as_blindenschrift = BooleanField(
    verbose_name='Haltestellen-/Linieninformationen in Blindenschrift vorhanden?',
    blank=True,
    null=True
  )
  as_beleuchtung = BooleanField(
    verbose_name='Beleuchtung vorhanden?',
    blank=True,
    null=True
  )
  as_hinweis_warnblinklicht_ein = BooleanField(
    verbose_name='Hinweis „Warnblinklicht ein“ vorhanden?',
    blank=True,
    null=True
  )
  bfe_park_and_ride = BooleanField(
    verbose_name='P+R-Parkplatz in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_fahrradabstellmoeglichkeit = BooleanField(
    verbose_name='Fahrradabstellmöglichkeit in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_querungshilfe = BooleanField(
    verbose_name='Querungshilfe in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_fussgaengerueberweg = BooleanField(
    verbose_name='Fußgängerüberweg in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_seniorenheim = BooleanField(
    verbose_name='Seniorenheim in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_pflegeeinrichtung = BooleanField(
    verbose_name='Pflegeeinrichtung in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bfe_medizinische_versorgungseinrichtung = BooleanField(
    verbose_name='Medizinische Versorgungseinrichtung in Umgebung vorhanden?',
    blank=True,
    null=True
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  bemerkungen = NullTextField(
    verbose_name='Bemerkungen',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = point_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"haltestellenkataster_haltestellen_hro'
    unique_together = ['hst_hafas_id', 'hst_bus_bahnsteigbezeichnung']
    ordering = ['id']
    verbose_name = 'Haltestelle des Haltestellenkatasters'
    verbose_name_plural = 'Haltestellen des Haltestellenkatasters'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Haltestellen des Haltestellenkatasters der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    associated_models = {
      'Haltestellenkataster_Fotos': 'haltestellenkataster_haltestelle'
    }
    readonly_fields = ['id']
    choices_models_for_choices_fields = {
      'hst_linien': 'Linien',
      'hst_verkehrsmittelklassen': 'Verkehrsmittelklassen'
    }
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Außerbetriebstellung',
      'id': 'ID',
      'hst_bezeichnung': 'Haltestellenbezeichnung',
      'hst_hafas_id': 'HAFAS-ID',
      'hst_bus_bahnsteigbezeichnung': 'Bus-/Bahnsteigbezeichnung'
    }
    list_fields_with_date = ['deaktiviert']
    map_feature_tooltip_fields = ['hst_bezeichnung']

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
    to=Haltestellenkataster_Haltestellen,
    verbose_name='Haltestelle',
    on_delete=CASCADE,
    db_column='haltestellenkataster_haltestelle',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_haltestellenkataster_haltestellen'
  )
  motiv = ForeignKey(
    to=Fotomotive_Haltestellenkataster,
    verbose_name='Motiv',
    on_delete=RESTRICT,
    db_column='motiv',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_motive'
  )
  aufnahmedatum = DateField(
    verbose_name='Aufnahmedatum',
    default=date.today
  )
  dateiname_original = CharField(
    verbose_name='Original-Dateiname',
    max_length=255,
    default='ohne'
  )
  foto = ImageField(
    verbose_name='Foto(s)',
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

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Fotos des Haltestellenkatasters der Hanse- und Universitätsstadt Rostock'
    short_name = 'Foto'
    readonly_fields = ['dateiname_original']
    fields_with_foreign_key_to_linkify = ['haltestellenkataster_haltestelle']
    multi_photos = True
    list_fields = {
      'aktiv': 'aktiv?',
      'haltestellenkataster_haltestelle': 'Haltestelle',
      'motiv': 'Motiv',
      'aufnahmedatum': 'Aufnahmedatum',
      'dateiname_original': 'Original-Dateiname',
      'foto': 'Foto'
    }
    list_fields_with_date = ['aufnahmedatum']
    list_fields_with_foreign_key = {
      'haltestellenkataster_haltestelle': 'id',
      'motiv': 'fotomotiv'
    }
    list_actions_assign = [
      {
        'action_name': 'haltestellenkataster_fotos-motiv',
        'action_title': 'ausgewählten Datensätzen Motiv direkt zuweisen',
        'field': 'motiv',
        'type': 'foreignkey'
      },
      {
        'action_name': 'haltestellenkataster_fotos-aufnahmedatum',
        'action_title': 'ausgewählten Datensätzen Aufnahmedatum direkt zuweisen',
        'field': 'aufnahmedatum',
        'type': 'date',
        'value_required': True
      }
    ]

  def __str__(self):
    return str(self.haltestellenkataster_haltestelle) + ' mit Motiv ' + str(self.motiv) + \
      ' und Aufnahmedatum ' + \
      datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')


post_save.connect(photo_post_processing, sender=Haltestellenkataster_Fotos)

post_delete.connect(delete_photo, sender=Haltestellenkataster_Fotos)


#
# Lichtwellenleiterinfrastruktur
#

class Lichtwellenleiterinfrastruktur_Abschnitte(ComplexModel):
  """
  Lichtwellenleiterinfrastruktur:
  Abschnitte
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"lichtwellenleiterinfrastruktur_abschnitte_hro'
    ordering = ['bezeichnung']
    verbose_name = 'Abschnitt der Lichtwellenleiterinfrastruktur'
    verbose_name_plural = 'Abschnitte der Lichtwellenleiterinfrastruktur'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Abschnitte der Lichtwellenleiterinfrastruktur ' \
                   'in der Hanse- und Universitätsstadt Rostock'
    associated_models = {
      'Lichtwellenleiterinfrastruktur': 'abschnitt'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung'
    }

  def __str__(self):
    return self.bezeichnung


class Lichtwellenleiterinfrastruktur(ComplexModel):
  """
  Lichtwellenleiterinfrastruktur:
  Lichtwellenleiterinfrastruktur
  """

  abschnitt = ForeignKey(
    to=Lichtwellenleiterinfrastruktur_Abschnitte,
    verbose_name='Abschnitt',
    on_delete=SET_NULL,
    db_column='abschnitt',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_abschnitte',
    blank=True,
    null=True
  )
  objektart = ForeignKey(
    to=Objektarten_Lichtwellenleiterinfrastruktur,
    verbose_name='Objektart',
    on_delete=RESTRICT,
    db_column='objektart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_objektarten'
  )
  kabeltyp = ForeignKey(
    to=Kabeltypen_Lichtwellenleiterinfrastruktur,
    verbose_name='Kabeltyp',
    on_delete=SET_NULL,
    db_column='kabeltyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_kabeltypen',
    blank=True,
    null=True
  )
  geometrie = multiline_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"lichtwellenleiterinfrastruktur_hro'
    verbose_name = 'Lichtwellenleiterinfrastruktur'
    verbose_name_plural = 'Lichtwellenleiterinfrastruktur'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Lichtwellenleiterinfrastruktur in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    fields_with_foreign_key_to_linkify = ['abschnitt']
    geometry_type = 'MultiLineString'
    list_fields = {
      'aktiv': 'aktiv?',
      'uuid': 'UUID',
      'abschnitt': 'Abschnitt',
      'objektart': 'Objektart',
      'kabeltyp': 'Kabeltyp'
    }
    list_fields_with_foreign_key = {
      'abschnitt': 'bezeichnung',
      'objektart': 'objektart',
      'kabeltyp': 'kabeltyp'
    }
    list_actions_assign = [
      {
        'action_name': 'lichtwellenleiterinfrastruktur-abschnitt',
        'action_title': 'ausgewählten Datensätzen Abschnitt direkt zuweisen',
        'field': 'abschnitt',
        'type': 'foreignkey'
      },
      {
        'action_name': 'lichtwellenleiterinfrastruktur-objektart',
        'action_title': 'ausgewählten Datensätzen Objektart direkt zuweisen',
        'field': 'objektart',
        'type': 'foreignkey'
      },
      {
        'action_name': 'lichtwellenleiterinfrastruktur-kabeltyp',
        'action_title': 'ausgewählten Datensätzen Kabeltyp direkt zuweisen',
        'field': 'kabeltyp',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['objektart', 'uuid']
    map_filter_fields = {
      'uuid': 'UUID',
      'abschnitt': 'Abschnitt',
      'objektart': 'Objektart',
      'kabeltyp': 'Kabeltyp'
    }
    map_filter_fields_as_list = ['abschnitt', 'objektart', 'kabeltyp']

  def __str__(self):
    return str(self.objektart) + ' ' + str(self.pk)


#
# Parkscheinautomaten
#

class Parkscheinautomaten_Tarife(ComplexModel):
  """
  Parkscheinautomaten:
  Tarife
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  zeiten = CharField(
    verbose_name='Bewirtschaftungszeiten',
    max_length=255
  )
  normaltarif_parkdauer_min = PositiveSmallIntegerMinField(
    verbose_name='Mindestparkdauer Normaltarif',
    min_value=1
  )
  normaltarif_parkdauer_min_einheit = ForeignKey(
    to=Zeiteinheiten,
    verbose_name='Einheit der Mindestparkdauer Normaltarif',
    on_delete=RESTRICT,
    db_column='normaltarif_parkdauer_min_einheit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_normaltarif_parkdauer_min_einheiten'
  )
  normaltarif_parkdauer_max = PositiveSmallIntegerMinField(
    verbose_name='Maximalparkdauer Normaltarif',
    min_value=1
  )
  normaltarif_parkdauer_max_einheit = ForeignKey(
    to=Zeiteinheiten,
    verbose_name='Einheit der Maximalparkdauer Normaltarif',
    on_delete=RESTRICT,
    db_column='normaltarif_parkdauer_max_einheit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_normaltarif_parkdauer_max_einheiten'
  )
  normaltarif_gebuehren_max = DecimalField(
    verbose_name='Maximalgebühren Normaltarif (in €)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Maximalgebühren Normaltarif</strong></em> müssen mindestens 0,'
        '01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Maximalgebühren Normaltarif</em></strong> dürfen höchstens 99,'
        '99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  normaltarif_gebuehren_pro_stunde = DecimalField(
    verbose_name='Gebühren pro Stunde Normaltarif (in €)',
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
    verbose_name='Gebührenschritte Normaltarif', max_length=255,
    blank=True,
    null=True
  )
  veranstaltungstarif_parkdauer_min = PositiveSmallIntegerMinField(
    verbose_name='Mindestparkdauer Veranstaltungstarif', min_value=1,
    blank=True,
    null=True
  )
  veranstaltungstarif_parkdauer_min_einheit = ForeignKey(
    to=Zeiteinheiten,
    verbose_name='Einheit der Mindestparkdauer Veranstaltungstarif',
    on_delete=SET_NULL,
    db_column='veranstaltungstarif_parkdauer_min_einheit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_veranstaltungstarif_parkdauer_min_einheiten',
    blank=True,
    null=True
  )
  veranstaltungstarif_parkdauer_max = PositiveSmallIntegerMinField(
    verbose_name='Maximalparkdauer Veranstaltungstarif', min_value=1,
    blank=True,
    null=True
  )
  veranstaltungstarif_parkdauer_max_einheit = ForeignKey(
    to=Zeiteinheiten,
    verbose_name='Einheit der Maximalparkdauer Veranstaltungstarif',
    on_delete=SET_NULL,
    db_column='veranstaltungstarif_parkdauer_max_einheit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_veranstaltungstarif_parkdauer_max_einheiten',
    blank=True,
    null=True
  )
  veranstaltungstarif_gebuehren_max = DecimalField(
    verbose_name='Maximalgebühren Veranstaltungstarif (in €)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Maximalgebühren Veranstaltungstarif</strong></em> müssen mindestens 0,'
        '01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Maximalgebühren Veranstaltungstarif</em></strong> dürfen höchstens 99,'
        '99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  veranstaltungstarif_gebuehren_pro_stunde = DecimalField(
    verbose_name='Gebühren pro Stunde Veranstaltungstarif (in €)',
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
    verbose_name='Gebührenschritte Veranstaltungstarif',
    max_length=255,
    blank=True,
    null=True
  )
  zugelassene_muenzen = CharField(
    verbose_name=' zugelassene Münzen',
    max_length=255
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"parkscheinautomaten_tarife_hro'
    ordering = ['bezeichnung']
    verbose_name = 'Tarif der Parkscheinautomaten'
    verbose_name_plural = 'Tarife der Parkscheinautomaten'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Tarife der Parkscheinautomaten der Hanse- und Universitätsstadt Rostock'
    associated_models = {
      'Parkscheinautomaten_Parkscheinautomaten': 'parkscheinautomaten_tarif'
    }
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'zeiten': 'Bewirtschaftungszeiten'
    }

  def __str__(self):
    return self.bezeichnung


class Parkscheinautomaten_Parkscheinautomaten(ComplexModel):
  """
  Parkscheinautomaten:
  Parkscheinautomaten
  """

  parkscheinautomaten_tarif = ForeignKey(
    to=Parkscheinautomaten_Tarife,
    verbose_name='Tarif',
    on_delete=CASCADE,
    db_column='parkscheinautomaten_tarif',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_parkscheinautomaten_tarife'
  )
  nummer = PositiveSmallIntegerField('Nummer')
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  zone = ForeignKey(
    to=Zonen_Parkscheinautomaten,
    verbose_name='Zone',
    on_delete=RESTRICT,
    db_column='zone',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zonen'
  )
  handyparkzone = PositiveIntegerRangeField(
    verbose_name='Handyparkzone',
    min_value=100000,
    max_value=999999
  )
  bewohnerparkgebiet = CharField(
    verbose_name='Bewohnerparkgebiet',
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
    verbose_name='Gerätenummer',
    max_length=8,
    validators=[
      RegexValidator(
        regex=parkscheinautomaten_geraetenummer_regex,
        message=parkscheinautomaten_geraetenummer_message
      )
    ]
  )
  inbetriebnahme = DateField(
    verbose_name='Inbetriebnahme',
    blank=True,
    null=True
  )
  e_anschluss = ForeignKey(
    to=E_Anschluesse_Parkscheinautomaten,
    verbose_name='E-Anschluss',
    on_delete=RESTRICT,
    db_column='e_anschluss',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_e_anschluesse'
  )
  stellplaetze_pkw = PositiveSmallIntegerMinField(
    verbose_name='Pkw-Stellplätze', min_value=1,
    blank=True,
    null=True
  )
  stellplaetze_bus = PositiveSmallIntegerMinField(
    verbose_name='Bus-Stellplätze', min_value=1,
    blank=True,
    null=True
  )
  haendlerkartennummer = PositiveIntegerRangeField(
    verbose_name='Händlerkartennummer',
    min_value=1000000000,
    max_value=9999999999,
    blank=True,
    null=True
  )
  laufzeit_geldkarte = DateField(
    verbose_name='Laufzeit der Geldkarte',
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"parkscheinautomaten_parkscheinautomaten_hro'
    verbose_name = 'Parkscheinautomat'
    verbose_name_plural = 'Parkscheinautomaten'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Parkscheinautomaten der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    fields_with_foreign_key_to_linkify = ['parkscheinautomaten_tarif']
    geometry_type = 'Point'
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
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'parkscheinautomaten_tarif': 'Tarif',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'zone': 'Zone'
    }
    map_filter_fields_as_list = ['parkscheinautomaten_tarif', 'zone']

  def __str__(self):
    return self.bezeichnung


#
# Punktwolken Projekte (besteht aus mehreren Punktwolken)
#

class Punktwolken_Projekte(ComplexModel):
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
  )
  beschreibung = NullTextField(
    verbose_name='Beschreibung',
    max_length=255,
    blank=True,
    null=True
  )
  projekt_update = DateTimeField(
    verbose_name='Aktualisierung',
    editable=False,
    auto_now=True,
  )
  geometrie = polygon_field
  # Project geometry results from the individual geometries of the point clouds,
  # so a project have no geometry at initialization.
  geometrie.null = True

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"punktwolken_projekte'
    verbose_name = 'Punktwolken Projekt'
    verbose_name_plural = 'Punktwolken Projekte'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    readonly_fields = ['geometrie']
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung',
      'projekt_update': 'Zuletzt aktualisiert'
    }
    list_fields_with_datetime = ['projekt_update']
    associated_models = {
      'Punktwolken': 'projekt'
    }
    geometry_type = 'Polygon'
    geometry_calculation = True

  def __str__(self):
    return self.bezeichnung


#
# Punktwolken (Punktwolken Dateien)
#

class Punktwolken(ComplexModel):
  dateiname = CharField(
    verbose_name='Dateiname',
    max_length=255
  )
  aufnahme = DateTimeField(
    verbose_name='Aufnahmezeitpunkt',
    auto_now_add=True
  )
  projekt = ForeignKey(
    to=Punktwolken_Projekte,
    verbose_name='Punktwolken Projekt',
    on_delete=CASCADE,
    db_column='punktwolken_projekte',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_punktwolken_projekte'
  )
  punktwolke = FileField(
    verbose_name='Punktwolkendatei',
    upload_to=path_and_rename(
      path=settings.PC_PATH_PREFIX_PRIVATE + 'punktwolken/',
      foreign_key_subdir_attr='projekt_id'
    ),
    storage=OverwriteStorage(path_root=settings.PC_MEDIA_ROOT),
    validators=[FileExtensionValidator(allowed_extensions=['e57', 'las', 'laz', 'xyz'])]
  )
  vc_update = DateTimeField(
    verbose_name='Zuletzt aktualisiert',
    auto_now=True
  )
  geometrie = polygon_field
  geometrie.null = True

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"punktwolken'
    verbose_name = 'Punktwolke'
    verbose_name_plural = 'Punktwolken'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Punktwolken aus LiDAR-Scans'
    list_fields = {
      'aktiv': 'aktiv?',
      'dateiname': 'Dateiname',
      'aufnahme': 'Aufnahmedatum',
      'projekt': 'Punktwolken Projekt',
      'vc_update': 'Letzte Aktualisierung',
    }
    list_fields_with_datetime = ['aufnahme', 'vc_update']
    list_fields_with_foreign_key = {
      'projekt': 'bezeichnung'
    }
    fields_with_foreign_key_to_linkify = ['projekt']
    geometry_type = 'Polygon'
    geometry_calculation = True
    not_listed = True

  def __str__(self):
    if self.aufnahme:
      aufnahme_str = ' vom ' + self.aufnahme.strftime('%d.%m.%Y %H:%M')
    else:
      aufnahme_str = ''
    return self.dateiname + aufnahme_str

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )


post_delete.connect(delete_pointcloud, sender=Punktwolken)


class RSAG_Gleise(ComplexModel):
  """
  RSAG: Gleise
  """
  quelle = CharField(
    verbose_name='Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = line_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"rsag_gleise_hro'
    verbose_name = 'RSAG-Gleis'
    verbose_name_plural = 'RSAG-Gleise'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Gleise innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    forms_in_high_zoom_mode = True
    forms_in_high_zoom_mode_default_aerial = True
    geometry_type = 'LineString'
    list_fields = {
      'uuid': 'UUID',
      'aktiv': 'aktiv?',
      'quelle': 'Quelle'
    }
    map_heavy_load_limit = 800
    map_filter_fields = {
      'uuid': 'UUID',
      'quelle': 'Quelle'
    }

  def __str__(self):
    return str(self.uuid)


class RSAG_Masten(ComplexModel):
  """
  RSAG:
  Masten
  """

  mastnummer = CharField(
    verbose_name='Mastnummer',
    max_length=255,
    validators=standard_validators
  )
  moment_am_fundament = DecimalField(
    verbose_name='Moment am Fundament (in kNm)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Moment am Fundament</em></strong> muss mindestens 0,01 kNm betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Der <strong><em>Moment am Fundament</em></strong> darf höchstens 999,99 kNm betragen.'
      )
    ],
    blank=True,
    null=True
  )
  spitzenzug_errechnet = DecimalField(
    verbose_name='Spitzenzug P - Errechnet (in kN)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Spitzenzug P</em></strong> muss mindestens 0,01 kN betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der <strong><em>Spitzenzug P</em></strong> darf höchstens 99,99 kN betragen.'
      )
    ],
    blank=True,
    null=True
  )
  spitzenzug_gewaehlt = DecimalField(
    verbose_name='Spitzenzug P - Gewählt (in kN)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Spitzenzug P</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der <strong><em>Spitzenzug P</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  gesamtlaenge = DecimalField(
    verbose_name='Gesamtlänge L (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gesamtlänge L</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Gesamtlänge L</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  einsatztiefe = DecimalField(
    verbose_name='Einsatztiefe T (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Einsatztiefe T</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Einsatztiefe T</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  so_bis_fundament = DecimalField(
    verbose_name='Schienenoberkante bis Fundament e (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('-1.00'),
        'Die <strong><em>Höhendifferenz zwischen Schienenoberkante und Fundament '
        'e</em></strong> muss mindestens -1,00 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Höhendifferenz zwischen Schienenoberkante und Fundament '
        'e</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  boeschung = DecimalField(
    verbose_name='Böschungshöhe z (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Böschungshöhe z</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Böschungshöhe z</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  freie_laenge = DecimalField(
    verbose_name=' freie Länge H (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>freie Länge H</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>freie Länge H</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  masttyp = ForeignKey(
    to=Masttypen_RSAG,
    verbose_name='Masttyp',
    on_delete=RESTRICT,
    db_column='masttyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_masttypen'
  )
  nennmass_ueber_so = PositiveSmallIntegerRangeField(
    verbose_name='Nennmaß über Schienenoberkante (in mm)',
    min_value=1,
    blank=True,
    null=True
  )
  mastgewicht = PositiveSmallIntegerRangeField(
    verbose_name='Mastgewicht (in kg)',
    min_value=1,
    blank=True,
    null=True
  )
  fundamenttyp = ForeignKey(
    to=Fundamenttypen_RSAG,
    verbose_name='Fundamenttyp',
    on_delete=SET_NULL,
    db_column='fundamenttyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_fundamenttypen',
    blank=True,
    null=True
  )
  fundamentlaenge = DecimalField(
    verbose_name='Länge des Fundamentes t (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Länge des Fundaments t</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Länge des Fundaments t</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  fundamentdurchmesser = CharField(
    verbose_name='Durchmesser des Fundaments',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  nicht_tragfaehiger_boden = DecimalField(
    verbose_name='Tiefe des nicht tragfähiger Boden (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.00'),
        'Die <strong><em>Tiefe des nicht tragfähigen Bodens</em></strong> muss mindestens 0,'
        '00 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Tiefe des nicht tragfähigen Bodens</em></strong> darf höchstens 99,'
        '99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  mastkennzeichen_1 = ForeignKey(
    to=Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 1',
    on_delete=SET_NULL,
    db_column='mastkennzeichen_1',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_mastkennzeichen_1',
    blank=True,
    null=True
  )
  mastkennzeichen_2 = ForeignKey(
    to=Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 2',
    on_delete=SET_NULL,
    db_column='mastkennzeichen_2',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_mastkennzeichen_2',
    blank=True,
    null=True
  )
  mastkennzeichen_3 = ForeignKey(
    to=Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 3',
    on_delete=SET_NULL,
    db_column='mastkennzeichen_3',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_mastkennzeichen_3',
    blank=True,
    null=True
  )
  mastkennzeichen_4 = ForeignKey(
    to=Mastkennzeichen_RSAG,
    verbose_name='Mastkennzeichen 4',
    on_delete=SET_NULL,
    db_column='mastkennzeichen_4',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_mastkennzeichen_4',
    blank=True,
    null=True
  )
  quelle = CharField(
    verbose_name='Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  dgm_hoehe = DecimalField(
    verbose_name='Höhenwert des Durchstoßpunktes auf dem DGM (in m)',
    max_digits=5,
    decimal_places=2,
    blank=True,
    null=True,
    editable=False
  )
  geometrie = point_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"rsag_masten_hro'
    ordering = ['mastnummer']
    verbose_name = 'RSAG-Mast'
    verbose_name_plural = 'RSAG-Masten'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Masten innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    default_overlays = ['RSAG_Masten']
    forms_in_high_zoom_mode = True
    forms_in_high_zoom_mode_default_aerial = True
    associated_models = {
      'RSAG_Quertraeger': 'mast',
      'RSAG_Spanndraehte': 'mast'
    }
    geometry_type = 'Point'
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
    list_fields_with_decimal = ['gesamtlaenge']
    list_fields_with_foreign_key = {
      'masttyp': 'typ',
      'fundamenttyp': 'typ',
      'mastkennzeichen_1': 'kennzeichen',
      'mastkennzeichen_2': 'kennzeichen',
      'mastkennzeichen_3': 'kennzeichen',
      'mastkennzeichen_4': 'kennzeichen'
    }
    map_feature_tooltip_fields = ['mastnummer']
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

  def __str__(self):
    return self.mastnummer


class RSAG_Leitungen(ComplexModel):
  """
  RSAG:
  Oberleitungen
  """

  geometrie = line_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"rsag_leitungen_hro'
    verbose_name = 'RSAG-Oberleitung'
    verbose_name_plural = 'RSAG-Oberleitungen'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Oberleitungen innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    forms_in_high_zoom_mode = True
    forms_in_high_zoom_mode_default_aerial = True
    geometry_type = 'LineString'
    list_fields = {
      'uuid': 'UUID',
      'aktiv': 'aktiv?'
    }
    map_filter_fields = {
      'uuid': 'UUID'
    }

  def __str__(self):
    return str(self.uuid)


class RSAG_Quertraeger(ComplexModel):
  """
  RSAG:
  Querträger
  """

  mast = ForeignKey(
    to=RSAG_Masten,
    verbose_name='Mast',
    on_delete=RESTRICT,
    db_column='mast',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_masten'
  )
  quelle = CharField(
    verbose_name='Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = line_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"rsag_quertraeger_hro'
    verbose_name = 'RSAG-Querträger'
    verbose_name_plural = 'RSAG-Querträger'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Querträger innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    forms_in_high_zoom_mode = True
    forms_in_high_zoom_mode_default_aerial = True
    fields_with_foreign_key_to_linkify = ['mast']
    geometry_type = 'LineString'
    list_fields = {
      'uuid': 'UUID',
      'aktiv': 'aktiv?',
      'mast': 'Mast',
      'quelle': 'Quelle'
    }
    list_fields_with_foreign_key = {
      'mast': 'mastnummer'
    }
    map_filter_fields = {
      'uuid': 'UUID',
      'mast': 'Mast',
      'quelle': 'Quelle'
    }
    map_filter_fields_as_list = ['mast']

  def __str__(self):
    return str(self.uuid)


class RSAG_Spanndraehte(ComplexModel):
  """
  RSAG:
  Spanndrähte
  """

  mast = ForeignKey(
    to=RSAG_Masten,
    verbose_name='Mast',
    on_delete=SET_NULL,
    db_column='mast',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_masten',
    blank=True,
    null=True
  )
  quelle = CharField(
    verbose_name='Quelle',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = line_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"rsag_spanndraehte_hro'
    verbose_name = 'RSAG-Spanndraht'
    verbose_name_plural = 'RSAG-Spanndrähte'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Spanndrähte innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    forms_in_high_zoom_mode = True
    forms_in_high_zoom_mode_default_aerial = True
    fields_with_foreign_key_to_linkify = ['mast']
    geometry_type = 'LineString'
    list_fields = {
      'uuid': 'UUID',
      'aktiv': 'aktiv?',
      'mast': 'Mast',
      'quelle': 'Quelle'
    }
    list_fields_with_foreign_key = {
      'mast': 'mastnummer'
    }
    map_filter_fields = {
      'uuid': 'UUID',
      'mast': 'Mast',
      'quelle': 'Quelle'
    }
    map_filter_fields_as_list = ['mast']

  def __str__(self):
    return str(self.uuid)


#
# Spielplätze
#

class Spielplaetze(ComplexModel):
  """
  Spielplätze:
  Spielplätze
  """

  gruenpflegeobjekt = ForeignKey(
    to=Gruenpflegeobjekte,
    verbose_name='Grünpflegeobjekt',
    on_delete=SET_NULL,
    db_column='gruenpflegeobjekt',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gruenpflegeobjekte',
    blank=True,
    null=True
  )
  staedtisch = BooleanField(
    verbose_name=' städtisch?',
    default=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  bodenarten = ChoiceArrayField(
    CharField(
      verbose_name='Bodenarten',
      max_length=255,
      choices=()
    ),
    verbose_name='Bodenarten',
    blank=True,
    null=True
  )
  spielgeraete = ChoiceArrayField(
    CharField(
      verbose_name='Spielgeräte',
      max_length=255,
      choices=()
    ),
    verbose_name='Spielgeräte',
    blank=True,
    null=True
  )
  besonderheiten = ChoiceArrayField(
    CharField(
      verbose_name='Besonderheiten',
      max_length=255,
      choices=()
    ),
    verbose_name='Besonderheiten',
    blank=True,
    null=True
  )
  spielplatz = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False
  )
  geometrie = point_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"spielplaetze_hro'
    ordering = ['staedtisch', 'gruenpflegeobjekt', 'bezeichnung']
    verbose_name = 'Spielplatz'
    verbose_name_plural = 'Spielplätze'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Spielplätze in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'bodenarten': 'Bodenarten_Spielplaetze',
      'spielgeraete': 'Spielgeraete',
      'besonderheiten': 'Besonderheiten_Spielplaetze'
    }
    associated_models = {
      'Spielplaetze_Fotos': 'spielplatz'
    }
    fields_with_foreign_key_to_linkify = ['gruenpflegeobjekt']
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'gruenpflegeobjekt': 'Grünpflegeobjekt',
      'staedtisch': 'städtisch?',
      'bezeichnung': 'Bezeichnung',
      'bodenarten': 'Bodenarten',
      'spielgeraete': 'Spielgeräte',
      'besonderheiten': 'Besonderheiten'
    }
    list_fields_with_foreign_key = {
      'gruenpflegeobjekt': 'gruenpflegeobjekt'
    }
    map_feature_tooltip_fields = ['gruenpflegeobjekt', 'bezeichnung']
    map_filter_fields = {
      'gruenpflegeobjekt': 'Grünpflegeobjekt',
      'staedtisch': 'städtisch?',
      'bezeichnung': 'Bezeichnung',
      'bodenarten': 'Bodenarten',
      'spielgeraete': 'Spielgeräte',
      'besonderheiten': 'Besonderheiten'
    }
    map_filter_fields_as_list = ['gruenpflegeobjekt']

  def string_representation(self):
    gruenpflegeobjekt_str = str(self.gruenpflegeobjekt) + ', ' if self.gruenpflegeobjekt else ''
    bezeichnung_str = self.bezeichnung + ', ' if self.bezeichnung else ''
    staedtisch_str = 'städtisch' if self.staedtisch else 'nicht städtisch'
    return gruenpflegeobjekt_str + bezeichnung_str + staedtisch_str

  def __str__(self):
    return self.string_representation()

  def save(self, force_insert=False, force_update=False, using=None, update_fields=None, **kwargs):
    # store search content in designated field
    self.spielplatz = self.string_representation()
    super().save(
      force_insert=force_insert,
      force_update=force_update,
      using=using,
      update_fields=update_fields
    )


class Spielplaetze_Fotos(ComplexModel):
  """
  Spielplätze:
  Fotos
  """

  spielplatz = ForeignKey(
    to=Spielplaetze,
    verbose_name='Spielplatz',
    on_delete=CASCADE,
    db_column='spielplatz',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_spielplaetze'
  )
  oeffentlich_sichtbar = BooleanField(
    verbose_name=' öffentlich sichtbar?',
    default=True
  )
  aufnahmedatum = DateField(
    verbose_name='Aufnahmedatum',
    default=date.today,
    blank=True,
    null=True
  )
  bemerkungen = NullTextField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  dateiname_original = CharField(
    verbose_name='Original-Dateiname',
    max_length=255,
    default='ohne'
  )
  foto = ImageField(
    verbose_name='Foto(s)',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC + 'spielplaetze'
    ),
    max_length=255
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"spielplaetze_fotos_hro'
    verbose_name = 'Foto des Spielplatzes'
    verbose_name_plural = 'Fotos der Spielplätze'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Fotos der Spielplätze in der Hanse- und Universitätsstadt Rostock'
    short_name = 'Foto'
    readonly_fields = ['dateiname_original']
    fields_with_foreign_key_to_linkify = ['spielplatz']
    multi_photos = True
    list_fields = {
      'aktiv': 'aktiv?',
      'spielplatz': 'Spielplatz',
      'oeffentlich_sichtbar': 'öffentlich sichtbar?',
      'aufnahmedatum': 'Aufnahmedatum',
      'bemerkungen': 'Bemerkungen',
      'dateiname_original': 'Original-Dateiname',
      'foto': 'Foto'
    }
    list_fields_with_foreign_key = {
      'spielplatz': 'spielplatz'
    }
    list_fields_with_date = ['aufnahmedatum']
    list_actions_assign = [
      {
        'action_name': 'spielplaetze_fotos-aufnahmedatum',
        'action_title': 'ausgewählten Datensätzen Aufnahmedatum direkt zuweisen',
        'field': 'aufnahmedatum',
        'type': 'date'
      }
    ]

  def __str__(self):
    if self.oeffentlich_sichtbar:
      oeffentlich_sichtbar_str = ' (öffentlich sichtbar)'
    else:
      oeffentlich_sichtbar_str = ' (nicht öffentlich sichtbar)'
    if self.aufnahmedatum:
      aufnahmedatum_str = ' mit Aufnahmedatum ' + datetime.strptime(
        str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')
    else:
      aufnahmedatum_str = ''
    return str(self.spielplatz) + aufnahmedatum_str + oeffentlich_sichtbar_str


post_save.connect(photo_post_processing, sender=Spielplaetze_Fotos)

post_delete.connect(delete_photo, sender=Spielplaetze_Fotos)


#
# Straßenreinigung
#

class Strassenreinigung(ComplexModel):
  """
  Straßenreinigung:
  Straßenreinigung
  """

  id = CharField(
    verbose_name='ID',
    max_length=14,
    default='0000000000-000'
  )
  gemeindeteil = ForeignKey(
    to=Gemeindeteile,
    verbose_name='Gemeindeteil',
    on_delete=RESTRICT,
    db_column='gemeindeteil',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gemeindeteile',
    default='00000000-0000-0000-0000-000000000000'
  )
  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True
  )
  inoffizielle_strasse = ForeignKey(
    to=Inoffizielle_Strassen,
    verbose_name=' inoffizielle Straße',
    on_delete=SET_NULL,
    db_column='inoffizielle_strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_inoffizielle_strassen',
    blank=True,
    null=True
  )
  beschreibung = CharField(
    verbose_name='Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  ausserhalb = BooleanField(' außerhalb geschlossener Ortslage?')
  reinigungsklasse = ForeignKey(
    to=Reinigungsklassen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsklasse',
    on_delete=SET_NULL,
    db_column='reinigungsklasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_reinigungsklassen',
    blank=True,
    null=True
  )
  reinigungsrhythmus = ForeignKey(
    to=Reinigungsrhythmen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsrhythmus',
    on_delete=SET_NULL,
    db_column='reinigungsrhythmus',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_reinigungsrhythmen',
    blank=True,
    null=True
  )
  fahrbahnwinterdienst = ForeignKey(
    to=Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO,
    verbose_name='Fahrbahnwinterdienst',
    on_delete=SET_NULL,
    db_column='fahrbahnwinterdienst',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_fahrbahnwinterdienste',
    blank=True,
    null=True
  )
  laenge = DecimalField(
    verbose_name='Länge (in m)',
    max_digits=7,
    decimal_places=2,
    default=0
  )
  geometrie = multiline_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten_strassenbezug\".\"strassenreinigung_hro'
    ordering = ['id']
    verbose_name = 'Straßenreinigung'
    verbose_name_plural = 'Straßenreinigung'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Straßenreinigung der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    associated_models = {
      'Strassenreinigung_Flaechen': 'strassenreinigung'
    }
    readonly_fields = ['id', 'gemeindeteil', 'laenge']
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'MultiLineString'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'gemeindeteil': 'Gemeindeteil',
      'strasse': 'Straße',
      'inoffizielle_strasse': 'inoffizielle Straße',
      'beschreibung': 'Beschreibung',
      'ausserhalb': 'außerhalb geschlossener Ortslage?',
      'reinigungsklasse': 'Reinigungsklasse',
      'reinigungsrhythmus': 'Reinigungsrhythmus',
      'fahrbahnwinterdienst': 'Fahrbahnwinterdienst',
      'laenge': 'Länge (in m)'
    }
    list_fields_with_decimal = ['laenge']
    list_fields_with_foreign_key = {
      'gemeindeteil': 'gemeindeteil',
      'strasse': 'strasse',
      'inoffizielle_strasse': 'strasse',
      'reinigungsklasse': 'code',
      'reinigungsrhythmus': 'reinigungsrhythmus',
      'fahrbahnwinterdienst': 'code'
    }
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'id': 'ID',
      'gemeindeteil': 'Gemeindeteil',
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
      'gemeindeteil',
      'inoffizielle_strasse',
      'reinigungsklasse',
      'reinigungsrhythmus',
      'fahrbahnwinterdienst'
    ]
    additional_wms_layers = [
      {
        'title': 'Reinigungsreviere',
        'url': 'https://geo.sv.rostock.de/geodienste/reinigungsreviere/wms',
        'layers': 'hro.reinigungsreviere.reinigungsreviere'
      }, {
        'title': 'Geh- und Radwegereinigung',
        'url': 'https://geo.sv.rostock.de/geodienste/geh_und_radwegereinigung/wms',
        'layers': 'hro.geh_und_radwegereinigung.geh_und_radwegereinigung'
      }, {
        'title': 'Straßenreinigung',
        'url': 'https://geo.sv.rostock.de/geodienste/strassenreinigung/wms',
        'layers': 'hro.strassenreinigung.strassenreinigung'
      }
    ]

  def __str__(self):
    return str(self.id) + (', ' + str(self.beschreibung) if self.beschreibung else '') + \
      (', außerhalb geschlossener Ortslage' if self.ausserhalb else '') + \
      (', Reinigungsklasse ' + str(self.reinigungsklasse) if self.reinigungsklasse else '') + \
      (', Fahrbahnwinterdienst ' +
       str(self.fahrbahnwinterdienst) if self.fahrbahnwinterdienst else '') + \
      (' [Straße: ' + str(self.strasse) + ']' if self.strasse else '') + \
      (' [inoffizielle Straße: ' +
       str(self.inoffizielle_strasse) + ']' if self.inoffizielle_strasse else '')


class Strassenreinigung_Flaechen(ComplexModel):
  """
  Straßenreinigung:
  Flächen
  """

  strassenreinigung = ForeignKey(
    to=Strassenreinigung,
    verbose_name='Straßenreinigung',
    on_delete=CASCADE,
    db_column='strassenreinigung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassenreinigung'
  )
  geometrie = multipolygon_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"strassenreinigung_flaechen_hro'
    verbose_name = 'Fläche zur Straßenreinigung'
    verbose_name_plural = 'Flächen zur Straßenreinigung'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Flächen zur Straßenreinigung der Hanse- und Universitätsstadt Rostock'
    short_name = 'Fläche'
    as_overlay = True
    fields_with_foreign_key_to_linkify = ['strassenreinigung']
    geometry_type = 'MultiPolygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'strassenreinigung': 'Straßenreinigung'
    }
    list_fields_with_foreign_key = {
      'strassenreinigung': 'id'
    }
    map_feature_tooltip_fields = ['strassenreinigung']

  def __str__(self):
    return str(self.strassenreinigung)


#
# Straßen
#

class Strassen_Simple(ComplexModel):
  """
  Straßen:
  Straßen
  """

  kategorie = ForeignKey(
    to=Kategorien_Strassen,
    verbose_name='Kategorie',
    on_delete=RESTRICT,
    db_column='kategorie',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_kategorien'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  schluessel = CharField(
    verbose_name='Schlüssel',
    max_length=5,
    unique=True,
    validators=[
      RegexValidator(
        regex=strassen_schluessel_regex,
        message=strassen_schluessel_message
      )
    ]
  )
  geometrie = multiline_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"strassen_hro'
    ordering = ['bezeichnung', 'schluessel']
    verbose_name = 'Straße'
    verbose_name_plural = 'Straßen'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Straßen in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    forms_in_mobile_mode = True
    associated_models = {
      'Strassen_Simple_Historie': 'strasse_simple',
      'Strassen_Simple_Namensanalyse': 'strasse_simple'
    }
    geometry_type = 'MultiLineString'
    list_fields = {
      'aktiv': 'aktiv?',
      'kategorie': 'Kategorie',
      'bezeichnung': 'Bezeichnung',
      'schluessel': 'Schlüssel'
    }
    list_fields_with_foreign_key = {
      'kategorie': 'code'
    }
    list_actions_assign = [
      {
        'action_name': 'strassen_simple-kategorie',
        'action_title': 'ausgewählten Datensätzen Kategorie direkt zuweisen',
        'field': 'kategorie',
        'type': 'foreignkey'
      }
    ]
    map_heavy_load_limit = 600
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'kategorie': 'Kategorie',
      'bezeichnung': 'Bezeichnung',
      'schluessel': 'Schlüssel'
    }
    map_filter_fields_as_list = ['kategorie']
    additional_wms_layers = [
      {
        'title': 'Eigentum HRO',
        'url': 'https://geo.sv.rostock.de/geodienste/eigentum_hro/wms',
        'layers': 'hro.eigentum_hro.eigentum_hro_hro',
        'proxy': True
      }, {
        'title': 'Bewirtschaftungskataster',
        'url': 'https://geo.sv.rostock.de/geodienste/bewirtschaftungskataster/wms',
        'layers': 'hro.bewirtschaftungskataster.bewirtschaftungskataster'
      }, {
        'title': 'Grundvermögen: Flächen in Abstimmung',
        'url': 'https://geo.sv.rostock.de/geodienste/grundvermoegen/wms',
        'layers': 'hro.grundvermoegen.flaechen_in_abstimmung',
        'proxy': True
      }, {
        'title': 'Grundvermögen: Realnutzungsarten',
        'url': 'https://geo.sv.rostock.de/geodienste/grundvermoegen/wms',
        'layers': 'hro.grundvermoegen.realnutzungsarten',
        'proxy': True
      }, {
        'title': 'Liegenschaftsverwaltung: An- und Verkauf',
        'url': 'https://geo.sv.rostock.de/geodienste/liegenschaftsverwaltung/wms',
        'layers': 'hro.liegenschaftsverwaltung.anundverkauf',
        'proxy': True
      }, {
        'title': 'Liegenschaftsverwaltung: Mieten und Pachten',
        'url': 'https://geo.sv.rostock.de/geodienste/liegenschaftsverwaltung/wms',
        'layers': 'hro.liegenschaftsverwaltung.mieten_pachten',
        'proxy': True
      }, {
        'title': 'Flurstücke',
        'url': 'https://geo.sv.rostock.de/geodienste/flurstuecke_hro/wms',
        'layers': 'hro.flurstuecke.flurstuecke'
      }, {
        'title': 'Straßenwidmungen',
        'url': 'https://geo.sv.rostock.de/geodienste/strassenwidmungen/wms',
        'layers': 'hro.strassenwidmungen.strassenwidmungen',
        'proxy': True
      }, {
        'title': 'Adressen',
        'url': 'https://geo.sv.rostock.de/geodienste/adressen/wms',
        'layers': 'hro.adressen.adressen'
      }
    ]
    additional_wfs_featuretypes = [
      {
        'name': 'eigentum_hro',
        'title': 'Eigentum HRO',
        'url': 'https://geo.sv.rostock.de/geodienste/eigentum_hro/wfs',
        'featuretypes': 'hro.eigentum_hro.eigentum_hro_hro',
        'proxy': True
      }, {
        'name': 'flurstuecke',
        'title': 'Flurstücke',
        'url': 'https://geo.sv.rostock.de/geodienste/flurstuecke_hro/wfs',
        'featuretypes': 'hro.flurstuecke.flurstuecke',
        'proxy': True
      }
    ]

  def __str__(self):
    return self.bezeichnung + ' (' + self.schluessel + ')'


class Strassen_Simple_Historie(ComplexModel):
  """
  Straßen:
  Historie
  """

  strasse_simple = ForeignKey(
    to=Strassen_Simple,
    verbose_name='Straße',
    on_delete=CASCADE,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strasse'
  )
  datum = CharField(
    verbose_name='Datum',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  beschluss = CharField(
    verbose_name='Beschluss',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  veroeffentlichung = CharField(
    verbose_name='Veröffentlichung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  historie = CharField(
    verbose_name='Historie',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"strassen_historie_hro'
    verbose_name = 'Historie zu einer Straße'
    verbose_name_plural = 'Historie zu Straßen'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Historie zu Straßen in der Hanse- und Universitätsstadt Rostock'
    short_name = 'Historie'
    fields_with_foreign_key_to_linkify = ['strasse_simple']
    list_fields = {
      'aktiv': 'aktiv?',
      'strasse_simple': 'Straße',
      'datum': 'Datum',
      'beschluss': 'Beschluss',
      'veroeffentlichung': 'Veröffentlichung',
      'historie': 'Historie'
    }
    list_fields_with_foreign_key = {
      'strasse_simple': 'bezeichnung'
    }
    list_additional_foreign_key_field = {
      'insert_after_field': 'strasse_simple',
      'insert_as': 'Straßenschlüssel',
      'source_field': 'strasse_simple',
      'target_field': 'schluessel'
    }

  def __str__(self):
    return str(self.strasse_simple)


class Strassen_Simple_Namensanalyse(ComplexModel):
  """
  Straßen:
  Namensanalyse
  """

  strasse_simple = ForeignKey(
    to=Strassen_Simple,
    verbose_name='Straße',
    on_delete=CASCADE,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strasse'
  )
  person_weiblich = BooleanField(
    verbose_name='Person weiblich?',
    blank=True,
    null=True
  )
  person_maennlich = BooleanField(
    verbose_name='Person männlich?',
    blank=True,
    null=True
  )
  beruf = BooleanField(
    verbose_name='Beruf?',
    blank=True,
    null=True
  )
  literatur = BooleanField(
    verbose_name=' literarische(r) Figur oder Begriff?',
    blank=True,
    null=True
  )
  historisch = BooleanField(
    verbose_name=' historischer Begriff?',
    blank=True,
    null=True
  )
  flora_fauna = BooleanField(
    verbose_name='Eigenname aus der Natur?',
    blank=True,
    null=True
  )
  orte_landschaften = BooleanField(
    verbose_name='Eigenname von Orten oder Landschaften?',
    blank=True,
    null=True
  )
  gesellschaft = BooleanField(
    verbose_name='Begriff gesellschaftlicher Werte?',
    blank=True,
    null=True
  )
  lagehinweis = BooleanField(
    verbose_name='Lagehinweis?',
    blank=True,
    null=True
  )
  religion = BooleanField(
    verbose_name=' religiöse(r) Figur oder Begriff?',
    blank=True,
    null=True
  )
  niederdeutsch = BooleanField(
    verbose_name=' niederdeutscher Begriff?',
    blank=True,
    null=True
  )
  erlaeuterungen_intern = NullTextField(
    verbose_name='Erläuterungen (intern)',
    max_length=1000,
    blank=True,
    null=True,
    validators=standard_validators
  )
  erlaeuterungen_richter = NullTextField(
    verbose_name='Erläuterungen (J. Richter)',
    max_length=1000,
    blank=True,
    null=True,
    validators=standard_validators
  )
  wikipedia = CharField(
    verbose_name='Link auf Wikipedia',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=wikipedia_regex,
        message=wikipedia_message
      )
    ]
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"strassen_namensanalye_hro'
    verbose_name = 'Namensanalyse zu einer Straße'
    verbose_name_plural = 'Namensanalyse zu Straßen'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Namensanalyse zu Straßen in der Hanse- und Universitätsstadt Rostock'
    short_name = 'Namensanalyse'
    fields_with_foreign_key_to_linkify = ['strasse_simple']
    list_fields = {
      'aktiv': 'aktiv?',
      'strasse_simple': 'Straße',
      'person_weiblich': 'Person weiblich?',
      'person_maennlich': 'Person männlich?',
      'beruf': 'Beruf?',
      'literatur': 'literarische(r) Figur oder Begriff?',
      'historisch': 'historischer Begriff?',
      'flora_fauna': 'Eigenname aus der Natur?',
      'orte_landschaften': 'Eigenname von Orten oder Landschaften?',
      'gesellschaft': 'Begriff gesellschaftlicher Werte?',
      'lagehinweis': 'Lagehinweis?',
      'religion': 'religiöse(r) Figur oder Begriff?',
      'niederdeutsch': 'niederdeutscher Begriff?',
      'erlaeuterungen_intern': 'Erläuterungen (intern)',
      'erlaeuterungen_richter': 'Erläuterungen (J. Richter)',
      'wikipedia': 'Link auf Wikipedia'
    }
    list_fields_with_foreign_key = {
      'strasse_simple': 'bezeichnung'
    }
    list_additional_foreign_key_field = {
      'insert_after_field': 'strasse_simple',
      'insert_as': 'Straßenschlüssel',
      'source_field': 'strasse_simple',
      'target_field': 'schluessel'
    }

  def __str__(self):
    return str(self.strasse_simple)


#
# UVP
#

class UVP_Vorhaben(ComplexModel):
  """
  UVP:
  Vorhaben
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  vorgangsart = ForeignKey(
    to=Vorgangsarten_UVP_Vorhaben,
    verbose_name='Vorgangsart',
    on_delete=RESTRICT,
    db_column='vorgangsart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_vorgangsarten'
  )
  genehmigungsbehoerde = ForeignKey(
    to=Genehmigungsbehoerden_UVP_Vorhaben,
    verbose_name='Genehmigungsbehörde',
    on_delete=RESTRICT,
    db_column='genehmigungsbehoerde',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_genehmigungsbehoerden'
  )
  datum_posteingang_genehmigungsbehoerde = DateField(
    verbose_name='Datum des Posteingangs bei der Genehmigungsbehörde'
  )
  registriernummer_bauamt = CharField(
    verbose_name='Registriernummer des Bauamtes',
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
    verbose_name='Aktenzeichen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  rechtsgrundlage = ForeignKey(
    to=Rechtsgrundlagen_UVP_Vorhaben,
    verbose_name='Rechtsgrundlage',
    on_delete=RESTRICT,
    db_column='rechtsgrundlage',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_rechtsgrundlagen'
  )
  typ = ForeignKey(
    to=Typen_UVP_Vorhaben,
    verbose_name='Typ',
    on_delete=RESTRICT,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen'
  )
  geometrie = polygon_field

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"uvp_vorhaben_hro'
    ordering = ['bezeichnung']
    verbose_name = 'UVP-Vorhaben'
    verbose_name_plural = 'UVP-Vorhaben'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Vorhaben, auf die sich Vorprüfungen der Hanse- und Universitätsstadt Rostock ' \
                  'zur Feststellung der UVP-Pflicht gemäß UVPG und LUVPG M-V beziehen'
    as_overlay = True
    associated_models = {
      'UVP_Vorpruefungen': 'uvp_vorhaben'
    }
    geometry_type = 'Polygon'
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
    list_fields_with_date = ['datum_posteingang_genehmigungsbehoerde']
    list_fields_with_foreign_key = {
      'vorgangsart': 'vorgangsart',
      'genehmigungsbehoerde': 'genehmigungsbehoerde',
      'rechtsgrundlage': 'rechtsgrundlage',
      'typ': 'typ'
    }
    map_feature_tooltip_fields = ['bezeichnung']
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

  def __str__(self):
    return self.bezeichnung


class UVP_Vorpruefungen(ComplexModel):
  """
  UVP:
  Vorprüfungen
  """

  uvp_vorhaben = ForeignKey(
    to=UVP_Vorhaben,
    verbose_name='Vorhaben',
    on_delete=CASCADE,
    db_column='uvp_vorhaben',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_uvp_vorhaben'
  )
  art = ForeignKey(
    to=Arten_UVP_Vorpruefungen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  datum_posteingang = DateField('Datum des Posteingangs')
  datum = DateField(
    verbose_name='Datum',
    default=date.today
  )
  ergebnis = ForeignKey(
    to=Ergebnisse_UVP_Vorpruefungen,
    verbose_name='Ergebnis',
    on_delete=RESTRICT,
    db_column='ergebnis',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ergebnisse'
  )
  datum_bekanntmachung = DateField(
    verbose_name='Datum Bekanntmachung „Städtischer Anzeiger“',
    blank=True,
    null=True
  )
  datum_veroeffentlichung = DateField(
    verbose_name='Datum Veröffentlichung UVP-Portal',
    blank=True,
    null=True
  )
  pruefprotokoll = CharField(
    verbose_name='Prüfprotokoll',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )

  class Meta(ComplexModel.Meta):
    db_table = 'fachdaten\".\"uvp_vorpruefungen_hro'
    verbose_name = 'UVP-Vorprüfung'
    verbose_name_plural = 'UVP-Vorprüfungen'

  class BasemodelMeta(ComplexModel.BasemodelMeta):
    description = 'Vorprüfungen der Hanse- und Universitätsstadt Rostock ' \
                  'zur Feststellung der UVP-Pflicht gemäß UVPG und LUVPG M-V'
    fields_with_foreign_key_to_linkify = ['uvp_vorhaben']
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
    list_actions_assign = [
      {
        'action_name': 'uvp_vorpruefungen-art',
        'action_title': 'ausgewählten Datensätzen Art direkt zuweisen',
        'field': 'art',
        'type': 'foreignkey'
      },
      {
        'action_name': 'uvp_vorpruefungen-datum_posteingang',
        'action_title': 'ausgewählten Datensätzen Datum des Posteingangs direkt zuweisen',
        'field': 'datum_posteingang',
        'type': 'date',
        'value_required': True
      },
      {
        'action_name': 'uvp_vorpruefungen-datum',
        'action_title': 'ausgewählten Datensätzen Datum direkt zuweisen',
        'field': 'datum',
        'type': 'date',
        'value_required': True
      },
      {
        'action_name': 'uvp_vorpruefungen-ergebnis',
        'action_title': 'ausgewählten Datensätzen Ergebnis direkt zuweisen',
        'field': 'ergebnis',
        'type': 'foreignkey'
      }
    ]

  def __str__(self):
    return str(self.uvp_vorhaben) + ' mit Datum ' + \
      datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + \
      ' [Art: ' + str(self.art) + ']'
