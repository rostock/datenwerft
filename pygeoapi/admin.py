from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm, Select
from django.forms.widgets import Textarea
from django.utils.translation import gettext_lazy as _

from gdihrometadata.models import Service, ServiceType

from .models import (
  Collection,
  CollectionCrs,
  CollectionKeyword,
  DatabaseConnection,
)
from .utils import reload_pygeoapi


class CollectionKeywordForInline(admin.StackedInline):
  model = CollectionKeyword
  fieldsets = [(None, {'fields': ['keyword']})]
  extra = 0


class CollectionCrsForInline(admin.StackedInline):
  model = CollectionCrs
  fieldsets = [(None, {'fields': ['crs']})]
  extra = 0


class ServiceChoiceField(ModelChoiceField):
  def label_from_instance(self, obj):
    return f'({obj.name}) {obj.title}'


class CollectionForm(ModelForm):
  required_css_class = 'required'

  service = ServiceChoiceField(
    queryset=Service.objects.filter(type=ServiceType.API_FEATURES),
    widget=Select(attrs={'class': 'select2'}),
    label=_('Service aus GDI.HRO Metadata'),
  )

  class Meta:
    exclude = ['service_id']

  def save(self, commit=True):
    instance = super().save(commit=False)
    service = self.cleaned_data['service']
    if service:
      instance.service_id = service.pk
    if commit:
      instance.save()
    return instance


@admin.register(DatabaseConnection)
class DatabaseConnectionForAdmin(admin.ModelAdmin):
  ordering = ['host', 'dbname', 'user']
  list_display = (
    'id',
    'host',
    'dbname',
    'user',
  )
  search_fields = (
    'host',
    'dbname',
    'user',
  )
  empty_value_display = ''


@admin.register(Collection)
class CollectionForAdmin(admin.ModelAdmin):
  ordering = ['name']
  list_display = ('name', 'title', 'deactivated')
  fields = [
    'service',
    'database_connection',
    'name',
    'title',
    'description',
    'schema',
    'table',
    'id_field',
    'geometry_field',
    'bbox_north',
    'bbox_east',
    'bbox_south',
    'bbox_west',
    'storage_crs',
    'deactivated',
  ]
  form = CollectionForm
  search_fields = ['name']
  inlines = [CollectionKeywordForInline, CollectionCrsForInline]

  def save_model(self, request, obj, form, change):
    super().save_model(request, obj, form, change)
    reload_pygeoapi()

  def delete_model(self, request, obj):
    super().delete_model(request, obj)
    reload_pygeoapi()

  def delete_queryset(self, request, queryset):
    super().delete_queryset(request, queryset)
    reload_pygeoapi()
