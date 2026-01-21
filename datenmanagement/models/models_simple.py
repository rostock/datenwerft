from datetime import date, datetime, timezone
from re import sub
from zoneinfo import ZoneInfo

from django.conf import settings
from django.core.validators import URLValidator
from django.db.models import CASCADE, SET_NULL, OneToOneField
from django.db.models.fields import DateTimeField
from django.db.models.fields.files import FileField, ImageField
from django.db.models.signals import post_delete, post_save, pre_save

from datenmanagement.utils import create_d3_link, get_current_year, path_and_rename
from toolbox.fields import NullTextField

from .base import SimpleModel
from .functions import (
  delete_pdf,
  delete_photo,
  delete_photo_after_emptied,
  photo_post_processing,
  set_pre_save_instance,
)
from .models_codelist import *
from .storage import OverwriteStorage


class Abfallbehaelter(SimpleModel):
  """
  Abfallbehälter
  """

  deaktiviert = DateField(verbose_name='Außerbetriebstellung', blank=True, null=True)
  id = CharField(verbose_name='ID', max_length=8, unique=True, default='00000000')
  typ = ForeignKey(
    to=Typen_Abfallbehaelter,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
    blank=True,
    null=True,
  )
  aufstellungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Aufstellungsjahr', max_value=get_current_year(), blank=True, null=True
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer',
  )
  bewirtschafter = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter',
  )
  pflegeobjekt = CharField(
    verbose_name='Pflegeobjekt', max_length=255, validators=standard_validators
  )
  inventarnummer = CharField(
    verbose_name='Inventarnummer',
    max_length=8,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)],
  )
  anschaffungswert = DecimalField(
    verbose_name='Anschaffungswert (in €)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.',
      ),
      MaxValueValidator(
        Decimal('9999.99'),
        'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 9.999,99 € betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  haltestelle = BooleanField(verbose_name='Lage an einer Haltestelle?', blank=True, null=True)
  leerungszeiten_sommer = ForeignKey(
    to=Leerungszeiten,
    verbose_name='Leerungszeiten im Sommer',
    on_delete=SET_NULL,
    db_column='leerungszeiten_sommer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_leerungszeiten_sommer',
    blank=True,
    null=True,
  )
  leerungszeiten_winter = ForeignKey(
    to=Leerungszeiten,
    verbose_name='Leerungszeiten im Winter',
    on_delete=SET_NULL,
    db_column='leerungszeiten_winter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_leerungszeiten_winter',
    blank=True,
    null=True,
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."abfallbehaelter_hro'
    verbose_name = 'Abfallbehälter'
    verbose_name_plural = 'Abfallbehälter'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Abfallbehälter in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['deaktiviert', 'id']
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Außerbetriebstellung',
      'id': 'ID',
      'typ': 'Typ',
      'eigentuemer': 'Eigentümer',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt',
      'leerungszeiten_sommer': 'Leerungszeiten im Sommer',
      'leerungszeiten_winter': 'Leerungszeiten im Winter',
    }
    list_fields_with_date = ['deaktiviert']
    list_fields_with_foreign_key = {
      'typ': 'typ',
      'eigentuemer': 'bezeichnung',
      'bewirtschafter': 'bezeichnung',
      'leerungszeiten_sommer': 'bezeichnung',
      'leerungszeiten_winter': 'bezeichnung',
    }
    list_actions_assign = [
      {
        'action_name': 'abfallbehaelter-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey',
      },
      {
        'action_name': 'abfallbehaelter-bewirtschafter',
        'action_title': 'ausgewählten Datensätzen Bewirtschafter direkt zuweisen',
        'field': 'bewirtschafter',
        'type': 'foreignkey',
      },
      {
        'action_name': 'abfallbehaelter-leerungszeiten_sommer',
        'action_title': 'ausgewählten Datensätzen Leerungszeiten im Sommer direkt zuweisen',
        'field': 'leerungszeiten_sommer',
        'type': 'foreignkey',
      },
      {
        'action_name': 'abfallbehaelter-leerungszeiten_winter',
        'action_title': 'ausgewählten Datensätzen Leerungszeiten im Winter direkt zuweisen',
        'field': 'leerungszeiten_winter',
        'type': 'foreignkey',
      },
    ]
    map_heavy_load_limit = 500
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'typ': 'Typ',
      'eigentuemer': 'Eigentümer',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt',
      'leerungszeiten_sommer': 'Leerungszeiten im Sommer',
      'leerungszeiten_winter': 'Leerungszeiten im Winter',
    }
    map_filter_fields_as_list = [
      'typ',
      'eigentuemer',
      'bewirtschafter',
      'leerungszeiten_sommer',
      'leerungszeiten_winter',
    ]

  def __str__(self):
    return self.id + (' [Typ: ' + str(self.typ) + ']' if self.typ else '')


class Abstellflaechen_E_Tretroller(SimpleModel):
  """
  Abstellflächen für E-Tretroller
  """

  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True,
  )
  id = CharField(verbose_name='ID', max_length=8, unique=True, default='00000000')
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  erstmarkierung = PositiveSmallIntegerMinField(verbose_name='Erstmarkierung', min_value=1)
  breite = DecimalField(
    verbose_name='Breite (in m)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Breite</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'), 'Die <strong><em>Breite</em></strong> darf höchstens 9,99 m betragen.'
      ),
    ],
  )
  laenge = DecimalField(
    verbose_name='Länge (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Länge</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'), 'Die <strong><em>Länge</em></strong> darf höchstens 99,99 m betragen.'
      ),
    ],
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'abstellflaechen_e_tretroller'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug"."abstellflaechen_e_tretroller_hro'
    verbose_name = 'Abstellfläche für E-Tretroller'
    verbose_name_plural = 'Abstellflächen für E-Tretroller'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Abstellflächen für E-Tretroller in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['id']
    address_type = 'Straße'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'lagebeschreibung': 'Lagebeschreibung',
      'erstmarkierung': 'Erstmarkierung',
      'breite': 'Breite (in m)',
      'laenge': 'Länge (in m)',
      'foto': 'Foto',
    }
    list_fields_with_decimal = ['breite', 'laenge']
    list_fields_with_foreign_key = {'strasse': 'strasse'}
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'lagebeschreibung': 'Lagebeschreibung',
      'erstmarkierung': 'Erstmarkierung',
      'breite': 'Breite (in m)',
      'laenge': 'Länge (in m)',
    }
    map_filter_fields_as_list = ['strasse']

  def __str__(self):
    return self.id


pre_save.connect(set_pre_save_instance, sender=Abstellflaechen_E_Tretroller)

post_save.connect(photo_post_processing, sender=Abstellflaechen_E_Tretroller)

post_save.connect(delete_photo_after_emptied, sender=Abstellflaechen_E_Tretroller)

post_delete.connect(delete_photo, sender=Abstellflaechen_E_Tretroller)


class Anerkennungsgebuehren_herrschend(SimpleModel):
  """
  Anerkennungsgebühren (herrschendes Flurstück)
  """

  grundbucheintrag = CharField(
    verbose_name='Grundbucheintrag',
    max_length=255,
    choices=ANERKENNUNGSGEBUEHREN_HERRSCHEND_GRUNDBUCHEINTRAG,
  )
  aktenzeichen_anerkennungsgebuehren = CharField(
    verbose_name='Aktenzeichen Anerkennungsgebühren',
    max_length=12,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=aktenzeichen_anerkennungsgebuehren_regex,
        message=aktenzeichen_anerkennungsgebuehren_message,
      )
    ],
  )
  aktenzeichen_kommunalvermoegen = CharField(
    verbose_name='Aktenzeichen Kommunalvermögen',
    max_length=10,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=aktenzeichen_kommunalvermoegen_regex, message=aktenzeichen_kommunalvermoegen_message
      )
    ],
  )
  vermoegenszuordnung_hro = BooleanField(
    verbose_name='Vermögenszuordnung der Hanse- und Universitätsstadt Rostock',
    blank=True,
    null=True,
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."anerkennungsgebuehren_herrschend_hro'
    verbose_name = 'Anerkennungsgebühr (herrschendes Flurstück)'
    verbose_name_plural = 'Anerkennungsgebühren (herrschendes Flurstück)'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = (
      'Anerkennungsgebühren (herrschendes Flurstück) der Hanse- und Universitätsstadt Rostock'
    )
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'grundbucheintrag': 'Grundbucheintrag',
      'aktenzeichen_anerkennungsgebuehren': 'Aktenzeichen Anerkennungsgebühren',
      'aktenzeichen_kommunalvermoegen': 'Aktenzeichen Kommunalvermögen',
      'vermoegenszuordnung_hro': 'Vermögenszuordnung der Hanse- und Universitätsstadt Rostock',
      'bemerkungen': 'Bemerkungen',
    }
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'grundbucheintrag': 'Grundbucheintrag',
      'aktenzeichen_anerkennungsgebuehren': 'Aktenzeichen Anerkennungsgebühren',
      'aktenzeichen_kommunalvermoegen': 'Aktenzeichen Kommunalvermögen',
      'vermoegenszuordnung_hro': 'Vermögenszuordnung der Hanse- und Universitätsstadt Rostock',
      'bemerkungen': 'Bemerkungen',
    }

  def __str__(self):
    return str(self.uuid)


class Angelverbotsbereiche(SimpleModel):
  """
  Angelverbotsbereiche
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  beschreibung = NullTextField(
    verbose_name='Beschreibung',
    max_length=1000,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = line_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."angelverbotsbereiche_hro'
    verbose_name = 'Angelverbotsbereich'
    verbose_name_plural = 'Angelverbotsbereiche'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Angelverbotsbereiche der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    geometry_type = 'LineString'
    list_fields = {'aktiv': 'aktiv?', 'bezeichnung': 'Bezeichnung', 'beschreibung': 'Beschreibung'}
    map_feature_tooltip_fields = ['bezeichnung']

  def __str__(self):
    return (self.bezeichnung if self.bezeichnung else 'ohne Bezeichnung') + (
      ' [Beschreibung: ' + str(self.beschreibung) + ']' if self.beschreibung else ''
    )


class Arrondierungsflaechen(SimpleModel):
  """
  Arrondierungsflächen
  """

  registriernummer = CharField(
    verbose_name='Registriernummer',
    max_length=6,
    validators=[
      RegexValidator(
        regex=arrondierungsflaechen_registriernummer_regex,
        message=arrondierungsflaechen_registriernummer_message,
      )
    ],
  )
  jahr = PositiveSmallIntegerRangeField(
    verbose_name='Jahr', default=get_current_year(), max_value=get_current_year()
  )
  geometrie = polygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."arrondierungsflaechen_hro'
    verbose_name = 'Arrondierungsfläche'
    verbose_name_plural = 'Arrondierungsflächen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Arrondierungsflächen in der Hanse- und Universitätsstadt Rostock'
    forms_in_high_zoom_mode = True
    geometry_type = 'Polygon'
    list_fields = {'aktiv': 'aktiv?', 'registriernummer': 'Registriernummer', 'jahr': 'Jahr'}
    map_feature_tooltip_fields = ['registriernummer']
    map_filter_fields = {'aktiv': 'aktiv?', 'registriernummer': 'Registriernummer', 'jahr': 'Jahr'}
    additional_wfs_featuretypes = [
      {
        'name': 'flurstuecke',
        'title': 'Flurstücke',
        'url': 'https://geo.sv.rostock.de/geodienste/flurstuecke_hro/wfs',
        'featuretypes': 'hro.flurstuecke.flurstuecke',
      }
    ]

  def __str__(self):
    return self.registriernummer + ' (Jahr: ' + str(self.jahr) + ')'


class Aufteilungsplaene_Wohnungseigentumsgesetz(SimpleModel):
  """
  Aufteilungspläne nach Wohnungseigentumsgesetz
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  aktenzeichen = CharField(
    verbose_name='Aktenzeichen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  datum_abgeschlossenheitserklaerung = DateField(
    verbose_name='Datum der Abgeschlossenheitserklärung', blank=True, null=True
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in', max_length=255, validators=standard_validators
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  datum = DateField(verbose_name='Datum', default=date.today)
  pdf = FileField(
    verbose_name='PDF',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PDF_PATH_PREFIX_PRIVATE + 'aufteilungsplaene_wohnungseigentumsgesetz'
    ),
    max_length=255,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."aufteilungsplaene_wohnungseigentumsgesetz_hro'
    verbose_name = 'Aufteilungsplan nach Wohnungseigentumsgesetz'
    verbose_name_plural = 'Aufteilungspläne nach Wohnungseigentumsgesetz'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = (
      'Aufteilungspläne nach Wohnungseigentumsgesetzin der Hanse- und Universitätsstadt Rostock'
    )
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'aktenzeichen': 'Aktenzeichen',
      'datum_abgeschlossenheitserklaerung': 'Datum der Abgeschlossenheitserklärung',
      'pdf': 'PDF',
      'datum': 'Datum',
    }
    list_fields_with_date = ['datum_abgeschlossenheitserklaerung', 'datum']
    list_fields_with_foreign_key = {'adresse': 'adresse'}
    list_actions_assign = [
      {
        'action_name': 'aufteilungsplaene_wohnungseigentumsgesetz-datum_abgeschlossenheitserklaerung',  # noqa: E501
        'action_title': 'ausgewählten Datensätzen Datum der Abgeschlossenheitserklärung'
        'direkt zuweisen',
        'field': 'datum_abgeschlossenheitserklaerung',
        'type': 'date',
      },
      {
        'action_name': 'aufteilungsplaene_wohnungseigentumsgesetz-datum',
        'action_title': 'ausgewählten Datensätzen Datum direkt zuweisen',
        'field': 'datum',
        'type': 'date',
        'value_required': True,
      },
    ]
    map_feature_tooltip_fields = ['datum']
    map_filter_fields = {
      'aktenzeichen': 'Aktenzeichen',
      'datum_abgeschlossenheitserklaerung': 'Datum der Abgeschlossenheitserklärung',
      'datum': 'Datum',
    }

  def __str__(self):
    return (
      'Abgeschlossenheitserklärung mit Datum '
      + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y')
      + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')
    )


post_delete.connect(delete_pdf, sender=Aufteilungsplaene_Wohnungseigentumsgesetz)


