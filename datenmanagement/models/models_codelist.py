from decimal import Decimal
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator, \
  RegexValidator
from django.db.models.fields import CharField, DecimalField

from toolbox.constants_vars import personennamen_validators, standard_validators, email_message
from .base import Metamodel, Codelist, Art, Befestigungsart, Material, Schlagwort, Status, Typ
from .constants_vars import fahrbahnwinterdienst_code_regex, fahrbahnwinterdienst_code_message, \
  haefen_abkuerzung_regex, haefen_abkuerzung_message, linien_linie_regex, linien_linie_message, \
  parkscheinautomaten_zone_regex, parkscheinautomaten_zone_message, quartiere_code_regex, \
  quartiere_code_message
from .fields import PositiveSmallIntegerMinField, PositiveSmallIntegerRangeField, \
  multipolygon_field


#
# meta models
# (not visible for ordinary users unless given explicit rights)
#

class Adressen(Metamodel):
  """
  Adressen
  """

  adresse = CharField(
    'Adresse',
    max_length=255,
    editable=False
  )

  class Meta(Metamodel.Meta):
    db_table = 'basisdaten\".\"adressenliste_datenwerft'
    ordering = ['adresse']
    verbose_name = 'Adresse'
    verbose_name_plural = 'Adressen'

  class BasemodelMeta(Metamodel.BasemodelMeta):
    description = 'Adressen in Mecklenburg-Vorpommern'
    list_fields = {
      'adresse': 'Adresse'
    }

  def __str__(self):
    return self.adresse


class Strassen(Metamodel):
  """
  Straßen
  """

  strasse = CharField(
    'Straße',
    max_length=255,
    editable=False
  )

  class Meta(Metamodel.Meta):
    db_table = 'basisdaten\".\"strassenliste_datenwerft'
    ordering = ['strasse']
    verbose_name = 'Straße'
    verbose_name_plural = 'Straßen'

  class BasemodelMeta(Metamodel.BasemodelMeta):
    description = 'Straßen in Mecklenburg-Vorpommern'
    list_fields = {
      'strasse': 'Straße'
    }

  def __str__(self):
    return self.strasse


class Inoffizielle_Strassen(Metamodel):
  """
  inoffizielle Straßen
  """

  strasse = CharField(
    'Straße',
    max_length=255,
    editable=False
  )

  class Meta(Metamodel.Meta):
    db_table = 'basisdaten\".\"inoffizielle_strassenliste_datenwerft_hro'
    ordering = ['strasse']
    verbose_name = 'Inoffizielle Straße der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Inoffizielle Straßen der Hanse- und Universitätsstadt Rostock'

  class BasemodelMeta(Metamodel.BasemodelMeta):
    description = 'Inoffizielle Straßen der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'strasse': 'Straße'
    }

  def __str__(self):
    return self.strasse


class Gemeindeteile(Metamodel):
  """
  Gemeindeteile
  """

  gemeindeteil = CharField(
    'Gemeindeteil',
    max_length=255,
    editable=False
  )
  geometrie = multipolygon_field

  class Meta(Metamodel.Meta):
    db_table = 'basisdaten\".\"gemeindeteile_datenwerft_hro'
    ordering = ['gemeindeteil']
    verbose_name = 'Gemeindeteil'
    verbose_name_plural = 'Gemeindeteile'

  class BasemodelMeta(Metamodel.BasemodelMeta):
    description = 'Gemeindeteile in Mecklenburg-Vorpommern'
    as_overlay = True
    list_fields = {
      'gemeindeteil': 'Gemeindeteil'
    }

  def __str__(self):
    return self.gemeindeteil


#
# codelists
# (not visible for ordinary users unless given explicit rights)
#

class Altersklassen_Kadaverfunde(Codelist):
  """
  Altersklassen bei Kadaverfunden
  """

  ordinalzahl = PositiveSmallIntegerRangeField(
    'Ordinalzahl',
    min_value=1
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"altersklassen_kadaverfunde'
    ordering = ['ordinalzahl']
    verbose_name = 'Altersklasse bei einem Kadaverfund'
    verbose_name_plural = 'Altersklassen bei Kadaverfunden'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Altersklassen bei Kadaverfunden'
    naming = 'bezeichnung'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'bezeichnung': 'Bezeichnung'
    }

  def __str__(self):
    return self.bezeichnung


