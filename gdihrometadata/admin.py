from django.contrib import admin
from django.forms import ModelForm, ValidationError

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
# forms
#


def field_one_mandatory_if_field_two(form, field_one_name, field_two_name):
  """
  checks if passed field one is set if passed field two is set
  and raises a validation error if not

  :param form: form
  :param field_one_name: name of the first field
  :param field_two_name: name of the second field
  """
  field_one_data = form.cleaned_data.get(field_one_name, None)
  field_two_data = form.cleaned_data.get(field_two_name, None)
  if field_two_data and not field_one_data:
    text = 'Wenn {} gesetzt ist, muss auch {} gesetzt sein.'.format(
      form._meta.model._meta.get_field(field_two_data).verbose_name,
      form._meta.model._meta.get_field(field_one_data).verbose_name,
    )
    raise ValidationError(text)


def field_two_later_than_field_one(form, field_one_name, field_two_name):
  """
  checks if passed field two is later (related to time) than field one
  and raises a validation error if not

  :param form: form
  :param field_one_name: name of the first field
  :param field_two_name: name of the second field
  """
  field_one_data = form.cleaned_data.get(field_one_name, None)
  field_two_data = form.cleaned_data.get(field_two_name, None)
  if field_one_data and field_two_data and field_one_data > field_two_data:
    text = '{} muss zeitlich nach {} liegen.'.format(
      form._meta.model._meta.get_field(field_two_name).verbose_name,
      form._meta.model._meta.get_field(field_one_name).verbose_name,
    )
    raise ValidationError(text)


def mandatory_field_pairs(form, field_one_name, field_two_name, field_three_name=None):
  """
  checks if passed fields are all set (or all not set)
  and raises a validation error if not

  :param form: form
  :param field_one_name: name of the first field
  :param field_two_name: name of the second field
  :param field_three_name: optional name of a third field
  """
  field_one_data = form.cleaned_data.get(field_one_name, None)
  field_two_data = form.cleaned_data.get(field_two_name, None)
  field_three_data = form.cleaned_data.get(field_three_name, None)
  if field_three_name:
    if not (field_one_data is None and field_two_data is None and field_three_data is None) or (
      field_one_data is not None and field_two_data is not None and field_three_data is not None
    ):
      text = '{}, {} und {} müssen immer gemeinsam gesetzt sein.'.format(
        form._meta.model._meta.get_field(field_one_name).verbose_name,
        form._meta.model._meta.get_field(field_two_name).verbose_name,
        form._meta.model._meta.get_field(field_three_name).verbose_name,
      )
      raise ValidationError(text)
  else:
    if (field_two_data and not field_one_data) or (field_one_data and not field_two_data):
      text = '{} und {} müssen immer gemeinsam gesetzt sein.'.format(
        form._meta.model._meta.get_field(field_one_name).verbose_name,
        form._meta.model._meta.get_field(field_two_name).verbose_name,
      )
      raise ValidationError(text)


class DataTypeAdminForm(ModelForm):
  def clean(self):
    mandatory_field_pairs(form=self, field_one_name='format', field_two_name='mime_type')
    return self.cleaned_data


class SpatialReferenceAdminForm(ModelForm):
  def clean(self):
    extent_spatial_south = self.cleaned_data.get('extent_spatial_south', None)
    extent_spatial_east = self.cleaned_data.get('extent_spatial_east', None)
    extent_spatial_north = self.cleaned_data.get('extent_spatial_north', None)
    extent_spatial_west = self.cleaned_data.get('extent_spatial_west', None)
    # extent_spatial_south must be smaller than extent_spatial_north
    if (
      extent_spatial_south and extent_spatial_north and extent_spatial_south > extent_spatial_north
    ):
      text = '{} muss größer sein als {}.'.format(
        self._meta.model._meta.get_field('extent_spatial_north').verbose_name,
        self._meta.model._meta.get_field('extent_spatial_south').verbose_name,
      )
      raise ValidationError(text)
    # extent_spatial_east must be smaller than extent_spatial_west
    if extent_spatial_east and extent_spatial_west and extent_spatial_south > extent_spatial_west:
      text = '{} muss größer sein als {}.'.format(
        self._meta.model._meta.get_field('extent_spatial_west').verbose_name,
        self._meta.model._meta.get_field('extent_spatial_east').verbose_name,
      )
      raise ValidationError(text)
    mandatory_field_pairs(
      form=self, field_one_name='political_geocoding_level', field_two_name='political_geocoding'
    )
    return self.cleaned_data


