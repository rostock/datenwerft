from datetime import date, datetime, timezone
from decimal import Decimal
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator, \
  RegexValidator, URLValidator
from django.db.models import CASCADE, RESTRICT, SET_NULL, ForeignKey, OneToOneField
from django.db.models.fields import BooleanField, CharField, DateField, DateTimeField, \
  DecimalField, PositiveIntegerField, TextField
from django.db.models.fields.files import FileField, ImageField
from django.db.models.signals import post_delete, post_save, pre_save
from re import sub
from zoneinfo import ZoneInfo

from datenmanagement.utils import get_current_year, path_and_rename
from toolbox.constants_vars import personennamen_validators, standard_validators, \
  aktenzeichen_anerkennungsgebuehren_regex, aktenzeichen_anerkennungsgebuehren_message, \
  aktenzeichen_kommunalvermoegen_regex, aktenzeichen_kommunalvermoegen_message, \
  d3_regex, d3_message, email_message, hausnummer_zusatz_regex, hausnummer_zusatz_message, \
  inventarnummer_regex, inventarnummer_message, postleitzahl_message, postleitzahl_regex, \
  rufnummer_regex, rufnummer_message, url_message
from .base import Basemodel, SimpleModel
from .constants_vars import arrondierungsflaechen_registriernummer_regex, \
  arrondierungsflaechen_registriernummer_message, denksteine_nummer_regex, \
  denksteine_nummer_message, erdwaermesonden_aktenzeichen_regex, \
  erdwaermesonden_aktenzeichen_message, erdwaermesonden_d3_regex, erdwaermesonden_d3_message, \
  hausnummern_antragsnummer_message, hausnummern_antragsnummer_regex, \
  hydranten_bezeichnung_regex, hydranten_bezeichnung_message, \
  ingenieurbauwerke_nummer_asb_regex, ingenieurbauwerke_nummer_asb_message, \
  ingenieurbauwerke_baujahr_regex, ingenieurbauwerke_baujahr_message, \
  kleinklaeranlagen_zulassung_regex, kleinklaeranlagen_zulassung_message, \
  mobilfunkantennen_stob_regex, mobilfunkantennen_stob_message, poller_nummer_regex, \
  poller_nummer_message, trinkwassernotbrunnen_nummer_regex, \
  trinkwassernotbrunnen_nummer_message, ANERKENNUNGSGEBUEHREN_HERRSCHEND_GRUNDBUCHEINTRAG
from .fields import ChoiceArrayField, NullTextField, PositiveSmallIntegerMinField, \
  PositiveSmallIntegerRangeField, point_field, line_field, multiline_field, polygon_field, \
  multipolygon_field, nullable_multipolygon_field
from .functions import delete_pdf, delete_photo, delete_photo_after_emptied, \
  set_pre_save_instance, photo_post_processing
from .models_codelist import Adressen, Gemeindeteile, Strassen, Altersklassen_Kadaverfunde, \
  Anbieter_Carsharing, Arten_Erdwaermesonden, Arten_Fahrradabstellanlagen, Arten_FairTrade, \
  Arten_Fallwildsuchen_Kontrollen, Arten_Feuerwachen, Arten_Fliessgewaesser, \
  Arten_Hundetoiletten, Arten_Ingenieurbauwerke, Arten_Meldedienst_flaechenhaft, \
  Arten_Meldedienst_punkthaft, Arten_Parkmoeglichkeiten, Arten_Pflegeeinrichtungen, \
  Arten_Poller, Arten_Reisebusparkplaetze_Terminals, Arten_Sportanlagen, \
  Arten_Toiletten, Ausfuehrungen_Ingenieurbauwerke, Betriebsarten, Betriebszeiten, \
  Bevollmaechtigte_Bezirksschornsteinfeger, Bewirtschafter_Betreiber_Traeger_Eigentuemer, \
  Gebaeudearten_Meldedienst_punkthaft, Gebaeudebauweisen, Gebaeudefunktionen, \
  Geschlechter_Kadaverfunde, Haefen, Hersteller_Poller, Materialien_Denksteine, \
  Ordnungen_Fliessgewaesser, Personentitel, Quartiere, Sportarten, \
  Status_Baudenkmale_Denkmalbereiche, Status_Poller, Tierseuchen, Typen_Abfallbehaelter, \
  Typen_Erdwaermesonden, Typen_Kleinklaeranlagen, Typen_Poller, \
  Verbuende_Ladestationen_Elektrofahrzeuge, Zustaende_Kadaverfunde, \
  Zustaende_Schutzzaeune_Tierseuchen
from .storage import OverwriteStorage


class Abfallbehaelter(SimpleModel):
  """
  Abfallbehälter
  """

  deaktiviert = DateField(
    verbose_name='Außerbetriebstellung',
    blank=True,
    null=True
  )
  id = CharField(
    verbose_name='ID',
    max_length=8,
    unique=True,
    default='00000000'
  )
  typ = ForeignKey(
    to=Typen_Abfallbehaelter,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
    blank=True,
    null=True
  )
  aufstellungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Aufstellungsjahr',
    max_value=get_current_year(),
    blank=True,
    null=True
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer'
  )
  bewirtschafter = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter'
  )
  pflegeobjekt = CharField(
    verbose_name='Pflegeobjekt',
    max_length=255,
    validators=standard_validators
  )
  inventarnummer = CharField(
    verbose_name='Inventarnummer',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=inventarnummer_regex,
        message=inventarnummer_message
      )
    ]
  )
  anschaffungswert = DecimalField(
    verbose_name='Anschaffungswert (in €)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9999.99'),
        'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 9.999,99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  haltestelle = BooleanField(
    verbose_name='Lage an einer Haltestelle?',
    blank=True,
    null=True
  )
  sommer_mo = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen montags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_di = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen dienstags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_mi = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen mittwochs im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_do = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen donnerstags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_fr = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen freitags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_sa = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen samstags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_so = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen sonntags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  winter_mo = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen montags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_di = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen dienstags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_mi = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen mittwochs im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_do = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen donnerstags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_fr = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen freitags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_sa = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen samstags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_so = PositiveSmallIntegerRangeField(
    verbose_name='Anzahl Leerungen sonntags im Winter',
    min_value=1,
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
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"abfallbehaelter_hro'
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
      'pflegeobjekt': 'Pflegeobjekt'
    }
    list_fields_with_date = ['deaktiviert']
    list_fields_with_foreign_key = {
      'typ': 'typ',
      'eigentuemer': 'bezeichnung',
      'bewirtschafter': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'abfallbehaelter-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey'
      },
      {
        'action_name': 'abfallbehaelter-bewirtschafter',
        'action_title': 'ausgewählten Datensätzen Bewirtschafter direkt zuweisen',
        'field': 'bewirtschafter',
        'type': 'foreignkey'
      }
    ]
    map_heavy_load_limit = 500
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'typ': 'Typ',
      'eigentuemer': 'Eigentümer',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt'
    }
    map_filter_fields_as_list = ['typ', 'eigentuemer', 'bewirtschafter']

  def __str__(self):
    return self.id + (' [Typ: ' + str(self.typ) + ']' if self.typ else '')


