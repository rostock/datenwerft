from django import forms
from django.forms import ChoiceField
from django.forms.models import ModelForm

from d3.models import Vorgang, Verfahren, Massnahme


class VorgangForm(ModelForm):

    def __init__(self, *args, **kwargs):

        super(VorgangForm, self).__init__(*args, **kwargs)

        vorgangs_optionen = []

        for verfahren in Verfahren.objects.all():
            vorgangs_optionen.append((verfahren.titel, verfahren.titel))

        for massnahme in Massnahme.objects.all():
            vorgangs_optionen.append((massnahme.titel, massnahme.titel))

        vorgangs_optionen.sort()
        vorgangs_typ = ChoiceField(choices=vorgangs_optionen)
        vorgangs_typ.widget.attrs.update({'class': 'select2'})

        self.fields['vorgangs_typ'] = vorgangs_typ

    class Meta:
        model = Vorgang
        fields = ['titel', 'vorgangs_typ']
