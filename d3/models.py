from django.contrib.auth.models import User
from django.db.models import CASCADE, FileField, ForeignKey, JSONField, ManyToManyField, Model, SET_NULL
from django.db.models.fields import AutoField, CharField, DateTimeField, TextField, BooleanField, DateField
from django.contrib.contenttypes.models import ContentType

from d3.constants_vars import GUI_ELEMENTE


class Akte(Model):
    id = AutoField(primary_key=True)
    d3_id = CharField(max_length=32)
    object_id = CharField(max_length=14)
    model = ForeignKey(ContentType, on_delete=CASCADE)

    class Meta:
        verbose_name = 'Akte'
        verbose_name_plural = 'Akten',
        db_table = 'd3_akte'


class AktenOrdner(Model):
    id = AutoField(primary_key=True)
    d3_id = CharField(max_length=32)
    model = ForeignKey(ContentType, on_delete=CASCADE)

    class Meta:
        verbose_name = 'AktenOrdner'
        verbose_name_plural = 'AktenOrdner',
        db_table = 'd3_akten_ordner'

class  Vorgang(Model):
    id = AutoField(primary_key=True)
    titel = CharField(max_length=255)
    akten_id = ForeignKey(Akte, on_delete=CASCADE)
    d3_id = CharField(max_length=32)
    vorgangs_typ = CharField(max_length=50)
    erstellt = DateTimeField(auto_now_add=True)
    erstellt_durch = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, to_field='username')
    aktualisiert = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Vorgang'
        verbose_name_plural = 'Vorgänge'
        db_table = 'd3_vorgang'


class Metadaten(Model):
    id = AutoField(primary_key=True)
    titel = CharField(verbose_name='Titel', max_length=255, unique=True)
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
    d3_id = CharField(max_length=32)

    class Meta:
        verbose_name = 'Metadaten'
        verbose_name_plural = 'Metadaten',
        db_table = 'd3_metadaten'


class VorgangMetadaten(Model):
    id = AutoField(primary_key=True)
    vorgang_id = ForeignKey(Vorgang, on_delete=CASCADE)
    metadaten_id = ForeignKey(Metadaten, on_delete=CASCADE)
    wert = CharField(max_length=255)
    aktualisiert = DateField(auto_now=True)
    erstellt = DateField(auto_now_add=True)
    erstellt_durch = ForeignKey(User, on_delete=SET_NULL, null=True, blank=True, to_field='username')

    class Meta:
        verbose_name = 'VorgangMetadaten'
        verbose_name_plural = 'VorgangMetadaten',
        db_table = 'd3_vorgang_metadaten'

class Massnahme(Model):
    id = AutoField(primary_key=True)
    titel = CharField(max_length=255)
    erstellt = DateTimeField(auto_now_add=True)
    aktualisiert = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Massnahme'
        verbose_name_plural = 'Massnahmen',
        db_table = 'd3_massnahme'

class Verfahren(Model):
    id = AutoField(primary_key=True)
    titel = CharField(max_length=255)
    erstellt = DateTimeField(auto_now_add=True)
    aktualisiert = DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Verfahren'
        verbose_name_plural = 'Verfahren',
        db_table = 'd3_verfahren'