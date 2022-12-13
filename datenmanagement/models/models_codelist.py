import uuid

from decimal import *
from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator

from . import constants_vars, fields


#
# abstrakte Datenmodelle für Codelisten
#

class Art(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  art = models.CharField(
    'Art',
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
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
      'art': 'Art'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['art']

  def __str__(self):
    return self.art


class Befestigungsart(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  befestigungsart = models.CharField(
    'Befestigungsart',
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
        message=constants_vars.gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
      'befestigungsart': 'Befestigungsart'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['befestigungsart']

  def __str__(self):
    return self.befestigungsart


class Material(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  material = models.CharField(
    'Material',
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
        message=constants_vars.gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
      'material': 'Material'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['material']

  def __str__(self):
    return self.material


class Schlagwort(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  schlagwort = models.CharField(
    'Schlagwort', max_length=255, validators=[
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

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
      'schlagwort': 'Schlagwort'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['schlagwort']

  def __str__(self):
    return self.schlagwort


class Status(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  status = models.CharField(
    'Status',
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
        message=constants_vars.gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
      'status': 'Status'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['status']

  def __str__(self):
    return self.status


class Typ(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  typ = models.CharField(
    'Typ',
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
        message=constants_vars.gravis_message)])

  class Meta:
    abstract = True
    managed = False
    codelist = True
    list_fields = {
      'typ': 'Typ'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['typ']

  def __str__(self):
    return self.typ


#
# Adressen
#

class Adressen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  adresse = models.CharField('Adresse', max_length=255, editable=False)

  class Meta:
    managed = False
    codelist = True
    db_table = 'basisdaten\".\"adressenliste_datenwerft'
    verbose_name = 'Adresse'
    verbose_name_plural = 'Adressen'
    description = 'Adressen in Mecklenburg-Vorpommern'
    list_fields = {
      'adresse': 'Adresse'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['adresse']

  def __str__(self):
    return self.adresse

  def save(self, *args, **kwargs):
    super(Adressen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Adressen, self).delete(*args, **kwargs)


#
# Straßen
#

class Strassen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  strasse = models.CharField('Straße', max_length=255, editable=False)

  class Meta:
    managed = False
    codelist = True
    db_table = 'basisdaten\".\"strassenliste_datenwerft'
    verbose_name = 'Straße'
    verbose_name_plural = 'Straßen'
    description = 'Straßen in Mecklenburg-Vorpommern'
    list_fields = {
      'strasse': 'Straße'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['strasse']

  def __str__(self):
    return self.strasse

  def save(self, *args, **kwargs):
    super(Strassen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Strassen, self).delete(*args, **kwargs)


#
# Gemeindeteile
#

class Gemeindeteile(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  gemeindeteil = models.CharField('Gemeindeteil', max_length=255, editable=False)

  class Meta:
    managed = False
    codelist = True
    db_table = 'basisdaten\".\"gemeindeteile_datenwerft_hro'
    verbose_name = 'Gemeindeteil'
    verbose_name_plural = 'Gemeindeteile'
    description = 'Gemeindeteile in Mecklenburg-Vorpommern'
    list_fields = {
      'gemeindeteil': 'Gemeindeteil'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['gemeindeteil']
    as_overlay = True

  def __str__(self):
    return self.gemeindeteil

  def save(self, *args, **kwargs):
    super(Gemeindeteile, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Gemeindeteile, self).delete(*args, **kwargs)


#
# Codelisten
#

# Altersklassen bei Kadaverfunden

class Altersklassen_Kadaverfunde(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ordinalzahl = fields.PositiveSmallIntegerRangeField(
    'Ordinalzahl', min_value=1)
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
      )])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"altersklassen_kadaverfunde'
    verbose_name = 'Altersklasse bei einem Kadaverfund'
    verbose_name_plural = 'Altersklassen bei Kadaverfunden'
    description = 'Altersklassen bei Kadaverfunden'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'bezeichnung': 'Bezeichnung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ordinalzahl']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Altersklassen_Kadaverfunde, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Altersklassen_Kadaverfunde, self).delete(*args, **kwargs)


# Angebote bei Mobilpunkten

class Angebote_Mobilpunkte(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  angebot = models.CharField(
    'Angebot',
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
      )])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"angebote_mobilpunkte'
    verbose_name = 'Angebot bei einem Mobilpunkt'
    verbose_name_plural = 'Angebote bei Mobilpunkten'
    description = 'Angebote bei Mobilpunkten'
    list_fields = {
      'angebot': 'Angebot'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['angebot']

  def __str__(self):
    return self.angebot

  def save(self, *args, **kwargs):
    super(Angebote_Mobilpunkte, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Angebote_Mobilpunkte, self).delete(*args, **kwargs)


# Angelberechtigungen

class Angelberechtigungen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  angelberechtigung = models.CharField(
    'Angelberechtigung',
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
      )])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"angelberechtigungen'
    verbose_name = 'Angelberechtigung'
    verbose_name_plural = 'Angelberechtigungen'
    description = 'Angelberechtigungen'
    list_fields = {
      'angelberechtigung': 'Angelberechtigung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['angelberechtigung']

  def __str__(self):
    return self.angelberechtigung

  def save(self, *args, **kwargs):
    super(Angelberechtigungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Angelberechtigungen, self).delete(*args, **kwargs)


# Arten von Baudenkmalen

class Arten_Baudenkmale(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_baudenkmale'
    verbose_name = 'Art eines Baudenkmals'
    verbose_name_plural = 'Arten von Baudenkmalen'
    description = 'Arten von Baudenkmalen'

  def save(self, *args, **kwargs):
    super(Arten_Baudenkmale, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Baudenkmale, self).delete(*args, **kwargs)


# Arten von Durchlässen

class Arten_Durchlaesse(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_durchlaesse'
    verbose_name = 'Art eines Durchlasses'
    verbose_name_plural = 'Arten von Durchlässen'
    description = 'Arten von Durchlässen'

  def save(self, *args, **kwargs):
    super(Arten_Durchlaesse, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Durchlaesse, self).delete(*args, **kwargs)


# Arten von Fair-Trade-Einrichtungen

class Arten_FairTrade(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fairtrade'
    verbose_name = 'Art einer Fair-Trade-Einrichtung'
    verbose_name_plural = 'Arten von Fair-Trade-Einrichtungen'
    description = 'Arten von Fair-Trade-Einrichtungen'

  def save(self, *args, **kwargs):
    super(Arten_FairTrade, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_FairTrade, self).delete(*args, **kwargs)


# Arten von Feldsportanlagen

class Arten_Feldsportanlagen(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_feldsportanlagen'
    verbose_name = 'Art einer Feldsportanlage'
    verbose_name_plural = 'Arten von Feldsportanlagen'
    description = 'Arten von Feldsportanlagen'

  def save(self, *args, **kwargs):
    super(Arten_Feldsportanlagen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Feldsportanlagen, self).delete(*args, **kwargs)


# Arten von Feuerwachen

class Arten_Feuerwachen(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_feuerwachen'
    verbose_name = 'Art einer Feuerwache'
    verbose_name_plural = 'Arten von Feuerwachen'
    description = 'Arten von Feuerwachen'

  def save(self, *args, **kwargs):
    super(Arten_Feuerwachen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Feuerwachen, self).delete(*args, **kwargs)


# Arten von Fließgewässern

class Arten_Fliessgewaesser(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fliessgewaesser'
    verbose_name = 'Art eines Fließgewässers'
    verbose_name_plural = 'Arten von Fließgewässern'
    description = 'Arten von Fließgewässern'

  def save(self, *args, **kwargs):
    super(Arten_Fliessgewaesser, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Fliessgewaesser, self).delete(*args, **kwargs)


# Arten von Hundetoiletten

class Arten_Hundetoiletten(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_hundetoiletten'
    verbose_name = 'Art einer Hundetoilette'
    verbose_name_plural = 'Arten von Hundetoiletten'
    description = 'Arten von Hundetoiletten'

  def save(self, *args, **kwargs):
    super(Arten_Hundetoiletten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Hundetoiletten, self).delete(*args, **kwargs)


# Arten von Kontrollen im Rahmen von Fallwildsuchen

class Arten_Fallwildsuchen_Kontrollen(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_fallwildsuchen_kontrollen'
    verbose_name = 'Art einer Kontrolle im Rahmen einer Fallwildsuche'
    verbose_name_plural = 'Arten von Kontrollen im Rahmen von Fallwildsuchen'
    description = 'Arten von Kontrollen im Rahmen von Fallwildsuchen'

  def save(self, *args, **kwargs):
    super(Arten_Fallwildsuchen_Kontrollen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Fallwildsuchen_Kontrollen, self).delete(*args, **kwargs)


# Arten von Meldediensten (flächenhaft)

class Arten_Meldedienst_flaechenhaft(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_meldedienst_flaechenhaft'
    verbose_name = 'Art eines Meldedienstes (flächenhaft)'
    verbose_name_plural = 'Arten von Meldediensten (flächenhaft)'
    description = 'Arten von Meldediensten (flächenhaft)'

  def save(self, *args, **kwargs):
    super(Arten_Meldedienst_flaechenhaft, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Meldedienst_flaechenhaft, self).delete(*args, **kwargs)


# Arten von Meldediensten (punkthaft)

class Arten_Meldedienst_punkthaft(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_meldedienst_punkthaft'
    verbose_name = 'Art eines Meldedienstes (punkthaft)'
    verbose_name_plural = 'Arten von Meldediensten (punkthaft)'
    description = 'Arten von Meldediensten (punkthaft)'

  def save(self, *args, **kwargs):
    super(Arten_Meldedienst_punkthaft, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Meldedienst_punkthaft, self).delete(*args, **kwargs)


# Arten von Parkmöglichkeiten

class Arten_Parkmoeglichkeiten(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_parkmoeglichkeiten'
    verbose_name = 'Art einer Parkmöglichkeit'
    verbose_name_plural = 'Arten von Parkmöglichkeiten'
    description = 'Arten von Parkmöglichkeiten'

  def save(self, *args, **kwargs):
    super(Arten_Parkmoeglichkeiten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Parkmoeglichkeiten, self).delete(*args, **kwargs)


# Arten von Pflegeeinrichtungen

class Arten_Pflegeeinrichtungen(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_pflegeeinrichtungen'
    verbose_name = 'Art einer Pflegeeinrichtung'
    verbose_name_plural = 'Arten von Pflegeeinrichtungen'
    description = 'Arten von Pflegeeinrichtungen'

  def save(self, *args, **kwargs):
    super(Arten_Pflegeeinrichtungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Pflegeeinrichtungen, self).delete(*args, **kwargs)


# Arten von Pollern

class Arten_Poller(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_poller'
    verbose_name = 'Art eines Pollers'
    verbose_name_plural = 'Arten von Pollern'
    description = 'Arten von Pollern'

  def save(self, *args, **kwargs):
    super(Arten_Poller, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Poller, self).delete(*args, **kwargs)


# Arten von Toiletten

class Arten_Toiletten(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_toiletten'
    verbose_name = 'Art einer Toilette'
    verbose_name_plural = 'Arten von Toiletten'
    description = 'Arten von Toiletten'

  def save(self, *args, **kwargs):
    super(Arten_Toiletten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Toiletten, self).delete(*args, **kwargs)


# Arten von UVP-Vorprüfungen

class Arten_UVP_Vorpruefungen(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_uvp_vorpruefungen'
    verbose_name = 'Art einer UVP-Vorprüfung'
    verbose_name_plural = 'Arten von UVP-Vorprüfungen'
    description = 'Arten von UVP-Vorprüfungen'

  def save(self, *args, **kwargs):
    super(Arten_UVP_Vorpruefungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_UVP_Vorpruefungen, self).delete(*args, **kwargs)


# Arten von Wegen

class Arten_Wege(Art):
  class Meta(Art.Meta):
    db_table = 'codelisten\".\"arten_wege'
    verbose_name = 'Art eines Weges'
    verbose_name_plural = 'Arten von Wegen'
    description = 'Arten von Wegen'

  def save(self, *args, **kwargs):
    super(Arten_Wege, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Arten_Wege, self).delete(*args, **kwargs)


# Auftraggeber von Baustellen

class Auftraggeber_Baustellen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  auftraggeber = models.CharField(
    'Auftraggeber',
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
      )])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"auftraggeber_baustellen'
    verbose_name = 'Auftraggeber einer Baustelle'
    verbose_name_plural = 'Auftraggeber von Baustellen'
    description = 'Auftraggeber von Baustellen'
    list_fields = {
      'auftraggeber': 'Auftraggeber'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['auftraggeber']

  def __str__(self):
    return self.auftraggeber

  def save(self, *args, **kwargs):
    super(Auftraggeber_Baustellen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Auftraggeber_Baustellen, self).delete(*args, **kwargs)


# Ausführungen innerhalb eines Haltestellenkatasters

class Ausfuehrungen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ausfuehrung = models.CharField(
    'Ausführung', max_length=255, validators=[
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"ausfuehrungen_haltestellenkataster'
    verbose_name = 'Ausführung innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Ausführungen innerhalb eines Haltestellenkatasters'
    description = 'Ausführungen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'ausfuehrung': 'Ausführung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ausfuehrung']

  def __str__(self):
    return self.ausfuehrung

  def save(self, *args, **kwargs):
    super(Ausfuehrungen_Haltestellenkataster, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Ausfuehrungen_Haltestellenkataster, self).delete(*args, **kwargs)


# Befestigungsarten der Aufstellfläche Bus innerhalb eines
# Haltestellenkatasters

class Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster(Befestigungsart):
  class Meta(Befestigungsart.Meta):
    db_table = 'codelisten\".\"befestigungsarten_aufstellflaeche_bus_haltestellenkataster'
    verbose_name = 'Befestigungsart der Aufstellfläche Bus innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Befestigungsarten der Aufstellfläche Bus innerhalb eines ' \
                          'Haltestellenkatasters'
    description = 'Befestigungsarten der Aufstellfläche Bus innerhalb eines Haltestellenkatasters'

  def save(self, *args, **kwargs):
    super(
      Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster,
      self).save(
      *
      args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Befestigungsarten_Aufstellflaeche_Bus_Haltestellenkataster,
      self).delete(
      *
      args,
      **kwargs)


# Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters

class Befestigungsarten_Warteflaeche_Haltestellenkataster(Befestigungsart):
  class Meta(Befestigungsart.Meta):
    db_table = 'codelisten\".\"befestigungsarten_warteflaeche_haltestellenkataster'
    verbose_name = 'Befestigungsart der Wartefläche innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters'
    description = 'Befestigungsarten der Wartefläche innerhalb eines Haltestellenkatasters'

  def save(self, *args, **kwargs):
    super(
      Befestigungsarten_Warteflaeche_Haltestellenkataster,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Befestigungsarten_Warteflaeche_Haltestellenkataster,
      self).delete(
      *args,
      **kwargs)


# Betriebsarten

class Betriebsarten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  betriebsart = models.CharField(
    'Betriebsart', max_length=255, validators=[
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"betriebsarten'
    verbose_name = 'Betriebsart'
    verbose_name_plural = 'Betriebsarten'
    description = 'Betriebsarten'
    list_fields = {
      'betriebsart': 'Betriebsart'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['betriebsart']

  def __str__(self):
    return self.betriebsart

  def save(self, *args, **kwargs):
    super(Betriebsarten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Betriebsarten, self).delete(*args, **kwargs)


# Betriebszeiten

class Betriebszeiten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  betriebszeit = models.CharField(
    'Betriebszeit', max_length=255, validators=[
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"betriebszeiten'
    verbose_name = 'Betriebszeit'
    verbose_name_plural = 'Betriebszeiten'
    description = 'Betriebszeiten'
    list_fields = {
      'betriebszeit': 'Betriebszeit'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['betriebszeit']

  def __str__(self):
    return self.betriebszeit

  def save(self, *args, **kwargs):
    super(Betriebszeiten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Betriebszeiten, self).delete(*args, **kwargs)


# Bewirtschafter, Betreiber, Träger, Eigentümer etc.

class Bewirtschafter_Betreiber_Traeger_Eigentuemer(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  bezeichnung = models.CharField(
    'Bezeichnung', max_length=255, validators=[
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
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message
      )])
  art = models.CharField(
    'Art', max_length=255, validators=[
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
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message
      )])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"bewirtschafter_betreiber_traeger_eigentuemer'
    verbose_name = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    verbose_name_plural = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    description = 'Bewirtschafter, Betreiber, Träger, Eigentümer etc.'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'art': 'Art'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(
      Bewirtschafter_Betreiber_Traeger_Eigentuemer,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Bewirtschafter_Betreiber_Traeger_Eigentuemer,
      self).delete(
      *args,
      **kwargs)


# Carsharing-Anbieter

class Anbieter_Carsharing(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  anbieter = models.CharField(
    'Anbieter', max_length=255, validators=[
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
        regex=constants_vars.gravis_regex, message=constants_vars.gravis_message
      )])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"anbieter_carsharing'
    verbose_name = 'Carsharing-Anbieter'
    verbose_name_plural = 'Carsharing-Anbieter'
    description = 'Carsharing-Anbieter'
    list_fields = {
      'anbieter': 'Anbieter'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['anbieter']

  def __str__(self):
    return self.anbieter

  def save(self, *args, **kwargs):
    super(Anbieter_Carsharing, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Anbieter_Carsharing, self).delete(*args, **kwargs)


# E-Anschlüsse für Parkscheinautomaten

class E_Anschluesse_Parkscheinautomaten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  e_anschluss = models.CharField(
    'E-Anschluss',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"e_anschluesse_parkscheinautomaten'
    verbose_name = 'E-Anschluss für einen Parkscheinautomaten'
    verbose_name_plural = 'E-Anschlüsse für Parkscheinautomaten'
    description = 'E-Anschlüsse für Parkscheinautomaten'
    list_fields = {
      'e_anschluss': 'E-Anschluss'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['e_anschluss']

  def __str__(self):
    return self.e_anschluss

  def save(self, *args, **kwargs):
    super(E_Anschluesse_Parkscheinautomaten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(E_Anschluesse_Parkscheinautomaten, self).delete(*args, **kwargs)


# Ergebnisse von UVP-Vorprüfungen

class Ergebnisse_UVP_Vorpruefungen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ergebnis = models.CharField(
    'Ergebnis',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"ergebnisse_uvp_vorpruefungen'
    verbose_name = 'Ergebnis einer UVP-Vorprüfung'
    verbose_name_plural = 'Ergebnisse von UVP-Vorprüfungen'
    description = 'Ergebnisse von UVP-Vorprüfungen'
    list_fields = {
      'ergebnis': 'Ergebnis'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ergebnis']

  def __str__(self):
    return self.ergebnis

  def save(self, *args, **kwargs):
    super(Ergebnisse_UVP_Vorpruefungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Ergebnisse_UVP_Vorpruefungen, self).delete(*args, **kwargs)


# Fahrbahnwinterdienst gemäß Straßenreinigungssatzung der Hanse- und
# Universitätsstadt Rostock

class Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  code = models.CharField(
    'Code',
    max_length=1,
    validators=[
      RegexValidator(
        regex=constants_vars.fw_sr_code_regex,
        message=constants_vars.fw_sr_code_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"fahrbahnwinterdienst_strassenreinigungssatzung_hro'
    verbose_name = 'Fahrbahnwinterdienst gemäß Straßenreinigungssatzung der Hanse- und ' \
                   'Universitätsstadt Rostock'
    verbose_name_plural = 'Fahrbahnwinterdienst gemäß Straßenreinigungssatzung der Hanse- und ' \
                          'Universitätsstadt Rostock'
    description = 'Fahrbahnwinterdienst gemäß Straßenreinigungssatzung der Hanse- und ' \
                  'Universitätsstadt Rostock'
    list_fields = {
      'code': 'Code'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['code']

  def __str__(self):
    return self.code

  def save(self, *args, **kwargs):
    super(
      Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Fahrbahnwinterdienst_Strassenreinigungssatzung_HRO,
      self).delete(
      *args,
      **kwargs)


# Fotomotive innerhalb eines Haltestellenkatasters

class Fotomotive_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  fotomotiv = models.CharField(
    'Fotomotiv',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"fotomotive_haltestellenkataster'
    verbose_name = 'Fotomotiv innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Fotomotive innerhalb eines Haltestellenkatasters'
    description = 'Fotomotive innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fotomotiv': 'Fotomotiv'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['fotomotiv']

  def __str__(self):
    return self.fotomotiv

  def save(self, *args, **kwargs):
    super(Fotomotive_Haltestellenkataster, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Fotomotive_Haltestellenkataster, self).delete(*args, **kwargs)


# Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur
# der Rostocker Straßenbahn AG

class Fundamenttypen_RSAG(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  typ = models.CharField(
    'Typ',
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

  erlaeuterung = models.CharField(
    'Erläuterung',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"fundamenttypen_rsag'
    verbose_name = 'Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur der ' \
                   'Rostocker Straßenbahn AG'
    verbose_name_plural = 'Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur der ' \
                          'Rostocker Straßenbahn AG'
    description = 'Fundamenttypen für Masten innerhalb der Straßenbahninfrastruktur der ' \
                  'Rostocker Straßenbahn AG'
    list_fields = {
      'typ': 'Typ',
      'erlaeuterung': 'Erläuterung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['typ']

  def __str__(self):
    return self.typ

  def save(self, *args, **kwargs):
    super(Fundamenttypen_RSAG, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Fundamenttypen_RSAG, self).delete(*args, **kwargs)


# Gebäudebauweisen

class Gebaeudebauweisen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  code = fields.PositiveSmallIntegerRangeField(
    'Code', min_value=1, blank=True, null=True)
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"gebaeudebauweisen'
    verbose_name = 'Gebäudebauweise'
    verbose_name_plural = 'Gebäudebauweisen'
    description = 'Gebäudebauweisen'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'code': 'Code'
    }
    list_fields_with_number = ['code']
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Gebaeudebauweisen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Gebaeudebauweisen, self).delete(*args, **kwargs)


# Gebäudefunktionen

class Gebaeudefunktionen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  code = fields.PositiveSmallIntegerRangeField(
    'Code', min_value=1, blank=True, null=True)
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"gebaeudefunktionen'
    verbose_name = 'Gebäudefunktion'
    verbose_name_plural = 'Gebäudefunktionen'
    description = 'Gebäudefunktionen'
    list_fields = {
      'bezeichnung': 'Bezeichnung',
      'code': 'Code'
    }
    list_fields_with_number = ['code']
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Gebaeudefunktionen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Gebaeudefunktionen, self).delete(*args, **kwargs)


# Genehmigungsbehörden von UVP-Vorhaben

class Genehmigungsbehoerden_UVP_Vorhaben(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  genehmigungsbehoerde = models.CharField(
    'Genehmigungsbehörde',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"genehmigungsbehoerden_uvp_vorhaben'
    verbose_name = 'Genehmigungsbehörde eines UVP-Vorhabens'
    verbose_name_plural = 'Genehmigungsbehörden von UVP-Vorhaben'
    description = 'Genehmigungsbehörden von UVP-Vorhaben'
    list_fields = {
      'genehmigungsbehoerde': 'Genehmigungsbehörde'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['genehmigungsbehoerde']

  def __str__(self):
    return self.genehmigungsbehoerde

  def save(self, *args, **kwargs):
    super(Genehmigungsbehoerden_UVP_Vorhaben, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Genehmigungsbehoerden_UVP_Vorhaben, self).delete(*args, **kwargs)


# Geschlechter bei Kadaverfunden

class Geschlechter_Kadaverfunde(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ordinalzahl = fields.PositiveSmallIntegerRangeField(
    'Ordinalzahl', min_value=1)
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
      )])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"geschlechter_kadaverfunde'
    verbose_name = 'Geschlecht bei einem Kadaverfund'
    verbose_name_plural = 'Geschlechter bei Kadaverfunden'
    description = 'Geschlechter bei Kadaverfunden'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'bezeichnung': 'Bezeichnung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ordinalzahl']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Geschlechter_Kadaverfunde, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Geschlechter_Kadaverfunde, self).delete(*args, **kwargs)


# Häfen

class Haefen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
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
  abkuerzung = models.CharField(
    'Abkürzung',
    max_length=5,
    validators=[
      RegexValidator(
        regex=constants_vars.haef_abkuerzung_regex,
        message=constants_vars.haef_abkuerzung_message)])
  code = fields.PositiveSmallIntegerRangeField(
    'Code', min_value=1, blank=True, null=True)

  class Meta:
    managed = False
    codelist = True
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
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Haefen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Haefen, self).delete(*args, **kwargs)


# Hersteller von Pollern

class Hersteller_Poller(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"hersteller_poller'
    verbose_name = 'Hersteller eines Pollers'
    verbose_name_plural = 'Hersteller von Pollern'
    description = 'Hersteller von Pollern'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Hersteller_Poller, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Hersteller_Poller, self).delete(*args, **kwargs)


# inoffizielle Straßen

class Inoffizielle_Strassen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  strasse = models.CharField('Straße', max_length=255, editable=False)

  class Meta:
    managed = False
    codelist = True
    db_table = 'basisdaten\".\"inoffizielle_strassenliste_datenwerft_hro'
    verbose_name = 'Inoffizielle Straße der Hanse- und Universitätsstadt Rostock'
    verbose_name_plural = 'Inoffizielle Straßen der Hanse- und Universitätsstadt Rostock'
    description = 'Inoffizielle Straßen der Hanse- und Universitätsstadt Rostock'
    list_fields = {
      'strasse': 'Straße'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['strasse']

  def __str__(self):
    return self.strasse

  def save(self, *args, **kwargs):
    super(Inoffizielle_Strassen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Inoffizielle_Strassen, self).delete(*args, **kwargs)


# Ladekarten für Ladestationen für Elektrofahrzeuge

class Ladekarten_Ladestationen_Elektrofahrzeuge(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ladekarte = models.CharField(
    'Ladekarte',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"ladekarten_ladestationen_elektrofahrzeuge'
    verbose_name = 'Ladekarte für eine Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Ladekarten für Ladestationen für Elektrofahrzeuge'
    description = 'Ladekarten für Ladestationen für Elektrofahrzeuge'
    list_fields = {
      'ladekarte': 'Ladekarte'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ladekarte']

  def __str__(self):
    return self.ladekarte

  def save(self, *args, **kwargs):
    super(
      Ladekarten_Ladestationen_Elektrofahrzeuge,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Ladekarten_Ladestationen_Elektrofahrzeuge,
      self).delete(
      *args,
      **kwargs)


# Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH

class Linien(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  linie = models.CharField(
    'Linie',
    max_length=4,
    validators=[
      RegexValidator(
        regex=constants_vars.lin_linie_regex,
        message=constants_vars.lin_linie_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"linien'
    verbose_name = 'Linie der Rostocker Straßenbahn AG und/oder der Regionalbus Rostock GmbH'
    verbose_name_plural = 'Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH'
    description = 'Linien der Rostocker Straßenbahn AG und der Regionalbus Rostock GmbH'
    list_fields = {
      'linie': 'Linie'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['linie']

  def __str__(self):
    return self.linie

  def save(self, *args, **kwargs):
    super(Linien, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Linien, self).delete(*args, **kwargs)


# Mastkennzeichen innerhalb der Straßenbahninfrastruktur
# der Rostocker Straßenbahn AG

class Mastkennzeichen_RSAG(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  kennzeichen = models.CharField(
    'Kennzeichen',
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

  erlaeuterung = models.CharField(
    'Erläuterung',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"mastkennzeichen_rsag'
    verbose_name = 'Mastkennzeichen innerhalb der Straßenbahninfrastruktur der Rostocker ' \
                   'Straßenbahn AG'
    verbose_name_plural = 'Mastkennzeichen innerhalb der Straßenbahninfrastruktur der Rostocker ' \
                          'Straßenbahn AG'
    description = 'Mastkennzeichen innerhalb der Straßenbahninfrastruktur der Rostocker ' \
                  'Straßenbahn AG'
    list_fields = {
      'kennzeichen': 'Kennzeichen',
      'erlaeuterung': 'Erläuterung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['kennzeichen']

  def __str__(self):
    return self.erlaeuterung + ' (' + self.kennzeichen + ')'

  def save(self, *args, **kwargs):
    super(Mastkennzeichen_RSAG, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Mastkennzeichen_RSAG, self).delete(*args, **kwargs)


# Masttypen innerhalb der Straßenbahninfrastruktur
# der Rostocker Straßenbahn AG

class Masttypen_RSAG(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  typ = models.CharField(
    'Typ',
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

  erlaeuterung = models.CharField(
    'Erläuterung',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"masttypen_rsag'
    verbose_name = 'Masttyp innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG'
    verbose_name_plural = 'Masttypen innerhalb der Straßenbahninfrastruktur der Rostocker ' \
                          'Straßenbahn AG'
    description = 'Masttypen innerhalb der Straßenbahninfrastruktur der Rostocker Straßenbahn AG'
    list_fields = {
      'typ': 'Typ',
      'erlaeuterung': 'Erläuterung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['typ']

  def __str__(self):
    return self.typ

  def save(self, *args, **kwargs):
    super(Masttypen_RSAG, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Masttypen_RSAG, self).delete(*args, **kwargs)


# Masttypen innerhalb eines Haltestellenkatasters

class Masttypen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  masttyp = models.CharField(
    'Masttyp',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"masttypen_haltestellenkataster'
    verbose_name = 'Masttyp innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Masttypen innerhalb eines Haltestellenkatasters'
    description = 'Masttypen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'masttyp': 'Masttyp'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['masttyp']

  def __str__(self):
    return self.masttyp

  def save(self, *args, **kwargs):
    super(Masttypen_Haltestellenkataster, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Masttypen_Haltestellenkataster, self).delete(*args, **kwargs)


# Materialien von Denksteinen

class Materialien_Denksteine(Material):
  class Meta(Material.Meta):
    db_table = 'codelisten\".\"materialien_denksteine'
    verbose_name = 'Material eines Denksteins'
    verbose_name_plural = 'Materialien von Denksteinen'
    description = 'Materialien von Denksteinen'

  def save(self, *args, **kwargs):
    super(Materialien_Denksteine, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Materialien_Denksteine, self).delete(*args, **kwargs)


# Materialien von Durchlässen

class Materialien_Durchlaesse(Material):
  class Meta(Material.Meta):
    db_table = 'codelisten\".\"materialien_durchlaesse'
    verbose_name = 'Material eines Durchlasses'
    verbose_name_plural = 'Materialien von Durchlässen'
    description = 'Materialien von Durchlässen'

  def save(self, *args, **kwargs):
    super(Materialien_Durchlaesse, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Materialien_Durchlaesse, self).delete(*args, **kwargs)


# Ordnungen von Fließgewässern

class Ordnungen_Fliessgewaesser(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ordnung = fields.PositiveSmallIntegerMinField('Ordnung', min_value=1)

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"ordnungen_fliessgewaesser'
    verbose_name = 'Ordnung eines Fließgewässers'
    verbose_name_plural = 'Ordnungen von Fließgewässern'
    description = 'Ordnungen von Fließgewässern'
    list_fields = {
      'ordnung': 'Ordnung'
    }
    list_fields_with_number = ['ordnung']
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ordnung']

  def __str__(self):
    return str(self.ordnung)

  def save(self, *args, **kwargs):
    super(Ordnungen_Fliessgewaesser, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Ordnungen_Fliessgewaesser, self).delete(*args, **kwargs)


# Personentitel

class Personentitel(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"personentitel'
    verbose_name = 'Personentitel'
    verbose_name_plural = 'Personentitel'
    description = 'Personentitel'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Personentitel, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Personentitel, self).delete(*args, **kwargs)


# Quartiere

class Quartiere(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  code = models.CharField(
    'Code',
    max_length=3,
    validators=[
      RegexValidator(
        regex=constants_vars.quar_code_regex,
        message=constants_vars.quar_code_message)])
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"quartiere'
    verbose_name = 'Quartier'
    verbose_name_plural = 'Quartiere'
    description = 'Quartiere'
    list_fields = {
      'code': 'Code',
      'bezeichnung': 'Bezeichnung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['code']

  def __str__(self):
    return str(self.code)

  def save(self, *args, **kwargs):
    super(Quartiere, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Quartiere, self).delete(*args, **kwargs)


# Räumbreiten gemäß Straßenreinigungssatzung der Hanse- und
# Universitätsstadt Rostock

class Raeumbreiten_Strassenreinigungssatzung_HRO(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  raeumbreite = models.DecimalField(
    'Räumbreite (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Räumbreite</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Räumbreite</em></strong> darf höchstens 99,99 m betragen.')])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"raeumbreiten_strassenreinigungssatzung_hro'
    verbose_name = 'Räumbreite gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt ' \
                   'Rostock'
    verbose_name_plural = 'Räumbreiten gemäß Straßenreinigungssatzung der Hanse- und ' \
                          'Universitätsstadt Rostock'
    description = 'Räumbreiten gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt ' \
                  'Rostock'
    list_fields = {
      'raeumbreite': 'Räumbreite'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['raeumbreite']

  def __str__(self):
    return str(self.raeumbreite)

  def save(self, *args, **kwargs):
    super(
      Raeumbreiten_Strassenreinigungssatzung_HRO,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Raeumbreiten_Strassenreinigungssatzung_HRO,
      self).delete(
      *args,
      **kwargs)


# Rechtsgrundlagen von UVP-Vorhaben

class Rechtsgrundlagen_UVP_Vorhaben(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  rechtsgrundlage = models.CharField(
    'Rechtsgrundlage',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"rechtsgrundlagen_uvp_vorhaben'
    verbose_name = 'Rechtsgrundlage eines UVP-Vorhabens'
    verbose_name_plural = 'Rechtsgrundlagen von UVP-Vorhaben'
    description = 'Rechtsgrundlagen von UVP-Vorhaben'
    list_fields = {
      'rechtsgrundlage': 'Rechtsgrundlage'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['rechtsgrundlage']

  def __str__(self):
    return self.rechtsgrundlage

  def save(self, *args, **kwargs):
    super(Rechtsgrundlagen_UVP_Vorhaben, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Rechtsgrundlagen_UVP_Vorhaben, self).delete(*args, **kwargs)


# Reinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und
# Universitätsstadt Rostock

class Reinigungsklassen_Strassenreinigungssatzung_HRO(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  code = fields.PositiveSmallIntegerRangeField(
    'Code', min_value=1, max_value=7)

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"reinigungsklassen_strassenreinigungssatzung_hro'
    verbose_name = 'Reinigungsklasse gemäß Straßenreinigungssatzung der Hanse- und ' \
                   'Universitätsstadt Rostock'
    verbose_name_plural = 'Reinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und ' \
                          'Universitätsstadt Rostock'
    description = 'Reinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und ' \
                  'Universitätsstadt Rostock'
    list_fields = {
      'code': 'Code'
    }
    list_fields_with_number = ['code']
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['code']

  def __str__(self):
    return str(self.code)

  def save(self, *args, **kwargs):
    super(
      Reinigungsklassen_Strassenreinigungssatzung_HRO,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Reinigungsklassen_Strassenreinigungssatzung_HRO,
      self).delete(
      *args,
      **kwargs)


# Reinigungsrhythmen gemäß Straßenreinigungssatzung der Hanse- und
# Universitätsstadt Rostock

class Reinigungsrhythmen_Strassenreinigungssatzung_HRO(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ordinalzahl = fields.PositiveSmallIntegerRangeField(
    'Ordinalzahl', min_value=1)
  reinigungsrhythmus = models.CharField(
    'Reinigungsrhythmus',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"reinigungsrhythmen_strassenreinigungssatzung_hro'
    verbose_name = 'Reinigungsrhythmus gemäß Straßenreinigungssatzung der Hanse- und ' \
                   'Universitätsstadt Rostock'
    verbose_name_plural = 'Reinigungsrhythmen gemäß Straßenreinigungssatzung der Hanse- und ' \
                          'Universitätsstadt Rostock'
    description = 'Reinigungsrhythmen gemäß Straßenreinigungssatzung der Hanse- und ' \
                  'Universitätsstadt Rostock'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'reinigungsrhythmus': 'Reinigungsrhythmus'
    }
    list_fields_with_number = ['ordinalzahl']
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ordinalzahl']

  def __str__(self):
    return str(self.reinigungsrhythmus)

  def save(self, *args, **kwargs):
    super(
      Reinigungsrhythmen_Strassenreinigungssatzung_HRO,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Reinigungsrhythmen_Strassenreinigungssatzung_HRO,
      self).delete(
      *args,
      **kwargs)


# Schäden innerhalb eines Haltestellenkatasters

class Schaeden_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  schaden = models.CharField(
    'Schaden',
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

  class Meta:
    managed = False  # Django kümmert sich nicht
    codelist = True
    db_table = 'codelisten\".\"schaeden_haltestellenkataster'
    verbose_name = 'Schaden innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Schäden innerhalb eines Haltestellenkatasters'
    description = 'Schäden innerhalb eines Haltestellenkatasters'
    list_fields = {
      'schaden': 'Schaden'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['schaden']

  def __str__(self):
    return self.schaden

  def save(self, *args, **kwargs):
    super(Schaeden_Haltestellenkataster, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Schaeden_Haltestellenkataster, self).delete(*args, **kwargs)


# Schlagwörter für Bildungsträger

class Schlagwoerter_Bildungstraeger(Schlagwort):
  class Meta(Schlagwort.Meta):
    db_table = 'codelisten\".\"schlagwoerter_bildungstraeger'
    verbose_name = 'Schlagwort für einen Bildungsträger'
    verbose_name_plural = 'Schlagwörter für Bildungsträger'
    description = 'Schlagwörter für Bildungsträger'

  def save(self, *args, **kwargs):
    super(Schlagwoerter_Bildungstraeger, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Schlagwoerter_Bildungstraeger, self).delete(*args, **kwargs)


# Schlagwörter für Vereine

class Schlagwoerter_Vereine(Schlagwort):
  class Meta(Schlagwort.Meta):
    db_table = 'codelisten\".\"schlagwoerter_vereine'
    verbose_name = 'Schlagwort für einen Verein'
    verbose_name_plural = 'Schlagwörter für Vereine'
    description = 'Schlagwörter für Vereine'

  def save(self, *args, **kwargs):
    super(Schlagwoerter_Vereine, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Schlagwoerter_Vereine, self).delete(*args, **kwargs)


# Schließungen von Pollern

class Schliessungen_Poller(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  schliessung = models.CharField(
    'Schließung',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"schliessungen_poller'
    verbose_name = 'Schließung eines Pollers'
    verbose_name_plural = 'Schließungen von Pollern'
    description = 'Schließungen von Pollern'
    list_fields = {
      'schliessung': 'Schließung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['schliessung']

  def __str__(self):
    return self.schliessung

  def save(self, *args, **kwargs):
    super(Schliessungen_Poller, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Schliessungen_Poller, self).delete(*args, **kwargs)


# Sitzbanktypen innerhalb eines Haltestellenkatasters

class Sitzbanktypen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  sitzbanktyp = models.CharField(
    'Sitzbanktyp',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"sitzbanktypen_haltestellenkataster'
    verbose_name = 'Sitzbanktyp innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Sitzbanktypen innerhalb eines Haltestellenkatasters'
    description = 'Sitzbanktypen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'sitzbanktyp': 'Sitzbanktyp'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['sitzbanktyp']

  def __str__(self):
    return self.sitzbanktyp

  def save(self, *args, **kwargs):
    super(Sitzbanktypen_Haltestellenkataster, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Sitzbanktypen_Haltestellenkataster, self).delete(*args, **kwargs)


# Sparten von Baustellen

class Sparten_Baustellen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  sparte = models.CharField(
    'Sparte',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"sparten_baustellen'
    verbose_name = 'Sparte einer Baustelle'
    verbose_name_plural = 'Sparten von Baustellen'
    description = 'Sparten von Baustellen'
    list_fields = {
      'sparte': 'Sparte'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['sparte']

  def __str__(self):
    return self.sparte

  def save(self, *args, **kwargs):
    super(Sparten_Baustellen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Sparten_Baustellen, self).delete(*args, **kwargs)


# Sportarten

class Sportarten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"sportarten'
    verbose_name = 'Sportart'
    verbose_name_plural = 'Sportarten'
    description = 'Sportarten'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Sportarten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Sportarten, self).delete(*args, **kwargs)


# Status von Baustellen (geplant)

class Status_Baustellen_geplant(Status):
  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_baustellen_geplant'
    verbose_name = 'Status einer Baustelle (geplant)'
    verbose_name_plural = 'Status von Baustellen (geplant)'
    description = 'Status von Baustellen (geplant)'

  def save(self, *args, **kwargs):
    super(Status_Baustellen_geplant, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Status_Baustellen_geplant, self).delete(*args, **kwargs)


# Status von Fotos der Baustellen-Fotodokumentation

class Status_Baustellen_Fotodokumentation_Fotos(Status):
  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_baustellen_fotodokumentation_fotos'
    verbose_name = 'Status eines Fotos der Baustellen-Fotodokumentation'
    verbose_name_plural = 'Status von Fotos der Baustellen-Fotodokumentation'
    description = 'Status von Fotos der Baustellen-Fotodokumentation'

  def save(self, *args, **kwargs):
    super(
      Status_Baustellen_Fotodokumentation_Fotos,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Status_Baustellen_Fotodokumentation_Fotos,
      self).delete(
      *args,
      **kwargs)


# Status von Pollern

class Status_Poller(Status):
  class Meta(Status.Meta):
    db_table = 'codelisten\".\"status_poller'
    verbose_name = 'Status eines Pollers'
    verbose_name_plural = 'Status von Pollern'
    description = 'Status von Pollern'

  def save(self, *args, **kwargs):
    super(Status_Poller, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Status_Poller, self).delete(*args, **kwargs)


# Tierseuchen

class Tierseuchen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  bezeichnung = models.CharField(
    'Bezeichnung', max_length=255, validators=[
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"tierseuchen'
    verbose_name = 'Tierseuche'
    verbose_name_plural = 'Tierseuchen'
    description = 'Tierseuchen'
    list_fields = {
      'bezeichnung': 'Bezeichnung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['bezeichnung']

  def __str__(self):
    return self.bezeichnung

  def save(self, *args, **kwargs):
    super(Tierseuchen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Tierseuchen, self).delete(*args, **kwargs)


# Typen von Abfallbehältern

class Typen_Abfallbehaelter(Typ):
  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_abfallbehaelter'
    verbose_name = 'Typ eines Abfallbehälters'
    verbose_name_plural = 'Typen von Abfallbehältern'
    description = 'Typen von Abfallbehältern'

  def save(self, *args, **kwargs):
    super(Typen_Abfallbehaelter, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Typen_Abfallbehaelter, self).delete(*args, **kwargs)


# Typen von Dynamischen Fahrgastinformationssystemen innerhalb eines
# Haltestellenkatasters

class DFI_Typen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  dfi_typ = models.CharField(
    'DFI-Typ',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"dfi_typen_haltestellenkataster'
    verbose_name = 'Typ eines Dynamischen Fahrgastinformationssystems innerhalb eines ' \
                   'Haltestellenkatasters'
    verbose_name_plural = 'Typen von Dynamischen Fahrgastinformationssystemen innerhalb eines ' \
                          'Haltestellenkatasters'
    description = 'Typen von Dynamischen Fahrgastinformationssystemen innerhalb eines ' \
                  'Haltestellenkatasters'
    list_fields = {
      'dfi_typ': 'DFI-Typ'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['dfi_typ']

  def __str__(self):
    return self.dfi_typ

  def save(self, *args, **kwargs):
    super(DFI_Typen_Haltestellenkataster, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(DFI_Typen_Haltestellenkataster, self).delete(*args, **kwargs)


# Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters

class Fahrgastunterstandstypen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  fahrgastunterstandstyp = models.CharField(
    'Fahrgastunterstandstyp',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"fahrgastunterstandstypen_haltestellenkataster'
    verbose_name = 'Typ eines Fahrgastunterstands innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters'
    description = 'Typen von Fahrgastunterständen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fahrgastunterstandstyp': 'Fahrgastunterstandstyp'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['fahrgastunterstandstyp']

  def __str__(self):
    return self.fahrgastunterstandstyp

  def save(self, *args, **kwargs):
    super(
      Fahrgastunterstandstypen_Haltestellenkataster,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Fahrgastunterstandstypen_Haltestellenkataster,
      self).delete(
      *args,
      **kwargs)


# Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters

class Fahrplanvitrinentypen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  fahrplanvitrinentyp = models.CharField(
    'Fahrplanvitrinentyp',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"fahrplanvitrinentypen_haltestellenkataster'
    verbose_name = 'Typ einer Fahrplanvitrine innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters'
    description = 'Typen von Fahrplanvitrinen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'fahrplanvitrinentyp': 'Fahrplanvitrinentyp'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['fahrplanvitrinentyp']

  def __str__(self):
    return self.fahrplanvitrinentyp

  def save(self, *args, **kwargs):
    super(
      Fahrplanvitrinentypen_Haltestellenkataster,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Fahrplanvitrinentypen_Haltestellenkataster,
      self).delete(
      *args,
      **kwargs)


# Typen von Haltestellen

class Typen_Haltestellen(Typ):
  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_haltestellen'
    verbose_name = 'Typ einer Haltestelle'
    verbose_name_plural = 'Typen von Haltestellen'
    description = 'Typen von Haltestellen'

  def save(self, *args, **kwargs):
    super(Typen_Haltestellen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Typen_Haltestellen, self).delete(*args, **kwargs)


# Typen von Pollern

class Typen_Poller(Typ):
  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_poller'
    verbose_name = 'Typ eines Pollers'
    verbose_name_plural = 'Typen von Pollern'
    description = 'Typen von Pollern'

  def save(self, *args, **kwargs):
    super(Typen_Poller, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Typen_Poller, self).delete(*args, **kwargs)


# Typen von UVP-Vorhaben

class Typen_UVP_Vorhaben(Typ):
  class Meta(Typ.Meta):
    db_table = 'codelisten\".\"typen_uvp_vorhaben'
    verbose_name = 'Typ eines UVP-Vorhabens'
    verbose_name_plural = 'Typen von UVP-Vorhaben'
    description = 'Typen von UVP-Vorhaben'

  def save(self, *args, **kwargs):
    super(Typen_UVP_Vorhaben, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Typen_UVP_Vorhaben, self).delete(*args, **kwargs)


# Verbünde von Ladestationen für Elektrofahrzeuge

class Verbuende_Ladestationen_Elektrofahrzeuge(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  verbund = models.CharField(
    'Verbund',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"verbuende_ladestationen_elektrofahrzeuge'
    verbose_name = 'Verbund einer Ladestation für Elektrofahrzeuge'
    verbose_name_plural = 'Verbünde von Ladestationen für Elektrofahrzeuge'
    description = 'Verbünde von Ladestationen für Elektrofahrzeuge'
    list_fields = {
      'verbund': 'Verbund'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['verbund']

  def __str__(self):
    return self.verbund

  def save(self, *args, **kwargs):
    super(
      Verbuende_Ladestationen_Elektrofahrzeuge,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Verbuende_Ladestationen_Elektrofahrzeuge,
      self).delete(
      *args,
      **kwargs)


# Verkehrliche Lagen von Baustellen

class Verkehrliche_Lagen_Baustellen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  verkehrliche_lage = models.CharField(
    ' verkehrliche Lage',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"verkehrliche_lagen_baustellen'
    verbose_name = 'Verkehrliche Lage einer Baustelle'
    verbose_name_plural = 'Verkehrliche Lagen von Baustellen'
    description = 'Verkehrliche Lagen von Baustellen'
    list_fields = {
      'verkehrliche_lage': 'verkehrliche Lage'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['verkehrliche_lage']

  def __str__(self):
    return self.verkehrliche_lage

  def save(self, *args, **kwargs):
    super(Verkehrliche_Lagen_Baustellen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Verkehrliche_Lagen_Baustellen, self).delete(*args, **kwargs)


# Verkehrsmittelklassen

class Verkehrsmittelklassen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  verkehrsmittelklasse = models.CharField(
    'Verkehrsmittelklasse',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"verkehrsmittelklassen'
    verbose_name = 'Verkehrsmittelklasse'
    verbose_name_plural = 'Verkehrsmittelklassen'
    description = 'Verkehrsmittelklassen'
    list_fields = {
      'verkehrsmittelklasse': 'Verkehrsmittelklasse'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['verkehrsmittelklasse']

  def __str__(self):
    return self.verkehrsmittelklasse

  def save(self, *args, **kwargs):
    super(Verkehrsmittelklassen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Verkehrsmittelklassen, self).delete(*args, **kwargs)


# Vorgangsarten von UVP-Vorhaben

class Vorgangsarten_UVP_Vorhaben(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  vorgangsart = models.CharField(
    'Vorgangsart',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"vorgangsarten_uvp_vorhaben'
    verbose_name = 'Vorgangsart eines UVP-Vorhabens'
    verbose_name_plural = 'Vorgangsarten von UVP-Vorhaben'
    description = 'Vorgangsarten von UVP-Vorhaben'
    list_fields = {
      'vorgangsart': 'Vorgangsart'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['vorgangsart']

  def __str__(self):
    return self.vorgangsart

  def save(self, *args, **kwargs):
    super(Vorgangsarten_UVP_Vorhaben, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Vorgangsarten_UVP_Vorhaben, self).delete(*args, **kwargs)


# Wegebreiten gemäß Straßenreinigungssatzung der Hanse- und
# Universitätsstadt Rostock

class Wegebreiten_Strassenreinigungssatzung_HRO(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  wegebreite = models.DecimalField(
    'Wegebreite (in m)',
    max_digits=4,
    decimal_places=2,
    validators=[
      MinValueValidator(
        Decimal('0.01'),
        'Die <strong><em>Wegebreite</em></strong> muss mindestens 0,01 m betragen.'),
      MaxValueValidator(
        Decimal('99.99'),
        'Die <strong><em>Wegebreite</em></strong> darf höchstens 99,99 m betragen.')])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"wegebreiten_strassenreinigungssatzung_hro'
    verbose_name = 'Wegebreite gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt ' \
                   'Rostock'
    verbose_name_plural = 'Wegebreiten gemäß Straßenreinigungssatzung der Hanse- und ' \
                          'Universitätsstadt Rostock'
    description = 'Wegebreiten gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt ' \
                  'Rostock'
    list_fields = {
      'wegebreite': 'Wegebreite'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['wegebreite']

  def __str__(self):
    return str(self.wegebreite)

  def save(self, *args, **kwargs):
    super(
      Wegebreiten_Strassenreinigungssatzung_HRO,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Wegebreiten_Strassenreinigungssatzung_HRO,
      self).delete(
      *args,
      **kwargs)


# Wegereinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und
# Universitätsstadt Rostock

class Wegereinigungsklassen_Strassenreinigungssatzung_HRO(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  code = fields.PositiveSmallIntegerRangeField(
    'Code', min_value=1, max_value=7)

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"wegereinigungsklassen_strassenreinigungssatzung_hro'
    verbose_name = 'Wegereinigungsklasse gemäß Straßenreinigungssatzung der Hanse- und ' \
                   'Universitätsstadt Rostock'
    verbose_name_plural = 'Wegereinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und ' \
                          'Universitätsstadt Rostock'
    description = 'Wegereinigungsklassen gemäß Straßenreinigungssatzung der Hanse- und ' \
                  'Universitätsstadt Rostock'
    list_fields = {
      'code': 'Code'
    }
    list_fields_with_number = ['code']
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['code']

  def __str__(self):
    return str(self.code)

  def save(self, *args, **kwargs):
    super(
      Wegereinigungsklassen_Strassenreinigungssatzung_HRO,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Wegereinigungsklassen_Strassenreinigungssatzung_HRO,
      self).delete(
      *args,
      **kwargs)


# Wegereinigungsrhythmen gemäß Straßenreinigungssatzung der Hanse- und
# Universitätsstadt Rostock

class Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ordinalzahl = fields.PositiveSmallIntegerRangeField(
    'Ordinalzahl', min_value=1)
  reinigungsrhythmus = models.CharField(
    'Reinigungsrhythmus',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"wegereinigungsrhythmen_strassenreinigungssatzung_hro'
    verbose_name = 'Wegereinigungsrhythmus gemäß Straßenreinigungssatzung der Hanse- und ' \
                   'Universitätsstadt Rostock'
    verbose_name_plural = 'Wegereinigungsrhythmen gemäß Straßenreinigungssatzung der Hanse- und ' \
                          'Universitätsstadt Rostock'
    description = 'Wegereinigungsrhythmen gemäß Straßenreinigungssatzung der Hanse- und ' \
                  'Universitätsstadt Rostock'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'reinigungsrhythmus': 'Reinigungsrhythmus'
    }
    list_fields_with_number = ['ordinalzahl']
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ordinalzahl']

  def __str__(self):
    return str(self.reinigungsrhythmus)

  def save(self, *args, **kwargs):
    super(
      Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Wegereinigungsrhythmen_Strassenreinigungssatzung_HRO,
      self).delete(
      *args,
      **kwargs)


# Wegetypen gemäß Straßenreinigungssatzung der Hanse- und
# Universitätsstadt Rostock

class Wegetypen_Strassenreinigungssatzung_HRO(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  wegetyp = models.CharField(
    'Wegetyp',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"wegetypen_strassenreinigungssatzung_hro'
    verbose_name = 'Wegetyp gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt ' \
                   'Rostock'
    verbose_name_plural = 'Wegetypen gemäß Straßenreinigungssatzung der Hanse- und ' \
                          'Universitätsstadt Rostock'
    description = 'Wegetypen gemäß Straßenreinigungssatzung der Hanse- und Universitätsstadt ' \
                  'Rostock'
    list_fields = {
      'wegetyp': 'Wegetyp'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['wegetyp']

  def __str__(self):
    return str(self.wegetyp)

  def save(self, *args, **kwargs):
    super(
      Wegetypen_Strassenreinigungssatzung_HRO,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Wegetypen_Strassenreinigungssatzung_HRO,
      self).delete(
      *args,
      **kwargs)


# Zeiteinheiten

class Zeiteinheiten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  zeiteinheit = models.CharField(
    'Zeiteinheit',
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
  erlaeuterung = models.CharField(
    'Erläuterung',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"zeiteinheiten'
    verbose_name = 'Zeiteinheit'
    verbose_name_plural = 'Zeiteinheiten'
    description = 'Zeiteinheiten'
    list_fields = {
      'zeiteinheit': 'Zeiteinheit',
      'erlaeuterung': 'Erläuterung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['erlaeuterung']

  def __str__(self):
    return self.erlaeuterung

  def save(self, *args, **kwargs):
    super(Zeiteinheiten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Zeiteinheiten, self).delete(*args, **kwargs)


# ZH-Typen innerhalb eines Haltestellenkatasters

class ZH_Typen_Haltestellenkataster(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  zh_typ = models.CharField(
    'ZH-Typ',
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"zh_typen_haltestellenkataster'
    verbose_name = 'ZH-Typ innerhalb eines Haltestellenkatasters'
    verbose_name_plural = 'ZH-Typen innerhalb eines Haltestellenkatasters'
    description = 'ZH-Typen innerhalb eines Haltestellenkatasters'
    list_fields = {
      'zh_typ': 'ZH-Typ'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['zh_typ']

  def __str__(self):
    return self.zh_typ

  def save(self, *args, **kwargs):
    super(ZH_Typen_Haltestellenkataster, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(ZH_Typen_Haltestellenkataster, self).delete(*args, **kwargs)


# Zonen für Parkscheinautomaten

class Zonen_Parkscheinautomaten(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  zone = models.CharField(
    'Zone',
    max_length=1,
    validators=[
      RegexValidator(
        regex=constants_vars.zon_psa_zone_regex,
        message=constants_vars.zon_psa_zone_message)])

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"zonen_parkscheinautomaten'
    verbose_name = 'Zone für einen Parkscheinautomaten'
    verbose_name_plural = 'Zonen für Parkscheinautomaten'
    description = 'Zonen für Parkscheinautomaten'
    list_fields = {
      'zone': 'Zone'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['zone']

  def __str__(self):
    return self.zone

  def save(self, *args, **kwargs):
    super(Zonen_Parkscheinautomaten, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Zonen_Parkscheinautomaten, self).delete(*args, **kwargs)


# Zustände von Kadaverfunden

class Zustaende_Kadaverfunde(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ordinalzahl = fields.PositiveSmallIntegerRangeField(
    'Ordinalzahl', min_value=1)
  zustand = models.CharField(
    'Zustand', max_length=255, validators=[
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"zustaende_kadaverfunde'
    verbose_name = 'Zustand eines Kadaverfunds'
    verbose_name_plural = 'Zustände von Kadaverfunden'
    description = 'Zustände von Kadaverfunden'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'zustand': 'Zustand'
    }
    list_fields_with_number = ['ordinalzahl']
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ordinalzahl']

  def __str__(self):
    return str(self.zustand)

  def save(self, *args, **kwargs):
    super(
      Zustaende_Kadaverfunde,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Zustaende_Kadaverfunde,
      self).delete(
      *args,
      **kwargs)


# Zustände von Schutzzäunen gegen Tierseuchen

class Zustaende_Schutzzaeune_Tierseuchen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  ordinalzahl = fields.PositiveSmallIntegerRangeField(
    'Ordinalzahl', min_value=1)
  zustand = models.CharField(
    'Zustand', max_length=255, validators=[
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

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"zustaende_schutzzaeune_tierseuchen'
    verbose_name = 'Zustand eines Schutzzauns gegen eine Tierseuche'
    verbose_name_plural = 'Zustände von Schutzzäunen gegen Tierseuchen'
    description = 'Zustände von Schutzzäunen gegen Tierseuchen'
    list_fields = {
      'ordinalzahl': 'Ordinalzahl',
      'zustand': 'Zustand'
    }
    list_fields_with_number = ['ordinalzahl']
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['ordinalzahl']

  def __str__(self):
    return str(self.zustand)

  def save(self, *args, **kwargs):
    super(
      Zustaende_Schutzzaeune_Tierseuchen,
      self).save(
      *args,
      **kwargs)

  def delete(self, *args, **kwargs):
    super(
      Zustaende_Schutzzaeune_Tierseuchen,
      self).delete(
      *args,
      **kwargs)


# Zustandsbewertungen

class Zustandsbewertungen(models.Model):
  uuid = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False)
  zustandsbewertung = fields.PositiveSmallIntegerMinField(
    'Zustandsbewertung', min_value=1)

  class Meta:
    managed = False
    codelist = True
    db_table = 'codelisten\".\"zustandsbewertungen'
    verbose_name = 'Zustandsbewertung'
    verbose_name_plural = 'Zustandsbewertungen'
    description = 'Zustandsbewertungen'
    list_fields = {
      'zustandsbewertung': 'Zustandsbewertung'
    }
    # wichtig, denn nur so werden Drop-down-Einträge in Formularen von
    # Kindtabellen sortiert aufgelistet
    ordering = ['zustandsbewertung']

  def __str__(self):
    return str(self.zustandsbewertung)

  def save(self, *args, **kwargs):
    super(Zustandsbewertungen, self).save(*args, **kwargs)

  def delete(self, *args, **kwargs):
    super(Zustandsbewertungen, self).delete(*args, **kwargs)
