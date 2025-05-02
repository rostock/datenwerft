from django.contrib import admin

from .models import (
  Access,
  App,
  Assetset,
  AssetType,
  Charset,
  Contact,
  Crs,
  CrsSet,
  Dataset,
  DatathemeCategory,
  DataType,
  Format,
  Frequency,
  HashType,
  HvdCategory,
  InspireServiceType,
  InspireSpatialScope,
  InspireTheme,
  Language,
  Legal,
  License,
  MimeType,
  Organization,
  PoliticalGeocoding,
  PoliticalGeocodingLevel,
  Repository,
  Service,
  Source,
  SpatialReference,
  SpatialRepresentationType,
  Tag,
  Topic,
)

#
# codelists
#


@admin.register(Access)
class AccessAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(AssetType)
class AssetTypeAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(Charset)
class CharsetAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(Crs)
class CrsAdmin(admin.ModelAdmin):
  list_display = ('code', 'title', 'description')
  search_fields = ('code', 'title', 'description')
  empty_value_display = ''


@admin.register(DatathemeCategory)
class DatathemeCategoryAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(Format)
class FormatAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(Frequency)
class FrequencyAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(HashType)
class HashTypeAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(HvdCategory)
class HvdCategoryAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(InspireServiceType)
class InspireServiceTypeAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(InspireSpatialScope)
class InspireSpatialScopeAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(InspireTheme)
class InspireThemeAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
  list_display = ('code', 'title', 'description')
  search_fields = ('code', 'title', 'description')
  empty_value_display = ''


@admin.register(MimeType)
class MimeTypeAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(PoliticalGeocoding)
class PoliticalGeocodingAdmin(admin.ModelAdmin):
  list_display = ('code', 'title', 'description')
  search_fields = ('code', 'title', 'description')
  empty_value_display = ''


@admin.register(PoliticalGeocodingLevel)
class PoliticalGeocodingLevelAdmin(admin.ModelAdmin):
  list_display = ('code', 'title', 'description')
  search_fields = ('code', 'title', 'description')
  empty_value_display = ''


@admin.register(SpatialRepresentationType)
class SpatialRepresentationTypeAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
  list_display = ('code', 'title')
  search_fields = ('code', 'title')
  empty_value_display = ''
  exclude = ['description']


#
# auxiliary models
#


@admin.register(CrsSet)
class CrsSetAdmin(admin.ModelAdmin):
  list_display = ('title', 'crs_display')
  search_fields = ('title', 'crs__title')
  filter_horizontal = ('crs',)
  empty_value_display = ''

  def crs_display(self, obj):
    return ', '.join([crs.title for crs in obj.crs.all()])

  crs_display.short_description = 'Koordinatenreferenzsystem(e)'


@admin.register(DataType)
class DataTypeAdmin(admin.ModelAdmin):
  list_display = ('title', 'format', 'mime_type')
  search_fields = ('title', 'format__title', 'mime_type__title')
  list_filter = ('format', 'mime_type')
  empty_value_display = ''


@admin.register(Legal)
class LegalAdmin(admin.ModelAdmin):
  list_display = ('title', 'access', 'license')
  search_fields = ('title', 'access__title', 'license__title', 'constraints')
  list_filter = ('access', 'license')
  empty_value_display = ''


@admin.register(SpatialReference)
class SpatialReferenceAdmin(admin.ModelAdmin):
  list_display = ('title', 'political_geocoding_level', 'political_geocoding')
  search_fields = ('title', 'political_geocoding_level__title', 'political_geocoding__title')
  list_filter = ('political_geocoding_level', 'political_geocoding')
  empty_value_display = ''


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
  list_display = ('name', 'title')
  search_fields = ('name', 'title')
  empty_value_display = ''


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
  list_display = ('first_name', 'last_name', 'email', 'organization')
  search_fields = ('first_name', 'last_name', 'email', 'organization__name', 'organization__title')
  list_filter = ('organization',)
  empty_value_display = ''


#
# core models
#


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
  list_display = ('type', 'connection_info', 'last_import', 'processing_type')
  list_filter = ('type', 'processing_type', 'geometry_type')
  search_fields = ('connection_info', 'description')
  filter_horizontal = ('tags', 'authors')


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
  list_display = ('type', 'connection_info', 'geometry_type', 'created', 'modified')
  list_filter = ('type', 'geometry_type', 'data_type')
  search_fields = ('connection_info', 'description')
  filter_horizontal = ('tags', 'maintainers', 'authors')


@admin.register(Assetset)
class AssetsetAdmin(admin.ModelAdmin):
  list_display = ('name', 'title', 'created', 'modified')
  search_fields = ('name', 'title', 'description')
  list_filter = ('type',)
  filter_horizontal = (
    'tags',
    'publishers',
    'maintainers',
    'repositories',
  )


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
  list_display = ('name', 'title', 'geometry_type', 'created', 'modified', 'uuid')
  list_filter = ('geometry_type', 'language', 'charset', 'data_type')
  search_fields = ('name', 'title', 'uuid', 'description')
  filter_horizontal = (
    'tags',
    'additional_crs',
    'publishers',
    'maintainers',
    'repositories',
  )


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
  list_display = ('name', 'title', 'type', 'created', 'modified', 'uuid')
  list_filter = ('type', 'language', 'charset')
  search_fields = ('name', 'title', 'uuid', 'description')
  filter_horizontal = (
    'tags',
    'additional_crs',
    'publishers',
    'maintainers',
    'datasets',
    'assetsets',
    'repositories',
  )


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
  list_display = ('name', 'title', 'created', 'modified', 'uuid')
  search_fields = ('name', 'title', 'uuid', 'description')
  filter_horizontal = (
    'tags',
    'categories',
    'services',
    'datasets',
    'assetsets',
  )


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
  list_display = ('name', 'title', 'created', 'modified', 'uuid')
  search_fields = ('name', 'title', 'uuid', 'description')
  filter_horizontal = (
    'tags',
    'publishers',
    'maintainers',
    'languages',
    'topics',
    'services',
    'datasets',
    'assetsets',
    'repositories',
  )
