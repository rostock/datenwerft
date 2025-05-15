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
from ..constants_vars import (
  INVALID_STRING,
)


class AccessModelTest(DefaultCodelistTestCase):
  """
  tests for Access model
  """

  model = Access
  attributes_values_db_initial = {'code': 'https://example.org/access/test', 'title': 'TestAccess'}
  attributes_values_db_updated = {
    'code': 'https://example.org/access/updated',
    'title': 'UpdatedAccess',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/access/test',
    'title': 'TestAccess',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/access/updated',
    'title': 'UpdatedAccess',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/access/invalid',
    'title': INVALID_STRING,
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
  tests for AssetType model
  """

  model = AssetType
  attributes_values_db_initial = {
    'code': 'https://example.org/assettype/test',
    'title': 'TestAssetType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/assettype/updated',
    'title': 'UpdatedAssetType',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/assettype/test',
    'title': 'TestAssetType',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/assettype/updated',
    'title': 'UpdatedAssetType',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/assettype/invalid',
    'title': INVALID_STRING,
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
  tests for Charset model
  """

  model = Charset
  attributes_values_db_initial = {
    'code': 'https://example.org/charset/test',
    'title': 'TestCharset',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/charset/updated',
    'title': 'UpdatedCharset',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/charset/test',
    'title': 'TestCharset',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/charset/updated',
    'title': 'UpdatedCharset',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/charset/invalid',
    'title': INVALID_STRING,
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
  tests for Crs model
  """

  model = Crs
  attributes_values_db_initial = {'code': 'https://example.org/crs/test', 'title': 'TestCrs'}
  attributes_values_db_updated = {'code': 'https://example.org/crs/updated', 'title': 'UpdatedCrs'}
  attributes_values_view_initial = {'code': 'https://example.org/crs/test', 'title': 'TestCrs'}
  attributes_values_view_updated = {
    'code': 'https://example.org/crs/updated',
    'title': 'UpdatedCrs',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/crs/invalid',
    'title': INVALID_STRING,
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
  tests for DatathemeCategory model
  """

  model = DatathemeCategory
  attributes_values_db_initial = {
    'code': 'https://example.org/datathemecategory/test',
    'title': 'TestDatathemeCategory',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/datathemecategory/updated',
    'title': 'UpdatedDatathemeCategory',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/datathemecategory/test',
    'title': 'TestDatathemeCategory',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/datathemecategory/updated',
    'title': 'UpdatedDatathemeCategory',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/datathemecategory/invalid',
    'title': INVALID_STRING,
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
  tests for Format model
  """

  model = Format
  attributes_values_db_initial = {'code': 'https://example.org/format/test', 'title': 'TestFormat'}
  attributes_values_db_updated = {
    'code': 'https://example.org/format/updated',
    'title': 'UpdatedFormat',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/format/test',
    'title': 'TestFormat',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/format/updated',
    'title': 'UpdatedFormat',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/format/invalid',
    'title': INVALID_STRING,
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
  tests for Frequency model
  """

  model = Frequency
  attributes_values_db_initial = {
    'code': 'https://example.org/frequency/test',
    'title': 'TestFrequency',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/frequency/updated',
    'title': 'UpdatedFrequency',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/frequency/test',
    'title': 'TestFrequency',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/frequency/updated',
    'title': 'UpdatedFrequency',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/frequency/invalid',
    'title': INVALID_STRING,
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
  tests for HashType model
  """

  model = HashType
  attributes_values_db_initial = {
    'code': 'https://example.org/hashtype/test',
    'title': 'TestHashType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/hashtype/updated',
    'title': 'UpdatedHashType',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/hashtype/test',
    'title': 'TestHashType',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/hashtype/updated',
    'title': 'UpdatedHashType',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/hashtype/invalid',
    'title': INVALID_STRING,
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
  tests for HvdCategory model
  """

  model = HvdCategory
  attributes_values_db_initial = {
    'code': 'https://example.org/hvdcategory/test',
    'title': 'TestHvdCategory',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/hvdcategory/updated',
    'title': 'UpdatedHvdCategory',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/hvdcategory/test',
    'title': 'TestHvdCategory',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/hvdcategory/updated',
    'title': 'UpdatedHvdCategory',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/hvdcategory/invalid',
    'title': INVALID_STRING,
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
  tests for InspireServiceType model
  """

  model = InspireServiceType
  attributes_values_db_initial = {
    'code': 'https://example.org/inspireservicetype/test',
    'title': 'TestInspireServiceType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/inspireservicetype/updated',
    'title': 'UpdatedInspireServiceType',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/inspireservicetype/test',
    'title': 'TestInspireServiceType',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/inspireservicetype/updated',
    'title': 'UpdatedInspireServiceType',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/inspireservicetype/invalid',
    'title': INVALID_STRING,
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
  tests for InspireSpatialScope model
  """

  model = InspireSpatialScope
  attributes_values_db_initial = {
    'code': 'https://example.org/inspirespatialscope/test',
    'title': 'TestInspireSpatialScope',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/inspirespatialscope/updated',
    'title': 'UpdatedInspireSpatialScope',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/inspirespatialscope/test',
    'title': 'TestInspireSpatialScope',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/inspirespatialscope/updated',
    'title': 'UpdatedInspireSpatialScope',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/inspirespatialscope/invalid',
    'title': INVALID_STRING,
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
  tests for InspireTheme model
  """

  model = InspireTheme
  attributes_values_db_initial = {
    'code': 'https://example.org/inspiretheme/test',
    'title': 'TestInspireTheme',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/inspiretheme/updated',
    'title': 'UpdatedInspireTheme',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/inspiretheme/test',
    'title': 'TestInspireTheme',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/inspiretheme/updated',
    'title': 'UpdatedInspireTheme',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/inspiretheme/invalid',
    'title': INVALID_STRING,
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
  tests for Language model
  """

  model = Language
  attributes_values_db_initial = {
    'code': 'https://example.org/language/test',
    'title': 'TestLanguage',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/language/updated',
    'title': 'UpdatedLanguage',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/language/test',
    'title': 'TestLanguage',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/language/updated',
    'title': 'UpdatedLanguage',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/language/invalid',
    'title': INVALID_STRING,
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
  tests for License model
  """

  model = License
  attributes_values_db_initial = {
    'code': 'https://example.org/license/test',
    'title': 'TestLicense',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/license/updated',
    'title': 'UpdatedLicense',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/license/test',
    'title': 'TestLicense',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/license/updated',
    'title': 'UpdatedLicense',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/license/invalid',
    'title': INVALID_STRING,
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
  tests for MimeType model
  """

  model = MimeType
  attributes_values_db_initial = {
    'code': 'https://example.org/mimetype/test',
    'title': 'TestMimeType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/mimetype/updated',
    'title': 'UpdatedMimeType',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/mimetype/test',
    'title': 'TestMimeType',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/mimetype/updated',
    'title': 'UpdatedMimeType',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/mimetype/invalid',
    'title': INVALID_STRING,
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
  tests for PoliticalGeocoding model
  """

  model = PoliticalGeocoding
  attributes_values_db_initial = {
    'code': 'https://example.org/politicalgeocoding/test',
    'title': 'TestPoliticalGeocoding',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/politicalgeocoding/updated',
    'title': 'UpdatedPoliticalGeocoding',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/politicalgeocoding/test',
    'title': 'TestPoliticalGeocoding',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/politicalgeocoding/updated',
    'title': 'UpdatedPoliticalGeocoding',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/politicalgeocoding/invalid',
    'title': INVALID_STRING,
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
  tests for PoliticalGeocodingLevel model
  """

  model = PoliticalGeocodingLevel
  attributes_values_db_initial = {
    'code': 'https://example.org/politicalgecodinglevel/test',
    'title': 'TestPoliticalGeocodingLevel',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/politicalgecodinglevel/updated',
    'title': 'UpdatedPoliticalGeocodingLevel',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/politicalgecodinglevel/test',
    'title': 'TestPoliticalGeocodingLevel',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/politicalgecodinglevel/updated',
    'title': 'UpdatedPoliticalGeocodingLevel',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/politicalgecodinglevel/invalid',
    'title': INVALID_STRING,
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
  tests for SpatialRepresentationType model
  """

  model = SpatialRepresentationType
  attributes_values_db_initial = {
    'code': 'https://example.org/spatialrepresentationtype/test',
    'title': 'TestSpatialRepresentationType',
  }
  attributes_values_db_updated = {
    'code': 'https://example.org/spatialrepresentationtype/updated',
    'title': 'UpdatedSpatialRepresentationType',
  }
  attributes_values_view_initial = {
    'code': 'https://example.org/spatialrepresentationtype/test',
    'title': 'TestSpatialRepresentationType',
  }
  attributes_values_view_updated = {
    'code': 'https://example.org/spatialrepresentationtype/updated',
    'title': 'UpdatedSpatialRepresentationType',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/spatialrepresentationtype/invalid',
    'title': INVALID_STRING,
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
  tests for Tag model
  """

  model = Tag
  attributes_values_db_initial = {'code': 'https://example.org/tag/test', 'title': 'TestTag'}
  attributes_values_db_updated = {'code': 'https://example.org/tag/updated', 'title': 'UpdatedTag'}
  attributes_values_view_initial = {'code': 'https://example.org/tag/test', 'title': 'TestTag'}
  attributes_values_view_updated = {
    'code': 'https://example.org/tag/updated',
    'title': 'UpdatedTag',
  }
  attributes_values_view_invalid = {
    'code': 'https://example.org/tag/invalid',
    'title': INVALID_STRING,
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