class Angebote_Mobilpunkte(Codelist):
  """
  Angebote bei Mobilpunkten
  """

  angebot = CharField(
    'Angebot',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"angebote_mobilpunkte'
    ordering = ['angebot']
    verbose_name = 'Angebot bei einem Mobilpunkt'
    verbose_name_plural = 'Angebote bei Mobilpunkten'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Angebote bei Mobilpunkten'
    list_fields = {
      'angebot': 'Angebot'
    }

  def __str__(self):
    return self.angebot


class Angelberechtigungen(Codelist):
  """
  Angelberechtigungen
  """

  angelberechtigung = CharField(
    'Angelberechtigung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"angelberechtigungen'
    ordering = ['angelberechtigung']
    verbose_name = 'Angelberechtigung'
    verbose_name_plural = 'Angelberechtigungen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Angelberechtigungen'
    list_fields = {
      'angelberechtigung': 'Angelberechtigung'
    }

  def __str__(self):
    return self.angelberechtigung


class Ansprechpartner_Baustellen(Codelist):
  """
  Ansprechpartner:innen bei Baustellen
  """

  vorname = CharField(
    'Vorname',
    max_length=255,
    blank=True,
    null=True,
    validators=personennamen_validators
  )
  nachname = CharField(
    'Nachname',
    max_length=255,
    blank=True,
    null=True,
    validators=personennamen_validators
  )
  email = CharField(
    'E-Mail-Adresse',
    max_length=255,
    unique=True,
    validators=[
      EmailValidator(
        message=email_message
      )
    ]
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"ansprechpartner_baustellen'
    ordering = [
      'nachname',
      'vorname',
      'email'
    ]
    verbose_name = 'Ansprechpartner:in bei einer Baustelle'
    verbose_name_plural = 'Ansprechpartner:innen bei Baustellen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Ansprechpartner:innen bei Baustellen'
    list_fields = {
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'email': 'E-Mail-Adresse'
    }

  def __str__(self):
    if not self.nachname:
      return self.email
    else:
      return self.vorname + ' ' + self.nachname + ' (' + self.email + ')'


class Arten_Adressunsicherheiten(Art):
  """
  Arten von Adressunsicherheiten
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_adressunsicherheiten'
    verbose_name = 'Art einer Adressunsicherheit'
    verbose_name_plural = 'Arten von Adressunsicherheiten'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Adressunsicherheiten'


class Arten_Durchlaesse(Art):
  """
  Arten von Durchlässen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_durchlaesse'
    verbose_name = 'Art eines Durchlasses'
    verbose_name_plural = 'Arten von Durchlässen'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Durchlässen'


class Arten_Fahrradabstellanlagen(Art):
  """
  Arten von Fahrradabstellanlagen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fahrradabstellanlagen'
    verbose_name = 'Art einer Fahrradabstellanlage'
    verbose_name_plural = 'Arten von Fahrradabstellanlagen'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Fahrradabstellanlagen'


class Arten_Erdwaermesonden(Art):
  """
  Arten von Erdwärmesonden
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_erdwaermesonden'
    verbose_name = 'Art einer Erdwärmesonde'
    verbose_name_plural = 'Arten von Erdwärmesonden'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Erdwärmesonden'


class Arten_FairTrade(Art):
  """
  Arten von Fair-Trade-Einrichtungen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fairtrade'
    verbose_name = 'Art einer Fair-Trade-Einrichtung'
    verbose_name_plural = 'Arten von Fair-Trade-Einrichtungen'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Fair-Trade-Einrichtungen'


class Arten_Feldsportanlagen(Art):
  """
  Arten von Feldsportanlagen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_feldsportanlagen'
    verbose_name = 'Art einer Feldsportanlage'
    verbose_name_plural = 'Arten von Feldsportanlagen'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Feldsportanlagen'


class Arten_Feuerwachen(Art):
  """
  Arten von Feuerwachen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_feuerwachen'
    verbose_name = 'Art einer Feuerwache'
    verbose_name_plural = 'Arten von Feuerwachen'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Feuerwachen'


class Arten_Fliessgewaesser(Art):
  """
  Arten von Fließgewässern
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fliessgewaesser'
    verbose_name = 'Art eines Fließgewässers'
    verbose_name_plural = 'Arten von Fließgewässern'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Fließgewässern'


class Arten_Hundetoiletten(Art):
  """
  Arten von Hundetoiletten
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_hundetoiletten'
    verbose_name = 'Art einer Hundetoilette'
    verbose_name_plural = 'Arten von Hundetoiletten'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Hundetoiletten'


class Arten_Fallwildsuchen_Kontrollen(Art):
  """
  Arten von Kontrollen im Rahmen von Fallwildsuchen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fallwildsuchen_kontrollen'
    verbose_name = 'Art einer Kontrolle im Rahmen einer Fallwildsuche'
    verbose_name_plural = 'Arten von Kontrollen im Rahmen von Fallwildsuchen'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Kontrollen im Rahmen von Fallwildsuchen'


class Arten_Meldedienst_flaechenhaft(Art):
  """
  Arten von Meldediensten (flächenhaft)
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_meldedienst_flaechenhaft'
    verbose_name = 'Art eines Meldedienstes (flächenhaft)'
    verbose_name_plural = 'Arten von Meldediensten (flächenhaft)'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Meldediensten (flächenhaft)'


class Arten_Meldedienst_punkthaft(Art):
  """
  Arten von Meldediensten (punkthaft)
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_meldedienst_punkthaft'
    verbose_name = 'Art eines Meldedienstes (punkthaft)'
    verbose_name_plural = 'Arten von Meldediensten (punkthaft)'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Meldediensten (punkthaft)'


class Arten_Parkmoeglichkeiten(Art):
  """
  Arten von Parkmöglichkeiten
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_parkmoeglichkeiten'
    verbose_name = 'Art einer Parkmöglichkeit'
    verbose_name_plural = 'Arten von Parkmöglichkeiten'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Parkmöglichkeiten'


class Arten_Pflegeeinrichtungen(Art):
  """
  Arten von Pflegeeinrichtungen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_pflegeeinrichtungen'
    verbose_name = 'Art einer Pflegeeinrichtung'
    verbose_name_plural = 'Arten von Pflegeeinrichtungen'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Pflegeeinrichtungen'


class Arten_Poller(Art):
  """
  Arten von Pollern
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_poller'
    verbose_name = 'Art eines Pollers'
    verbose_name_plural = 'Arten von Pollern'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Pollern'


class Arten_Toiletten(Art):
  """
  Arten von Toiletten
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_toiletten'
    verbose_name = 'Art einer Toilette'
    verbose_name_plural = 'Arten von Toiletten'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Toiletten'


class Arten_UVP_Vorpruefungen(Art):
  """
  Arten von UVP-Vorprüfungen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_uvp_vorpruefungen'
    verbose_name = 'Art einer UVP-Vorprüfung'
    verbose_name_plural = 'Arten von UVP-Vorprüfungen'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von UVP-Vorprüfungen'


class Arten_Wege(Art):
  """
  Arten von Wegen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_wege'
    verbose_name = 'Art eines Weges'
    verbose_name_plural = 'Arten von Wegen'

  class BasemodelMeta(Art.BasemodelMeta):
    description = 'Arten von Wegen'


class Auftraggeber_Baustellen(Codelist):
  """
  Auftraggeber von Baustellen
  """

  auftraggeber = CharField(
    'Auftraggeber',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"auftraggeber_baustellen'
    ordering = ['auftraggeber']
    verbose_name = 'Auftraggeber einer Baustelle'
    verbose_name_plural = 'Auftraggeber von Baustellen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Auftraggeber von Baustellen'
    list_fields = {
      'auftraggeber': 'Auftraggeber'
    }

  def __str__(self):
    return self.auftraggeber


class Ausfuehrungen_Haltestellenkataster(Codelist):
  """
  Ausführungen innerhalb eines Haltestellenkatasters
  """

  ausfuehrung = CharField(
    'Ausführung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"ausfuehrungen_haltestellenkataster'
    ordering = ['ausfuehrung']
    verbose_name = 'Ausführung innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Ausführungen innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Ausführungen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'ausfuehrung': 'Ausführung'
    }

  def __str__(self):
    return self.ausfuehrung


class Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster(Befestigungsart):
  """
  Befestigungsarten der Aufstellfläche Bus innerhalb eines Haltestellenkatasters
  """

  class Meta(Befestigungsart.Meta):
    db_table = 'codelisten\".\"befestigungsarten_aufstellflaeche_bus_haltestellenkataster'
    verbose_name = 'Befestigungsart der Aufstellfläche Bus innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Befestigungsarten der Aufstellfläche Bus ' \
                          'innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Befestigungsart.BasemodelMeta):
    description = 'Befestigungsarten der Aufstellfläche Bus innerhalb eines Haltestellenkatasters'


class Befestigungsarten_Warteflaeche_Haltestellenkataster(Befestigungsart):
  """
  Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters
  """

  class Meta(Befestigungsart.Meta):
    db_table = 'codelisten\".\"befestigungsarten_warteflaeche_haltestellenkataster'
    verbose_name = 'Befestigungsart der Wartefläche innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Befestigungsart.BasemodelMeta):
    description = 'Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters'


class Betriebsarten(Codelist):
  """
  Betriebsarten
  """

  betriebsart = CharField(
    'Betriebsart',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"betriebsarten'
    ordering = ['betriebsart']
    verbose_name = 'Betriebsart'
    verbose_name_plural = 'Betriebsarten'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Betriebsarten'
    list_fields = {
      'betriebsart': 'Betriebsart'
    }

  def __str__(self):
    return self.betriebsart


class Betriebszeiten(Codelist):
  """
  Betriebszeiten
  """

  betriebszeit = CharField(
    'Betriebszeit',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"betriebszeiten'
    ordering = ['betriebszeit']
    verbose_name = 'Betriebszeit'
    verbose_name_plural = 'Betriebszeiten'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Betriebszeiten'
    list_fields = {
      'betriebszeit': 'Betriebszeit'
    }

  def __str__(self):
    return self.betriebszeit


class Bewirtschafter_Betreiber_Traeger_Eigentuemer(Codelist):
  """
  Bewirtschafter, Betreiber, Träger, Eigentümer etc.
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  art = CharField(
    'Art',
    max_length=255,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"bewirtschafter_betreiber_traeger_eigentuemer'
    ordering = ['bezeichnung']
    verbose_name = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    verbose_name_plural = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'art': 'Art'
    }

  def __str__(self):
    return self.bezeichnung


class Anbieter_Carsharing(Codelist):
  """
  Carsharing-Anbieter
  """

  anbieter = CharField(
    'Anbieter',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"anbieter_carsharing'
    ordering = ['anbieter']
    verbose_name = 'Carsharing-Anbieter'
    verbose_name_plural = 'Carsharing-Anbieter'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Carsharing-Anbieter'
    list_fields = {
      'anbieter': 'Anbieter'
    }

  def __str__(self):
    return self.anbieter


class E_Anschluesse_Parkscheinautomaten(Codelist):
  """
  E-Anschlüsse für Parkscheinautomaten
  """

  e_anschluss = CharField(
    'E-Anschluss',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"e_anschluesse_parkscheinautomaten'
    ordering = ['e_anschluss']
    verbose_name = 'E-Anschluss für einen Parkscheinautomaten'
    verbose_name_plural = 'E-Anschlüsse für Parkscheinautomaten'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'E-Anschlüsse für Parkscheinautomaten'
    list_fields = {
      'e_anschluss': 'E-Anschluss'
    }

  def __str__(self):
    return self.e_anschluss


class Ergebnisse_UVP_Vorpruefungen(Codelist):
  """
  Ergebnisse von UVP-Vorprüfungen
  """

  ergebnis = CharField(
    'Ergebnis',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"ergebnisse_uvp_vorpruefungen'
    ordering = ['ergebnis']
    verbose_name = 'Ergebnis einer UVP-Vorprüfung'
    verbose_name_plural = 'Ergebnisse von UVP-Vorprüfungen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Ergebnisse von UVP-Vorprüfungen'
    list_fields = {
      'ergebnis': 'Ergebnis'
    }

  def __str__(self):
    return self.ergebnis


class Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO(Codelist):
  """
  Fahrbahnwinterdienst gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  code = CharField(
    'Code',
    max_length=1,
    unique=True,
    validators=[
      RegexValidator(
        regex=fahrbahnwinterdienst_code_regex,
        message=fahrbahnwinterdienst_code_message
      )
    ]
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"fahrbahnwinterdienst_strassenreinigungssatzung_hro'
    ordering = ['code']
    verbose_name = 'Fahrbahnwinterdienst gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Fahrbahnwinterdienst gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Fahrbahnwinterdienst gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'code': 'Code'
    }

  def __str__(self):
    return self.code


class Fotomotive_Haltestellenkataster(Codelist):
  """
  Fotomotive innerhalb eines Haltestellenkatasters
  """

  fotomotiv = CharField(
    'Fotomotiv',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"fotomotive_haltestellenkataster'
    ordering = ['fotomotiv']
    verbose_name = 'Fotomotiv innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Fotomotive innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Fotomotive innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fotomotiv': 'Fotomotiv'
    }

  def __str__(self):
    return self.fotomotiv


class Fundamenttypen_RSAG(Codelist):
  """
  Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG
  """

  typ = CharField(
    'Typ',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  erlaeuterung = CharField(
    'Erläuterung',
    max_length=255,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"fundamenttypen_rsag'
    ordering = ['typ']
    verbose_name = 'Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur ' \
                   'der Rostocker Straßenbahn AG'
    verbose_name_plural = 'Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur ' \
                          'der Rostocker Straßenbahn AG'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG'
    list_fields = {
      'typ': 'Typ',
      'erlaeuterung': 'Erläuterung'
    }

  def __str__(self):
    return self.typ


class Gebaeudearten_Meldedienst_punkthaft(Codelist):
  """
  Gebäudearten für den Meldedienst (punkthaft)
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"gebaeudearten_meldedienst_punkthaft'
    ordering = ['bezeichnung']
    verbose_name = 'Gebäudeart für den Meldedienst (punkthaft)'
    verbose_name_plural = 'Gebäudearten für den Meldedienst (punkthaft)'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Gebäudearten für den Meldedienst (punkthaft)'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }

  def __str__(self):
    return self.bezeichnung


class Gebaeudebauweisen(Codelist):
  """
  Gebäudebauweisen
  """

  code = PositiveSmallIntegerRangeField(
    'Code',
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

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"gebaeudebauweisen'
    ordering = ['bezeichnung']
    verbose_name = 'Gebäudebauweise'
    verbose_name_plural = 'Gebäudebauweisen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Gebäudebauweisen'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'code': 'Code'
    }
    list_fields_with_number = ['code']

  def __str__(self):
    return self.bezeichnung


class Gebaeudefunktionen(Codelist):
  """
  Gebäudefunktionen
  """

  code = PositiveSmallIntegerRangeField(
    'Code',
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

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"gebaeudefunktionen'
    ordering = ['bezeichnung']
    verbose_name = 'Gebäudefunktion'
    verbose_name_plural = 'Gebäudefunktionen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Gebäudefunktionen'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'code': 'Code'
    }
    list_fields_with_number = ['code']

  def __str__(self):
    return self.bezeichnung


class Genehmigungsbehoerden_UVP_Vorhaben(Codelist):
  """
  Genehmigungsbehörden von UVP-Vorhaben
  """

  genehmigungsbehoerde = CharField(
    'Genehmigungsbehörde',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"genehmigungsbehoerden_uvp_vorhaben'
    ordering = ['genehmigungsbehoerde']
    verbose_name = 'Genehmigungsbehörde eines UVP-Vorhabens'
    verbose_name_plural = 'Genehmigungsbehörden von UVP-Vorhaben'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Genehmigungsbehörden von UVP-Vorhaben'
    list_fields = {
      'genehmigungsbehoerde': 'Genehmigungsbehörde'
    }

  def __str__(self):
    return self.genehmigungsbehoerde


class Geschlechter_Kadaverfunde(Codelist):
  """
  Geschlechter bei Kadaverfunden
  """

  ordinalzahl = PositiveSmallIntegerRangeField(
    'Ordinalzahl',
    min_value=1
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"geschlechter_kadaverfunde'
    ordering = ['ordinalzahl']
    verbose_name = 'Geschlecht bei einem Kadaverfund'
    verbose_name_plural = 'Geschlechter bei Kadaverfunden'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Geschlechter bei Kadaverfunden'
    naming = 'bezeichnung'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'bezeichnung': 'Bezeichnung'
    }

  def __str__(self):
    return self.bezeichnung


class Haefen(Codelist):
  """
  Häfen
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  abkuerzung = CharField(
    'Abkürzung',
    max_length=5,
    unique=True,
    validators=[
      RegexValidator(
        regex=haefen_abkuerzung_regex,
        message=haefen_abkuerzung_message
      )
    ]
  )
  code = PositiveSmallIntegerRangeField(
    'Code',
    min_value=1,
    unique=True,
    blank=True,
    null=True
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"haefen'
    ordering = ['bezeichnung']
    verbose_name = 'Hafen'
    verbose_name_plural = 'Häfen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Häfen'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'abkuerzung': 'Abkürzung',
      'code': 'Code'
    }
    list_fields_with_number = ['code']

  def __str__(self):
    return self.bezeichnung


class Hersteller_Poller(Codelist):
  """
  Hersteller von Pollern
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"hersteller_poller'
    ordering = ['bezeichnung']
    verbose_name = 'Hersteller eines Pollers'
    verbose_name_plural = 'Hersteller von Pollern'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Hersteller von Pollern'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }

  def __str__(self):
    return self.bezeichnung


class Kategorien_Strassen(Codelist):
  """
  Kategorien von Straßen
  """

  code = PositiveSmallIntegerRangeField(
    'Code',
    min_value=1,
    unique=True
  )
  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    validators=standard_validators
  )
  erlaeuterung = CharField(
    'Erläuterung',
    max_length=255,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"kategorien_strassen'
    ordering = ['code']
    verbose_name = 'Kategorie einer Straße'
    verbose_name_plural = 'Kategorien von Straßen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Kategorien von Straßen'
    naming = 'bezeichnung'
    list_fields = {
      'code': 'Code',
      'bezeichnung': 'Bezeichnung',
      'erlaeuterung': 'Erläuterung'
    }
    list_fields_with_number = ['code']

  def __str__(self):
    return self.bezeichnung


class Ladekarten_Ladestationen_Elektrofahrzeuge(Codelist):
  """
  Ladekarten für Ladestationen für Elektrofahrzeuge
  """

  ladekarte = CharField(
    'Ladekarte',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"ladekarten_ladestationen_elektrofahrzeuge'
    ordering = ['ladekarte']
    verbose_name = 'Ladekarte für eine Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Ladekarten für Ladestationen für Elektrofahrzeuge'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Ladekarten für Ladestationen für Elektrofahrzeuge'
    list_fields = {
      'ladekarte': 'Ladekarte'
    }

  def __str__(self):
    return self.ladekarte


class Linien(Codelist):
  """
  Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH
  """

  linie = CharField(
    'Linie',
    max_length=4,
    unique=True,
    validators=[
      RegexValidator(
        regex=linien_linie_regex,
        message=linien_linie_message
      )
    ]
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"linien'
    ordering = ['linie']
    verbose_name = 'Linie der Rostocker Straßenbahn AG und/oder der Regionalbus Rostock GmbH'
    verbose_name_plural = 'Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH'
    list_fields = {
      'linie': 'Linie'
    }

  def __str__(self):
    return self.linie


class Mastkennzeichen_RSAG(Codelist):
  """
  Mastkennzeichen innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG
  """

  kennzeichen = CharField(
    'Kennzeichen',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  erlaeuterung = CharField(
    'Erläuterung',
    max_length=255,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"mastkennzeichen_rsag'
    ordering = ['kennzeichen']
    verbose_name = 'Mastkennzeichen innerhalb der Straßenbahninfrastruktur ' \
                   'der Rostocker Straßenbahn AG'
    verbose_name_plural = 'Mastkennzeichen innerhalb der Straßenbahninfrastruktur ' \
                          'der Rostocker Straßenbahn AG'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Mastkennzeichen innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG'
    list_fields = {
      'kennzeichen': 'Kennzeichen',
      'erlaeuterung': 'Erläuterung'
    }

  def __str__(self):
    return self.erlaeuterung + ' (' + self.kennzeichen + ')'


class Masttypen_RSAG(Codelist):
  """
  Masttypen innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG
  """

  typ = CharField(
    'Typ',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  erlaeuterung = CharField(
    'Erläuterung',
    max_length=255,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"masttypen_rsag'
    ordering = ['typ']
    verbose_name = 'Masttyp innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG'
    verbose_name_plural = 'Masttypen innerhalb der Straßenbahninfrastruktur ' \
                          'der Rostocker Straßenbahn AG'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Masttypen innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG'
    list_fields = {
      'typ': 'Typ',
      'erlaeuterung': 'Erläuterung'
    }

  def __str__(self):
    return self.typ


class Masttypen_Haltestellenkataster(Codelist):
  """
  Masttypen innerhalb eines Haltestellenkatasters
  """

  masttyp = CharField(
    'Masttyp',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"masttypen_haltestellenkataster'
    ordering = ['masttyp']
    verbose_name = 'Masttyp innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Masttypen innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Masttypen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'masttyp': 'Masttyp'
    }

  def __str__(self):
    return self.masttyp


class Materialien_Denksteine(Material):
  """
  Materialien von Denksteinen
  """

  class Meta(Material.Meta):
    db_table = 'codelisten\".\"materialien_denksteine'
    verbose_name = 'Material eines Denksteins'
    verbose_name_plural = 'Materialien von Denksteinen'

  class BasemodelMeta(Material.BasemodelMeta):
    description = 'Materialien von Denksteinen'


class Materialien_Durchlaesse(Material):
  """
  Materialien von Durchlässen
  """

  class Meta(Material.Meta):
    db_table = 'codelisten\".\"materialien_durchlaesse'
    verbose_name = 'Material eines Durchlasses'
    verbose_name_plural = 'Materialien von Durchlässen'

  class BasemodelMeta(Material.BasemodelMeta):
    description = 'Materialien von Durchlässen'


class Ordnungen_Fliessgewaesser(Codelist):
  """
  Ordnungen von Fließgewässern
  """

  ordnung = PositiveSmallIntegerMinField(
    'Ordnung',
    min_value=1,
    unique=True
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"ordnungen_fliessgewaesser'
    ordering = ['ordnung']
    verbose_name = 'Ordnung eines Fließgewässers'
    verbose_name_plural = 'Ordnungen von Fließgewässern'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Ordnungen von Fließgewässern'
    list_fields = {
      'ordnung': 'Ordnung'
    }
    list_fields_with_number = ['ordnung']

  def __str__(self):
    return str(self.ordnung)


class Personentitel(Codelist):
  """
  Personentitel
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"personentitel'
    ordering = ['bezeichnung']
    verbose_name = 'Personentitel'
    verbose_name_plural = 'Personentitel'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Personentitel'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }

  def __str__(self):
    return self.bezeichnung


class Quartiere(Codelist):
  """
  Quartiere
  """

  code = CharField(
    'Code',
    max_length=3,
    unique=True,
    validators=[
      RegexValidator(
        regex=quartiere_code_regex,
        message=quartiere_code_message
      )
    ]
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"quartiere'
    ordering = ['code']
    verbose_name = 'Quartier'
    verbose_name_plural = 'Quartiere'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Quartiere'
    list_fields = {
      'code': 'Code'
    }

  def __str__(self):
    return str(self.code)


class Raeumbreiten_Strassenreinigungssatzung_HRO(Codelist):
  """
  Räumbreiten gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  raeumbreite = DecimalField(
    'Räumbreite (in m)',
    max_digits=4,
    decimal_places=2,
    unique=True,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Räumbreite</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Räumbreite</em></strong> darf höchstens 99,99 m betragen.'
      )
    ]
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"raeumbreiten_strassenreinigungssatzung_hro'
    ordering = ['raeumbreite']
    verbose_name = 'Räumbreite gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Räumbreiten gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Räumbreiten gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'raeumbreite': 'Räumbreite'
    }
    list_fields_with_number = ['raeumbreite']

  def __str__(self):
    return str(self.raeumbreite)


class Rechtsgrundlagen_UVP_Vorhaben(Codelist):
  """
  Rechtsgrundlagen von UVP-Vorhaben
  """

  rechtsgrundlage = CharField(
    'Rechtsgrundlage',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"rechtsgrundlagen_uvp_vorhaben'
    ordering = ['rechtsgrundlage']
    verbose_name = 'Rechtsgrundlage eines UVP-Vorhabens'
    verbose_name_plural = 'Rechtsgrundlagen von UVP-Vorhaben'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Rechtsgrundlagen von UVP-Vorhaben'
    list_fields = {
      'rechtsgrundlage': 'Rechtsgrundlage'
    }

  def __str__(self):
    return self.rechtsgrundlage


class Reinigungsklassen_Strassenreinigungssatzung_HRO(Codelist):
  """
  Reinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  code = PositiveSmallIntegerRangeField(
    'Code',
    min_value=1,
    max_value=7,
    unique=True
  )
  reinigungshaeufigkeit_pro_jahr = PositiveSmallIntegerRangeField(
    'Reinigungshäufigkeit pro Jahr',
    min_value=1
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"reinigungsklassen_strassenreinigungssatzung_hro'
    ordering = ['code']
    verbose_name = 'Reinigungsklasse gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Reinigungsklassen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Reinigungsklassen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'code': 'Code',
      'reinigungshaeufigkeit_pro_jahr': 'Reinigungshäufigkeit pro Jahr'
    }
    list_fields_with_number = ['code', 'reinigungshaeufigkeit_pro_jahr']

  def __str__(self):
    return str(self.code)


class Reinigungsrhythmen_Strassenreinigungssatzung_HRO(Codelist):
  """
  Reinigungsrhythmen gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  ordinalzahl = PositiveSmallIntegerRangeField(
    'Ordinalzahl',
    min_value=1,
    unique=True
  )
  reinigungsrhythmus = CharField(
    'Reinigungsrhythmus',
    max_length=255,
    validators=standard_validators
  )
  reinigungshaeufigkeit_pro_jahr = PositiveSmallIntegerRangeField(
    'Reinigungshäufigkeit pro Jahr',
    min_value=1,
    blank=True,
    null=True
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"reinigungsrhythmen_strassenreinigungssatzung_hro'
    ordering = ['ordinalzahl']
    verbose_name = 'Reinigungsrhythmus gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Reinigungsrhythmen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Reinigungsrhythmen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    naming = 'reinigungsrhythmus'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'reinigungsrhythmus': 'Reinigungsrhythmus',
      'reinigungshaeufigkeit_pro_jahr': 'Reinigungshäufigkeit pro Jahr'
    }
    list_fields_with_number = ['ordinalzahl', 'reinigungshaeufigkeit_pro_jahr']

  def __str__(self):
    return str(self.reinigungsrhythmus)


class Schaeden_Haltestellenkataster(Codelist):
  """
  Schäden innerhalb eines Haltestellenkatasters
  """

  schaden = CharField(
    'Schaden',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"schaeden_haltestellenkataster'
    ordering = ['schaden']
    verbose_name = 'Schaden innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Schäden innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Schäden innerhalb eines Haltestellenkatasters'
    list_fields = {
      'schaden': 'Schaden'
    }

  def __str__(self):
    return self.schaden


class Schlagwoerter_Bildungstraeger(Schlagwort):
  """
  Schlagwörter für Bildungsträger
  """

  class Meta(Schlagwort.Meta):
    db_table = 'codelisten\".\"schlagwoerter_bildungstraeger'
    verbose_name = 'Schlagwort für einen Bildungsträger'
    verbose_name_plural = 'Schlagwörter für Bildungsträger'

  class BasemodelMeta(Schlagwort.BasemodelMeta):
    description = 'Schlagwörter für Bildungsträger'


class Schlagwoerter_Vereine(Schlagwort):
  """
  Schlagwörter für Vereine
  """

  class Meta(Schlagwort.Meta):
    db_table = 'codelisten\".\"schlagwoerter_vereine'
    verbose_name = 'Schlagwort für einen Verein'
    verbose_name_plural = 'Schlagwörter für Vereine'

  class BasemodelMeta(Schlagwort.BasemodelMeta):
    description = 'Schlagwörter für Vereine'


class Schliessungen_Poller(Codelist):
  """
  Schließungen von Pollern
  """

  schliessung = CharField(
    'Schließung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"schliessungen_poller'
    ordering = ['schliessung']
    verbose_name = 'Schließung eines Pollers'
    verbose_name_plural = 'Schließungen von Pollern'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Schließungen von Pollern'
    list_fields = {
      'schliessung': 'Schließung'
    }

  def __str__(self):
    return self.schliessung


class Sitzbanktypen_Haltestellenkataster(Codelist):
  """
  Sitzbanktypen innerhalb eines Haltestellenkatasters
  """

  sitzbanktyp = CharField(
    'Sitzbanktyp',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"sitzbanktypen_haltestellenkataster'
    ordering = ['sitzbanktyp']
    verbose_name = 'Sitzbanktyp innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Sitzbanktypen innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Sitzbanktypen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'sitzbanktyp': 'Sitzbanktyp'
    }

  def __str__(self):
    return self.sitzbanktyp


class Sparten_Baustellen(Codelist):
  """
  Sparten von Baustellen
  """

  sparte = CharField(
    'Sparte',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"sparten_baustellen'
    ordering = ['sparte']
    verbose_name = 'Sparte einer Baustelle'
    verbose_name_plural = 'Sparten von Baustellen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Sparten von Baustellen'
    list_fields = {
      'sparte': 'Sparte'
    }

  def __str__(self):
    return self.sparte


class Sportarten(Codelist):
  """
  Sportarten
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"sportarten'
    ordering = ['bezeichnung']
    verbose_name = 'Sportart'
    verbose_name_plural = 'Sportarten'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Sportarten'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }

  def __str__(self):
    return self.bezeichnung


class Status_Baudenkmale_Denkmalbereiche(Status):
  """
  Status von Baudenkmalen und Denkmalbereichen
  """

  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_baudenkmale_denkmalbereiche'
    verbose_name = 'Status eines Baudenkmals oder Denkmalbereichs'
    verbose_name_plural = 'Status von Baudenkmalen und Denkmalbereichen'

  class BasemodelMeta(Status.BasemodelMeta):
    description = 'Status von Baudenkmalen und Denkmalbereichen'


class Status_Baustellen_geplant(Status):
  """
  Status von Baustellen (geplant)
  """

  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_baustellen_geplant'
    verbose_name = 'Status einer Baustelle (geplant)'
    verbose_name_plural = 'Status von Baustellen (geplant)'

  class BasemodelMeta(Status.BasemodelMeta):
    description = 'Status von Baustellen (geplant)'


class Status_Baustellen_Fotodokumentation_Fotos(Status):
  """
  Status von Fotos der Baustellen-Fotodokumentation
  """

  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_baustellen_fotodokumentation_fotos'
    verbose_name = 'Status eines Fotos der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Status von Fotos der Baustellen-Fotodokumentation'

  class BasemodelMeta(Status.BasemodelMeta):
    description = 'Status von Fotos der Baustellen-Fotodokumentation'


class Status_Poller(Status):
  """
  Status von Pollern
  """

  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_poller'
    verbose_name = 'Status eines Pollers'
    verbose_name_plural = 'Status von Pollern'

  class BasemodelMeta(Status.BasemodelMeta):
    description = 'Status von Pollern'


class Tierseuchen(Codelist):
  """
  Tierseuchen
  """

  bezeichnung = CharField(
    'Bezeichnung',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"tierseuchen'
    ordering = ['bezeichnung']
    verbose_name = 'Tierseuche'
    verbose_name_plural = 'Tierseuchen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Tierseuchen'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }

  def __str__(self):
    return self.bezeichnung


class Typen_Abfallbehaelter(Typ):
  """
  Typen von Abfallbehältern
  """

  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_abfallbehaelter'
    verbose_name = 'Typ eines Abfallbehälters'
    verbose_name_plural = 'Typen von Abfallbehältern'

  class BasemodelMeta(Typ.BasemodelMeta):
    description = 'Typen von Abfallbehältern'


class DFI_Typen_Haltestellenkataster(Codelist):
  """
  Typen von Dynamischen Fahrgastinformationssystemen innerhalb eines Haltestellenkatasters
  """

  dfi_typ = CharField(
    'DFI-Typ',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"dfi_typen_haltestellenkataster'
    ordering = ['dfi_typ']
    verbose_name = 'Typ eines Dynamischen Fahrgastinformationssystems ' \
                   'innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Dynamischen Fahrgastinformationssystemen ' \
                          'innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Typen von Dynamischen Fahrgastinformationssystemen ' \
                  'innerhalb eines Haltestellenkatasters'
    list_fields = {
      'dfi_typ': 'DFI-Typ'
    }

  def __str__(self):
    return self.dfi_typ


class Typen_Erdwaermesonden(Typ):
  """
  Typen von Erdwärmesonden
  """

  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_erdwaermesonden'
    verbose_name = 'Typ einer Erdwärmesonde'
    verbose_name_plural = 'Typen von Erdwärmesonden'

  class BasemodelMeta(Typ.BasemodelMeta):
    description = 'Typen von Erdwärmesonden'


class Typen_Kleinklaeranlagen(Typ):
  """
  Typen von Kleinkläranlagen
  """

  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_kleinklaeranlagen'
    verbose_name = 'Typ einer Kleinkläranlage'
    verbose_name_plural = 'Typen von Kleinkläranlagen'

  class BasemodelMeta(Typ.BasemodelMeta):
    description = 'Typen von Kleinkläranlagen'


class Fahrgastunterstandstypen_Haltestellenkataster(Codelist):
  """
  Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters
  """

  fahrgastunterstandstyp = CharField(
    'Fahrgastunterstandstyp',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"fahrgastunterstandstypen_haltestellenkataster'
    ordering = ['fahrgastunterstandstyp']
    verbose_name = 'Typ eines Fahrgastunterstands innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fahrgastunterstandstyp': 'Fahrgastunterstandstyp'
    }

  def __str__(self):
    return self.fahrgastunterstandstyp


class Fahrplanvitrinentypen_Haltestellenkataster(Codelist):
  """
  Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters
  """

  fahrplanvitrinentyp = CharField(
    'Fahrplanvitrinentyp',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"fahrplanvitrinentypen_haltestellenkataster'
    ordering = ['fahrplanvitrinentyp']
    verbose_name = 'Typ einer Fahrplanvitrine innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fahrplanvitrinentyp': 'Fahrplanvitrinentyp'
    }

  def __str__(self):
    return self.fahrplanvitrinentyp


class Typen_Haltestellen(Typ):
  """
  Typen von Haltestellen
  """

  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_haltestellen'
    verbose_name = 'Typ einer Haltestelle'
    verbose_name_plural = 'Typen von Haltestellen'

  class BasemodelMeta(Typ.BasemodelMeta):
    description = 'Typen von Haltestellen'


class Typen_Poller(Typ):
  """
  Typen von Pollern
  """

  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_poller'
    verbose_name = 'Typ eines Pollers'
    verbose_name_plural = 'Typen von Pollern'

  class BasemodelMeta(Typ.BasemodelMeta):
    description = 'Typen von Pollern'


class Typen_UVP_Vorhaben(Typ):
  """
  Typen von UVP-Vorhaben
  """

  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_uvp_vorhaben'
    verbose_name = 'Typ eines UVP-Vorhabens'
    verbose_name_plural = 'Typen von UVP-Vorhaben'

  class BasemodelMeta(Typ.BasemodelMeta):
    description = 'Typen von UVP-Vorhaben'


class Verbuende_Ladestationen_Elektrofahrzeuge(Codelist):
  """
  Verbünde von Ladestationen für Elektrofahrzeuge
  """

  verbund = CharField(
    'Verbund',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"verbuende_ladestationen_elektrofahrzeuge'
    ordering = ['verbund']
    verbose_name = 'Verbund einer Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Verbünde von Ladestationen für Elektrofahrzeuge'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Verbünde von Ladestationen für Elektrofahrzeuge'
    list_fields = {
      'verbund': 'Verbund'
    }

  def __str__(self):
    return self.verbund


class Verkehrliche_Lagen_Baustellen(Codelist):
  """
  Verkehrliche Lagen von Baustellen
  """

  verkehrliche_lage = CharField(
    ' verkehrliche Lage',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"verkehrliche_lagen_baustellen'
    ordering = ['verkehrliche_lage']
    verbose_name = 'Verkehrliche Lage einer Baustelle'
    verbose_name_plural = 'Verkehrliche Lagen von Baustellen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Verkehrliche Lagen von Baustellen'
    list_fields = {
      'verkehrliche_lage': 'verkehrliche Lage'
    }

  def __str__(self):
    return self.verkehrliche_lage


class Verkehrsmittelklassen(Codelist):
  """
  Verkehrsmittelklassen
  """

  verkehrsmittelklasse = CharField(
    'Verkehrsmittelklasse',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"verkehrsmittelklassen'
    ordering = ['verkehrsmittelklasse']
    verbose_name = 'Verkehrsmittelklasse'
    verbose_name_plural = 'Verkehrsmittelklassen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Verkehrsmittelklassen'
    list_fields = {
      'verkehrsmittelklasse': 'Verkehrsmittelklasse'
    }

  def __str__(self):
    return self.verkehrsmittelklasse


class Vorgangsarten_UVP_Vorhaben(Codelist):
  """
  Vorgangsarten von UVP-Vorhaben
  """

  vorgangsart = CharField(
    'Vorgangsart',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"vorgangsarten_uvp_vorhaben'
    ordering = ['vorgangsart']
    verbose_name = 'Vorgangsart eines UVP-Vorhabens'
    verbose_name_plural = 'Vorgangsarten von UVP-Vorhaben'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Vorgangsarten von UVP-Vorhaben'
    list_fields = {
      'vorgangsart': 'Vorgangsart'
    }

  def __str__(self):
    return self.vorgangsart


class Wegebreiten_Strassenreinigungssatzung_HRO(Codelist):
  """
  Wegebreiten gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  wegebreite = DecimalField(
    'Wegebreite (in m)',
    max_digits=4,
    decimal_places=2,
    unique=True,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Wegebreite</em></strong> muss mindestens 0,01 m betragen.'
      ),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Wegebreite</em></strong> darf höchstens 99,99 m betragen.'
      )
    ]
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"wegebreiten_strassenreinigungssatzung_hro'
    ordering = ['wegebreite']
    verbose_name = 'Wegebreite gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Wegebreiten gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Wegebreiten gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'wegebreite': 'Wegebreite'
    }
    list_fields_with_number = ['wegebreite']

  def __str__(self):
    return str(self.wegebreite)


class Wegereinigungsklassen_Strassenreinigungssatzung_HRO(Codelist):
  """
  Wegereinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  code = PositiveSmallIntegerRangeField(
    'Code',
    min_value=1,
    max_value=7,
    unique=True
  )
  reinigungshaeufigkeit_pro_jahr = PositiveSmallIntegerRangeField(
    'Reinigungshäufigkeit pro Jahr',
    min_value=1
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"wegereinigungsklassen_strassenreinigungssatzung_hro'
    ordering = ['code']
    verbose_name = 'Wegereinigungsklasse gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Wegereinigungsklassen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Wegereinigungsklassen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'code': 'Code',
      'reinigungshaeufigkeit_pro_jahr': 'Reinigungshäufigkeit pro Jahr'
    }
    list_fields_with_number = ['code', 'reinigungshaeufigkeit_pro_jahr']

  def __str__(self):
    return str(self.code)


class Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO(Codelist):
  """
  Wegereinigungsrhythmen gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  ordinalzahl = PositiveSmallIntegerRangeField(
    'Ordinalzahl',
    min_value=1,
    unique=True
  )
  reinigungsrhythmus = CharField(
    'Reinigungsrhythmus',
    max_length=255,
    validators=standard_validators
  )
  reinigungshaeufigkeit_pro_jahr = PositiveSmallIntegerRangeField(
    'Reinigungshäufigkeit pro Jahr',
    min_value=1,
    blank=True,
    null=True
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"wegereinigungsrhythmen_strassenreinigungssatzung_hro'
    ordering = ['ordinalzahl']
    verbose_name = 'Wegereinigungsrhythmus gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Wegereinigungsrhythmen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Wegereinigungsrhythmen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    naming = 'reinigungsrhythmus'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'reinigungsrhythmus': 'Reinigungsrhythmus',
      'reinigungshaeufigkeit_pro_jahr': 'Reinigungshäufigkeit pro Jahr'
    }
    list_fields_with_number = ['ordinalzahl', 'reinigungshaeufigkeit_pro_jahr']

  def __str__(self):
    return str(self.reinigungsrhythmus)


class Wegetypen_Strassenreinigungssatzung_HRO(Codelist):
  """
  Wegetypen gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  wegetyp = CharField(
    'Wegetyp',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"wegetypen_strassenreinigungssatzung_hro'
    ordering = ['wegetyp']
    verbose_name = 'Wegetyp gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Wegetypen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Wegetypen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'wegetyp': 'Wegetyp'
    }

  def __str__(self):
    return str(self.wegetyp)


class Zeiteinheiten(Codelist):
  """
  Zeiteinheiten
  """

  zeiteinheit = CharField(
    'Zeiteinheit',
    max_length=255,
    unique=True,
    validators=standard_validators
  )
  erlaeuterung = CharField(
    'Erläuterung',
    max_length=255,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"zeiteinheiten'
    ordering = ['erlaeuterung']
    verbose_name = 'Zeiteinheit'
    verbose_name_plural = 'Zeiteinheiten'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Zeiteinheiten'
    list_fields = {
      'zeiteinheit': 'Zeiteinheit',
      'erlaeuterung': 'Erläuterung'
    }

  def __str__(self):
    return self.erlaeuterung


class ZH_Typen_Haltestellenkataster(Codelist):
  """
  ZH-Typen innerhalb eines Haltestellenkatasters
  """

  zh_typ = CharField(
    'ZH-Typ',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"zh_typen_haltestellenkataster'
    ordering = ['zh_typ']
    verbose_name = 'ZH-Typ innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'ZH-Typen innerhalb eines Haltestellenkatasters'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'ZH-Typen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'zh_typ': 'ZH-Typ'
    }

  def __str__(self):
    return self.zh_typ


class Zonen_Parkscheinautomaten(Codelist):
  """
  Zonen für Parkscheinautomaten
  """

  zone = CharField(
    'Zone',
    max_length=1,
    unique=True,
    validators=[
      RegexValidator(
        regex=parkscheinautomaten_zone_regex,
        message=parkscheinautomaten_zone_message
      )
    ]
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"zonen_parkscheinautomaten'
    ordering = ['zone']
    verbose_name = 'Zone für einen Parkscheinautomaten'
    verbose_name_plural = 'Zonen für Parkscheinautomaten'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Zonen für Parkscheinautomaten'
    list_fields = {
      'zone': 'Zone'
    }

  def __str__(self):
    return self.zone


class Zustaende_Kadaverfunde(Codelist):
  """
  Zustände von Kadaverfunden
  """

  ordinalzahl = PositiveSmallIntegerRangeField(
    'Ordinalzahl',
    min_value=1
  )
  zustand = CharField(
    'Zustand',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"zustaende_kadaverfunde'
    ordering = ['ordinalzahl']
    verbose_name = 'Zustand eines Kadaverfunds'
    verbose_name_plural = 'Zustände von Kadaverfunden'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Zustände von Kadaverfunden'
    naming = 'zustand'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'zustand': 'Zustand'
    }
    list_fields_with_number = ['ordinalzahl']

  def __str__(self):
    return str(self.zustand)


class Zustaende_Schutzzaeune_Tierseuchen(Codelist):
  """
  Zustände von Schutzzäunen gegen Tierseuchen
  """

  ordinalzahl = PositiveSmallIntegerRangeField(
    'Ordinalzahl',
    min_value=1
  )
  zustand = CharField(
    'Zustand',
    max_length=255,
    unique=True,
    validators=standard_validators
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"zustaende_schutzzaeune_tierseuchen'
    ordering = ['ordinalzahl']
    verbose_name = 'Zustand eines Schutzzauns gegen eine Tierseuche'
    verbose_name_plural = 'Zustände von Schutzzäunen gegen Tierseuchen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Zustände von Schutzzäunen gegen Tierseuchen'
    naming = 'zustand'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'zustand': 'Zustand'
    }
    list_fields_with_number = ['ordinalzahl']

  def __str__(self):
    return str(self.zustand)


class Zustandsbewertungen(Codelist):
  """
  Zustandsbewertungen
  """

  zustandsbewertung = PositiveSmallIntegerMinField(
    'Zustandsbewertung',
    min_value=1,
    unique=True
  )

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"zustandsbewertungen'
    ordering = ['zustandsbewertung']
    verbose_name = 'Zustandsbewertung'
    verbose_name_plural = 'Zustandsbewertungen'

  class BasemodelMeta(Codelist.BasemodelMeta):
    description = 'Zustandsbewertungen'
    list_fields = {
      'zustandsbewertung': 'Zustandsbewertung'
    }

  def __str__(self):
    return str(self.zustandsbewertung)