class ContactAdminForm(ModelForm):
  def clean(self):
    organization = self.cleaned_data.get('organization', None)
    first_name = self.cleaned_data.get('first_name', None)
    last_name = self.cleaned_data.get('last_name', None)
    if not organization and not first_name and not last_name:
      text = '{} muss gesetzt sein, wenn {} und {} nicht gesetzt sind.'.format(
        self._meta.model._meta.get_field('organization').verbose_name,
        self._meta.model._meta.get_field('first_name').verbose_name,
        self._meta.model._meta.get_field('last_name').verbose_name,
      )
      text += ' {} und {} müssen gesetzt sein, wenn {} nicht gesetzt ist.'.format(
        self._meta.model._meta.get_field('first_name').verbose_name,
        self._meta.model._meta.get_field('last_name').verbose_name,
        self._meta.model._meta.get_field('organization').verbose_name,
      )
      raise ValidationError(text)
    elif (not first_name and last_name) or (first_name and not last_name):
      text = '{} und {} müssen immer gemeinsam gesetzt sein.'.format(
        self._meta.model._meta.get_field('first_name').verbose_name,
        self._meta.model._meta.get_field('last_name').verbose_name,
      )
      raise ValidationError(text)
    return self.cleaned_data


class SourceAdminForm(ModelForm):
  def clean(self):
    field_one_mandatory_if_field_two(
      form=self,
      field_one_name='spatial_representation_type',
      field_two_name='geometry_type',
    )
    return self.cleaned_data


class RepositoryAdminForm(ModelForm):
  def clean(self):
    field_one_mandatory_if_field_two(
      form=self,
      field_one_name='spatial_representation_type',
      field_two_name='geometry_type',
    )
    return self.cleaned_data


class DatasetAdminForm(ModelForm):
  def clean(self):
    mandatory_field_pairs(
      form=self, field_one_name='extent_temporal_start', field_two_name='extent_temporal_end'
    )
    field_two_later_than_field_one(
      form=self, field_one_name='extent_temporal_start', field_two_name='extent_temporal_end'
    )
    mandatory_field_pairs(
      form=self, field_one_name='inspire_theme', field_two_name='inspire_spatial_scope'
    )
    mandatory_field_pairs(form=self, field_one_name='language', field_two_name='charset')
    field_one_mandatory_if_field_two(
      form=self,
      field_one_name='spatial_representation_type',
      field_two_name='geometry_type',
    )
    mandatory_field_pairs(form=self, field_one_name='hash_type', field_two_name='hash')
    mandatory_field_pairs(
      form=self, field_one_name='ground_resolution', field_two_name='ground_resolution_uom'
    )
    return self.cleaned_data


class ServiceAdminForm(ModelForm):
  def clean(self):
    mandatory_field_pairs(
      form=self, field_one_name='extent_temporal_start', field_two_name='extent_temporal_end'
    )
    field_two_later_than_field_one(
      form=self, field_one_name='extent_temporal_start', field_two_name='extent_temporal_end'
    )
    mandatory_field_pairs(
      form=self,
      field_one_name='inspire_theme',
      field_two_name='inspire_spatial_scope',
      field_three_name='inspire_service_type',
    )
    datasets = self.cleaned_data.get('datasets', None)
    assetsets = self.cleaned_data.get('assetsets', None)
    repositories = self.cleaned_data.get('repositories', None)
    # at least one dataset, one assetset, or one repository must be linked to the service
    if not datasets and not assetsets and not repositories:
      raise ValidationError(
        'Es muss mindestens ein Datensatz, eine Asset-Sammlung '
        'oder ein Speicherort verknüpft werden.'
      )
    return self.cleaned_data


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
    return ', '.join([str(crs) for crs in obj.crs.all()])

  crs_display.short_description = 'Koordinatenreferenzsystem(e)'


