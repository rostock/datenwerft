from django.contrib import admin
from django.forms import ModelChoiceField, ModelForm, Select
from django.utils.translation import gettext_lazy as _

from gdihrometadata.models import Service, ServiceType
from pygeoapi.models import Collection, DatabaseConnection
from pygeoapi.utils import reload_pygeoapi


class ServiceChoiceField(ModelChoiceField):
  def label_from_instance(self, obj):
    return f'({obj.name}) {obj.title}'


class CollectionForm(ModelForm):
  required_css_class = 'required'

  service = ServiceChoiceField(
    queryset=Service.objects.filter(type=ServiceType.API_FEATURES),
    widget=Select(attrs={'class': 'select2'}),
    label=_('Service-Metadatensatz aus GDI.HRO Metadata'),
  )

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
  form = CollectionForm
  list_display = (
    'id',
    'database_connection',
    'deactivated',
  )
  search_fields = ('id',)
  list_filter = ('database_connection',)
  fields = (
    'service',
    'database_connection',
    'schema',
    'table',
    'id_field',
    'title_field',
    'geom_field',
    'storage_crs',
    'deactivated',
  )
  empty_value_display = ''

  def save_model(self, request, obj, form, change):
    super().save_model(request, obj, form, change)
    reload_pygeoapi()

  def delete_model(self, request, obj):
    super().delete_model(request, obj)
    reload_pygeoapi()

  def delete_queryset(self, request, queryset):
    super().delete_queryset(request, queryset)
    reload_pygeoapi()
