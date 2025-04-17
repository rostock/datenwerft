from django.db import models
from django.utils.translation import gettext_lazy as _

# Importiere abstrakte Klassen
from .abstract import Base, BaseMetadata, CreationalMetadata, SpatioTemporalMetadata
from .auxiliary import (
  Contact,  # Source wird hier definiert, aber referenziert
  CrsSet,
  DataType,
  Legal,
  SpatialReference,
)

# Importiere Hilfsmodelle und Codelisten
# Verwende String-Referenzen ('app_name.ModelName' oder 'ModelName' wenn im selben App-models-Paket)
# oder direkte Imports, da __init__.py sie verfügbar macht.
# Direkte Imports sind hier meist ok, aber String-Referenzen sind robuster gegen Zirkelbezüge.
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

# Importiere Enums
from .enums import GeometryType, ProcessingType, RepositoryType, ServiceType, UnitOfMeasurement

# ------------- Kernmodelle -------------


class App(Base, BaseMetadata):
  """Modell für Anwendungen (Apps)."""

  name = models.TextField(unique=True, verbose_name=_('Name (intern)'))
  title = models.TextField(verbose_name=_('Titel'))
  # ManyToMany Beziehungen (M2M)
  publisher = models.ManyToManyField(
    Contact, related_name='published_apps', verbose_name=_('Herausgeber')
  )
  maintainer = models.ManyToManyField(
    Contact, related_name='maintained_apps', verbose_name=_('Betreuer')
  )
  language = models.ManyToManyField(Language, verbose_name=_('Sprache(n)'))
  # M2M zu anderen Kernmodellen (String-Referenz empfohlen)
  theme = models.ManyToManyField(
    'Theme', blank=True, related_name='apps', verbose_name=_('Thema/Themen')
  )
  service = models.ManyToManyField(
    'Service', blank=True, related_name='apps', verbose_name=_('Dienst(e)')
  )
  dataset = models.ManyToManyField(
    'Dataset', blank=True, related_name='apps', verbose_name=_('Datensatz/Datensätze')
  )
  assetset = models.ManyToManyField(
    'Assetset', blank=True, related_name='apps', verbose_name=_('Asset-Set(s)')
  )
  repository = models.ManyToManyField(
    'Repository', blank=True, related_name='apps', verbose_name=_('Repository(s)')
  )
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='apps', verbose_name=_('Schlagwörter')
  )
  # ForeignKey (FK)
  legal = models.ForeignKey(
    Legal, on_delete=models.PROTECT, verbose_name=_('Rechtliche Informationen')
  )

  def __str__(self):
    return self.title


class Theme(Base, BaseMetadata):
  """Modell für Themen."""

  name = models.TextField(unique=True, verbose_name=_('Name (intern)'))
  title = models.TextField(verbose_name=_('Titel'))
  # M2M
  category = models.ManyToManyField(DatathemeCategory, verbose_name=_('Kategorie(n)'))
  service = models.ManyToManyField(
    'Service', blank=True, related_name='themes', verbose_name=_('Dienst(e)')
  )
  dataset = models.ManyToManyField(
    'Dataset', blank=True, related_name='themes', verbose_name=_('Datensatz/Datensätze')
  )
  assetset = models.ManyToManyField(
    'Assetset', blank=True, related_name='themes', verbose_name=_('Asset-Set(s)')
  )
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='themes', verbose_name=_('Schlagwörter')
  )
  # FK
  hvd_category = models.ForeignKey(
    HvdCategory, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('HVD Kategorie')
  )

  def __str__(self):
    return self.title


class Service(Base, BaseMetadata, SpatioTemporalMetadata):
  """Modell für Dienste."""

  name = models.TextField(verbose_name=_('Name'))
  title = models.TextField(verbose_name=_('Titel'))
  type = models.CharField(max_length=50, choices=ServiceType.choices, verbose_name=_('Diensttyp'))
  # M2M
  publisher = models.ManyToManyField(
    Contact, related_name='published_services', verbose_name=_('Herausgeber')
  )
  maintainer = models.ManyToManyField(
    Contact, related_name='maintained_services', verbose_name=_('Betreuer')
  )
  dataset = models.ManyToManyField(
    'Dataset', blank=True, related_name='services', verbose_name=_('Datensatz/Datensätze')
  )
  assetset = models.ManyToManyField(
    'Assetset', blank=True, related_name='services', verbose_name=_('Asset-Set(s)')
  )
  repository = models.ManyToManyField(
    'Repository', blank=True, related_name='services', verbose_name=_('Repository(s)')
  )
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='services', verbose_name=_('Schlagwörter')
  )
  additional_crs = models.ManyToManyField(
    CrsSet, blank=True, related_name='additional_services', verbose_name=_('Zusätzliche CRS Sets')
  )
  # FK
  legal = models.ForeignKey(
    Legal, on_delete=models.PROTECT, verbose_name=_('Rechtliche Informationen')
  )
  inspire_theme = models.ForeignKey(
    InspireTheme, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('INSPIRE Thema')
  )
  inspire_spatial_scope = models.ForeignKey(
    InspireSpatialScope,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    verbose_name=_('INSPIRE Räumlicher Geltungsbereich'),
  )
  inspire_service_type = models.ForeignKey(
    InspireServiceType,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    verbose_name=_('INSPIRE Diensttyp'),
  )
  language = models.ForeignKey(Language, on_delete=models.PROTECT, verbose_name=_('Sprache'))
  charset = models.ForeignKey(Charset, on_delete=models.PROTECT, verbose_name=_('Zeichensatz'))
  native_crs = models.ForeignKey(
    Crs,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    related_name='native_services',
    verbose_name=_('Natives CRS'),
  )
  spatial_reference = models.ForeignKey(
    SpatialReference,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    related_name='services',
    verbose_name=_('Räumliche Referenz'),
  )

  class Meta:
    # Eindeutigkeit für Name und Typ zusammen
    unique_together = ('name', 'type')
    verbose_name = _('Dienst')
    verbose_name_plural = _('Dienste')

  def __str__(self):
    return f'{self.title} ({self.get_type_display()})'