@admin.register(DataType)
class DataTypeAdmin(admin.ModelAdmin):
  form = DataTypeAdminForm
  list_display = ('title', 'format', 'mime_type')
  search_fields = ('title',)
  list_filter = ('format', 'mime_type')
  empty_value_display = ''


@admin.register(Legal)
class LegalAdmin(admin.ModelAdmin):
  list_display = ('title', 'access', 'license', 'constraints')
  search_fields = ('title', 'constraints')
  list_filter = ('access', 'license')
  empty_value_display = ''


@admin.register(SpatialReference)
class SpatialReferenceAdmin(admin.ModelAdmin):
  form = SpatialReferenceAdminForm
  list_display = ('title', 'political_geocoding_level', 'political_geocoding')
  search_fields = ('title',)
  list_filter = ('political_geocoding_level', 'political_geocoding')
  empty_value_display = ''


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
  list_display = ('title', 'name', 'image')
  search_fields = ('title', 'name')
  empty_value_display = ''


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
  form = ContactAdminForm
  list_display = ('email', 'first_name', 'last_name', 'organization')
  search_fields = (
    'email',
    'first_name',
    'last_name',
  )
  list_filter = ('organization',)
  empty_value_display = ''


#
# core models
#


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
  form = SourceAdminForm
  list_display = (
    'uuid',
    'modified',
    'last_import',
    'import_frequency',
    'processing_type',
    'type',
    'connection_info',
    'data_type',
  )
  list_filter = (
    'import_frequency',
    'processing_type',
    'type',
    'data_type',
  )
  search_fields = (
    'uuid',
    'modified',
    'description',
    'last_import',
    'connection_info',
  )
  filter_horizontal = ('authors',)
  empty_value_display = ''
  fieldsets = [
    ('Allgemeine Informationen', {'fields': ['description', 'external', 'authors']}),
    ('Aktualität', {'fields': ['last_import', 'import_frequency']}),
    (
      'Technische Informationen',
      {
        'fields': [
          'processing_type',
          'type',
          'connection_info',
          'data_type',
          'spatial_representation_type',
          'geometry_type',
        ]
      },
    ),
  ]


@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
  form = RepositoryAdminForm
  list_display = (
    'uuid',
    'modified',
    'creation',
    'last_update',
    'update_frequency',
    'type',
    'connection_info',
    'data_type',
    'source',
  )
  list_filter = (
    'update_frequency',
    'type',
    'data_type',
    'source',
  )
  search_fields = (
    'uuid',
    'modified',
    'description',
    'creation',
    'last_update',
    'connection_info',
  )
  filter_horizontal = ('maintainers', 'authors')
  empty_value_display = ''
  fieldsets = [
    (
      'Allgemeine Informationen',
      {'fields': ['description', 'external', 'maintainers', 'authors']},
    ),
    ('Aktualität', {'fields': ['creation', 'last_update', 'update_frequency']}),
    (
      'Technische Informationen',
      {
        'fields': [
          'type',
          'connection_info',
          'data_type',
          'spatial_representation_type',
          'geometry_type',
        ]
      },
    ),
    ('Verknüpfungen', {'fields': ['source']}),
  ]