class Anerkennungsgebuehren_herrschend(SimpleModel):
  """
  Anerkennungsgebühren (herrschendes Flurstück)
  """

  grundbucheintrag = CharField(
    verbose_name='Grundbucheintrag',
    max_length=255,
    choices=ANERKENNUNGSGEBUEHREN_HERRSCHEND_GRUNDBUCHEINTRAG
  )
  aktenzeichen_anerkennungsgebuehren = CharField(
    verbose_name='Aktenzeichen Anerkennungsgebühren',
    max_length=12,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=aktenzeichen_anerkennungsgebuehren_regex,
        message=aktenzeichen_anerkennungsgebuehren_message
      )
    ]
  )
  aktenzeichen_kommunalvermoegen = CharField(
    verbose_name='Aktenzeichen Kommunalvermögen',
    max_length=10,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=aktenzeichen_kommunalvermoegen_regex,
        message=aktenzeichen_kommunalvermoegen_message
      )
    ]
  )
  vermoegenszuordnung_hro = BooleanField(
    verbose_name='Vermögenszuordnung der Hanse- und Universitätsstadt Rostock',
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
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"anerkennungsgebuehren_herrschend_hro'
    verbose_name = 'Anerkennungsgebühr (herrschendes Flurstück)'
    verbose_name_plural = 'Anerkennungsgebühren (herrschendes Flurstück)'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Anerkennungsgebühren (herrschendes Flurstück) ' \
                  'der Hanse- und Universitätsstadt Rostock'
    as_overlay = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'grundbucheintrag': 'Grundbucheintrag',
      'aktenzeichen_anerkennungsgebuehren': 'Aktenzeichen Anerkennungsgebühren',
      'aktenzeichen_kommunalvermoegen': 'Aktenzeichen Kommunalvermögen',
      'vermoegenszuordnung_hro': 'Vermögenszuordnung der Hanse- und Universitätsstadt Rostock',
      'bemerkungen': 'Bemerkungen'
    }
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'grundbucheintrag': 'Grundbucheintrag',
      'aktenzeichen_anerkennungsgebuehren': 'Aktenzeichen Anerkennungsgebühren',
      'aktenzeichen_kommunalvermoegen': 'Aktenzeichen Kommunalvermögen',
      'vermoegenszuordnung_hro': 'Vermögenszuordnung der Hanse- und Universitätsstadt Rostock',
      'bemerkungen': 'Bemerkungen'
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
    validators=standard_validators
  )
  beschreibung = NullTextField(
    verbose_name='Beschreibung',
    max_length=1000,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = line_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"angelverbotsbereiche_hro'
    verbose_name = 'Angelverbotsbereich'
    verbose_name_plural = 'Angelverbotsbereiche'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Angelverbotsbereiche der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    geometry_type = 'LineString'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung'
    }
    map_feature_tooltip_fields = ['bezeichnung']

  def __str__(self):
    return (self.bezeichnung if self.bezeichnung else 'ohne Bezeichnung') + \
      (' [Beschreibung: ' + str(self.beschreibung) + ']' if self.beschreibung else '')


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
        message=arrondierungsflaechen_registriernummer_message
      )
    ]
  )
  jahr = PositiveSmallIntegerRangeField(
    verbose_name='Jahr',
    default=get_current_year(),
    max_value=get_current_year()
  )
  geometrie = polygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"arrondierungsflaechen_hro'
    verbose_name = 'Arrondierungsfläche'
    verbose_name_plural = 'Arrondierungsflächen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Arrondierungsflächen in der Hanse- und Universitätsstadt Rostock'
    as_overlay = False
    geometry_type = 'Polygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'registriernummer': 'Registriernummer',
      'jahr': 'Jahr'
    }
    map_feature_tooltip_fields = ['registriernummer']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'registriernummer': 'Registriernummer',
      'jahr': 'Jahr'
    }

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
    null=True
  )
  aktenzeichen = CharField(
    verbose_name='Aktenzeichen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  datum_abgeschlossenheitserklaerung = DateField(
    verbose_name='Datum der Abgeschlossenheitserklärung',
    blank=True,
    null=True
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
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
  datum = DateField(
    verbose_name='Datum',
    default=date.today
  )
  pdf = FileField(
    verbose_name='PDF',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PDF_PATH_PREFIX_PRIVATE + 'aufteilungsplaene_wohnungseigentumsgesetz'
    ),
    max_length=255
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"aufteilungsplaene_wohnungseigentumsgesetz_hro'
    verbose_name = 'Aufteilungsplan nach Wohnungseigentumsgesetz'
    verbose_name_plural = 'Aufteilungspläne nach Wohnungseigentumsgesetz'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Aufteilungspläne nach Wohnungseigentumsgesetz' \
                  'in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'aktenzeichen': 'Aktenzeichen',
      'datum_abgeschlossenheitserklaerung': 'Datum der Abgeschlossenheitserklärung',
      'pdf': 'PDF',
      'datum': 'Datum'
    }
    list_fields_with_date = ['datum_abgeschlossenheitserklaerung', 'datum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    list_actions_assign = [
      {
        'action_name':
          'aufteilungsplaene_wohnungseigentumsgesetz-datum_abgeschlossenheitserklaerung',
        'action_title': 'ausgewählten Datensätzen Datum der Abgeschlossenheitserklärung'
                        'direkt zuweisen',
        'field': 'datum_abgeschlossenheitserklaerung',
        'type': 'date'
      },
      {
        'action_name': 'aufteilungsplaene_wohnungseigentumsgesetz-datum',
        'action_title': 'ausgewählten Datensätzen Datum direkt zuweisen',
        'field': 'datum',
        'type': 'date',
        'value_required': True
      }
    ]
    map_feature_tooltip_fields = ['datum']
    map_filter_fields = {
      'aktenzeichen': 'Aktenzeichen',
      'datum_abgeschlossenheitserklaerung': 'Datum der Abgeschlossenheitserklärung',
      'datum': 'Datum'
    }

  def __str__(self):
    return 'Abgeschlossenheitserklärung mit Datum ' + \
      datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + \
      (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


post_delete.connect(delete_pdf, sender=Aufteilungsplaene_Wohnungseigentumsgesetz)


class Baudenkmale(SimpleModel):
  """
  Baudenkmale
  """

  id = PositiveIntegerField(
    verbose_name='ID',
    unique=True,
    default=0
  )
  status = ForeignKey(
    to=Status_Baudenkmale_Denkmalbereiche,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
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
  beschreibung = CharField(
    verbose_name='Beschreibung',
    max_length=255,
    validators=standard_validators
  )
  vorherige_beschreibung = CharField(
    verbose_name=' vorherige Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  lage = CharField(
    verbose_name='Lage',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  unterschutzstellungen = ArrayField(
    DateField(
      verbose_name='Unterschutzstellungen',
      blank=True,
      null=True
    ),
    verbose_name='Unterschutzstellungen',
    blank=True,
    null=True
  )
  veroeffentlichungen = ArrayField(
    DateField(
      verbose_name='Veröffentlichungen',
      blank=True,
      null=True
    ),
    verbose_name='Veröffentlichungen',
    blank=True,
    null=True
  )
  denkmalnummern = ArrayField(
    CharField(
      verbose_name='Denkmalnummern',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators
    ),
    verbose_name='Denkmalnummern',
    blank=True,
    null=True
  )
  gartendenkmal = BooleanField(' Gartendenkmal?')
  hinweise = NullTextField(
    verbose_name='Hinweise',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators
  )
  aenderungen = NullTextField(
    verbose_name='Änderungen',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = nullable_multipolygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"baudenkmale_hro'
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
      'beschreibung': 'Beschreibung'
    }
    list_fields_with_foreign_key = {
      'status': 'status',
      'adresse': 'adresse'
    }
    list_actions_assign = [
      {
        'action_name': 'baudenkmale-status',
        'action_title': 'ausgewählten Datensätzen Status direkt zuweisen',
        'field': 'status',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'status': 'Status',
      'lage': 'Lage',
      'beschreibung': 'Beschreibung',
      'gartendenkmal': 'Gartendenkmal?'
    }
    map_filter_fields_as_list = ['status']
    additional_wfs_featuretypes = [
      {
        'name': 'flurstuecke',
        'title': 'Flurstücke',
        'url': '/flurstuecke_hro/wfs',
        'featuretypes': 'hro.flurstuecke.flurstuecke',
        'proxy': True
      },
      {
        'name': 'gebaeude',
        'title': 'Gebäude',
        'url': '/gebaeude/wfs',
        'featuretypes': 'hro.gebaeude.gebaeude',
        'proxy': True
      }
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
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  plaetze = PositiveSmallIntegerMinField(
    verbose_name='Plätze',
    min_value=1,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"behinderteneinrichtungen_hro'
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
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'behinderteneinrichtungen-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return self.bezeichnung + \
      ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ']'


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
    null=True
  )
  beschlussjahr = PositiveSmallIntegerRangeField(
    verbose_name='Beschlussjahr',
    min_value=1990,
    max_value=get_current_year(),
    default=get_current_year()
  )
  vorhabenbezeichnung = CharField(
    verbose_name='Bezeichnung des Vorhabens',
    max_length=255,
    validators=standard_validators
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
    max_length=255,
    validators=standard_validators
  )
  pdf = FileField(
    verbose_name='PDF',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PDF_PATH_PREFIX_PRIVATE + 'beschluesse_bau_planungsausschuss'
    ),
    max_length=255
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"beschluesse_bau_planungsausschuss_hro'
    verbose_name = 'Beschluss des Bau- und Planungsausschusses'
    verbose_name_plural = 'Beschlüsse des Bau- und Planungsausschusses'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Beschlüsse des Bau- und Planungsausschusses der Bürgerschaft ' \
                  'der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'beschlussjahr': 'Beschlussjahr',
      'vorhabenbezeichnung': 'Bezeichnung des Vorhabens',
      'bearbeiter': 'Bearbeiter:in',
      'pdf': 'PDF'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_fields = ['vorhabenbezeichnung']
    map_filter_fields = {
      'beschlussjahr': 'Beschlussjahr',
      'vorhabenbezeichnung': 'Bezeichnung des Vorhabens'
    }

  def __str__(self):
    return self.vorhabenbezeichnung + ' (Beschlussjahr ' + str(self.beschlussjahr) + ')' + \
      (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


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
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  betreiber = CharField(
    verbose_name='Betreiber:in',
    max_length=255,
    validators=standard_validators
  )
  schlagwoerter = ChoiceArrayField(
    CharField(
      verbose_name='Schlagwörter',
      max_length=255,
      choices=()
    ),
    verbose_name='Schlagwörter'
  )
  barrierefrei = BooleanField(
    verbose_name=' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    verbose_name='Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"bildungstraeger_hro'
    verbose_name = 'Bildungsträger'
    verbose_name_plural = 'Bildungsträger'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Bildungsträger in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'schlagwoerter': 'Schlagwoerter_Bildungstraeger'
    }
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter'
    }

  def __str__(self):
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Carsharing_Stationen(SimpleModel):
  """
  Carsharing-Stationen
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
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  anbieter = ForeignKey(
    to=Anbieter_Carsharing,
    verbose_name='Anbieter',
    on_delete=RESTRICT,
    db_column='anbieter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_anbieter'
  )
  anzahl_fahrzeuge = PositiveSmallIntegerMinField(
    verbose_name='Anzahl der Fahrzeuge',
    min_value=1,
    blank=True,
    null=True
  )
  bemerkungen = NullTextField(
    verbose_name='Bemerkungen',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"carsharing_stationen_hro'
    verbose_name = 'Carsharing-Station'
    verbose_name_plural = 'Carsharing-Stationen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Carsharing-Stationen in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'anbieter': 'Anbieter',
      'anzahl_fahrzeuge': 'Anzahl der Fahrzeuge'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'anbieter': 'anbieter'
    }
    list_actions_assign = [
      {
        'action_name': 'behinderteneinrichtungen-anbieter',
        'action_title': 'ausgewählten Datensätzen Anbieter direkt zuweisen',
        'field': 'anbieter',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'anbieter': 'Anbieter'
    }
    map_filter_fields_as_list = ['anbieter']

  def __str__(self):
    return self.bezeichnung + \
      ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Anbieter: ' + str(self.anbieter) + ']'


class Containerstellplaetze(SimpleModel):
  """
  Containerstellplätze
  """

  deaktiviert = DateField(
    verbose_name='Außerbetriebstellung',
    blank=True,
    null=True
  )
  id = CharField(
    verbose_name='ID',
    max_length=5,
    unique=True,
    default='00-00'
  )
  privat = BooleanField(' privat?')
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  bewirtschafter_grundundboden = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Grund und Boden',
    on_delete=SET_NULL,
    db_column='bewirtschafter_grundundboden',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_grundundboden',
    blank=True,
    null=True
  )
  bewirtschafter_glas = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Glas',
    on_delete=SET_NULL,
    db_column='bewirtschafter_glas',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_glas',
    blank=True,
    null=True
  )
  anzahl_glas = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Glas normal',
    min_value=1,
    blank=True,
    null=True
  )
  anzahl_glas_unterflur = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Glas unterflur',
    min_value=1,
    blank=True,
    null=True
  )
  bewirtschafter_papier = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Papier',
    on_delete=SET_NULL,
    db_column='bewirtschafter_papier',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_papier',
    blank=True,
    null=True
  )
  anzahl_papier = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Papier normal',
    min_value=1,
    blank=True,
    null=True
  )
  anzahl_papier_unterflur = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Papier unterflur',
    min_value=1,
    blank=True,
    null=True
  )
  bewirtschafter_altkleider = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Altkleider',
    on_delete=SET_NULL,
    db_column='bewirtschafter_altkleider',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_altkleider',
    blank=True,
    null=True
  )
  anzahl_altkleider = PositiveSmallIntegerMinField(
    verbose_name='Anzahl Altkleider',
    min_value=1,
    blank=True,
    null=True
  )
  inbetriebnahmejahr = PositiveSmallIntegerRangeField(
    verbose_name='Inbetriebnahmejahr',
    max_value=get_current_year(),
    blank=True,
    null=True
  )
  inventarnummer = CharField(
    verbose_name='Inventarnummer Stellplatz',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=inventarnummer_regex,
        message=inventarnummer_message
      )
    ]
  )
  inventarnummer_grundundboden = CharField(
    verbose_name='Inventarnummer Grund und Boden',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=inventarnummer_regex,
        message=inventarnummer_message
      )
    ]
  )
  inventarnummer_zaun = CharField(
    verbose_name='Inventarnummer Zaun',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=inventarnummer_regex,
        message=inventarnummer_message
      )
    ]
  )
  anschaffungswert = DecimalField(
    verbose_name='Anschaffungswert (in €)',
    max_digits=7,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('99999.99'),
        'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 99.999,99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  oeffentliche_widmung = BooleanField(
    verbose_name=' öffentliche Widmung?',
    blank=True,
    null=True
  )
  bga = BooleanField(
    verbose_name='Zuordnung BgA Stellplatz?',
    blank=True,
    null=True
  )
  bga_grundundboden = BooleanField(
    verbose_name='Zuordnung BgA Grund und Boden?',
    blank=True,
    null=True
  )
  bga_zaun = BooleanField(
    verbose_name='Zuordnung BgA Zaun?',
    blank=True,
    null=True
  )
  art_eigentumserwerb = CharField(
    verbose_name='Art des Eigentumserwerbs Stellplatz',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  art_eigentumserwerb_zaun = CharField(
    verbose_name='Art des Eigentumserwerbs Zaun',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  vertraege = CharField(
    verbose_name='Verträge',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  winterdienst_a = BooleanField(
    verbose_name='Winterdienst A?',
    blank=True,
    null=True
  )
  winterdienst_b = BooleanField(
    verbose_name='Winterdienst B?',
    blank=True,
    null=True
  )
  winterdienst_c = BooleanField(
    verbose_name='Winterdienst C?',
    blank=True,
    null=True
  )
  flaeche = DecimalField(
    verbose_name='Fläche (in m²)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Fläche</em></strong> muss mindestens 0,01 m² betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Fläche</em></strong> darf höchstens 999,99 m² betragen.'
      )
    ],
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
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE + 'containerstellplaetze'
    ),
    max_length=255,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"containerstellplaetze_hro'
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
      'foto': 'Foto'
    }
    list_fields_with_date = ['deaktiviert']
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'id': 'ID',
      'privat': 'privat?',
      'bezeichnung': 'Bezeichnung'
    }

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

  id = PositiveIntegerField(
    verbose_name='ID',
    unique=True,
    default=0
  )
  status = ForeignKey(
    to=Status_Baudenkmale_Denkmalbereiche,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  beschreibung = CharField(
    verbose_name='Beschreibung',
    max_length=255,
    validators=standard_validators
  )
  unterschutzstellungen = ArrayField(
    DateField(
      verbose_name='Unterschutzstellungen',
      blank=True,
      null=True
    ),
    verbose_name='Unterschutzstellungen',
    blank=True,
    null=True
  )
  veroeffentlichungen = ArrayField(
    DateField(
      verbose_name='Veröffentlichungen',
      blank=True,
      null=True
    ),
    verbose_name='Veröffentlichungen',
    blank=True,
    null=True
  )
  denkmalnummern = ArrayField(
    CharField(
      verbose_name='Denkmalnummern',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators
    ),
    verbose_name='Denkmalnummern',
    blank=True,
    null=True
  )
  hinweise = NullTextField(
    verbose_name='Hinweise',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators
  )
  aenderungen = NullTextField(
    verbose_name='Änderungen',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = multipolygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"denkmalbereiche_hro'
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
      'beschreibung': 'Beschreibung'
    }
    list_fields_with_foreign_key = {
      'status': 'status'
    }
    list_actions_assign = [
      {
        'action_name': 'denkmalbereiche-status',
        'action_title': 'ausgewählten Datensätzen Status direkt zuweisen',
        'field': 'status',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'status': 'Status',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung'
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
    null=True
  )
  nummer = CharField(
    verbose_name='Nummer',
    max_length=255,
    validators=[
      RegexValidator(
        regex=denksteine_nummer_regex,
        message=denksteine_nummer_message
      )
    ]
  )
  titel = ForeignKey(
    to=Personentitel,
    verbose_name='Titel',
    on_delete=SET_NULL,
    db_column='titel',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_titel',
    blank=True,
    null=True
  )
  vorname = CharField(
    verbose_name='Vorname',
    max_length=255,
    validators=personennamen_validators
  )
  nachname = CharField(
    verbose_name='Nachname',
    max_length=255,
    validators=personennamen_validators
  )
  geburtsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Geburtsjahr',
    min_value=1850,
    max_value=1945
  )
  sterbejahr = PositiveSmallIntegerRangeField(
    verbose_name='Sterbejahr',
    min_value=1933,
    max_value=1945,
    blank=True,
    null=True
  )
  text_auf_dem_stein = CharField(
    verbose_name='Text auf dem Stein',
    max_length=255,
    validators=standard_validators
  )
  ehemalige_adresse = CharField(
    verbose_name=' ehemalige Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  material = ForeignKey(
    to=Materialien_Denksteine,
    verbose_name='Material',
    on_delete=RESTRICT,
    db_column='material',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_materialien'
  )
  erstes_verlegejahr = PositiveSmallIntegerRangeField(
    verbose_name=' erstes Verlegejahr',
    min_value=2002,
    max_value=get_current_year()
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"denksteine_hro'
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
      'sterbejahr': 'Sterbejahr'
    }
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

  def __str__(self):
    return (str(self.titel) + ' ' if self.titel else '') + \
      self.vorname + ' ' + self.nachname + ' (* ' + str(self.geburtsjahr) + \
      (', † ' + str(self.sterbejahr) if self.sterbejahr else '') + ')' + \
      (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Erdwaermesonden(SimpleModel):
  """
  Erdwärmesonden
  """

  aktenzeichen = CharField(
    verbose_name='Aktenzeichen',
    max_length=18,
    validators=[
      RegexValidator(
        regex=erdwaermesonden_aktenzeichen_regex,
        message=erdwaermesonden_aktenzeichen_message
      )
    ]
  )
  d3 = CharField(
    verbose_name=' d.3',
    max_length=16,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=erdwaermesonden_d3_regex,
        message=erdwaermesonden_d3_message
      )
    ]
  )
  art = ForeignKey(
    to=Arten_Erdwaermesonden,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  typ = ForeignKey(
    to=Typen_Erdwaermesonden,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
    blank=True,
    null=True
  )
  awsv_anlage = BooleanField(
    verbose_name='AwSV-Anlage?',
    blank=True,
    null=True
  )
  anzahl_sonden = PositiveSmallIntegerMinField(
    verbose_name='Anzahl der Sonden',
    min_value=1,
    blank=True,
    null=True
  )
  sondenfeldgroesse = PositiveSmallIntegerMinField(
    verbose_name='Sondenfeldgröße (in m²)',
    min_value=1,
    blank=True,
    null=True
  )
  endteufe = DecimalField(
    verbose_name='Endteufe (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Endteufe</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Endteufe</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  hinweis = CharField(
    verbose_name='Hinweis',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"erdwaermesonden_hro'
    verbose_name = 'Erdwärmesonde'
    verbose_name_plural = 'Erdwärmesonden'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Erdwärmesonden in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'd3': 'd.3',
      'aktenzeichen': 'Aktenzeichen',
      'art': 'Art',
      'typ': 'Typ',
      'awsv_anlage': 'AwSV-Anlage?',
      'anzahl_sonden': 'Anzahl der Sonden',
      'sondenfeldgroesse': 'Sondenfeldgröße (in m²)',
      'endteufe': 'Endteufe (in m)',
      'hinweis': 'Hinweis'
    }
    list_fields_with_decimal = ['endteufe']
    list_fields_with_foreign_key = {
      'art': 'art',
      'typ': 'typ'
    }
    map_feature_tooltip_fields = ['aktenzeichen']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'd3': 'd.3',
      'aktenzeichen': 'Aktenzeichen',
      'art': 'Art',
      'typ': 'Typ',
      'awsv_anlage': 'AwSV-Anlage?',
      'anzahl_sonden': 'Anzahl der Sonden',
      'sondenfeldgroesse': 'Sondenfeldgröße (in m²)',
      'endteufe': 'Endteufe (in m)',
      'hinweis': 'Hinweis'
    }
    map_filter_fields_as_list = ['art', 'typ']

  def __str__(self):
    return self.aktenzeichen


class Fahrradabstellanlagen(SimpleModel):
  """
  Fahrradabstellanlagen
  """

  art = ForeignKey(
    to=Arten_Fahrradabstellanlagen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  stellplaetze = PositiveSmallIntegerMinField(
    verbose_name='Stellplätze',
    min_value=1,
    blank=True,
    null=True
  )
  gebuehren = BooleanField(
    verbose_name='Gebühren?'
  )
  ueberdacht = BooleanField(
    verbose_name=' überdacht?'
  )
  ebike_lademoeglichkeiten = BooleanField(
    verbose_name='E-Bike-Lademöglichkeiten?',
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"fahrradabstellanlagen_hro'
    verbose_name = 'Fahrradabstellanlage'
    verbose_name_plural = 'Fahrradabstellanlagen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Fahrradabstellanlagen in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'stellplaetze': 'Stellplätze',
      'gebuehren': 'Gebühren?',
      'ueberdacht': 'überdacht?',
      'ebike_lademoeglichkeiten': 'E-Bike-Lademöglichkeiten?'
    }
    list_fields_with_foreign_key = {
      'art': 'art'
    }
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'stellplaetze': 'Stellplätze',
      'gebuehren': 'Gebühren?',
      'ueberdacht': 'überdacht?',
      'ebike_lademoeglichkeiten': 'E-Bike-Lademöglichkeiten?'
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return str(self.uuid)


class FairTrade(SimpleModel):
  """
  Fair Trade
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
    to=Arten_FairTrade,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  betreiber = CharField(
    verbose_name='Betreiber:in',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  barrierefrei = BooleanField(
    verbose_name=' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    verbose_name='Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"fairtrade_hro'
    verbose_name = 'Fair Trade'
    verbose_name_plural = 'Fair Trade'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Fair Trade in der Hanse- und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
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
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung'
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Art: ' + str(self.art) + ']'


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
    null=True
  )
  art = ForeignKey(
    to=Arten_Feuerwachen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"feuerwachen_hro'
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
      'bezeichnung': 'Bezeichnung'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'art': 'art'
    }
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung'
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Art: ' + str(self.art) + ']'


class Fliessgewaesser(SimpleModel):
  """
  Fließgewässer
  """

  nummer = CharField(
    verbose_name='Nummer',
    max_length=255,
    validators=standard_validators
  )
  art = ForeignKey(
    to=Arten_Fliessgewaesser,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  ordnung = ForeignKey(
    to=Ordnungen_Fliessgewaesser,
    verbose_name='Ordnung',
    on_delete=SET_NULL,
    db_column='ordnung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ordnungen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  nennweite = PositiveSmallIntegerMinField(
    verbose_name='Nennweite (in mm)',
    min_value=100,
    blank=True,
    null=True
  )
  laenge = PositiveIntegerField(
    verbose_name='Länge (in m)',
    default=0
  )
  laenge_in_hro = PositiveIntegerField(
    verbose_name='Länge innerhalb Rostocks (in m)',
    blank=True,
    null=True
  )
  geometrie = line_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"fliessgewaesser_hro'
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
      'laenge_in_hro': 'Länge innerhalb Rostocks (in m)'
    }
    list_fields_with_foreign_key = {
      'art': 'art',
      'ordnung': 'ordnung'
    }
    map_heavy_load_limit = 500
    map_feature_tooltip_fields = ['nummer']
    map_filter_fields = {
      'nummer': 'Nummer',
      'art': 'Art',
      'ordnung': 'Ordnung',
      'bezeichnung': 'Bezeichnung'
    }
    map_filter_fields_as_list = ['art', 'ordnung']

  def __str__(self):
    return self.nummer + ' [Art: ' + str(self.art) + \
      (', Ordnung: ' + str(self.ordnung) if self.ordnung else '') + ']'


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
    null=True
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
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
  datum = DateField(
    verbose_name='Datum',
    default=date.today
  )
  aufnahmedatum = DateField(
    verbose_name='Aufnahmedatum',
    default=date.today
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PRIVATE + 'gutachterfotos'
    ),
    max_length=255
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"gutachterfotos_hro'
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
      'foto': 'Foto'
    }
    list_fields_with_date = ['datum', 'aufnahmedatum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    list_actions_assign = [
      {
        'action_name': 'gutachterfotos-datum',
        'action_title': 'ausgewählten Datensätzen Datum direkt zuweisen',
        'field': 'datum',
        'type': 'date',
        'value_required': True
      },
      {
        'action_name': 'gutachterfotos-aufnahmedatum',
        'action_title': 'ausgewählten Datensätzen Aufnahmedatum direkt zuweisen',
        'field': 'aufnahmedatum',
        'type': 'date',
        'value_required': True
      }
    ]
    map_heavy_load_limit = 800
    map_feature_tooltip_fields = ['datum']
    map_filter_fields = {
      'datum': 'Datum',
      'aufnahmedatum': 'Aufnahmedatum'
    }

  def __str__(self):
    return 'Gutachterfoto mit Aufnahmedatum ' + \
      datetime.strptime(str(self.aufnahmedatum), '%Y-%m-%d').strftime('%d.%m.%Y') + \
      (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


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
    null=True
  )
  deaktiviert = DateField(
    verbose_name='Datum der Löschung',
    blank=True,
    null=True
  )
  loeschung_details = CharField(
    verbose_name='Details zur Löschung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  vorherige_adresse = CharField(
    verbose_name=' vorherige Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  vorherige_antragsnummer = CharField(
    verbose_name=' vorherige Antragsnummer',
    max_length=6,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=hausnummern_antragsnummer_regex,
        message=hausnummern_antragsnummer_message
      )
    ]
  )
  hausnummer = PositiveSmallIntegerRangeField(
    verbose_name='Hausnummer',
    min_value=1,
    max_value=999
  )
  hausnummer_zusatz = CharField(
    verbose_name='Hausnummernzusatz',
    max_length=1,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=hausnummer_zusatz_regex,
        message=hausnummer_zusatz_message
      )
    ]
  )
  postleitzahl = CharField(
    verbose_name='Postleitzahl',
    max_length=5,
    validators=[
      RegexValidator(
        regex=postleitzahl_regex,
        message=postleitzahl_message
      )
    ]
  )
  vergabe_datum = DateField(
    verbose_name='Datum der Vergabe',
    default=date.today
  )
  antragsnummer = CharField(
    verbose_name='Antragsnummer',
    max_length=6,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=hausnummern_antragsnummer_regex,
        message=hausnummern_antragsnummer_message
      )
    ]
  )
  gebaeude_bauweise = ForeignKey(
    to=Gebaeudebauweisen,
    verbose_name='Bauweise des Gebäudes',
    on_delete=SET_NULL,
    db_column='gebaeude_bauweise',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gebaeude_bauweisen',
    blank=True,
    null=True
  )
  gebaeude_funktion = ForeignKey(
    to=Gebaeudefunktionen,
    verbose_name='Funktion des Gebäudes',
    on_delete=SET_NULL,
    db_column='gebaeude_funktion',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gebaeude_funktionen',
    blank=True,
    null=True
  )
  hinweise_gebaeude = CharField(
    verbose_name=' weitere Hinweise zum Gebäude',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
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
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug\".\"hausnummern_hro'
    unique_together = ['strasse', 'hausnummer', 'hausnummer_zusatz']
    verbose_name = 'Hausnummer'
    verbose_name_plural = 'Hausnummern'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Hausnummern der Hanse- und Universitätsstadt Rostock'
    catalog_link_fields = {
      'gebaeude_bauweise': 'https://geo.sv.rostock.de/alkis-ok/31001/baw/',
      'gebaeude_funktion': 'https://geo.sv.rostock.de/alkis-ok/31001/gfk/'
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
      'gebaeude_funktion': 'Funktion des Gebäudes'
    }
    list_fields_with_date = [
      'deaktiviert',
      'vergabe_datum'
    ]
    list_fields_with_foreign_key = {
      'strasse': 'strasse',
      'gebaeude_bauweise': 'bezeichnung',
      'gebaeude_funktion': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'hausnummern-vergabe_datum',
        'action_title': 'ausgewählten Datensätzen Datum der Vergabe direkt zuweisen',
        'field': 'vergabe_datum',
        'type': 'date',
        'value_required': True
      }
    ]
    map_heavy_load_limit = 800
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
    map_filter_fields_as_list = ['strasse', 'gebaeude_bauweise', 'gebaeude_funktion']

  def __str__(self):
    return str(self.strasse) + ' ' + str(self.hausnummer) + \
      (self.hausnummer_zusatz if self.hausnummer_zusatz else '') + \
      ' [Postleitzahl: ' + self.postleitzahl + ']'


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
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  plaetze = PositiveSmallIntegerMinField(
    verbose_name='Plätze',
    min_value=1,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"hospize_hro'
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
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'hospize-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ']'


