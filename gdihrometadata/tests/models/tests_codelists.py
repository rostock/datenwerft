from gdihrometadata.models import (
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

from ..base import DefaultCodelistTestCase


class AccessModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  access (Zugriff)
  """

  model = Access
  attributes_values_db_initial = {
    'code': 'https://example.org/access/initial',
    'title': 'InitialAccess',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/access/updated',
    'title': 'UpdatedAccess',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class AssetTypeModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  asset type (Typ eines Assets)
  """

  model = AssetType
  attributes_values_db_initial = {
    'code': 'https://example.org/assettype/initial',
    'title': 'InitialAssetType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/assettype/updated',
    'title': 'UpdatedAssetType',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CharsetModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  charset (Zeichensatz)
  """

  model = Charset
  attributes_values_db_initial = {
    'code': 'https://example.org/charset/initial',
    'title': 'InitialCharset',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/charset/updated',
    'title': 'UpdatedCharset',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class CrsModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  coordinate reference system (Koordinatenreferenzsystem)
  """

  model = Crs
  attributes_values_db_initial = {
    'code': 'https://example.org/crs/initial',
    'title': 'InitialCrs',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/crs/updated',
    'title': 'UpdatedCrs',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class DatathemeCategoryModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  data theme category (Datenthemenkategorie)
  """

  model = DatathemeCategory
  attributes_values_db_initial = {
    'code': 'https://example.org/datathemecategory/initial',
    'title': 'InitialDatathemeCategory',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/datathemecategory/updated',
    'title': 'UpdatedDatathemeCategory',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class FormatModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  format (Format)
  """

  model = Format
  attributes_values_db_initial = {
    'code': 'https://example.org/format/initial',
    'title': 'InitialFormat',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/format/updated',
    'title': 'UpdatedFormat',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class FrequencyModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  frequency (Häufigkeit)
  """

  model = Frequency
  attributes_values_db_initial = {
    'code': 'https://example.org/frequency/initial',
    'title': 'InitialFrequency',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/frequency/updated',
    'title': 'UpdatedFrequency',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class HashTypeModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  hash type (Typ eines Hashes)
  """

  model = HashType
  attributes_values_db_initial = {
    'code': 'https://example.org/hashtype/initial',
    'title': 'InitialHashType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/hashtype/updated',
    'title': 'UpdatedHashType',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class HvdCategoryModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  high-value dataset category (HVD-Kategorie)
  """

  model = HvdCategory
  attributes_values_db_initial = {
    'code': 'https://example.org/hvdcategory/initial',
    'title': 'InitialHvdCategory',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/hvdcategory/updated',
    'title': 'UpdatedHvdCategory',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class InspireServiceTypeModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  INSPIRE service type (Typ eines INSPIRE-Services)
  """

  model = InspireServiceType
  attributes_values_db_initial = {
    'code': 'https://example.org/inspireservicetype/initial',
    'title': 'InitialInspireServiceType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/inspireservicetype/updated',
    'title': 'UpdatedInspireServiceType',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class InspireSpatialScopeModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  INSPIRE spatial scope (räumlicher INSPIRE-Bezugsbereich)
  """

  model = InspireSpatialScope
  attributes_values_db_initial = {
    'code': 'https://example.org/inspirespatialscope/initial',
    'title': 'InitialInspireSpatialScope',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/inspirespatialscope/updated',
    'title': 'UpdatedInspireSpatialScope',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class InspireThemeModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  INSPIRE theme (INSPIRE-Thema)
  """

  model = InspireTheme
  attributes_values_db_initial = {
    'code': 'https://example.org/inspiretheme/initial',
    'title': 'InitialInspireTheme',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/inspiretheme/updated',
    'title': 'UpdatedInspireTheme',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class LanguageModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  language (Sprache)
  """

  model = Language
  attributes_values_db_initial = {
    'code': 'https://example.org/language/initial',
    'title': 'InitialLanguage',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/language/updated',
    'title': 'UpdatedLanguage',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class LicenseModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  license (Lizenz)
  """

  model = License
  attributes_values_db_initial = {
    'code': 'https://example.org/license/initial',
    'title': 'InitialLicense',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/license/updated',
    'title': 'UpdatedLicense',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class MimeTypeModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  MIME type (MIME-Typ)
  """

  model = MimeType
  attributes_values_db_initial = {
    'code': 'https://example.org/mimetype/initial',
    'title': 'InitialMimeType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/mimetype/updated',
    'title': 'UpdatedMimeType',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class PoliticalGeocodingModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  political geocoding (geopolitische Verwaltungscodierung)
  """

  model = PoliticalGeocoding
  attributes_values_db_initial = {
    'code': 'https://example.org/politicalgeocoding/initial',
    'title': 'InitialPoliticalGeocoding',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/politicalgeocoding/updated',
    'title': 'UpdatedPoliticalGeocoding',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class PoliticalGeocodingLevelModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  political geocoding level (Ebene der geopolitischen Verwaltungscodierung)
  """

  model = PoliticalGeocodingLevel
  attributes_values_db_initial = {
    'code': 'https://example.org/politicalgeocodinglevel/initial',
    'title': 'InitialPoliticalGeocodingLevel',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/politicalgeocodinglevel/updated',
    'title': 'UpdatedPoliticalGeocodingLevel',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class SpatialRepresentationTypeModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  spatial representation type (Typ der räumlichen Repräsentation)
  """

  model = SpatialRepresentationType
  attributes_values_db_initial = {
    'code': 'https://example.org/spatialrepresentationtype/initial',
    'title': 'InitialSpatialRepresentationType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/spatialrepresentationtype/updated',
    'title': 'UpdatedSpatialRepresentationType',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()


class TagModelTest(DefaultCodelistTestCase):
  """
  test class for codelist:
  tag (Schlagwort)
  """

  model = Tag
  attributes_values_db_initial = {
    'code': 'https://example.org/tag/initial',
    'title': 'InitialTag',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/tag/updated',
    'title': 'UpdatedTag',
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test()

  def test_create(self):
    self.generic_create_test()

  def test_update(self):
    self.generic_update_test()

  def test_delete(self):
    self.generic_delete_test()
