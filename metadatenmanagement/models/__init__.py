# Importiere Enums, damit sie leicht zugänglich sind
# Importiere abstrakte Klassen (optional, je nach Bedarf)
from .abstract import Base, BaseMetadata, Codelist, CreationalMetadata, SpatioTemporalMetadata

# Importiere Hilfsmodelle
from .auxiliary import Contact, CrsSet, DataType, Legal, Organization, SpatialReference

# Importiere alle konkreten Codelisten-Modelle
from .codelists import (
  Access,
  AssetType,
  Charset,
  Crs,
  DatathemeCategory,
  Format,
  Frequency,
  HashType,
  HvdCategory,
  InspireServiceType,
  InspireSpatialScope,
  InspireTheme,
  Language,
  License,
  MimeType,
  PoliticalGeocoding,
  PoliticalGeocodingLevel,
  SpatialRepresentationType,
  Tag,
)

# Importiere Kernmodelle
from .core import App, Assetset, Dataset, Repository, Service, Source, Theme
from .enums import GeometryType, ProcessingType, RepositoryType, ServiceType, UnitOfMeasurement

# Optional: __all__ definieren, um explizit zu machen, was exportiert wird
# Hilft Werkzeugen wie linters und verbessert die Klarheit
__all__ = [
  # Enums
  'GeometryType',
  'ProcessingType',
  'RepositoryType',
  'ServiceType',
  'UnitOfMeasurement',
  # Abstrakte Klassen (falls benötigt)
  'Base',
  'Codelist',
  'BaseMetadata',
  'CreationalMetadata',
  'SpatioTemporalMetadata',
  # Codelisten
  'Access',
  'AssetType',
  'Charset',
  'Crs',
  'DatathemeCategory',
  'Format',
  'Frequency',
  'HashType',
  'HvdCategory',
  'InspireServiceType',
  'InspireSpatialScope',
  'InspireTheme',
  'Language',
  'License',
  'MimeType',
  'PoliticalGeocoding',
  'PoliticalGeocodingLevel',
  'SpatialRepresentationType',
  'Tag',
  # Hilfsmodelle
  'CrsSet',
  'DataType',
  'Legal',
  'SpatialReference',
  'Organization',
  'Contact',
  # Kernmodelle
  'App',
  'Theme',
  'Service',
  'Dataset',
  'Assetset',
  'Source',
  'Repository',
]
