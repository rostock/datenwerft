from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import ArrayField
from django.db.models import CASCADE, FileField, ForeignKey, JSONField, ManyToManyField, Model
from django.db.models.fields import AutoField, CharField, DateTimeField, TextField


class Subsets(Model):
  id = AutoField(primary_key=True)
  created_at = DateTimeField(auto_now=True)
  model = ForeignKey(to=ContentType, on_delete=CASCADE)
  pk_field = CharField(max_length=255)
  pk_values = ArrayField(
    CharField(
      # usually, model primary keys are UUIDs (36 chars in length)
      max_length=36
    )
  )

  class Meta:
    verbose_name = 'Subset'
    verbose_name_plural = 'Subsets'

  def __str__(self):
    return str(self.id)


class PdfTemplate(Model):
  id = AutoField(primary_key=True)
  created_at = DateTimeField(verbose_name='Erstellungszeitpunkt', auto_now=True)
  templatefile = FileField(verbose_name='tatsächliche Templatedatei', upload_to='latex_templates/')
  suitedfor = ManyToManyField(
    to=ContentType, through='SuitableFor', verbose_name='geeignet für Datenthemen'
  )
  name = TextField(verbose_name='Name des Templates', default='noch nicht benannt')
  description = TextField(verbose_name='Kurzbeschreibung des Templates')

  class Meta:
    verbose_name = 'Export-Vorlage'
    verbose_name_plural = 'Export-Vorlagen'

  def __str__(self):
    return self.name


class SuitableFor(Model):
  id = AutoField(primary_key=True)
  datenthema = ForeignKey(
    to=ContentType, on_delete=CASCADE, limit_choices_to={'app_label': 'datenmanagement'}
  )
  template = ForeignKey(PdfTemplate, on_delete=CASCADE)
  usedkeys = JSONField(verbose_name='ins Template zu speisende Attribute', blank=True, null=True)
  sortby = JSONField(verbose_name='Sortierung der Einträge', blank=True, null=True)
  bemerkungen = TextField(blank=True, null=True)

  class Meta:
    verbose_name = 'Vorlage-Datenthema-Verknüpfung'
    verbose_name_plural = 'Vorlage-Datenthema-Verknüpfungen'

  def __str__(self):
    return str(self.id)

  def template__name(self):
    return self.template.name
