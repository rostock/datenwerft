from django.contrib import admin
from django.contrib.messages import warning
from django.forms import CharField, ChoiceField, ModelForm, Select
from django.forms.widgets import HiddenInput

from datenwerft.settings import D3_AKTEN_CATEGORY, D3_DATEI_CATEGORY, D3_VORGANG_CATEGORY

from .models import (
  Akte,
  AktenOrdner,
  AktenOrdnerOption,
  Massnahme,
  Metadaten,
  MetadatenOption,
  Verfahren,
)
from .utils import lade_d3_properties, lade_d3_session_id


class AktenOrdnerOptionenForInline(admin.StackedInline):
  model = AktenOrdnerOption
  fieldsets = [(None, {'fields': ['d3_id', 'wert', 'ist_namens_feld']})]
  extra = 0

  def get_formset(self, request, obj=None, **kwargs):
    d3_properties = [('', '---------')] + lade_d3_properties(request, D3_AKTEN_CATEGORY)
    d3_field = ChoiceField(label='D3 Feld', choices=d3_properties)
    d3_field.required = False

    self.form.base_fields['d3_id'] = d3_field

    return super().get_formset(request, obj, **kwargs)


class MetadatenOptionenForInline(admin.StackedInline):
  model = MetadatenOption
  fieldsets = [(None, {'fields': ['value']})]
  extra = 0


class VorgangMetadatenProxy(Metadaten):
  class Meta:
    proxy = True
    verbose_name = 'Metadaten (Vorgang)'
    verbose_name_plural = 'Metadaten (Vorgang)'


class DokumentMetadatenProxy(Metadaten):
  class Meta:
    proxy = True
    verbose_name = 'Metadaten (Dokument)'
    verbose_name_plural = 'Metadaten (Dokument)'


@admin.register(Massnahme)
class MassnahmeForAdmin(admin.ModelAdmin):
  ordering = ['titel']
  list_display = ('id', 'titel', 'erstellt', 'aktualisiert')


@admin.register(Verfahren)
class VerfahrenForAdmin(admin.ModelAdmin):
  ordering = ['titel']
  list_display = ('id', 'titel', 'erstellt', 'aktualisiert')


class VorgangMetadatenProxyForm(ModelForm):
  required_css_class = 'required'
  user_request = None

  def __init__(self, *args, **kwargs):
    super(VorgangMetadatenProxyForm, self).__init__(*args, **kwargs)

    if lade_d3_session_id(self.user_request) is None:
      self.fields['d3_id'] = CharField(
        widget=HiddenInput(attrs={'readonly': 'readonly'}), required=False
      )
    else:
      d3_properties = [('', '---------')] + lade_d3_properties(
        self.user_request, D3_VORGANG_CATEGORY
      )
      d3_field = ChoiceField(label='D3 Feld', choices=d3_properties)
      d3_field.widget.attrs.update({'class': 'select2'})
      d3_field.required = False

      self.fields['d3_id'] = d3_field


class DokumentMetadatenProxyForm(ModelForm):
  required_css_class = 'required'
  user_request = None

  def __init__(self, *args, **kwargs):
    super(DokumentMetadatenProxyForm, self).__init__(*args, **kwargs)

    if lade_d3_session_id(self.user_request) is None:
      self.fields['d3_id'] = CharField(
        widget=HiddenInput(attrs={'readonly': 'readonly'}), required=False
      )
    else:
      d3_properties = [('', '---------')] + lade_d3_properties(
        self.user_request, D3_DATEI_CATEGORY
      )
      d3_field = ChoiceField(label='D3 Feld', choices=d3_properties)
      d3_field.widget.attrs.update({'class': 'select2'})
      d3_field.required = False

      self.fields['d3_id'] = d3_field


@admin.register(VorgangMetadatenProxy)
class VorgangMetadatenForAdmin(admin.ModelAdmin):
  ordering = ['titel']
  list_display = ('id', 'titel', 'gui_element', 'erforderlich', 'd3_id')
  readonly_fields = ['category']
  form = VorgangMetadatenProxyForm
  inlines = [MetadatenOptionenForInline]

  def get_queryset(self, request):
    return self.model.objects.filter(category='vorgang')

  def get_form(self, request, obj=None, change=False, **kwargs):
    form = super(VorgangMetadatenForAdmin, self).get_form(request, obj, change, **kwargs)
    form.user_request = request

    if (
      kwargs.get('fields') is not None
      and 'd3_id' in kwargs.get('fields')
      and lade_d3_session_id(request) is None
    ):
      warning(request, 'Die Metadaten konnten nicht über die D3 API geladen werden.')

    return form

  def category(self, obj):
    return 'vorgang'


@admin.register(DokumentMetadatenProxy)
class DokumentenMetadatenForAdmin(admin.ModelAdmin):
  ordering = ['titel']
  list_display = ('id', 'titel', 'gui_element', 'erforderlich', 'd3_id')
  readonly_fields = ['category']
  form = DokumentMetadatenProxyForm
  inlines = [MetadatenOptionenForInline]

  def get_queryset(self, request):
    return self.model.objects.filter(category='dokument')

  def get_form(self, request, obj=None, change=False, **kwargs):
    form = super(DokumentenMetadatenForAdmin, self).get_form(request, obj, change, **kwargs)
    form.user_request = request

    if (
      kwargs.get('fields') is not None
      and 'd3_id' in kwargs.get('fields')
      and lade_d3_session_id(request) is None
    ):
      warning(request, 'Die Metadaten konnten nicht über die D3 API geladen werden.')

    return form

  def category(self, obj):
    return 'dokument'

  def save_model(self, request, obj, form, change):
    obj.category = 'dokument'
    super().save_model(request, obj, form, change)


class AktenOrdnerForm(ModelForm):
  required_css_class = 'required'

  class Meta:
    widgets = {'model': Select(attrs={'class': 'select2'})}


@admin.register(AktenOrdner)
class AktenOrdnerForAdmin(admin.ModelAdmin):
  ordering = ['model']
  list_display = ('id', 'model')
  form = AktenOrdnerForm
  inlines = [AktenOrdnerOptionenForInline]


class AktenForm(ModelForm):
  required_css_class = 'required'

  class Meta:
    widgets = {'model': Select(attrs={'class': 'select2'})}


@admin.register(Akte)
class AktenForAdmin(admin.ModelAdmin):
  ordering = ['model']
  list_display = ('id', 'd3_id', 'model', 'object_id')
  fields = ['model', 'object_id', 'd3_id']
  form = AktenForm
  search_fields = ['object_id']
