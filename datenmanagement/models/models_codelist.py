from decimal import Decimal
from django.core.validators import EmailValidator, MaxValueValidator, MinValueValidator, \
  RegexValidator
from django.db.models.fields import CharField, DecimalField

from .base import Metamodel, Codelist, Art, Befestigungsart, Material, Schlagwort, Status, Typ
from .constants_vars import personennamen_validators, standard_validators, email_message, \
  fahrbahnwinterdienst_code_regex, fahrbahnwinterdienst_code_message, haefen_abkuerzung_regex, \
  haefen_abkuerzung_message, linien_linie_regex, linien_linie_message, \
  parkscheinautomaten_zone_regex, parkscheinautomaten_zone_message, quartiere_code_regex, \
  quartiere_code_message
from .fields import PositiveSmallIntegerMinField, PositiveSmallIntegerRangeField


#
# Meta-Datenmodelle
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
    verbose_name = 'Adresse'
    verbose_name_plural = 'Adressen'
    description = 'Adressen in Mecklenburg-Vorpommern'
    list_fields = {
      'adresse': 'Adresse'
    }
    ordering = ['adresse']

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
    verbose_name = 'Straße'
    verbose_name_plural = 'Straßen'
    description = 'Straßen in Mecklenburg-Vorpommern'
    list_fields = {
      'strasse': 'Straße'
    }
    ordering = ['strasse']

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
    verbose_name = 'Inoffizielle Straße der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Inoffizielle Straßen der Hanse- und Universitätsstadt Rostock'
    description = 'Inoffizielle Straßen der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'strasse': 'Straße'
    }
    ordering = ['strasse']

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

  class Meta(Metamodel.Meta):
    db_table = 'basisdaten\".\"gemeindeteile_datenwerft_hro'
    verbose_name = 'Gemeindeteil'
    verbose_name_plural = 'Gemeindeteile'
    description = 'Gemeindeteile in Mecklenburg-Vorpommern'
    list_fields = {
      'gemeindeteil': 'Gemeindeteil'
    }
    ordering = ['gemeindeteil']
    as_overlay = True

  def __str__(self):
    return self.gemeindeteil


#
# Codelisten
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
    verbose_name = 'Altersklasse bei einem Kadaverfund'
    verbose_name_plural = 'Altersklassen bei Kadaverfunden'
    description = 'Altersklassen bei Kadaverfunden'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'bezeichnung': 'Bezeichnung'
    }
    ordering = ['ordinalzahl']
    naming = 'bezeichnung'

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
    verbose_name = 'Angebot bei einem Mobilpunkt'
    verbose_name_plural = 'Angebote bei Mobilpunkten'
    description = 'Angebote bei Mobilpunkten'
    list_fields = {
      'angebot': 'Angebot'
    }
    ordering = ['angebot']

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
    verbose_name = 'Angelberechtigung'
    verbose_name_plural = 'Angelberechtigungen'
    description = 'Angelberechtigungen'
    list_fields = {
      'angelberechtigung': 'Angelberechtigung'
    }
    ordering = ['angelberechtigung']

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
    verbose_name = 'Ansprechpartner:in bei einer Baustelle'
    verbose_name_plural = 'Ansprechpartner:innen bei Baustellen'
    description = 'Ansprechpartner:innen bei Baustellen'
    list_fields = {
      'vorname': 'Vorname',
      'nachname': 'Nachname',
      'email': 'E-Mail-Adresse'
    }
    ordering = [
      'nachname',
      'vorname',
      'email'
    ]

  def __str__(self):
    if not self.nachname:
      return self.email
    else:
      return self.vorname + ' ' + self.nachname + ' (' + self.email + ')'


class Arten_Baudenkmale(Art):
  """
  Arten von Baudenkmalen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_baudenkmale'
    verbose_name = 'Art eines Baudenkmals'
    verbose_name_plural = 'Arten von Baudenkmalen'
    description = 'Arten von Baudenkmalen'


class Arten_Durchlaesse(Art):
  """
  Arten von Durchlässen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_durchlaesse'
    verbose_name = 'Art eines Durchlasses'
    verbose_name_plural = 'Arten von Durchlässen'
    description = 'Arten von Durchlässen'


