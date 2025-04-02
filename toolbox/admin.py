from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db import models
from django.forms import ModelForm, TextInput

from .models import PdfTemplate, SuitableFor


class SuitableForInline(admin.StackedInline):
  model = SuitableFor
  fieldsets = [(None, {'fields': ['id', 'datenthema', 'bemerkungen', 'usedkeys', 'sortby']})]


@admin.register(PdfTemplate)
class PdfTemplateAdmin(admin.ModelAdmin):
  list_display = ('id', 'name', 'created_at', 'description')
  inlines = [SuitableForInline]
  formfield_overrides = {models.CharField: {'widget': TextInput(attrs={'size': '20'})}}


class SuitableForm(ModelForm):
  def get_f_names(self):
    fields = self.cleaned_data['datenthema'].model_class()._meta.get_fields()
    return [f.name for f in fields]

  def clean_sortby(self):
    keylist = self.cleaned_data['sortby']
    fieldnames = self.get_f_names()
    if keylist is not None:
      for key in keylist:
        if key not in fieldnames and not (key[0] == '-' and key[1:] in fieldnames):
          raise ValidationError(f'{key} ist kein Feld von {self.cleaned_data["datenthema"]}!')
    return self.cleaned_data['sortby']

  def clean_usedkeys(self):
    keylist = self.cleaned_data['usedkeys']
    fieldnames = self.get_f_names()
    if keylist is not None:
      for key in keylist:
        if key[0] not in fieldnames:
          raise ValidationError(f'{key[0]} ist kein Feld von {self.cleaned_data["datenthema"]}!')
    return keylist


@admin.register(SuitableFor)
class SuitableForAdmin(admin.ModelAdmin):
  ordering = ['datenthema']
  list_display = ('id', 'datenthema', 'template__name', 'bemerkungen')
  form = SuitableForm
