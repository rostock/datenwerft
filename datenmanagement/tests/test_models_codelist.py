from datenmanagement.models import Adressen, Strassen, Inoffizielle_Strassen, Gemeindeteile, \
  Anbieter_Carsharing

from .base import DefaultCodelistTestCase, DefaultMetaModelTestCase
from .constants_vars import *


#
# Meta-Datenmodelle
#

class AdressenTest(DefaultMetaModelTestCase):
  """
  Testklasse für Adressen
  """

  model = Adressen
  attributes_values_db_initial = {
    'adresse': 'Deppendorfer Str. 23a'
  }
  attributes_values_db_updated = {
    'adresse': 'Suppenkasperweg 42'
  }

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    self.generic_is_metamodel_test(self.model)

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
      "'recordsTotal': 1"
    )


class StrassenTest(DefaultMetaModelTestCase):
  """
  Testklasse für Straßen
  """

  model = Strassen
  attributes_values_db_initial = {
    'strasse': 'Deppendorfer Str.'
  }
  attributes_values_db_updated = {
    'strasse': 'Suppenkasperweg'
  }

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    self.generic_is_metamodel_test(self.model)

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
      "'recordsTotal': 1"
    )


class InoffizielleStrassenTest(DefaultMetaModelTestCase):
  """
  Testklasse für inoffizielle Straßen
  """

  model = Inoffizielle_Strassen
  attributes_values_db_initial = {
    'strasse': 'Deppendorfer Str.'
  }
  attributes_values_db_updated = {
    'strasse': 'Suppenkasperweg'
  }

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    self.generic_is_metamodel_test(self.model)

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
      "'recordsTotal': 1"
    )


class GemeindeteileTest(DefaultMetaModelTestCase):
  """
  Testklasse für Gemeindeteile
  """

  model = Gemeindeteile
  attributes_values_db_initial = {
    'gemeindeteil': 'Entenhausen',
    'geometrie': VALID_MULTIPOLYGON
  }
  attributes_values_db_updated = {
    'gemeindeteil': 'Katzensteige'
  }

  def setUp(self):
    self.init()

  def test_is_metamodel(self):
    self.generic_is_metamodel_test(self.model)

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
      "'recordsTotal': 1"
    )


#
# Codelisten
#

class AnbieterCarsharingTest(DefaultCodelistTestCase):
  """
  Testklasse für Carsharing-Anbieter
  """

  model = Anbieter_Carsharing
  attributes_values_db_initial = {
    'anbieter': 'Deppendorf GmbH & Co. KG'
  }
  attributes_values_db_updated = {
    'anbieter': 'Suppenkasper AG'
  }
  attributes_values_view_initial = {
    'anbieter': 'Deppendorf AG'
  }
  attributes_values_view_updated = {
    'anbieter': 'Suppenkasper GmbH & Co. KG'
  }
  attributes_values_view_invalid = {
    'anbieter': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_codelist(self):
    self.generic_is_codelist_test(self.model)

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
      "'recordsTotal': 1"
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