class Arten_FairTrade(Art):
  """
  Arten von Fair-Trade-Einrichtungen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fairtrade'
    verbose_name = 'Art einer Fair-Trade-Einrichtung'
    verbose_name_plural = 'Arten von Fair-Trade-Einrichtungen'
    description = 'Arten von Fair-Trade-Einrichtungen'


class Arten_Feldsportanlagen(Art):
  """
  Arten von Feldsportanlagen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_feldsportanlagen'
    verbose_name = 'Art einer Feldsportanlage'
    verbose_name_plural = 'Arten von Feldsportanlagen'
    description = 'Arten von Feldsportanlagen'


class Arten_Feuerwachen(Art):
  """
  Arten von Feuerwachen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_feuerwachen'
    verbose_name = 'Art einer Feuerwache'
    verbose_name_plural = 'Arten von Feuerwachen'
    description = 'Arten von Feuerwachen'


class Arten_Fliessgewaesser(Art):
  """
  Arten von Fließgewässern
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fliessgewaesser'
    verbose_name = 'Art eines Fließgewässers'
    verbose_name_plural = 'Arten von Fließgewässern'
    description = 'Arten von Fließgewässern'


class Arten_Hundetoiletten(Art):
  """
  Arten von Hundetoiletten
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_hundetoiletten'
    verbose_name = 'Art einer Hundetoilette'
    verbose_name_plural = 'Arten von Hundetoiletten'
    description = 'Arten von Hundetoiletten'


class Arten_Fallwildsuchen_Kontrollen(Art):
  """
  Arten von Kontrollen im Rahmen von Fallwildsuchen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fallwildsuchen_kontrollen'
    verbose_name = 'Art einer Kontrolle im Rahmen einer Fallwildsuche'
    verbose_name_plural = 'Arten von Kontrollen im Rahmen von Fallwildsuchen'
    description = 'Arten von Kontrollen im Rahmen von Fallwildsuchen'


class Arten_Meldedienst_flaechenhaft(Art):
  """
  Arten von Meldediensten (flächenhaft)
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_meldedienst_flaechenhaft'
    verbose_name = 'Art eines Meldedienstes (flächenhaft)'
    verbose_name_plural = 'Arten von Meldediensten (flächenhaft)'
    description = 'Arten von Meldediensten (flächenhaft)'


class Arten_Meldedienst_punkthaft(Art):
  """
  Arten von Meldediensten (punkthaft)
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_meldedienst_punkthaft'
    verbose_name = 'Art eines Meldedienstes (punkthaft)'
    verbose_name_plural = 'Arten von Meldediensten (punkthaft)'
    description = 'Arten von Meldediensten (punkthaft)'


class Arten_Parkmoeglichkeiten(Art):
  """
  Arten von Parkmöglichkeiten
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_parkmoeglichkeiten'
    verbose_name = 'Art einer Parkmöglichkeit'
    verbose_name_plural = 'Arten von Parkmöglichkeiten'
    description = 'Arten von Parkmöglichkeiten'


class Arten_Pflegeeinrichtungen(Art):
  """
  Arten von Pflegeeinrichtungen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_pflegeeinrichtungen'
    verbose_name = 'Art einer Pflegeeinrichtung'
    verbose_name_plural = 'Arten von Pflegeeinrichtungen'
    description = 'Arten von Pflegeeinrichtungen'


class Arten_Poller(Art):
  """
  Arten von Pollern
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_poller'
    verbose_name = 'Art eines Pollers'
    verbose_name_plural = 'Arten von Pollern'
    description = 'Arten von Pollern'


class Arten_Toiletten(Art):
  """
  Arten von Toiletten
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_toiletten'
    verbose_name = 'Art einer Toilette'
    verbose_name_plural = 'Arten von Toiletten'
    description = 'Arten von Toiletten'