class Baudenkmale(SimpleModel):
  """
  Baudenkmale
  """

  id = PositiveIntegerField(verbose_name='ID', unique=True, default=0)
  status = ForeignKey(
    to=Status_Baudenkmale_Denkmalbereiche,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status',
  )
  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  beschreibung = CharField(
    verbose_name='Beschreibung', max_length=255, validators=standard_validators
  )
  vorherige_beschreibung = CharField(
    verbose_name=' vorherige Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  lage = CharField(
    verbose_name='Lage', max_length=255, blank=True, null=True, validators=standard_validators
  )
  unterschutzstellungen = ArrayField(
    DateField(verbose_name='Unterschutzstellungen', blank=True, null=True),
    verbose_name='Unterschutzstellungen',
    blank=True,
    null=True,
  )
  veroeffentlichungen = ArrayField(
    DateField(verbose_name='Veröffentlichungen', blank=True, null=True),
    verbose_name='Veröffentlichungen',
    blank=True,
    null=True,
  )
  denkmalnummern = ArrayField(
    CharField(
      verbose_name='Denkmalnummern',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators,
    ),
    verbose_name='Denkmalnummern',
    blank=True,
    null=True,
  )
  gartendenkmal = BooleanField(verbose_name='Gartendenkmal?')
  hinweise = NullTextField(
    verbose_name='Hinweise', max_length=500, blank=True, null=True, validators=standard_validators
  )
  aenderungen = NullTextField(
    verbose_name='Änderungen',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = nullable_multipolygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."baudenkmale_hro'
    verbose_name = 'Baudenkmal'
    verbose_name_plural = 'Baudenkmale'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Baudenkmale der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['id']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'MultiPolygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'status': 'Status',
      'adresse': 'Adresse',
      'lage': 'Lage',
      'beschreibung': 'Beschreibung',
    }
    list_fields_with_foreign_key = {'status': 'status', 'adresse': 'adresse'}
    list_actions_assign = [
      {
        'action_name': 'baudenkmale-status',
        'action_title': 'ausgewählten Datensätzen Status direkt zuweisen',
        'field': 'status',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'status': 'Status',
      'lage': 'Lage',
      'beschreibung': 'Beschreibung',
      'gartendenkmal': 'Gartendenkmal?',
    }
    map_filter_fields_as_list = ['status']
    additional_wfs_featuretypes = [
      {
        'name': 'flurstuecke',
        'title': 'Flurstücke',
        'url': 'https://geo.sv.rostock.de/geodienste/flurstuecke_hro/wfs',
        'featuretypes': 'hro.flurstuecke.flurstuecke',
      },
      {
        'name': 'gebaeude',
        'title': 'Gebäude',
        'url': 'https://geo.sv.rostock.de/geodienste/gebaeude/wfs',
        'featuretypes': 'hro.gebaeude.gebaeude',
      },
    ]

  def __str__(self):
    return self.beschreibung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Behinderteneinrichtungen(SimpleModel):
  """
  Behinderteneinrichtungen
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger',
  )
  plaetze = PositiveSmallIntegerMinField(verbose_name='Plätze', min_value=1, blank=True, null=True)
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."behinderteneinrichtungen_hro'
    verbose_name = 'Behinderteneinrichtung'
    verbose_name_plural = 'Behinderteneinrichtungen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Behinderteneinrichtungen in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'traeger': 'bezeichnung'}
    list_actions_assign = [
      {
        'action_name': 'behinderteneinrichtungen-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'bezeichnung': 'Bezeichnung', 'traeger': 'Träger'}
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return (
      self.bezeichnung
      + ' ['
      + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '')
      + 'Träger: '
      + str(self.traeger)
      + ']'
    )


class Beschluesse_Bau_Planungsausschuss(SimpleModel):
  """
  Beschlüsse des Bau- und Planungsausschusses
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  beschlussjahr = PositiveSmallIntegerRangeField(
    verbose_name='Beschlussjahr',
    min_value=1990,
    max_value=get_current_year(),
    default=get_current_year(),
  )
  vorhabenbezeichnung = CharField(
    verbose_name='Bezeichnung des Vorhabens', max_length=255, validators=standard_validators
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in', max_length=255, validators=standard_validators
  )
  pdf = FileField(
    verbose_name='PDF',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PDF_PATH_PREFIX_PRIVATE + 'beschluesse_bau_planungsausschuss'
    ),
    max_length=255,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."beschluesse_bau_planungsausschuss_hro'
    verbose_name = 'Beschluss des Bau- und Planungsausschusses'
    verbose_name_plural = 'Beschlüsse des Bau- und Planungsausschusses'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = (
      'Beschlüsse des Bau- und Planungsausschusses der Bürgerschaft '
      'der Hanse- und Universitätsstadt Rostock'
    )
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'beschlussjahr': 'Beschlussjahr',
      'vorhabenbezeichnung': 'Bezeichnung des Vorhabens',
      'bearbeiter': 'Bearbeiter:in',
      'pdf': 'PDF',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse'}
    map_feature_tooltip_fields = ['vorhabenbezeichnung']
    map_filter_fields = {
      'beschlussjahr': 'Beschlussjahr',
      'vorhabenbezeichnung': 'Bezeichnung des Vorhabens',
    }

  def __str__(self):
    return (
      self.vorhabenbezeichnung
      + ' (Beschlussjahr '
      + str(self.beschlussjahr)
      + ')'
      + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')
    )


post_delete.connect(delete_pdf, sender=Beschluesse_Bau_Planungsausschuss)


class Bildungstraeger(SimpleModel):
  """
  Bildungsträger
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  betreiber = CharField(
    verbose_name='Betreiber:in', max_length=255, validators=standard_validators
  )
  schlagwoerter = ChoiceArrayField(
    CharField(verbose_name='Schlagwörter', max_length=255, choices=()), verbose_name='Schlagwörter'
  )
  barrierefrei = BooleanField(verbose_name=' barrierefrei?', blank=True, null=True)
  zeiten = CharField(verbose_name='Öffnungszeiten', max_length=255, blank=True, null=True)
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."bildungstraeger_hro'
    verbose_name = 'Bildungsträger'
    verbose_name_plural = 'Bildungsträger'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Bildungsträger in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {'schlagwoerter': 'Schlagwoerter_Bildungstraeger'}
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse'}
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'bezeichnung': 'Bezeichnung', 'schlagwoerter': 'Schlagwörter'}

  def __str__(self):
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Brunnen(SimpleModel):
  """
  Brunnen
  """

  d3 = CharField(
    verbose_name=' d.3-Vorgangsnummer',
    max_length=16,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=brunnen_d3_regex, message=brunnen_d3_message)],
  )
  d3_link = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False,
  )
  aktenzeichen = CharField(
    verbose_name='Aktenzeichen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  art = ForeignKey(
    to=Arten_Brunnen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  datum_bescheid = DateField(verbose_name='Datum des Bescheids', blank=True, null=True)
  datum_befristung = DateField(verbose_name='Datum der Befristung', blank=True, null=True)
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung', max_length=255, validators=standard_validators
  )
  realisierung_erfolgt = BooleanField(verbose_name='Realisierung erfolgt?', blank=True, null=True)
  in_betrieb = BooleanField(verbose_name=' in Betrieb?', blank=True, null=True)
  endteufe = ArrayField(
    DecimalField(
      verbose_name='Endteufe(n) (in m)',
      max_digits=3,
      decimal_places=1,
      validators=[
        MinValueValidator(
          Decimal('0.1'), 'Eine <strong><em>Endteufe</em></strong> muss mindestens 0,1 m betragen.'
        ),
        MaxValueValidator(
          Decimal('99.9'),
          'Eine <strong><em>Endteufe</em></strong> darf höchstens 99,9 m betragen.',
        ),
      ],
      blank=True,
      null=True,
    ),
    verbose_name='Endteufe(n) (in m)',
    blank=True,
    null=True,
  )
  entnahmemenge = PositiveIntegerMinField(
    verbose_name='Entnahmemenge (in m³/a)', min_value=1, blank=True, null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."brunnen_hro'
    verbose_name = 'Brunnen'
    verbose_name_plural = 'Brunnen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Brunnen in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'd3': 'd.3-Vorgang',
      'aktenzeichen': 'Aktenzeichen',
      'art': 'Art',
      'datum_bescheid': 'Datum des Bescheids',
      'datum_befristung': 'Datum der Befristung',
      'lagebeschreibung': 'Lagebeschreibung',
      'realisierung_erfolgt': 'Realisierung erfolgt?',
      'in_betrieb': 'in Betrieb?',
      'endteufe': 'Endteufe(n) (in m)',
      'entnahmemenge': 'Entnahmemenge (in m³/a)',
    }
    list_fields_with_date = ['datum_bescheid', 'datum_befristung']
    list_fields_with_foreign_key = {'art': 'art'}
    map_feature_tooltip_fields = ['lagebeschreibung']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'd3': 'd.3-Vorgangsnummer',
      'aktenzeichen': 'Aktenzeichen',
      'art': 'Art',
      'datum_bescheid': 'Datum des Bescheids',
      'datum_befristung': 'Datum der Befristung',
      'lagebeschreibung': 'Lagebeschreibung',
      'realisierung_erfolgt': 'Realisierung erfolgt?',
      'in_betrieb': 'in Betrieb?',
      'endteufe': 'Endteufe(n) (in m)',
      'entnahmemenge': 'Entnahmemenge (in m³/a)',
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return self.lagebeschreibung

  def d3_element(self):
    if self.d3_link:
      return create_d3_link(self.d3, self.d3_link)
    return self.d3


class Containerstellplaetze(SimpleModel):
  """
  Containerstellplätze
  """

  deaktiviert = DateField(verbose_name='Außerbetriebstellung', blank=True, null=True)
  id = CharField(verbose_name='ID', max_length=5, unique=True, default='00-00')
  privat = BooleanField(verbose_name=' privat?')
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  bewirtschafter_grundundboden = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Grund und Boden',
    on_delete=SET_NULL,
    db_column='bewirtschafter_grundundboden',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_grundundboden',
    blank=True,
    null=True,
  )
  bewirtschafter_glas = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Glas',
    on_delete=SET_NULL,
    db_column='bewirtschafter_glas',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_glas',
    blank=True,
    null=True,
  )
  anzahl_glas = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Glas normal', min_value=1, blank=True, null=True
  )
  anzahl_glas_unterflur = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Glas unterflur', min_value=1, blank=True, null=True
  )
  bewirtschafter_papier = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Papier',
    on_delete=SET_NULL,
    db_column='bewirtschafter_papier',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_papier',
    blank=True,
    null=True,
  )
  anzahl_papier = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Papier normal', min_value=1, blank=True, null=True
  )
  anzahl_papier_unterflur = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Papier unterflur', min_value=1, blank=True, null=True
  )
  bewirtschafter_altkleider = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Altkleider',
    on_delete=SET_NULL,
    db_column='bewirtschafter_altkleider',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_altkleider',
    blank=True,
    null=True,
  )
  anzahl_altkleider = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Altkleider', min_value=1, blank=True, null=True
  )
  inbetriebnahmejahr = PositiveSmallIntegerRangeField(
    verbose_name='Inbetriebnahmejahr', max_value=get_current_year(), blank=True, null=True
  )
  inventarnummer = CharField(
    verbose_name='Inventarnummer Stellplatz',
    max_length=8,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)],
  )
  inventarnummer_grundundboden = CharField(
    verbose_name='Inventarnummer Grund und Boden',
    max_length=8,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)],
  )
  inventarnummer_zaun = CharField(
    verbose_name='Inventarnummer Zaun',
    max_length=8,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)],
  )
  anschaffungswert = DecimalField(
    verbose_name='Anschaffungswert (in €)',
    max_digits=7,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.',
      ),
      MaxValueValidator(
        Decimal('99999.99'),
        'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 99.999,99 € betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  oeffentliche_widmung = BooleanField(verbose_name=' öffentliche Widmung?', blank=True, null=True)
  bga = BooleanField(verbose_name='Zuordnung BgA Stellplatz?', blank=True, null=True)
  bga_grundundboden = BooleanField(
    verbose_name='Zuordnung BgA Grund und Boden?', blank=True, null=True
  )
  bga_zaun = BooleanField(verbose_name='Zuordnung BgA Zaun?', blank=True, null=True)
  art_eigentumserwerb = CharField(
    verbose_name='Art des Eigentumserwerbs Stellplatz',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  art_eigentumserwerb_zaun = CharField(
    verbose_name='Art des Eigentumserwerbs Zaun',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  vertraege = CharField(
    verbose_name='Verträge', max_length=255, blank=True, null=True, validators=standard_validators
  )
  winterdienst_a = BooleanField(verbose_name='Winterdienst A?', blank=True, null=True)
  winterdienst_b = BooleanField(verbose_name='Winterdienst B?', blank=True, null=True)
  winterdienst_c = BooleanField(verbose_name='Winterdienst C?', blank=True, null=True)
  flaeche = DecimalField(
    verbose_name='Fläche (in m²)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Fläche</em></strong> muss mindestens 0,01 m² betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Fläche</em></strong> darf höchstens 999,99 m² betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'containerstellplaetze'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."containerstellplaetze_hro'
    verbose_name = 'Containerstellplatz'
    verbose_name_plural = 'Containerstellplätze'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Containerstellplätze in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['deaktiviert', 'id']
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Außerbetriebstellung',
      'id': 'ID',
      'privat': 'privat?',
      'bezeichnung': 'Bezeichnung',
      'foto': 'Foto',
    }
    list_fields_with_date = ['deaktiviert']
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {'id': 'ID', 'privat': 'privat?', 'bezeichnung': 'Bezeichnung'}

  def __str__(self):
    return self.bezeichnung


pre_save.connect(set_pre_save_instance, sender=Containerstellplaetze)

post_save.connect(photo_post_processing, sender=Containerstellplaetze)

post_save.connect(delete_photo_after_emptied, sender=Containerstellplaetze)

post_delete.connect(delete_photo, sender=Containerstellplaetze)


class Denkmalbereiche(SimpleModel):
  """
  Denkmalbereiche
  """

  id = PositiveIntegerField(verbose_name='ID', unique=True, default=0)
  status = ForeignKey(
    to=Status_Baudenkmale_Denkmalbereiche,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status',
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  beschreibung = CharField(
    verbose_name='Beschreibung', max_length=255, validators=standard_validators
  )
  unterschutzstellungen = ArrayField(
    DateField(verbose_name='Unterschutzstellungen', blank=True, null=True),
    verbose_name='Unterschutzstellungen',
    blank=True,
    null=True,
  )
  veroeffentlichungen = ArrayField(
    DateField(verbose_name='Veröffentlichungen', blank=True, null=True),
    verbose_name='Veröffentlichungen',
    blank=True,
    null=True,
  )
  denkmalnummern = ArrayField(
    CharField(
      verbose_name='Denkmalnummern',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators,
    ),
    verbose_name='Denkmalnummern',
    blank=True,
    null=True,
  )
  hinweise = NullTextField(
    verbose_name='Hinweise', max_length=500, blank=True, null=True, validators=standard_validators
  )
  aenderungen = NullTextField(
    verbose_name='Änderungen',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = multipolygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."denkmalbereiche_hro'
    verbose_name = 'Denkmalbereich'
    verbose_name_plural = 'Denkmalbereiche'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Denkmalbereiche der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['id']
    geometry_type = 'MultiPolygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'status': 'Status',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung',
    }
    list_fields_with_foreign_key = {'status': 'status'}
    list_actions_assign = [
      {
        'action_name': 'denkmalbereiche-status',
        'action_title': 'ausgewählten Datensätzen Status direkt zuweisen',
        'field': 'status',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'status': 'Status',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung',
    }
    map_filter_fields_as_list = ['status']

  def __str__(self):
    return self.bezeichnung + ' [Beschreibung: ' + str(self.beschreibung) + ']'


class Denksteine(SimpleModel):
  """
  Denksteine
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  nummer = CharField(
    verbose_name='Nummer',
    max_length=255,
    validators=[RegexValidator(regex=denksteine_nummer_regex, message=denksteine_nummer_message)],
  )
  titel = ForeignKey(
    to=Personentitel,
    verbose_name='Titel',
    on_delete=SET_NULL,
    db_column='titel',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_titel',
    blank=True,
    null=True,
  )
  vorname = CharField(verbose_name='Vorname', max_length=255, validators=personennamen_validators)
  nachname = CharField(
    verbose_name='Nachname', max_length=255, validators=personennamen_validators
  )
  geburtsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Geburtsjahr', min_value=1850, max_value=1945
  )
  sterbejahr = PositiveSmallIntegerRangeField(
    verbose_name='Sterbejahr', min_value=1933, max_value=1945, blank=True, null=True
  )
  text_auf_dem_stein = CharField(
    verbose_name='Text auf dem Stein', max_length=255, validators=standard_validators
  )
  ehemalige_adresse = CharField(
    verbose_name=' ehemalige Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  material = ForeignKey(
    to=Materialien_Denksteine,
    verbose_name='Material',
    on_delete=RESTRICT,
    db_column='material',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_materialien',
  )
  erstes_verlegejahr = PositiveSmallIntegerRangeField(
    verbose_name=' erstes Verlegejahr', min_value=2002, max_value=get_current_year()
  )
  website = CharField(
    verbose_name='Website', max_length=255, validators=[URLValidator(message=url_message)]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."denksteine_hro'
    verbose_name = 'Denkstein'
    verbose_name_plural = 'Denksteine'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Denksteine in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'nummer': 'Nummer',
      'titel': 'Titel',
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'geburtsjahr': 'Geburtsjahr',
      'sterbejahr': 'Sterbejahr',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'titel': 'bezeichnung'}
    map_feature_tooltip_fields = ['titel', 'vorname', 'nachname']
    map_filter_fields = {
      'nummer': 'Nummer',
      'titel': 'Titel',
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'geburtsjahr': 'Geburtsjahr',
      'sterbejahr': 'Sterbejahr',
    }
    map_filter_fields_as_list = ['titel']

  def __str__(self):
    return (
      (str(self.titel) + ' ' if self.titel else '')
      + self.vorname
      + ' '
      + self.nachname
      + ' (* '
      + str(self.geburtsjahr)
      + (', † ' + str(self.sterbejahr) if self.sterbejahr else '')
      + ')'
      + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')
    )