class Hundetoiletten(SimpleModel):
  """
  Hundetoiletten
  """

  deaktiviert = DateField(
    verbose_name='Außerbetriebstellung',
    blank=True,
    null=True
  )
  id = CharField(
    verbose_name='ID',
    max_length=8,
    unique=True,
    default='00000000'
  )
  art = ForeignKey(
    to=Arten_Hundetoiletten,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  aufstellungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Aufstellungsjahr',
    max_value=get_current_year(),
    blank=True,
    null=True
  )
  bewirtschafter = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter'
  )
  pflegeobjekt = CharField(
    verbose_name='Pflegeobjekt',
    max_length=255,
    validators=standard_validators
  )
  inventarnummer = CharField(
    verbose_name='Inventarnummer',
    max_length=8,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=inventarnummer_regex,
        message=inventarnummer_message
      )
    ]
  )
  anschaffungswert = DecimalField(
    verbose_name='Anschaffungswert (in €)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Anschaffungswert</em></strong> muss mindestens 0,01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9999.99'),
        'Der <strong><em>Anschaffungswert</em></strong> darf höchstens 9.999,99 € betragen.'
      )
    ],
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
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"hundetoiletten_hro'
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
      'pflegeobjekt': 'Pflegeobjekt'
    }
    list_fields_with_date = ['deaktiviert']
    list_fields_with_foreign_key = {
      'art': 'art',
      'bewirtschafter': 'bezeichnung'
    }
    map_feature_tooltip_fields = ['id']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'id': 'ID',
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'pflegeobjekt': 'Pflegeobjekt'
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
      RegexValidator(
        regex=hydranten_bezeichnung_regex,
        message=hydranten_bezeichnung_message
      )
    ]
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer'
  )
  bewirtschafter = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter'
  )
  feuerloeschgeeignet = BooleanField(' feuerlöschgeeignet?')
  betriebszeit = ForeignKey(
    to=Betriebszeiten,
    verbose_name='Betriebszeit',
    on_delete=RESTRICT,
    db_column='betriebszeit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betriebszeiten'
  )
  entnahme = CharField(
    verbose_name='Entnahme',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  hauptwasserzaehler = CharField(
    verbose_name='Hauptwasserzähler',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"hydranten_hro'
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
      'hauptwasserzaehler': 'Hauptwasserzähler'
    }
    list_fields_with_foreign_key = {
      'eigentuemer': 'bezeichnung',
      'bewirtschafter': 'bezeichnung',
      'betriebszeit': 'betriebszeit'
    }
    list_actions_assign = [
      {
        'action_name': 'hydranten-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey'
      },
      {
        'action_name': 'hydranten-bewirtschafter',
        'action_title': 'ausgewählten Datensätzen Bewirtschafter direkt zuweisen',
        'field': 'bewirtschafter',
        'type': 'foreignkey'
      },
      {
        'action_name': 'hydranten-feuerloeschgeeignet',
        'action_title': 'ausgewählten Datensätzen feuerlöschgeeignet (ja/nein) direkt zuweisen',
        'field': 'feuerloeschgeeignet',
        'type': 'boolean'
      },
      {
        'action_name': 'hydranten-betriebszeit',
        'action_title': 'ausgewählten Datensätzen Betriebszeit direkt zuweisen',
        'field': 'betriebszeit',
        'type': 'foreignkey'
      }
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
      'hauptwasserzaehler': 'Hauptwasserzähler'
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
    null=True
  )
  nummer = CharField(
    verbose_name='Nummer',
    max_length=255,
    validators=standard_validators
  )
  nummer_asb = CharField(
    verbose_name='ASB-Nummer',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=ingenieurbauwerke_nummer_asb_regex,
        message=ingenieurbauwerke_nummer_asb_message
      )
    ]
  )
  art = ForeignKey(
    to=Arten_Ingenieurbauwerke,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  baujahr = CharField(
    verbose_name='Baujahr',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=ingenieurbauwerke_baujahr_regex,
        message=ingenieurbauwerke_baujahr_message
      )
    ]
  )
  ausfuehrung = ForeignKey(
    to=Ausfuehrungen_Ingenieurbauwerke,
    verbose_name='Ausführung',
    on_delete=SET_NULL,
    db_column='ausfuehrung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ausfuehrungen',
    blank=True,
    null=True
  )
  oben = CharField(
    verbose_name='Verkehrsweg oben',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  unten = CharField(
    verbose_name='Verkehrsweg unten',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  flaeche = DecimalField(
    verbose_name='Fläche (in m²)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Fläche</em></strong> muss mindestens 0,01 m² betragen.'
      ),
      MaxValueValidator(
        Decimal('9999.99'),
        'Die <strong><em>Fläche</em></strong> darf höchstens 9.999,99 m² betragen.'
      )
    ],
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
  breite = CharField(
    verbose_name='Breite',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  hoehe = CharField(
    verbose_name='Höhe',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  lichte_weite = DecimalField(
    verbose_name=' lichte Weite (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>lichte Weite</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>lichte Weite</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  lichte_hoehe = CharField(
    verbose_name=' lichte Höhe',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  durchfahrtshoehe = DecimalField(
    verbose_name='Durchfahrtshöhe (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Durchfahrtshöhe</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Durchfahrtshöhe</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  nennweite = CharField(
    verbose_name='Nennweite',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  schwerlast = BooleanField(
    verbose_name='Schwerlast?'
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug\".\"ingenieurbauwerke_hro'
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
      'schwerlast': 'Schwerlast'
    }
    list_fields_with_decimal = ['flaeche', 'laenge', 'lichte_weite', 'durchfahrtshoehe']
    list_fields_with_foreign_key = {
      'art': 'art',
      'strasse': 'strasse',
      'ausfuehrung': 'ausfuehrung'
    }
    list_actions_assign = [
      {
        'action_name': 'ingenieurbauwerke-art',
        'action_title': 'ausgewählten Datensätzen Art direkt zuweisen',
        'field': 'art',
        'type': 'foreignkey'
      },
      {
        'action_name': 'ingenieurbauwerke-ausfuehrung',
        'action_title': 'ausgewählten Datensätzen Ausführung direkt zuweisen',
        'field': 'ausfuehrung',
        'type': 'foreignkey'
      },
      {
        'action_name': 'ingenieurbauwerke-schwerlast',
        'action_title': 'ausgewählten Datensätzen Schwerlast (ja/nein) direkt zuweisen',
        'field': 'schwerlast',
        'type': 'boolean'
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
      'schwerlast': 'Schwerlast'
    }
    map_filter_fields_as_list = ['art', 'strasse', 'ausfuehrung']

  def __str__(self):
    return self.nummer


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
    related_name='%(app_label)s_%(class)s_tierseuchen'
  )
  geschlecht = ForeignKey(
    to=Geschlechter_Kadaverfunde,
    verbose_name='Geschlecht',
    on_delete=RESTRICT,
    db_column='geschlecht',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_geschlechter'
  )
  altersklasse = ForeignKey(
    to=Altersklassen_Kadaverfunde,
    verbose_name='Altersklasse',
    on_delete=RESTRICT,
    db_column='altersklasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_altersklassen'
  )
  gewicht = PositiveSmallIntegerRangeField(
    verbose_name=' geschätztes Gewicht (in kg)',
    min_value=1,
    blank=True,
    null=True
  )
  zustand = ForeignKey(
    to=Zustaende_Kadaverfunde,
    verbose_name='Zustand',
    on_delete=RESTRICT,
    db_column='zustand',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende'
  )
  art_auffinden = ForeignKey(
    to=Arten_Fallwildsuchen_Kontrollen,
    verbose_name='Art des Auffindens',
    on_delete=RESTRICT,
    db_column='art_auffinden',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten_auffinden'
  )
  witterung = CharField(
    verbose_name='Witterung vor Ort',
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

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"kadaverfunde_hro'
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
      'zeitpunkt': 'Zeitpunkt'
    }
    list_fields_with_datetime = ['zeitpunkt']
    list_fields_with_foreign_key = {
      'tierseuche': 'bezeichnung',
      'geschlecht': 'bezeichnung',
      'altersklasse': 'bezeichnung',
      'zustand': 'zustand',
      'art_auffinden': 'art'
    }
    map_feature_tooltip_fields = ['tierseuche', 'zeitpunkt']
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

  def __str__(self):
    local_tz = ZoneInfo(settings.TIME_ZONE)
    zeitpunkt_str = sub(r'([+-][0-9]{2}):', '\\1', str(self.zeitpunkt))
    zeitpunkt = datetime.strptime(
      zeitpunkt_str,
      '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=timezone.utc).astimezone(local_tz)
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
    related_name='%(app_label)s_%(class)s_adressen'
  )
  bevollmaechtigter_bezirksschornsteinfeger = ForeignKey(
    to=Bevollmaechtigte_Bezirksschornsteinfeger,
    verbose_name=' bevollmächtigter Bezirksschornsteinfeger',
    on_delete=RESTRICT,
    db_column='bevollmaechtigter_bezirksschornsteinfeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bevollmaechtigte_bezirksschornsteinfeger',
    blank=True,
    null=True
  )
  vergabedatum = DateField(
    verbose_name='Vergabedatum der Adresse',
    blank=True,
    null=True
  )

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"kehrbezirke_hro'
    verbose_name = 'Kehrbezirk'
    verbose_name_plural = 'Kehrbezirke'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Kehrbezirke der bevollmächtigten Bezirksschornsteinfeger ' \
                  'in der Hanse- und Universitätsstadt Rostock'
    readonly_fields = ['vergabedatum']
    address_search_long_results = True
    address_type = 'Adresse'
    address_mandatory = True
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bevollmaechtigter_bezirksschornsteinfeger': 'bevollmächtigter Bezirksschornsteinfeger',
      'vergabedatum': 'Vergabedatum der Adresse'
    }
    list_fields_with_date = ['vergabedatum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse_lang',
      'bevollmaechtigter_bezirksschornsteinfeger': 'nachname'
    }
    list_actions_assign = [
      {
        'action_name': 'kehrbezirke-bevollmaechtigter_bezirksschornsteinfeger',
        'action_title': 'ausgewählten Datensätzen bevollmächtigten '
                        'Bezirksschornsteinfeger direkt zuweisen',
        'field': 'bevollmaechtigter_bezirksschornsteinfeger',
        'type': 'foreignkey'
      }
    ]

  def __str__(self):
    return (str(self.adresse.adresse_lang) + ' zu ' +
            str(self.bevollmaechtigter_bezirksschornsteinfeger))


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
    null=True
  )
  vorname = CharField(
    verbose_name='Vorname',
    max_length=255,
    validators=personennamen_validators
  )
  nachname = CharField(
    verbose_name='Nachname',
    max_length=255,
    validators=personennamen_validators
  )
  plaetze = PositiveSmallIntegerMinField(
    verbose_name='Plätze',
    min_value=1,
    blank=True,
    null=True
  )
  zeiten = CharField(
    verbose_name='Betreuungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"kindertagespflegeeinrichtungen_hro'
    verbose_name = 'Kindertagespflegeeinrichtung'
    verbose_name_plural = 'Kindertagespflegeeinrichtungen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Kindertagespflegeeinrichtungen (Tagesmütter und Tagesväter) in der Hanse- ' \
                  'und Universitätsstadt Rostock'
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'plaetze': 'Plätze',
      'zeiten': 'Betreuungszeiten'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_fields = ['vorname', 'nachname']
    map_filter_fields = {
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'plaetze': 'Plätze'
    }

  def __str__(self):
    return self.vorname + ' ' + self.nachname + \
      (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


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
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"kinder_jugendbetreuung_hro'
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
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'kinder_jugendbetreuung-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') \
      + 'Träger: ' + str(self.traeger) + ']'


class Kleinklaeranlagen(SimpleModel):
  """
  Kleinkläranlagen
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
  d3 = CharField(
    verbose_name=' d.3',
    max_length=16,
    validators=[
      RegexValidator(
        regex=d3_regex,
        message=d3_message
      )
    ]
  )
  we_datum = DateField(
    verbose_name='Datum der wasserrechtlichen Erlaubnis',
    default=date.today
  )
  we_aktenzeichen = CharField(
    verbose_name='Aktenzeichen der wasserrechtlichen Erlaubnis',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  we_befristung = DateField(
    verbose_name='Befristung der wasserrechtlichen Erlaubnis',
    blank=True,
    null=True
  )
  typ = ForeignKey(
    to=Typen_Kleinklaeranlagen,
    verbose_name='Anlagetyp',
    on_delete=RESTRICT,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen'
  )
  einleitstelle = CharField(
    verbose_name='Einleitstelle',
    max_length=255,
    validators=standard_validators
  )
  gewaesser_berichtspflichtig = BooleanField(
    verbose_name=' berichtspflichtiges Gewässer?',
  )
  umfang_einleitung = DecimalField(
    verbose_name='Umfang der Einleitung (in m³/d)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>Umfang der Einleitung</em></strong> muss mindestens 0,01 m³/d betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Der <strong><em>Umfang der Einleitung</em></strong> darf höchstens 9,99 m³/d betragen.'
      )
    ],
    blank=True,
    null=True
  )
  einwohnerwert = DecimalField(
    verbose_name='Einwohnerwert',
    max_digits=3,
    decimal_places=1,
    validators=[
      MinValueValidator(
        Decimal('0.1'),
        'Der <strong><em>Einwohnerwert</em></strong> muss mindestens 0,1 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.9'),
        'Der <strong><em>Einwohnerwert</em></strong> darf höchstens 99,9 betragen.'
      )
    ],
    blank=True,
    null=True
  )
  zulassung = CharField(
    verbose_name='Zulassung',
    max_length=11,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=kleinklaeranlagen_zulassung_regex,
        message=kleinklaeranlagen_zulassung_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"kleinklaeranlagen_hro'
    verbose_name = 'Kleinkläranlage'
    verbose_name_plural = 'Kleinkläranlagen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Kleinkläranlagen in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'd3': 'd.3',
      'we_datum': 'Datum der wasserrechtlichen Erlaubnis',
      'we_aktenzeichen': 'Aktenzeichen der wasserrechtlichen Erlaubnis',
      'we_befristung': 'Befristung der wasserrechtlichen Erlaubnis',
      'typ': 'Anlagetyp',
      'einleitstelle': 'Einleitstelle',
      'adresse': 'Adresse',
      'gewaesser_berichtspflichtig': 'berichtspflichtiges Gewässer?',
      'umfang_einleitung': 'Umfang der Einleitung (in m³/d)',
      'einwohnerwert': 'Einwohnerwert',
      'zulassung': 'Zulassung'
    }
    list_fields_with_date = ['we_datum', 'we_befristung']
    list_fields_with_decimal = ['umfang_einleitung', 'einwohnerwert']
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'typ': 'typ'
    }
    map_feature_tooltip_fields = ['d3']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'd3': 'd.3',
      'we_datum': 'Datum der wasserrechtlichen Erlaubnis',
      'we_aktenzeichen': 'Aktenzeichen der wasserrechtlichen Erlaubnis',
      'we_befristung': 'Befristung der wasserrechtlichen Erlaubnis',
      'typ': 'Anlagetyp',
      'einleitstelle': 'Einleitstelle',
      'gewaesser_berichtspflichtig': 'berichtspflichtiges Gewässer?',
      'umfang_einleitung': 'Umfang der Einleitung (in m³/d)',
      'einwohnerwert': 'Einwohnerwert',
      'zulassung': 'Zulassung'
    }
    map_filter_fields_as_list = ['typ']

  def __str__(self):
    return self.d3 + ' mit Datum der wasserrechtlichen Erlaubnis ' + str(self.we_datum)


class Kunst_im_oeffentlichen_Raum(SimpleModel):
  """
  Kunst im öffentlichen Raum
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  ausfuehrung = CharField(
    verbose_name='Ausführung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  schoepfer = CharField(
    verbose_name='Schöpfer',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  entstehungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Entstehungsjahr',
    max_value=get_current_year(),
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"kunst_im_oeffentlichen_raum_hro'
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
      'entstehungsjahr': 'Entstehungsjahr'
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
    null=True
  )
  geplant = BooleanField(' geplant?')
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  betreiber = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=SET_NULL,
    db_column='betreiber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betreiber',
    blank=True,
    null=True
  )
  verbund = ForeignKey(
    to=Verbuende_Ladestationen_Elektrofahrzeuge,
    verbose_name='Verbund',
    on_delete=SET_NULL,
    db_column='verbund',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_verbuende',
    blank=True,
    null=True
  )
  betriebsart = ForeignKey(
    to=Betriebsarten,
    verbose_name='Betriebsart',
    on_delete=RESTRICT,
    db_column='betriebsart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betriebsarten'
  )
  anzahl_ladepunkte = PositiveSmallIntegerMinField(
    verbose_name='Anzahl an Ladepunkten',
    min_value=1,
    blank=True,
    null=True
  )
  arten_ladepunkte = CharField(
    verbose_name='Arten der Ladepunkte',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  ladekarten = ChoiceArrayField(
    CharField(
      verbose_name='Ladekarten',
      max_length=255,
      choices=()
    ),
    verbose_name='Ladekarten',
    blank=True,
    null=True
  )
  kosten = CharField(
    verbose_name='Kosten',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  zeiten = CharField(
    verbose_name='Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"ladestationen_elektrofahrzeuge_hro'
    verbose_name = 'Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Ladestationen für Elektrofahrzeuge'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Ladestationen für Elektrofahrzeuge in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'ladekarten': 'Ladekarten_Ladestationen_Elektrofahrzeuge'
    }
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
      'ladekarten': 'Ladekarten'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'betreiber': 'bezeichnung',
      'verbund': 'verbund',
      'betriebsart': 'betriebsart'
    }
    list_actions_assign = [
      {
        'action_name': 'ladestationen_elektrofahrzeuge-geplant',
        'action_title': 'ausgewählten Datensätzen geplant (ja/nein) direkt zuweisen',
        'field': 'geplant',
        'type': 'boolean'
      },
      {
        'action_name': 'ladestationen_elektrofahrzeuge-betreiber',
        'action_title': 'ausgewählten Datensätzen Betreiber direkt zuweisen',
        'field': 'betreiber',
        'type': 'foreignkey'
      },
      {
        'action_name': 'ladestationen_elektrofahrzeuge-verbund',
        'action_title': 'ausgewählten Datensätzen Verbund direkt zuweisen',
        'field': 'verbund',
        'type': 'foreignkey'
      },
      {
        'action_name': 'ladestationen_elektrofahrzeuge-betriebsart',
        'action_title': 'ausgewählten Datensätzen Betriebsart direkt zuweisen',
        'field': 'betriebsart',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
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
    related_name='%(app_label)s_%(class)s_arten'
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
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
  datum = DateField(
    verbose_name='Datum',
    default=date.today
  )
  geometrie = polygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"meldedienst_flaechenhaft_hro'
    verbose_name = 'Meldedienst (flächenhaft)'
    verbose_name_plural = 'Meldedienst (flächenhaft)'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Meldedienst (flächenhaft) der Hanse- und Universitätsstadt Rostock'
    geometry_type = 'Polygon'
    list_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bearbeiter': 'Bearbeiter:in',
      'bemerkungen': 'Bemerkungen',
      'datum': 'Datum'
    }
    list_fields_with_date = ['datum']
    list_fields_with_foreign_key = {
      'art': 'art'
    }
    map_feature_tooltip_fields = ['art']
    map_filter_fields = {
      'art': 'Art',
      'bearbeiter': 'Bearbeiter:in',
      'datum': 'Datum'
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return str(self.art) + \
      ' [Datum: ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + ']'


class Meldedienst_punkthaft(SimpleModel):
  """
  Meldedienst (punkthaft)
  """

  deaktiviert = DateField(
    verbose_name='Zurückstellung',
    blank=True,
    null=True
  )
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
    to=Arten_Meldedienst_punkthaft,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bearbeiter = CharField(
    verbose_name='Bearbeiter:in',
    max_length=255,
    validators=standard_validators
  )
  gebaeudeart = ForeignKey(
    to=Gebaeudearten_Meldedienst_punkthaft,
    verbose_name='Gebäudeart',
    on_delete=RESTRICT,
    db_column='gebaeudeart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gebaeudearten',
    blank=True,
    null=True
  )
  flaeche = DecimalField(
    verbose_name='Fläche (in m²)',
    max_digits=6,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Fläche</em></strong> muss mindestens 0,01 m² betragen.'
      ),
      MaxValueValidator(
        Decimal('9999.99'),
        'Die <strong><em>Fläche</em></strong> darf höchstens 9.999,99 m² betragen.'
      )
    ],
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
  datum = DateField(
    verbose_name='Datum',
    default=date.today
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"meldedienst_punkthaft_hro'
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
      'datum': 'Datum'
    }
    list_fields_with_date = ['deaktiviert', 'datum']
    list_fields_with_decimal = ['flaeche']
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'art': 'art',
      'gebaeudeart': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'meldedienst_punkthaft-gebaeudeart',
        'action_title': 'ausgewählten Datensätzen Gebäudeart direkt zuweisen',
        'field': 'gebaeudeart',
        'type': 'foreignkey'
      },
      {
        'action_name': 'meldedienst_punkthaft-datum',
        'action_title': 'ausgewählten Datensätzen Datum direkt zuweisen',
        'field': 'datum',
        'type': 'date',
        'value_required': True
      }
    ]
    map_heavy_load_limit = 600
    map_feature_tooltip_fields = ['art']
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'art': 'Art',
      'bearbeiter': 'Bearbeiter:in',
      'gebaeudeart': 'Gebäudeart',
      'bemerkungen': 'Bemerkungen',
      'datum': 'Datum'
    }
    map_filter_fields_as_list = ['art', 'gebaeudeart']

  def __str__(self):
    return str(self.art) + \
      ' [Datum: ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + \
      (', Adresse: ' + str(self.adresse) if self.adresse else '') + ']'


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
    null=True
  )
  stob = CharField(
    verbose_name='Standortbescheinigungsnummer',
    max_length=255,
    validators=[
      RegexValidator(
        regex=mobilfunkantennen_stob_regex,
        message=mobilfunkantennen_stob_message
      )
    ]
  )
  erteilungsdatum = DateField(
    verbose_name='Erteilungsdatum',
    default=date.today
  )
  techniken = ArrayField(
    CharField(
      verbose_name='Techniken',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators
    ),
    verbose_name='Techniken',
    blank=True,
    null=True
  )
  betreiber = ArrayField(
    CharField(
      verbose_name='Betreiber',
      max_length=255,
      blank=True,
      null=True,
      validators=standard_validators
    ),
    verbose_name='Betreiber',
    blank=True,
    null=True
  )
  montagehoehe = CharField(
    verbose_name='Montagehöhe',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  anzahl_gsm = PositiveSmallIntegerMinField(
    verbose_name='Anzahl GSM-Einheiten',
    min_value=1,
    blank=True,
    null=True
  )
  anzahl_umts = PositiveSmallIntegerMinField(
    verbose_name='Anzahl UMTS-Einheiten',
    min_value=1,
    blank=True,
    null=True
  )
  anzahl_lte = PositiveSmallIntegerMinField(
    verbose_name='Anzahl LTE-Einheiten',
    min_value=1,
    blank=True,
    null=True
  )
  anzahl_sonstige = PositiveSmallIntegerMinField(
    verbose_name='Anzahl sonstige Einheiten',
    min_value=1,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"mobilfunkantennen_hro'
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
      'anzahl_sonstige': 'Anzahl sonstige Einheiten'
    }
    list_fields_with_date = ['erteilungsdatum']
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
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
      'anzahl_sonstige': 'Anzahl sonstige Einheiten'
    }

  def __str__(self):
    return self.stob