class Arten_UVP_Vorpruefungen(Art):
  """
  Arten von UVP-Vorprüfungen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_uvp_vorpruefungen'
    verbose_name = 'Art einer UVP-Vorprüfung'
    verbose_name_plural = 'Arten von UVP-Vorprüfungen'
    description = 'Arten von UVP-Vorprüfungen'


class Arten_Wege(Art):
  """
  Arten von Wegen
  """

  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_wege'
    verbose_name = 'Art eines Weges'
    verbose_name_plural = 'Arten von Wegen'
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
    verbose_name = 'Auftraggeber einer Baustelle'
    verbose_name_plural = 'Auftraggeber von Baustellen'
    description = 'Auftraggeber von Baustellen'
    list_fields = {
      'auftraggeber': 'Auftraggeber'
    }
    ordering = ['auftraggeber']

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
    verbose_name = 'Ausführung innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Ausführungen innerhalb eines Haltestellenkatasters'
    description = 'Ausführungen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'ausfuehrung': 'Ausführung'
    }
    ordering = ['ausfuehrung']

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
    description = 'Befestigungsarten der Aufstellfläche Bus innerhalb eines Haltestellenkatasters'


class Befestigungsarten_Warteflaeche_Haltestellenkataster(Befestigungsart):
  """
  Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters
  """

  class Meta(Befestigungsart.Meta):
    db_table = 'codelisten\".\"befestigungsarten_warteflaeche_haltestellenkataster'
    verbose_name = 'Befestigungsart der Wartefläche innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters'
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
    verbose_name = 'Betriebsart'
    verbose_name_plural = 'Betriebsarten'
    description = 'Betriebsarten'
    list_fields = {
      'betriebsart': 'Betriebsart'
    }
    ordering = ['betriebsart']

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
    verbose_name = 'Betriebszeit'
    verbose_name_plural = 'Betriebszeiten'
    description = 'Betriebszeiten'
    list_fields = {
      'betriebszeit': 'Betriebszeit'
    }
    ordering = ['betriebszeit']

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
    verbose_name = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    verbose_name_plural = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    description = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'art': 'Art'
    }
    ordering = ['bezeichnung']

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
    verbose_name = 'Carsharing-Anbieter'
    verbose_name_plural = 'Carsharing-Anbieter'
    description = 'Carsharing-Anbieter'
    list_fields = {
      'anbieter': 'Anbieter'
    }
    ordering = ['anbieter']

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
    verbose_name = 'E-Anschluss für einen Parkscheinautomaten'
    verbose_name_plural = 'E-Anschlüsse für Parkscheinautomaten'
    description = 'E-Anschlüsse für Parkscheinautomaten'
    list_fields = {
      'e_anschluss': 'E-Anschluss'
    }
    ordering = ['e_anschluss']

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
    verbose_name = 'Ergebnis einer UVP-Vorprüfung'
    verbose_name_plural = 'Ergebnisse von UVP-Vorprüfungen'
    description = 'Ergebnisse von UVP-Vorprüfungen'
    list_fields = {
      'ergebnis': 'Ergebnis'
    }
    ordering = ['ergebnis']

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
    verbose_name = 'Fahrbahnwinterdienst gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Fahrbahnwinterdienst gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'
    description = 'Fahrbahnwinterdienst gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'code': 'Code'
    }
    ordering = ['code']

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
    verbose_name = 'Fotomotiv innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Fotomotive innerhalb eines Haltestellenkatasters'
    description = 'Fotomotive innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fotomotiv': 'Fotomotiv'
    }
    ordering = ['fotomotiv']

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
    verbose_name = 'Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur ' \
                   'der Rostocker Straßenbahn AG'
    verbose_name_plural = 'Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur ' \
                          'der Rostocker Straßenbahn AG'
    description = 'Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG'
    list_fields = {
      'typ': 'Typ',
      'erlaeuterung': 'Erläuterung'
    }
    ordering = ['typ']

  def __str__(self):
    return self.typ


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
    verbose_name = 'Gebäudebauweise'
    verbose_name_plural = 'Gebäudebauweisen'
    description = 'Gebäudebauweisen'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'code': 'Code'
    }
    list_fields_with_number = ['code']
    ordering = ['bezeichnung']

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
    verbose_name = 'Gebäudefunktion'
    verbose_name_plural = 'Gebäudefunktionen'
    description = 'Gebäudefunktionen'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'code': 'Code'
    }
    list_fields_with_number = ['code']
    ordering = ['bezeichnung']

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
    verbose_name = 'Genehmigungsbehörde eines UVP-Vorhabens'
    verbose_name_plural = 'Genehmigungsbehörden von UVP-Vorhaben'
    description = 'Genehmigungsbehörden von UVP-Vorhaben'
    list_fields = {
      'genehmigungsbehoerde': 'Genehmigungsbehörde'
    }
    ordering = ['genehmigungsbehoerde']

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
    verbose_name = 'Geschlecht bei einem Kadaverfund'
    verbose_name_plural = 'Geschlechter bei Kadaverfunden'
    description = 'Geschlechter bei Kadaverfunden'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'bezeichnung': 'Bezeichnung'
    }
    ordering = ['ordinalzahl']
    naming = 'bezeichnung'

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
    verbose_name = 'Hafen'
    verbose_name_plural = 'Häfen'
    description = 'Häfen'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'abkuerzung': 'Abkürzung',
      'code': 'Code'
    }
    list_fields_with_number = ['code']
    ordering = ['bezeichnung']

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
    verbose_name = 'Hersteller eines Pollers'
    verbose_name_plural = 'Hersteller von Pollern'
    description = 'Hersteller von Pollern'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }
    ordering = ['bezeichnung']

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
    verbose_name = 'Kategorie einer Straße'
    verbose_name_plural = 'Kategorien von Straßen'
    description = 'Kategorien von Straßen'
    list_fields = {
      'code': 'Code',
      'bezeichnung': 'Bezeichnung',
      'erlaeuterung': 'Erläuterung'
    }
    list_fields_with_number = ['code']
    ordering = ['code']
    naming = 'bezeichnung'

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
    verbose_name = 'Ladekarte für eine Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Ladekarten für Ladestationen für Elektrofahrzeuge'
    description = 'Ladekarten für Ladestationen für Elektrofahrzeuge'
    list_fields = {
      'ladekarte': 'Ladekarte'
    }
    ordering = ['ladekarte']

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
    verbose_name = 'Linie der Rostocker Straßenbahn AG und/oder der Regionalbus Rostock GmbH'
    verbose_name_plural = 'Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH'
    description = 'Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH'
    list_fields = {
      'linie': 'Linie'
    }
    ordering = ['linie']

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
    verbose_name = 'Mastkennzeichen innerhalb der Straßenbahninfrastruktur ' \
                   'der Rostocker Straßenbahn AG'
    verbose_name_plural = 'Mastkennzeichen innerhalb der Straßenbahninfrastruktur ' \
                          'der Rostocker Straßenbahn AG'
    description = 'Mastkennzeichen innerhalb der Straßenbahninfrastruktur ' \
                  'der Rostocker Straßenbahn AG'
    list_fields = {
      'kennzeichen': 'Kennzeichen',
      'erlaeuterung': 'Erläuterung'
    }
    ordering = ['kennzeichen']

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
    verbose_name = 'Masttyp innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG'
    verbose_name_plural = 'Masttypen innerhalb der Straßenbahninfrastruktur ' \
                          'der Rostocker Straßenbahn AG'
    description = 'Masttypen innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG'
    list_fields = {
      'typ': 'Typ',
      'erlaeuterung': 'Erläuterung'
    }
    ordering = ['typ']

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
    verbose_name = 'Masttyp innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Masttypen innerhalb eines Haltestellenkatasters'
    description = 'Masttypen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'masttyp': 'Masttyp'
    }
    ordering = ['masttyp']

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
    description = 'Materialien von Denksteinen'


class Materialien_Durchlaesse(Material):
  """
  Materialien von Durchlässen
  """

  class Meta(Material.Meta):
    db_table = 'codelisten\".\"materialien_durchlaesse'
    verbose_name = 'Material eines Durchlasses'
    verbose_name_plural = 'Materialien von Durchlässen'
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
    verbose_name = 'Ordnung eines Fließgewässers'
    verbose_name_plural = 'Ordnungen von Fließgewässern'
    description = 'Ordnungen von Fließgewässern'
    list_fields = {
      'ordnung': 'Ordnung'
    }
    list_fields_with_number = ['ordnung']
    ordering = ['ordnung']

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
    verbose_name = 'Personentitel'
    verbose_name_plural = 'Personentitel'
    description = 'Personentitel'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }
    ordering = ['bezeichnung']

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
    verbose_name = 'Quartier'
    verbose_name_plural = 'Quartiere'
    description = 'Quartiere'
    list_fields = {
      'code': 'Code'
    }
    ordering = ['code']

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
    verbose_name = 'Räumbreite gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Räumbreiten gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'
    description = 'Räumbreiten gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'raeumbreite': 'Räumbreite'
    }
    ordering = ['raeumbreite']

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
    verbose_name = 'Rechtsgrundlage eines UVP-Vorhabens'
    verbose_name_plural = 'Rechtsgrundlagen von UVP-Vorhaben'
    description = 'Rechtsgrundlagen von UVP-Vorhaben'
    list_fields = {
      'rechtsgrundlage': 'Rechtsgrundlage'
    }
    ordering = ['rechtsgrundlage']

  def __str__(self):
    return self.rechtsgrundlage


class Reinigungsklassen_Strassenreinigungssatzung_HRO(Codelist):
  """
  Reinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  code = PositiveSmallIntegerRangeField(
    'Code', min_value=1, max_value=7, unique=True)

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"reinigungsklassen_strassenreinigungssatzung_hro'
    verbose_name = 'Reinigungsklasse gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Reinigungsklassen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'
    description = 'Reinigungsklassen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'code': 'Code'
    }
    list_fields_with_number = ['code']
    ordering = ['code']

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

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"reinigungsrhythmen_strassenreinigungssatzung_hro'
    verbose_name = 'Reinigungsrhythmus gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Reinigungsrhythmen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'
    description = 'Reinigungsrhythmen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'reinigungsrhythmus': 'Reinigungsrhythmus'
    }
    list_fields_with_number = ['ordinalzahl']
    ordering = ['ordinalzahl']
    naming = 'reinigungsrhythmus'

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
    verbose_name = 'Schaden innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Schäden innerhalb eines Haltestellenkatasters'
    description = 'Schäden innerhalb eines Haltestellenkatasters'
    list_fields = {
      'schaden': 'Schaden'
    }
    ordering = ['schaden']

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
    description = 'Schlagwörter für Bildungsträger'