class Erdwaermesonden(SimpleModel):
  """
  Erdwärmesonden
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  d3 = CharField(
    verbose_name=' d3-Vorgangsnummer',
    max_length=16,
    blank=True,
    null=True,
    validators=[
      RegexValidator(regex=erdwaermesonden_d3_regex, message=erdwaermesonden_d3_message)
    ],
  )
  d3_link = CharField(
    max_length=255,
    blank=True,
    null=True,
    editable=False,
  )
  bohrprofil = BooleanField(verbose_name='Bohrprofil?', blank=True, null=True)
  aktenzeichen = CharField(
    verbose_name='Aktenzeichen',
    max_length=18,
    validators=[
      RegexValidator(
        regex=erdwaermesonden_aktenzeichen_regex, message=erdwaermesonden_aktenzeichen_message
      )
    ],
  )
  art = ForeignKey(
    to=Arten_Erdwaermesonden,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  typ = ForeignKey(
    to=Typen_Erdwaermesonden,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
    blank=True,
    null=True,
  )
  awsv_anlage = BooleanField(verbose_name='AwSV-Anlage?', blank=True, null=True)
  anzahl_sonden = PositiveSmallIntegerMinField(
    verbose_name='Anzahl der Sonden', min_value=1, blank=True, null=True
  )
  sondenfeldgroesse = PositiveSmallIntegerMinField(
    verbose_name='Sondenfeldgröße (in m²)', min_value=1, blank=True, null=True
  )
  endteufe = DecimalField(
    verbose_name='Endteufe (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Endteufe</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Endteufe</em></strong> darf höchstens 999,99 m betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  hinweis = CharField(
    verbose_name='Hinweis', max_length=255, blank=True, null=True, validators=standard_validators
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."erdwaermesonden_hro'
    verbose_name = 'Erdwärmesonde'
    verbose_name_plural = 'Erdwärmesonden'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Erdwärmesonden in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'd3': 'd.3-Vorgang',
      'bohrprofil': 'Bohrprofil?',
      'aktenzeichen': 'Aktenzeichen',
      'adresse': 'Adresse',
      'art': 'Art',
      'typ': 'Typ',
      'awsv_anlage': 'AwSV-Anlage?',
      'anzahl_sonden': 'Anzahl der Sonden',
      'sondenfeldgroesse': 'Sondenfeldgröße (in m²)',
      'endteufe': 'Endteufe (in m)',
      'hinweis': 'Hinweis',
    }
    list_fields_with_decimal = ['endteufe']
    list_fields_with_foreign_key = {'adresse': 'adresse', 'art': 'art', 'typ': 'typ'}
    map_feature_tooltip_fields = ['aktenzeichen']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'd3': 'd.3-Vorgangsnummer',
      'bohrprofil': 'Bohrprofil?',
      'aktenzeichen': 'Aktenzeichen',
      'art': 'Art',
      'typ': 'Typ',
      'awsv_anlage': 'AwSV-Anlage?',
      'anzahl_sonden': 'Anzahl der Sonden',
      'sondenfeldgroesse': 'Sondenfeldgröße (in m²)',
      'endteufe': 'Endteufe (in m)',
      'hinweis': 'Hinweis',
    }
    map_filter_fields_as_list = ['art', 'typ']

  def __str__(self):
    aktenzeichen_str = f'{self.aktenzeichen}'
    return f'{self.adresse}, {aktenzeichen_str}' if self.adresse else aktenzeichen_str

  def d3_element(self):
    if self.d3_link:
      return create_d3_link(self.d3, self.d3_link)
    return self.d3


class Fahrradabstellanlagen(SimpleModel):
  """
  Fahrradabstellanlagen
  """

  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True,
  )
  id = CharField(verbose_name='ID', max_length=8, unique=True, default='00000000')
  hersteller = ForeignKey(
    to=Hersteller_Fahrradabstellanlagen,
    verbose_name='Hersteller',
    on_delete=SET_NULL,
    db_column='hersteller',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_hersteller',
    blank=True,
    null=True,
  )
  ausfuehrung = ForeignKey(
    to=Ausfuehrungen_Fahrradabstellanlagen,
    verbose_name='Ausführung',
    on_delete=RESTRICT,
    db_column='ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ausfuehrungen',
  )
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  anzahl_stellplaetze = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Stellplätze', min_value=1, blank=True, null=True
  )
  ausfuehrung_stellplaetze = ForeignKey(
    to=Ausfuehrungen_Fahrradabstellanlagen_Stellplaetze,
    verbose_name='Ausführung Stellplätze',
    on_delete=SET_NULL,
    db_column='ausfuehrung_stellplaetze',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ausfuehrungen_stellplaetze',
    blank=True,
    null=True,
  )
  baujahr = PositiveSmallIntegerRangeField(
    verbose_name='Baujahr', min_value=1900, max_value=get_current_year(), blank=True, null=True
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer',
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'fahrradabstellanlagen'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug"."fahrradabstellanlagen_hro'
    verbose_name = 'Fahrradabstellanlage'
    verbose_name_plural = 'Fahrradabstellanlagen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Fahrradabstellanlagen in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['id']
    address_type = 'Straße'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'hersteller': 'Hersteller',
      'ausfuehrung': 'Ausführung',
      'lagebeschreibung': 'Lagebeschreibung',
      'anzahl_stellplaetze': 'Anzahl Stellplätze',
      'ausfuehrung_stellplaetze': 'Ausführung Stellplätze',
      'baujahr': 'Baujahr',
      'eigentuemer': 'Eigentümer',
      'foto': 'Foto',
    }
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'hersteller': 'bezeichnung',
      'ausfuehrung': 'ausfuehrung',
      'ausfuehrung_stellplaetze': 'ausfuehrung',
      'eigentuemer': 'bezeichnung',
    }
    list_actions_assign = [
      {
        'action_name': 'fahrradabstellanlagen-ausfuehrung',
        'action_title': 'ausgewählten Datensätzen Ausführung direkt zuweisen',
        'field': 'ausfuehrung',
        'type': 'foreignkey',
      },
      {
        'action_name': 'fahrradabstellanlagen-ausfuehrung_stellplaetze',
        'action_title': 'ausgewählten Datensätzen Ausführung Stellplätze direkt zuweisen',
        'field': 'ausfuehrung_stellplaetze',
        'type': 'foreignkey',
      },
      {
        'action_name': 'fahrradabstellanlagen-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey',
      },
      {
        'action_name': 'fahrradabstellanlagen-hersteller',
        'action_title': 'ausgewählten Datensätzen Hersteller direkt zuweisen',
        'field': 'hersteller',
        'type': 'foreignkey',
      },
    ]
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'hersteller': 'Hersteller',
      'ausfuehrung': 'Ausführung',
      'lagebeschreibung': 'Lagebeschreibung',
      'anzahl_stellplaetze': 'Anzahl Stellplätze',
      'ausfuehrung_stellplaetze': 'Ausführung Stellplätze',
      'baujahr': 'Baujahr',
      'eigentuemer': 'Eigentümer',
    }
    map_filter_fields_as_list = [
      'strasse',
      'hersteller',
      'ausfuehrung',
      'ausfuehrung_stellplaetze',
      'eigentuemer',
    ]

  def __str__(self):
    return self.id


pre_save.connect(set_pre_save_instance, sender=Fahrradabstellanlagen)

post_save.connect(photo_post_processing, sender=Fahrradabstellanlagen)

post_save.connect(delete_photo_after_emptied, sender=Fahrradabstellanlagen)

post_delete.connect(delete_photo, sender=Fahrradabstellanlagen)


class Fahrradboxen(SimpleModel):
  """
  Fahrradboxen
  """

  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True,
  )
  id = CharField(verbose_name='ID', max_length=8, unique=True, default='00000000')
  ausfuehrung = ForeignKey(
    to=Ausfuehrungen_Fahrradboxen,
    verbose_name='Ausführung',
    on_delete=RESTRICT,
    db_column='ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ausfuehrungen',
  )
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  anzahl_stellplaetze = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Stellplätze', min_value=1, blank=True, null=True
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer',
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'fahrradboxen'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug"."fahrradboxen_hro'
    verbose_name = 'Fahrradbox'
    verbose_name_plural = 'Fahrradboxen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Fahrradboxen in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['id']
    address_type = 'Straße'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'ausfuehrung': 'Ausführung',
      'lagebeschreibung': 'Lagebeschreibung',
      'anzahl_stellplaetze': 'Anzahl Stellplätze',
      'eigentuemer': 'Eigentümer',
      'foto': 'Foto',
    }
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'ausfuehrung': 'ausfuehrung',
      'eigentuemer': 'bezeichnung',
    }
    list_actions_assign = [
      {
        'action_name': 'fahrradboxen-ausfuehrung',
        'action_title': 'ausgewählten Datensätzen Ausführung direkt zuweisen',
        'field': 'ausfuehrung',
        'type': 'foreignkey',
      },
      {
        'action_name': 'fahrradboxen-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey',
      },
    ]
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'ausfuehrung': 'Ausführung',
      'lagebeschreibung': 'Lagebeschreibung',
      'anzahl_stellplaetze': 'Anzahl Stellplätze',
      'eigentuemer': 'Eigentümer',
    }
    map_filter_fields_as_list = ['strasse', 'ausfuehrung', 'eigentuemer']

  def __str__(self):
    return self.id


pre_save.connect(set_pre_save_instance, sender=Fahrradboxen)

post_save.connect(photo_post_processing, sender=Fahrradboxen)

post_save.connect(delete_photo_after_emptied, sender=Fahrradboxen)

post_delete.connect(delete_photo, sender=Fahrradboxen)


class Fahrradreparatursets(SimpleModel):
  """
  Fahrradreparatursets
  """

  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True,
  )
  id = CharField(verbose_name='ID', max_length=8, unique=True, default='00000000')
  ausfuehrung = ForeignKey(
    to=Ausfuehrungen_Fahrradreparatursets,
    verbose_name='Ausführung',
    on_delete=RESTRICT,
    db_column='ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ausfuehrungen',
  )
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  baujahr = PositiveSmallIntegerRangeField(
    verbose_name='Baujahr', min_value=1900, max_value=get_current_year(), blank=True, null=True
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer',
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'fahrradreparatursets'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug"."fahrradreparatursets_hro'
    verbose_name = 'Fahrradreparaturset'
    verbose_name_plural = 'Fahrradreparatursets'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Fahrradreparatursets in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['id']
    address_type = 'Straße'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'ausfuehrung': 'Ausführung',
      'lagebeschreibung': 'Lagebeschreibung',
      'baujahr': 'Baujahr',
      'eigentuemer': 'Eigentümer',
      'foto': 'Foto',
    }
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'ausfuehrung': 'ausfuehrung',
      'eigentuemer': 'bezeichnung',
    }
    list_actions_assign = [
      {
        'action_name': 'fahrradreparatursets-ausfuehrung',
        'action_title': 'ausgewählten Datensätzen Ausführung direkt zuweisen',
        'field': 'ausfuehrung',
        'type': 'foreignkey',
      },
      {
        'action_name': 'fahrradreparatursets-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey',
      },
    ]
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'ausfuehrung': 'Ausführung',
      'lagebeschreibung': 'Lagebeschreibung',
      'baujahr': 'Baujahr',
      'eigentuemer': 'Eigentümer',
    }
    map_filter_fields_as_list = ['strasse', 'ausfuehrung', 'eigentuemer']

  def __str__(self):
    return self.id


pre_save.connect(set_pre_save_instance, sender=Fahrradreparatursets)

post_save.connect(photo_post_processing, sender=Fahrradreparatursets)

post_save.connect(delete_photo_after_emptied, sender=Fahrradreparatursets)

post_delete.connect(delete_photo, sender=Fahrradreparatursets)


class Fahrradstaender(SimpleModel):
  """
  Fahrradständer
  """

  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True,
  )
  id = CharField(verbose_name='ID', max_length=8, unique=True, default='00000000')
  ausfuehrung = ForeignKey(
    to=Ausfuehrungen_Fahrradstaender,
    verbose_name='Ausführung',
    on_delete=RESTRICT,
    db_column='ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ausfuehrungen',
  )
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  anzahl_stellplaetze = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Stellplätze', min_value=1, blank=True, null=True
  )
  anzahl_fahrradstaender = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Fahrradständer', min_value=1, blank=True, null=True
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer',
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'fahrradstaender'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug"."fahrradstaender_hro'
    verbose_name = 'Fahrradständer'
    verbose_name_plural = 'Fahrradständer'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Fahrradständer in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['id']
    address_type = 'Straße'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'ausfuehrung': 'Ausführung',
      'lagebeschreibung': 'Lagebeschreibung',
      'anzahl_stellplaetze': 'Anzahl Stellplätze',
      'anzahl_fahrradstaender': 'Anzahl Fahrradständer',
      'eigentuemer': 'Eigentümer',
      'foto': 'Foto',
    }
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'ausfuehrung': 'ausfuehrung',
      'eigentuemer': 'bezeichnung',
    }
    list_actions_assign = [
      {
        'action_name': 'fahrradstaender-ausfuehrung',
        'action_title': 'ausgewählten Datensätzen Ausführung direkt zuweisen',
        'field': 'ausfuehrung',
        'type': 'foreignkey',
      },
      {
        'action_name': 'fahrradstaender-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey',
      },
    ]
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'ausfuehrung': 'Ausführung',
      'lagebeschreibung': 'Lagebeschreibung',
      'anzahl_stellplaetze': 'Anzahl Stellplätze',
      'anzahl_fahrradstaender': 'Anzahl Fahrradständer',
      'eigentuemer': 'Eigentümer',
    }
    map_filter_fields_as_list = ['strasse', 'ausfuehrung', 'eigentuemer']

  def __str__(self):
    return self.id


pre_save.connect(set_pre_save_instance, sender=Fahrradstaender)

post_save.connect(photo_post_processing, sender=Fahrradstaender)

post_save.connect(delete_photo_after_emptied, sender=Fahrradstaender)

post_delete.connect(delete_photo, sender=Fahrradstaender)


class Feuerwachen(SimpleModel):
  """
  Feuerwachen
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  art = ForeignKey(
    to=Arten_Feuerwachen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."feuerwachen_hro'
    verbose_name = 'Feuerwache'
    verbose_name_plural = 'Feuerwachen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Feuerwachen in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'art': 'art'}
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'art': 'Art', 'bezeichnung': 'Bezeichnung'}
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return (
      self.bezeichnung
      + ' ['
      + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '')
      + 'Art: '
      + str(self.art)
      + ']'
    )


class Fliessgewaesser(SimpleModel):
  """
  Fließgewässer
  """

  nummer = CharField(verbose_name='Nummer', max_length=255, validators=standard_validators)
  art = ForeignKey(
    to=Arten_Fliessgewaesser,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  ordnung = ForeignKey(
    to=Ordnungen_Fliessgewaesser,
    verbose_name='Ordnung',
    on_delete=SET_NULL,
    db_column='ordnung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ordnungen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  nennweite = PositiveSmallIntegerMinField(
    verbose_name='Nennweite (in mm)', min_value=100, blank=True, null=True
  )
  laenge = PositiveIntegerField(verbose_name='Länge (in m)', default=0)
  laenge_in_hro = PositiveIntegerField(
    verbose_name='Länge innerhalb Rostocks (in m)', blank=True, null=True
  )
  geometrie = line_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."fliessgewaesser_hro'
    verbose_name = 'Fließgewässer'
    verbose_name_plural = 'Fließgewässer'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Fließgewässer in der Hanse- und Universitätsstadt Rostock und Umgebung'
    as_overlay = True
    readonly_fields = ['laenge', 'laenge_in_hro']
    geometry_type = 'LineString'
    list_fields = {
      'aktiv': 'aktiv?',
      'nummer': 'Nummer',
      'art': 'Art',
      'ordnung': 'Ordnung',
      'bezeichnung': 'Bezeichnung',
      'laenge': 'Länge (in m)',
      'laenge_in_hro': 'Länge innerhalb Rostocks (in m)',
    }
    list_fields_with_foreign_key = {'art': 'art', 'ordnung': 'ordnung'}
    map_heavy_load_limit = 500
    map_feature_tooltip_fields = ['nummer']
    map_filter_fields = {
      'nummer': 'Nummer',
      'art': 'Art',
      'ordnung': 'Ordnung',
      'bezeichnung': 'Bezeichnung',
    }
    map_filter_fields_as_list = ['art', 'ordnung']

  def __str__(self):
    return (
      self.nummer
      + ' [Art: '
      + str(self.art)
      + (', Ordnung: ' + str(self.ordnung) if self.ordnung else '')
      + ']'
    )


class Fussgaengerueberwege(SimpleModel):
  """
  Fußgängerüberwege
  """

  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True,
  )
  id = CharField(verbose_name='ID', max_length=8, unique=True, default='00000000')
  breite = DecimalField(
    verbose_name='Breite (in m)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Breite</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'), 'Die <strong><em>Breite</em></strong> darf höchstens 9,99 m betragen.'
      ),
    ],
  )
  laenge = DecimalField(
    verbose_name='Länge (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Länge</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'), 'Die <strong><em>Länge</em></strong> darf höchstens 99,99 m betragen.'
      ),
    ],
  )
  barrierefrei = BooleanField(verbose_name=' barrierefrei?')
  beleuchtungsart = ForeignKey(
    to=Beleuchtungsarten,
    verbose_name='Beleuchtungsart',
    on_delete=RESTRICT,
    db_column='beleuchtungsart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betriebsarten',
  )
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  baujahr = PositiveSmallIntegerRangeField(
    verbose_name='Baujahr', min_value=1900, max_value=get_current_year(), blank=True, null=True
  )
  kreisverkehr = BooleanField(verbose_name='Kreisverkehr?', blank=True, null=True)
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'fussgaengerueberwege'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug"."fussgaengerueberwege_hro'
    verbose_name = 'Fußgängerüberweg'
    verbose_name_plural = 'Fußgängerüberwege'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Fußgängerüberwege in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['id']
    address_type = 'Straße'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'breite': 'Breite (in m)',
      'laenge': 'Länge (in m)',
      'barrierefrei': 'barrierefrei?',
      'beleuchtungsart': 'Beleuchtungsart',
      'lagebeschreibung': 'Lagebeschreibung',
      'baujahr': 'Baujahr',
      'kreisverkehr': 'Kreisverkehr?',
      'foto': 'Foto',
    }
    list_fields_with_decimal = ['breite', 'laenge']
    list_fields_with_foreign_key = {'strasse': 'strasse', 'beleuchtungsart': 'bezeichnung'}
    list_actions_assign = [
      {
        'action_name': 'fussgaengerueberwege-barrierefrei',
        'action_title': 'ausgewählten Datensätzen barrierefrei (ja/nein) direkt zuweisen',
        'field': 'barrierefrei',
        'type': 'boolean',
      },
      {
        'action_name': 'fussgaengerueberwege-beleuchtungsart',
        'action_title': 'ausgewählten Datensätzen Beleuchtungsart direkt zuweisen',
        'field': 'beleuchtungsart',
        'type': 'foreignkey',
      },
    ]
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'strasse': 'Straße',
      'breite': 'Breite (in m)',
      'laenge': 'Länge (in m)',
      'barrierefrei': 'barrierefrei?',
      'beleuchtungsart': 'Beleuchtungsart',
      'lagebeschreibung': 'Lagebeschreibung',
      'baujahr': 'Baujahr',
      'kreisverkehr': 'Kreisverkehr?',
    }
    map_filter_fields_as_list = ['strasse', 'beleuchtungsart']

  def __str__(self):
    return self.id


pre_save.connect(set_pre_save_instance, sender=Fussgaengerueberwege)

post_save.connect(photo_post_processing, sender=Fussgaengerueberwege)

post_save.connect(delete_photo_after_emptied, sender=Fussgaengerueberwege)

post_delete.connect(delete_photo, sender=Fussgaengerueberwege)


