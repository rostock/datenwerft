from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from toolbox.constants_vars import (
  dateiname_message,
  dateiname_regex,
  kleinbuchstaben_bindestrich_message,
  kleinbuchstaben_bindestrich_regex,
  standard_validators,
)

from .abstract import Base, BaseMetadata, CreationalMetadata, SpatioTemporalMetadata
from .auxiliary import (
  Contact,
  CrsSet,
  DataType,
  Legal,
  SpatialReference,
)
from .codelists import (
  AssetType,
  Charset,
  Crs,
  DatathemeCategory,
  Frequency,
  HashType,
  HvdCategory,
  InspireServiceType,
  InspireSpatialScope,
  InspireTheme,
  Language,
  SpatialRepresentationType,
  Tag,
)
from .enums import GeometryType, ProcessingType, RepositoryType, ServiceType, UnitOfMeasurement


class Source(Base, BaseMetadata):
  """
  source (Datenquelle)
  """

  tags = models.ManyToManyField(
    Tag, blank=True, related_name='sources', verbose_name=_('Schlagwort/Schlagwörter')
  )
  last_import = models.DateField(verbose_name=_('Datum des letzten Imports'))
  import_frequency = models.ForeignKey(
    Frequency,
    on_delete=models.PROTECT,
    related_name='source_import_frequencies',
    verbose_name=_('Importhäufigkeit'),
  )
  authors = models.ManyToManyField(
    Contact, related_name='authored_sources', verbose_name=_('Autor(en):in(nen)')
  )
  processing_type = models.CharField(
    choices=ProcessingType.choices, verbose_name=_('Verarbeitungstyp')
  )
  type = models.CharField(choices=RepositoryType.choices, verbose_name=_('Typ'))
  connection_info = models.CharField(
    validators=standard_validators, verbose_name=_('Verbindungsinformation')
  )
  data_type = models.ForeignKey(
    DataType,
    on_delete=models.PROTECT,
    related_name='source_data_types',
    verbose_name=_('Datentyp'),
  )
  spatial_representation_type = models.ForeignKey(
    SpatialRepresentationType,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='source_spatial_representation_types',
    verbose_name=_('Typ der räumlichen Repräsentation'),
  )
  geometry_type = models.CharField(
    choices=GeometryType.choices,
    blank=True,
    null=True,
    verbose_name=_('Geometrietyp'),
  )

  class Meta(Base.Meta):
    ordering = ['connection_info']
    verbose_name = _('Datenquelle')
    verbose_name_plural = _('Datenquellen')

  def __str__(self):
    type_display = self.get_type_display() if hasattr(self, 'get_type_display') else self.type
    return f'{type_display} ({self.connection_info})'


class Repository(Base, BaseMetadata, CreationalMetadata):
  """
  repository (Speicherort)
  """

  tags = models.ManyToManyField(
    Tag, blank=True, related_name='repositories', verbose_name=_('Schlagwort/Schlagwörter')
  )
  update_frequency = models.ForeignKey(
    Frequency,
    on_delete=models.PROTECT,
    related_name='repository_update_frequencies',
    verbose_name=_('Aktualisierungshäufigkeit'),
  )
  maintainers = models.ManyToManyField(
    Contact, related_name='maintained_repositories', verbose_name=_('Betreuer:in(nen)')
  )
  authors = models.ManyToManyField(
    Contact, related_name='authored_repositories', verbose_name=_('Autor(en):in(nen)')
  )
  type = models.CharField(choices=RepositoryType.choices, verbose_name=_('Typ'))
  connection_info = models.CharField(
    validators=standard_validators, verbose_name=_('Verbindungsinformation')
  )
  data_type = models.ForeignKey(
    DataType,
    on_delete=models.PROTECT,
    related_name='repository_data_types',
    verbose_name=_('Datentyp'),
  )
  spatial_representation_type = models.ForeignKey(
    SpatialRepresentationType,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='repository_spatial_representation_types',
    verbose_name=_('Typ der räumlichen Repräsentation'),
  )
  geometry_type = models.CharField(
    choices=GeometryType.choices,
    blank=True,
    null=True,
    verbose_name=_('Geometrietyp'),
  )
  source = models.ForeignKey(
    Source,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='repository_sources',
    verbose_name=_('Datenquelle'),
  )

  class Meta(Base.Meta):
    ordering = ['connection_info']
    verbose_name = _('Speicherort')
    verbose_name_plural = _('Speicherorte')

  def __str__(self):
    type_display = self.get_type_display() if hasattr(self, 'get_type_display') else self.type
    return f'{type_display} ({self.connection_info})'


