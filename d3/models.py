from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.models import CASCADE, SET_NULL, ForeignKey, Model, OneToOneField
from django.db.models.fields import AutoField, BooleanField, CharField, DateField, DateTimeField

from d3.constants_vars import GUI_ELEMENTE


class Akte(Model):
  id = AutoField(primary_key=True)
  d3_id = CharField(verbose_name='d.3-ID', max_length=36)
  object_id = CharField(verbose_name='Objekt-ID', max_length=36)
  model = ForeignKey(
    ContentType,
    verbose_name='Datenmodell',
    on_delete=CASCADE,
    limit_choices_to={'app_label': 'datenmanagement'},
  )

  class Meta:
    verbose_name = 'Akte'
    verbose_name_plural = 'Akten'
    db_table = 'd3_akte'

  def __str__(self):
    return f'{self.id})'


class AktenOrdner(Model):
  id = AutoField(primary_key=True)
  model = OneToOneField(
    ContentType, on_delete=CASCADE, limit_choices_to={'app_label': 'datenmanagement'}
  )

  class Meta:
    verbose_name = 'Aktenordner'
    verbose_name_plural = 'Aktenordner'
    db_table = 'd3_akten_ordner'

  def __str__(self):
    return f'{self.id})'


class AktenOrdnerOption(Model):
  id = AutoField(primary_key=True)
  akten_ordner = ForeignKey(AktenOrdner, on_delete=CASCADE)
  d3_id = CharField(max_length=36)
  wert = CharField(max_length=255, null=True, blank=True)
  ist_namens_feld = BooleanField(default=False)

  class Meta:
    verbose_name = 'Aktenordner-Option'
    verbose_name_plural = 'Aktenordner-Optionen'
    db_table = 'd3_akten_ordner_option'

  def __str__(self):
    return f'{self.id})'


class Vorgang(Model):
  id = AutoField(primary_key=True)
  titel = CharField(max_length=255)
  akten = ForeignKey(Akte, on_delete=CASCADE)
  d3_id = CharField(max_length=36)
  vorgangs_typ = CharField(max_length=50)
  erstellt = DateTimeField(auto_now_add=True)
  erstellt_durch = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, to_field='id')
  aktualisiert = DateTimeField(auto_now=True)

  class BasemodelMeta:
    editable = True
    list_fields = {
      'id': 'ID',
      'vorgangs_typ': 'Vorgangstyp',
      'titel': 'Titel',
      'akten': 'Akte',
      'd3_id': 'd.3-ID',
      'erstellt': 'erstellt',
      'erstellt_durch': 'erstellt durch',
      'aktualisiert': 'aktualisiert',
    }
    list_fields_with_date = ['erstellt', 'aktualisiert']
    list_fields_with_datetime = ['erstellt', 'aktualisiert']
    list_fields_with_decimal = []
    list_fields_with_foreign_key = ['akten', 'erstellt_durch']
    list_additional_foreign_key_field = None
    highlight_flag = None
    thumbs = []

  class Meta:
    verbose_name = 'Vorgang'
    verbose_name_plural = 'Vorgänge'
    db_table = 'd3_vorgang'

  def __str__(self):
    return f'{self.id})'


class Metadaten(Model):
  id = AutoField(primary_key=True)
  titel = CharField(verbose_name='Titel', max_length=255, unique=False)
  gui_element = CharField(
    verbose_name='GUI-Element',
    max_length=45,
    choices=GUI_ELEMENTE,
  )
  erforderlich = BooleanField(
    verbose_name='Eingabe erforderlich?', default=False, blank=False, null=True
  )
  regex = CharField(
    verbose_name='Validierung via Regex',
    max_length=255,
    blank=True,
    null=True,
  )
  d3_id = CharField(max_length=36, null=True, blank=True, default=None)
  category = CharField(
    verbose_name='Kategorie', max_length=50, null=False, blank=False, default='vorgang'
  )

  class Meta:
    verbose_name = 'Metadaten'
    verbose_name_plural = 'Metadatum'
    db_table = 'd3_metadaten'

  def __str__(self):
    return f'{self.id})'


class MetadatenOption(Model):
  id = AutoField(primary_key=True)
  metadaten = ForeignKey(Metadaten, on_delete=CASCADE)
  value = CharField(verbose_name='Wert', max_length=255)

  class Meta:
    verbose_name = 'Metadatenoption'
    verbose_name_plural = 'Metadatenoptionen'
    db_table = 'd3_metadaten_option'

  def __str__(self):
    return f'{self.id})'


class VorgangMetadaten(Model):
  id = AutoField(primary_key=True)
  vorgang = ForeignKey(Vorgang, on_delete=CASCADE)
  metadaten = ForeignKey(Metadaten, on_delete=CASCADE)
  wert = CharField(max_length=255)
  aktualisiert = DateField(auto_now=True)
  erstellt = DateField(auto_now_add=True)
  erstellt_durch = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, to_field='id')

  class Meta:
    verbose_name = 'Vorgang-Metadaten'
    verbose_name_plural = 'Vorgänge-Metadaten'
    db_table = 'd3_vorgang_metadaten'

  def __str__(self):
    return f'{self.id})'


class Massnahme(Model):
  id = AutoField(primary_key=True)
  titel = CharField(max_length=255)
  erstellt = DateTimeField(auto_now_add=True)
  aktualisiert = DateTimeField(auto_now=True)

  class Meta:
    verbose_name = 'Maßnahme'
    verbose_name_plural = 'Maßnahmen'
    db_table = 'd3_massnahme'

  def __str__(self):
    return f'{self.id})'


class Verfahren(Model):
  id = AutoField(primary_key=True)
  titel = CharField(max_length=255)
  erstellt = DateTimeField(auto_now_add=True)
  aktualisiert = DateTimeField(auto_now=True)

  class Meta:
    verbose_name = 'Verfahren'
    verbose_name_plural = 'Verfahren'
    db_table = 'd3_verfahren'

  def __str__(self):
    return f'{self.id})'
