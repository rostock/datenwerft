from django.contrib import admin
from django.forms import ModelForm, ChoiceField, Select

from .models import Metadaten, AktenOrdner, Massnahme, Verfahren
from .utils import lade_d3_properties

@admin.register(Massnahme)
class MassnahmeForAdmin(admin.ModelAdmin):
  ordering = ['titel']
  list_display = ('id', 'titel', 'erstellt', 'aktualisiert')

@admin.register(Verfahren)
class VerfahrenForAdmin(admin.ModelAdmin):
  ordering = ['titel']
  list_display = ('id', 'titel', 'erstellt', 'aktualisiert')

class MetadatenForm(ModelForm):

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):

    super(MetadatenForm, self).__init__(*args, **kwargs)

    d3_properties = [('', '---------')] + lade_d3_properties()

    d3_field = ChoiceField(choices=d3_properties)
    d3_field.widget.attrs.update({'class': 'select2'})
    d3_field.required = False

    self.fields['d3_id'] = d3_field

@admin.register(Metadaten)
class MetadatenForAdmin(admin.ModelAdmin):
  ordering = ['titel']
  list_display = ('id', 'titel', 'gui_element', 'erforderlich', 'd3_id')
  form = MetadatenForm

class AktenOrdnerForm(ModelForm):

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):

    super(AktenOrdnerForm, self).__init__(*args, **kwargs)

    d3_akten_ordner = [("test1", "Test1"), ("test2", "Test2"),("test3", "Test3")]
    # d3_akten_ordner = lade_d3_properties()

    d3_field = ChoiceField(choices=d3_akten_ordner)
    d3_field.widget.attrs.update({'class': 'select2'})

    self.fields['d3_id'] = d3_field

  class Meta:

    widgets = {
      'model': Select(attrs={'class': 'select2'})
    }

@admin.register(AktenOrdner)
class AktenOrdnerForAdmin(admin.ModelAdmin):
  ordering = ['model']
  list_display = ('id', 'd3_id', 'model')
  form = AktenOrdnerForm