class Schlagwoerter_Vereine(Schlagwort):
  """
  Schlagwörter für Vereine
  """

  class Meta(Schlagwort.Meta):
    db_table = 'codelisten\".\"schlagwoerter_vereine'
    verbose_name = 'Schlagwort für einen Verein'
    verbose_name_plural = 'Schlagwörter für Vereine'
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
    verbose_name = 'Schließung eines Pollers'
    verbose_name_plural = 'Schließungen von Pollern'
    description = 'Schließungen von Pollern'
    list_fields = {
      'schliessung': 'Schließung'
    }
    ordering = ['schliessung']

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
    verbose_name = 'Sitzbanktyp innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Sitzbanktypen innerhalb eines Haltestellenkatasters'
    description = 'Sitzbanktypen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'sitzbanktyp': 'Sitzbanktyp'
    }
    ordering = ['sitzbanktyp']

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
    verbose_name = 'Sparte einer Baustelle'
    verbose_name_plural = 'Sparten von Baustellen'
    description = 'Sparten von Baustellen'
    list_fields = {
      'sparte': 'Sparte'
    }
    ordering = ['sparte']

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
    verbose_name = 'Sportart'
    verbose_name_plural = 'Sportarten'
    description = 'Sportarten'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung


class Status_Baustellen_geplant(Status):
  """
  Status von Baustellen (geplant)
  """

  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_baustellen_geplant'
    verbose_name = 'Status einer Baustelle (geplant)'
    verbose_name_plural = 'Status von Baustellen (geplant)'
    description = 'Status von Baustellen (geplant)'