class Dataset(Base, BaseMetadata, CreationalMetadata, SpatioTemporalMetadata):
  """Modell für Datensätze."""

  name = models.TextField(unique=True, verbose_name=_('Name (intern)'))
  title = models.TextField(verbose_name=_('Titel'))
  geometry_type = models.CharField(
    max_length=50,
    choices=GeometryType.choices,
    blank=True,
    null=True,
    verbose_name=_('Geometrietyp'),
  )
  hash = models.TextField(verbose_name=_('Hash-Wert'))
  byte_size = models.BigIntegerField(verbose_name=_('Größe in Bytes'))
  scale_factor = models.IntegerField(blank=True, null=True, verbose_name=_('Maßstabsfaktor'))
  ground_resolution = models.DecimalField(
    max_digits=10, decimal_places=2, blank=True, null=True, verbose_name=_('Bodenauflösung')
  )
  ground_resolution_uom = models.CharField(
    max_length=5,
    choices=UnitOfMeasurement.choices,
    blank=True,
    null=True,
    verbose_name=_('Einheit der Bodenauflösung'),
  )
  # M2M
  publisher = models.ManyToManyField(
    Contact, related_name='published_datasets', verbose_name=_('Herausgeber')
  )
  maintainer = models.ManyToManyField(
    Contact, related_name='maintained_datasets', verbose_name=_('Betreuer')
  )
  repository = models.ManyToManyField(
    'Repository', related_name='datasets', verbose_name=_('Repository(s)')
  )
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='datasets', verbose_name=_('Schlagwörter')
  )
  additional_crs = models.ManyToManyField(
    CrsSet, blank=True, related_name='additional_datasets', verbose_name=_('Zusätzliche CRS Sets')
  )
  # FK
  legal = models.ForeignKey(
    Legal, on_delete=models.PROTECT, verbose_name=_('Rechtliche Informationen')
  )
  inspire_theme = models.ForeignKey(
    InspireTheme, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('INSPIRE Thema')
  )
  inspire_spatial_scope = models.ForeignKey(
    InspireSpatialScope,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    verbose_name=_('INSPIRE Räumlicher Geltungsbereich'),
  )
  language = models.ForeignKey(Language, on_delete=models.PROTECT, verbose_name=_('Sprache'))
  charset = models.ForeignKey(Charset, on_delete=models.PROTECT, verbose_name=_('Zeichensatz'))
  data_type = models.ForeignKey(DataType, on_delete=models.PROTECT, verbose_name=_('Datentyp'))
  spatial_representation_type = models.ForeignKey(
    SpatialRepresentationType,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    verbose_name=_('Räumlicher Repräsentationstyp'),
  )
  hash_type = models.ForeignKey(HashType, on_delete=models.PROTECT, verbose_name=_('Hash-Typ'))
  update_frequency = models.ForeignKey(
    Frequency,
    on_delete=models.PROTECT,
    related_name='datasets',
    verbose_name=_('Aktualisierungshäufigkeit'),
  )
  native_crs = models.ForeignKey(
    Crs,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    related_name='native_datasets',
    verbose_name=_('Natives CRS'),
  )
  spatial_reference = models.ForeignKey(
    SpatialReference,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    related_name='datasets',
    verbose_name=_('Räumliche Referenz'),
  )

  class Meta:
    verbose_name = _('Datensatz')
    verbose_name_plural = _('Datensätze')

  def __str__(self):
    return self.title


