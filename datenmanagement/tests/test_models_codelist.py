from django.test import TestCase

# hier: import ALLE evtl. via Liste PyCharm?
from datenmanagement.models import Adressen, Strassen, Gemeindeteile, Altersklassen_Kadaverfunde,\
  Angebote_Mobilpunkte, Angelberechtigungen, Arten_Baudenkmale, Arten_Durchlaesse,\
  Arten_FairTrade, Arten_Feldsportanlagen, Arten_Feuerwachen, Arten_Fliessgewaesser,\
  Arten_Hundetoiletten, Arten_Fallwildsuchen_Kontrollen, Arten_Meldedienst_flaechenhaft,\
  Arten_Meldedienst_punkthaft, Arten_Parkmoeglichkeiten, Arten_Pflegeeinrichtungen, Arten_Poller,\
  Arten_Toiletten, Arten_UVP_Vorpruefungen, Arten_Wege, Auftraggeber_Baustellen,\
  Ausfuehrungen_Haltestellenkataster, Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster,\
  Befestigungsarten_Warteflaeche_Haltestellenkataster, Betriebsarten, Betriebszeiten,\
  Bewirtschafter_Betreiber_Traeger_Eigentuemer, Anbieter_Carsharing,\
  E_Anschluesse_Parkscheinautomaten, Ergebnisse_UVP_Vorpruefungen,\
  Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO, Fotomotive_Haltestellenkataster,\
  Fundamenttypen_RSAG, Gebaeudebauweisen, Gebaeudefunktionen, Genehmigungsbehoerden_UVP_Vorhaben,\
  Geschlechter_Kadaverfunde, Haefen, Hersteller_Poller, Inoffizielle_Strassen,\
  Ladekarten_Ladestationen_Elektrofahrzeuge, Linien, Mastkennzeichen_RSAG, Masttypen_RSAG,\
  Masttypen_Haltestellenkataster, Materialien_Denksteine, Materialien_Durchlaesse,\
  Ordnungen_Fliessgewaesser, Personentitel, Raeumbreiten_Strassenreinigungssatzung_HRO,\
  Rechtsgrundlagen_UVP_Vorhaben, Reinigungsklassen_Strassenreinigungssatzung_HRO,\
  Reinigungsrhythmen_Strassenreinigungssatzung_HRO, Schaeden_Haltestellenkataster,\
  Schlagwoerter_Bildungstraeger, Schlagwoerter_Vereine, Schliessungen_Poller,\
  Sitzbanktypen_Haltestellenkataster, Sparten_Baustellen, Sportarten, Status_Baustellen_geplant,\
  Status_Baustellen_Fotodokumentation_Fotos, Status_Poller, Tierseuchen, Typen_Abfallbehaelter,\
  DFI_Typen_Haltestellenkataster, Fahrgastunterstandstypen_Haltestellenkataster,\
  Fahrplanvitrinentypen_Haltestellenkataster, Typen_Haltestellen, Typen_Poller,\
  Typen_UVP_Vorhaben, Verbuende_Ladestationen_Elektrofahrzeuge, Verkehrliche_Lagen_Baustellen,\
  Verkehrsmittelklassen, Vorgangsarten_UVP_Vorhaben, Wegebreiten_Strassenreinigungssatzung_HRO,\
  Wegereinigungsklassen_Strassenreinigungssatzung_HRO,\
  Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO, Wegetypen_Strassenreinigungssatzung_HRO,\
  Zeiteinheiten, ZH_Typen_Haltestellenkataster, Zonen_Parkscheinautomaten, Zustaende_Kadaverfunde,\
  Zustaende_Schutzzaeune_Tierseuchen, Zustandsbewertungen

from . import constants_vars, functions


#
# Adressen
#

class AdressenTest(TestCase):
  databases = constants_vars.DATABASES
  adresse_initial = 'Deppendorfer Str. 23a'
  adresse_updated = 'Suppenkasperweg 42'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.adresse = Adressen.objects.create(adresse=cls.adresse_initial)

  def test_create(self):
    self.assertEqual(Adressen.objects.all().count(), 1)
    adresse = Adressen.objects.get(adresse=self.adresse_initial)
    self.assertEqual(adresse, self.adresse)
    self.assertEqual(str(adresse), self.adresse_initial)

  def test_update(self):
    self.adresse.adresse = self.adresse_updated
    self.adresse.save()
    self.assertEqual(Adressen.objects.all().count(), 1)
    adresse = Adressen.objects.get(adresse=self.adresse_updated)
    self.assertEqual(adresse, self.adresse)
    self.assertEqual(str(adresse), self.adresse_updated)

  def test_delete(self):
    self.adresse.delete()
    self.assertEqual(Adressen.objects.all().count(), 0)
    self.assertFalse(Adressen.objects.filter(adresse=self.adresse_initial).exists())


#
# Straßen
#

class StrassenTest(TestCase):
  databases = constants_vars.DATABASES
  strasse_initial = 'Deppendorfer Str.'
  strasse_updated = 'Suppenkasperweg'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.strasse = Strassen.objects.create(strasse=cls.strasse_initial)

  def test_create(self):
    self.assertEqual(Strassen.objects.all().count(), 1)
    strasse = Strassen.objects.get(strasse=self.strasse_initial)
    self.assertEqual(strasse, self.strasse)
    self.assertEqual(str(strasse), self.strasse_initial)

  def test_update(self):
    self.strasse.strasse = self.strasse_updated
    self.strasse.save()
    self.assertEqual(Strassen.objects.all().count(), 1)
    strasse = Strassen.objects.get(strasse=self.strasse_updated)
    self.assertEqual(strasse, self.strasse)
    self.assertEqual(str(strasse), self.strasse_updated)

  def test_delete(self):
    self.strasse.delete()
    self.assertEqual(Strassen.objects.all().count(), 0)
    self.assertFalse(Strassen.objects.filter(strasse=self.strasse_initial).exists())


#
# Codelisten
#

# Carsharing-Anbieter

class AnbieterCarsharingTest(TestCase):
  databases = constants_vars.DATABASES
  anbieter_initial = 'Deppendorf GmbH & Co. KG'
  anbieter_updated = 'Suppenkasper AG'

  @classmethod
  def setUpTestData(cls):
    functions.load_sql_schema()
    cls.anbieter_carsharing = Anbieter_Carsharing.objects.create(anbieter=cls.anbieter_initial)

  def test_create(self):
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    anbieter_carsharing = Anbieter_Carsharing.objects.get(anbieter=self.anbieter_initial)
    self.assertEqual(anbieter_carsharing, self.anbieter_carsharing)
    self.assertEqual(str(anbieter_carsharing), self.anbieter_initial)

  def test_update(self):
    self.anbieter_carsharing.anbieter = self.anbieter_updated
    self.anbieter_carsharing.save()
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 1)
    anbieter_carsharing = Anbieter_Carsharing.objects.get(anbieter=self.anbieter_updated)
    self.assertEqual(anbieter_carsharing, self.anbieter_carsharing)
    self.assertEqual(str(anbieter_carsharing), self.anbieter_updated)

  def test_delete(self):
    self.anbieter_carsharing.delete()
    self.assertEqual(Anbieter_Carsharing.objects.all().count(), 0)
    self.assertFalse(Anbieter_Carsharing.objects.filter(anbieter=self.anbieter_initial).exists())
