from django.contrib.auth.models import User
from django.db.models import CASCADE, ForeignKey, Model, SET_NULL, OneToOneField, ManyToManyField
from django.db.models.fields import AutoField, CharField, DateTimeField, BooleanField, DateField
from django.contrib.contenttypes.models import ContentType

from d3.constants_vars import GUI_ELEMENTE


class Akte(Model):
    id = AutoField(primary_key=True)
    d3_id = CharField(max_length=36)
    object_id = CharField(max_length=36)
    model = ForeignKey(ContentType, on_delete=CASCADE, limit_choices_to={'app_label': 'datenmanagement'})

    class Meta:
        verbose_name = 'Akte'
        verbose_name_plural = 'Akten'
        db_table = 'd3_akte'

class AktenOrdner(Model):
    id = AutoField(primary_key=True)
    d3_id = CharField(max_length=36)
    model = OneToOneField(ContentType, on_delete=CASCADE, limit_choices_to={'app_label': 'datenmanagement'})

    class Meta:
        verbose_name = 'Akten Ordner'
        verbose_name_plural = 'Akten Ordner'
        db_table = 'd3_akten_ordner'

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
            'id': 'Id',
            'vorgangs_typ': 'Vorgangs Typ',
            'titel': 'Titel',
            'akten': 'Akte',
            'd3_id': 'D3 Id',
            'erstellt': 'Erstellt',
            'erstellt_durch': 'Erstellt Durch',
            'aktualisiert': 'Aktualisiert',
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

class Metadaten(Model):
    id = AutoField(primary_key=True)
    titel = CharField(verbose_name='Titel', max_length=255, unique=False)
    gui_element = CharField(
        verbose_name='GUI Element',
        max_length=45,
        choices=GUI_ELEMENTE,
    )
    erforderlich = BooleanField(
        verbose_name='Eingabe erforderlich?', default=False, blank=False, null=True
    )
    regex = CharField(
        verbose_name='Validierung über Regex',
        max_length=255,
        blank=True,
        null=True,
    )
    d3_id = CharField(max_length=36, null=True, blank=True, default=None)
    category = CharField(max_length=50, null=False, blank=False, default="vorgang")

    class Meta:
        verbose_name = 'Metadaten'
        verbose_name_plural = 'Metadaten'
        db_table = 'd3_metadaten'

class MetadatenOption(Model):
    id = AutoField(primary_key=True)
    metadaten = ForeignKey(Metadaten, on_delete=CASCADE)
    value = CharField(verbose_name='Wert', max_length=255)

    class Meta:
        verbose_name = 'Metadatenoption'
        verbose_name_plural = 'Metadatenoption'
        db_table = 'd3_metadaten_option'

class VorgangMetadaten(Model):
    id = AutoField(primary_key=True)
    vorgang = ForeignKey(Vorgang, on_delete=CASCADE)
    metadaten = ForeignKey(Metadaten, on_delete=CASCADE)
    wert = CharField(max_length=255)
    aktualisiert = DateField(auto_now=True)
    erstellt = DateField(auto_now_add=True)
    erstellt_durch = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, to_field='id')

    class Meta:
        verbose_name = 'VorgangMetadaten'
        verbose_name_plural = 'VorgangMetadaten'
        db_table = 'd3_vorgang_metadaten'

class Massnahme(Model):
    id = AutoField(primary_key=True)
    titel = CharField(max_length=255)
    erstellt = DateTimeField(auto_now_add=True)
    aktualisiert = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Massnahme'
        verbose_name_plural = 'Massnahmen'
        db_table = 'd3_massnahme'

class Verfahren(Model):
    id = AutoField(primary_key=True)
    titel = CharField(max_length=255)
    erstellt = DateTimeField(auto_now_add=True)
    aktualisiert = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Verfahren'
        verbose_name_plural = 'Verfahren'
        db_table = 'd3_verfahren'
