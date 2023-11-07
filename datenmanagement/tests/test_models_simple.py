from django.conf import settings
from django.core.files import File
from django.test import override_settings
from datenmanagement.models import Abfallbehaelter, Adressen, Altersklassen_Kadaverfunde, \
  Anbieter_Carsharing, Angebote_Mobilpunkte, Angelverbotsbereiche, Arten_Erdwaermesonden, \
  Arten_Fahrradabstellanlagen, Arten_FairTrade, Arten_Fallwildsuchen_Kontrollen, \
  Arten_Feldsportanlagen, Arten_Feuerwachen, Arten_Fliessgewaesser, Arten_Hundetoiletten, \
  Arten_Meldedienst_flaechenhaft, Arten_Meldedienst_punkthaft, Arten_Parkmoeglichkeiten, \
  Arten_Pflegeeinrichtungen, Arten_Poller, Arten_Toiletten, \
  Aufteilungsplaene_Wohnungseigentumsgesetz, Baudenkmale, Behinderteneinrichtungen, \
  Beschluesse_Bau_Planungsausschuss, Betriebsarten, Betriebszeiten, \
  Bevollmaechtigte_Bezirksschornsteinfeger, Bewirtschafter_Betreiber_Traeger_Eigentuemer, \
  Bildungstraeger, Carsharing_Stationen, Containerstellplaetze, Denkmalbereiche, Denksteine, \
  Erdwaermesonden, Fahrradabstellanlagen, FairTrade, Feldsportanlagen, Feuerwachen, \
  Fliessgewaesser, Geraetespielanlagen, Geschlechter_Kadaverfunde, Gutachterfotos, Haefen, \
  Hausnummern, Hospize, Hundetoiletten, Hydranten, Kadaverfunde, Kehrbezirke, \
  Kindertagespflegeeinrichtungen, Kinder_Jugendbetreuung, Kleinklaeranlagen, \
  Kunst_im_oeffentlichen_Raum, Ladestationen_Elektrofahrzeuge, Materialien_Denksteine, \
  Meldedienst_flaechenhaft, Meldedienst_punkthaft, Mobilpunkte, Parkmoeglichkeiten, \
  Pflegeeinrichtungen, Poller, Quartiere, Reinigungsreviere, Rettungswachen, Schiffsliegeplaetze, \
  Schlagwoerter_Bildungstraeger, Schlagwoerter_Vereine, Schutzzaeune_Tierseuchen, Sportarten, \
  Sporthallen, Stadtteil_Begegnungszentren, Standortqualitaeten_Geschaeftslagen_Sanierungsgebiet, \
  Standortqualitaeten_Wohnlagen_Sanierungsgebiet, Status_Baudenkmale_Denkmalbereiche, \
  Status_Poller, Strassen, Thalasso_Kurwege, Tierseuchen, Toiletten, Trinkwassernotbrunnen, \
  Typen_Kleinklaeranlagen, Vereine, Verkaufstellen_Angelberechtigungen, Zustaende_Kadaverfunde, \
  Zustaende_Schutzzaeune_Tierseuchen
from datenmanagement.utils import get_current_year

from .base import DefaultSimpleModelTestCase
from .constants_vars import *
from .functions import create_test_subset, remove_uploaded_test_files