class Assetset(Base, BaseMetadata, CreationalMetadata):
  """
  asset-set (Asset-Sammlung)
  """

  name = models.CharField(
    unique=True,
    validators=[
      RegexValidator(
        regex=kleinbuchstaben_bindestrich_regex, message=kleinbuchstaben_bindestrich_message
      )
    ],
    verbose_name=_('Name'),
  )
  title = models.CharField(
    blank=True, null=True, validators=standard_validators, verbose_name=_('Titel')
  )
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='assetsets', verbose_name=_('Schlagwort/Schlagwörter')
  )
  update_frequency = models.ForeignKey(
    Frequency,
    on_delete=models.PROTECT,
    related_name='assetset_update_frequencies',
    verbose_name=_('Aktualisierungshäufigkeit'),
  )
  publishers = models.ManyToManyField(
    Contact, related_name='published_assetsets', verbose_name=_('Herausgeber:in(nen)')
  )
  maintainers = models.ManyToManyField(
    Contact, related_name='maintained_assetsets', verbose_name=_('Betreuer:in(nen)')
  )
  legal = models.ForeignKey(
    Legal, on_delete=models.PROTECT, related_name='assetset_legals', verbose_name=_('Rechtsstatus')
  )
  type = models.ForeignKey(
    AssetType, on_delete=models.PROTECT, related_name='assetset_types', verbose_name=_('Typ')
  )
  repositories = models.ManyToManyField(
    Repository, blank=True, related_name='assetsets', verbose_name=_('Speicherort(e)')
  )

  class Meta(Base.Meta):
    ordering = ['title', 'name']
    verbose_name = _('Asset-Sammlung')
    verbose_name_plural = _('Asset-Sammlungen')

  def __str__(self):
    return self.title or self.name