class Gemeinbedarfsflaechen(SimpleModel):
  """
  Gemeinbedarfsflächen
  """

  registriernummer = CharField(
    verbose_name='Registriernummer',
    max_length=6,
    validators=[
      RegexValidator(
        regex=gemeinbedarfsflaechen_registriernummer_regex,
        message=gemeinbedarfsflaechen_registriernummer_message,
      )
    ],
  )
  jahr = PositiveSmallIntegerRangeField(
    verbose_name='Jahr', default=get_current_year(), max_value=get_current_year()
  )
  geometrie = polygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."gemeinbedarfsflaechen_hro'
    verbose_name = 'Gemeinbedarfsfläche'
    verbose_name_plural = 'Gemeinbedarfsflächen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Gemeinbedarfsflächen in der Hanse- und Universitätsstadt Rostock'
    forms_in_high_zoom_mode = True
    geometry_type = 'Polygon'
    list_fields = {'aktiv': 'aktiv?', 'registriernummer': 'Registriernummer', 'jahr': 'Jahr'}
    map_feature_tooltip_fields = ['registriernummer']
    map_filter_fields = {'aktiv': 'aktiv?', 'registriernummer': 'Registriernummer', 'jahr': 'Jahr'}
    additional_wfs_featuretypes = [
      {
        'name': 'flurstuecke',
        'title': 'Flurstücke',
        'url': 'https://geo.sv.rostock.de/geodienste/flurstuecke_hro/wfs',
        'featuretypes': 'hro.flurstuecke.flurstuecke',
      }
    ]

  def __str__(self):
    return self.registriernummer + ' (Jahr: ' + str(self.jahr) + ')'


class Gutachterfotos(SimpleModel):
  """
  Gutachterfotos
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in', max_length=255, validators=standard_validators
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  datum = DateField(verbose_name='Datum', default=date.today)
  aufnahmedatum = DateField(verbose_name='Aufnahmedatum', default=date.today)
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'gutachterfotos'),
    max_length=255,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."gutachterfotos_hro'
    verbose_name = 'Gutachterfoto'
    verbose_name_plural = 'Gutachterfotos'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Gutachterfotos der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bearbeiter': 'Bearbeiter:in',
      'datum': 'Datum',
      'aufnahmedatum': 'Aufnahmedatum',
      'foto': 'Foto',
    }
    list_fields_with_date = ['datum', 'aufnahmedatum']
    list_fields_with_foreign_key = {'adresse': 'adresse'}
    list_actions_assign = [
      {
        'action_name': 'gutachterfotos-datum',
        'action_title': 'ausgewählten Datensätzen Datum direkt zuweisen',
        'field': 'datum',
        'type': 'date',
        'value_required': True,
      },
      {
        'action_name': 'gutachterfotos-aufnahmedatum',
        'action_title': 'ausgewählten Datensätzen Aufnahmedatum direkt zuweisen',
        'field': 'aufnahmedatum',
        'type': 'date',
        'value_required': True,
      },
    ]
    map_heavy_load_limit = 800
    map_feature_tooltip_fields = ['datum']
    map_filter_fields = {'datum': 'Datum', 'aufnahmedatum': 'Aufnahmedatum'}

  def __str__(self):
    return (
      'Gutachterfoto mit Aufnahmedatum '
      + datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y')
      + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')
    )


post_save.connect(photo_post_processing, sender=Gutachterfotos)

post_delete.connect(delete_photo, sender=Gutachterfotos)


class Hausnummern(SimpleModel):
  """
  Hausnummern
  """

  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True,
  )
  deaktiviert = DateField(verbose_name='Datum der Löschung', blank=True, null=True)
  loeschung_details = CharField(
    verbose_name='Details zur Löschung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  vorherige_adresse = CharField(
    verbose_name=' vorherige Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  vorherige_antragsnummer = CharField(
    verbose_name=' vorherige Antragsnummer',
    max_length=6,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=hausnummern_antragsnummer_regex, message=hausnummern_antragsnummer_message
      )
    ],
  )
  hausnummer = PositiveSmallIntegerRangeField(
    verbose_name='Hausnummer', min_value=1, max_value=999
  )
  hausnummer_zusatz = CharField(
    verbose_name='Hausnummernzusatz',
    max_length=1,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=hausnummer_zusatz_regex, message=hausnummer_zusatz_message)],
  )
  postleitzahl = CharField(
    verbose_name='Postleitzahl',
    max_length=5,
    validators=[RegexValidator(regex=postleitzahl_regex, message=postleitzahl_message)],
  )
  vergabe_datum = DateField(verbose_name='Datum der Vergabe', default=date.today)
  antragsnummer = CharField(
    verbose_name='Antragsnummer',
    max_length=6,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=hausnummern_antragsnummer_regex, message=hausnummern_antragsnummer_message
      )
    ],
  )
  gebaeude_bauweise = ForeignKey(
    to=Gebaeudebauweisen,
    verbose_name='Bauweise des Gebäudes',
    on_delete=SET_NULL,
    db_column='gebaeude_bauweise',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gebaeude_bauweisen',
    blank=True,
    null=True,
  )
  gebaeude_funktion = ForeignKey(
    to=Gebaeudefunktionen,
    verbose_name='Funktion des Gebäudes',
    on_delete=SET_NULL,
    db_column='gebaeude_funktion',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gebaeude_funktionen',
    blank=True,
    null=True,
  )
  hinweise_gebaeude = CharField(
    verbose_name=' weitere Hinweise zum Gebäude',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in', max_length=255, validators=standard_validators
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug"."hausnummern_hro'
    unique_together = ['strasse', 'hausnummer', 'hausnummer_zusatz']
    verbose_name = 'Hausnummer'
    verbose_name_plural = 'Hausnummern'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Hausnummern der Hanse- und Universitätsstadt Rostock'
    catalog_link_fields = {
      'gebaeude_bauweise': 'https://geo.sv.rostock.de/alkis-ok/31001/baw/',
      'gebaeude_funktion': 'https://geo.sv.rostock.de/alkis-ok/31001/gfk/',
    }
    address_type = 'Straße'
    address_mandatory = True
    geometry_type = 'Point'
    postcode_assigner = 'postleitzahl'
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
      'gebaeude_funktion': 'Funktion des Gebäudes',
    }
    list_fields_with_date = ['deaktiviert', 'vergabe_datum']
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'gebaeude_bauweise': 'bezeichnung',
      'gebaeude_funktion': 'bezeichnung',
    }
    list_actions_assign = [
      {
        'action_name': 'hausnummern-vergabe_datum',
        'action_title': 'ausgewählten Datensätzen Datum der Vergabe direkt zuweisen',
        'field': 'vergabe_datum',
        'type': 'date',
        'value_required': True,
      }
    ]
    map_heavy_load_limit = 800
    map_feature_tooltip_fields = ['strasse', 'hausnummer', 'hausnummer_zusatz']
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
      'gebaeude_funktion': 'Funktion des Gebäudes',
    }
    map_filter_fields_as_list = ['strasse', 'gebaeude_bauweise', 'gebaeude_funktion']

  def __str__(self):
    return (
      str(self.strasse)
      + ' '
      + str(self.hausnummer)
      + (self.hausnummer_zusatz if self.hausnummer_zusatz else '')
      + ' [Postleitzahl: '
      + self.postleitzahl
      + ']'
    )


class Hoehenfestpunkte(SimpleModel):
  """
  Höhenfestpunkte
  """

  aktualisiert = DateField(verbose_name='letzte Änderung', editable=False, auto_now=True)
  bearbeiter = CharField(
    verbose_name=' letzte:r Bearbeiter:in', max_length=255, validators=standard_validators
  )
  punktkennung = PositiveIntegerField(verbose_name='Punktkennung', unique=True)
  hoehe_hn_ausg = DecimalField(
    verbose_name='Höhe HN Ausgangswert (in m)',
    max_digits=6,
    decimal_places=3,
    validators=[
      MinValueValidator(
        Decimal('0.001'),
        'Die <strong><em>Höhe HN Ausgangswert</em></strong> muss mindestens 0,001 m betragen.',
      ),
      MaxValueValidator(
        Decimal('999.999'),
        'Die <strong><em>Höhe HN Ausgangswert</em></strong> darf höchstens 999,999 m betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  hoehe_hn_na = DecimalField(
    verbose_name='Höhe HN Nachmessung (in m)',
    max_digits=6,
    decimal_places=3,
    validators=[
      MinValueValidator(
        Decimal('0.001'),
        'Die <strong><em>Höhe HN Nachmessung</em></strong> muss mindestens 0,001 m betragen.',
      ),
      MaxValueValidator(
        Decimal('999.999'),
        'Die <strong><em>Höhe HN Nachmessung</em></strong> darf höchstens 999,999 m betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  skizze_dateiformat = ForeignKey(
    to=Dateiformate,
    verbose_name='Dateiformat der Skizze unter K:/GDS/Festpunkte/Ap&tp/HP/Hp',
    on_delete=RESTRICT,
    db_column='skizze_dateiformat',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_skizzen_dateiformate',
  )
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."hoehenfestpunkte_hro'
    verbose_name = 'Höhenfestpunkt'
    verbose_name_plural = 'Höhenfestpunkte'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Höhenfestpunkte in der Hanse- und Universitätsstadt Rostock'
    group_with_users_for_choice_field = 'datenmanagement_hoehenfestpunkte_full'
    as_overlay = False
    geometry_type = 'Point'
    geometry_coordinates_input = True
    list_fields = {
      'aktiv': 'aktiv?',
      'aktualisiert': 'letzte Änderung',
      'bearbeiter': 'letzte:r Bearbeiter:in',
      'punktkennung': 'Punktkennung',
      'hoehe_hn_ausg': 'Höhe HN Ausgangswert (in m)',
      'hoehe_hn_na': 'Höhe HN Nachmessung (in m)',
      'skizze_dateiformat': 'Dateiformat der Skizze unter K:/GDS/Festpunkte/Ap&tp/HP/Hp',
      'lagebeschreibung': 'Lagebeschreibung',
    }
    list_fields_with_date = ['aktualisiert']
    list_fields_with_decimal = ['hoehe_hn_ausg', 'hoehe_hn_na']
    list_fields_with_foreign_key = {'skizze_dateiformat': 'bezeichnung'}
    map_feature_tooltip_fields = ['punktkennung']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'aktualisiert': 'letzte Änderung',
      'bearbeiter': 'letzte:r Bearbeiter:in',
      'punktkennung': 'Punktkennung',
      'hoehe_hn_ausg': 'Höhe HN Ausgangswert (in m)',
      'hoehe_hn_na': 'Höhe HN Nachmessung (in m)',
      'skizze_dateiformat': 'Dateiformat der Skizze unter K:/GDS/Festpunkte/Ap&tp/HP/Hp',
      'lagebeschreibung': 'Lagebeschreibung',
    }
    map_filter_fields_as_list = ['skizze_dateiformat']

  def __str__(self):
    return f'{self.punktkennung}'


class Hospize(SimpleModel):
  """
  Hospize
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger',
  )
  plaetze = PositiveSmallIntegerMinField(verbose_name='Plätze', min_value=1, blank=True, null=True)
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."hospize_hro'
    verbose_name = 'Hospiz'
    verbose_name_plural = 'Hospize'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Hospize in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'traeger': 'bezeichnung'}
    list_actions_assign = [
      {
        'action_name': 'hospize-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'bezeichnung': 'Bezeichnung', 'traeger': 'Träger'}
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return (
      self.bezeichnung
      + ' ['
      + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '')
      + 'Träger: '
      + str(self.traeger)
      + ']'
    )


class Hundetoiletten(SimpleModel):
  """
  Hundetoiletten
  """

  deaktiviert = DateField(verbose_name='Außerbetriebstellung', blank=True, null=True)
  id = CharField(verbose_name='ID', max_length=8, unique=True, default='00000000')
  art = ForeignKey(
    to=Arten_Hundetoiletten,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  aufstellungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Aufstellungsjahr', max_value=get_current_year(), blank=True, null=True
  )
  bewirtschafter = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter',
  )
  pflegeobjekt = CharField(
    verbose_name='Pflegeobjekt', max_length=255, validators=standard_validators
  )
  inventarnummer = CharField(
    verbose_name='Inventarnummer',
    max_length=8,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=inventarnummer_regex, message=inventarnummer_message)],
  )
  anschaffungswert = DecimalField(
    verbose_name='Anschaffungswert (in €)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.',
      ),
      MaxValueValidator(
        Decimal('9999.99'),
        'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 9.999,99 € betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."hundetoiletten_hro'
    verbose_name = 'Hundetoilette'
    verbose_name_plural = 'Hundetoiletten'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Hundetoiletten im Eigentum der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['deaktiviert', 'id']
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Außerbetriebstellung',
      'id': 'ID',
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt',
    }
    list_fields_with_date = ['deaktiviert']
    list_fields_with_foreign_key = {'art': 'art', 'bewirtschafter': 'bezeichnung'}
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt',
    }
    map_filter_fields_as_list = ['art', 'bewirtschafter']

  def __str__(self):
    return self.id + ' [Art: ' + str(self.art) + ']'