class AbfallbehaelterTest(DefaultSimpleModelTestCase):
  """
  Abfallbehälter
  """

  model = Abfallbehaelter
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    bewirtschafter_eigentuemer = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'eigentuemer': bewirtschafter_eigentuemer,
      'bewirtschafter': bewirtschafter_eigentuemer,
      'pflegeobjekt': 'Pflegeobjekt1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'pflegeobjekt': 'Pflegeobjekt2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': '00000000',
      'eigentuemer': str(bewirtschafter_eigentuemer.pk),
      'bewirtschafter': str(bewirtschafter_eigentuemer.pk),
      'pflegeobjekt': 'Pflegeobjekt3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': '00000000',
      'eigentuemer': str(bewirtschafter_eigentuemer.pk),
      'bewirtschafter': str(bewirtschafter_eigentuemer.pk),
      'pflegeobjekt': 'Pflegeobjekt4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'pflegeobjekt': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class AngelverbotsbereicheTest(DefaultSimpleModelTestCase):
  """
  Angelverbotsbereiche
  """

  model = Angelverbotsbereiche
  attributes_values_db_initial = {
    'bezeichnung': 'Bezeichnung1',
    'geometrie': VALID_LINE_DB
  }
  attributes_values_db_updated = {
    'bezeichnung': 'Bezeichnung2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung3',
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung4',
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_invalid = {
    'bezeichnung': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class AufteilungsplaeneWohnungseigentumsgesetzTest(DefaultSimpleModelTestCase):
  """
  Aufteilungspläne nach Wohnungseigentumsgesetz
  """

  model = Aufteilungsplaene_Wohnungseigentumsgesetz
  pdf = File(open(VALID_PDF_FILE, 'rb'))
  attributes_values_db_initial = {
    'bearbeiter': 'Bearbeiter1',
    'pdf': pdf,
    'geometrie': VALID_POINT_DB
  }
  attributes_values_db_updated = {
    'bearbeiter': 'Bearbeiter2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter3',
    'datum': VALID_DATE,
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter4',
    'datum': VALID_DATE,
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_invalid = {
    'bearbeiter': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_delete(self):
    self.generic_delete_test(self.model)
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1,
      VALID_PDF_FILE,
      'pdf',
      'application/pdf'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1,
      VALID_PDF_FILE,
      'pdf',
      'application/pdf'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))


class BaudenkmaleTest(DefaultSimpleModelTestCase):
  """
  Baudenkmale
  """

  model = Baudenkmale
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    status_baudenkmal = Status_Baudenkmale_Denkmalbereiche.objects.create(
      status='Status'
    )
    cls.attributes_values_db_initial = {
      'status': status_baudenkmal,
      'beschreibung': 'Beschreibung1',
      'gartendenkmal': False,
      'geometrie': VALID_MULTIPOLYGON_DB
    }
    cls.attributes_values_db_updated = {
      'beschreibung': 'Beschreibung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': 2,
      'status': str(status_baudenkmal.pk),
      'beschreibung': 'Beschreibung3',
      'gartendenkmal': False,
      'geometrie': VALID_MULTIPOLYGON_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': 3,
      'status': str(status_baudenkmal.pk),
      'beschreibung': 'Beschreibung4',
      'gartendenkmal': False,
      'geometrie': VALID_MULTIPOLYGON_VIEW
    }
    cls.attributes_values_view_invalid = {
      'beschreibung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class BehinderteneinrichtungenTest(DefaultSimpleModelTestCase):
  """
  Behinderteneinrichtungen
  """

  model = Behinderteneinrichtungen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    traeger = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class BeschluesseBauPlanungsausschussTest(DefaultSimpleModelTestCase):
  """
  Beschlüsse des Bau- und Planungsausschusses
  """

  model = Beschluesse_Bau_Planungsausschuss
  pdf = File(open(VALID_PDF_FILE, 'rb'))
  attributes_values_db_initial = {
    'bearbeiter': 'Bearbeiter1',
    'vorhabenbezeichnung': 'Vorhabenbezeichnung1',
    'pdf': pdf,
    'geometrie': VALID_POINT_DB
  }
  attributes_values_db_updated = {
    'bearbeiter': 'Bearbeiter2',
    'vorhabenbezeichnung': 'Vorhabenbezeichnung2',
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter3',
    'beschlussjahr': get_current_year(),
    'vorhabenbezeichnung': 'Vorhabenbezeichnung3',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter4',
    'beschlussjahr': get_current_year(),
    'vorhabenbezeichnung': 'Vorhabenbezeichnung4',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_invalid = {
    'bearbeiter': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1,
      VALID_PDF_FILE,
      'pdf',
      'application/pdf'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1,
      VALID_PDF_FILE,
      'pdf',
      'application/pdf'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class BildungstraegerTest(DefaultSimpleModelTestCase):
  """
  Bildungsträger
  """

  model = Bildungstraeger
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    schlagwort1 = Schlagwoerter_Bildungstraeger.objects.create(
      schlagwort='Schlagwort1'
    )
    schlagwort2 = Schlagwoerter_Bildungstraeger.objects.create(
      schlagwort='Schlagwort2'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'betreiber': 'Betreiber1',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2',
      'betreiber': 'Betreiber2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'betreiber': 'Betreiber3',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'betreiber': 'Betreiber4',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class CarsharingStationenTest(DefaultSimpleModelTestCase):
  """
  Carsharing-Stationen
  """

  model = Carsharing_Stationen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    anbieter = Anbieter_Carsharing.objects.create(
      anbieter='Anbieter'
    )
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'anbieter': anbieter,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'anbieter': str(anbieter.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'anbieter': str(anbieter.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class ContainerstellplaetzeTest(DefaultSimpleModelTestCase):
  """
  Containerstellplätze
  """

  model = Containerstellplaetze
  attributes_values_db_initial = {
    'privat': False,
    'bezeichnung': 'Bezeichnung1',
    'geometrie': VALID_POINT_DB
  }
  attributes_values_db_updated = {
    'bezeichnung': 'Bezeichnung2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'id': '00-00',
    'privat': False,
    'bezeichnung': 'Bezeichnung3',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'id': '00-00',
    'privat': False,
    'bezeichnung': 'Bezeichnung4',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_invalid = {
    'bezeichnung': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class DenkmalbereicheTest(DefaultSimpleModelTestCase):
  """
  Denkmalbereiche
  """

  model = Denkmalbereiche
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    status_denkmalbereich = Status_Baudenkmale_Denkmalbereiche.objects.create(
      status='Status'
    )
    cls.attributes_values_db_initial = {
      'status': status_denkmalbereich,
      'bezeichnung': 'Bezeichnung1',
      'beschreibung': 'Beschreibung1',
      'geometrie': VALID_MULTIPOLYGON_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2',
      'beschreibung': 'Beschreibung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': 2,
      'status': str(status_denkmalbereich.pk),
      'bezeichnung': 'Bezeichnung3',
      'beschreibung': 'Beschreibung3',
      'geometrie': VALID_MULTIPOLYGON_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': 3,
      'status': str(status_denkmalbereich.pk),
      'bezeichnung': 'Bezeichnung4',
      'beschreibung': 'Beschreibung4',
      'geometrie': VALID_MULTIPOLYGON_VIEW
    }
    cls.attributes_values_view_invalid = {
      'beschreibung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class DenksteineTest(DefaultSimpleModelTestCase):
  """
  Denksteine
  """

  model = Denksteine
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    material = Materialien_Denksteine.objects.create(
      material='Material'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'nummer': '94a',
      'vorname': 'Vorname1',
      'nachname': 'Nachname1',
      'geburtsjahr': 1920,
      'text_auf_dem_stein': 'Text auf dem Stein1',
      'material': material,
      'erstes_verlegejahr': 2010,
      'website': 'https://worschdsupp.1.de',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'nachname': 'Nachname2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'nummer': '23xy',
      'vorname': 'Vorname3',
      'nachname': 'Nachname3',
      'geburtsjahr': 1910,
      'text_auf_dem_stein': 'Text auf dem Stein3',
      'material': str(material.pk),
      'erstes_verlegejahr': 2020,
      'website': 'https://worschdsupp.3.de',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'nummer': '42n',
      'vorname': 'Vorname4',
      'nachname': 'Nachname4',
      'geburtsjahr': 1929,
      'text_auf_dem_stein': 'Text auf dem Stein4',
      'material': str(material.pk),
      'erstes_verlegejahr': 2006,
      'website': 'https://worschdsupp.4.de',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'nachname': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class ErdwaermesondenTest(DefaultSimpleModelTestCase):
  """
  Erdwärmesonden
  """

  model = Erdwaermesonden
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art_erdwaermesonde = Arten_Erdwaermesonden.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'aktenzeichen': 'B/EW/02/2005',
      'art': art_erdwaermesonde,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'aktenzeichen': '73.40.01.05-2001'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art_erdwaermesonde.pk),
      'aktenzeichen': 'WST/20/2015',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art_erdwaermesonde.pk),
      'aktenzeichen': '73.40.01.05-2102-Ä',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'aktenzeichen': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class FahrradabstellanlagenTest(DefaultSimpleModelTestCase):
  """
  Fahrradabstellanlagen
  """

  model = Fahrradabstellanlagen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art_fahrradabstellanlage = Arten_Fahrradabstellanlagen.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'art': art_fahrradabstellanlage,
      'gebuehren': True,
      'ueberdacht': False,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'gebuehren': False
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art_fahrradabstellanlage.pk),
      'gebuehren': True,
      'ueberdacht': False,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art_fahrradabstellanlage.pk),
      'gebuehren': False,
      'ueberdacht': True,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'stellplaetze': INVALID_INTEGER
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class FairTradeTest(DefaultSimpleModelTestCase):
  """
  Fair Trade
  """

  model = FairTrade
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    art = Arten_FairTrade.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'art': art,
      'bezeichnung': 'Bezeichnung1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class FeldsportanlagenTest(DefaultSimpleModelTestCase):
  """
  Feldsportanlagen
  """

  model = Feldsportanlagen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Feldsportanlagen.objects.create(
      art='Art'
    )
    traeger = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'art': art,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class FeuerwachenTest(DefaultSimpleModelTestCase):
  """
  Feuerwachen
  """

  model = Feuerwachen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    art = Arten_Feuerwachen.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'art': art,
      'bezeichnung': 'Bezeichnung1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class FliessgewaesserTest(DefaultSimpleModelTestCase):
  """
  Fließgewässer
  """

  model = Fliessgewaesser
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Fliessgewaesser.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'nummer': 'Nummer1',
      'art': art,
      'geometrie': VALID_LINE_DB
    }
    cls.attributes_values_db_updated = {
      'nummer': 'Nummer2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'nummer': 'Nummer3',
      'art': str(art.pk),
      'laenge': 0,
      'geometrie': VALID_LINE_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'nummer': 'Nummer4',
      'art': str(art.pk),
      'laenge': 0,
      'geometrie': VALID_LINE_VIEW
    }
    cls.attributes_values_view_invalid = {
      'nummer': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class GeraetespielanlagenTest(DefaultSimpleModelTestCase):
  """
  Gerätespielanlagen
  """

  model = Geraetespielanlagen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    traeger = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class GutachterfotosTest(DefaultSimpleModelTestCase):
  """
  Gutachterfotos
  """

  model = Gutachterfotos
  foto = File(open(VALID_IMAGE_FILE, 'rb'))
  attributes_values_db_initial = {
    'bearbeiter': 'Bearbeiter1',
    'datum': VALID_DATE,
    'aufnahmedatum': VALID_DATE,
    'foto': foto,
    'geometrie': VALID_POINT_DB
  }
  attributes_values_db_updated = {
    'bearbeiter': 'Bearbeiter2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter3',
    'datum': VALID_DATE,
    'aufnahmedatum': VALID_DATE,
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter4',
    'datum': VALID_DATE,
    'aufnahmedatum': VALID_DATE,
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_invalid = {
    'bearbeiter': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_delete(self):
    self.generic_delete_test(self.model)
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1,
      VALID_IMAGE_FILE,
      'foto',
      'image/jpeg'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1,
      VALID_IMAGE_FILE,
      'foto',
      'image/jpeg'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))


class HausnummernTest(DefaultSimpleModelTestCase):
  """
  Hausnummern
  """

  model = Hausnummern
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    strasse = Strassen.objects.create(
      strasse='Straße'
    )
    cls.attributes_values_db_initial = {
      'strasse': strasse,
      'hausnummer': 1,
      'postleitzahl': '12345',
      'vergabe_datum': VALID_DATE,
      'bearbeiter': 'Bearbeiter1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'hausnummer': 2
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'hausnummer': 3,
      'postleitzahl': '12345',
      'vergabe_datum': VALID_DATE,
      'bearbeiter': 'Bearbeiter2',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'hausnummer': 4,
      'postleitzahl': '12345',
      'vergabe_datum': VALID_DATE,
      'bearbeiter': 'Bearbeiter3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'hausnummer': INVALID_INTEGER
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class HospizeTest(DefaultSimpleModelTestCase):
  """
  Hospize
  """

  model = Hospize
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    traeger = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class HundetoilettenTest(DefaultSimpleModelTestCase):
  """
  Hundetoiletten
  """

  model = Hundetoiletten
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Hundetoiletten.objects.create(
      art='Art'
    )
    bewirtschafter = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'art': art,
      'bewirtschafter': bewirtschafter,
      'pflegeobjekt': 'Pflegeobjekt1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'pflegeobjekt': 'Pflegeobjekt2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': '00000000',
      'art': str(art.pk),
      'bewirtschafter': str(bewirtschafter.pk),
      'pflegeobjekt': 'Pflegeobjekt3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': '00000000',
      'art': str(art.pk),
      'bewirtschafter': str(bewirtschafter.pk),
      'pflegeobjekt': 'Pflegeobjekt4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'pflegeobjekt': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class HydrantenTest(DefaultSimpleModelTestCase):
  """
  Hydranten
  """

  model = Hydranten
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    bewirtschafter_eigentuemer = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    betriebszeit = Betriebszeiten.objects.create(
      betriebszeit='Betriebszeit'
    )
    cls.attributes_values_db_initial = {
      'bezeichnung': 'HSA 1',
      'eigentuemer': bewirtschafter_eigentuemer,
      'bewirtschafter': bewirtschafter_eigentuemer,
      'feuerloeschgeeignet': True,
      'betriebszeit': betriebszeit,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'HSA 2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'HSA 3',
      'eigentuemer': str(bewirtschafter_eigentuemer.pk),
      'bewirtschafter': str(bewirtschafter_eigentuemer.pk),
      'feuerloeschgeeignet': True,
      'betriebszeit': str(betriebszeit.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'HSA 4',
      'eigentuemer': str(bewirtschafter_eigentuemer.pk),
      'bewirtschafter': str(bewirtschafter_eigentuemer.pk),
      'feuerloeschgeeignet': True,
      'betriebszeit': str(betriebszeit.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class KadaverfundeTest(DefaultSimpleModelTestCase):
  """
  Kadaverfunde
  """

  model = Kadaverfunde
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    tierseuche = Tierseuchen.objects.create(
      bezeichnung='Bezeichnung'
    )
    geschlecht = Geschlechter_Kadaverfunde.objects.create(
      ordinalzahl=1,
      bezeichnung='Bezeichnung'
    )
    altersklasse = Altersklassen_Kadaverfunde.objects.create(
      ordinalzahl=1,
      bezeichnung='Bezeichnung'
    )
    zustand = Zustaende_Kadaverfunde.objects.create(
      ordinalzahl=1,
      zustand='Zustand'
    )
    art_auffinden = Arten_Fallwildsuchen_Kontrollen.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'zeitpunkt': VALID_DATETIME,
      'tierseuche': tierseuche,
      'geschlecht': geschlecht,
      'altersklasse': altersklasse,
      'zustand': zustand,
      'art_auffinden': art_auffinden,
      'witterung': 'Witterung1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'witterung': 'Witterung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'zeitpunkt': VALID_DATETIME,
      'tierseuche': str(tierseuche.pk),
      'geschlecht': str(geschlecht.pk),
      'altersklasse': str(altersklasse.pk),
      'zustand': str(zustand.pk),
      'art_auffinden': str(art_auffinden.pk),
      'witterung': 'Witterung3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'zeitpunkt': VALID_DATETIME,
      'tierseuche': str(tierseuche.pk),
      'geschlecht': str(geschlecht.pk),
      'altersklasse': str(altersklasse.pk),
      'zustand': str(zustand.pk),
      'art_auffinden': str(art_auffinden.pk),
      'witterung': 'Witterung4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'witterung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class KehrbezirkeTest(DefaultSimpleModelTestCase):
  """
  Kehrbezirke
  """

  model = Kehrbezirke
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse1 = Adressen.objects.create(
      adresse='Adresse1'
    )
    adresse2 = Adressen.objects.create(
      adresse='Adresse1'
    )
    bevollmaechtigter_bezirksschornsteinfeger1 = (
      Bevollmaechtigte_Bezirksschornsteinfeger.objects.create(
        auswaertig=False,
        vorname='Vorname1',
        nachname='Nachname1',
        anschrift_strasse='Straße1',
        anschrift_hausnummer='123',
        anschrift_postleitzahl='12345',
        anschrift_ort='Ort1'
      )
    )
    bevollmaechtigter_bezirksschornsteinfeger2 = (
      Bevollmaechtigte_Bezirksschornsteinfeger.objects.create(
        auswaertig=True,
        vorname='Vorname2',
        nachname='Nachname2',
        anschrift_strasse='Straße2',
        anschrift_hausnummer='456',
        anschrift_postleitzahl='23456',
        anschrift_ort='Ort2'
      )
    )
    cls.bevollmaechtigter_bezirksschornsteinfeger2 = bevollmaechtigter_bezirksschornsteinfeger2
    cls.attributes_values_db_initial = {
      'adresse': adresse1,
      'bevollmaechtigter_bezirksschornsteinfeger': bevollmaechtigter_bezirksschornsteinfeger1
    }
    cls.attributes_values_db_updated = {
      'bevollmaechtigter_bezirksschornsteinfeger': bevollmaechtigter_bezirksschornsteinfeger2
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse2.pk),
      'bevollmaechtigter_bezirksschornsteinfeger': str(
        bevollmaechtigter_bezirksschornsteinfeger1.pk)
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse2.pk),
      'bevollmaechtigter_bezirksschornsteinfeger': str(
        bevollmaechtigter_bezirksschornsteinfeger1.pk),
      'vergabedatum': VALID_DATE
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_updated,
      'bevollmaechtigter_bezirksschornsteinfeger',
      str(self.bevollmaechtigter_bezirksschornsteinfeger2.pk),
      204,
      'text/html; charset=utf-8',
      1
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )


class KindertagespflegeeinrichtungenTest(DefaultSimpleModelTestCase):
  """
  Kindertagespflegeeinrichtungen
  """

  model = Kindertagespflegeeinrichtungen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'vorname': 'Vorname1',
      'nachname': 'Nachname1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'nachname': 'Nachname2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'vorname': 'Vorname3',
      'nachname': 'Nachname3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'vorname': 'Vorname4',
      'nachname': 'Nachname4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'nachname': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class KinderJugendbetreuungTest(DefaultSimpleModelTestCase):
  """
  Kinder- und Jugendbetreuung
  """

  model = Kinder_Jugendbetreuung
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    traeger1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1',
      art='Art1'
    )
    traeger2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2',
      art='Art2'
    )
    cls.traeger2 = traeger2
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger1,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'traeger': traeger2
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger1.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger1.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_updated,
      'traeger',
      str(self.traeger2.pk),
      204,
      'text/html; charset=utf-8',
      1
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class KleinklaeranlagenTest(DefaultSimpleModelTestCase):
  """
  Kleinkläranlagen
  """

  model = Kleinklaeranlagen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    typ = Typen_Kleinklaeranlagen.objects.create(
      typ='Typ'
    )
    cls.attributes_values_db_initial = {
      'd3': '538.111-047',
      'we_datum': VALID_DATE,
      'typ': typ,
      'einleitstelle': 'Einleitstelle1',
      'gewaesser_berichtspflichtig': True,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'einleitstelle': 'Einleitstelle2'
    }
    cls.attributes_values_view_initial = {
      'd3': '538.111-047',
      'we_datum': VALID_DATE,
      'typ': str(typ.pk),
      'einleitstelle': 'Einleitstelle3',
      'gewaesser_berichtspflichtig': True,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'd3': '538.111-047',
      'we_datum': VALID_DATE,
      'typ': str(typ.pk),
      'einleitstelle': 'Einleitstelle4',
      'gewaesser_berichtspflichtig': True,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'einleitstelle': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class KunstImOeffentlichenRaumTest(DefaultSimpleModelTestCase):
  """
  Kunst im öffentlichen Raum
  """

  model = Kunst_im_oeffentlichen_Raum
  attributes_values_db_initial = {
    'bezeichnung': 'Bezeichnung1',
    'geometrie': VALID_POINT_DB
  }
  attributes_values_db_updated = {
    'bezeichnung': 'Bezeichnung2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung3',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung4',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_invalid = {
    'bezeichnung': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class LadestationenElektrofahrzeugeTest(DefaultSimpleModelTestCase):
  """
  Ladestationen für Elektrofahrzeuge
  """

  model = Ladestationen_Elektrofahrzeuge
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    betriebsart = Betriebsarten.objects.create(
      betriebsart='Betriebsart'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'geplant': False,
      'bezeichnung': 'Bezeichnung1',
      'betriebsart': betriebsart,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'geplant': False,
      'bezeichnung': 'Bezeichnung3',
      'betriebsart': str(betriebsart.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'geplant': False,
      'bezeichnung': 'Bezeichnung4',
      'betriebsart': str(betriebsart.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class MeldedienstFlaechenhaftTest(DefaultSimpleModelTestCase):
  """
  Meldedienst (flächenhaft)
  """

  model = Meldedienst_flaechenhaft
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Meldedienst_flaechenhaft.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'art': art,
      'bearbeiter': 'Bearbeiter1',
      'datum': VALID_DATE,
      'geometrie': VALID_POLYGON_DB
    }
    cls.attributes_values_db_updated = {
      'bearbeiter': 'Bearbeiter2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'bearbeiter': 'Bearbeiter3',
      'datum': VALID_DATE,
      'geometrie': VALID_POLYGON_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'bearbeiter': 'Bearbeiter4',
      'datum': VALID_DATE,
      'geometrie': VALID_POLYGON_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bearbeiter': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class MeldedienstPunkthaftTest(DefaultSimpleModelTestCase):
  """
  Meldedienst (punkthaft)
  """

  model = Meldedienst_punkthaft
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Meldedienst_punkthaft.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'art': art,
      'bearbeiter': 'Bearbeiter1',
      'datum': VALID_DATE,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bearbeiter': 'Bearbeiter2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'bearbeiter': 'Bearbeiter3',
      'datum': VALID_DATE,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'bearbeiter': 'Bearbeiter4',
      'datum': VALID_DATE,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bearbeiter': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class MobilpunkteTest(DefaultSimpleModelTestCase):
  """
  Mobilpunkte
  """

  model = Mobilpunkte
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    angebot1 = Angebote_Mobilpunkte.objects.create(
      angebot='Angebot1'
    )
    angebot2 = Angebote_Mobilpunkte.objects.create(
      angebot='Angebot2'
    )
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'angebote': [angebot1, angebot2],
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'angebote': [angebot1, angebot2],
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'angebote': [angebot1, angebot2],
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class ParkmoeglichkeitenTest(DefaultSimpleModelTestCase):
  """
  Parkmöglichkeiten
  """

  model = Parkmoeglichkeiten
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Parkmoeglichkeiten.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'art': art,
      'standort': 'Standort1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'standort': 'Standort2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'standort': 'Standort3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'standort': 'Standort4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'standort': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class PflegeeinrichtungenTest(DefaultSimpleModelTestCase):
  """
  Pflegeeinrichtungen
  """

  model = Pflegeeinrichtungen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    art = Arten_Pflegeeinrichtungen.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'art': art,
      'bezeichnung': 'Bezeichnung1',
      'betreiber': 'Betreiber1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung3',
      'betreiber': 'Betreiber3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung4',
      'betreiber': 'Betreiber4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class PollerTest(DefaultSimpleModelTestCase):
  """
  Poller
  """

  model = Poller
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Poller.objects.create(
      art='Art'
    )
    status = Status_Poller.objects.create(
      status='Status'
    )
    cls.attributes_values_db_initial = {
      'art': art,
      'bezeichnung': 'Bezeichnung1',
      'status': status,
      'anzahl': 42,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung3',
      'status': str(status.pk),
      'anzahl': 23,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung4',
      'status': str(status.pk),
      'anzahl': 4711,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class ReinigungsreviereTest(DefaultSimpleModelTestCase):
  """
  Reinigungsreviere
  """

  model = Reinigungsreviere
  attributes_values_db_initial = {
    'bezeichnung': 'Bezeichnung1',
    'geometrie': VALID_MULTIPOLYGON_DB
  }
  attributes_values_db_updated = {
    'bezeichnung': 'Bezeichnung2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung3',
    'geometrie': VALID_MULTIPOLYGON_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung4',
    'geometrie': VALID_MULTIPOLYGON_VIEW
  }
  attributes_values_view_invalid = {
    'bezeichnung': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class RettungswachenTest(DefaultSimpleModelTestCase):
  """
  Rettungswachen
  """

  model = Rettungswachen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    traeger = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class SchiffsliegeplaetzeTest(DefaultSimpleModelTestCase):
  """
  Schiffsliegeplätze
  """

  model = Schiffsliegeplaetze
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    hafen = Haefen.objects.create(
      bezeichnung='Bezeichnung',
      abkuerzung='A-BC',
      code=1
    )
    cls.attributes_values_db_initial = {
      'hafen': hafen,
      'liegeplatznummer': 'Liegeplatz1',
      'bezeichnung': 'Bezeichnung1',
      'geometrie': VALID_POLYGON_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'hafen': str(hafen.pk),
      'liegeplatznummer': 'Liegeplatz3',
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POLYGON_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'hafen': str(hafen.pk),
      'liegeplatznummer': 'Liegeplatz4',
      'bezeichnung': 'Bezeichnung4',
      'geometrie': VALID_POLYGON_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class SchutzzaeuneTierseuchenTest(DefaultSimpleModelTestCase):
  """
  Schutzzäune gegen Tierseuchen
  """

  model = Schutzzaeune_Tierseuchen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    tierseuche = Tierseuchen.objects.create(
      bezeichnung='Bezeichnung'
    )
    zustand1 = Zustaende_Schutzzaeune_Tierseuchen.objects.create(
      ordinalzahl=1,
      zustand='Zustand1'
    )
    zustand2 = Zustaende_Schutzzaeune_Tierseuchen.objects.create(
      ordinalzahl=2,
      zustand='Zustand2'
    )
    cls.attributes_values_db_initial = {
      'tierseuche': tierseuche,
      'zustand': zustand1,
      'geometrie': VALID_MULTILINE_DB
    }
    cls.attributes_values_db_updated = {
      'zustand': zustand2
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'tierseuche': str(tierseuche.pk),
      'zustand': str(zustand1.pk),
      'laenge': 0,
      'geometrie': VALID_MULTILINE_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'tierseuche': str(tierseuche.pk),
      'zustand': str(zustand1.pk),
      'laenge': 0,
      'geometrie': VALID_MULTILINE_VIEW
    }
    cls.attributes_values_view_invalid = {
      'zustand': str(zustand2.pk)
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class SporthallenTest(DefaultSimpleModelTestCase):
  """
  Sporthallen
  """

  model = Sporthallen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    traeger = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    sportart = Sportarten.objects.create(
      bezeichnung='Bezeichnung'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger,
      'sportart': sportart,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger.pk),
      'sportart': str(sportart.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger.pk),
      'sportart': str(sportart.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class StadtteilBegegnungszentrenTest(DefaultSimpleModelTestCase):
  """
  Stadtteil- und Begegnungszentren
  """

  model = Stadtteil_Begegnungszentren
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    traeger = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class StandortqualitaetenGeschaeftslagenSanierungsgebietTest(DefaultSimpleModelTestCase):
  """
  Standortqualitäten von Geschäftslagen im Sanierungsgebiet
  """

  model = Standortqualitaeten_Geschaeftslagen_Sanierungsgebiet
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    quartier = Quartiere.objects.create(
      code='123'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bewertungsjahr': get_current_year(),
      'quartier': quartier,
      'kundschaftskontakte_anfangswert': 23.42,
      'kundschaftskontakte_endwert': 23.42,
      'verkehrsanbindung_anfangswert': 23.42,
      'verkehrsanbindung_endwert': 23.42,
      'ausstattung_anfangswert': 23.42,
      'ausstattung_endwert': 23.42,
      'beeintraechtigung_anfangswert': 23.42,
      'beeintraechtigung_endwert': 23.42,
      'standortnutzung_anfangswert': 23.42,
      'standortnutzung_endwert': 23.42,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'standortnutzung_endwert': 42.23
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bewertungsjahr': get_current_year(),
      'quartier': str(quartier.pk),
      'kundschaftskontakte_anfangswert': 23.42,
      'kundschaftskontakte_endwert': 23.42,
      'verkehrsanbindung_anfangswert': 23.42,
      'verkehrsanbindung_endwert': 23.42,
      'ausstattung_anfangswert': 23.42,
      'ausstattung_endwert': 23.42,
      'beeintraechtigung_anfangswert': 23.42,
      'beeintraechtigung_endwert': 23.42,
      'standortnutzung_anfangswert': 23.42,
      'standortnutzung_endwert': 23.42,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bewertungsjahr': get_current_year(),
      'quartier': str(quartier.pk),
      'kundschaftskontakte_anfangswert': 42.23,
      'kundschaftskontakte_endwert': 42.23,
      'verkehrsanbindung_anfangswert': 42.23,
      'verkehrsanbindung_endwert': 42.23,
      'ausstattung_anfangswert': 42.23,
      'ausstattung_endwert': 42.23,
      'beeintraechtigung_anfangswert': 42.23,
      'beeintraechtigung_endwert': 42.23,
      'standortnutzung_anfangswert': 42.23,
      'standortnutzung_endwert': 42.23,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'standortnutzung_endwert': INVALID_DECIMAL
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class StandortqualitaetenWohnlagenSanierungsgebietTest(DefaultSimpleModelTestCase):
  """
  Standortqualitäten von Wohnlagen im Sanierungsgebiet
  """

  model = Standortqualitaeten_Wohnlagen_Sanierungsgebiet
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    quartier = Quartiere.objects.create(
      code='123'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bewertungsjahr': get_current_year(),
      'quartier': quartier,
      'gesellschaftslage_anfangswert': 23.42,
      'gesellschaftslage_endwert': 23.42,
      'verkehrsanbindung_anfangswert': 23.42,
      'verkehrsanbindung_endwert': 23.42,
      'ausstattung_anfangswert': 23.42,
      'ausstattung_endwert': 23.42,
      'beeintraechtigung_anfangswert': 23.42,
      'beeintraechtigung_endwert': 23.42,
      'standortnutzung_anfangswert': 23.42,
      'standortnutzung_endwert': 23.42,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'standortnutzung_endwert': 42.23
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bewertungsjahr': get_current_year(),
      'quartier': str(quartier.pk),
      'gesellschaftslage_anfangswert': 23.42,
      'gesellschaftslage_endwert': 23.42,
      'verkehrsanbindung_anfangswert': 23.42,
      'verkehrsanbindung_endwert': 23.42,
      'ausstattung_anfangswert': 23.42,
      'ausstattung_endwert': 23.42,
      'beeintraechtigung_anfangswert': 23.42,
      'beeintraechtigung_endwert': 23.42,
      'standortnutzung_anfangswert': 23.42,
      'standortnutzung_endwert': 23.42,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bewertungsjahr': get_current_year(),
      'quartier': str(quartier.pk),
      'gesellschaftslage_anfangswert': 42.23,
      'gesellschaftslage_endwert': 42.23,
      'verkehrsanbindung_anfangswert': 42.23,
      'verkehrsanbindung_endwert': 42.23,
      'ausstattung_anfangswert': 42.23,
      'ausstattung_endwert': 42.23,
      'beeintraechtigung_anfangswert': 42.23,
      'beeintraechtigung_endwert': 42.23,
      'standortnutzung_anfangswert': 42.23,
      'standortnutzung_endwert': 42.23,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'standortnutzung_endwert': INVALID_DECIMAL
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class ThalassoKurwegeTest(DefaultSimpleModelTestCase):
  """
  Thalasso-Kurwege
  """

  model = Thalasso_Kurwege
  attributes_values_db_initial = {
    'bezeichnung': 'Bezeichnung1',
    'barrierefrei': True,
    'farbe': '#FF0011',
    'geometrie': VALID_LINE_DB
  }
  attributes_values_db_updated = {
    'bezeichnung': 'Bezeichnung2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung3',
    'barrierefrei': True,
    'farbe': '#FF0011',
    'laenge': 0,
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung4',
    'barrierefrei': True,
    'farbe': '#FF0011',
    'laenge': 0,
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_invalid = {
    'bezeichnung': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class ToilettenTest(DefaultSimpleModelTestCase):
  """
  Toiletten
  """

  model = Toiletten
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Toiletten.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'art': art,
      'behindertengerecht': False,
      'duschmoeglichkeit': True,
      'wickelmoeglichkeit': False,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'behindertengerecht': True
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'behindertengerecht': False,
      'duschmoeglichkeit': True,
      'wickelmoeglichkeit': False,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'behindertengerecht': False,
      'duschmoeglichkeit': True,
      'wickelmoeglichkeit': True,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'zeiten': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class TrinkwassernotbrunnenTest(DefaultSimpleModelTestCase):
  """
  Trinkwassernotbrunnen
  """

  model = Trinkwassernotbrunnen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    betreiber = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung',
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'nummer': '13003000-001',
      'bezeichnung': 'Bezeichnung1',
      'betreiber': betreiber,
      'betriebsbereit': True,
      'bohrtiefe': 5.21,
      'ausbautiefe': 89.79,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'nummer': '13003000-003',
      'bezeichnung': 'Bezeichnung3',
      'betreiber': str(betreiber.pk),
      'betriebsbereit': True,
      'bohrtiefe': 5.21,
      'ausbautiefe': 89.79,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'nummer': '13003000-004',
      'bezeichnung': 'Bezeichnung4',
      'betreiber': str(betreiber.pk),
      'betriebsbereit': True,
      'bohrtiefe': 5.21,
      'ausbautiefe': 89.79,
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class VereineTest(DefaultSimpleModelTestCase):
  """
  Vereine
  """

  model = Vereine
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    schlagwort1 = Schlagwoerter_Vereine.objects.create(
      schlagwort='Schlagwort1'
    )
    schlagwort2 = Schlagwoerter_Vereine.objects.create(
      schlagwort='Schlagwort2'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )


class VerkaufstellenAngelberechtigungenTest(DefaultSimpleModelTestCase):
  """
  Verkaufstellen für Angelberechtigungen
  """

  model = Verkaufstellen_Angelberechtigungen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(
      adresse='Adresse'
    )
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial)

  def test_update(self):
    self.generic_update_test(self.model, self.attributes_values_db_updated)

  def test_delete(self):
    self.generic_delete_test(self.model)

  def test_view_start(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_start',
      {},
      200,
      'text/html; charset=utf-8',
      START_VIEW_STRING
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_data_subset(self):
    data_subset_view_params = DATA_VIEW_PARAMS.copy()
    data_subset_view_params['subset_id'] = self.test_subset.pk
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data_subset',
      data_subset_view_params,
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_updated,
      302,
      'text/html; charset=utf-8',
      1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True,
      self.model,
      self.attributes_values_view_invalid,
      200,
      'text/html; charset=utf-8',
      0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False,
      self.model,
      self.attributes_values_db_initial,
      302,
      'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial,
      204,
      'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk)
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk)
    )