class Dataset(Base, BaseMetadata, CreationalMetadata, SpatioTemporalMetadata):
  """
  dataset (Datensatz)
  """

  name = models.CharField(
    unique=True,
    validators=[RegexValidator(regex=dateiname_regex, message=dateiname_message)],
    verbose_name=_('Name'),
  )
  title = models.CharField(validators=standard_validators, verbose_name=_('Titel'))
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='datasets', verbose_name=_('Schlagwort/Schlagwörter')
  )
  update_frequency = models.ForeignKey(
    Frequency,
    on_delete=models.PROTECT,
    related_name='dataset_update_frequencies',
    verbose_name=_('Aktualisierungshäufigkeit'),
  )
  native_crs = models.ForeignKey(
    Crs,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='dataset_native_crs',
    verbose_name=_('Natives Koordinatenreferenzsystem'),
  )
  additional_crs = models.ManyToManyField(
    CrsSet,
    blank=True,
    related_name='datasets',
    verbose_name=_('Zusätzliche(s) Koordinatenreferenzsystem(e)'),
  )
  spatial_reference = models.ForeignKey(
    SpatialReference,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='dataset_spatial_references',
    verbose_name=_('Raumbezug'),
  )
  publishers = models.ManyToManyField(
    Contact, related_name='published_datasets', verbose_name=_('Herausgeber:in(nen)')
  )
  maintainers = models.ManyToManyField(
    Contact, related_name='maintained_datasets', verbose_name=_('Betreuer:in(nen)')
  )
  legal = models.ForeignKey(
    Legal, on_delete=models.PROTECT, related_name='dataset_legals', verbose_name=_('Rechtsstatus')
  )
  inspire_theme = models.ForeignKey(
    InspireTheme,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='dataset_inspire_themes',
    verbose_name=_('INSPIRE-Thema'),
  )
  inspire_spatial_scope = models.ForeignKey(
    InspireSpatialScope,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='dataset_inspire_spatial_scopes',
    verbose_name=_('INSPIRE-Raumbezug'),
  )
  language = models.ForeignKey(
    Language, on_delete=models.PROTECT, related_name='dataset_languages', verbose_name=_('Sprache')
  )
  charset = models.ForeignKey(
    Charset,
    on_delete=models.PROTECT,
    related_name='dataset_charsets',
    verbose_name=_('Zeichensatz'),
  )
  data_type = models.ForeignKey(
    DataType,
    on_delete=models.PROTECT,
    related_name='dataset_data_types',
    verbose_name=_('Datentyp'),
  )
  spatial_representation_type = models.ForeignKey(
    SpatialRepresentationType,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='dataset_spatial_representation_types',
    verbose_name=_('Typ der räumlichen Repräsentation'),
  )
  geometry_type = models.CharField(
    choices=GeometryType.choices,
    blank=True,
    null=True,
    verbose_name=_('Geometrietyp'),
  )
  hash_type = models.ForeignKey(
    HashType,
    on_delete=models.PROTECT,
    related_name='dataset_hash_types',
    verbose_name=_('Typ des Hashes'),
  )
  hash = models.CharField(validators=standard_validators, verbose_name=_('Hash-Wert'))
  byte_size = models.PositiveIntegerField(verbose_name=_('Größe in der Einheit Byte'))
  scale_factor = models.PositiveIntegerField(
    blank=True, null=True, verbose_name=_('Maßstabsfaktor')
  )
  ground_resolution = models.DecimalField(
    max_digits=4, decimal_places=2, blank=True, null=True, verbose_name=_('Bodenauflösung')
  )
  ground_resolution_uom = models.CharField(
    choices=UnitOfMeasurement.choices,
    blank=True,
    null=True,
    verbose_name=_('Maßeinheit der Bodenauflösung'),
  )
  repositories = models.ManyToManyField(
    Repository, blank=True, related_name='datasets', verbose_name=_('Speicherort(e)')
  )

  class Meta(Base.Meta):
    ordering = ['title']
    verbose_name = _('Datensatz')
    verbose_name_plural = _('Datensätze')

  def __str__(self):
    return self.title


class Service(Base, BaseMetadata, SpatioTemporalMetadata):
  """
  service (Service)
  """

  name = models.CharField(
    validators=[
      RegexValidator(
        regex=kleinbuchstaben_bindestrich_regex, message=kleinbuchstaben_bindestrich_message
      )
    ],
    verbose_name=_('Name'),
  )
  title = models.CharField(validators=standard_validators, verbose_name=_('Titel'))
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='services', verbose_name=_('Schlagwort/Schlagwörter')
  )
  native_crs = models.ForeignKey(
    Crs,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='service_native_crs',
    verbose_name=_('Natives Koordinatenreferenzsystem'),
  )
  additional_crs = models.ManyToManyField(
    CrsSet,
    blank=True,
    related_name='services',
    verbose_name=_('Zusätzliche(s) Koordinatenreferenzsystem(e)'),
  )
  spatial_reference = models.ForeignKey(
    SpatialReference,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='service_spatial_references',
    verbose_name=_('Raumbezug'),
  )
  publishers = models.ManyToManyField(
    Contact, related_name='published_services', verbose_name=_('Herausgeber:in(nen)')
  )
  maintainers = models.ManyToManyField(
    Contact, related_name='maintained_services', verbose_name=_('Betreuer:in(nen)')
  )
  legal = models.ForeignKey(
    Legal, on_delete=models.PROTECT, related_name='service_legals', verbose_name=_('Rechtsstatus')
  )
  type = models.CharField(choices=ServiceType.choices, verbose_name=_('Typ'))
  inspire_theme = models.ForeignKey(
    InspireTheme,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='service_inspire_themes',
    verbose_name=_('INSPIRE-Thema'),
  )
  inspire_spatial_scope = models.ForeignKey(
    InspireSpatialScope,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='service_inspire_spatial_scopes',
    verbose_name=_('INSPIRE-Raumbezug'),
  )
  inspire_service_type = models.ForeignKey(
    InspireServiceType,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='service_inspire_service_types',
    verbose_name=_('Typ des INSPIRE-Services'),
  )
  language = models.ForeignKey(
    Language, on_delete=models.PROTECT, related_name='service_languages', verbose_name=_('Sprache')
  )
  charset = models.ForeignKey(
    Charset,
    on_delete=models.PROTECT,
    related_name='service_charsets',
    verbose_name=_('Zeichensatz'),
  )
  datasets = models.ManyToManyField(
    Dataset, blank=True, related_name='services', verbose_name=_('Datensatz/Datensätze')
  )
  assetsets = models.ManyToManyField(
    Assetset, blank=True, related_name='services', verbose_name=_('Asset-Sammlung(en)')
  )
  repositories = models.ManyToManyField(
    Repository, blank=True, related_name='services', verbose_name=_('Speicherort(e)')
  )

  class Meta(Base.Meta):
    unique_together = ('name', 'type')
    ordering = ['title']
    verbose_name = _('Service')
    verbose_name_plural = _('Services')

  def __str__(self):
    return f'{self.title} ({self.get_type_display()})'