class Hydranten(SimpleModel):
  """
  Hydranten
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    unique=True,
    validators=[
      RegexValidator(regex=hydranten_bezeichnung_regex, message=hydranten_bezeichnung_message)
    ],
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer',
  )
  bewirtschafter = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter',
  )
  feuerloeschgeeignet = BooleanField(verbose_name=' feuerlöschgeeignet?')
  betriebszeit = ForeignKey(
    to=Betriebszeiten,
    verbose_name='Betriebszeit',
    on_delete=RESTRICT,
    db_column='betriebszeit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betriebszeiten',
  )
  entnahme = CharField(
    verbose_name='Entnahme', max_length=255, blank=True, null=True, validators=standard_validators
  )
  hauptwasserzaehler = CharField(
    verbose_name='Hauptwasserzähler',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."hydranten_hro'
    verbose_name = 'Hydrant'
    verbose_name_plural = 'Hydranten'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Hydranten im Eigentum der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'eigentuemer': 'Eigentümer',
      'bewirtschafter': 'Bewirtschafter',
      'feuerloeschgeeignet': 'feuerlöschgeeignet?',
      'betriebszeit': 'Betriebszeit',
      'entnahme': 'Entnahme',
      'hauptwasserzaehler': 'Hauptwasserzähler',
    }
    list_fields_with_foreign_key = {
      'eigentuemer': 'bezeichnung',
      'bewirtschafter': 'bezeichnung',
      'betriebszeit': 'betriebszeit',
    }
    list_actions_assign = [
      {
        'action_name': 'hydranten-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey',
      },
      {
        'action_name': 'hydranten-bewirtschafter',
        'action_title': 'ausgewählten Datensätzen Bewirtschafter direkt zuweisen',
        'field': 'bewirtschafter',
        'type': 'foreignkey',
      },
      {
        'action_name': 'hydranten-feuerloeschgeeignet',
        'action_title': 'ausgewählten Datensätzen feuerlöschgeeignet (ja/nein) direkt zuweisen',
        'field': 'feuerloeschgeeignet',
        'type': 'boolean',
      },
      {
        'action_name': 'hydranten-betriebszeit',
        'action_title': 'ausgewählten Datensätzen Betriebszeit direkt zuweisen',
        'field': 'betriebszeit',
        'type': 'foreignkey',
      },
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'eigentuemer': 'Eigentümer',
      'bewirtschafter': 'Bewirtschafter',
      'feuerloeschgeeignet': 'feuerlöschgeeignet?',
      'betriebszeit': 'Betriebszeit',
      'entnahme': 'Entnahme',
      'hauptwasserzaehler': 'Hauptwasserzähler',
    }
    map_filter_fields_as_list = ['eigentuemer', 'bewirtschafter', 'betriebszeit']

  def __str__(self):
    return self.bezeichnung


class Ingenieurbauwerke(SimpleModel):
  """
  Ingenieurbauwerke
  """

  strasse = ForeignKey(
    to=Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True,
  )
  nummer = CharField(verbose_name='Nummer', max_length=255, validators=standard_validators)
  nummer_asb = CharField(
    verbose_name='ASB-Nummer',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=ingenieurbauwerke_nummer_asb_regex, message=ingenieurbauwerke_nummer_asb_message
      )
    ],
  )
  art = ForeignKey(
    to=Arten_Ingenieurbauwerke,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  baujahr = CharField(
    verbose_name='Baujahr',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=ingenieurbauwerke_baujahr_regex, message=ingenieurbauwerke_baujahr_message
      )
    ],
  )
  ausfuehrung = ForeignKey(
    to=Ausfuehrungen_Ingenieurbauwerke,
    verbose_name='Ausführung',
    on_delete=SET_NULL,
    db_column='ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ausfuehrungen',
    blank=True,
    null=True,
  )
  oben = CharField(
    verbose_name='Verkehrsweg oben',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  unten = CharField(
    verbose_name='Verkehrsweg unten',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  flaeche = DecimalField(
    verbose_name='Fläche (in m²)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Fläche</em></strong> muss mindestens 0,01 m² betragen.'
      ),
      MaxValueValidator(
        Decimal('9999.99'),
        'Die <strong><em>Fläche</em></strong> darf höchstens 9.999,99 m² betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  laenge = DecimalField(
    verbose_name='Länge (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Länge</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'), 'Die <strong><em>Länge</em></strong> darf höchstens 999,99 m betragen.'
      ),
    ],
    blank=True,
    null=True,
  )
  breite = CharField(
    verbose_name='Breite', max_length=255, blank=True, null=True, validators=standard_validators
  )
  hoehe = CharField(
    verbose_name='Höhe', max_length=255, blank=True, null=True, validators=standard_validators
  )
  lichte_weite = DecimalField(
    verbose_name=' lichte Weite (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>lichte Weite</em></strong> muss mindestens 0,01 m betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>lichte Weite</em></strong> darf höchstens 99,99 m betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  lichte_hoehe = CharField(
    verbose_name=' lichte Höhe',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  durchfahrtshoehe = DecimalField(
    verbose_name='Durchfahrtshöhe (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Durchfahrtshöhe</em></strong> muss mindestens 0,01 m betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Durchfahrtshöhe</em></strong> darf höchstens 99,99 m betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  nennweite = CharField(
    verbose_name='Nennweite', max_length=255, blank=True, null=True, validators=standard_validators
  )
  schwerlast = BooleanField(verbose_name='Schwerlast?')
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug"."ingenieurbauwerke_hro'
    verbose_name = 'Ingenieurbauwerk'
    verbose_name_plural = 'Ingenieurbauwerke'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Ingenieurbauwerke im Eigentum der Hanse- und Universitätsstadt Rostock'
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'nummer': 'Nummer',
      'nummer_asb': 'ASB-Nummer',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'strasse': 'Straße',
      'baujahr': 'Baujahr',
      'ausfuehrung': 'Ausführung',
      'oben': 'Verkehrsweg oben',
      'unten': 'Verkehrsweg unten',
      'flaeche': 'Fläche (in m²)',
      'laenge': 'Länge (in m)',
      'breite': 'Breite',
      'hoehe': 'Höhe',
      'lichte_weite': 'lichte Weite (in m)',
      'lichte_hoehe': 'lichte Höhe',
      'durchfahrtshoehe': 'Durchfahrtshöhe (in m)',
      'nennweite': 'Nennweite',
      'schwerlast': 'Schwerlast',
    }
    list_fields_with_decimal = ['flaeche', 'laenge', 'lichte_weite', 'durchfahrtshoehe']
    list_fields_with_foreign_key = {
      'art': 'art',
      'strasse': 'strasse',
      'ausfuehrung': 'ausfuehrung',
    }
    list_actions_assign = [
      {
        'action_name': 'ingenieurbauwerke-art',
        'action_title': 'ausgewählten Datensätzen Art direkt zuweisen',
        'field': 'art',
        'type': 'foreignkey',
      },
      {
        'action_name': 'ingenieurbauwerke-ausfuehrung',
        'action_title': 'ausgewählten Datensätzen Ausführung direkt zuweisen',
        'field': 'ausfuehrung',
        'type': 'foreignkey',
      },
      {
        'action_name': 'ingenieurbauwerke-schwerlast',
        'action_title': 'ausgewählten Datensätzen Schwerlast (ja/nein) direkt zuweisen',
        'field': 'schwerlast',
        'type': 'boolean',
      },
    ]
    map_feature_tooltip_fields = ['nummer']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'nummer': 'Nummer',
      'nummer_asb': 'ASB-Nummer',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'strasse': 'Straße',
      'baujahr': 'Baujahr',
      'ausfuehrung': 'Ausführung',
      'oben': 'Verkehrsweg oben',
      'unten': 'Verkehrsweg unten',
      'schwerlast': 'Schwerlast',
    }
    map_filter_fields_as_list = ['art', 'strasse', 'ausfuehrung']

  def __str__(self):
    return self.nummer


class Jagdkataster_Skizzenebenen(SimpleModel):
  """
  Skizzenebenen des Jagdkatasters
  """

  antragsteller = ForeignKey(
    to=Antragsteller_Jagdkataster_Skizzenebenen,
    verbose_name='Antragsteller:in',
    on_delete=RESTRICT,
    db_column='antragsteller',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_antragsteller',
  )
  thema = ForeignKey(
    to=Themen_Jagdkataster_Skizzenebenen,
    verbose_name='Thema',
    on_delete=RESTRICT,
    db_column='thema',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_themen',
  )
  status = ForeignKey(
    to=Status_Jagdkataster_Skizzenebenen,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status',
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = multiline_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."jagdkataster_skizzenebenen_hro'
    verbose_name = 'Skizzenebene des Jagdkatasters'
    verbose_name_plural = 'Skizzenebenen des Jagdkatasters'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Skizzenebenen des Jagdkatasters der Hanse- und Universitätsstadt Rostock'
    forms_in_high_zoom_mode = True
    geometry_type = 'MultiLineString'
    list_fields = {
      'aktiv': 'aktiv?',
      'antragsteller': 'Antragsteller:in',
      'thema': 'Thema',
      'status': 'Status',
      'bemerkungen': 'Bemerkungen',
    }
    list_fields_with_foreign_key = {
      'antragsteller': 'bezeichnung',
      'thema': 'bezeichnung',
      'status': 'status',
    }
    map_feature_tooltip_fields = ['thema', 'status', 'bemerkungen']
    additional_wms_layers = [
      {
        'title': 'Jagdbereiche',
        'url': 'https://geo.sv.rostock.de/geodienste/jagdkataster/wms',
        'layers': 'hro.jagdkataster.jagdbereiche',
        'proxy': True,
      },
      {
        'title': 'Pachtbögen',
        'url': 'https://geo.sv.rostock.de/geodienste/jagdkataster/wms',
        'layers': 'hro.jagdkataster.pachtboegen',
        'proxy': True,
      },
      {
        'title': 'Jagdbezirke',
        'url': 'https://geo.sv.rostock.de/geodienste/jagdkataster/wms',
        'layers': 'hro.jagdkataster.jagdbezirke',
        'proxy': True,
      },
      {
        'title': 'Flurstücke',
        'url': 'https://geo.sv.rostock.de/geodienste/flurstuecke_hro/wms',
        'layers': 'hro.flurstuecke.flurstuecke',
      },
    ]
    map_filter_fields = {
      'antragsteller': 'Antragsteller:in',
      'thema': 'Thema',
      'status': 'Status',
      'bemerkungen': 'Bemerkungen',
    }
    map_filter_fields_as_list = ['antragsteller', 'thema', 'status']

  def __str__(self):
    ansprechpartner = 'Antragsteller:in: ' + str(self.antragsteller)
    thema = 'Thema: ' + str(self.thema)
    status = 'Status: ' + str(self.status)
    bemerkungen = ', Bemerkungen: ' + self.bemerkungen if self.bemerkungen else ''
    return ansprechpartner + ', ' + thema + ', ' + status + bemerkungen


class Kadaverfunde(SimpleModel):
  """
  Kadaverfunde
  """

  zeitpunkt = DateTimeField('Zeitpunkt')
  tierseuche = ForeignKey(
    to=Tierseuchen,
    verbose_name='Tierseuche',
    on_delete=RESTRICT,
    db_column='tierseuche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tierseuchen',
  )
  geschlecht = ForeignKey(
    to=Geschlechter_Kadaverfunde,
    verbose_name='Geschlecht',
    on_delete=RESTRICT,
    db_column='geschlecht',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_geschlechter',
  )
  altersklasse = ForeignKey(
    to=Altersklassen_Kadaverfunde,
    verbose_name='Altersklasse',
    on_delete=RESTRICT,
    db_column='altersklasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_altersklassen',
  )
  gewicht = PositiveSmallIntegerRangeField(
    verbose_name=' geschätztes Gewicht (in kg)', min_value=1, blank=True, null=True
  )
  zustand = ForeignKey(
    to=Zustaende_Kadaverfunde,
    verbose_name='Zustand',
    on_delete=RESTRICT,
    db_column='zustand',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende',
  )
  art_auffinden = ForeignKey(
    to=Arten_Fallwildsuchen_Kontrollen,
    verbose_name='Art des Auffindens',
    on_delete=RESTRICT,
    db_column='art_auffinden',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten_auffinden',
  )
  witterung = CharField(
    verbose_name='Witterung vor Ort',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  bemerkungen = NullTextField(
    verbose_name='Bemerkungen',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."kadaverfunde_hro'
    verbose_name = 'Kadaverfund'
    verbose_name_plural = 'Kadaverfunde'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Kadaverfunde in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'tierseuche': 'Tierseuche',
      'geschlecht': 'Geschlecht',
      'altersklasse': 'Altersklasse',
      'gewicht': 'geschätztes Gewicht (in kg)',
      'zustand': 'Zustand',
      'art_auffinden': 'Art des Auffindens',
      'zeitpunkt': 'Zeitpunkt',
    }
    list_fields_with_datetime = ['zeitpunkt']
    list_fields_with_foreign_key = {
      'tierseuche': 'bezeichnung',
      'geschlecht': 'bezeichnung',
      'altersklasse': 'bezeichnung',
      'zustand': 'zustand',
      'art_auffinden': 'art',
    }
    map_feature_tooltip_fields = ['tierseuche', 'zeitpunkt']
    map_filter_fields = {
      'tierseuche': 'Tierseuche',
      'geschlecht': 'Geschlecht',
      'altersklasse': 'Altersklasse',
      'zustand': 'Zustand',
      'art_auffinden': 'Art des Auffindens',
      'zeitpunkt': 'Zeitpunkt',
    }
    map_filter_fields_as_list = [
      'tierseuche',
      'geschlecht',
      'altersklasse',
      'zustand',
      'art_auffinden',
    ]

  def __str__(self):
    local_tz = ZoneInfo(settings.TIME_ZONE)
    zeitpunkt_str = sub(r'([+-][0-9]{2}):', '\\1', str(self.zeitpunkt))
    zeitpunkt = (
      datetime.strptime(zeitpunkt_str, '%Y-%m-%d %H:%M:%S%z')
      .replace(tzinfo=timezone.utc)
      .astimezone(local_tz)
    )
    zeitpunkt_str = zeitpunkt.strftime('%d.%m.%Y, %H:%M:%S Uhr')
    return str(self.tierseuche) + ' mit Zeitpunkt ' + zeitpunkt_str + ', '


class Kehrbezirke(SimpleModel):
  """
  Kehrbezirke
  """

  adresse = OneToOneField(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=CASCADE,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
  )
  bevollmaechtigter_bezirksschornsteinfeger = ForeignKey(
    to=Bevollmaechtigte_Bezirksschornsteinfeger,
    verbose_name=' bevollmächtigter Bezirksschornsteinfeger',
    on_delete=RESTRICT,
    db_column='bevollmaechtigter_bezirksschornsteinfeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bevollmaechtigte_bezirksschornsteinfeger',
    blank=True,
    null=True,
  )
  vergabedatum = DateField(verbose_name='Vergabedatum der Adresse', blank=True, null=True)

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."kehrbezirke_hro'
    verbose_name = 'Kehrbezirk'
    verbose_name_plural = 'Kehrbezirke'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = (
      'Kehrbezirke der bevollmächtigten Bezirksschornsteinfeger '
      'in der Hanse- und Universitätsstadt Rostock'
    )
    readonly_fields = ['vergabedatum']
    address_search_long_results = True
    address_type = 'Adresse'
    address_mandatory = True
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bevollmaechtigter_bezirksschornsteinfeger': 'bevollmächtigter Bezirksschornsteinfeger',
      'vergabedatum': 'Vergabedatum der Adresse',
    }
    list_fields_with_date = ['vergabedatum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse_lang',
      'bevollmaechtigter_bezirksschornsteinfeger': 'nachname',
    }
    list_actions_assign = [
      {
        'action_name': 'kehrbezirke-bevollmaechtigter_bezirksschornsteinfeger',
        'action_title': 'ausgewählten Datensätzen bevollmächtigten '
        'Bezirksschornsteinfeger direkt zuweisen',
        'field': 'bevollmaechtigter_bezirksschornsteinfeger',
        'type': 'foreignkey',
      }
    ]

  def __str__(self):
    return (
      str(self.adresse.adresse_lang) + ' zu ' + str(self.bevollmaechtigter_bezirksschornsteinfeger)
    )


class Kindertagespflegeeinrichtungen(SimpleModel):
  """
  Kindertagespflegeeinrichtungen
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  vorname = CharField(verbose_name='Vorname', max_length=255, validators=personennamen_validators)
  nachname = CharField(
    verbose_name='Nachname', max_length=255, validators=personennamen_validators
  )
  plaetze = PositiveSmallIntegerMinField(verbose_name='Plätze', min_value=1, blank=True, null=True)
  zeiten = CharField(verbose_name='Betreuungszeiten', max_length=255, blank=True, null=True)
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."kindertagespflegeeinrichtungen_hro'
    verbose_name = 'Kindertagespflegeeinrichtung'
    verbose_name_plural = 'Kindertagespflegeeinrichtungen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = (
      'Kindertagespflegeeinrichtungen (Tagesmütter und Tagesväter) in der Hanse- '
      'und Universitätsstadt Rostock'
    )
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'plaetze': 'Plätze',
      'zeiten': 'Betreuungszeiten',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse'}
    map_feature_tooltip_fields = ['vorname', 'nachname']
    map_filter_fields = {'vorname': 'Vorname', 'nachname': 'Nachname', 'plaetze': 'Plätze'}

  def __str__(self):
    return (
      self.vorname
      + ' '
      + self.nachname
      + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')
    )


class Kinder_Jugendbetreuung(SimpleModel):
  """
  Kinder- und Jugendbetreuung
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger',
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."kinder_jugendbetreuung_hro'
    verbose_name = 'Kinder- und/oder Jugendbetreuung'
    verbose_name_plural = 'Kinder- und Jugendbetreuung'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Kinder- und Jugendbetreuung in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'traeger': 'bezeichnung'}
    list_actions_assign = [
      {
        'action_name': 'kinder_jugendbetreuung-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'bezeichnung': 'Bezeichnung', 'traeger': 'Träger'}
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return (
      self.bezeichnung
      + ' ['
      + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '')
      + 'Träger: '
      + str(self.traeger)
      + ']'
    )


class Kunst_im_oeffentlichen_Raum(SimpleModel):
  """
  Kunst im öffentlichen Raum
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  ausfuehrung = CharField(
    verbose_name='Ausführung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  schoepfer = CharField(
    verbose_name='Schöpfer', max_length=255, blank=True, null=True, validators=standard_validators
  )
  entstehungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Entstehungsjahr', max_value=get_current_year(), blank=True, null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."kunst_im_oeffentlichen_raum_hro'
    verbose_name = 'Kunst im öffentlichen Raum'
    verbose_name_plural = 'Kunst im öffentlichen Raum'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Kunst im öffentlichen Raum der Hanse- und Universitätsstadt Rostock'
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'ausfuehrung': 'Ausführung',
      'schoepfer': 'Schöpfer',
      'entstehungsjahr': 'Entstehungsjahr',
    }
    map_feature_tooltip_fields = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung


