from .abstract import DefaultViewTestCase

#
# codelists
#


class AccessViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  access (Zugriff)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='access_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class AssetTypeViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  asset type (Typ eines Assets)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='assettype_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class CharsetViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  charset (Zeichensatz)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='charset_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class CrsViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  coordinate reference system (Koordinatenreferenzsystem)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='crs_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class DatathemeCategoryViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  data theme category (Datenthemenkategorie)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='datathemecategory_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class FormatViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  format (Format)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='format_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class FrequencyViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  frequency (Häufigkeit)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='frequency_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class HashTypeViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  hash type (Typ eines Hashes)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='hashtype_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class HvdCategoryViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  high-value dataset category (HVD-Kategorie)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='hvdcategory_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class InspireServiceTypeViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  INSPIRE service type (Typ eines INSPIRE-Services)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='inspireservicetype_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class InspireSpatialScopeViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  INSPIRE spatial scope (räumlicher INSPIRE-Bezugsbereich)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='inspirespatialscope_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class InspireThemeViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  INSPIRE theme (INSPIRE-Thema)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='inspiretheme_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class LanguageViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  language (Sprache)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='language_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class LicenseViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  license (Lizenz)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='license_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class MimeTypeViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  MIME type (MIME-Typ)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='mimetype_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class PoliticalGeocodingViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  political geocoding (geopolitische Verwaltungscodierung)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='politicalgeocoding_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class PoliticalGeocodingLevelViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  political geocoding level (Ebene der geopolitischen Verwaltungscodierung)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='politicalgeocodinglevel_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class SpatialRepresentationTypeViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  spatial representation type (Typ der räumlichen Repräsentation)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='spatialrepresentationtype_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class TagViewTest(DefaultViewTestCase):
  """
  test class for codelist:
  tag (Schlagwort)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='tag_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


#
# auxiliary models
#


class CrsSetViewTest(DefaultViewTestCase):
  """
  test class for auxiliary model:
  set of coordinate reference systems (Set aus einem oder mehreren Koordinatenreferenzsystem(en))
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='crsset_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class DataTypeViewTest(DefaultViewTestCase):
  """
  test class for auxiliary model:
  data type (Datentyp)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='datatype_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class LegalViewTest(DefaultViewTestCase):
  """
  test class for auxiliary model:
  legal (rechtliche Informationen)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='legal_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class SpatialReferenceViewTest(DefaultViewTestCase):
  """
  test class for auxiliary model:
  spatial reference (räumlicher Bezug)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='spatialreference_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class OrganizationViewTest(DefaultViewTestCase):
  """
  test class for auxiliary model:
  organization (Organisation)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='organization_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class ContactViewTest(DefaultViewTestCase):
  """
  test class for auxiliary model:
  contact (Kontakt)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='contact_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


#
# core models
#


class SourceViewTest(DefaultViewTestCase):
  """
  test class for core model:
  source (Datenquelle)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='source_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class RepositoryViewTest(DefaultViewTestCase):
  """
  test class for core model:
  repository (Speicherort)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='repository_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class AssetsetViewTest(DefaultViewTestCase):
  """
  test class for core model:
  asset-set (Asset-Sammlung)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='assetset_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class DatasetViewTest(DefaultViewTestCase):
  """
  test class for core model:
  dataset (Datensatz)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='dataset_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class ServiceViewTest(DefaultViewTestCase):
  """
  test class for core model:
  service (Service)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='service_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class TopicViewTest(DefaultViewTestCase):
  """
  test class for core model:
  topic (Datenthema)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='topic_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )


class AppViewTest(DefaultViewTestCase):
  """
  test class for core model:
  app (App)
  """

  def setUp(self):
    self.init()

  def test_add_view(self):
    self.generic_view_test(
      view_name='app_add',
      status_code=200,
      content_type='text/html; charset=utf-8',
    )
