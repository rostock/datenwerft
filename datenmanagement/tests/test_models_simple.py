from datetime import date
from django.conf import settings
from django.core.files import File
from django.test import override_settings
from datenmanagement.models import Abfallbehaelter, Adressen, Anbieter_Carsharing, \
  Angelverbotsbereiche, Arten_Baudenkmale, Aufteilungsplaene_Wohnungseigentumsgesetz, \
  Baudenkmale, Behinderteneinrichtungen, Beschluesse_Bau_Planungsausschuss, \
  Bewirtschafter_Betreiber_Traeger_Eigentuemer, Bildungstraeger, Carsharing_Stationen, \
  Schlagwoerter_Bildungstraeger
from datenmanagement.models.functions import current_year

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
      'id': '00000000',
      'eigentuemer': str(bewirtschafter_eigentuemer.pk),
      'bewirtschafter': str(bewirtschafter_eigentuemer.pk),
      'pflegeobjekt': 'Pflegeobjekt3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
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
    self.generic_is_simplemodel_test(self.model)

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
    'geometrie': VALID_LINESTRING_DB
  }
  attributes_values_db_updated = {
    'bezeichnung': 'Bezeichnung2'
  }
  attributes_values_view_initial = {
    'bezeichnung': 'Bezeichnung3',
    'geometrie': VALID_LINESTRING_VIEW
  }
  attributes_values_view_updated = {
    'bezeichnung': 'Bezeichnung4',
    'geometrie': VALID_LINESTRING_VIEW
  }
  attributes_values_view_invalid = {
    'bezeichnung': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test(self.model)

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
    'datum': date.today(),
    'pdf': pdf,
    'geometrie': VALID_POINT_DB
  }
  attributes_values_db_updated = {
    'bearbeiter': 'Bearbeiter2'
  }
  attributes_values_view_initial = {
    'bearbeiter': 'Bearbeiter3',
    'datum': date.today(),
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_updated = {
    'bearbeiter': 'Bearbeiter4',
    'datum': date.today(),
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_invalid = {
    'bearbeiter': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test(self.model)

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
    art_baudenkmal = Arten_Baudenkmale.objects.create(
      art='Art'
    )
    cls.attributes_values_db_initial = {
      'art': art_baudenkmal,
      'beschreibung': 'Beschreibung1',
      'geometrie': VALID_MULTIPOLYGON_DB
    }
    cls.attributes_values_db_updated = {
      'beschreibung': 'Beschreibung2'
    }
    cls.attributes_values_view_initial = {
      'art': str(art_baudenkmal.pk),
      'beschreibung': 'Beschreibung3',
      'geometrie': VALID_MULTIPOLYGON_VIEW
    }
    cls.attributes_values_view_updated = {
      'art': str(art_baudenkmal.pk),
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
    self.generic_is_simplemodel_test(self.model)

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
    adresse = Adressen.objects.create(adresse='Adresse')
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
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
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
    self.generic_is_simplemodel_test(self.model)

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
    'beschlussjahr': current_year(),
    'vorhabenbezeichnung': 'Vorhabenbezeichnung1',
    'pdf': pdf,
    'geometrie': VALID_POINT_DB
  }
  attributes_values_db_updated = {
    'bearbeiter': 'Bearbeiter2',
    'vorhabenbezeichnung': 'Vorhabenbezeichnung2',
  }
  attributes_values_view_initial = {
    'bearbeiter': 'Bearbeiter3',
    'beschlussjahr': current_year(),
    'vorhabenbezeichnung': 'Vorhabenbezeichnung3',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_updated = {
    'bearbeiter': 'Bearbeiter4',
    'beschlussjahr': current_year(),
    'vorhabenbezeichnung': 'Vorhabenbezeichnung4',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_invalid = {
    'bearbeiter': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test(self.model)

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
    adresse = Adressen.objects.create(adresse='Adresse')
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
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'betreiber': 'Betreiber3',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
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
    self.generic_is_simplemodel_test(self.model)

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
      'bezeichnung': 'Bezeichnung3',
      'anbieter': str(anbieter.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
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
    self.generic_is_simplemodel_test(self.model)

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