class Ladestationen_Elektrofahrzeuge(SimpleModel):
  """
  Ladestationen für Elektrofahrzeuge
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  geplant = BooleanField(verbose_name=' geplant?')
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  betreiber = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=SET_NULL,
    db_column='betreiber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betreiber',
    blank=True,
    null=True,
  )
  verbund = ForeignKey(
    to=Verbuende_Ladestationen_Elektrofahrzeuge,
    verbose_name='Verbund',
    on_delete=SET_NULL,
    db_column='verbund',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_verbuende',
    blank=True,
    null=True,
  )
  betriebsart = ForeignKey(
    to=Betriebsarten,
    verbose_name='Betriebsart',
    on_delete=RESTRICT,
    db_column='betriebsart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betriebsarten',
  )
  anzahl_ladepunkte = PositiveSmallIntegerMinField(
    verbose_name='Anzahl an Ladepunkten', min_value=1, blank=True, null=True
  )
  arten_ladepunkte = CharField(
    verbose_name='Arten der Ladepunkte',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  ladekarten = ChoiceArrayField(
    CharField(verbose_name='Ladekarten', max_length=255, choices=()),
    verbose_name='Ladekarten',
    blank=True,
    null=True,
  )
  kosten = CharField(
    verbose_name='Kosten', max_length=255, blank=True, null=True, validators=standard_validators
  )
  zeiten = CharField(verbose_name='Öffnungszeiten', max_length=255, blank=True, null=True)
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."ladestationen_elektrofahrzeuge_hro'
    verbose_name = 'Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Ladestationen für Elektrofahrzeuge'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Ladestationen für Elektrofahrzeuge in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {'ladekarten': 'Ladekarten_Ladestationen_Elektrofahrzeuge'}
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'geplant': 'geplant?',
      'bezeichnung': 'Bezeichnung',
      'betreiber': 'Betreiber',
      'verbund': 'Verbund',
      'betriebsart': 'Betriebsart',
      'anzahl_ladepunkte': 'Anzahl an Ladepunkten',
      'ladekarten': 'Ladekarten',
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'betreiber': 'bezeichnung',
      'verbund': 'verbund',
      'betriebsart': 'betriebsart',
    }
    list_actions_assign = [
      {
        'action_name': 'ladestationen_elektrofahrzeuge-geplant',
        'action_title': 'ausgewählten Datensätzen geplant (ja/nein) direkt zuweisen',
        'field': 'geplant',
        'type': 'boolean',
      },
      {
        'action_name': 'ladestationen_elektrofahrzeuge-betreiber',
        'action_title': 'ausgewählten Datensätzen Betreiber direkt zuweisen',
        'field': 'betreiber',
        'type': 'foreignkey',
      },
      {
        'action_name': 'ladestationen_elektrofahrzeuge-verbund',
        'action_title': 'ausgewählten Datensätzen Verbund direkt zuweisen',
        'field': 'verbund',
        'type': 'foreignkey',
      },
      {
        'action_name': 'ladestationen_elektrofahrzeuge-betriebsart',
        'action_title': 'ausgewählten Datensätzen Betriebsart direkt zuweisen',
        'field': 'betriebsart',
        'type': 'foreignkey',
      },
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'geplant': 'geplant?',
      'bezeichnung': 'Bezeichnung',
      'betreiber': 'Betreiber',
      'verbund': 'Verbund',
      'betriebsart': 'Betriebsart',
      'anzahl_ladepunkte': 'Anzahl an Ladepunkten',
      'ladekarten': 'Ladekarten',
    }
    map_filter_fields_as_list = ['betreiber', 'verbund', 'betriebsart']

  def __str__(self):
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Meldedienst_flaechenhaft(SimpleModel):
  """
  Meldedienst (flächenhaft)
  """

  art = ForeignKey(
    to=Arten_Meldedienst_flaechenhaft,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  erfasser = CharField(verbose_name='Erfasser:in', max_length=255, validators=standard_validators)
  erfassungsdatum = DateField(verbose_name='Erfassungsdatum', default=date.today)
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  bearbeitungsbeginn = DateField(verbose_name='Bearbeitungsbeginn', blank=True, null=True)
  geometrie = polygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."meldedienst_flaechenhaft_hro'
    verbose_name = 'Meldedienst (flächenhaft)'
    verbose_name_plural = 'Meldedienst (flächenhaft)'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Meldedienst (flächenhaft) der Hanse- und Universitätsstadt Rostock'
    group_with_users_for_choice_field = 'datenmanagement_meldedienst_flaechenhaft_full'
    geometry_type = 'Polygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'erfasser': 'Erfasser:in',
      'erfassungsdatum': 'Erfassungsdatum',
      'bemerkungen': 'Bemerkungen',
      'bearbeiter': 'Bearbeiter:in',
      'bearbeitungsbeginn': 'Bearbeitungsbeginn',
    }
    list_fields_with_date = ['erfassungsdatum', 'bearbeitungsbeginn']
    list_fields_with_foreign_key = {'art': 'art'}
    map_feature_tooltip_fields = ['art']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'erfasser': 'Erfasser:in',
      'erfassungsdatum': 'Erfassungsdatum',
      'bemerkungen': 'Bemerkungen',
      'bearbeiter': 'Bearbeiter:in',
      'bearbeitungsbeginn': 'Bearbeitungsbeginn',
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return (
      str(self.art)
      + ' [Erfassungsdatum: '
      + datetime.strptime(str(self.erfassungsdatum), '%Y-%m-%d').strftime('%d.%m.%Y')
      + ']'
    )


class Meldedienst_punkthaft(SimpleModel):
  """
  Meldedienst (punkthaft)
  """

  deaktiviert = DateField(verbose_name='Zurückstellung', blank=True, null=True)
  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  art = ForeignKey(
    to=Arten_Meldedienst_punkthaft,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in', max_length=255, validators=standard_validators
  )
  gebaeudeart = ForeignKey(
    to=Gebaeudearten_Meldedienst_punkthaft,
    verbose_name='Gebäudeart',
    on_delete=RESTRICT,
    db_column='gebaeudeart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gebaeudearten',
    blank=True,
    null=True,
  )
  flaeche = DecimalField(
    verbose_name='Fläche (in m²)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Fläche</em></strong> muss mindestens 0,01 m² betragen.'
      ),
      MaxValueValidator(
        Decimal('9999.99'),
        'Die <strong><em>Fläche</em></strong> darf höchstens 9.999,99 m² betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  datum = DateField(verbose_name='Datum', default=date.today)
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."meldedienst_punkthaft_hro'
    verbose_name = 'Meldedienst (punkthaft)'
    verbose_name_plural = 'Meldedienst (punkthaft)'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Meldedienst (punkthaft) der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['deaktiviert']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Zurückstellung',
      'adresse': 'Adresse',
      'art': 'Art',
      'bearbeiter': 'Bearbeiter:in',
      'gebaeudeart': 'Gebäudeart',
      'flaeche': 'Fläche (in m²)',
      'bemerkungen': 'Bemerkungen',
      'datum': 'Datum',
    }
    list_fields_with_date = ['deaktiviert', 'datum']
    list_fields_with_decimal = ['flaeche']
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'art': 'art',
      'gebaeudeart': 'bezeichnung',
    }
    list_actions_assign = [
      {
        'action_name': 'meldedienst_punkthaft-gebaeudeart',
        'action_title': 'ausgewählten Datensätzen Gebäudeart direkt zuweisen',
        'field': 'gebaeudeart',
        'type': 'foreignkey',
      },
      {
        'action_name': 'meldedienst_punkthaft-datum',
        'action_title': 'ausgewählten Datensätzen Datum direkt zuweisen',
        'field': 'datum',
        'type': 'date',
        'value_required': True,
      },
    ]
    map_heavy_load_limit = 600
    map_feature_tooltip_fields = ['art']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bearbeiter': 'Bearbeiter:in',
      'gebaeudeart': 'Gebäudeart',
      'bemerkungen': 'Bemerkungen',
      'datum': 'Datum',
    }
    map_filter_fields_as_list = ['art', 'gebaeudeart']

  def __str__(self):
    return (
      str(self.art)
      + ' [Datum: '
      + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y')
      + (', Adresse: ' + str(self.adresse) if self.adresse else '')
      + ']'
    )


class Meldedienst_Qualitaetsverbesserung(SimpleModel):
  """
  Meldedienst (Qualitätsverbesserung Liegenschaftskataster)
  """

  kategorie = ForeignKey(
    to=Kategorien_Qualitaetsverbesserung,
    verbose_name='Kategorie',
    on_delete=RESTRICT,
    db_column='kategorie',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_kategorien',
  )
  erfasser = CharField(verbose_name='Erfasser:in', max_length=255, validators=standard_validators)
  erfassungsdatum = DateField(verbose_name='Erfassungsdatum', default=date.today)
  lage = CharField(
    verbose_name='Lage',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  bearbeitungsbeginn = DateField(verbose_name='Bearbeitungsbeginn', blank=True, null=True)
  geometrie = polygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."meldedienst_qualitaetsverbesserung_hro'
    verbose_name = 'Meldedienst (Qualitätsverbesserung Liegenschaftskataster)'
    verbose_name_plural = 'Meldedienst (Qualitätsverbesserung Liegenschaftskataster)'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = ('Meldedienst (Qualitätsverbesserung Liegenschaftskataster)'
                   'der Hanse- und Universitätsstadt Rostock')
    group_with_users_for_choice_field = 'datenmanagement_meldedienst_qualitaetsverbesserung_full'
    geometry_type = 'Polygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'kategorie': 'Kategorie',
      'erfasser': 'Erfasser:in',
      'erfassungsdatum': 'Erfassungsdatum',
      'lage': 'Lage',
      'bemerkungen': 'Bemerkungen',
      'bearbeiter': 'Bearbeiter:in',
      'bearbeitungsbeginn': 'Bearbeitungsbeginn',
    }
    list_fields_with_date = ['erfassungsdatum', 'bearbeitungsbeginn']
    list_fields_with_foreign_key = {'kategorie': 'kategorie'}
    map_feature_tooltip_fields = ['kategorie']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'kategorie': 'Kategorie',
      'erfasser': 'Erfasser:in',
      'erfassungsdatum': 'Erfassungsdatum',
      'lage': 'Lage',
      'bemerkungen': 'Bemerkungen',
      'bearbeiter': 'Bearbeiter:in',
      'bearbeitungsbeginn': 'Bearbeitungsbeginn',
    }
    map_filter_fields_as_list = ['kategorie']

  def __str__(self):
    return (
      str(self.kategorie)
      + ' [Erfassungsdatum: '
      + datetime.strptime(str(self.erfassungsdatum), '%Y-%m-%d').strftime('%d.%m.%Y')
      + ']'
    )


class Mobilfunkantennen(SimpleModel):
  """
  Mobilfunkantennen
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  stob = CharField(
    verbose_name='Standortbescheinigungsnummer',
    max_length=255,
    validators=[
      RegexValidator(regex=mobilfunkantennen_stob_regex, message=mobilfunkantennen_stob_message)
    ],
  )
  erteilungsdatum = DateField(verbose_name='Erteilungsdatum', default=date.today)
  techniken = ArrayField(
    CharField(
      verbose_name='Techniken',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators,
    ),
    verbose_name='Techniken',
    blank=True,
    null=True,
  )
  betreiber = ArrayField(
    CharField(
      verbose_name='Betreiber',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators,
    ),
    verbose_name='Betreiber',
    blank=True,
    null=True,
  )
  montagehoehe = CharField(
    verbose_name='Montagehöhe',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  anzahl_gsm = PositiveSmallIntegerMinField(
    verbose_name='Anzahl GSM-Einheiten', min_value=1, blank=True, null=True
  )
  anzahl_umts = PositiveSmallIntegerMinField(
    verbose_name='Anzahl UMTS-Einheiten', min_value=1, blank=True, null=True
  )
  anzahl_lte = PositiveSmallIntegerMinField(
    verbose_name='Anzahl LTE-Einheiten', min_value=1, blank=True, null=True
  )
  anzahl_sonstige = PositiveSmallIntegerMinField(
    verbose_name='Anzahl sonstige Einheiten', min_value=1, blank=True, null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."mobilfunkantennen_hro'
    verbose_name = 'Mobilfunkantenne'
    verbose_name_plural = 'Mobilfunkantennen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Mobilfunkantennen in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'stob': 'Standortbescheinigungsnummer',
      'erteilungsdatum': 'Erteilungsdatum',
      'techniken': 'Techniken',
      'betreiber': 'Betreiber',
      'montagehoehe': 'Montagehöhe',
      'anzahl_gsm': 'Anzahl GSM-Einheiten',
      'anzahl_umts': 'Anzahl UMTS-Einheiten',
      'anzahl_lte': 'Anzahl LTE-Einheiten',
      'anzahl_sonstige': 'Anzahl sonstige Einheiten',
    }
    list_fields_with_date = ['erteilungsdatum']
    list_fields_with_foreign_key = {'adresse': 'adresse'}
    map_feature_tooltip_fields = ['stob']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'stob': 'Standortbescheinigungsnummer',
      'erteilungsdatum': 'Erteilungsdatum',
      'techniken': 'Techniken',
      'betreiber': 'Betreiber',
      'montagehoehe': 'Montagehöhe',
      'anzahl_gsm': 'Anzahl GSM-Einheiten',
      'anzahl_umts': 'Anzahl UMTS-Einheiten',
      'anzahl_lte': 'Anzahl LTE-Einheiten',
      'anzahl_sonstige': 'Anzahl sonstige Einheiten',
    }

  def __str__(self):
    return self.stob


class Mobilpunkte(SimpleModel):
  """
  Mobilpunkte
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  angebote = ChoiceArrayField(
    CharField(verbose_name='Angebote', max_length=255, choices=()), verbose_name='Angebote'
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."mobilpunkte_hro'
    verbose_name = 'Mobilpunkt'
    verbose_name_plural = 'Mobilpunkte'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Mobilpunkte in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {'angebote': 'Angebote_Mobilpunkte'}
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'angebote': 'Angebote',
      'website': 'Website',
    }
    map_feature_tooltip_fields = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung


class Naturdenkmale(SimpleModel):
  """
  Naturdenkmale
  """

  typ = ForeignKey(
    to=Typen_Naturdenkmale,
    verbose_name='Typ',
    on_delete=RESTRICT,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
  )
  nummer = PositiveSmallIntegerMinField(
    verbose_name='Nummer',
    min_value=1,
    unique=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  rechtsvorschrift_festsetzung = CharField(
    verbose_name='Rechtsvorschrift zur Festsetzung',
    max_length=255,
    validators=standard_validators,
    blank=True,
    null=True,
  )
  datum_rechtsvorschrift_festsetzung = DateField(
    verbose_name='Datum der Rechtsvorschrift zur Festsetzung', blank=True, null=True
  )
  pdf = FileField(
    verbose_name='Datenblatt',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PDF_PATH_PREFIX_PUBLIC + '_naturdenkmale'),
    max_length=255,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."_naturdenkmale_hro'
    verbose_name = 'Naturdenkmal'
    verbose_name_plural = 'Naturdenkmale'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Naturdenkmale in der Hanse- und Universitätsstadt Rostock'
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'typ': 'Typ',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'rechtsvorschrift_festsetzung': 'Rechtsvorschrift zur Festsetzung',
      'datum_rechtsvorschrift_festsetzung': 'Datum der Rechtsvorschrift zur Festsetzung',
      'pdf': 'Datenblatt',
    }
    list_fields_with_date = ['datum_rechtsvorschrift_festsetzung']
    list_fields_with_foreign_key = {
      'typ': 'typ',
    }
    list_actions_assign = [
      {
        'action_name': 'naturdenkmale-typ',
        'action_title': 'ausgewählten Datensätzen Typ direkt zuweisen',
        'field': 'typ',
        'type': 'foreignkey',
      },
      {
        'action_name': 'naturdenkmale-rechtsvorschrift_festsetzung',
        'action_title': 'ausgewählten Datensätzen Rechtsvorschrift zur Festsetzung direkt zuweisen',  # noqa: E501
        'field': 'rechtsvorschrift_festsetzung',
        'type': 'text',
      },
      {
        'action_name': 'naturdenkmale-datum_rechtsvorschrift_festsetzung',
        'action_title': 'ausgewählten Datensätzen Datum der Rechtsvorschrift zur Festsetzung direkt zuweisen',  # noqa: E501
        'field': 'datum_rechtsvorschrift_festsetzung',
        'type': 'date',
      },
    ]
    map_feature_tooltip_fields = ['nummer']
    map_filter_fields = {
      'typ': 'Typ',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'rechtsvorschrift_festsetzung': 'Rechtsvorschrift zur Festsetzung',
      'datum_rechtsvorschrift_festsetzung': 'Datum der Rechtsvorschrift zur Festsetzung',
    }
    map_filter_fields_as_list = ['typ']

  def __str__(self):
    return f'{self.nummer}'


post_delete.connect(delete_pdf, sender=Naturdenkmale)


class Notfalltreffpunkte(SimpleModel):
  """
  Notfalltreffpunkte/Wärmeinseln
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  art = ForeignKey(
    to=Arten_Notfalltreffpunkte,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  standort = CharField(verbose_name='Standort', max_length=255, validators=standard_validators)
  ressource = CharField(verbose_name='Ressource', max_length=255, validators=standard_validators)
  personal = CharField(verbose_name='Personal', max_length=255, validators=standard_validators)
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."notfalltreffpunkte_hro'
    verbose_name = 'Notfalltreffpunkt/Wärmeinsel'
    verbose_name_plural = 'Notfalltreffpunkte/Wärmeinseln'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Notfalltreffpunkte/Wärmeinseln in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'standort': 'Standort',
      'ressource': 'Ressource',
      'personal': 'Personal',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'art': 'art'}
    map_feature_tooltip_fields = ['standort']
    map_filter_fields = {
      'art': 'Art',
      'standort': 'Standort',
      'ressource': 'Ressource',
      'personal': 'Personal',
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return (
      self.standort
      + ' ['
      + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '')
      + 'Art: '
      + str(self.art)
      + ']'
    )


class Parkmoeglichkeiten(SimpleModel):
  """
  Parkmöglichkeiten
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  art = ForeignKey(
    to=Arten_Parkmoeglichkeiten,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  parkandride = BooleanField(verbose_name='P+R?', blank=True, null=True)
  standort = CharField(verbose_name='Standort', max_length=255, validators=standard_validators)
  betreiber = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=SET_NULL,
    db_column='betreiber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betreiber',
    blank=True,
    null=True,
  )
  stellplaetze_pkw = PositiveSmallIntegerMinField(
    verbose_name='Pkw-Stellplätze', min_value=1, blank=True, null=True
  )
  stellplaetze_wohnmobil = PositiveSmallIntegerMinField(
    verbose_name='Wohnmobilstellplätze', min_value=1, blank=True, null=True
  )
  stellplaetze_bus = PositiveSmallIntegerMinField(
    verbose_name='Busstellplätze', min_value=1, blank=True, null=True
  )
  gebuehren_halbe_stunde = DecimalField(
    verbose_name='Gebühren pro ½ h (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro ½ h</em></strong> müssen mindestens 0,01 € betragen.',
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro ½ h</em></strong> dürfen höchstens 9,99 € betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  gebuehren_eine_stunde = DecimalField(
    verbose_name='Gebühren pro 1 h (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro 1 h</em></strong> müssen mindestens 0,01 € betragen.',
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro 1 h</em></strong> dürfen höchstens 9,99 € betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  gebuehren_zwei_stunden = DecimalField(
    verbose_name='Gebühren pro 2 h (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro 2 h</em></strong> müssen mindestens 0,01 € betragen.',
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro 2 h</em></strong> dürfen höchstens 9,99 € betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  gebuehren_ganztags = DecimalField(
    verbose_name='Gebühren ganztags (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren ganztags</em></strong> müssen mindestens 0,01 € betragen.',
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren ganztags</em></strong> dürfen höchstens 9,99 € betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  bemerkungen = CharField(
    verbose_name='Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."parkmoeglichkeiten_hro'
    verbose_name = 'Parkmöglichkeit'
    verbose_name_plural = 'Parkmöglichkeiten'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Parkmöglichkeiten in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'parkandride': 'P+R',
      'standort': 'Standort',
      'betreiber': 'Betreiber',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'art': 'art', 'betreiber': 'bezeichnung'}
    map_feature_tooltip_fields = ['art', 'standort']
    map_filter_fields = {
      'art': 'Art',
      'parkandride': 'P+R',
      'standort': 'Standort',
      'betreiber': 'Betreiber',
    }
    map_filter_fields_as_list = ['art', 'betreiber']

  def __str__(self):
    return (
      str(self.art)
      + ' '
      + self.standort
      + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')
    )


class Pflegeeinrichtungen(SimpleModel):
  """
  Pflegeeinrichtungen
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  art = ForeignKey(
    to=Arten_Pflegeeinrichtungen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  betreiber = CharField(
    verbose_name='Betreiber:in', max_length=255, validators=standard_validators
  )
  plaetze = PositiveSmallIntegerMinField(verbose_name='Plätze', min_value=1, blank=True, null=True)
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."pflegeeinrichtungen_hro'
    verbose_name = 'Pflegeeinrichtung'
    verbose_name_plural = 'Pflegeeinrichtungen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Pflegeeinrichtungen in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'betreiber': 'Betreiber:in',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'art': 'art'}
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'art': 'Art', 'bezeichnung': 'Bezeichnung', 'betreiber': 'Betreiber:in'}
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return (
      self.bezeichnung
      + ' ['
      + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '')
      + 'Art: '
      + str(self.art)
      + ']'
    )