class Topic(Base, BaseMetadata):
  """
  topic (Datenthema)
  """

  name = models.CharField(
    unique=True,
    validators=[
      RegexValidator(
        regex=kleinbuchstaben_bindestrich_regex, message=kleinbuchstaben_bindestrich_message
      )
    ],
    verbose_name=_('Name'),
  )
  title = models.CharField(validators=standard_validators, verbose_name=_('Titel'))
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='topics', verbose_name=_('Schlagwort/Schlagwörter')
  )
  categories = models.ManyToManyField(
    DatathemeCategory, related_name='topics', verbose_name=_('Kategorie(n)')
  )
  hvd_category = models.ForeignKey(
    HvdCategory,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name='topic_hvd_categories',
    verbose_name=_('HVD-Kategorie'),
  )
  services = models.ManyToManyField(
    Service, blank=True, related_name='topics', verbose_name=_('Service(s)')
  )
  datasets = models.ManyToManyField(
    Dataset, blank=True, related_name='topics', verbose_name=_('Datensatz/Datensätze')
  )
  assetsets = models.ManyToManyField(
    Assetset, blank=True, related_name='topics', verbose_name=_('Asset-Sammlung(en)')
  )

  class Meta(Base.Meta):
    ordering = ['title']
    verbose_name = _('Datenthema')
    verbose_name_plural = _('Datenthemen')

  def __str__(self):
    return self.title


class App(Base, BaseMetadata):
  """
  app (App)
  """

  name = models.CharField(
    unique=True,
    validators=[
      RegexValidator(
        regex=kleinbuchstaben_bindestrich_regex, message=kleinbuchstaben_bindestrich_message
      )
    ],
    verbose_name=_('Name'),
  )
  title = models.CharField(validators=standard_validators, verbose_name=_('Titel'))
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='apps', verbose_name=_('Schlagwort/Schlagwörter')
  )
  publishers = models.ManyToManyField(
    Contact, related_name='published_apps', verbose_name=_('Herausgeber:in(nen)')
  )
  maintainers = models.ManyToManyField(
    Contact, related_name='maintained_apps', verbose_name=_('Betreuer:in(nen)')
  )
  legal = models.ForeignKey(
    Legal, on_delete=models.PROTECT, related_name='app_legals', verbose_name=_('Rechtsstatus')
  )
  languages = models.ManyToManyField(Language, related_name='apps', verbose_name=_('Sprache(n)'))
  topics = models.ManyToManyField(
    Topic, blank=True, related_name='apps', verbose_name=_('Datenthema/-themen')
  )
  services = models.ManyToManyField(
    Service, blank=True, related_name='apps', verbose_name=_('Service(s)')
  )
  datasets = models.ManyToManyField(
    Dataset, blank=True, related_name='apps', verbose_name=_('Datensatz/Datensätze')
  )
  assetsets = models.ManyToManyField(
    Assetset, blank=True, related_name='apps', verbose_name=_('Asset-Sammlung(en)')
  )
  repositories = models.ManyToManyField(
    Repository, blank=True, related_name='apps', verbose_name=_('Speicherort(e)')
  )

  class Meta(Base.Meta):
    ordering = ['title']
    verbose_name = _('App')
    verbose_name_plural = _('Apps')

  def __str__(self):
    return self.title
