from datetime import date, datetime, timezone
from decimal import Decimal
from django.conf import settings
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator, \
  RegexValidator, URLValidator
from django.db.models import CASCADE, RESTRICT, SET_NULL, ForeignKey
from django.db.models.fields import BooleanField, CharField, DateField, DateTimeField, \
  DecimalField, PositiveIntegerField
from django.db.models.fields.files import FileField, ImageField
from django.db.models.signals import post_delete, post_save, pre_save
from re import sub
from zoneinfo import ZoneInfo

from .base import SimpleModel
from .constants_vars import personennamen_validators, standard_validators, \
  hausnummer_zusatz_regex, email_message, hausnummer_zusatz_message, inventarnummer_regex, \
  inventarnummer_message, rufnummer_regex, rufnummer_message, url_message, \
  denksteine_nummer_regex, denksteine_nummer_message, hausnummern_antragsnummer_message, \
  hausnummern_antragsnummer_regex, hydranten_bezeichnung_regex, hydranten_bezeichnung_message, \
  poller_nummer_regex, poller_nummer_message, postleitzahl_message, postleitzahl_regex, \
  strassen_schluessel_regex, strassen_schluessel_message, trinkwassernotbrunnen_nummer_regex, \
  trinkwassernotbrunnen_nummer_message
from .fields import ChoiceArrayField, NullTextField, PositiveSmallIntegerMinField, \
  PositiveSmallIntegerRangeField, point_field, line_field, multiline_field, polygon_field, \
  multipolygon_field
from .functions import current_year, delete_pdf, delete_photo, delete_photo_after_emptied, \
  get_pre_save_instance, path_and_rename, photo_post_processing, sequence_id
from .models_codelist import Adressen, Strassen, Inoffizielle_Strassen, Gemeindeteile, \
  Altersklassen_Kadaverfunde, Arten_Baudenkmale, Arten_FairTrade, Arten_Feldsportanlagen, \
  Arten_Feuerwachen, Arten_Fliessgewaesser, Arten_Hundetoiletten, \
  Arten_Fallwildsuchen_Kontrollen, Arten_Meldedienst_flaechenhaft, Arten_Meldedienst_punkthaft, \
  Arten_Parkmoeglichkeiten, Arten_Pflegeeinrichtungen, Arten_Poller, Arten_Toiletten, Arten_Wege, \
  Betriebsarten, Betriebszeiten, Bewirtschafter_Betreiber_Traeger_Eigentuemer, \
  Anbieter_Carsharing, Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO, Gebaeudebauweisen, \
  Gebaeudefunktionen, Geschlechter_Kadaverfunde, Haefen, Hersteller_Poller, Kategorien_Strassen, \
  Materialien_Denksteine, Ordnungen_Fliessgewaesser, Personentitel, Quartiere, \
  Raeumbreiten_Strassenreinigungssatzung_HRO, Reinigungsklassen_Strassenreinigungssatzung_HRO, \
  Reinigungsrhythmen_Strassenreinigungssatzung_HRO, Sportarten, \
  Status_Baudenkmale_Denkmalbereiche, Status_Poller, Tierseuchen, Typen_Abfallbehaelter, \
  Typen_Poller, Verbuende_Ladestationen_Elektrofahrzeuge, \
  Wegebreiten_Strassenreinigungssatzung_HRO, Wegereinigungsklassen_Strassenreinigungssatzung_HRO, \
  Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO, Wegetypen_Strassenreinigungssatzung_HRO, \
  Zustaende_Kadaverfunde, Zustaende_Schutzzaeune_Tierseuchen
from .storage import OverwriteStorage