class Status_Baustellen_Fotodokumentation_Fotos(Status):
  """
  Status von Fotos der Baustellen-Fotodokumentation
  """

  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_baustellen_fotodokumentation_fotos'
    verbose_name = 'Status eines Fotos der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Status von Fotos der Baustellen-Fotodokumentation'
    description = 'Status von Fotos der Baustellen-Fotodokumentation'


class Status_Poller(Status):
  """
  Status von Pollern
  """

  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_poller'
    verbose_name = 'Status eines Pollers'
    verbose_name_plural = 'Status von Pollern'
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
    verbose_name = 'Tierseuche'
    verbose_name_plural = 'Tierseuchen'
    description = 'Tierseuchen'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }
    ordering = ['bezeichnung']

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
    verbose_name = 'Typ eines Dynamischen Fahrgastinformationssystems ' \
                   'innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Dynamischen Fahrgastinformationssystemen ' \
                          'innerhalb eines Haltestellenkatasters'
    description = 'Typen von Dynamischen Fahrgastinformationssystemen ' \
                  'innerhalb eines Haltestellenkatasters'
    list_fields = {
      'dfi_typ': 'DFI-Typ'
    }
    ordering = ['dfi_typ']

  def __str__(self):
    return self.dfi_typ


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
    verbose_name = 'Typ eines Fahrgastunterstands innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters'
    description = 'Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fahrgastunterstandstyp': 'Fahrgastunterstandstyp'
    }
    ordering = ['fahrgastunterstandstyp']

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
    verbose_name = 'Typ einer Fahrplanvitrine innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters'
    description = 'Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fahrplanvitrinentyp': 'Fahrplanvitrinentyp'
    }
    ordering = ['fahrplanvitrinentyp']

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
    description = 'Typen von Haltestellen'