@admin.register(Assetset)
class AssetsetAdmin(admin.ModelAdmin):
  list_display = (
    'uuid',
    'modified',
    'name',
    'title',
    'creation',
    'last_update',
    'update_frequency',
    'legal',
    'type',
    'repositories_display',
  )
  list_filter = (
    'update_frequency',
    'legal',
    'type',
  )
  search_fields = (
    'uuid',
    'modified',
    'name',
    'title',
    'description',
    'creation',
    'last_update',
  )
  filter_horizontal = ('publishers', 'maintainers', 'repositories')
  empty_value_display = ''
  fieldsets = [
    (
      'Allgemeine Informationen',
      {'fields': ['name', 'title', 'description', 'external', 'publishers', 'maintainers']},
    ),
    ('Aktualität', {'fields': ['creation', 'last_update', 'update_frequency']}),
    ('Rechtliche Informationen', {'fields': ['legal']}),
    ('Technische Informationen', {'fields': ['type']}),
    ('Verknüpfungen', {'fields': ['repositories']}),
  ]

  def repositories_display(self, obj):
    return ', '.join([str(repository) for repository in obj.repositories.all()])

  repositories_display.short_description = 'Speicherort(e)'


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
  form = DatasetAdminForm
  list_display = (
    'uuid',
    'modified',
    'name',
    'title',
    'link',
    'creation',
    'last_update',
    'update_frequency',
    'legal',
    'data_type',
    'repositories_display',
  )
  list_filter = (
    'update_frequency',
    'crs',
    'spatial_reference',
    'legal',
    'inspire_theme',
    'inspire_spatial_scope',
    'language',
    'charset',
    'data_type',
    'spatial_representation_type',
    'geometry_type',
    'hash_type',
    'ground_resolution_uom',
  )
  search_fields = (
    'uuid',
    'modified',
    'name',
    'title',
    'description',
    'link',
    'creation',
    'last_update',
  )
  filter_horizontal = ('tags', 'publishers', 'maintainers', 'repositories')
  empty_value_display = ''
  fieldsets = [
    (
      'Allgemeine Informationen',
      {
        'fields': [
          'name',
          'title',
          'description',
          'link',
          'external',
          'tags',
          'publishers',
          'maintainers',
        ]
      },
    ),
    ('Aktualität', {'fields': ['creation', 'last_update', 'update_frequency']}),
    (
      'Raum-zeitliche Informationen',
      {
        'fields': [
          'crs',
          'spatial_reference',
          'extent_temporal_start',
          'extent_temporal_end',
        ]
      },
    ),
    ('Rechtliche Informationen', {'fields': ['legal']}),
    ('INSPIRE', {'fields': ['inspire_theme', 'inspire_spatial_scope']}),
    (
      'Technische Informationen',
      {
        'fields': [
          'language',
          'charset',
          'data_type',
          'spatial_representation_type',
          'geometry_type',
          'hash_type',
          'hash',
          'byte_size',
          'scale_factor',
          'ground_resolution',
          'ground_resolution_uom',
        ]
      },
    ),
    ('Verknüpfungen', {'fields': ['repositories']}),
  ]

  def repositories_display(self, obj):
    return ', '.join([str(repository) for repository in obj.repositories.all()])

  repositories_display.short_description = 'Speicherort(e)'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
  form = ServiceAdminForm
  list_display = (
    'uuid',
    'modified',
    'name',
    'title',
    'link',
    'legal',
    'type',
    'datasets_display',
    'assetsets_display',
    'repositories_display',
  )
  list_filter = (
    'native_crs',
    'spatial_reference',
    'legal',
    'type',
    'inspire_theme',
    'inspire_spatial_scope',
    'inspire_service_type',
    'language',
    'charset',
  )
  search_fields = (
    'uuid',
    'modified',
    'name',
    'title',
    'description',
    'link',
  )
  filter_horizontal = (
    'tags',
    'additional_crs',
    'publishers',
    'maintainers',
    'datasets',
    'assetsets',
    'repositories',
  )
  empty_value_display = ''
  fieldsets = [
    (
      'Allgemeine Informationen',
      {
        'fields': [
          'name',
          'title',
          'description',
          'link',
          'external',
          'tags',
          'publishers',
          'maintainers',
        ]
      },
    ),
    (
      'Raum-zeitliche Informationen',
      {
        'fields': [
          'native_crs',
          'additional_crs',
          'spatial_reference',
          'extent_temporal_start',
          'extent_temporal_end',
        ]
      },
    ),
    ('Rechtliche Informationen', {'fields': ['legal']}),
    ('INSPIRE', {'fields': ['inspire_theme', 'inspire_spatial_scope', 'inspire_service_type']}),
    (
      'Technische Informationen',
      {
        'fields': [
          'type',
          'language',
          'charset',
        ]
      },
    ),
    ('Verknüpfungen', {'fields': ['datasets', 'assetsets', 'repositories']}),
  ]

  def datasets_display(self, obj):
    return ', '.join([str(dataset) for dataset in obj.datasets.all()])

  def assetsets_display(self, obj):
    return ', '.join([str(assetset) for assetset in obj.assetsets.all()])

  def repositories_display(self, obj):
    return ', '.join([str(repository) for repository in obj.repositories.all()])

  datasets_display.short_description = 'Datensatz/Datensätze'
  assetsets_display.short_description = 'Asset-Sammlung(en)'
  repositories_display.short_description = 'Speicherort(e)'


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
  list_display = (
    'uuid',
    'modified',
    'name',
    'title',
    'categories_display',
    'hvd_category',
    'services_display',
    'datasets_display',
    'assetsets_display',
  )
  list_filter = ('hvd_category',)
  search_fields = (
    'uuid',
    'modified',
    'name',
    'title',
    'description',
  )
  filter_horizontal = (
    'tags',
    'categories',
    'services',
    'datasets',
    'assetsets',
  )
  empty_value_display = ''
  fieldsets = [
    (
      'Allgemeine Informationen',
      {'fields': ['name', 'title', 'description', 'external', 'tags']},
    ),
    ('Kategoriale Informationen', {'fields': ['categories', 'hvd_category']}),
    ('Verknüpfungen', {'fields': ['services', 'datasets', 'assetsets']}),
  ]

  def categories_display(self, obj):
    return ', '.join([str(category) for category in obj.categories.all()])

  def services_display(self, obj):
    return ', '.join([str(service) for service in obj.services.all()])

  def datasets_display(self, obj):
    return ', '.join([str(dataset) for dataset in obj.datasets.all()])

  def assetsets_display(self, obj):
    return ', '.join([str(assetset) for assetset in obj.assetsets.all()])

  categories_display.short_description = 'Kategorie(n)'
  services_display.short_description = 'Service(s)'
  datasets_display.short_description = 'Datensatz/Datensätze'
  assetsets_display.short_description = 'Asset-Sammlung(en)'