class Abfallbehaelter(SimpleModel):
  """
  Abfallbehälter
  """

  deaktiviert = DateField(
    'Außerbetriebstellung',
    blank=True,
    null=True
  )
  id = CharField(
    'ID',
    max_length=8,
    unique=True,
    default='00000000'
  )
  typ = ForeignKey(
    Typen_Abfallbehaelter,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
    blank=True,
    null=True
  )
  aufstellungsjahr = PositiveSmallIntegerRangeField(
    'Aufstellungsjahr',
    max_value=current_year(),
    blank=True,
    null=True
  )
  eigentuemer = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer'
  )
  bewirtschafter = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter'
  )
  pflegeobjekt = CharField(
    'Pflegeobjekt',
    max_length=255,
    validators=standard_validators
  )
  inventarnummer = CharField(
    'Inventarnummer',
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
    'Anschaffungswert (in €)',
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
    'Lage an einer Haltestelle?',
    blank=True,
    null=True
  )
  sommer_mo = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen montags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_di = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen dienstags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_mi = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen mittwochs im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_do = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen donnerstags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_fr = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen freitags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_sa = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen samstags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  sommer_so = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen sonntags im Sommer',
    min_value=1,
    blank=True,
    null=True
  )
  winter_mo = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen montags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_di = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen dienstags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_mi = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen mittwochs im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_do = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen donnerstags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_fr = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen freitags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_sa = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen samstags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  winter_so = PositiveSmallIntegerRangeField(
    'Anzahl Leerungen sonntags im Winter',
    min_value=1,
    blank=True,
    null=True
  )
  bemerkungen = CharField(
    'Bemerkungen',
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


class Angelverbotsbereiche(SimpleModel):
  """
  Angelverbotsbereiche
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  beschreibung = NullTextField(
    'Beschreibung',
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


class Aufteilungsplaene_Wohnungseigentumsgesetz(SimpleModel):
  """
  Aufteilungspläne nach Wohnungseigentumsgesetz
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  aktenzeichen = CharField(
    'Aktenzeichen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  datum_abgeschlossenheitserklaerung = DateField(
    'Datum der Abgeschlossenheitserklärung',
    blank=True,
    null=True
  )
  bearbeiter = CharField(
    'Bearbeiter:in',
    max_length=255,
    validators=standard_validators
  )
  bemerkungen = CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  datum = DateField(
    'Datum',
    default=date.today
  )
  pdf = FileField(
    'PDF',
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
    description = 'Aufteilungspläne nach Wohnungseigentumsgesetz' \
                  'in der Hanse- und Universitätsstadt Rostock'
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
    return 'Abgeschlossenheitserklärung mit Datum ' + \
      datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + \
      (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


post_delete.connect(delete_pdf, sender=Aufteilungsplaene_Wohnungseigentumsgesetz)


class Baudenkmale(SimpleModel):
  """
  Baudenkmale
  """

  deaktiviert = DateField(
    ' gestrichen am',
    blank=True,
    null=True
  )
  id = PositiveIntegerField(
    'ID',
    default=sequence_id('fachdaten_adressbezug.baudenkmale_hro_id_seq')
  )
  status = ForeignKey(
    Status_Baudenkmale_Denkmalbereiche,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  art = ForeignKey(
    Arten_Baudenkmale,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  beschreibung = CharField(
    'Beschreibung',
    max_length=255,
    validators=standard_validators
  )
  landschaftsdenkmal = BooleanField(' Landschaftsdenkmal?')
  geometrie = multipolygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"baudenkmale_hro'
    verbose_name = 'Baudenkmal'
    verbose_name_plural = 'Baudenkmale'
    description = 'Baudenkmale der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'gestrichen am',
      'id': 'ID',
      'status': 'Status',
      'adresse': 'Adresse',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung',
      'landschaftsdenkmal': 'Landschaftsdenkmal?'
    }
    list_fields_with_date = ['deaktiviert']
    list_fields_with_number = ['id']
    list_fields_with_foreign_key = {
      'status': 'Status',
      'adresse': 'adresse',
      'art': 'art'
    }
    readonly_fields = ['deaktiviert', 'id']
    map_feature_tooltip_field = 'id'
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'gestrichen am',
      'id': 'ID',
      'status': 'Status',
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung',
      'landschaftsdenkmal': 'Landschaftsdenkmal?'
    }
    map_filter_fields_as_list = ['art', 'status']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'MultiPolygon'
    as_overlay = True

  def __str__(self):
    return self.beschreibung + \
      ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Art: ' + str(self.art) + ']'


class Behinderteneinrichtungen(SimpleModel):
  """
  Behinderteneinrichtungen
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  plaetze = PositiveSmallIntegerMinField(
    'Plätze',
    min_value=1,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + \
      ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ']'


class Beschluesse_Bau_Planungsausschuss(SimpleModel):
  """
  Beschlüsse des Bau- und Planungsausschusses
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  beschlussjahr = PositiveSmallIntegerRangeField(
    'Beschlussjahr',
    min_value=1990,
    max_value=current_year(),
    default=current_year()
  )
  vorhabenbezeichnung = CharField(
    'Bezeichnung des Vorhabens',
    max_length=255,
    validators=standard_validators
  )
  bearbeiter = CharField(
    'Bearbeiter:in',
    max_length=255,
    validators=standard_validators
  )
  pdf = FileField(
    'PDF',
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
    description = 'Beschlüsse des Bau- und Planungsausschusses der Bürgerschaft ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'adresse': 'Adresse',
      'beschlussjahr': 'Beschlussjahr',
      'vorhabenbezeichnung': 'Bezeichnung des Vorhabens',
      'bearbeiter': 'Bearbeiter:in',
      'pdf': 'PDF'
    }
    list_fields_with_number = ['beschlussjahr']
    list_fields_with_foreign_key = {
      'adresse': 'adresse'
    }
    map_feature_tooltip_field = 'vorhabenbezeichnung'
    map_filter_fields = {
      'beschlussjahr': 'Beschlussjahr',
      'vorhabenbezeichnung': 'Bezeichnung des Vorhabens'
    }
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'

  def __str__(self):
    return self.vorhabenbezeichnung + ' (Beschlussjahr ' + str(self.beschlussjahr) + ')' + \
           (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


post_delete.connect(delete_pdf, sender=Beschluesse_Bau_Planungsausschuss)


class Bildungstraeger(SimpleModel):
  """
  Bildungsträger
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  betreiber = CharField(
    'Betreiber:in',
    max_length=255,
    validators=standard_validators
  )
  schlagwoerter = ChoiceArrayField(
    CharField(
      'Schlagwörter',
      max_length=255,
      choices=()
    ),
    verbose_name='Schlagwörter'
  )
  barrierefrei = BooleanField(
    ' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Carsharing_Stationen(SimpleModel):
  """
  Carsharing-Stationen
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  anbieter = ForeignKey(
    Anbieter_Carsharing,
    verbose_name='Anbieter',
    on_delete=RESTRICT,
    db_column='anbieter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_anbieter'
  )
  anzahl_fahrzeuge = PositiveSmallIntegerMinField(
    'Anzahl der Fahrzeuge',
    min_value=1,
    blank=True,
    null=True
  )
  bemerkungen = NullTextField(
    'Bemerkungen',
    max_length=500,
    blank=True,
    null=True,
    validators=standard_validators
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + \
      ' [' + ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Anbieter: ' + str(self.anbieter) + ']'


class Containerstellplaetze(SimpleModel):
  """
  Containerstellplätze
  """

  deaktiviert = DateField(
    'Außerbetriebstellung',
    blank=True,
    null=True
  )
  id = CharField(
    'ID',
    max_length=5,
    unique=True,
    default='00-00'
  )
  privat = BooleanField(' privat?')
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  bewirtschafter_grundundboden = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Grund und Boden',
    on_delete=SET_NULL,
    db_column='bewirtschafter_grundundboden',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_grundundboden',
    blank=True,
    null=True
  )
  bewirtschafter_glas = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Glas',
    on_delete=SET_NULL,
    db_column='bewirtschafter_glas',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_glas',
    blank=True,
    null=True
  )
  anzahl_glas = PositiveSmallIntegerMinField(
    'Anzahl Glas normal',
    min_value=1,
    blank=True,
    null=True
  )
  anzahl_glas_unterflur = PositiveSmallIntegerMinField(
    'Anzahl Glas unterflur',
    min_value=1,
    blank=True,
    null=True
  )
  bewirtschafter_papier = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Papier',
    on_delete=SET_NULL,
    db_column='bewirtschafter_papier',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_papier',
    blank=True,
    null=True
  )
  anzahl_papier = PositiveSmallIntegerMinField(
    'Anzahl Papier normal',
    min_value=1,
    blank=True,
    null=True
  )
  anzahl_papier_unterflur = PositiveSmallIntegerMinField(
    'Anzahl Papier unterflur',
    min_value=1,
    blank=True,
    null=True
  )
  bewirtschafter_altkleider = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter Altkleider',
    on_delete=SET_NULL,
    db_column='bewirtschafter_altkleider',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter_altkleider',
    blank=True,
    null=True
  )
  anzahl_altkleider = PositiveSmallIntegerMinField(
    'Anzahl Altkleider',
    min_value=1,
    blank=True,
    null=True
  )
  inbetriebnahmejahr = PositiveSmallIntegerRangeField(
    'Inbetriebnahmejahr',
    max_value=current_year(),
    blank=True,
    null=True
  )
  inventarnummer = CharField(
    'Inventarnummer Stellplatz',
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
    'Inventarnummer Grund und Boden',
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
    'Inventarnummer Zaun',
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
    'Anschaffungswert (in €)',
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
    ' öffentliche Widmung?',
    blank=True,
    null=True
  )
  bga = BooleanField(
    'Zuordnung BgA Stellplatz?',
    blank=True,
    null=True
  )
  bga_grundundboden = BooleanField(
    'Zuordnung BgA Grund und Boden?',
    blank=True,
    null=True
  )
  bga_zaun = BooleanField(
    'Zuordnung BgA Zaun?',
    blank=True,
    null=True
  )
  art_eigentumserwerb = CharField(
    'Art des Eigentumserwerbs Stellplatz',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  art_eigentumserwerb_zaun = CharField(
    'Art des Eigentumserwerbs Zaun',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  vertraege = CharField(
    'Verträge',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  winterdienst_a = BooleanField(
    'Winterdienst A?',
    blank=True,
    null=True
  )
  winterdienst_b = BooleanField(
    'Winterdienst B?',
    blank=True,
    null=True
  )
  winterdienst_c = BooleanField(
    'Winterdienst C?',
    blank=True,
    null=True
  )
  flaeche = DecimalField(
    'Fläche (in m²)',
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
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  foto = ImageField(
    'Foto',
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
    readonly_fields = ['deaktiviert', 'id']
    map_feature_tooltip_field = 'id'
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


pre_save.connect(get_pre_save_instance, sender=Containerstellplaetze)

post_save.connect(photo_post_processing, sender=Containerstellplaetze)

post_save.connect(delete_photo_after_emptied, sender=Containerstellplaetze)

post_delete.connect(delete_photo, sender=Containerstellplaetze)


class Denkmalbereiche(SimpleModel):
  """
  Denkmalbereiche
  """

  deaktiviert = DateField(
    ' gestrichen am',
    blank=True,
    null=True
  )
  id = PositiveIntegerField(
    'ID',
    default=sequence_id('fachdaten.denkmalbereiche_hro_id_seq')
  )
  status = ForeignKey(
    Status_Baudenkmale_Denkmalbereiche,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  beschreibung = CharField(
    'Beschreibung',
    max_length=255,
    validators=standard_validators
  )
  geometrie = multipolygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"denkmalbereiche_hro'
    verbose_name = 'Denkmalbereich'
    verbose_name_plural = 'Denkmalbereiche'
    description = 'Denkmalbereiche der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'gestrichen am',
      'id': 'ID',
      'status': 'Status',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung'
    }
    list_fields_with_date = ['deaktiviert']
    list_fields_with_number = ['id']
    list_fields_with_foreign_key = {
      'status': 'Status'
    }
    readonly_fields = ['deaktiviert', 'id']
    map_feature_tooltip_field = 'id'
    map_filter_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'gestrichen am',
      'id': 'ID',
      'status': 'Status',
      'bezeichnung': 'Bezeichnung',
      'beschreibung': 'Beschreibung'
    }
    map_filter_fields_as_list = ['status']
    geometry_type = 'MultiPolygon'
    as_overlay = True

  def __str__(self):
    return self.bezeichnung + ' [Beschreibung: ' + str(self.beschreibung) + ']'


class Denksteine(SimpleModel):
  """
  Denksteine
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  nummer = CharField(
    'Nummer',
    max_length=255,
    validators=[
      RegexValidator(
        regex=denksteine_nummer_regex,
        message=denksteine_nummer_message
      )
    ]
  )
  titel = ForeignKey(
    Personentitel,
    verbose_name='Titel',
    on_delete=SET_NULL,
    db_column='titel',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_titel',
    blank=True,
    null=True
  )
  vorname = CharField(
    'Vorname',
    max_length=255,
    validators=personennamen_validators
  )
  nachname = CharField(
    'Nachname',
    max_length=255,
    validators=personennamen_validators
  )
  geburtsjahr = PositiveSmallIntegerRangeField(
    'Geburtsjahr',
    min_value=1850,
    max_value=1945
  )
  sterbejahr = PositiveSmallIntegerRangeField(
    'Sterbejahr',
    min_value=1933,
    max_value=1945,
    blank=True,
    null=True
  )
  text_auf_dem_stein = CharField(
    'Text auf dem Stein',
    max_length=255,
    validators=standard_validators
  )
  ehemalige_adresse = CharField(
    ' ehemalige Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  material = ForeignKey(
    Materialien_Denksteine,
    verbose_name='Material',
    on_delete=RESTRICT,
    db_column='material',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_materialien'
  )
  erstes_verlegejahr = PositiveSmallIntegerRangeField(
    ' erstes Verlegejahr',
    min_value=2002,
    max_value=current_year()
  )
  website = CharField(
    'Website',
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
    return (str(self.titel) + ' ' if self.titel else '') + \
      self.vorname + ' ' + self.nachname + ' (* ' + str(self.geburtsjahr) + \
      (', † ' + str(self.sterbejahr) if self.sterbejahr else '') + ')' + \
      (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class FairTrade(SimpleModel):
  """
  Fair Trade
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  art = ForeignKey(
    Arten_FairTrade,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  betreiber = CharField(
    'Betreiber:in',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  barrierefrei = BooleanField(
    ' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Art: ' + str(self.art) + ']'


class Feldsportanlagen(SimpleModel):
  """
  Feldsportanlagen
  """

  art = ForeignKey(
    Arten_Feldsportanlagen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  foto = ImageField(
    'Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC + 'feldsportanlagen'
    ),
    max_length=255,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
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


pre_save.connect(get_pre_save_instance, sender=Feldsportanlagen)

post_save.connect(photo_post_processing, sender=Feldsportanlagen)

post_save.connect(delete_photo_after_emptied, sender=Feldsportanlagen)

post_delete.connect(delete_photo, sender=Feldsportanlagen)


class Feuerwachen(SimpleModel):
  """
  Feuerwachen
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  art = ForeignKey(
    Arten_Feuerwachen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Art: ' + str(self.art) + ']'


class Fliessgewaesser(SimpleModel):
  """
  Fließgewässer
  """

  nummer = CharField(
    'Nummer',
    max_length=255,
    validators=standard_validators
  )
  art = ForeignKey(
    Arten_Fliessgewaesser,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  ordnung = ForeignKey(
    Ordnungen_Fliessgewaesser,
    verbose_name='Ordnung',
    on_delete=SET_NULL,
    db_column='ordnung',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_ordnungen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  nennweite = PositiveSmallIntegerMinField(
    'Nennweite (in mm)',
    min_value=100,
    blank=True,
    null=True
  )
  laenge = PositiveIntegerField(
    'Länge (in m)',
    default=0
  )
  laenge_in_hro = PositiveIntegerField(
    'Länge innerhalb Rostocks (in m)',
    blank=True,
    null=True
  )
  geometrie = line_field

  class Meta(SimpleModel.Meta):
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
    return self.nummer + ' [Art: ' + str(self.art) + \
      (', Ordnung: ' + str(self.ordnung) if self.ordnung else '') + ']'


class Geh_Radwegereinigung(SimpleModel):
  """
  Geh- und Radwegereinigung
  """

  id = CharField(
    'ID',
    max_length=14,
    default='0000000000-000'
  )
  gemeindeteil = ForeignKey(
    Gemeindeteile,
    verbose_name='Gemeindeteil',
    on_delete=RESTRICT,
    db_column='gemeindeteil',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gemeindeteile',
    default='00000000-0000-0000-0000-000000000000'
  )
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
  inoffizielle_strasse = ForeignKey(
    Inoffizielle_Strassen,
    verbose_name=' inoffizielle Straße',
    on_delete=SET_NULL,
    db_column='inoffizielle_strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_inoffizielle_strassen',
    blank=True,
    null=True
  )
  nummer = CharField(
    'Nummer',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  beschreibung = CharField(
    'Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  wegeart = ForeignKey(
    Arten_Wege,
    verbose_name='Wegeart',
    on_delete=CASCADE,
    db_column='wegeart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_wegearten'
  )
  wegetyp = ForeignKey(
    Wegetypen_Strassenreinigungssatzung_HRO,
    verbose_name='Wegetyp',
    on_delete=CASCADE,
    db_column='wegetyp',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_wegetypen',
    blank=True,
    null=True
  )
  reinigungsklasse = ForeignKey(
    Wegereinigungsklassen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsklasse',
    on_delete=SET_NULL,
    db_column='reinigungsklasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_reinigungsklassen',
    blank=True,
    null=True
  )
  reinigungsrhythmus = ForeignKey(
    Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsrhythmus',
    on_delete=SET_NULL,
    db_column='reinigungsrhythmus',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_reinigungsrhythmen',
    blank=True,
    null=True
  )
  laenge = DecimalField(
    'Länge (in m)',
    max_digits=6,
    decimal_places=2,
    default=0
  )
  breite = ForeignKey(
    Wegebreiten_Strassenreinigungssatzung_HRO,
    verbose_name='Breite (in m)',
    on_delete=CASCADE,
    db_column='breite',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_breiten',
    blank=True,
    null=True
  )
  reinigungsflaeche = DecimalField(
    'Reinigungsfläche (in m²)',
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
    'Winterdienst?',
    blank=True,
    null=True
  )
  raeumbreite = ForeignKey(
    Raeumbreiten_Strassenreinigungssatzung_HRO,
    verbose_name='Räumbreite im Winterdienst (in m)',
    on_delete=CASCADE,
    db_column='raeumbreite',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_raeumbreiten',
    blank=True,
    null=True
  )
  winterdienstflaeche = DecimalField(
    'Winterdienstfläche (in m²)',
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

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug\".\"geh_und_radwegereinigung_hro'
    verbose_name = 'Geh- und Radwegereinigung'
    verbose_name_plural = 'Geh- und Radwegereinigung'
    description = 'Geh- und Radwegereinigung der Hanse- und Universitätsstadt Rostock'
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
    list_fields_with_number = ['id', 'laenge', 'breite']
    readonly_fields = ['id', 'gemeindeteil', 'laenge']
    map_feature_tooltip_field = 'id'
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
      'winterdienst': 'Winterdienst?',
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


class Geraetespielanlagen(SimpleModel):
  """
  Gerätespielanlagen
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  beschreibung = CharField(
    'Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  foto = ImageField(
    'Foto',
    storage=OverwriteStorage(),
    upload_to=path_and_rename(
      settings.PHOTO_PATH_PREFIX_PUBLIC + 'geraetespielanlagen'
    ),
    max_length=255,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
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


pre_save.connect(get_pre_save_instance, sender=Geraetespielanlagen)

post_save.connect(photo_post_processing, sender=Geraetespielanlagen)

post_save.connect(delete_photo_after_emptied, sender=Geraetespielanlagen)

post_delete.connect(delete_photo, sender=Geraetespielanlagen)


class Gutachterfotos(SimpleModel):
  """
  Gutachterfotos
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bearbeiter = CharField(
    'Bearbeiter:in',
    max_length=255,
    validators=standard_validators
  )
  bemerkungen = CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  datum = DateField(
    'Datum',
    default=date.today
  )
  aufnahmedatum = DateField(
    'Aufnahmedatum',
    default=date.today
  )
  foto = ImageField(
    'Foto',
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
    description = 'Gutachterfotos der Hanse- und Universitätsstadt Rostock'
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
    Strassen,
    verbose_name='Straße',
    on_delete=SET_NULL,
    db_column='strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_strassen',
    blank=True,
    null=True
  )
  deaktiviert = DateField(
    'Datum der Löschung',
    blank=True,
    null=True
  )
  loeschung_details = CharField(
    'Details zur Löschung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  vorherige_adresse = CharField(
    ' vorherige Adresse',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  vorherige_antragsnummer = CharField(
    ' vorherige Antragsnummer',
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
    'Hausnummer',
    min_value=1,
    max_value=999
  )
  hausnummer_zusatz = CharField(
    'Hausnummernzusatz',
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
    'Postleitzahl',
    max_length=5,
    validators=[
      RegexValidator(
        regex=postleitzahl_regex,
        message=postleitzahl_message
      )
    ]
  )
  vergabe_datum = DateField(
    'Datum der Vergabe',
    default=date.today
  )
  antragsnummer = CharField(
    'Antragsnummer',
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
    Gebaeudebauweisen,
    verbose_name='Bauweise des Gebäudes',
    on_delete=SET_NULL,
    db_column='gebaeude_bauweise',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gebaeude_bauweisen',
    blank=True,
    null=True
  )
  gebaeude_funktion = ForeignKey(
    Gebaeudefunktionen,
    verbose_name='Funktion des Gebäudes',
    on_delete=SET_NULL,
    db_column='gebaeude_funktion',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gebaeude_funktionen',
    blank=True,
    null=True
  )
  hinweise_gebaeude = CharField(
    ' weitere Hinweise zum Gebäude',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  bearbeiter = CharField(
    'Bearbeiter:in',
    max_length=255,
    validators=standard_validators
  )
  bemerkungen = CharField(
    'Bemerkungen',
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
    description = 'Hausnummern der Hanse- und Universitätsstadt Rostock'
    catalog_link_fields = {
      'gebaeude_bauweise': 'https://geo.sv.rostock.de/alkis-ok/31001/baw/',
      'gebaeude_funktion': 'https://geo.sv.rostock.de/alkis-ok/31001/gfk/'
    }
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
    map_filter_fields_as_list = ['strasse', 'gebaeude_bauweise', 'gebaeude_funktion']
    address_type = 'Straße'
    address_mandatory = True
    geometry_type = 'Point'
    postcode_assigner = 'postleitzahl'
    heavy_load_limit = 800

  def __str__(self):
    return str(self.strasse) + ' ' + str(self.hausnummer) + \
      (self.hausnummer_zusatz if self.hausnummer_zusatz else '') + \
      ' [Postleitzahl: ' + self.postleitzahl + ']'


class Hospize(SimpleModel):
  """
  Hospize
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  plaetze = PositiveSmallIntegerMinField(
    'Plätze',
    min_value=1,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ']'


class Hundetoiletten(SimpleModel):
  """
  Hundetoiletten
  """

  deaktiviert = DateField(
    'Außerbetriebstellung',
    blank=True,
    null=True
  )
  id = CharField(
    'ID',
    max_length=8,
    unique=True,
    default='00000000'
  )
  art = ForeignKey(
    Arten_Hundetoiletten,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  aufstellungsjahr = PositiveSmallIntegerRangeField(
    'Aufstellungsjahr',
    max_value=current_year(),
    blank=True,
    null=True
  )
  bewirtschafter = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter'
  )
  pflegeobjekt = CharField(
    'Pflegeobjekt',
    max_length=255,
    validators=standard_validators
  )
  inventarnummer = CharField(
    'Inventarnummer',
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
    'Anschaffungswert (in €)',
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
    'Bemerkungen',
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


class Hydranten(SimpleModel):
  """
  Hydranten
  """

  bezeichnung = CharField(
    'Bezeichnung',
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
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=RESTRICT,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer'
  )
  bewirtschafter = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Bewirtschafter',
    on_delete=RESTRICT,
    db_column='bewirtschafter',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_bewirtschafter'
  )
  feuerloeschgeeignet = BooleanField(' feuerlöschgeeignet?')
  betriebszeit = ForeignKey(
    Betriebszeiten,
    verbose_name='Betriebszeit',
    on_delete=RESTRICT,
    db_column='betriebszeit',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betriebszeiten'
  )
  entnahme = CharField(
    'Entnahme',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  hauptwasserzaehler = CharField(
    'Hauptwasserzähler',
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
    map_filter_fields_as_list = ['eigentuemer', 'bewirtschafter', 'betriebszeit']
    geometry_type = 'Point'
    as_overlay = True

  def __str__(self):
    return self.bezeichnung


class Kadaverfunde(SimpleModel):
  """
  Kadaverfunde
  """

  zeitpunkt = DateTimeField('Zeitpunkt')
  tierseuche = ForeignKey(
    Tierseuchen,
    verbose_name='Tierseuche',
    on_delete=RESTRICT,
    db_column='tierseuche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tierseuchen'
  )
  geschlecht = ForeignKey(
    Geschlechter_Kadaverfunde,
    verbose_name='Geschlecht',
    on_delete=RESTRICT,
    db_column='geschlecht',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_geschlechter'
  )
  altersklasse = ForeignKey(
    Altersklassen_Kadaverfunde,
    verbose_name='Altersklasse',
    on_delete=RESTRICT,
    db_column='altersklasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_altersklassen'
  )
  gewicht = PositiveSmallIntegerRangeField(
    ' geschätztes Gewicht (in kg)',
    min_value=1,
    blank=True,
    null=True
  )
  zustand = ForeignKey(
    Zustaende_Kadaverfunde,
    verbose_name='Zustand',
    on_delete=RESTRICT,
    db_column='zustand',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende'
  )
  art_auffinden = ForeignKey(
    Arten_Fallwildsuchen_Kontrollen,
    verbose_name='Art des Auffindens',
    on_delete=RESTRICT,
    db_column='art_auffinden',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten_auffinden'
  )
  witterung = CharField(
    'Witterung vor Ort',
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
  geometrie = point_field

  class Meta(SimpleModel.Meta):
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
    zeitpunkt_str = sub(r'([+-][0-9]{2}):', '\\1', str(self.zeitpunkt))
    zeitpunkt = datetime.strptime(
      zeitpunkt_str,
      '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=timezone.utc).astimezone(local_tz)
    zeitpunkt_str = zeitpunkt.strftime('%d.%m.%Y, %H:%M:%S Uhr')
    return str(self.tierseuche) + ' mit Zeitpunkt ' + zeitpunkt_str + ', '


class Kindertagespflegeeinrichtungen(SimpleModel):
  """
  Kindertagespflegeeinrichtungen
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  vorname = CharField(
    'Vorname',
    max_length=255,
    validators=personennamen_validators
  )
  nachname = CharField(
    'Nachname',
    max_length=255,
    validators=personennamen_validators
  )
  plaetze = PositiveSmallIntegerMinField(
    'Plätze',
    min_value=1,
    blank=True,
    null=True
  )
  zeiten = CharField(
    'Betreuungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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


class Kinder_Jugendbetreuung(SimpleModel):
  """
  Kinder- und Jugendbetreuung
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') \
      + 'Träger: ' + str(self.traeger) + ']'


class Kunst_im_oeffentlichen_Raum(SimpleModel):
  """
  Kunst im öffentlichen Raum
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  ausfuehrung = CharField(
    'Ausführung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  schoepfer = CharField(
    'Schöpfer',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  entstehungsjahr = PositiveSmallIntegerRangeField(
    'Entstehungsjahr',
    max_value=current_year(),
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
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


class Ladestationen_Elektrofahrzeuge(SimpleModel):
  """
  Ladestationen für Elektrofahrzeuge
  """

  adresse = ForeignKey(
    Adressen,
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
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  betreiber = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=SET_NULL,
    db_column='betreiber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betreiber',
    blank=True,
    null=True
  )
  verbund = ForeignKey(
    Verbuende_Ladestationen_Elektrofahrzeuge,
    verbose_name='Verbund',
    on_delete=SET_NULL,
    db_column='verbund',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_verbuende',
    blank=True,
    null=True
  )
  betriebsart = ForeignKey(
    Betriebsarten,
    verbose_name='Betriebsart',
    on_delete=RESTRICT,
    db_column='betriebsart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betriebsarten'
  )
  anzahl_ladepunkte = PositiveSmallIntegerMinField(
    'Anzahl an Ladepunkten',
    min_value=1,
    blank=True,
    null=True
  )
  arten_ladepunkte = CharField(
    'Arten der Ladepunkte',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  ladekarten = ChoiceArrayField(
    CharField(
      'Ladekarten',
      max_length=255,
      choices=()
    ),
    verbose_name='Ladekarten',
    blank=True,
    null=True
  )
  kosten = CharField(
    'Kosten',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  zeiten = CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  website = CharField(
    'Website',
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
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Meldedienst_flaechenhaft(SimpleModel):
  """
  Meldedienst (flächenhaft)
  """

  art = ForeignKey(
    Arten_Meldedienst_flaechenhaft,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bearbeiter = CharField(
    'Bearbeiter:in',
    max_length=255,
    validators=standard_validators
  )
  bemerkungen = CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  datum = DateField(
    'Datum',
    default=date.today
  )
  geometrie = polygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"meldedienst_flaechenhaft_hro'
    verbose_name = 'Meldedienst (flächenhaft)'
    verbose_name_plural = 'Meldedienst (flächenhaft)'
    description = 'Meldedienst (flächenhaft) der Hanse- und Universitätsstadt Rostock'
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
    map_feature_tooltip_field = 'art'
    map_filter_fields = {
      'art': 'Art',
      'bearbeiter': 'Bearbeiter:in',
      'datum': 'Datum'
    }
    map_filter_fields_as_list = ['art']
    geometry_type = 'Polygon'

  def __str__(self):
    return str(self.art) + \
      ' [Datum: ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + ']'


class Meldedienst_punkthaft(SimpleModel):
  """
  Meldedienst (punkthaft)
  """

  deaktiviert = DateField(
    'Zurückstellung',
    blank=True,
    null=True
  )
  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  art = ForeignKey(
    Arten_Meldedienst_punkthaft,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bearbeiter = CharField(
    'Bearbeiter:in',
    max_length=255,
    validators=standard_validators
  )
  bemerkungen = CharField(
    'Bemerkungen',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  datum = DateField(
    'Datum',
    default=date.today
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_adressbezug\".\"meldedienst_punkthaft_hro'
    verbose_name = 'Meldedienst (punkthaft)'
    verbose_name_plural = 'Meldedienst (punkthaft)'
    description = 'Meldedienst (punkthaft) der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'deaktiviert': 'Zurückstellung',
      'adresse': 'Adresse',
      'art': 'Art',
      'bearbeiter': 'Bearbeiter:in',
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
      'bearbeiter': 'Bearbeiter:in',
      'datum': 'Datum'
    }
    map_filter_fields_as_list = ['art']
    address_type = 'Adresse'
    address_mandatory = False
    geometry_type = 'Point'
    as_overlay = True
    heavy_load_limit = 600

  def __str__(self):
    return str(self.art) + \
      ' [Datum: ' + datetime.strptime(str(self.datum), '%Y-%m-%d').strftime('%d.%m.%Y') + \
      (', Adresse: ' + str(self.adresse) if self.adresse else '') + ']'


class Mobilpunkte(SimpleModel):
  """
  Mobilpunkte
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  angebote = ChoiceArrayField(
    CharField(
      'Angebote',
      max_length=255,
      choices=()
    ),
    verbose_name='Angebote'
  )
  website = CharField(
    'Website',
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


class Parkmoeglichkeiten(SimpleModel):
  """
  Parkmöglichkeiten
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  art = ForeignKey(
    Arten_Parkmoeglichkeiten,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  standort = CharField(
    'Standort',
    max_length=255,
    validators=standard_validators
  )
  betreiber = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=SET_NULL,
    db_column='betreiber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betreiber',
    blank=True,
    null=True
  )
  stellplaetze_pkw = PositiveSmallIntegerMinField(
    'Pkw-Stellplätze',
    min_value=1,
    blank=True,
    null=True
  )
  stellplaetze_wohnmobil = PositiveSmallIntegerMinField(
    'Wohnmobilstellplätze',
    min_value=1,
    blank=True,
    null=True
  )
  stellplaetze_bus = PositiveSmallIntegerMinField(
    'Busstellplätze',
    min_value=1,
    blank=True,
    null=True
  )
  gebuehren_halbe_stunde = DecimalField(
    'Gebühren pro ½ h (in €)',
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
    'Gebühren pro 1 h (in €)',
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
    'Gebühren pro 2 h (in €)',
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
    'Gebühren ganztags (in €)',
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
    'Bemerkungen',
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


class Pflegeeinrichtungen(SimpleModel):
  """
  Pflegeeinrichtungen
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  art = ForeignKey(
    Arten_Pflegeeinrichtungen,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  betreiber = CharField(
    'Betreiber:in',
    max_length=255,
    validators=standard_validators
  )
  plaetze = PositiveSmallIntegerMinField(
    'Plätze',
    min_value=1,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    description = 'Pflegeeinrichtungen in der Hanse- und Universitätsstadt Rostock'
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
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'art': 'Art',
      'bezeichnung': 'Bezeichnung',
      'betreiber': 'Betreiber:in'
    }
    map_filter_fields_as_list = ['art']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'

  def __str__(self):
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Art: ' + str(self.art) + ']'


class Poller(SimpleModel):
  """
  Poller
  """

  art = ForeignKey(
    Arten_Poller,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  nummer = CharField(
    'Nummer',
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
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  status = ForeignKey(
    Status_Poller,
    verbose_name='Status',
    on_delete=RESTRICT,
    db_column='status',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_status'
  )
  zeiten = CharField(
    'Lieferzeiten',
    max_length=255,
    blank=True,
    null=True
  )
  hersteller = ForeignKey(
    Hersteller_Poller,
    verbose_name='Hersteller',
    on_delete=SET_NULL,
    db_column='hersteller',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_hersteller',
    blank=True,
    null=True
  )
  typ = ForeignKey(
    Typen_Poller,
    verbose_name='Typ',
    on_delete=SET_NULL,
    db_column='typ',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_typen',
    blank=True,
    null=True
  )
  anzahl = PositiveSmallIntegerMinField(
    'Anzahl',
    min_value=1
  )
  schliessungen = ChoiceArrayField(
    CharField(
      'Schließungen',
      max_length=255,
      choices=()
    ),
    verbose_name='Schließungen',
    blank=True,
    null=True
  )
  bemerkungen = CharField(
    'Bemerkungen',
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


class Reinigungsreviere(SimpleModel):
  """
  Reinigungsreviere
  """

  gemeindeteil = ForeignKey(
    Gemeindeteile,
    verbose_name='Gemeindeteil',
    on_delete=SET_NULL,
    db_column='gemeindeteil',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gemeindeteile',
    blank=True,
    null=True
  )
  nummer = PositiveSmallIntegerMinField(
    'Nummer',
    min_value=1,
    unique=True,
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  geometrie = multipolygon_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_gemeindeteilbezug\".\"reinigungsreviere_hro'
    verbose_name = 'Reinigungsreviere'
    verbose_name_plural = 'Reinigungsreviere'
    description = 'Reinigungsreviere der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'gemeindeteil': 'Gemeindeteil',
      'nummer': 'Nummer',
      'bezeichnung': 'Bezeichnung'
    }
    list_fields_with_foreign_key = {
      'gemeindeteil': 'gemeindeteil'
    }
    list_fields_with_number = ['nummer']
    map_feature_tooltip_field = 'bezeichnung'
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
    address_type = 'Gemeindeteil'
    address_mandatory = False
    geometry_type = 'MultiPolygon'
    as_overlay = True

  def __str__(self):
    return self.bezeichnung + (' (Nummer: ' + str(self.nummer) + ')' if self.nummer else '')


class Rettungswachen(SimpleModel):
  """
  Rettungswachen
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ']'


class Schiffsliegeplaetze(SimpleModel):
  """
  Schiffsliegeplätze
  """

  hafen = ForeignKey(
    Haefen,
    verbose_name='Hafen',
    on_delete=CASCADE,
    db_column='hafen',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_haefen'
  )
  liegeplatznummer = CharField(
    'Liegeplatz',
    max_length=255,
    validators=standard_validators
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  liegeplatzlaenge = DecimalField(
    'Liegeplatzlänge (in m)',
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
    ' zulässiger Tiefgang (in m)',
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
    ' zulässige Schiffslänge (in m)',
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
    'Kaihöhe (in m)',
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
    'Pollerzug',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  poller_von = CharField(
    'Poller (von)',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  poller_bis = CharField(
    'Poller (bis)',
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
      'zulaessiger_tiefgang': 'zulässiger Tiefgang (in m)'
    }
    map_filter_fields_as_list = ['hafen']
    geometry_type = 'Polygon'
    as_overlay = True

  def __str__(self):
    return self.liegeplatznummer + ', ' + self.bezeichnung + ' [Hafen: ' + str(self.hafen) + ']'


class Schutzzaeune_Tierseuchen(SimpleModel):
  """
  Schutzzäune gegen Tierseuchen
  """

  tierseuche = ForeignKey(
    Tierseuchen,
    verbose_name='Tierseuche',
    on_delete=RESTRICT,
    db_column='tierseuche',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_tierseuchen'
  )
  zustand = ForeignKey(
    Zustaende_Schutzzaeune_Tierseuchen,
    verbose_name='Zustand',
    on_delete=RESTRICT,
    db_column='zustand',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_zustaende'
  )
  laenge = PositiveIntegerField(
    'Länge (in m)',
    default=0
  )
  geometrie = multiline_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"schutzzaeune_tierseuchen_hro'
    verbose_name = 'Schutzzaun gegen eine Tierseuche'
    verbose_name_plural = 'Schutzzäune gegen Tierseuchen'
    description = 'Schutzzäune gegen Tierseuchen in der Hanse- und Universitätsstadt Rostock'
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
    list_fields_with_number = ['laenge']
    readonly_fields = ['laenge']
    map_feature_tooltip_field = 'zustand'
    map_filter_fields = {
      'tierseuche': 'Tierseuche',
      'zustand': 'Zustand'
    }
    map_filter_fields_as_list = ['tierseuche', 'zustand']
    geometry_type = 'MultiLineString'
    as_overlay = True

  def __str__(self):
    return str(self.tierseuche) + ', ' + str(self.zustand)


class Sporthallen(SimpleModel):
  """
  Sporthallen
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  sportart = ForeignKey(
    Sportarten,
    verbose_name='Sportart',
    on_delete=RESTRICT,
    db_column='sportart',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_sportarten'
  )
  barrierefrei = BooleanField(
    ' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  foto = ImageField(
    'Foto',
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
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ', Sportart: ' + str(self.sportart) + ']'


pre_save.connect(get_pre_save_instance, sender=Sporthallen)

post_save.connect(photo_post_processing, sender=Sporthallen)

post_save.connect(delete_photo_after_emptied, sender=Sporthallen)

post_delete.connect(delete_photo, sender=Sporthallen)


class Stadtteil_Begegnungszentren(SimpleModel):
  """
  Stadtteil- und Begegnungszentren
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  traeger = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Träger',
    on_delete=RESTRICT,
    db_column='traeger',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_traeger'
  )
  barrierefrei = BooleanField(
    ' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + ' [' + \
      ('Adresse: ' + str(self.adresse) + ', ' if self.adresse else '') + \
      'Träger: ' + str(self.traeger) + ']'


class Standortqualitaeten_Geschaeftslagen_Sanierungsgebiet(SimpleModel):
  """
  Standortqualitäten von Geschäftslagen im Sanierungsgebiet
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bewertungsjahr = PositiveSmallIntegerRangeField(
    'Bewertungsjahr',
    min_value=1990,
    max_value=current_year(),
    default=current_year()
  )
  quartier = ForeignKey(
    Quartiere,
    verbose_name='Quartier',
    on_delete=RESTRICT,
    db_column='quartier',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_quartiere'
  )
  kundschaftskontakte_anfangswert = DecimalField(
    'Kundschaftskontakte (Anfangswert)',
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
    'Kundschaftskontakte (Endwert)',
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
    'Verkehrsanbindung (Anfangswert)',
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
    'Verkehrsanbindung (Endwert)',
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
    'Ausstattung (Anfangswert)',
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
    'Ausstattung (Endwert)',
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
    'Beeinträchtigung (Anfangswert)',
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
    'Beeinträchtigung (Endwert)',
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
    'Standortnutzung (Anfangswert)',
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
    'Standortnutzung (Endwert)',
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
    description = 'Standortqualitäten von Geschäftslagen ' \
                  'im Sanierungsgebiet der Hanse- und Universitätsstadt Rostock'
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
    list_fields_with_number = [
      'bewertungsjahr',
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
    map_feature_tooltip_field = 'adresse'
    map_filter_fields = {
      'adresse': 'Adresse',
      'bewertungsjahr': 'Bewertungsjahr',
      'quartier': 'Quartier'
    }
    map_filter_fields_as_list = ['quartier']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'

  def __str__(self):
    return str(self.adresse)


class Standortqualitaeten_Wohnlagen_Sanierungsgebiet(SimpleModel):
  """
  Standortqualitäten von Wohnlagen im Sanierungsgebiet
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bewertungsjahr = PositiveSmallIntegerRangeField(
    'Bewertungsjahr',
    min_value=1990,
    max_value=current_year(),
    default=current_year()
  )
  quartier = ForeignKey(
    Quartiere,
    verbose_name='Quartier',
    on_delete=RESTRICT,
    db_column='quartier',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_quartiere'
  )
  gesellschaftslage_anfangswert = DecimalField(
    'Gesellschaftslage (Anfangswert)',
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
    'Gesellschaftslage (Endwert)',
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
    'Verkehrsanbindung (Anfangswert)',
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
    'Verkehrsanbindung (Endwert)',
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
    'Ausstattung (Anfangswert)',
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
    'Ausstattung (Endwert)',
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
    'Beeinträchtigung (Anfangswert)',
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
    'Beeinträchtigung (Endwert)',
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
    'Standortnutzung (Anfangswert)',
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
    'Standortnutzung (Endwert)',
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
    description = 'Standortqualitäten von Wohnlagen ' \
                  'im Sanierungsgebiet der Hanse- und Universitätsstadt Rostock'
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
    list_fields_with_number = [
      'bewertungsjahr',
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
    map_feature_tooltip_field = 'adresse'
    map_filter_fields = {
      'adresse': 'Adresse',
      'bewertungsjahr': 'Bewertungsjahr',
      'quartier': 'Quartier'
    }
    map_filter_fields_as_list = ['quartier']
    address_type = 'Adresse'
    address_mandatory = True
    geometry_type = 'Point'

  def __str__(self):
    return str(self.adresse)


class Strassen_Simple(SimpleModel):
  """
  Straßen
  """

  kategorie = ForeignKey(
    Kategorien_Strassen,
    verbose_name='Kategorie',
    on_delete=RESTRICT,
    db_column='kategorie',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_kategorien'
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  schluessel = CharField(
    'Schlüssel',
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

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten\".\"strassen_hro'
    verbose_name = 'Straße'
    verbose_name_plural = 'Straßen'
    description = 'Straßen in der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'aktiv': 'aktiv?',
      'kategorie': 'Kategorie',
      'bezeichnung': 'Bezeichnung',
      'schluessel': 'Schlüssel'
    }
    list_fields_with_foreign_key = {
      'kategorie': 'code'
    }
    map_feature_tooltip_field = 'bezeichnung'
    map_filter_fields = {
      'kategorie': 'Kategorie',
      'bezeichnung': 'Bezeichnung',
      'schluessel': 'Schlüssel'
    }
    map_filter_fields_as_list = ['kategorie']
    additional_wms_layers = [
      {
        'title': 'Eigentum HRO',
        'url': '/eigentum_hro/wms',
        'layers': 'hro.eigentum_hro.eigentum_hro_hro',
        'proxy': True
      }, {
        'title': 'Bewirtschaftungskataster',
        'url': 'https://geo.sv.rostock.de/geodienste/bewirtschaftungskataster/wms',
        'layers': 'hro.bewirtschaftungskataster.bewirtschaftungskataster'
      }, {
        'title': 'Grundvermögen: Flächen in Abstimmung',
        'url': '/grundvermoegen/wms',
        'layers': 'hro.grundvermoegen.flaechen_in_abstimmung',
        'proxy': True
      }, {
        'title': 'Grundvermögen: Realnutzungsarten',
        'url': '/grundvermoegen/wms',
        'layers': 'hro.grundvermoegen.realnutzungsarten',
        'proxy': True
      }, {
        'title': 'Liegenschaftsverwaltung: An- und Verkauf',
        'url': '/liegenschaftsverwaltung/wms',
        'layers': 'hro.liegenschaftsverwaltung.anundverkauf',
        'proxy': True
      }, {
        'title': 'Liegenschaftsverwaltung: Mieten und Pachten',
        'url': '/liegenschaftsverwaltung/wms',
        'layers': 'hro.liegenschaftsverwaltung.mieten_pachten',
        'proxy': True
      }, {
        'title': 'Flurstücke',
        'url': 'https://geo.sv.rostock.de/geodienste/flurstuecke_hro/wms',
        'layers': 'hro.flurstuecke.flurstuecke'
      }, {
        'title': 'Straßenwidmungen',
        'url': '/strassenwidmungen/wms',
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
        'url': '/eigentum_hro/wfs',
        'featuretypes': 'hro.eigentum_hro.eigentum_hro_hro',
        'proxy': True
      }, {
        'name': 'flurstuecke',
        'title': 'Flurstücke',
        'url': '/flurstuecke_hro/wfs',
        'featuretypes': 'hro.flurstuecke.flurstuecke',
        'proxy': True
      }
    ]
    geometry_type = 'MultiLineString'
    as_overlay = True
    heavy_load_limit = 600
    forms_in_mobile_mode = True

  def __str__(self):
    return self.bezeichnung + ' (' + self.schluessel + ')'


class Strassenreinigung(SimpleModel):
  """
  Straßenreinigung
  """

  id = CharField(
    'ID',
    max_length=14,
    default='0000000000-000'
  )
  gemeindeteil = ForeignKey(
    Gemeindeteile,
    verbose_name='Gemeindeteil',
    on_delete=RESTRICT,
    db_column='gemeindeteil',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_gemeindeteile',
    default='00000000-0000-0000-0000-000000000000'
  )
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
  inoffizielle_strasse = ForeignKey(
    Inoffizielle_Strassen,
    verbose_name=' inoffizielle Straße',
    on_delete=SET_NULL,
    db_column='inoffizielle_strasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_inoffizielle_strassen',
    blank=True,
    null=True
  )
  beschreibung = CharField(
    'Beschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  ausserhalb = BooleanField(' außerhalb geschlossener Ortslage?')
  reinigungsklasse = ForeignKey(
    Reinigungsklassen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsklasse',
    on_delete=SET_NULL,
    db_column='reinigungsklasse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_reinigungsklassen',
    blank=True,
    null=True
  )
  reinigungsrhythmus = ForeignKey(
    Reinigungsrhythmen_Strassenreinigungssatzung_HRO,
    verbose_name='Reinigungsrhythmus',
    on_delete=SET_NULL,
    db_column='reinigungsrhythmus',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_reinigungsrhythmen',
    blank=True,
    null=True
  )
  fahrbahnwinterdienst = ForeignKey(
    Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO,
    verbose_name='Fahrbahnwinterdienst',
    on_delete=SET_NULL,
    db_column='fahrbahnwinterdienst',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_fahrbahnwinterdienste',
    blank=True,
    null=True
  )
  laenge = DecimalField(
    'Länge (in m)',
    max_digits=6,
    decimal_places=2,
    default=0
  )
  geometrie = multiline_field

  class Meta(SimpleModel.Meta):
    db_table = 'fachdaten_strassenbezug\".\"strassenreinigung_hro'
    verbose_name = 'Straßenreinigung'
    verbose_name_plural = 'Straßenreinigung'
    description = 'Straßenreinigung der Hanse- und Universitätsstadt Rostock'
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
    list_fields_with_foreign_key = {
      'gemeindeteil': 'gemeindeteil',
      'strasse': 'strasse',
      'inoffizielle_strasse': 'strasse',
      'reinigungsklasse': 'code',
      'reinigungsrhythmus': 'reinigungsrhythmus',
      'fahrbahnwinterdienst': 'code'
    }
    list_fields_with_number = ['id', 'laenge']
    readonly_fields = ['id', 'gemeindeteil', 'laenge']
    map_feature_tooltip_field = 'id'
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
    address_type = 'Straße'
    address_mandatory = False
    geometry_type = 'MultiLineString'
    as_overlay = True

  def __str__(self):
    return str(self.id) + (', ' + str(self.beschreibung) if self.beschreibung else '') + \
      (', außerhalb geschlossener Ortslage' if self.ausserhalb else '') + \
      (', Reinigungsklasse ' + str(self.reinigungsklasse) if self.reinigungsklasse else '') + \
      (', Fahrbahnwinterdienst ' +
       str(self.fahrbahnwinterdienst) if self.fahrbahnwinterdienst else '') + \
      (' [Straße: ' + str(self.strasse) + ']' if self.strasse else '') + \
      (' [inoffizielle Straße: ' +
       str(self.inoffizielle_strasse) + ']' if self.inoffizielle_strasse else '')


class Thalasso_Kurwege(SimpleModel):
  """
  Thalasso-Kurwege
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  streckenbeschreibung = CharField(
    'Streckenbeschreibung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  barrierefrei = BooleanField(
    ' barrierefrei?',
    default=False
  )
  farbe = CharField(
    'Farbe',
    max_length=7
  )
  beschriftung = CharField(
    'Beschriftung',
    max_length=255,
    blank=True,
    null=True,
    validators=standard_validators
  )
  laenge = PositiveIntegerField(
    'Länge (in m)',
    default=0
  )
  geometrie = line_field

  class Meta(SimpleModel.Meta):
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
      'barrierefrei': 'barrierefrei?'
    }
    geometry_type = 'LineString'

  def __str__(self):
    return self.bezeichnung


class Toiletten(SimpleModel):
  """
  Toiletten
  """

  art = ForeignKey(
    Arten_Toiletten,
    verbose_name='Art',
    on_delete=RESTRICT,
    db_column='art',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_arten'
  )
  bewirtschafter = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
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
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  geometrie = point_field

  class Meta(SimpleModel.Meta):
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
    return str(self.art) + \
      (' [Bewirtschafter: ' + str(self.bewirtschafter) + ']' if self.bewirtschafter else '') + \
      (' mit Öffnungszeiten ' + self.zeiten + ']' if self.zeiten else '')


class Trinkwassernotbrunnen(SimpleModel):
  """
  Trinkwassernotbrunnen
  """

  nummer = CharField(
    'Nummer',
    max_length=12,
    validators=[
      RegexValidator(
        regex=trinkwassernotbrunnen_nummer_regex,
        message=trinkwassernotbrunnen_nummer_message
      )
    ]
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  eigentuemer = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Eigentümer',
    on_delete=SET_NULL,
    db_column='eigentuemer',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_eigentuemer',
    blank=True,
    null=True
  )
  betreiber = ForeignKey(
    Bewirtschafter_Betreiber_Traeger_Eigentuemer,
    verbose_name='Betreiber',
    on_delete=RESTRICT,
    db_column='betreiber',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_betreiber'
  )
  betriebsbereit = BooleanField(' betriebsbereit?')
  bohrtiefe = DecimalField(
    'Bohrtiefe (in m)',
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
    'Ausbautiefe (in m)',
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
      'betriebsbereit': 'betriebsbereit?',
      'bohrtiefe': 'Bohrtiefe (in m)',
      'ausbautiefe': 'Ausbautiefe (in m)'
    }
    map_filter_fields_as_list = ['eigentuemer', 'betreiber']
    geometry_type = 'Point'

  def __str__(self):
    return self.nummer


class Vereine(SimpleModel):
  """
  Vereine
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  vereinsregister_id = PositiveSmallIntegerMinField(
    'ID im Vereinsregister',
    min_value=1,
    blank=True,
    null=True
  )
  vereinsregister_datum = DateField(
    'Datum des Eintrags im Vereinsregister',
    blank=True,
    null=True
  )
  schlagwoerter = ChoiceArrayField(
    CharField(
      'Schlagwörter',
      max_length=255,
      choices=()
    ),
    verbose_name='Schlagwörter'
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')


class Verkaufstellen_Angelberechtigungen(SimpleModel):
  """
  Verkaufstellen für Angelberechtigungen
  """

  adresse = ForeignKey(
    Adressen,
    verbose_name='Adresse',
    on_delete=SET_NULL,
    db_column='adresse',
    to_field='uuid',
    related_name='%(app_label)s_%(class)s_adressen',
    blank=True,
    null=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  berechtigungen = ChoiceArrayField(
    CharField(
      ' verkaufte Berechtigung(en)',
      max_length=255,
      choices=()
    ),
    verbose_name=' verkaufte Berechtigung(en)',
    blank=True,
    null=True
  )
  barrierefrei = BooleanField(
    ' barrierefrei?',
    blank=True,
    null=True
  )
  zeiten = CharField(
    'Öffnungszeiten',
    max_length=255,
    blank=True,
    null=True
  )
  telefon_festnetz = CharField(
    'Telefon (Festnetz)',
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
    'Telefon (mobil)',
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
    'E-Mail-Adresse',
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
    'Website',
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
    return self.bezeichnung + (' [Adresse: ' + str(self.adresse) + ']' if self.adresse else '')