class Assetset(Base, BaseMetadata, CreationalMetadata):
  """Modell für Asset-Sets."""

  name = models.TextField(unique=True, verbose_name=_('Name (intern)'))
  title = models.TextField(blank=True, null=True, verbose_name=_('Titel'))
  # M2M
  publisher = models.ManyToManyField(
    Contact, related_name='published_assetsets', verbose_name=_('Herausgeber')
  )
  maintainer = models.ManyToManyField(
    Contact, related_name='maintained_assetsets', verbose_name=_('Betreuer')
  )
  repository = models.ManyToManyField(
    'Repository', related_name='assetsets', verbose_name=_('Repository(s)')
  )
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='assetsets', verbose_name=_('Schlagwörter')
  )
  # FK
  legal = models.ForeignKey(
    Legal, on_delete=models.PROTECT, verbose_name=_('Rechtliche Informationen')
  )
  type = models.ForeignKey(AssetType, on_delete=models.PROTECT, verbose_name=_('Asset-Typ'))
  update_frequency = models.ForeignKey(
    Frequency,
    on_delete=models.PROTECT,
    related_name='assetsets',
    verbose_name=_('Aktualisierungshäufigkeit'),
  )

  class Meta:
    verbose_name = _('Asset-Set')
    verbose_name_plural = _('Asset-Sets')

  def __str__(self):
    return self.title or self.name


class Source(Base, BaseMetadata):
  """Modell für Datenquellen (Sources)."""

  last_import = models.DateField(verbose_name=_('Letzter Import'))
  processing_type = models.CharField(
    max_length=20, choices=ProcessingType.choices, verbose_name=_('Verarbeitungstyp')
  )
  type = models.CharField(
    max_length=20, choices=RepositoryType.choices, verbose_name=_('Quelltyp')
  )
  connection_info = models.TextField(verbose_name=_('Verbindungsinformationen'))
  geometry_type = models.CharField(
    max_length=50,
    choices=GeometryType.choices,
    blank=True,
    null=True,
    verbose_name=_('Geometrietyp'),
  )
  # M2M
  author = models.ManyToManyField(
    Contact, related_name='authored_sources', verbose_name=_('Autor(en)')
  )
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='sources', verbose_name=_('Schlagwörter')
  )
  # FK
  import_frequency = models.ForeignKey(
    Frequency, on_delete=models.PROTECT, verbose_name=_('Import-Häufigkeit')
  )
  data_type = models.ForeignKey(DataType, on_delete=models.PROTECT, verbose_name=_('Datentyp'))
  spatial_representation_type = models.ForeignKey(
    SpatialRepresentationType,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    verbose_name=_('Räumlicher Repräsentationstyp'),
  )

  class Meta:
    verbose_name = _('Quelle')
    verbose_name_plural = _('Quellen')

  def __str__(self):
    # Holt den lesbaren Wert des Enum-Typs
    type_display = self.get_type_display() if hasattr(self, 'get_type_display') else self.type
    return f'{type_display} - {self.connection_info[:50]}'  # Kurze Darstellung


class Repository(Base, BaseMetadata, CreationalMetadata):
  """Modell für Repositories."""

  type = models.CharField(
    max_length=20, choices=RepositoryType.choices, verbose_name=_('Repository-Typ')
  )
  connection_info = models.TextField(verbose_name=_('Verbindungsinformationen'))
  geometry_type = models.CharField(
    max_length=50,
    choices=GeometryType.choices,
    blank=True,
    null=True,
    verbose_name=_('Geometrietyp'),
  )
  # M2M
  maintainer = models.ManyToManyField(
    Contact, related_name='maintained_repositories', verbose_name=_('Betreuer')
  )
  author = models.ManyToManyField(
    Contact, related_name='authored_repositories', verbose_name=_('Autor(en)')
  )
  tags = models.ManyToManyField(
    Tag, blank=True, related_name='repositories', verbose_name=_('Schlagwörter')
  )
  # FK
  data_type = models.ForeignKey(DataType, on_delete=models.PROTECT, verbose_name=_('Datentyp'))
  spatial_representation_type = models.ForeignKey(
    SpatialRepresentationType,
    on_delete=models.SET_NULL,
    blank=True,
    null=True,
    verbose_name=_('Räumlicher Repräsentationstyp'),
  )
  # Erlaube Null für Source, da es optional ist [0..1]
  source = models.ForeignKey(
    Source, on_delete=models.SET_NULL, blank=True, null=True, verbose_name=_('Quelle')
  )
  update_frequency = models.ForeignKey(
    Frequency,
    on_delete=models.PROTECT,
    related_name='repositories',
    verbose_name=_('Aktualisierungshäufigkeit'),
  )

  class Meta:
    verbose_name = _('Repository')
    verbose_name_plural = _('Repositories')

  def __str__(self):
    # Holt den lesbaren Wert des Enum-Typs
    type_display = self.get_type_display() if hasattr(self, 'get_type_display') else self.type
    return f'{type_display} - {self.connection_info[:50]}'  # Kurze Darstellung