class Mobilpunkte(SimpleModel):
  """
  Mobilpunkte
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  angebote = ChoiceArrayField(
    CharField(
      verbose_name='Angebote',
      max_length=255,
      choices=()
    ),
    verbose_name='Angebote'
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"mobilpunkte_hro'
    verbose_name = 'Mobilpunkt'
    verbose_name_plural = 'Mobilpunkte'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Mobilpunkte in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'angebote': 'Angebote_Mobilpunkte'
    }
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'bezeichnung': 'Bezeichnung',
      'angebote': 'Angebote',
      'website': 'Website'
    }
    map_feature_tooltip_fields = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung


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
    null=True
  )
  art = ForeignKey(
    to=Arten_Parkmoeglichkeiten,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  standort = CharField(
    verbose_name='Standort',
    max_length=255,
    validators=standard_validators
  )
  betreiber = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=SET_NULL,
    db_column='betreiber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betreiber',
    blank=True,
    null=True
  )
  stellplaetze_pkw = PositiveSmallIntegerMinField(
    verbose_name='Pkw-Stellplätze',
    min_value=1,
    blank=True,
    null=True
  )
  stellplaetze_wohnmobil = PositiveSmallIntegerMinField(
    verbose_name='Wohnmobilstellplätze',
    min_value=1,
    blank=True,
    null=True
  )
  stellplaetze_bus = PositiveSmallIntegerMinField(
    verbose_name='Busstellplätze',
    min_value=1,
    blank=True,
    null=True
  )
  gebuehren_halbe_stunde = DecimalField(
    verbose_name='Gebühren pro ½ h (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro ½ h</em></strong> müssen mindestens 0,01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro ½ h</em></strong> dürfen höchstens 9,99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  gebuehren_eine_stunde = DecimalField(
    verbose_name='Gebühren pro 1 h (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro 1 h</em></strong> müssen mindestens 0,01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro 1 h</em></strong> dürfen höchstens 9,99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  gebuehren_zwei_stunden = DecimalField(
    verbose_name='Gebühren pro 2 h (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren pro 2 h</em></strong> müssen mindestens 0,01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren pro 2 h</em></strong> dürfen höchstens 9,99 € betragen.'
      )
    ],
    blank=True,
    null=True
  )
  gebuehren_ganztags = DecimalField(
    verbose_name='Gebühren ganztags (in €)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Gebühren ganztags</em></strong> müssen mindestens 0,01 € betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Gebühren ganztags</em></strong> dürfen höchstens 9,99 € betragen.'
      )
    ],
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
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"parkmoeglichkeiten_hro'
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

  def __str__(self):
    return str(self.art) + ' ' + self.standort + \
      (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


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
    null=True
  )
  art = ForeignKey(
    to=Arten_Pflegeeinrichtungen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  betreiber = CharField(
    verbose_name='Betreiber:in',
    max_length=255,
    validators=standard_validators
  )
  plaetze = PositiveSmallIntegerMinField(
    verbose_name='Plätze',
    min_value=1,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"pflegeeinrichtungen_hro'
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
      'betreiber': 'Betreiber:in'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'art': 'art'
    }
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'betreiber': 'Betreiber:in'
    }
    map_filter_fields_as_list = ['art']

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Art: ' + str(self.art) + ']'


class Poller(SimpleModel):
  """
  Poller
  """

  art = ForeignKey(
    to=Arten_Poller,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  nummer = CharField(
    verbose_name='Nummer',
    max_length=3,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=poller_nummer_regex,
        message=poller_nummer_message
      )
    ]
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  status = ForeignKey(
    to=Status_Poller,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
  zeiten = CharField(
    verbose_name='Lieferzeiten',
    max_length=255,
    blank=True,
    null=True
  )
  hersteller = ForeignKey(
    to=Hersteller_Poller,
    verbose_name='Hersteller',
    on_delete=SET_NULL,
    db_column='hersteller',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_hersteller',
    blank=True,
    null=True
  )
  typ = ForeignKey(
    to=Typen_Poller,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
    blank=True,
    null=True
  )
  anzahl = PositiveSmallIntegerMinField(
    verbose_name='Anzahl',
    min_value=1
  )
  schliessungen = ChoiceArrayField(
    CharField(
      verbose_name='Schließungen',
      max_length=255,
      choices=()
    ),
    verbose_name='Schließungen',
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
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"poller_hro'
    verbose_name = 'Poller'
    verbose_name_plural = 'Poller'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Poller in der Hanse- und Universitätsstadt Rostock'
    as_overlay = True
    choices_models_for_choices_fields = {
      'schliessungen': 'Schliessungen_Poller'
    }
    geometry_type = 'Point'
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
    list_fields_with_foreign_key = {
      'art': 'art',
      'status': 'status',
      'hersteller': 'bezeichnung',
      'typ': 'typ'
    }
    list_actions_assign = [
      {
        'action_name': 'poller-status',
        'action_title': 'ausgewählten Datensätzen Status direkt zuweisen',
        'field': 'status',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
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

  def __str__(self):
    return (self.nummer + ', ' if self.nummer else '') + \
      self.bezeichnung + ' [Status: ' + str(self.status) + ']'


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
    null=True
  )
  nummer = PositiveSmallIntegerMinField(
    verbose_name='Nummer',
    min_value=1,
    unique=True,
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  geometrie = multipolygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_gemeindeteilbezug\".\"reinigungsreviere_hro'
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
      'bezeichnung': 'Bezeichnung'
    }
    list_fields_with_foreign_key = {
      'gemeindeteil': 'gemeindeteil'
    }
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'gemeindeteil': 'Gemeindeteil',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung'
    }
    map_filter_fields_as_list = ['gemeindeteil']
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
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  stellplaetze = PositiveSmallIntegerMinField(
    verbose_name='Stellplätze',
    min_value=1
  )
  gebuehren = BooleanField(
    verbose_name='Gebühren?'
  )
  einschraenkungen = CharField(
    verbose_name='Einschränkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"reisebusparkplaetze_terminals_hro'
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
      'einschraenkungen': 'Einschränkungen'
    }
    list_fields_with_foreign_key = {
      'art': 'art'
    }
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'stellplaetze': 'Stellplätze',
      'gebuehren': 'Gebühren',
      'einschraenkungen': 'Einschränkungen'
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
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"rettungswachen_hro'
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
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'rettungswachen-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ']'


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
    related_name='%(app_label)s_%(class)s_haefen'
  )
  liegeplatznummer = CharField(
    verbose_name='Liegeplatz',
    max_length=255,
    validators=standard_validators
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  liegeplatzlaenge = DecimalField(
    verbose_name='Liegeplatzlänge (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Liegeplatzlänge</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>Liegeplatzlänge</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  zulaessiger_tiefgang = DecimalField(
    verbose_name=' zulässiger Tiefgang (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der <strong><em>zulässige Tiefgang</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der <strong><em>zulässige Tiefgang</em></strong> darf höchstens 99,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  zulaessige_schiffslaenge = DecimalField(
    verbose_name=' zulässige Schiffslänge (in m)',
    max_digits=5,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>zulässige Schiffslänge</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('999.99'),
        'Die <strong><em>zulässige Schiffslänge</em></strong> darf höchstens 999,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  kaihoehe = DecimalField(
    verbose_name='Kaihöhe (in m)',
    max_digits=3,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Kaihöhe</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('9.99'),
        'Die <strong><em>Kaihöhe</em></strong> darf höchstens 9,99 m betragen.'
      )
    ],
    blank=True,
    null=True
  )
  pollerzug = CharField(
    verbose_name='Pollerzug',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  poller_von = CharField(
    verbose_name='Poller (von)',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  poller_bis = CharField(
    verbose_name='Poller (bis)',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  geometrie = polygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"schiffsliegeplaetze_hro'
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
      'zulaessiger_tiefgang': 'zulässiger Tiefgang (in m)'
    }
    list_fields_with_decimal = ['zulaessiger_tiefgang']
    list_fields_with_foreign_key = {
      'hafen': 'bezeichnung'
    }
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'hafen': 'Hafen',
      'liegeplatznummer': 'Liegeplatz',
      'bezeichnung': 'Bezeichnung',
      'zulaessiger_tiefgang': 'zulässiger Tiefgang (in m)'
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
    related_name='%(app_label)s_%(class)s_tierseuchen'
  )
  zustand = ForeignKey(
    to=Zustaende_Schutzzaeune_Tierseuchen,
    verbose_name='Zustand',
    on_delete=RESTRICT,
    db_column='zustand',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende'
  )
  laenge = PositiveIntegerField(
    verbose_name='Länge (in m)',
    default=0
  )
  geometrie = multiline_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"schutzzaeune_tierseuchen_hro'
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
      'zustand': 'Zustand'
    }
    list_fields_with_foreign_key = {
      'tierseuche': 'bezeichnung',
      'zustand': 'zustand'
    }
    list_actions_assign = [
      {
        'action_name': 'schutzzaeune_tierseuchen-zustand',
        'action_title': 'ausgewählten Datensätzen Zustand direkt zuweisen',
        'field': 'zustand',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['zustand']
    map_filter_fields = {
      'tierseuche': 'Tierseuche',
      'zustand': 'Zustand'
    }
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
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC + 'sportanlagen'
    ),
    max_length=255,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"sportanlagen_hro'
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
      'foto': 'Foto'
    }
    list_fields_with_foreign_key = {
      'art': 'art',
      'traeger': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'sportanlagen-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
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
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  sportart = ForeignKey(
    to=Sportarten,
    verbose_name='Sportart',
    on_delete=RESTRICT,
    db_column='sportart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_sportarten'
  )
  barrierefrei = BooleanField(
    verbose_name=' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    verbose_name='Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  foto = ImageField(
    verbose_name='Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC + 'sporthallen'
    ),
    max_length=255,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"sporthallen_hro'
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
      'foto': 'Foto'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'traeger': 'bezeichnung',
      'sportart': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'sporthallen-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey'
      },
      {
        'action_name': 'sporthallen-sportart',
        'action_title': 'ausgewählten Datensätzen Sportart direkt zuweisen',
        'field': 'sportart',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger',
      'sportart': 'Sportart'
    }
    map_filter_fields_as_list = ['traeger', 'sportart']

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ', Sportart: ' + str(self.sportart) + ']'


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
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  barrierefrei = BooleanField(
    verbose_name=' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    verbose_name='Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"stadtteil_begegnungszentren_hro'
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
      'traeger': 'Träger'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'traeger': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'stadtteil_begegnungszentren-traeger',
        'action_title': 'ausgewählten Datensätzen Träger direkt zuweisen',
        'field': 'traeger',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'traeger': 'Träger'
    }
    map_filter_fields_as_list = ['traeger']

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ']'


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
    null=True
  )
  bewertungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Bewertungsjahr',
    min_value=1990,
    max_value=get_current_year(),
    default=get_current_year()
  )
  quartier = ForeignKey(
    to=Quartiere,
    verbose_name='Quartier',
    on_delete=RESTRICT,
    db_column='quartier',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_quartiere'
  )
  kundschaftskontakte_anfangswert = DecimalField(
    verbose_name='Kundschaftskontakte (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Kundschaftskontakte</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Kundschaftskontakte</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  kundschaftskontakte_endwert = DecimalField(
    verbose_name='Kundschaftskontakte (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Kundschaftskontakte</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Kundschaftskontakte</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  verkehrsanbindung_anfangswert = DecimalField(
    verbose_name='Verkehrsanbindung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Verkehrsanbindung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Verkehrsanbindung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  verkehrsanbindung_endwert = DecimalField(
    verbose_name='Verkehrsanbindung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Verkehrsanbindung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Verkehrsanbindung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  ausstattung_anfangswert = DecimalField(
    verbose_name='Ausstattung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Ausstattung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Ausstattung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  ausstattung_endwert = DecimalField(
    verbose_name='Ausstattung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Ausstattung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Ausstattung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  beeintraechtigung_anfangswert = DecimalField(
    verbose_name='Beeinträchtigung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Beeinträchtigung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Beeinträchtigung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  beeintraechtigung_endwert = DecimalField(
    verbose_name='Beeinträchtigung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Beeinträchtigung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Beeinträchtigung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  standortnutzung_anfangswert = DecimalField(
    verbose_name='Standortnutzung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Standortnutzung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Standortnutzung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  standortnutzung_endwert = DecimalField(
    verbose_name='Standortnutzung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Standortnutzung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Standortnutzung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"standortqualitaeten_geschaeftslagen_sanierungsgebiet_hro'
    verbose_name = 'Standortqualität einer Geschäftslage im Sanierungsgebiet'
    verbose_name_plural = 'Standortqualitäten von Geschäftslagen im Sanierungsgebiet'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Standortqualitäten von Geschäftslagen ' \
                  'im Sanierungsgebiet der Hanse- und Universitätsstadt Rostock'
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
      'standortnutzung_endwert': 'Standortnutzung (Endwert)'
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
      'standortnutzung_endwert'
    ]
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'quartier': 'code'
    }
    map_feature_tooltip_fields = ['adresse']
    map_filter_fields = {
      'adresse': 'Adresse',
      'bewertungsjahr': 'Bewertungsjahr',
      'quartier': 'Quartier'
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
    null=True
  )
  bewertungsjahr = PositiveSmallIntegerRangeField(
    verbose_name='Bewertungsjahr',
    min_value=1990,
    max_value=get_current_year(),
    default=get_current_year()
  )
  quartier = ForeignKey(
    to=Quartiere,
    verbose_name='Quartier',
    on_delete=RESTRICT,
    db_column='quartier',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_quartiere'
  )
  gesellschaftslage_anfangswert = DecimalField(
    verbose_name='Gesellschaftslage (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Gesellschaftslage</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Gesellschaftslage</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  gesellschaftslage_endwert = DecimalField(
    verbose_name='Gesellschaftslage (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Gesellschaftslage</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Gesellschaftslage</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  verkehrsanbindung_anfangswert = DecimalField(
    verbose_name='Verkehrsanbindung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Verkehrsanbindung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Verkehrsanbindung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  verkehrsanbindung_endwert = DecimalField(
    verbose_name='Verkehrsanbindung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Verkehrsanbindung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Verkehrsanbindung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  ausstattung_anfangswert = DecimalField(
    verbose_name='Ausstattung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Ausstattung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Ausstattung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  ausstattung_endwert = DecimalField(
    verbose_name='Ausstattung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Ausstattung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Ausstattung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  beeintraechtigung_anfangswert = DecimalField(
    verbose_name='Beeinträchtigung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Beeinträchtigung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Beeinträchtigung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  beeintraechtigung_endwert = DecimalField(
    verbose_name='Beeinträchtigung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Beeinträchtigung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Beeinträchtigung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  standortnutzung_anfangswert = DecimalField(
    verbose_name='Standortnutzung (Anfangswert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Anfangswert <strong><em>Standortnutzung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Anfangswert <strong><em>Standortnutzung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  standortnutzung_endwert = DecimalField(
    verbose_name='Standortnutzung (Endwert)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Der Endwert <strong><em>Standortnutzung</em></strong> '
        'muss mindestens 0,01 betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Der Endwert <strong><em>Standortnutzung</em></strong> '
        'darf höchstens 99,99 betragen.'
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"standortqualitaeten_wohnlagen_sanierungsgebiet_hro'
    verbose_name = 'Standortqualität einer Wohnlage im Sanierungsgebiet'
    verbose_name_plural = 'Standortqualitäten von Wohnlagen im Sanierungsgebiet'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Standortqualitäten von Wohnlagen ' \
                  'im Sanierungsgebiet der Hanse- und Universitätsstadt Rostock'
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
      'standortnutzung_endwert': 'Standortnutzung (Endwert)'
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
      'standortnutzung_endwert'
    ]
    list_fields_with_foreign_key = {
      'adresse': 'adresse',
      'quartier': 'code'
    }
    map_feature_tooltip_fields = ['adresse']
    map_filter_fields = {
      'adresse': 'Adresse',
      'bewertungsjahr': 'Bewertungsjahr',
      'quartier': 'Quartier'
    }
    map_filter_fields_as_list = ['quartier']

  def __str__(self):
    return str(self.adresse)


class Thalasso_Kurwege(SimpleModel):
  """
  Thalasso-Kurwege
  """

  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  streckenbeschreibung = CharField(
    verbose_name='Streckenbeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  barrierefrei = BooleanField(
    verbose_name=' barrierefrei?',
    default=False
  )
  farbe = CharField(
    verbose_name='Farbe',
    max_length=7
  )
  beschriftung = CharField(
    verbose_name='Beschriftung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  laenge = PositiveIntegerField(
    verbose_name='Länge (in m)',
    default=0
  )
  geometrie = line_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"thalasso_kurwege_hro'
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
      'laenge': 'Länge (in m)'
    }
    list_actions_assign = [
      {
        'action_name': 'thalasso_kurwege-barrierefrei',
        'action_title': 'ausgewählten Datensätzen barrierefrei (ja/nein) direkt zuweisen',
        'field': 'barrierefrei',
        'type': 'boolean'
      }
    ]
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'streckenbeschreibung': 'Streckenbeschreibung',
      'barrierefrei': 'barrierefrei?'
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
    related_name='%(app_label)s_%(class)s_arten'
  )
  bewirtschafter = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=SET_NULL,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter',
    blank=True,
    null=True
  )
  behindertengerecht = BooleanField(' behindertengerecht?')
  duschmoeglichkeit = BooleanField('Duschmöglichkeit vorhanden?')
  wickelmoeglichkeit = BooleanField('Wickelmöglichkeit vorhanden?')
  zeiten = CharField(
    verbose_name='Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"toiletten_hro'
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
      'zeiten': 'Öffnungszeiten'
    }
    list_fields_with_foreign_key = {
      'art': 'art',
      'bewirtschafter': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'toiletten-bewirtschafter',
        'action_title': 'ausgewählten Datensätzen Bewirtschafter direkt zuweisen',
        'field': 'bewirtschafter',
        'type': 'foreignkey'
      }
    ]
    map_feature_tooltip_fields = ['art']
    map_filter_fields = {
      'art': 'Art',
      'bewirtschafter': 'Bewirtschafter',
      'behindertengerecht': 'behindertengerecht?',
      'duschmoeglichkeit': 'Duschmöglichkeit vorhanden?',
      'wickelmoeglichkeit': 'Wickelmöglichkeit?'
    }
    map_filter_fields_as_list = ['art', 'bewirtschafter']

  def __str__(self):
    return str(self.art) + \
      (' [Bewirtschafter: ' + str(self.bewirtschafter) + ']' if self.bewirtschafter else '') + \
      (' mit Öffnungszeiten ' + self.zeiten + ']' if self.zeiten else '')


class Trinkwassernotbrunnen(SimpleModel):
  """
  Trinkwassernotbrunnen
  """

  nummer = CharField(
    verbose_name='Nummer',
    max_length=12,
    validators=[
      RegexValidator(
        regex=trinkwassernotbrunnen_nummer_regex,
        message=trinkwassernotbrunnen_nummer_message
      )
    ]
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  eigentuemer = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=SET_NULL,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer',
    blank=True,
    null=True
  )
  betreiber = ForeignKey(
    to=Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=RESTRICT,
    db_column='betreiber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betreiber'
  )
  betriebsbereit = BooleanField(' betriebsbereit?')
  bohrtiefe = DecimalField(
    verbose_name='Bohrtiefe (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Bohrtiefe</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Bohrtiefe</em></strong> darf höchstens 99,99 m betragen.'
      )
    ]
  )
  ausbautiefe = DecimalField(
    verbose_name='Ausbautiefe (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Ausbautiefe</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Ausbautiefe</em></strong> darf höchstens 99,99 m betragen.'
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"trinkwassernotbrunnen_hro'
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
      'ausbautiefe': 'Ausbautiefe (in m)'
    }
    list_fields_with_decimal = ['bohrtiefe', 'ausbautiefe']
    list_fields_with_foreign_key = {
      'eigentuemer': 'bezeichnung',
      'betreiber': 'bezeichnung'
    }
    list_actions_assign = [
      {
        'action_name': 'trinkwassernotbrunnen-eigentuemer',
        'action_title': 'ausgewählten Datensätzen Eigentümer direkt zuweisen',
        'field': 'eigentuemer',
        'type': 'foreignkey'
      },
      {
        'action_name': 'trinkwassernotbrunnen-betreiber',
        'action_title': 'ausgewählten Datensätzen Betreiber direkt zuweisen',
        'field': 'betreiber',
        'type': 'foreignkey'
      },
      {
        'action_name': 'trinkwassernotbrunnen-betriebsbereit',
        'action_title': 'ausgewählten Datensätzen betriebsbereit (ja/nein) direkt zuweisen',
        'field': 'betriebsbereit',
        'type': 'boolean'
      }
    ]
    map_feature_tooltip_fields = ['nummer']
    map_filter_fields = {
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung',
      'eigentuemer': 'Eigentümer',
      'betreiber': 'Betreiber',
      'betriebsbereit': 'betriebsbereit?',
      'bohrtiefe': 'Bohrtiefe (in m)',
      'ausbautiefe': 'Ausbautiefe (in m)'
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
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  vereinsregister_id = PositiveSmallIntegerMinField(
    verbose_name='ID im Vereinsregister',
    min_value=1,
    blank=True,
    null=True
  )
  vereinsregister_datum = DateField(
    verbose_name='Datum des Eintrags im Vereinsregister',
    blank=True,
    null=True
  )
  schlagwoerter = ChoiceArrayField(
    CharField(
      verbose_name='Schlagwörter',
      max_length=255,
      choices=()
    ),
    verbose_name='Schlagwörter'
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"vereine_hro'
    verbose_name = 'Verein'
    verbose_name_plural = 'Vereine'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Vereine in der Hanse- und Universitätsstadt Rostock'
    choices_models_for_choices_fields = {
      'schlagwoerter': 'Schlagwoerter_Vereine'
    }
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'schlagwoerter': 'Schlagwörter'
    }

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
    null=True
  )
  bezeichnung = CharField(
    verbose_name='Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  berechtigungen = ChoiceArrayField(
    CharField(
      verbose_name=' verkaufte Berechtigung(en)',
      max_length=255,
      choices=()
    ),
    verbose_name=' verkaufte Berechtigung(en)',
    blank=True,
    null=True
  )
  barrierefrei = BooleanField(
    verbose_name=' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    verbose_name='Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    verbose_name='Telefon (Festnetz)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  telefon_mobil = CharField(
    verbose_name='Telefon (mobil)',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      RegexValidator(
        regex=rufnummer_regex,
        message=rufnummer_message
      )
    ]
  )
  email = CharField(
    verbose_name='E-Mail-Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )
  website = CharField(
    verbose_name='Website',
    max_length=255,
    blank=True,
    null=True,
    validators=[
      URLValidator(
        message=url_message
      )
    ]
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"verkaufstellen_angelberechtigungen_hro'
    verbose_name = 'Verkaufstelle für Angelberechtigungen'
    verbose_name_plural = 'Verkaufstellen für Angelberechtigungen'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'Verkaufstellen für Angelberechtigungen in der Hanse- und Universitätsstadt ' \
                  'Rostock'
    choices_models_for_choices_fields = {
      'berechtigungen': 'Angelberechtigungen'
    }
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'bezeichnung': 'Bezeichnung',
      'berechtigungen': 'verkaufte Berechtigung(en)'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_fields = ['bezeichnung']
    map_filter_fields = {
      'bezeichnung': 'Bezeichnung',
      'berechtigungen': 'verkaufte Berechtigung(en)'
    }

  def __str__(self):
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


BEMAS_ALTDATEN_VERURSACHER_TARGET_SECTOR_CHOICES = (
  ('Anlage an Wohnhaus', 'Anlage an Wohnhaus'),
  ('Anlage für gesundheitliche und soziale Zwecke',
   'Anlage für gesundheitliche und soziale Zwecke'),
  ('Baustelle/Einsatz von Geräten und Maschinen', 'Baustelle/Einsatz von Geräten und Maschinen'),
  ('Einzelhandel', 'Einzelhandel'),
  ('Elektromagnetische Strahlung', 'Elektromagnetische Strahlung'),
  ('Fahrzeug- und Maschinenbau', 'Fahrzeug- und Maschinenbau'),
  ('Forschung/Universität', 'Forschung/Universität'),
  ('Freizeitanlage', 'Freizeitanlage'),
  ('Gastgewerbe', 'Gastgewerbe'),
  ('Hafen/Umschlag/Liegeplatz', 'Hafen/Umschlag/Liegeplatz'),
  ('Handel, Vermietung und Reparatur von Fahrzeugen, Maschinen und Anlagen',
   'Handel, Vermietung und Reparatur von Fahrzeugen, Maschinen und Anlagen'),
  ('Kultureinrichtung', 'Kultureinrichtung'),
  ('landwirtschaftlicher Betrieb/Tierhaltung', 'landwirtschaftlicher Betrieb/Tierhaltung'),
  ('produzierendes und verarbeitendes Gewerbe', 'produzierendes und verarbeitendes Gewerbe'),
  ('Schienenverkehr', 'Schienenverkehr'),
  ('sonstige Anlage', 'sonstige Anlage'),
  ('sonstige Dienstleistung und sonstiges Gewerbe',
   'sonstige Dienstleistung und sonstiges Gewerbe'),
  ('sonstiger Verkehr', 'sonstiger Verkehr'),
  ('Speditionsbetrieb/Logistikunternehmen/Großhandel/Zusteller',
   'Speditionsbetrieb/Logistikunternehmen/Großhandel/Zusteller'),
  ('Sportanlage', 'Sportanlage'),
  ('Stellplatzanlage/Parkhaus', 'Stellplatzanlage/Parkhaus'),
  ('Straßenverkehr', 'Straßenverkehr'),
  ('Tankstelle/Ladestation', 'Tankstelle/Ladestation'),
  ('Veranstaltung im Freien', 'Veranstaltung im Freien'),
  ('Verbrennungsanlage', 'Verbrennungsanlage'),
  ('Ver- und Entsorgung', 'Ver- und Entsorgung')
)


class Bemas_Altdaten_Verursacher(Basemodel):
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
  id = PositiveIntegerField(
    verbose_name=' aus altem BEMAS: ID',
    default=0
  )
  bearbeitet = BooleanField(
    verbose_name=' bearbeitet?'
  )
  reason_sector = BooleanField(
    verbose_name='Mangel in altem BEMAS: Branche fehlte'
  )
  reason_emission_point = BooleanField(
    verbose_name='Mangel in altem BEMAS: Verortung fehlte'
  )
  target_sector = CharField(
    verbose_name=' für neues BEMAS: Branche',
    choices=BEMAS_ALTDATEN_VERURSACHER_TARGET_SECTOR_CHOICES
  )
  target_description = TextField(
    verbose_name=' für neues BEMAS: Beschreibung',
    validators=standard_validators
  )
  source_verursacher_strasse = CharField(
    verbose_name=' aus altem BEMAS: Verursacher Straße',
    blank=True,
    null=True
  )
  source_verursacher_plz = CharField(
    verbose_name=' aus altem BEMAS: Verursacher PLZ',
    blank=True,
    null=True
  )
  source_verursacher_ort = CharField(
    verbose_name=' aus altem BEMAS: Verursacher Ort',
    blank=True,
    null=True
  )
  source_betreiber_name = CharField(
    verbose_name=' aus altem BEMAS: Betreiber Name',
    blank=True,
    null=True
  )
  source_betreiber_strasse = CharField(
    verbose_name=' aus altem BEMAS: Betreiber Straße',
    blank=True,
    null=True
  )
  source_betreiber_plz = CharField(
    verbose_name=' aus altem BEMAS: Betreiber PLZ',
    blank=True,
    null=True
  )
  source_betreiber_ort = CharField(
    verbose_name=' aus altem BEMAS: Betreiber Ort',
    blank=True,
    null=True
  )
  target_operator_organization_id = PositiveIntegerField(
    verbose_name=' aus altem BEMAS: Betreiber Organisation',
    default=0,
    blank=True,
    null=True
  )
  target_operator_person_id = PositiveIntegerField(
    verbose_name=' aus altem BEMAS: Betreiber Person',
    default=0,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(Basemodel.Meta):
    db_table = 'fachdaten_adressbezug\".\"bemas_altdaten_verursacher'
    verbose_name = 'BEMAS-Altdaten: Verursacher'
    verbose_name_plural = 'BEMAS-Altdaten: Verursacher'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'BEMAS-Altdaten: Verursacher'
    readonly_fields = [
      'id', 'reason_sector', 'reason_emission_point', 'source_verursacher_strasse',
      'source_verursacher_plz', 'source_verursacher_ort', 'source_betreiber_name',
      'source_betreiber_strasse', 'source_betreiber_plz', 'source_betreiber_ort',
      'target_operator_organization_id', 'target_operator_person_id'
    ]
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'id': 'ID',
      'bearbeitet': 'bearbeitet?',
      'reason_sector': 'Branche fehlt(e)',
      'reason_emission_point': 'Verortung fehlt(e)',
      'adresse': 'Adresse',
      'target_sector': 'Branche',
      'target_description': 'Beschreibung'
    }
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_fields = ['id']

  def __str__(self):
    return str(self.id)


BEMAS_ALTDATEN_BESCHWERDEN_TARGET_STATUS_CHOICES = (
  ('in Bearbeitung', 'in Bearbeitung'),
  ('abgeschlossen', 'abgeschlossen'),
  ('nicht zuständig', 'nicht zuständig')
)


BEMAS_ALTDATEN_BESCHWERDEN_TARGET_TYPE_OF_IMMISSION_CHOICES = (
  ('Abgas/Rauch', 'Abgas/Rauch'),
  ('Elektromagnetische Strahlung', 'Elektromagnetische Strahlung'),
  ('Erschütterungen', 'Erschütterungen'),
  ('Geruch', 'Geruch'),
  ('Lärm', 'Lärm'),
  ('Licht', 'Licht'),
  ('Staub', 'Staub')
)


class Bemas_Altdaten_Beschwerden(Basemodel):
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
  id = PositiveIntegerField(
    verbose_name=' aus altem BEMAS: ID',
    default=0
  )
  bearbeitet = BooleanField(
    verbose_name=' bearbeitet?'
  )
  reason_date_of_receipt = BooleanField(
    verbose_name='Mangel in altem BEMAS: Eingangsdatum fehlte'
  )
  reason_type_of_immission = BooleanField(
    verbose_name='Mangel in altem BEMAS: Immissionsart fehlte'
  )
  reason_originator_id = BooleanField(
    verbose_name='Mangel in altem BEMAS: Verursacher ebenfalls mit Mängeln'
  )
  reason_immission_point = BooleanField(
    verbose_name='Mangel in altem BEMAS: Verortung fehlte'
  )
  target_date_of_receipt = DateField(
    verbose_name=' für neues BEMAS: Eingangsdatum'
  )
  target_status = CharField(
    verbose_name=' für neues BEMAS: Bearbeitungsstatus',
    choices=BEMAS_ALTDATEN_BESCHWERDEN_TARGET_STATUS_CHOICES
  )
  target_type_of_immission = CharField(
    verbose_name=' für neues BEMAS: Immissionsart',
    choices=BEMAS_ALTDATEN_BESCHWERDEN_TARGET_TYPE_OF_IMMISSION_CHOICES
  )
  target_originator_id = PositiveIntegerField(
    verbose_name=' aus altem BEMAS/für neues BEMAS: Verursacher'
  )
  target_description = TextField(
    verbose_name=' für neues BEMAS: Beschreibung',
    validators=standard_validators
  )
  source_beschwerdefuehrer_strasse = CharField(
    verbose_name=' aus altem BEMAS: Beschwerdeführer Straße',
    blank=True,
    null=True
  )
  source_beschwerdefuehrer_plz = CharField(
    verbose_name=' aus altem BEMAS: Beschwerdeführer PLZ',
    blank=True,
    null=True
  )
  source_beschwerdefuehrer_ort = CharField(
    verbose_name=' aus altem BEMAS: Beschwerdeführer Ort',
    blank=True,
    null=True
  )
  source_immissionsart = CharField(
    verbose_name=' aus altem BEMAS: Immissionsart',
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(Basemodel.Meta):
    db_table = 'fachdaten_adressbezug\".\"bemas_altdaten_beschwerden'
    verbose_name = 'BEMAS-Altdaten: Beschwerde'
    verbose_name_plural = 'BEMAS-Altdaten: Beschwerden'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'BEMAS-Altdaten: Beschwerden'
    readonly_fields = [
      'id', 'reason_date_of_receipt', 'reason_type_of_immission', 'reason_originator_id',
      'reason_immission_point', 'target_originator_id', 'source_beschwerdefuehrer_strasse',
      'source_beschwerdefuehrer_plz', 'source_beschwerdefuehrer_ort', 'source_immissionsart'
    ]
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    list_fields = {
      'id': 'ID',
      'bearbeitet': 'bearbeitet?',
      'reason_date_of_receipt': 'Eingangsdatum fehlt(e)',
      'reason_type_of_immission': 'Immissionsart fehlt(e)',
      'reason_originator_id': 'Verursacher ebenfalls mit Mängeln',
      'reason_immission_point': 'Verortung fehlt(e)',
      'adresse': 'Adresse',
      'target_date_of_receipt': 'Eingangsdatum',
      'target_status': 'Bearbeitungsstatus',
      'target_type_of_immission': 'Immissionsart',
      'target_originator_id': 'Verursacher',
      'target_description': 'Beschreibung'
    }
    list_fields_with_date = ['target_date_of_receipt']
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_fields = ['id']

  def __str__(self):
    return str(self.id)


BEMAS_ALTDATEN_JOURNALEREIGNISSE_TARGET_TYPE_OF_EVENT = (
  ('Besprechung', 'Besprechung'),
  ('Ortsbegehung', 'Ortsbegehung'),
  ('Prognose/Messung', 'Prognose/Messung'),
  ('Schriftverkehr', 'Schriftverkehr'),
  ('Telefonat', 'Telefonat')
)


class Bemas_Altdaten_Journalereignisse(Basemodel):
  id = PositiveIntegerField(
    verbose_name=' aus altem BEMAS: ID',
    default=0
  )
  bearbeitet = BooleanField(
    verbose_name=' bearbeitet?'
  )
  target_created_at = DateTimeField(
    verbose_name=' für neues BEMAS: Zeitstempel'
  )
  target_complaint_id = PositiveIntegerField(
    verbose_name=' aus altem BEMAS/für neues BEMAS: Beschwerde'
  )
  target_type_of_event = CharField(
    verbose_name=' für neues BEMAS: Ereignisart',
    choices=BEMAS_ALTDATEN_JOURNALEREIGNISSE_TARGET_TYPE_OF_EVENT
  )
  target_description = TextField(
    verbose_name=' für neues BEMAS: Beschreibung',
    validators=standard_validators
  )

  class Meta(Basemodel.Meta):
    db_table = 'fachdaten\".\"bemas_altdaten_journalereignisse'
    verbose_name = 'BEMAS-Altdaten: Journalereignis'
    verbose_name_plural = 'BEMAS-Altdaten: Journalereignisse'

  class BasemodelMeta(SimpleModel.BasemodelMeta):
    description = 'BEMAS-Altdaten: Journalereignisse'
    readonly_fields = ['id']
    list_fields = {
      'id': 'ID',
      'bearbeitet': 'bearbeitet?',
      'target_created_at': 'Zeitstempel',
      'target_complaint_id': 'Beschwerde',
      'target_type_of_event': 'Ereignisart',
      'target_description': 'Beschreibung'
    }
    list_fields_with_datetime = ['target_created_at']

  def __str__(self):
    return str(self.id)
