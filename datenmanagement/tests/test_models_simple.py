from datenmanagement.models import Abfallbehaelter, Angelverbotsbereiche, \
  Bewirtschafter_Betreiber_Traeger_Eigentuemer

from .base import DefaultSimpleModelTestCase
from .constants_vars import *


class AbfallbehaelterTest(DefaultSimpleModelTestCase):
  """
  Abfallbehälter
  """

  model = Abfallbehaelter
  create_test_object_in_classmethod = False

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

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      DATA_VIEW_STRING
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

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
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

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      DATA_VIEW_STRING
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

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
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
