from django.contrib import admin
from django.forms import ModelForm, Select, ModelChoiceField
from django.forms.widgets import Textarea

from .models import (
  DatabaseConnection,
  Collection,
  CollectionCrs,
  CollectionKeyword,
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

class DatenbankVerbindungChoiceField(ModelChoiceField):

  def label_from_instance(self, obj):
    return "(%d) %s" % (obj.id, obj.dbname)

class CollectionForm(ModelForm):
  required_css_class = 'required'

  database_connection = DatenbankVerbindungChoiceField(queryset=DatabaseConnection.objects.all())

  class Meta:
    widgets = {
      'model': Select(attrs={'class': 'select2 load-database-config'}),
      'description': Textarea()
    }

@admin.register(Collection)
class CollectionForAdmin(admin.ModelAdmin):
  ordering = ['name']
  list_display = ('model', 'name', 'title', 'deactivated')
  fields = [
    'model',
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
    'deactivated'
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

@admin.register(DatabaseConnection)
class DatenbankVerbindungForAdmin(admin.ModelAdmin):
  ordering = ['dbname']
  list_display = ('id', 'dbname')
  fields = ['host', 'port', 'dbname', 'user', 'password']
  search_fields = ['dbname']