class Reinigungsreviere(SimpleModel):
  """
  Reinigungsreviere
  """

  gemeindeteil = ForeignKey(
    to=Gemeindeteile,
    verbose_name='Gemeindeteil',
    on_delete=SET_NULL,
    db_column='gemeindeteil',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gemeindeteile',
    blank=True,
    null=True,
  )
  nummer = PositiveSmallIntegerMinField(verbose_name='Nummer', min_value=1, blank=True, null=True)
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators,
    blank=True,
    null=True,
  )
  geometrie = multipolygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_gemeindeteilbezug"."reinigungsreviere_hro'
    verbose_name = 'Reinigungsreviere'
    verbose_name_plural = 'Reinigungsreviere'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Reinigungsreviere der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    address_type = 'Gemeindeteil'
    address_mandatory = False
    geometry_type = 'MultiPolygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'gemeindeteil': 'Gemeindeteil',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
    }
    list_fields_with_foreign_key = {'gemeindeteil': 'gemeindeteil'}
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'gemeindeteil': 'Gemeindeteil',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
    }
    map_filter_fields_as_list = ['gemeindeteil']
    additional_wms_layers = [
      {
        'title': 'Reinigungsreviere',
        'url': 'https://geo.sv.rostock.de/geodienste/reinigungsreviere/wms',
        'layers': 'hro.reinigungsreviere.reinigungsreviere',
      },
      {
        'title': 'Geh- und Radwegereinigung',
        'url': 'https://geo.sv.rostock.de/geodienste/geh_und_radwegereinigung/wms',
        'layers': 'hro.geh_und_radwegereinigung.geh_und_radwegereinigung_flaechenhaft,'
        'hro.geh_und_radwegereinigung.geh_und_radwegereinigung_linienhaft',
      },
      {
        'title': 'Straßenreinigung',
        'url': 'https://geo.sv.rostock.de/geodienste/strassenreinigung/wms',
        'layers': 'hro.strassenreinigung.strassenreinigung',
      },
    ]

  def __str__(self):
    return self.bezeichnung + (' (Nummer: ' + str(self.nummer) + ')' if self.nummer else '')


class Reisebusparkplaetze_Terminals(SimpleModel):
  """
  Reisebusparkplätze und -terminals
  """

  art = ForeignKey(
    to=Arten_Reisebusparkplaetze_Terminals,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  stellplaetze = PositiveSmallIntegerMinField(verbose_name='Stellplätze', min_value=1)
  gebuehren = BooleanField(verbose_name='Gebühren?')
  einschraenkungen = CharField(
    verbose_name='Einschränkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."reisebusparkplaetze_terminals_hro'
    verbose_name = 'Reisebusparkplatz oder -terminal'
    verbose_name_plural = 'Reisebusparkplätze und -terminals'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Reisebusparkplätze und -terminals in der Hanse- und Universitätsstadt Rostock'
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'stellplaetze': 'Stellplätze',
      'gebuehren': 'Gebühren',
      'einschraenkungen': 'Einschränkungen',
    }
    list_fields_with_foreign_key = {'art': 'art'}
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'stellplaetze': 'Stellplätze',
      'gebuehren': 'Gebühren',
      'einschraenkungen': 'Einschränkungen',
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return str(self.art) + ' ' + self.bezeichnung


class Rettungswachen(SimpleModel):
  """
  Rettungswachen
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger',
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."rettungswachen_hro'
    verbose_name = 'Rettungswache'
    verbose_name_plural = 'Rettungswachen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Rettungswachen in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'traeger': 'bezeichnung'}
    list_actions_assign = [
      {
        'action_name': 'rettungswachen-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'bezeichnung': 'Bezeichnung', 'traeger': 'Träger'}
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return (
      self.bezeichnung
      + ' ['
      + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '')
      + 'Träger: '
      + str(self.traeger)
      + ']'
    )


class Schiffsliegeplaetze(SimpleModel):
  """
  Schiffsliegeplätze
  """

  hafen = ForeignKey(
    to=Haefen,
    verbose_name='Hafen',
    on_delete=CASCADE,
    db_column='hafen',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_haefen',
  )
  liegeplatznummer = CharField(
    verbose_name='Liegeplatz', max_length=255, validators=standard_validators
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  liegeplatzlaenge = DecimalField(
    verbose_name='Liegeplatzlänge (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Liegeplatzlänge</em></strong> muss mindestens 0,01 m betragen.',
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Liegeplatzlänge</em></strong> darf höchstens 999,99 m betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  zulaessiger_tiefgang = DecimalField(
    verbose_name=' zulässiger Tiefgang (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>zulässige Tiefgang</em></strong> muss mindestens 0,01 m betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der <strong><em>zulässige Tiefgang</em></strong> darf höchstens 99,99 m betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  zulaessige_schiffslaenge = DecimalField(
    verbose_name=' zulässige Schiffslänge (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>zulässige Schiffslänge</em></strong> muss mindestens 0,01 m betragen.',
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>zulässige Schiffslänge</em></strong> darf höchstens 999,99 m betragen.',
      ),
    ],
    blank=True,
    null=True,
  )
  kaihoehe = DecimalField(
    verbose_name='Kaihöhe (in m)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Kaihöhe</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'), 'Die <strong><em>Kaihöhe</em></strong> darf höchstens 9,99 m betragen.'
      ),
    ],
    blank=True,
    null=True,
  )
  pollerzug = CharField(
    verbose_name='Pollerzug', max_length=255, blank=True, null=True, validators=standard_validators
  )
  poller_von = CharField(
    verbose_name='Poller (von)',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  poller_bis = CharField(
    verbose_name='Poller (bis)',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  geometrie = polygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."schiffsliegeplaetze_hro'
    verbose_name = 'Schiffsliegeplatz'
    verbose_name_plural = 'Schiffsliegeplätze'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Schiffsliegeplätze der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    geometry_type = 'Polygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'hafen': 'Hafen',
      'liegeplatznummer': 'Liegeplatz',
      'bezeichnung': 'Bezeichnung',
      'zulaessiger_tiefgang': 'zulässiger Tiefgang (in m)',
    }
    list_fields_with_decimal = ['zulaessiger_tiefgang']
    list_fields_with_foreign_key = {'hafen': 'bezeichnung'}
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'hafen': 'Hafen',
      'liegeplatznummer': 'Liegeplatz',
      'bezeichnung': 'Bezeichnung',
      'zulaessiger_tiefgang': 'zulässiger Tiefgang (in m)',
    }
    map_filter_fields_as_list = ['hafen']

  def __str__(self):
    return self.liegeplatznummer + ', ' + self.bezeichnung + ' [Hafen: ' + str(self.hafen) + ']'


class Schutzzaeune_Tierseuchen(SimpleModel):
  """
  Schutzzäune gegen Tierseuchen
  """

  tierseuche = ForeignKey(
    to=Tierseuchen,
    verbose_name='Tierseuche',
    on_delete=RESTRICT,
    db_column='tierseuche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tierseuchen',
  )
  zustand = ForeignKey(
    to=Zustaende_Schutzzaeune_Tierseuchen,
    verbose_name='Zustand',
    on_delete=RESTRICT,
    db_column='zustand',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende',
  )
  laenge = PositiveIntegerField(verbose_name='Länge (in m)', default=0)
  geometrie = multiline_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."schutzzaeune_tierseuchen_hro'
    verbose_name = 'Schutzzaun gegen eine Tierseuche'
    verbose_name_plural = 'Schutzzäune gegen Tierseuchen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Schutzzäune gegen Tierseuchen in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = ['laenge']
    geometry_type = 'MultiLineString'
    list_fields = {
      'aktiv': 'aktiv?',
      'tierseuche': 'Tierseuche',
      'laenge': 'Länge (in m)',
      'zustand': 'Zustand',
    }
    list_fields_with_foreign_key = {'tierseuche': 'bezeichnung', 'zustand': 'zustand'}
    list_actions_assign = [
      {
        'action_name': 'schutzzaeune_tierseuchen-zustand',
        'action_title': 'ausgewählten Datensätzen Zustand direkt zuweisen',
        'field': 'zustand',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['zustand']
    map_filter_fields = {'tierseuche': 'Tierseuche', 'zustand': 'Zustand'}
    map_filter_fields_as_list = ['tierseuche', 'zustand']

  def __str__(self):
    return str(self.tierseuche) + ', ' + str(self.zustand)


class Sportanlagen(SimpleModel):
  """
  Sportanlagen
  """

  art = ForeignKey(
    to=Arten_Sportanlagen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger',
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PUBLIC + 'sportanlagen'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."sportanlagen_hro'
    verbose_name = 'Sportanlage'
    verbose_name_plural = 'Sportanlagen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Sportanlagen in der Hanse- und Universitätsstadt Rostock'
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
      'foto': 'Foto',
    }
    list_fields_with_foreign_key = {'art': 'art', 'traeger': 'bezeichnung'}
    list_actions_assign = [
      {
        'action_name': 'sportanlagen-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'art': 'Art', 'bezeichnung': 'Bezeichnung', 'traeger': 'Träger'}
    map_filter_fields_as_list = ['art', 'traeger']

  def __str__(self):
    return self.bezeichnung + ' [Art: ' + str(self.art) + ']'


pre_save.connect(set_pre_save_instance, sender=Sportanlagen)

post_save.connect(photo_post_processing, sender=Sportanlagen)

post_save.connect(delete_photo_after_emptied, sender=Sportanlagen)

post_delete.connect(delete_photo, sender=Sportanlagen)


class Sporthallen(SimpleModel):
  """
  Sporthallen
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger',
  )
  sportart = ForeignKey(
    to=Sportarten,
    verbose_name='Sportart',
    on_delete=RESTRICT,
    db_column='sportart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_sportarten',
  )
  barrierefrei = BooleanField(verbose_name=' barrierefrei?', blank=True, null=True)
  zeiten = CharField(verbose_name='Öffnungszeiten', max_length=255, blank=True, null=True)
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PUBLIC + 'sporthallen'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."sporthallen_hro'
    verbose_name = 'Sporthalle'
    verbose_name_plural = 'Sporthallen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Sporthallen in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
      'sportart': 'Sportart',
      'foto': 'Foto',
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'traeger': 'bezeichnung',
      'sportart': 'bezeichnung',
    }
    list_actions_assign = [
      {
        'action_name': 'sporthallen-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey',
      },
      {
        'action_name': 'sporthallen-sportart',
        'action_title': 'ausgewählten Datensätzen Sportart direkt zuweisen',
        'field': 'sportart',
        'type': 'foreignkey',
      },
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'bezeichnung': 'Bezeichnung', 'traeger': 'Träger', 'sportart': 'Sportart'}
    map_filter_fields_as_list = ['traeger', 'sportart']

  def __str__(self):
    return (
      self.bezeichnung
      + ' ['
      + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '')
      + 'Träger: '
      + str(self.traeger)
      + ', Sportart: '
      + str(self.sportart)
      + ']'
    )


pre_save.connect(set_pre_save_instance, sender=Sporthallen)

post_save.connect(photo_post_processing, sender=Sporthallen)

post_save.connect(delete_photo_after_emptied, sender=Sporthallen)

post_delete.connect(delete_photo, sender=Sporthallen)


class Stadtteil_Begegnungszentren(SimpleModel):
  """
  Stadtteil- und Begegnungszentren
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger',
  )
  barrierefrei = BooleanField(verbose_name=' barrierefrei?', blank=True, null=True)
  zeiten = CharField(verbose_name='Öffnungszeiten', max_length=255, blank=True, null=True)
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."stadtteil_begegnungszentren_hro'
    verbose_name = 'Stadtteil- und/oder Begegnungszentrum'
    verbose_name_plural = 'Stadtteil- und Begegnungszentren'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Stadtteil- und Begegnungszentren in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse', 'traeger': 'bezeichnung'}
    list_actions_assign = [
      {
        'action_name': 'stadtteil_begegnungszentren-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'bezeichnung': 'Bezeichnung', 'traeger': 'Träger'}
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return (
      self.bezeichnung
      + ' ['
      + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '')
      + 'Träger: '
      + str(self.traeger)
      + ']'
    )


class Standortqualitaeten_Geschaeftslagen_Sanierungsgebiet(SimpleModel):
  """
  Standortqualitäten von Geschäftslagen im Sanierungsgebiet
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bewertungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Bewertungsjahr',
    min_value=1990,
    max_value=get_current_year(),
    default=get_current_year(),
  )
  quartier = ForeignKey(
    to=Quartiere,
    verbose_name='Quartier',
    on_delete=RESTRICT,
    db_column='quartier',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_quartiere',
  )
  kundschaftskontakte_anfangswert = DecimalField(
    verbose_name='Kundschaftskontakte (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Kundschaftskontakte</em></strong> '
        'muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Kundschaftskontakte</em></strong> '
        'darf höchstens 99,99 betragen.',
      ),
    ],
  )
  kundschaftskontakte_endwert = DecimalField(
    verbose_name='Kundschaftskontakte (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Kundschaftskontakte</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Kundschaftskontakte</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  verkehrsanbindung_anfangswert = DecimalField(
    verbose_name='Verkehrsanbindung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Verkehrsanbindung</em></strong> '
        'muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Verkehrsanbindung</em></strong> '
        'darf höchstens 99,99 betragen.',
      ),
    ],
  )
  verkehrsanbindung_endwert = DecimalField(
    verbose_name='Verkehrsanbindung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Verkehrsanbindung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Verkehrsanbindung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  ausstattung_anfangswert = DecimalField(
    verbose_name='Ausstattung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Ausstattung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Ausstattung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  ausstattung_endwert = DecimalField(
    verbose_name='Ausstattung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Ausstattung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Ausstattung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  beeintraechtigung_anfangswert = DecimalField(
    verbose_name='Beeinträchtigung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Beeinträchtigung</em></strong> '
        'muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Beeinträchtigung</em></strong> '
        'darf höchstens 99,99 betragen.',
      ),
    ],
  )
  beeintraechtigung_endwert = DecimalField(
    verbose_name='Beeinträchtigung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Beeinträchtigung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Beeinträchtigung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  standortnutzung_anfangswert = DecimalField(
    verbose_name='Standortnutzung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Standortnutzung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Standortnutzung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  standortnutzung_endwert = DecimalField(
    verbose_name='Standortnutzung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Standortnutzung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Standortnutzung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro'
    verbose_name = 'Standortqualität einer Geschäftslage im Sanierungsgebiet'
    verbose_name_plural = 'Standortqualitäten von Geschäftslagen im Sanierungsgebiet'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = (
      'Standortqualitäten von Geschäftslagen '
      'im Sanierungsgebiet der Hanse- und Universitätsstadt Rostock'
    )
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bewertungsjahr': 'Bewertungsjahr',
      'quartier': 'Quartier',
      'kundschaftskontakte_anfangswert': 'Kundschaftskontakte (Anfangswert)',
      'kundschaftskontakte_endwert': 'Kundschaftskontakte (Endwert)',
      'verkehrsanbindung_anfangswert': 'Verkehrsanbindung (Anfangswert)',
      'verkehrsanbindung_endwert': 'Verkehrsanbindung (Endwert)',
      'ausstattung_anfangswert': 'Ausstattung (Anfangswert)',
      'ausstattung_endwert': 'Ausstattung (Endwert)',
      'beeintraechtigung_anfangswert': 'Beeinträchtigung (Anfangswert)',
      'beeintraechtigung_endwert': 'Beeinträchtigung (Endwert)',
      'standortnutzung_anfangswert': 'Standortnutzung (Anfangswert)',
      'standortnutzung_endwert': 'Standortnutzung (Endwert)',
    }
    list_fields_with_decimal = [
      'kundschaftskontakte_anfangswert',
      'kundschaftskontakte_endwert',
      'verkehrsanbindung_anfangswert',
      'verkehrsanbindung_endwert',
      'ausstattung_anfangswert',
      'ausstattung_endwert',
      'beeintraechtigung_anfangswert',
      'beeintraechtigung_endwert',
      'standortnutzung_anfangswert',
      'standortnutzung_endwert',
    ]
    list_fields_with_foreign_key = {'adresse': 'adresse', 'quartier': 'code'}
    map_feature_tooltip_fields = ['adresse']
    map_filter_fields = {
      'adresse': 'Adresse',
      'bewertungsjahr': 'Bewertungsjahr',
      'quartier': 'Quartier',
    }
    map_filter_fields_as_list = ['quartier']

  def __str__(self):
    return str(self.adresse)


