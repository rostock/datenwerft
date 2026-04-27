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

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

    used_ids = set(
      Collection.objects.exclude(service_id__isnull=True).values_list('service_id', flat=True)
    )

    qs = Service.objects.filter(type=ServiceType.API_FEATURES)

    # Ensure current instance value is not excluded (edit mode)
    if self.instance and self.instance.service_id:
      used_ids.discard(self.instance.service_id)

    # Apply filtering
    qs = qs.exclude(pk__in=used_ids)

    self.fields['service'].queryset = qs

    # Ensure preselection in edit mode (safe fallback)
    if self.instance and self.instance.service_id:
      self.fields['service'].initial = self.instance.service_id

  def save(self, commit=True):
    instance = super().save(commit=False)
    service = self.cleaned_data.get('service')
    instance.service_id = service.pk if service else None
    if commit:
      instance.save()
    return instance


@admin.register(DatabaseConnection)
class DatabaseConnectionAdmin(admin.ModelAdmin):
  ordering = ('host', 'dbname', 'user')
  list_display = ('id', 'host', 'dbname', 'user')
  empty_value_display = ''


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
  form = CollectionForm
  list_display = ('id', 'service_display', 'database_connection', 'schema', 'table', 'deactivated')
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

  def get_queryset(self, request):
    qs = super().get_queryset(request)

    # Collect all service_ids from the queryset
    service_ids = set(qs.exclude(service_id__isnull=True).values_list('service_id', flat=True))

    # Cache related services in one query (avoid N+1)
    self._service_cache = {s.id: s for s in Service.objects.filter(id__in=service_ids)}

    return qs

  def service_display(self, obj):
    service = getattr(self, '_service_cache', {}).get(obj.service_id)
    if not service:
      return '-' if not obj.service_id else f'Unknown ({obj.service_id})'
    return f'({service.name}) {service.title}'

  service_display.short_description = 'Service-Metadatensatz aus GDI.HRO Metadata'
  service_display.admin_order_field = 'service_id'

  def save_model(self, request, obj, form, change):
    super().save_model(request, obj, form, change)
    reload_pygeoapi()

  def delete_model(self, request, obj):
    super().delete_model(request, obj)
    reload_pygeoapi()

  def delete_queryset(self, request, queryset):
    super().delete_queryset(request, queryset)
    reload_pygeoapi()