class Typen_Poller(Typ):
  """
  Typen von Pollern
  """

  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_poller'
    verbose_name = 'Typ eines Pollers'
    verbose_name_plural = 'Typen von Pollern'
    description = 'Typen von Pollern'


class Typen_UVP_Vorhaben(Typ):
  """
  Typen von UVP-Vorhaben
  """

  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_uvp_vorhaben'
    verbose_name = 'Typ eines UVP-Vorhabens'
    verbose_name_plural = 'Typen von UVP-Vorhaben'
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
    verbose_name = 'Verbund einer Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Verbünde von Ladestationen für Elektrofahrzeuge'
    description = 'Verbünde von Ladestationen für Elektrofahrzeuge'
    list_fields = {
      'verbund': 'Verbund'
    }
    ordering = ['verbund']

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
    verbose_name = 'Verkehrliche Lage einer Baustelle'
    verbose_name_plural = 'Verkehrliche Lagen von Baustellen'
    description = 'Verkehrliche Lagen von Baustellen'
    list_fields = {
      'verkehrliche_lage': 'verkehrliche Lage'
    }
    ordering = ['verkehrliche_lage']

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
    verbose_name = 'Verkehrsmittelklasse'
    verbose_name_plural = 'Verkehrsmittelklassen'
    description = 'Verkehrsmittelklassen'
    list_fields = {
      'verkehrsmittelklasse': 'Verkehrsmittelklasse'
    }
    ordering = ['verkehrsmittelklasse']

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
    verbose_name = 'Vorgangsart eines UVP-Vorhabens'
    verbose_name_plural = 'Vorgangsarten von UVP-Vorhaben'
    description = 'Vorgangsarten von UVP-Vorhaben'
    list_fields = {
      'vorgangsart': 'Vorgangsart'
    }
    ordering = ['vorgangsart']

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
    verbose_name = 'Wegebreite gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Wegebreiten gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'
    description = 'Wegebreiten gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'wegebreite': 'Wegebreite'
    }
    ordering = ['wegebreite']

  def __str__(self):
    return str(self.wegebreite)