@admin.register(App)
class AppAdmin(admin.ModelAdmin):
  list_display = (
    'uuid',
    'modified',
    'name',
    'title',
    'link',
    'legal',
    'topics_display',
    'services_display',
    'datasets_display',
    'assetsets_display',
    'repositories_display',
  )
  list_filter = ('legal',)
  search_fields = (
    'uuid',
    'modified',
    'name',
    'title',
    'link',
    'description',
  )
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
  empty_value_display = ''
  fieldsets = [
    (
      'Allgemeine Informationen',
      {
        'fields': [
          'name',
          'title',
          'description',
          'link',
          'external',
          'tags',
          'publishers',
          'maintainers',
        ]
      },
    ),
    ('Rechtliche Informationen', {'fields': ['legal']}),
    ('Technische Informationen', {'fields': ['languages']}),
    ('Verknüpfungen', {'fields': ['topics', 'services', 'datasets', 'assetsets', 'repositories']}),
  ]

  def topics_display(self, obj):
    return ', '.join([str(topic) for topic in obj.topics.all()])

  def services_display(self, obj):
    return ', '.join([str(service) for service in obj.services.all()])

  def datasets_display(self, obj):
    return ', '.join([str(dataset) for dataset in obj.datasets.all()])

  def assetsets_display(self, obj):
    return ', '.join([str(assetset) for assetset in obj.assetsets.all()])

  def repositories_display(self, obj):
    return ', '.join([str(repository) for repository in obj.repositories.all()])

  topics_display.short_description = 'Datenthema/-themen'
  services_display.short_description = 'Service(s)'
  datasets_display.short_description = 'Datensatz/Datensätze'
  assetsets_display.short_description = 'Asset-Sammlung(en)'
  repositories_display.short_description = 'Speicherort(e)'