class Standortqualitaeten_Wohnlagen_Sanierungsgebiet(SimpleModel):
  """
  Standortqualitäten von Wohnlagen im Sanierungsgebiet
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bewertungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Bewertungsjahr',
    min_value=1990,
    max_value=get_current_year(),
    default=get_current_year(),
  )
  quartier = ForeignKey(
    to=Quartiere,
    verbose_name='Quartier',
    on_delete=RESTRICT,
    db_column='quartier',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_quartiere',
  )
  gesellschaftslage_anfangswert = DecimalField(
    verbose_name='Gesellschaftslage (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Gesellschaftslage</em></strong> '
        'muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Gesellschaftslage</em></strong> '
        'darf höchstens 99,99 betragen.',
      ),
    ],
  )
  gesellschaftslage_endwert = DecimalField(
    verbose_name='Gesellschaftslage (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Gesellschaftslage</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Gesellschaftslage</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  verkehrsanbindung_anfangswert = DecimalField(
    verbose_name='Verkehrsanbindung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Verkehrsanbindung</em></strong> '
        'muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Verkehrsanbindung</em></strong> '
        'darf höchstens 99,99 betragen.',
      ),
    ],
  )
  verkehrsanbindung_endwert = DecimalField(
    verbose_name='Verkehrsanbindung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Verkehrsanbindung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Verkehrsanbindung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  ausstattung_anfangswert = DecimalField(
    verbose_name='Ausstattung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Ausstattung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Ausstattung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  ausstattung_endwert = DecimalField(
    verbose_name='Ausstattung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Ausstattung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Ausstattung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  beeintraechtigung_anfangswert = DecimalField(
    verbose_name='Beeinträchtigung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Beeinträchtigung</em></strong> '
        'muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Beeinträchtigung</em></strong> '
        'darf höchstens 99,99 betragen.',
      ),
    ],
  )
  beeintraechtigung_endwert = DecimalField(
    verbose_name='Beeinträchtigung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Beeinträchtigung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Beeinträchtigung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  standortnutzung_anfangswert = DecimalField(
    verbose_name='Standortnutzung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Standortnutzung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Standortnutzung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  standortnutzung_endwert = DecimalField(
    verbose_name='Standortnutzung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Standortnutzung</em></strong> muss mindestens 0,01 betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Standortnutzung</em></strong> darf höchstens 99,99 betragen.',
      ),
    ],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."standortqualitaeten_wohnlagen_sanierungsgebiet_hro'
    verbose_name = 'Standortqualität einer Wohnlage im Sanierungsgebiet'
    verbose_name_plural = 'Standortqualitäten von Wohnlagen im Sanierungsgebiet'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = (
      'Standortqualitäten von Wohnlagen '
      'im Sanierungsgebiet der Hanse- und Universitätsstadt Rostock'
    )
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bewertungsjahr': 'Bewertungsjahr',
      'quartier': 'Quartier',
      'gesellschaftslage_anfangswert': 'Gesellschaftslage (Anfangswert)',
      'gesellschaftslage_endwert': 'Gesellschaftslage (Endwert)',
      'verkehrsanbindung_anfangswert': 'Verkehrsanbindung (Anfangswert)',
      'verkehrsanbindung_endwert': 'Verkehrsanbindung (Endwert)',
      'ausstattung_anfangswert': 'Ausstattung (Anfangswert)',
      'ausstattung_endwert': 'Ausstattung (Endwert)',
      'beeintraechtigung_anfangswert': 'Beeinträchtigung (Anfangswert)',
      'beeintraechtigung_endwert': 'Beeinträchtigung (Endwert)',
      'standortnutzung_anfangswert': 'Standortnutzung (Anfangswert)',
      'standortnutzung_endwert': 'Standortnutzung (Endwert)',
    }
    list_fields_with_decimal = [
      'gesellschaftslage_anfangswert',
      'gesellschaftslage_endwert',
      'verkehrsanbindung_anfangswert',
      'verkehrsanbindung_endwert',
      'ausstattung_anfangswert',
      'ausstattung_endwert',
      'beeintraechtigung_anfangswert',
      'beeintraechtigung_endwert',
      'standortnutzung_anfangswert',
      'standortnutzung_endwert',
    ]
    list_fields_with_foreign_key = {'adresse': 'adresse', 'quartier': 'code'}
    map_feature_tooltip_fields = ['adresse']
    map_filter_fields = {
      'adresse': 'Adresse',
      'bewertungsjahr': 'Bewertungsjahr',
      'quartier': 'Quartier',
    }
    map_filter_fields_as_list = ['quartier']

  def __str__(self):
    return str(self.adresse)


class Thalasso_Kurwege(SimpleModel):
  """
  Thalasso-Kurwege
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  streckenbeschreibung = CharField(
    verbose_name='Streckenbeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  barrierefrei = BooleanField(verbose_name=' barrierefrei?', default=False)
  farbe = CharField(verbose_name='Farbe', max_length=7)
  beschriftung = CharField(
    verbose_name='Beschriftung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators,
  )
  laenge = PositiveIntegerField(verbose_name='Länge (in m)', default=0)
  geometrie = line_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."thalasso_kurwege_hro'
    verbose_name = 'Thalasso-Kurweg'
    verbose_name_plural = 'Thalasso-Kurwege'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Thalasso-Kurwege in der Hanse- und Universitätsstadt Rostock'
    readonly_fields = ['laenge']
    geometry_type = 'LineString'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'streckenbeschreibung': 'Streckenbeschreibung',
      'barrierefrei': 'barrierefrei?',
      'farbe': 'Farbe',
      'beschriftung': 'Beschriftung',
      'laenge': 'Länge (in m)',
    }
    list_actions_assign = [
      {
        'action_name': 'thalasso_kurwege-barrierefrei',
        'action_title': 'ausgewählten Datensätzen barrierefrei (ja/nein) direkt zuweisen',
        'field': 'barrierefrei',
        'type': 'boolean',
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'streckenbeschreibung': 'Streckenbeschreibung',
      'barrierefrei': 'barrierefrei?',
    }

  def __str__(self):
    return self.bezeichnung


class Toiletten(SimpleModel):
  """
  Toiletten
  """

  art = ForeignKey(
    to=Arten_Toiletten,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten',
  )
  bewirtschafter = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=SET_NULL,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter',
    blank=True,
    null=True,
  )
  behindertengerecht = BooleanField(verbose_name=' behindertengerecht?')
  duschmoeglichkeit = BooleanField(verbose_name='Duschmöglichkeit vorhanden?')
  wickelmoeglichkeit = BooleanField(verbose_name='Wickelmöglichkeit vorhanden?')
  zeiten = CharField(verbose_name='Öffnungszeiten', max_length=255, blank=True, null=True)
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."toiletten_hro'
    verbose_name = 'Toilette'
    verbose_name_plural = 'Toiletten'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Toiletten in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'behindertengerecht': 'behindertengerecht?',
      'duschmoeglichkeit': 'Duschmöglichkeit vorhanden?',
      'wickelmoeglichkeit': 'Wickelmöglichkeit?',
      'zeiten': 'Öffnungszeiten',
    }
    list_fields_with_foreign_key = {'art': 'art', 'bewirtschafter': 'bezeichnung'}
    list_actions_assign = [
      {
        'action_name': 'toiletten-bewirtschafter',
        'action_title': 'ausgewählten Datensätzen Bewirtschafter direkt zuweisen',
        'field': 'bewirtschafter',
        'type': 'foreignkey',
      }
    ]
    map_feature_tooltip_fields = ['art']
    map_filter_fields = {
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'behindertengerecht': 'behindertengerecht?',
      'duschmoeglichkeit': 'Duschmöglichkeit vorhanden?',
      'wickelmoeglichkeit': 'Wickelmöglichkeit?',
    }
    map_filter_fields_as_list = ['art', 'bewirtschafter']

  def __str__(self):
    return (
      str(self.art)
      + (' [Bewirtschafter: ' + str(self.bewirtschafter) + ']' if self.bewirtschafter else '')
      + (' mit Öffnungszeiten ' + self.zeiten + ']' if self.zeiten else '')
    )


class Trinkwassernotbrunnen(SimpleModel):
  """
  Trinkwassernotbrunnen
  """

  nummer = CharField(
    verbose_name='Nummer',
    max_length=12,
    validators=[
      RegexValidator(
        regex=trinkwassernotbrunnen_nummer_regex, message=trinkwassernotbrunnen_nummer_message
      )
    ],
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=SET_NULL,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer',
    blank=True,
    null=True,
  )
  betreiber = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=RESTRICT,
    db_column='betreiber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betreiber',
  )
  betriebsbereit = BooleanField(verbose_name=' betriebsbereit?')
  bohrtiefe = DecimalField(
    verbose_name='Bohrtiefe (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'), 'Die <strong><em>Bohrtiefe</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Bohrtiefe</em></strong> darf höchstens 99,99 m betragen.',
      ),
    ],
  )
  ausbautiefe = DecimalField(
    verbose_name='Ausbautiefe (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Ausbautiefe</em></strong> muss mindestens 0,01 m betragen.',
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Ausbautiefe</em></strong> darf höchstens 99,99 m betragen.',
      ),
    ],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."trinkwassernotbrunnen_hro'
    verbose_name = 'Trinkwassernotbrunnen'
    verbose_name_plural = 'Trinkwassernotbrunnen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Trinkwassernotbrunnen in der Hanse- und Universitätsstadt Rostock'
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'eigentuemer': 'Eigentümer',
      'betreiber': 'Betreiber',
      'betriebsbereit': 'betriebsbereit?',
      'bohrtiefe': 'Bohrtiefe (in m)',
      'ausbautiefe': 'Ausbautiefe (in m)',
    }
    list_fields_with_decimal = ['bohrtiefe', 'ausbautiefe']
    list_fields_with_foreign_key = {'eigentuemer': 'bezeichnung', 'betreiber': 'bezeichnung'}
    list_actions_assign = [
      {
        'action_name': 'trinkwassernotbrunnen-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey',
      },
      {
        'action_name': 'trinkwassernotbrunnen-betreiber',
        'action_title': 'ausgewählten Datensätzen Betreiber direkt zuweisen',
        'field': 'betreiber',
        'type': 'foreignkey',
      },
      {
        'action_name': 'trinkwassernotbrunnen-betriebsbereit',
        'action_title': 'ausgewählten Datensätzen betriebsbereit (ja/nein) direkt zuweisen',
        'field': 'betriebsbereit',
        'type': 'boolean',
      },
    ]
    map_feature_tooltip_fields = ['nummer']
    map_filter_fields = {
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'eigentuemer': 'Eigentümer',
      'betreiber': 'Betreiber',
      'betriebsbereit': 'betriebsbereit?',
      'bohrtiefe': 'Bohrtiefe (in m)',
      'ausbautiefe': 'Ausbautiefe (in m)',
    }
    map_filter_fields_as_list = ['eigentuemer', 'betreiber']

  def __str__(self):
    return self.nummer


class Vereine(SimpleModel):
  """
  Vereine
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  vereinsregister_id = PositiveSmallIntegerMinField(
    verbose_name='ID im Vereinsregister', min_value=1, blank=True, null=True
  )
  vereinsregister_datum = DateField(
    verbose_name='Datum des Eintrags im Vereinsregister', blank=True, null=True
  )
  schlagwoerter = ChoiceArrayField(
    CharField(verbose_name='Schlagwörter', max_length=255, choices=()), verbose_name='Schlagwörter'
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."vereine_hro'
    verbose_name = 'Verein'
    verbose_name_plural = 'Vereine'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Vereine in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {'schlagwoerter': 'Schlagwoerter_Vereine'}
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse'}
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {'bezeichnung': 'Bezeichnung', 'schlagwoerter': 'Schlagwörter'}

  def __str__(self):
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Verkaufstellen_Angelberechtigungen(SimpleModel):
  """
  Verkaufstellen für Angelberechtigungen
  """

  adresse = ForeignKey(
    to=Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True,
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung', max_length=255, validators=standard_validators
  )
  berechtigungen = ChoiceArrayField(
    CharField(verbose_name=' verkaufte Berechtigung(en)', max_length=255, choices=()),
    verbose_name=' verkaufte Berechtigung(en)',
    blank=True,
    null=True,
  )
  barrierefrei = BooleanField(verbose_name=' barrierefrei?', blank=True, null=True)
  zeiten = CharField(verbose_name='Öffnungszeiten', max_length=255, blank=True, null=True)
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[RegexValidator(regex=rufnummer_regex, message=rufnummer_message)],
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[EmailValidator(message=email_message)],
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[URLValidator(message=url_message)],
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug"."verkaufstellen_angelberechtigungen_hro'
    verbose_name = 'Verkaufstelle für Angelberechtigungen'
    verbose_name_plural = 'Verkaufstellen für Angelberechtigungen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = (
      'Verkaufstellen für Angelberechtigungen in der Hanse- und Universitätsstadt Rostock'
    )
    choices_models_for_choices_fields = {'berechtigungen': 'Angelberechtigungen'}
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'berechtigungen': 'verkaufte Berechtigung(en)',
    }
    list_fields_with_foreign_key = {'adresse': 'adresse'}
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'berechtigungen': 'verkaufte Berechtigung(en)',
    }

  def __str__(self):
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Versenkpoller(SimpleModel):
  """
  Versenkpoller
  """

  nummer = PositiveSmallIntegerMinField(
    verbose_name='Nummer',
    min_value=1,
    blank=True,
    null=True,
  )
  kurzbezeichnung = CharField(
    verbose_name='Kurzbezeichnung',
    max_length=3,
    blank=True,
    null=True,
  )
  lagebeschreibung = CharField(
    verbose_name='Lagebeschreibung',
    max_length=255,
    blank=True,
    null=True,
  )
  statusinformation = CharField(
    verbose_name='Statusinformation',
    max_length=255,
    blank=True,
    null=True,
  )
  zusatzbeschilderung = CharField(
    verbose_name='Zusatzbeschilderung',
    max_length=255,
    blank=True,
    null=True,
  )
  hersteller = ForeignKey(
    to=Hersteller_Versenkpoller,
    verbose_name='Hersteller',
    on_delete=SET_NULL,
    db_column='hersteller',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_hersteller',
    blank=True,
    null=True,
  )
  typ = ForeignKey(
    to=Typen_Versenkpoller,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
    blank=True,
    null=True,
  )
  baujahr = PositiveSmallIntegerRangeField(
    verbose_name='Baujahr', min_value=1900, max_value=get_current_year(), blank=True, null=True
  )
  wartungsfirma = ForeignKey(
    to=Wartungsfirmen_Versenkpoller,
    verbose_name='Wartungsfirma',
    on_delete=SET_NULL,
    db_column='wartungsfirma',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_hersteller',
    blank=True,
    null=True,
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(settings.PHOTO_PATH_PREFIX_PRIVATE + 'versenkpoller'),
    max_length=255,
    blank=True,
    null=True,
  )
  geometrie = nullable_point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten"."versenkpoller_hro'
    verbose_name = 'Versenkpoller'
    verbose_name_plural = 'Versenkpoller'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Versenkpoller in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    readonly_fields = [
      'nummer',
      'kurzbezeichnung',
      'lagebeschreibung',
      'statusinformation',
      'zusatzbeschilderung',
    ]
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'nummer': 'Nummer',
      'kurzbezeichnung': 'Kurzbezeichnung',
      'statusinformation': 'Statusinformation',
      'hersteller': 'Hersteller',
      'typ': 'Typ',
      'baujahr': 'Baujahr',
      'wartungsfirma': 'Wartungsfirma',
      'foto': 'Foto',
    }
    list_fields_with_foreign_key = {
      'hersteller': 'bezeichnung',
      'typ': 'typ',
      'wartungsfirma': 'bezeichnung',
    }
    list_actions_assign = [
      {
        'action_name': 'versenkpoller-hersteller',
        'action_title': 'ausgewählten Datensätzen Hersteller direkt zuweisen',
        'field': 'hersteller',
        'type': 'foreignkey',
      },
      {
        'action_name': 'versenkpoller-wartungsfirma',
        'action_title': 'ausgewählten Datensätzen Wartungsfirma direkt zuweisen',
        'field': 'wartungsfirma',
        'type': 'foreignkey',
      },
    ]
    map_feature_tooltip_fields = ['kurzbezeichnung']
    map_filter_fields = {
      'nummer': 'Nummer',
      'kurzbezeichnung': 'Kurzbezeichnung',
      'lagebeschreibung': 'Lagebeschreibung',
      'statusinformation': 'Statusinformation',
      'zusatzbeschilderung': 'Zusatzbeschilderung',
      'hersteller': 'Hersteller',
      'typ': 'Typ',
      'baujahr': 'Baujahr',
      'wartungsfirma': 'Wartungsfirma',
    }
    map_filter_fields_as_list = ['hersteller', 'typ', 'wartungsfirma']

  def __str__(self):
    return str(self.kurzbezeichnung) if self.kurzbezeichnung else str(self.uuid)


pre_save.connect(set_pre_save_instance, sender=Versenkpoller)

post_save.connect(photo_post_processing, sender=Versenkpoller)

post_save.connect(delete_photo_after_emptied, sender=Versenkpoller)

post_delete.connect(delete_photo, sender=Versenkpoller)