class Wegereinigungsklassen_Strassenreinigungssatzung_HRO(Codelist):
  """
  Wegereinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt Rostock
  """

  code = PositiveSmallIntegerRangeField(
    'Code', min_value=1, max_value=7, unique=True)

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"wegereinigungsklassen_strassenreinigungssatzung_hro'
    verbose_name = 'Wegereinigungsklasse gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Wegereinigungsklassen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'
    description = 'Wegereinigungsklassen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'code': 'Code'
    }
    list_fields_with_number = ['code']
    ordering = ['code']

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

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"wegereinigungsrhythmen_strassenreinigungssatzung_hro'
    verbose_name = 'Wegereinigungsrhythmus gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Wegereinigungsrhythmen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'
    description = 'Wegereinigungsrhythmen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'reinigungsrhythmus': 'Reinigungsrhythmus'
    }
    list_fields_with_number = ['ordinalzahl']
    ordering = ['ordinalzahl']
    naming = 'reinigungsrhythmus'

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
    verbose_name = 'Wegetyp gemäß Straßenreinigungssatzung ' \
                   'der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Wegetypen gemäß Straßenreinigungssatzung ' \
                          'der Hanse- und Universitätsstadt Rostock'
    description = 'Wegetypen gemäß Straßenreinigungssatzung ' \
                  'der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'wegetyp': 'Wegetyp'
    }
    ordering = ['wegetyp']

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
    verbose_name = 'Zeiteinheit'
    verbose_name_plural = 'Zeiteinheiten'
    description = 'Zeiteinheiten'
    list_fields = {
      'zeiteinheit': 'Zeiteinheit',
      'erlaeuterung': 'Erläuterung'
    }
    ordering = ['erlaeuterung']

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
    verbose_name = 'ZH-Typ innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'ZH-Typen innerhalb eines Haltestellenkatasters'
    description = 'ZH-Typen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'zh_typ': 'ZH-Typ'
    }
    ordering = ['zh_typ']

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
    verbose_name = 'Zone für einen Parkscheinautomaten'
    verbose_name_plural = 'Zonen für Parkscheinautomaten'
    description = 'Zonen für Parkscheinautomaten'
    list_fields = {
      'zone': 'Zone'
    }
    ordering = ['zone']

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
    verbose_name = 'Zustand eines Kadaverfunds'
    verbose_name_plural = 'Zustände von Kadaverfunden'
    description = 'Zustände von Kadaverfunden'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'zustand': 'Zustand'
    }
    list_fields_with_number = ['ordinalzahl']
    ordering = ['ordinalzahl']
    naming = 'zustand'

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
    verbose_name = 'Zustand eines Schutzzauns gegen eine Tierseuche'
    verbose_name_plural = 'Zustände von Schutzzäunen gegen Tierseuchen'
    description = 'Zustände von Schutzzäunen gegen Tierseuchen'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'zustand': 'Zustand'
    }
    list_fields_with_number = ['ordinalzahl']
    ordering = ['ordinalzahl']
    naming = 'zustand'

  def __str__(self):
    return str(self.zustand)


class Zustandsbewertungen(Codelist):
  """
  Zustandsbewertungen
  """

  zustandsbewertung = PositiveSmallIntegerMinField(
    'Zustandsbewertung', min_value=1, unique=True)

  class Meta(Codelist.Meta):
    db_table = 'codelisten\".\"zustandsbewertungen'
    verbose_name = 'Zustandsbewertung'
    verbose_name_plural = 'Zustandsbewertungen'
    description = 'Zustandsbewertungen'
    list_fields = {
      'zustandsbewertung': 'Zustandsbewertung'
    }
    ordering = ['zustandsbewertung']

  def __str__(self):
    return str(self.zustandsbewertung)
