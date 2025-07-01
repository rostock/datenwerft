from django import forms
from django.forms import ChoiceField
from django.forms.models import ModelForm

from d3.models import Vorgang, Verfahren, Massnahme

class VorgangForm(ModelForm):

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):

    metadaten_felder = kwargs.pop('metadaten')

    super(VorgangForm, self).__init__(*args, **kwargs)

    self.fields['titel'].widget.attrs.update({'class': 'form-control'})

    self.__init_vorgangs_feld()
    self.__init_metadaten_felder(metadaten_felder)

  class Meta:
    model = Vorgang
    fields = ['vorgangs_typ', 'titel']

  def __init_vorgangs_feld(self):
    """
    Lade die Werte des Feldes "Vorgangs" aus der Datenbank und setze sie als Choice-Feld.
    """
    vorgangs_optionen = []

    for verfahren in Verfahren.objects.all():
      vorgangs_optionen.append((verfahren.titel, verfahren.titel))

    for massnahme in Massnahme.objects.all():
      vorgangs_optionen.append((massnahme.titel, massnahme.titel))

    vorgangs_optionen.sort()
    vorgangs_typ = ChoiceField(choices=vorgangs_optionen)
    vorgangs_typ.widget.attrs.update({'class': 'select2'})

    self.fields['vorgangs_typ'] = vorgangs_typ

  def __init_metadaten_felder(self, metadaten_felder):
    """
    Fügt alle Metadaten Felder zum Formular hinzu, damit diese eingegeben und validiert werden können.

    Parameters:
        metadaten_felder (list): Liste der Metadaten die eingegeben werden können

    """
    for metadaten in metadaten_felder:

      feld_key = 'metadaten.' + str(metadaten.id)
      attributes = {'class': 'form-control'}

      match metadaten.gui_element:
        case 'select':
          self.fields[feld_key] = forms.CharField(label=metadaten.titel, required=metadaten.erforderlich)
        case 'input_text':
          self.fields[feld_key] = forms.CharField(label=metadaten.titel, required=metadaten.erforderlich)
        case 'input_zahl':
          self.fields[feld_key] = forms.DecimalField(label=metadaten.titel, required=metadaten.erforderlich)
        case 'checkbox':
          self.fields[feld_key] = forms.BooleanField(label=metadaten.titel, required=metadaten.erforderlich)
          attributes.pop('class')

      if metadaten.regex:
        attributes['pattern'] = metadaten.regex

      self.fields[feld_key].widget.attrs.update(attributes)
