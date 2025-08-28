from django.core.files import File
from django.test import override_settings

from datenmanagement.models.models_simple import *
from datenmanagement.utils import get_current_year

from .base import DefaultSimpleModelTestCase
from .constants_vars import *
from .functions import (
  create_test_subset,
  remove_file_attributes_from_object_filter,
  remove_uploaded_test_files,
)


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
    bewirtschafter_eigentuemer1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    cls.bewirtschafter_eigentuemer1 = bewirtschafter_eigentuemer1
    bewirtschafter_eigentuemer2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.bewirtschafter_eigentuemer2 = bewirtschafter_eigentuemer2
    leerungszeiten_sommer = Leerungszeiten.objects.create(bezeichnung='Sommer')
    cls.leerungszeiten_sommer = leerungszeiten_sommer
    leerungszeiten_winter = Leerungszeiten.objects.create(bezeichnung='Winter')
    cls.leerungszeiten_winter = leerungszeiten_winter
    cls.attributes_values_db_initial = {
      'eigentuemer': bewirtschafter_eigentuemer1,
      'bewirtschafter': bewirtschafter_eigentuemer1,
      'pflegeobjekt': 'Pflegeobjekt1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'eigentuemer': bewirtschafter_eigentuemer2,
      'bewirtschafter': bewirtschafter_eigentuemer2,
      'pflegeobjekt': 'Pflegeobjekt2',
    }
    cls.attributes_values_db_assigned_eigentuemer = {'eigentuemer': bewirtschafter_eigentuemer1}
    cls.attributes_values_db_assigned_bewirtschafter = {
      'bewirtschafter': bewirtschafter_eigentuemer2
    }
    cls.attributes_values_db_assigned_leerungszeiten_sommer = {
      'leerungszeiten_sommer': leerungszeiten_sommer
    }
    cls.attributes_values_db_assigned_leerungszeiten_winter = {
      'leerungszeiten_winter': leerungszeiten_winter
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': '00000000',
      'eigentuemer': str(bewirtschafter_eigentuemer1.pk),
      'bewirtschafter': str(bewirtschafter_eigentuemer1.pk),
      'pflegeobjekt': 'Pflegeobjekt3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': '00000000',
      'eigentuemer': str(bewirtschafter_eigentuemer1.pk),
      'bewirtschafter': str(bewirtschafter_eigentuemer1.pk),
      'pflegeobjekt': 'Pflegeobjekt4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'pflegeobjekt': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_eigentuemer(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_eigentuemer,
      'eigentuemer',
      str(self.bewirtschafter_eigentuemer1.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_bewirtschafter(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_bewirtschafter,
      'bewirtschafter',
      str(self.bewirtschafter_eigentuemer2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_leerungszeiten_sommer(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_leerungszeiten_sommer,
      'leerungszeiten_sommer',
      str(self.leerungszeiten_sommer.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_leerungszeiten_winter(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_leerungszeiten_winter,
      'leerungszeiten_winter',
      str(self.leerungszeiten_winter.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class AbstellflaechenETretrollerTest(DefaultSimpleModelTestCase):
  """
  Abstellflächen für E-Tretroller
  """

  model = Abstellflaechen_E_Tretroller
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    strasse = Strassen.objects.create(strasse='Straße')
    cls.attributes_values_db_initial = {
      'strasse': strasse,
      'erstmarkierung': 23,
      'breite': 4.20,
      'laenge': 42.23,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'erstmarkierung': 42}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'erstmarkierung': 23,
      'breite': 4.20,
      'laenge': 42.23,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'erstmarkierung': 42,
      'breite': 4.20,
      'laenge': 42.23,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'breite': INVALID_DECIMAL}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class AnerkennungsgebuehrenHerrschendTest(DefaultSimpleModelTestCase):
  """
  Anerkennungsgebühren (herrschendes Flurstück)
  """

  model = Anerkennungsgebuehren_herrschend
  attributes_values_db_initial = {'grundbucheintrag': 'ja', 'geometrie': VALID_POINT_DB}
  attributes_values_db_updated = {'grundbucheintrag': 'nein'}
  attributes_values_view_initial = {
    'aktiv': True,
    'grundbucheintrag': 'ja',
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'grundbucheintrag': 'nein',
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_invalid = {'bemerkungen': INVALID_STRING}

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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class AngelverbotsbereicheTest(DefaultSimpleModelTestCase):
  """
  Angelverbotsbereiche
  """

  model = Angelverbotsbereiche
  attributes_values_db_initial = {'bezeichnung': 'Bezeichnung1', 'geometrie': VALID_LINE_DB}
  attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
  attributes_values_view_initial = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung3',
    'geometrie': VALID_LINE_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung4',
    'geometrie': VALID_LINE_VIEW,
  }
  attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}

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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class ArrondierungsflaechenTest(DefaultSimpleModelTestCase):
  """
  Arrondierungsflächen
  """

  model = Arrondierungsflaechen
  attributes_values_db_initial = {
    'registriernummer': '12345',
    'jahr': 1987,
    'geometrie': VALID_POLYGON_DB,
  }
  attributes_values_db_updated = {'registriernummer': '525.43', 'jahr': 2023}
  attributes_values_view_initial = {
    'aktiv': True,
    'registriernummer': '54321',
    'jahr': 1978,
    'geometrie': VALID_POLYGON_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'registriernummer': '43.525',
    'jahr': 2024,
    'geometrie': VALID_POLYGON_VIEW,
  }
  attributes_values_view_invalid = {'registriernummer': INVALID_STRING}

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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    'geometrie': VALID_POINT_DB,
  }
  attributes_values_db_updated = {'bearbeiter': 'Bearbeiter2'}
  attributes_values_view_initial = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter3',
    'datum': VALID_DATE,
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter4',
    'datum': VALID_DATE,
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_invalid = {'bearbeiter': INVALID_STRING}

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
      START_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
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
      'application/pdf',
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
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
      'application/pdf',
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_initial,
      'datum_abgeschlossenheitserklaerung',
      '',
      204,
      'text/html; charset=utf-8',
      1,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    status1 = Status_Baudenkmale_Denkmalbereiche.objects.create(status='Status1')
    status2 = Status_Baudenkmale_Denkmalbereiche.objects.create(status='Status2')
    cls.status2 = status2
    cls.attributes_values_db_initial = {
      'status': status1,
      'beschreibung': 'Beschreibung1',
      'gartendenkmal': False,
      'geometrie': VALID_MULTIPOLYGON_DB,
    }
    cls.attributes_values_db_updated = {'status': status2, 'beschreibung': 'Beschreibung2'}
    cls.attributes_values_db_assigned = {'status': status2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': 2,
      'status': str(status1.pk),
      'beschreibung': 'Beschreibung3',
      'gartendenkmal': False,
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': 3,
      'status': str(status2.pk),
      'beschreibung': 'Beschreibung4',
      'gartendenkmal': False,
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_invalid = {'beschreibung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'status',
      str(self.status2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    traeger1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    traeger2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.traeger2 = traeger2
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'traeger': traeger2, 'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_db_assigned = {'traeger': traeger2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'traeger',
      str(self.traeger2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    'geometrie': VALID_POINT_DB,
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
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter4',
    'beschlussjahr': get_current_year(),
    'vorhabenbezeichnung': 'Vorhabenbezeichnung4',
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_invalid = {'bearbeiter': INVALID_STRING}

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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
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
      'application/pdf',
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
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
      'application/pdf',
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    schlagwort1 = Schlagwoerter_Bildungstraeger.objects.create(schlagwort='Schlagwort1')
    schlagwort2 = Schlagwoerter_Bildungstraeger.objects.create(schlagwort='Schlagwort2')
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'betreiber': 'Betreiber1',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2', 'betreiber': 'Betreiber2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'betreiber': 'Betreiber3',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'betreiber': 'Betreiber4',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class BrunnenTest(DefaultSimpleModelTestCase):
  """
  Brunnen
  """

  model = Brunnen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art_brunnen = Arten_Brunnen.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'art': art_brunnen,
      'lagebeschreibung': 'Lagebeschreibung1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'lagebeschreibung': 'Lagebeschreibung2',
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art_brunnen.pk),
      'lagebeschreibung': 'Lagebeschreibung3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art_brunnen.pk),
      'lagebeschreibung': 'Lagebeschreibung4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'lagebeschreibung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class ContainerstellplaetzeTest(DefaultSimpleModelTestCase):
  """
  Containerstellplätze
  """

  model = Containerstellplaetze
  attributes_values_db_initial = {
    'privat': False,
    'bezeichnung': 'Bezeichnung1',
    'geometrie': VALID_POINT_DB,
  }
  attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
  attributes_values_view_initial = {
    'aktiv': True,
    'id': '00-00',
    'privat': False,
    'bezeichnung': 'Bezeichnung3',
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'id': '00-00',
    'privat': False,
    'bezeichnung': 'Bezeichnung4',
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}

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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    status1 = Status_Baudenkmale_Denkmalbereiche.objects.create(status='Status1')
    status2 = Status_Baudenkmale_Denkmalbereiche.objects.create(status='Status2')
    cls.status2 = status2
    cls.attributes_values_db_initial = {
      'status': status1,
      'bezeichnung': 'Bezeichnung1',
      'beschreibung': 'Beschreibung1',
      'geometrie': VALID_MULTIPOLYGON_DB,
    }
    cls.attributes_values_db_updated = {
      'status': status2,
      'bezeichnung': 'Bezeichnung2',
      'beschreibung': 'Beschreibung2',
    }
    cls.attributes_values_db_assigned = {'status': status2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': 2,
      'status': str(status1.pk),
      'bezeichnung': 'Bezeichnung3',
      'beschreibung': 'Beschreibung3',
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': 3,
      'status': str(status2.pk),
      'bezeichnung': 'Bezeichnung4',
      'beschreibung': 'Beschreibung4',
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_invalid = {'beschreibung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'status',
      str(self.status2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    material = Materialien_Denksteine.objects.create(material='Material')
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
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'nachname': 'Nachname2'}
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
      'geometrie': VALID_POINT_VIEW,
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
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'nachname': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    art_erdwaermesonde = Arten_Erdwaermesonden.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'aktenzeichen': 'B/EW/02/2005',
      'art': art_erdwaermesonde,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'aktenzeichen': '73.40.01.05-2001'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art_erdwaermesonde.pk),
      'aktenzeichen': 'WST/20/2015',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art_erdwaermesonde.pk),
      'aktenzeichen': '73.40.01.05-2102-Ä',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'aktenzeichen': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    strasse = Strassen.objects.create(strasse='Straße')
    hersteller = Hersteller_Fahrradabstellanlagen.objects.create(bezeichnung='Bezeichnung1')
    cls.hersteller = hersteller
    ausfuehrung1 = Ausfuehrungen_Fahrradabstellanlagen.objects.create(ausfuehrung='Ausführung1')
    ausfuehrung2 = Ausfuehrungen_Fahrradabstellanlagen.objects.create(ausfuehrung='Ausführung2')
    cls.ausfuehrung2 = ausfuehrung2
    ausfuehrung_stellplaetze1 = Ausfuehrungen_Fahrradabstellanlagen_Stellplaetze.objects.create(
      ausfuehrung='AusführungStellplatz1'
    )
    ausfuehrung_stellplaetze2 = Ausfuehrungen_Fahrradabstellanlagen_Stellplaetze.objects.create(
      ausfuehrung='AusführungStellplatz2'
    )
    cls.ausfuehrung_stellplaetze2 = ausfuehrung_stellplaetze2
    bewirtschafter_eigentuemer1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    bewirtschafter_eigentuemer2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.bewirtschafter_eigentuemer2 = bewirtschafter_eigentuemer2
    cls.attributes_values_db_initial = {
      'strasse': strasse,
      'ausfuehrung': ausfuehrung1,
      'ausfuehrung_stellplaetze': ausfuehrung_stellplaetze1,
      'eigentuemer': bewirtschafter_eigentuemer1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'ausfuehrung': ausfuehrung2,
      'anzahl_stellplaetze': 23,
      'ausfuehrung_stellplaetze': ausfuehrung_stellplaetze2,
      'eigentuemer': bewirtschafter_eigentuemer2,
    }
    cls.attributes_values_db_assigned_ausfuehrung = {'ausfuehrung': ausfuehrung2}
    cls.attributes_values_db_assigned_ausfuehrung_stellplaetze = {
      'ausfuehrung_stellplaetze': ausfuehrung_stellplaetze2
    }
    cls.attributes_values_db_assigned_eigentuemer = {'eigentuemer': bewirtschafter_eigentuemer2}
    cls.attributes_values_db_assigned_hersteller = {'hersteller': hersteller}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'ausfuehrung': str(ausfuehrung1.pk),
      'ausfuehrung_stellplaetze': str(ausfuehrung_stellplaetze1.pk),
      'eigentuemer': str(bewirtschafter_eigentuemer1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'ausfuehrung': str(ausfuehrung2.pk),
      'anzahl_stellplaetze': 42,
      'ausfuehrung_stellplaetze': str(ausfuehrung_stellplaetze2.pk),
      'eigentuemer': str(bewirtschafter_eigentuemer2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'anzahl_stellplaetze': INVALID_INTEGER}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_ausfuehrung(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_ausfuehrung,
      'ausfuehrung',
      str(self.ausfuehrung2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_ausfuehrung_stellplaetze(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_ausfuehrung_stellplaetze,
      'ausfuehrung_stellplaetze',
      str(self.ausfuehrung_stellplaetze2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_eigentuemer(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_eigentuemer,
      'eigentuemer',
      str(self.bewirtschafter_eigentuemer2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_hersteller(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_hersteller,
      'hersteller',
      str(self.hersteller.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class FahrradboxenTest(DefaultSimpleModelTestCase):
  """
  Fahrradboxen
  """

  model = Fahrradboxen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    strasse = Strassen.objects.create(strasse='Straße')
    ausfuehrung1 = Ausfuehrungen_Fahrradboxen.objects.create(ausfuehrung='Ausführung1')
    ausfuehrung2 = Ausfuehrungen_Fahrradboxen.objects.create(ausfuehrung='Ausführung2')
    cls.ausfuehrung2 = ausfuehrung2
    bewirtschafter_eigentuemer1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    bewirtschafter_eigentuemer2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.bewirtschafter_eigentuemer2 = bewirtschafter_eigentuemer2
    cls.attributes_values_db_initial = {
      'strasse': strasse,
      'ausfuehrung': ausfuehrung1,
      'eigentuemer': bewirtschafter_eigentuemer1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'ausfuehrung': ausfuehrung2,
      'anzahl_stellplaetze': 23,
      'eigentuemer': bewirtschafter_eigentuemer2,
    }
    cls.attributes_values_db_assigned_ausfuehrung = {'ausfuehrung': ausfuehrung2}
    cls.attributes_values_db_assigned_eigentuemer = {'eigentuemer': bewirtschafter_eigentuemer2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'ausfuehrung': str(ausfuehrung1.pk),
      'eigentuemer': str(bewirtschafter_eigentuemer1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'ausfuehrung': str(ausfuehrung2.pk),
      'anzahl_stellplaetze': 42,
      'eigentuemer': str(bewirtschafter_eigentuemer2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'anzahl_stellplaetze': INVALID_INTEGER}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_ausfuehrung(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_ausfuehrung,
      'ausfuehrung',
      str(self.ausfuehrung2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_eigentuemer(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_eigentuemer,
      'eigentuemer',
      str(self.bewirtschafter_eigentuemer2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class FahrradreparatursetsTest(DefaultSimpleModelTestCase):
  """
  Fahrradreparatursets
  """

  model = Fahrradreparatursets
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    strasse = Strassen.objects.create(strasse='Straße')
    ausfuehrung1 = Ausfuehrungen_Fahrradreparatursets.objects.create(ausfuehrung='Ausführung1')
    ausfuehrung2 = Ausfuehrungen_Fahrradreparatursets.objects.create(ausfuehrung='Ausführung2')
    cls.ausfuehrung2 = ausfuehrung2
    bewirtschafter_eigentuemer1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    bewirtschafter_eigentuemer2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.bewirtschafter_eigentuemer2 = bewirtschafter_eigentuemer2
    cls.attributes_values_db_initial = {
      'strasse': strasse,
      'ausfuehrung': ausfuehrung1,
      'eigentuemer': bewirtschafter_eigentuemer1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'ausfuehrung': ausfuehrung2,
      'baujahr': get_current_year(),
      'eigentuemer': bewirtschafter_eigentuemer2,
    }
    cls.attributes_values_db_assigned_ausfuehrung = {'ausfuehrung': ausfuehrung2}
    cls.attributes_values_db_assigned_eigentuemer = {'eigentuemer': bewirtschafter_eigentuemer2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'ausfuehrung': str(ausfuehrung1.pk),
      'eigentuemer': str(bewirtschafter_eigentuemer1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'ausfuehrung': str(ausfuehrung2.pk),
      'baujahr': get_current_year(),
      'eigentuemer': str(bewirtschafter_eigentuemer2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'baujahr': INVALID_INTEGER}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_ausfuehrung(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_ausfuehrung,
      'ausfuehrung',
      str(self.ausfuehrung2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_eigentuemer(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_eigentuemer,
      'eigentuemer',
      str(self.bewirtschafter_eigentuemer2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class FahrradstaenderTest(DefaultSimpleModelTestCase):
  """
  Fahrradständer
  """

  model = Fahrradstaender
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    strasse = Strassen.objects.create(strasse='Straße')
    ausfuehrung1 = Ausfuehrungen_Fahrradstaender.objects.create(ausfuehrung='Ausführung1')
    ausfuehrung2 = Ausfuehrungen_Fahrradstaender.objects.create(ausfuehrung='Ausführung2')
    cls.ausfuehrung2 = ausfuehrung2
    bewirtschafter_eigentuemer1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    bewirtschafter_eigentuemer2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.bewirtschafter_eigentuemer2 = bewirtschafter_eigentuemer2
    cls.attributes_values_db_initial = {
      'strasse': strasse,
      'ausfuehrung': ausfuehrung1,
      'eigentuemer': bewirtschafter_eigentuemer1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'ausfuehrung': ausfuehrung2,
      'anzahl_stellplaetze': 23,
      'anzahl_fahrradstaender': 42,
      'eigentuemer': bewirtschafter_eigentuemer2,
    }
    cls.attributes_values_db_assigned_ausfuehrung = {'ausfuehrung': ausfuehrung2}
    cls.attributes_values_db_assigned_eigentuemer = {'eigentuemer': bewirtschafter_eigentuemer2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'ausfuehrung': str(ausfuehrung1.pk),
      'eigentuemer': str(bewirtschafter_eigentuemer1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'ausfuehrung': str(ausfuehrung2.pk),
      'anzahl_stellplaetze': 42,
      'anzahl_fahrradstaender': 23,
      'eigentuemer': str(bewirtschafter_eigentuemer2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'anzahl_stellplaetze': INVALID_INTEGER}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_ausfuehrung(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_ausfuehrung,
      'ausfuehrung',
      str(self.ausfuehrung2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_eigentuemer(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_eigentuemer,
      'eigentuemer',
      str(self.bewirtschafter_eigentuemer2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    art = Arten_Feuerwachen.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'art': art,
      'bezeichnung': 'Bezeichnung1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    art = Arten_Fliessgewaesser.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'nummer': 'Nummer1',
      'art': art,
      'geometrie': VALID_LINE_DB,
    }
    cls.attributes_values_db_updated = {'nummer': 'Nummer2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'nummer': 'Nummer3',
      'art': str(art.pk),
      'laenge': 0,
      'geometrie': VALID_LINE_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'nummer': 'Nummer4',
      'art': str(art.pk),
      'laenge': 0,
      'geometrie': VALID_LINE_VIEW,
    }
    cls.attributes_values_view_invalid = {'nummer': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class FussgaengerueberwegeTest(DefaultSimpleModelTestCase):
  """
  Fußgängerüberwege
  """

  model = Fussgaengerueberwege
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    strasse = Strassen.objects.create(strasse='Straße')
    beleuchtungsart1 = Beleuchtungsarten.objects.create(bezeichnung='Bezeichnung1')
    beleuchtungsart2 = Beleuchtungsarten.objects.create(bezeichnung='Bezeichnung2')
    cls.beleuchtungsart2 = beleuchtungsart2
    cls.attributes_values_db_initial = {
      'strasse': strasse,
      'breite': 4.20,
      'laenge': 42.23,
      'barrierefrei': True,
      'beleuchtungsart': beleuchtungsart1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'barrierefrei': False}
    cls.attributes_values_db_assigned_barrierefrei = {'barrierefrei': True}
    cls.attributes_values_db_assigned_beleuchtungsart = {'beleuchtungsart': beleuchtungsart2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'breite': 4.20,
      'laenge': 42.23,
      'barrierefrei': True,
      'beleuchtungsart': str(beleuchtungsart1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'id': '00000000',
      'breite': 4.20,
      'laenge': 42.23,
      'barrierefrei': False,
      'beleuchtungsart': str(beleuchtungsart1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'breite': INVALID_DECIMAL}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_barrierefrei(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_barrierefrei,
      'barrierefrei',
      str(True),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_beleuchtungsart(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_beleuchtungsart,
      'beleuchtungsart',
      str(self.beleuchtungsart2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class GemeinbedarfsflaechenTest(DefaultSimpleModelTestCase):
  """
  Gemeinbedarfsflächen
  """

  model = Gemeinbedarfsflaechen
  attributes_values_db_initial = {
    'registriernummer': '12345',
    'jahr': 1987,
    'geometrie': VALID_POLYGON_DB,
  }
  attributes_values_db_updated = {'registriernummer': '525.43', 'jahr': 2023}
  attributes_values_view_initial = {
    'aktiv': True,
    'registriernummer': '54321',
    'jahr': 1978,
    'geometrie': VALID_POLYGON_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'registriernummer': '43.525',
    'jahr': 2024,
    'geometrie': VALID_POLYGON_VIEW,
  }
  attributes_values_view_invalid = {'registriernummer': INVALID_STRING}

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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    'geometrie': VALID_POINT_DB,
  }
  attributes_values_db_updated = {'bearbeiter': 'Bearbeiter2'}
  attributes_values_view_initial = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter3',
    'datum': VALID_DATE,
    'aufnahmedatum': VALID_DATE,
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bearbeiter': 'Bearbeiter4',
    'datum': VALID_DATE,
    'aufnahmedatum': VALID_DATE,
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_invalid = {'bearbeiter': INVALID_STRING}

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
      START_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
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
      'image/jpeg',
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
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
      'image/jpeg',
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign_datum(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_initial,
      'datum',
      str(VALID_DATE),
      204,
      'text/html; charset=utf-8',
      1,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign_aufnahmedatum(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_initial,
      'aufnahmedatum',
      str(VALID_DATE),
      204,
      'text/html; charset=utf-8',
      1,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    strasse = Strassen.objects.create(strasse='Straße')
    cls.attributes_values_db_initial = {
      'strasse': strasse,
      'hausnummer': 1,
      'postleitzahl': '12345',
      'vergabe_datum': VALID_DATE,
      'bearbeiter': 'Bearbeiter1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'hausnummer': 2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'hausnummer': 3,
      'postleitzahl': '12345',
      'vergabe_datum': VALID_DATE,
      'bearbeiter': 'Bearbeiter2',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse': str(strasse.pk),
      'hausnummer': 4,
      'postleitzahl': '12345',
      'vergabe_datum': VALID_DATE,
      'bearbeiter': 'Bearbeiter3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'hausnummer': INVALID_INTEGER}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_initial,
      'vergabe_datum',
      str(VALID_DATE),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    traeger1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    traeger2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.traeger2 = traeger2
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2', 'traeger': traeger2}
    cls.attributes_values_db_assigned = {'traeger': traeger2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'traeger',
      str(self.traeger2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    art = Arten_Hundetoiletten.objects.create(art='Art')
    bewirtschafter = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung', art='Art'
    )
    cls.attributes_values_db_initial = {
      'art': art,
      'bewirtschafter': bewirtschafter,
      'pflegeobjekt': 'Pflegeobjekt1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'pflegeobjekt': 'Pflegeobjekt2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': '00000000',
      'art': str(art.pk),
      'bewirtschafter': str(bewirtschafter.pk),
      'pflegeobjekt': 'Pflegeobjekt3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': '00000000',
      'art': str(art.pk),
      'bewirtschafter': str(bewirtschafter.pk),
      'pflegeobjekt': 'Pflegeobjekt4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'pflegeobjekt': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class IngenieurbauwerkeTest(DefaultSimpleModelTestCase):
  """
  Ingenieurbauwerke
  """

  model = Ingenieurbauwerke
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art1 = Arten_Ingenieurbauwerke.objects.create(art='Art1')
    art2 = Arten_Ingenieurbauwerke.objects.create(art='Art2')
    cls.art2 = art2
    cls.attributes_values_db_initial = {
      'nummer': 'Nummer1',
      'art': art1,
      'bezeichnung': 'Bezeichnung1',
      'schwerlast': False,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'nummer': 'Nummer2',
      'art': art2,
      'bezeichnung': 'Bezeichnung2',
      'schwerlast': True,
    }
    cls.attributes_values_db_assigned = {'art': art2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'nummer': 'Nummer3',
      'art': str(art1.pk),
      'bezeichnung': 'Bezeichnung3',
      'schwerlast': False,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'nummer': 'Nummer4',
      'art': str(art2.pk),
      'bezeichnung': 'Bezeichnung4',
      'schwerlast': True,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'art',
      str(self.art2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class JagdkatasterSkizzenebenenTest(DefaultSimpleModelTestCase):
  """
  Skizzenebenen des Jagdkatasters
  """

  model = Jagdkataster_Skizzenebenen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    antragsteller = Antragsteller_Jagdkataster_Skizzenebenen.objects.create(
      bezeichnung='Bezeichnung'
    )
    thema = Themen_Jagdkataster_Skizzenebenen.objects.create(bezeichnung='Bezeichnung')
    status = Status_Jagdkataster_Skizzenebenen.objects.create(status='Status')
    cls.attributes_values_db_initial = {
      'antragsteller': antragsteller,
      'thema': thema,
      'status': status,
      'geometrie': VALID_MULTILINE_DB,
    }
    cls.attributes_values_db_updated = {'bemerkungen': 'Bemerkung1'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'antragsteller': str(antragsteller.pk),
      'thema': str(thema.pk),
      'status': str(status.pk),
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'antragsteller': str(antragsteller.pk),
      'thema': str(thema.pk),
      'status': str(status.pk),
      'bemerkungen': 'Bemerkung2',
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_invalid = {'bemerkungen': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    bewirtschafter_eigentuemer1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    cls.bewirtschafter_eigentuemer1 = bewirtschafter_eigentuemer1
    bewirtschafter_eigentuemer2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.bewirtschafter_eigentuemer2 = bewirtschafter_eigentuemer2
    betriebszeit1 = Betriebszeiten.objects.create(betriebszeit='Betriebszeit1')
    betriebszeit2 = Betriebszeiten.objects.create(betriebszeit='Betriebszeit2')
    cls.betriebszeit2 = betriebszeit2
    cls.attributes_values_db_initial = {
      'bezeichnung': 'HSA 1',
      'eigentuemer': bewirtschafter_eigentuemer1,
      'bewirtschafter': bewirtschafter_eigentuemer1,
      'feuerloeschgeeignet': False,
      'betriebszeit': betriebszeit1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'HSA 2',
      'eigentuemer': bewirtschafter_eigentuemer2,
      'bewirtschafter': bewirtschafter_eigentuemer2,
      'betriebszeit': betriebszeit2,
    }
    cls.attributes_values_db_assigned_eigentuemer = {'eigentuemer': bewirtschafter_eigentuemer2}
    cls.attributes_values_db_assigned_bewirtschafter = {
      'bewirtschafter': bewirtschafter_eigentuemer2
    }
    cls.attributes_values_db_assigned_feuerloeschgeeignet = {'feuerloeschgeeignet': True}
    cls.attributes_values_db_assigned_betriebszeit = {'betriebszeit': betriebszeit2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'HSA 3',
      'eigentuemer': str(bewirtschafter_eigentuemer1.pk),
      'bewirtschafter': str(bewirtschafter_eigentuemer1.pk),
      'feuerloeschgeeignet': True,
      'betriebszeit': str(betriebszeit1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'HSA 4',
      'eigentuemer': str(bewirtschafter_eigentuemer2.pk),
      'bewirtschafter': str(bewirtschafter_eigentuemer2.pk),
      'feuerloeschgeeignet': True,
      'betriebszeit': str(betriebszeit2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_eigentuemer(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_eigentuemer,
      'eigentuemer',
      str(self.bewirtschafter_eigentuemer2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_bewirtschafter(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_bewirtschafter,
      'bewirtschafter',
      str(self.bewirtschafter_eigentuemer2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_feuerloeschgeeignet(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_feuerloeschgeeignet,
      'feuerloeschgeeignet',
      str(True),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_betriebszeit(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_betriebszeit,
      'betriebszeit',
      str(self.betriebszeit2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    tierseuche = Tierseuchen.objects.create(bezeichnung='Bezeichnung')
    geschlecht = Geschlechter_Kadaverfunde.objects.create(ordinalzahl=1, bezeichnung='Bezeichnung')
    altersklasse = Altersklassen_Kadaverfunde.objects.create(
      ordinalzahl=1, bezeichnung='Bezeichnung'
    )
    zustand = Zustaende_Kadaverfunde.objects.create(ordinalzahl=1, zustand='Zustand')
    art_auffinden = Arten_Fallwildsuchen_Kontrollen.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'zeitpunkt': VALID_DATETIME,
      'tierseuche': tierseuche,
      'geschlecht': geschlecht,
      'altersklasse': altersklasse,
      'zustand': zustand,
      'art_auffinden': art_auffinden,
      'witterung': 'Witterung1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'witterung': 'Witterung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'zeitpunkt': VALID_DATETIME,
      'tierseuche': str(tierseuche.pk),
      'geschlecht': str(geschlecht.pk),
      'altersklasse': str(altersklasse.pk),
      'zustand': str(zustand.pk),
      'art_auffinden': str(art_auffinden.pk),
      'witterung': 'Witterung3',
      'geometrie': VALID_POINT_VIEW,
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
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'witterung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse1 = Adressen.objects.create(adresse='Adresse1')
    adresse2 = Adressen.objects.create(adresse='Adresse2')
    bevollmaechtigter_bezirksschornsteinfeger1 = (
      Bevollmaechtigte_Bezirksschornsteinfeger.objects.create(
        bezirk='ABC-12',
        auswaertig=False,
        vorname='Vorname1',
        nachname='Nachname1',
        anschrift_strasse='Straße1',
        anschrift_hausnummer='123',
        anschrift_postleitzahl='12345',
        anschrift_ort='Ort1',
      )
    )
    bevollmaechtigter_bezirksschornsteinfeger2 = (
      Bevollmaechtigte_Bezirksschornsteinfeger.objects.create(
        bezirk='DEF-34',
        auswaertig=True,
        vorname='Vorname2',
        nachname='Nachname2',
        anschrift_strasse='Straße2',
        anschrift_hausnummer='456',
        anschrift_postleitzahl='23456',
        anschrift_ort='Ort2',
      )
    )
    cls.bevollmaechtigter_bezirksschornsteinfeger2 = bevollmaechtigter_bezirksschornsteinfeger2
    cls.attributes_values_db_initial = {
      'adresse': adresse1,
      'bevollmaechtigter_bezirksschornsteinfeger': bevollmaechtigter_bezirksschornsteinfeger1,
    }
    cls.attributes_values_db_updated = {
      'bevollmaechtigter_bezirksschornsteinfeger': bevollmaechtigter_bezirksschornsteinfeger2,
      'vergabedatum': VALID_DATE,
    }
    cls.attributes_values_db_assigned_bevollmaechtigter_bezirksschornsteinfeger = {
      'bevollmaechtigter_bezirksschornsteinfeger': bevollmaechtigter_bezirksschornsteinfeger2
    }
    cls.attributes_values_db_assigned_vergabedatum = {'vergabedatum': VALID_DATE}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse2.pk),
      'bevollmaechtigter_bezirksschornsteinfeger': str(
        bevollmaechtigter_bezirksschornsteinfeger1.pk
      ),
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse2.pk),
      'bevollmaechtigter_bezirksschornsteinfeger': str(
        bevollmaechtigter_bezirksschornsteinfeger2.pk
      ),
      'vergabedatum': VALID_DATE,
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_bevollmaechtigter_bezirksschornsteinfeger(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_bevollmaechtigter_bezirksschornsteinfeger,
      'bevollmaechtigter_bezirksschornsteinfeger',
      str(self.bevollmaechtigter_bezirksschornsteinfeger2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_vergabedatum(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_vergabedatum,
      'vergabedatum',
      str(VALID_DATE),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
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
    adresse = Adressen.objects.create(adresse='Adresse')
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'vorname': 'Vorname1',
      'nachname': 'Nachname1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'nachname': 'Nachname2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'vorname': 'Vorname3',
      'nachname': 'Nachname3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'vorname': 'Vorname4',
      'nachname': 'Nachname4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'nachname': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    traeger1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    traeger2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.traeger2 = traeger2
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2', 'traeger': traeger2}
    cls.attributes_values_db_assigned = {'traeger': traeger2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'traeger',
      str(self.traeger2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class KunstImOeffentlichenRaumTest(DefaultSimpleModelTestCase):
  """
  Kunst im öffentlichen Raum
  """

  model = Kunst_im_oeffentlichen_Raum
  attributes_values_db_initial = {'bezeichnung': 'Bezeichnung1', 'geometrie': VALID_POINT_DB}
  attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
  attributes_values_view_initial = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung3',
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung4',
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}

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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    betreiber1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    betreiber2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.betreiber2 = betreiber2
    verbund1 = Verbuende_Ladestationen_Elektrofahrzeuge.objects.create(verbund='Verbund1')
    verbund2 = Verbuende_Ladestationen_Elektrofahrzeuge.objects.create(verbund='Verbund2')
    cls.verbund2 = verbund2
    betriebsart1 = Betriebsarten.objects.create(betriebsart='Betriebsart1')
    betriebsart2 = Betriebsarten.objects.create(betriebsart='Betriebsart2')
    cls.betriebsart2 = betriebsart2
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'geplant': False,
      'bezeichnung': 'Bezeichnung1',
      'betreiber': betreiber1,
      'verbund': verbund1,
      'betriebsart': betriebsart1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2',
      'betreiber': betreiber2,
      'verbund': verbund2,
      'betriebsart': betriebsart2,
    }
    cls.attributes_values_db_assigned_geplant = {'geplant': True}
    cls.attributes_values_db_assigned_betreiber = {'betreiber': betreiber2}
    cls.attributes_values_db_assigned_verbund = {'verbund': verbund2}
    cls.attributes_values_db_assigned_betriebsart = {'betriebsart': betriebsart2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'geplant': False,
      'bezeichnung': 'Bezeichnung3',
      'betreiber': str(betreiber1.pk),
      'verbund': str(verbund1.pk),
      'betriebsart': str(betriebsart1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'geplant': True,
      'bezeichnung': 'Bezeichnung4',
      'betreiber': str(betreiber2.pk),
      'verbund': str(verbund2.pk),
      'betriebsart': str(betriebsart2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_geplant(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_geplant,
      'geplant',
      str(True),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_betreiber(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_betreiber,
      'betreiber',
      str(self.betreiber2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_verbund(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_verbund,
      'verbund',
      str(self.verbund2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_betriebsart(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_betriebsart,
      'betriebsart',
      str(self.betriebsart2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    art = Arten_Meldedienst_flaechenhaft.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'art': art,
      'erfasser': 'Erfasser1',
      'erfassungsdatum': VALID_DATE,
      'geometrie': VALID_POLYGON_DB,
    }
    cls.attributes_values_db_updated = {'erfasser': 'Erfasser2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'erfasser': 'Erfasser3',
      'erfassungsdatum': VALID_DATE,
      'geometrie': VALID_POLYGON_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'erfasser': 'Erfasser4',
      'erfassungsdatum': VALID_DATE,
      'geometrie': VALID_POLYGON_VIEW,
    }
    cls.attributes_values_view_invalid = {'erfasser': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    art = Arten_Meldedienst_punkthaft.objects.create(art='Art')
    gebaeudeart1 = Gebaeudearten_Meldedienst_punkthaft.objects.create(bezeichnung='Bezeichnung1')
    gebaeudeart2 = Gebaeudearten_Meldedienst_punkthaft.objects.create(bezeichnung='Bezeichnung2')
    cls.gebaeudeart2 = gebaeudeart2
    cls.attributes_values_db_initial = {
      'art': art,
      'bearbeiter': 'Bearbeiter1',
      'gebaeudeart': gebaeudeart1,
      'datum': VALID_DATE,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bearbeiter': 'Bearbeiter2', 'gebaeudeart': gebaeudeart2}
    cls.attributes_values_db_assigned_gebaeudeart = {'gebaeudeart': gebaeudeart2}
    cls.attributes_values_db_assigned_datum = {'datum': VALID_DATE}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'bearbeiter': 'Bearbeiter3',
      'gebaeudeart': str(gebaeudeart1.pk),
      'datum': VALID_DATE,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'bearbeiter': 'Bearbeiter4',
      'gebaeudeart': str(gebaeudeart2.pk),
      'datum': VALID_DATE,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bearbeiter': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_gebaeudeart(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_gebaeudeart,
      'gebaeudeart',
      str(self.gebaeudeart2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_datum(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_datum,
      'datum',
      str(VALID_DATE),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class MobilfunkantennenTest(DefaultSimpleModelTestCase):
  """
  Mobilfunkantennen
  """

  model = Mobilfunkantennen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse = Adressen.objects.create(adresse='Adresse')
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'stob': '1234567',
      'erteilungsdatum': VALID_DATE,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'stob': '2345678'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'stob': '7654321',
      'erteilungsdatum': VALID_DATE,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'stob': '8765432',
      'erteilungsdatum': VALID_DATE,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'montagehoehe': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    angebot1 = Angebote_Mobilpunkte.objects.create(angebot='Angebot1')
    angebot2 = Angebote_Mobilpunkte.objects.create(angebot='Angebot2')
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'angebote': [angebot1, angebot2],
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'angebote': [angebot1, angebot2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'angebote': [angebot1, angebot2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class NaturdenkmaleTest(DefaultSimpleModelTestCase):
  """
  Naturdenkmale
  """

  model = Naturdenkmale
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Naturdenkmale.objects.create(art='Art')
    typ1 = Typen_Naturdenkmale.objects.create(art=art, typ='Typ1')
    typ2 = Typen_Naturdenkmale.objects.create(art=art, typ='Typ2')
    cls.typ2 = typ2
    pdf = File(open(VALID_PDF_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'typ': typ1,
      'nummer': 1,
      'bezeichnung': 'Bezeichnung1',
      'pdf': pdf,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {'typ': typ2}
    cls.attributes_values_db_assigned_typ = {'typ': typ2}
    cls.attributes_values_db_assigned_rechtsvorschrift_festsetzung = {
      'rechtsvorschrift_festsetzung': 'gwe235fweg'
    }
    cls.attributes_values_db_assigned_datum_rechtsvorschrift_festsetzung = {
      'datum_rechtsvorschrift_festsetzung': VALID_DATE
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'typ': str(typ1.pk),
      'nummer': 2,
      'bezeichnung': 'Bezeichnung2',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'typ': str(typ2.pk),
      'nummer': 3,
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_simplemodel(self):
    self.generic_is_simplemodel_test()
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial_cleaned)
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
      START_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
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
      'application/pdf',
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
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
      'application/pdf',
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial_cleaned, 302, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign_typ(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_assigned_typ,
      'typ',
      str(self.typ2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign_rechtsvorschrift_festsetzung(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_assigned_rechtsvorschrift_festsetzung,
      'rechtsvorschrift_festsetzung',
      'gwe235fweg',
      204,
      'text/html; charset=utf-8',
      1,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign_datum_rechtsvorschrift_festsetzung(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_assigned_datum_rechtsvorschrift_festsetzung,
      'datum_rechtsvorschrift_festsetzung',
      str(VALID_DATE),
      204,
      'text/html; charset=utf-8',
      1,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial_cleaned, 204, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))


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
    art = Arten_Parkmoeglichkeiten.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'art': art,
      'standort': 'Standort1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'standort': 'Standort2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'standort': 'Standort3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'standort': 'Standort4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'standort': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    art = Arten_Pflegeeinrichtungen.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'art': art,
      'bezeichnung': 'Bezeichnung1',
      'betreiber': 'Betreiber1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung3',
      'betreiber': 'Betreiber3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung4',
      'betreiber': 'Betreiber4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class ReinigungsreviereTest(DefaultSimpleModelTestCase):
  """
  Reinigungsreviere
  """

  model = Reinigungsreviere
  attributes_values_db_initial = {
    'bezeichnung': 'Bezeichnung1',
    'geometrie': VALID_MULTIPOLYGON_DB,
  }
  attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
  attributes_values_view_initial = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung3',
    'geometrie': VALID_MULTIPOLYGON_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung4',
    'geometrie': VALID_MULTIPOLYGON_VIEW,
  }
  attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}

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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class ReisebusparkplaetzeTerminalsTest(DefaultSimpleModelTestCase):
  """
  Reisebusparkplätze und -terminals
  """

  model = Reisebusparkplaetze_Terminals
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Reisebusparkplaetze_Terminals.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'art': art,
      'bezeichnung': 'Bezeichnung1',
      'stellplaetze': 23,
      'gebuehren': False,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung3',
      'stellplaetze': 42,
      'gebuehren': True,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung4',
      'stellplaetze': 99,
      'gebuehren': False,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    traeger1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    traeger2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.traeger2 = traeger2
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2', 'traeger': traeger2}
    cls.attributes_values_db_assigned = {'traeger': traeger2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'traeger',
      str(self.traeger2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    hafen = Haefen.objects.create(bezeichnung='Bezeichnung', abkuerzung='A-BC', code=1)
    cls.attributes_values_db_initial = {
      'hafen': hafen,
      'liegeplatznummer': 'Liegeplatz1',
      'bezeichnung': 'Bezeichnung1',
      'geometrie': VALID_POLYGON_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'hafen': str(hafen.pk),
      'liegeplatznummer': 'Liegeplatz3',
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POLYGON_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'hafen': str(hafen.pk),
      'liegeplatznummer': 'Liegeplatz4',
      'bezeichnung': 'Bezeichnung4',
      'geometrie': VALID_POLYGON_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    tierseuche = Tierseuchen.objects.create(bezeichnung='Bezeichnung')
    zustand1 = Zustaende_Schutzzaeune_Tierseuchen.objects.create(ordinalzahl=1, zustand='Zustand1')
    zustand2 = Zustaende_Schutzzaeune_Tierseuchen.objects.create(ordinalzahl=2, zustand='Zustand2')
    cls.zustand2 = zustand2
    cls.attributes_values_db_initial = {
      'tierseuche': tierseuche,
      'zustand': zustand1,
      'geometrie': VALID_MULTILINE_DB,
    }
    cls.attributes_values_db_updated = {'zustand': zustand2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'tierseuche': str(tierseuche.pk),
      'zustand': str(zustand1.pk),
      'laenge': 0,
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'tierseuche': str(tierseuche.pk),
      'zustand': str(zustand2.pk),
      'laenge': 0,
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_invalid = {}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_updated,
      'zustand',
      str(self.zustand2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class SportanlagenTest(DefaultSimpleModelTestCase):
  """
  Sportanlagen
  """

  model = Sportanlagen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    art = Arten_Sportanlagen.objects.create(art='Art')
    traeger1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    traeger2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.traeger2 = traeger2
    cls.attributes_values_db_initial = {
      'art': art,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2', 'traeger': traeger2}
    cls.attributes_values_db_assigned = {'traeger': traeger2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'traeger',
      str(self.traeger2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    traeger1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    traeger2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.traeger2 = traeger2
    sportart1 = Sportarten.objects.create(bezeichnung='Bezeichnung1')
    sportart2 = Sportarten.objects.create(bezeichnung='Bezeichnung2')
    cls.sportart2 = sportart2
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger1,
      'sportart': sportart1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2',
      'traeger': traeger2,
      'sportart': sportart2,
    }
    cls.attributes_values_db_assigned_traeger = {'traeger': traeger2}
    cls.attributes_values_db_assigned_sportart = {'sportart': sportart2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger1.pk),
      'sportart': str(sportart1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger2.pk),
      'sportart': str(sportart2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_traeger(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_traeger,
      'traeger',
      str(self.traeger2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_sportart(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_sportart,
      'sportart',
      str(self.sportart2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    traeger1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    traeger2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.traeger2 = traeger2
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'traeger': traeger1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2', 'traeger': traeger2}
    cls.attributes_values_db_assigned = {'traeger': traeger2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'traeger': str(traeger1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'traeger': str(traeger2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'traeger',
      str(self.traeger2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    quartier = Quartiere.objects.create(code='123')
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
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'standortnutzung_endwert': 42.23}
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
      'geometrie': VALID_POINT_VIEW,
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
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'standortnutzung_endwert': INVALID_DECIMAL}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    quartier = Quartiere.objects.create(code='123')
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
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'standortnutzung_endwert': 42.23}
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
      'geometrie': VALID_POINT_VIEW,
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
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'standortnutzung_endwert': INVALID_DECIMAL}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class ThalassoKurwegeTest(DefaultSimpleModelTestCase):
  """
  Thalasso-Kurwege
  """

  model = Thalasso_Kurwege
  attributes_values_db_initial = {
    'bezeichnung': 'Bezeichnung1',
    'barrierefrei': False,
    'farbe': '#FF0011',
    'geometrie': VALID_LINE_DB,
  }
  attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2', 'barrierefrei': True}
  attributes_values_db_assigned = {'barrierefrei': True}
  attributes_values_view_initial = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung3',
    'barrierefrei': False,
    'farbe': '#FF0011',
    'laenge': 0,
    'geometrie': VALID_LINE_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'bezeichnung': 'Bezeichnung4',
    'barrierefrei': True,
    'farbe': '#FF0011',
    'laenge': 0,
    'geometrie': VALID_LINE_VIEW,
  }
  attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}

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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'barrierefrei',
      str(True),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    art = Arten_Toiletten.objects.create(art='Art')
    bewirtschafter1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    bewirtschafter2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.bewirtschafter2 = bewirtschafter2
    cls.attributes_values_db_initial = {
      'art': art,
      'bewirtschafter': bewirtschafter1,
      'behindertengerecht': False,
      'duschmoeglichkeit': True,
      'wickelmoeglichkeit': False,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'bewirtschafter': bewirtschafter2,
      'behindertengerecht': True,
    }
    cls.attributes_values_db_assigned = {'bewirtschafter': bewirtschafter2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'art': str(art.pk),
      'bewirtschafter': str(bewirtschafter1.pk),
      'behindertengerecht': False,
      'duschmoeglichkeit': True,
      'wickelmoeglichkeit': False,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'art': str(art.pk),
      'bewirtschafter': str(bewirtschafter2.pk),
      'behindertengerecht': False,
      'duschmoeglichkeit': True,
      'wickelmoeglichkeit': True,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'zeiten': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned,
      'bewirtschafter',
      str(self.bewirtschafter2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    eigentuemer1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung1', art='Art1'
    )
    eigentuemer2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung2', art='Art2'
    )
    cls.eigentuemer2 = eigentuemer2
    betreiber1 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung3', art='Art3'
    )
    betreiber2 = Bewirtschafter_Betreiber_Traeger_Eigentuemer.objects.create(
      bezeichnung='Bezeichnung4', art='Art4'
    )
    cls.betreiber2 = betreiber2
    cls.attributes_values_db_initial = {
      'nummer': '13003000-001',
      'bezeichnung': 'Bezeichnung1',
      'eigentuemer': eigentuemer1,
      'betreiber': betreiber1,
      'betriebsbereit': False,
      'bohrtiefe': 5.21,
      'ausbautiefe': 89.79,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2',
      'eigentuemer': eigentuemer2,
      'betreiber': betreiber2,
      'betriebsbereit': True,
    }
    cls.attributes_values_db_assigned_eigentuemer = {'eigentuemer': eigentuemer2}
    cls.attributes_values_db_assigned_betreiber = {'betreiber': betreiber2}
    cls.attributes_values_db_assigned_betriebsbereit = {'betriebsbereit': True}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'nummer': '13003000-003',
      'bezeichnung': 'Bezeichnung3',
      'eigentuemer': str(eigentuemer1.pk),
      'betreiber': str(betreiber1.pk),
      'betriebsbereit': False,
      'bohrtiefe': 5.21,
      'ausbautiefe': 89.79,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'nummer': '13003000-004',
      'bezeichnung': 'Bezeichnung4',
      'eigentuemer': str(eigentuemer2.pk),
      'betreiber': str(betreiber2.pk),
      'betriebsbereit': True,
      'bohrtiefe': 5.21,
      'ausbautiefe': 89.79,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_eigentuemer(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_eigentuemer,
      'eigentuemer',
      str(self.eigentuemer2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_betreiber(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_betreiber,
      'betreiber',
      str(self.betreiber2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_betriebsbereit(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_betriebsbereit,
      'betriebsbereit',
      str(True),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    schlagwort1 = Schlagwoerter_Vereine.objects.create(schlagwort='Schlagwort1')
    schlagwort2 = Schlagwoerter_Vereine.objects.create(schlagwort='Schlagwort2')
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'schlagwoerter': [schlagwort1, schlagwort2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
    adresse = Adressen.objects.create(adresse='Adresse')
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'bezeichnung': 'Bezeichnung1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'bezeichnung': 'Bezeichnung4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )


class VersenkpollerTest(DefaultSimpleModelTestCase):
  """
  Versenkpoller
  """

  model = Versenkpoller
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    hersteller1 = Hersteller_Versenkpoller.objects.create(bezeichnung='Bezeichnung1')
    hersteller2 = Hersteller_Versenkpoller.objects.create(bezeichnung='Bezeichnung2')
    typ = Typen_Versenkpoller.objects.create(typ='Typ')
    wartungsfirma1 = Wartungsfirmen_Versenkpoller.objects.create(bezeichnung='Bezeichnung1')
    wartungsfirma2 = Wartungsfirmen_Versenkpoller.objects.create(bezeichnung='Bezeichnung2')
    cls.hersteller2 = hersteller2
    cls.wartungsfirma2 = wartungsfirma2
    cls.attributes_values_db_initial = {
      'hersteller': hersteller1,
      'typ': typ,
      'wartungsfirma': wartungsfirma1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'hersteller': hersteller2}
    cls.attributes_values_db_assigned_hersteller = {'hersteller': hersteller2}
    cls.attributes_values_db_assigned_wartungsfirma = {'wartungsfirma': wartungsfirma2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'hersteller': str(hersteller1.pk),
      'typ': str(typ.pk),
      'wartungsfirma': str(wartungsfirma1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'hersteller': str(hersteller2.pk),
      'wartungsfirma': str(wartungsfirma2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'baujahr': 1899}
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
      START_VIEW_STRING,
    )

  def test_view_list(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list',
      {},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_list_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_list_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      LIST_VIEW_STRING,
    )

  def test_view_data(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_data',
      DATA_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
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
      str(self.test_object.pk),
    )

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_map_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )

  def test_view_mapdata(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_mapdata_subset(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_mapdata_subset',
      {'subset_id': self.test_subset.pk},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_initial, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_add_error(self):
    self.generic_add_update_view_test(
      False, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_change_success(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_updated, 302, 'text/html; charset=utf-8', 1
    )

  def test_view_change_error(self):
    self.generic_add_update_view_test(
      True, self.model, self.attributes_values_view_invalid, 200, 'text/html; charset=utf-8', 0
    )

  def test_view_delete(self):
    self.generic_delete_view_test(
      False, self.model, self.attributes_values_db_initial, 302, 'text/html; charset=utf-8'
    )

  def test_view_assign_hersteller(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_hersteller,
      'hersteller',
      str(self.hersteller2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_wartungsfirma(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_wartungsfirma,
      'wartungsfirma',
      str(self.wartungsfirma2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )

  def test_view_geometry(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_pk(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      {'pk': str(self.test_object.pk)},
      200,
      'application/json',
      str(self.test_object.pk),
    )

  def test_view_geometry_lat_lng(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_geometry',
      GEOMETRY_VIEW_PARAMS,
      200,
      'application/json',
      str(self.test_object.pk),
    )
