from datetime import date
from django.conf import settings
from django.core.files import File
from django.test import override_settings
from datenmanagement.models import Abfallbehaelter, Angelverbotsbereiche, \
  Aufteilungsplaene_Wohnungseigentumsgesetz, Bewirtschafter_Betreiber_Traeger_Eigentuemer

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
    self.generic_file_existance_test(
      Path(settings.MEDIA_ROOT) / 'aufteilungsplaene_wohnungseigentumsgesetz' /
      (str(self.test_object.pk) + '.pdf')
    )
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
