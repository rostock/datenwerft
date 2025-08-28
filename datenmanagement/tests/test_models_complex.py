from django.core.files import File
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from datenmanagement.models import *

from .base import DefaultComplexModelTestCase, GenericRSAGTestCase
from .constants_vars import *
from .functions import (
  create_test_subset,
  remove_file_attributes_from_object_filter,
  remove_uploaded_test_files,
)

#
# Adressunsicherheiten
#


def adressunsicherheit_data():
  adresse = Adressen.objects.create(adresse='Adresse')
  art1 = Arten_Adressunsicherheiten.objects.create(art='Art1')
  art2 = Arten_Adressunsicherheiten.objects.create(art='Art2')
  return adresse, art1, art2


class AdressunsicherheitenTest(DefaultComplexModelTestCase):
  """
  Adressunsicherheiten:
  Adressunsicherheiten
  """

  model = Adressunsicherheiten
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse, art1, art2 = adressunsicherheit_data()
    cls.art2 = art2
    cls.attributes_values_db_initial = {
      'adresse': adresse,
      'art': art1,
      'beschreibung': 'Beschreibung1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'beschreibung': 'Beschreibung2', 'art': art2}
    cls.attributes_values_db_assigned = {'art': art2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art1.pk),
      'beschreibung': 'Beschreibung3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adresse': str(adresse.pk),
      'art': str(art2.pk),
      'beschreibung': 'Beschreibung4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'beschreibung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class AdressunsicherheitenFotosTest(DefaultComplexModelTestCase):
  """
  Adressunsicherheiten:
  Fotos
  """

  model = Adressunsicherheiten_Fotos
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    adresse, art1, art2 = adressunsicherheit_data()
    adressunsicherheit = Adressunsicherheiten.objects.create(
      adresse=adresse, art=art1, beschreibung='Beschreibung', geometrie=VALID_POINT_DB
    )
    foto = File(open(VALID_IMAGE_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'adressunsicherheit': adressunsicherheit,
      'aufnahmedatum': VALID_DATE,
      'foto': foto,
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {'dateiname_original': 'image_also_valid.jpg'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'adressunsicherheit': str(adressunsicherheit.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'adressunsicherheit': str(adressunsicherheit.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_also_valid.jpg',
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()
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

  def test_view_add_multiple_files(self):
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
      True,
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
      False, self.model, self.attributes_values_db_initial_cleaned, 302, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial_cleaned, 204, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))


#
# Baugrunduntersuchungen
#


def create_baugrunduntersuchung():
  labor = Labore_Baugrunduntersuchungen.objects.create(bezeichnung='Bezeichnung')
  auftraggeber = Auftraggeber_Baugrunduntersuchungen.objects.create(auftraggeber='Auftraggeber')
  return Baugrunduntersuchungen.objects.create(
    historisch=False,
    auftraggeber=auftraggeber,
    labor=labor,
    bezeichnung='Bezeichnung',
    datum=VALID_DATE,
  )


class BaugrunduntersuchungenTest(DefaultComplexModelTestCase):
  """
  Baugrunduntersuchungen:
  Baugrunduntersuchungen
  """

  model = Baugrunduntersuchungen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    labor1 = Labore_Baugrunduntersuchungen.objects.create(bezeichnung='Bezeichnung1')
    labor2 = Labore_Baugrunduntersuchungen.objects.create(bezeichnung='Bezeichnung2')
    cls.labor2 = labor2
    auftraggeber1 = Auftraggeber_Baugrunduntersuchungen.objects.create(
      auftraggeber='Auftraggeber1'
    )
    auftraggeber2 = Auftraggeber_Baugrunduntersuchungen.objects.create(
      auftraggeber='Auftraggeber2'
    )
    cls.auftraggeber2 = auftraggeber2
    cls.attributes_values_db_initial = {
      'historisch': False,
      'auftraggeber': auftraggeber1,
      'labor': labor1,
      'bezeichnung': 'Bezeichnung1',
      'datum': VALID_DATE,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_db_assigned_auftraggeber = {'auftraggeber': auftraggeber2}
    cls.attributes_values_db_assigned_historisch = {'historisch': True}
    cls.attributes_values_db_assigned_labor = {'labor': labor2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'historisch': False,
      'auftraggeber': str(auftraggeber1.pk),
      'labor': str(labor1.pk),
      'bezeichnung': 'Bezeichnung3',
      'datum': VALID_DATE,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'historisch': False,
      'auftraggeber': str(auftraggeber1.pk),
      'labor': str(labor1.pk),
      'bezeichnung': 'Bezeichnung4',
      'datum': VALID_DATE,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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

  def test_view_assign_auftraggeber(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_auftraggeber,
      'auftraggeber',
      str(self.auftraggeber2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_historisch(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_historisch,
      'historisch',
      str(True),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_labor(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_labor,
      'labor',
      str(self.labor2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class BaugrunduntersuchungenDokumenteTest(DefaultComplexModelTestCase):
  """
  Baugrunduntersuchungen:
  Dokumente
  """

  model = Baugrunduntersuchungen_Dokumente
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    baugrunduntersuchung = create_baugrunduntersuchung()
    pdf = File(open(VALID_PDF_FILE, 'rb'))
    cls.attributes_values_db_initial = {'baugrunduntersuchung': baugrunduntersuchung, 'pdf': pdf}
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {'aktiv': False}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'baugrunduntersuchung': str(baugrunduntersuchung.pk),
      'dateiname_original': 'pdf_valid.pdf',
    }
    cls.attributes_values_view_updated = {
      'aktiv': False,
      'baugrunduntersuchung': str(baugrunduntersuchung.pk),
      'dateiname_original': 'pdf_valid.pdf',
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()
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

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial_cleaned, 204, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))


class BaugrunduntersuchungenBaugrundbohrungenTest(DefaultComplexModelTestCase):
  """
  Baugrunduntersuchungen:
  Baugrundbohrungen
  """

  model = Baugrunduntersuchungen_Baugrundbohrungen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    baugrunduntersuchung = create_baugrunduntersuchung()
    cls.attributes_values_db_initial = {
      'baugrunduntersuchung': baugrunduntersuchung,
      'nummer': 'Nummer1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'nummer': 'Nummer2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'baugrunduntersuchung': str(baugrunduntersuchung.pk),
      'nummer': 'Nummer3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'baugrunduntersuchung': str(baugrunduntersuchung.pk),
      'nummer': 'Nummer4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'nummer': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


#
# Baustellen-Fotodokumentation
#


def baustelle_data():
  verkehrliche_lage1 = Verkehrliche_Lagen_Baustellen.objects.create(
    verkehrliche_lage='verkehrliche Lage 1'
  )
  verkehrliche_lage2 = Verkehrliche_Lagen_Baustellen.objects.create(
    verkehrliche_lage='verkehrliche Lage 2'
  )
  sparte1 = Sparten_Baustellen.objects.create(sparte='Sparte 1')
  sparte2 = Sparten_Baustellen.objects.create(sparte='Sparte 2')
  auftraggeber1 = Auftraggeber_Baustellen.objects.create(auftraggeber='Auftraggeber1')
  auftraggeber2 = Auftraggeber_Baustellen.objects.create(auftraggeber='Auftraggeber2')
  return verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber1, auftraggeber2


class BaustellenFotodokumentationBaustellenTest(DefaultComplexModelTestCase):
  """
  Baustellen-Fotodokumentation:
  Baustellen
  """

  model = Baustellen_Fotodokumentation_Baustellen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber1, auftraggeber2 = (
      baustelle_data()
    )
    cls.auftraggeber2 = auftraggeber2
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'auftraggeber': auftraggeber1,
      'ansprechpartner': 'Ansprechpartner1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2',
      'auftraggeber': auftraggeber2,
    }
    cls.attributes_values_db_assigned = {'auftraggeber': auftraggeber2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'auftraggeber': str(auftraggeber1.pk),
      'ansprechpartner': 'Ansprechpartner3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'auftraggeber': str(auftraggeber2.pk),
      'ansprechpartner': 'Ansprechpartner4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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
      'auftraggeber',
      str(self.auftraggeber2.pk),
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
class BaustellenFotodokumentationFotosTest(DefaultComplexModelTestCase):
  """
  Baustellen-Fotodokumentation:
  Fotos
  """

  model = Baustellen_Fotodokumentation_Fotos
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber1, auftraggeber2 = (
      baustelle_data()
    )
    baustelle = Baustellen_Fotodokumentation_Baustellen.objects.create(
      bezeichnung='Bezeichnung',
      verkehrliche_lagen=[verkehrliche_lage1, verkehrliche_lage2],
      sparten=[sparte1, sparte2],
      auftraggeber=auftraggeber1,
      ansprechpartner='Ansprechpartner',
      geometrie=VALID_POINT_DB,
    )
    status1 = Status_Baustellen_Fotodokumentation_Fotos.objects.create(status='Status 1')
    status2 = Status_Baustellen_Fotodokumentation_Fotos.objects.create(status='Status 2')
    cls.status2 = status2
    status3 = Status_Baustellen_Fotodokumentation_Fotos.objects.create(status='Status 3')
    status4 = Status_Baustellen_Fotodokumentation_Fotos.objects.create(status='Status 4')
    foto = File(open(VALID_IMAGE_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'baustellen_fotodokumentation_baustelle': baustelle,
      'status': status1,
      'aufnahmedatum': VALID_DATE,
      'foto': foto,
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {'status': status2}
    cls.attributes_values_db_assigned_aufnahmedatum = {'aufnahmedatum': VALID_DATE}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'baustellen_fotodokumentation_baustelle': str(baustelle.pk),
      'status': str(status3.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'baustellen_fotodokumentation_baustelle': str(baustelle.pk),
      'status': str(status4.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()
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

  def test_view_add_multiple_files(self):
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
      True,
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
      False, self.model, self.attributes_values_db_initial_cleaned, 302, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign_status(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_updated,
      'status',
      str(self.status2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign_aufnahmedatum(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_assigned_aufnahmedatum,
      'aufnahmedatum',
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


#
# Baustellen (geplant)
#


def create_baustelle_geplant():
  verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber1, auftraggeber2 = (
    baustelle_data()
  )
  status = Status_Baustellen_geplant.objects.create(status='Status')
  return Baustellen_geplant.objects.create(
    bezeichnung='Bezeichnung',
    verkehrliche_lagen=[verkehrliche_lage1, verkehrliche_lage2],
    sparten=[sparte1, sparte2],
    beginn=VALID_DATE,
    ende=VALID_DATE,
    auftraggeber=auftraggeber1,
    ansprechpartner='Ansprechpartner',
    status=status,
    geometrie=VALID_MULTIPOLYGON_DB,
  )


class BaustellenGeplantTest(DefaultComplexModelTestCase):
  """
  Baustellen (geplant):
  Baustellen
  """

  model = Baustellen_geplant
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber1, auftraggeber2 = (
      baustelle_data()
    )
    cls.auftraggeber2 = auftraggeber2
    status1 = Status_Baustellen_geplant.objects.create(status='Status1')
    status2 = Status_Baustellen_geplant.objects.create(status='Status2')
    cls.status2 = status2
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'beginn': VALID_DATE,
      'ende': VALID_DATE,
      'auftraggeber': auftraggeber1,
      'ansprechpartner': 'Ansprechpartner1',
      'status': status1,
      'geometrie': VALID_MULTIPOLYGON_DB,
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2',
      'auftraggeber': auftraggeber2,
      'status': status2,
    }
    cls.attributes_values_db_assigned_auftraggeber = {'auftraggeber': auftraggeber2}
    cls.attributes_values_db_assigned_status = {'status': status2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'beginn': VALID_DATE,
      'ende': VALID_DATE,
      'auftraggeber': str(auftraggeber1.pk),
      'ansprechpartner': 'Ansprechpartner3',
      'status': str(status1.pk),
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'beginn': VALID_DATE,
      'ende': VALID_DATE,
      'auftraggeber': str(auftraggeber2.pk),
      'ansprechpartner': 'Ansprechpartner4',
      'status': str(status2.pk),
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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

  def test_view_assign_auftraggeber(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_auftraggeber,
      'auftraggeber',
      str(self.auftraggeber2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_status(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_status,
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


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class BaustellenGeplantDokumenteTest(DefaultComplexModelTestCase):
  """
  Baustellen (geplant):
  Dokumente
  """

  model = Baustellen_geplant_Dokumente
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    baustelle = create_baustelle_geplant()
    pdf = File(open(VALID_PDF_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'baustelle_geplant': baustelle,
      'bezeichnung': 'Bezeichnung1',
      'pdf': pdf,
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'baustelle_geplant': str(baustelle.pk),
      'bezeichnung': 'Bezeichnung3',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'baustelle_geplant': str(baustelle.pk),
      'bezeichnung': 'Bezeichnung4',
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()
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

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial_cleaned, 204, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))


class BaustellenGeplantLinksTest(DefaultComplexModelTestCase):
  """
  Baustellen (geplant):
  Links
  """

  model = Baustellen_geplant_Links
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    baustelle = create_baustelle_geplant()
    cls.attributes_values_db_initial = {
      'baustelle_geplant': baustelle,
      'bezeichnung': 'Bezeichnung1',
      'link': 'https://worschdsupp.1.de',
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'baustelle_geplant': str(baustelle.pk),
      'bezeichnung': 'Bezeichnung3',
      'link': 'https://worschdsupp.3.de',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'baustelle_geplant': str(baustelle.pk),
      'bezeichnung': 'Bezeichnung4',
      'link': 'https://worschdsupp.4.de',
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


#
# Durchlässe
#


class DurchlaesseDurchlaesseTest(DefaultComplexModelTestCase):
  """
  Durchlässe:
  Durchlässe
  """

  model = Durchlaesse_Durchlaesse
  attributes_values_db_initial = {
    'aktenzeichen': 'RL.18-11-1',
    'zustaendigkeit': 'Zuständigkeit1',
    'bearbeiter': 'Bearbeiter1',
    'geometrie': VALID_POINT_DB,
  }
  attributes_values_db_updated = {'bearbeiter': 'Bearbeiter2'}
  attributes_values_view_initial = {
    'aktiv': True,
    'aktenzeichen': 'STR-E.20-1-1',
    'zustaendigkeit': 'Zuständigkeit3',
    'bearbeiter': 'Bearbeiter3',
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'aktenzeichen': 'DL.28-4',
    'zustaendigkeit': 'Zuständigkeit4',
    'bearbeiter': 'Bearbeiter4',
    'geometrie': VALID_POINT_VIEW,
  }
  attributes_values_view_invalid = {'zustaendigkeit': INVALID_STRING}

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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
      'kontrolle',
      '',
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
class DurchlaesseFotosTest(DefaultComplexModelTestCase):
  """
  Durchlässe:
  Fotos
  """

  model = Durchlaesse_Fotos
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    durchlass = Durchlaesse_Durchlaesse.objects.create(
      aktenzeichen='RL.18-11-1',
      zustaendigkeit='Zuständigkeit',
      bearbeiter='Bearbeiter',
      geometrie=VALID_POINT_DB,
    )
    foto = File(open(VALID_IMAGE_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'durchlaesse_durchlass': durchlass,
      'bemerkungen': 'Bemerkung1',
      'foto': foto,
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {'bemerkungen': 'Bemerkung2'}
    cls.attributes_values_db_assigned_aufnahmedatum = {'aufnahmedatum': VALID_DATE}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'durchlaesse_durchlass': str(durchlass.pk),
      'bemerkungen': 'Bemerkung3',
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'durchlaesse_durchlass': str(durchlass.pk),
      'bemerkungen': 'Bemerkung4',
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_invalid = {'bemerkungen': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()
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

  def test_view_add_multiple_files(self):
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
      True,
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
      False, self.model, self.attributes_values_db_initial_cleaned, 302, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_assigned_aufnahmedatum,
      'aufnahmedatum',
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


#
# Fallwildsuchen
#


class FallwildsuchenKontrollgebieteTest(DefaultComplexModelTestCase):
  """
  Fallwildsuchen:
  Kontrollgebiete
  """

  model = Fallwildsuchen_Kontrollgebiete
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    tierseuche = Tierseuchen.objects.create(bezeichnung='Bezeichnung')
    cls.attributes_values_db_initial = {
      'tierseuche': tierseuche,
      'bezeichnung': 'Bezeichnung1',
      'geometrie': VALID_POLYGON_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'tierseuche': str(tierseuche.pk),
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POLYGON_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'tierseuche': str(tierseuche.pk),
      'bezeichnung': 'Bezeichnung4',
      'geometrie': VALID_POLYGON_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class FallwildsuchenNachweiseTest(DefaultComplexModelTestCase):
  """
  Fallwildsuchen:
  Nachweise
  """

  model = Fallwildsuchen_Nachweise
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    tierseuche = Tierseuchen.objects.create(bezeichnung='Bezeichnung')
    kontrollgebiet = Fallwildsuchen_Kontrollgebiete.objects.create(
      tierseuche=tierseuche, bezeichnung='Bezeichnung', geometrie=VALID_POLYGON_DB
    )
    art_kontrolle1 = Arten_Fallwildsuchen_Kontrollen.objects.create(art='Art1')
    art_kontrolle2 = Arten_Fallwildsuchen_Kontrollen.objects.create(art='Art2')
    art_kontrolle3 = Arten_Fallwildsuchen_Kontrollen.objects.create(art='Art3')
    art_kontrolle4 = Arten_Fallwildsuchen_Kontrollen.objects.create(art='Art4')
    cls.attributes_values_db_initial = {
      'kontrollgebiet': kontrollgebiet,
      'art_kontrolle': art_kontrolle1,
      'startzeitpunkt': VALID_DATETIME,
      'endzeitpunkt': VALID_DATETIME,
      'geometrie': VALID_MULTILINE_DB,
    }
    cls.attributes_values_db_updated = {'art_kontrolle': art_kontrolle2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'kontrollgebiet': str(kontrollgebiet.pk),
      'art_kontrolle': str(art_kontrolle3.pk),
      'startzeitpunkt': VALID_DATETIME,
      'endzeitpunkt': VALID_DATETIME,
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'kontrollgebiet': str(kontrollgebiet.pk),
      'art_kontrolle': str(art_kontrolle4.pk),
      'startzeitpunkt': VALID_DATETIME,
      'endzeitpunkt': VALID_DATETIME,
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


#
# Feuerwehrzufahrten
#


class FeuerwehrzufahrtenFeuerwehrzufahrtenTest(DefaultComplexModelTestCase):
  """
  Feuerwehrzufahrten:
  Feuerwehrzufahrten
  """

  model = Feuerwehrzufahrten_Feuerwehrzufahrten
  attributes_values_db_initial = {'registriernummer': 1234}
  attributes_values_db_updated = {'registriernummer': 5432}
  attributes_values_view_initial = {'aktiv': True, 'registriernummer': 2345}
  attributes_values_view_updated = {'aktiv': True, 'registriernummer': 6543}
  attributes_values_view_invalid = {'bemerkungen': INVALID_STRING}

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class FeuerwehrzufahrtenSchilderTest(DefaultComplexModelTestCase):
  """
  Feuerwehrzufahrten:
  Schilder
  """

  model = Feuerwehrzufahrten_Schilder
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    feuerwehrzufahrt = Feuerwehrzufahrten_Feuerwehrzufahrten.objects.create(registriernummer=1234)
    typ = Typen_Feuerwehrzufahrten_Schilder.objects.create(typ='Typ')
    cls.attributes_values_db_initial = {
      'feuerwehrzufahrt': feuerwehrzufahrt,
      'typ': typ,
      'hinweise_aufstellort': 'Hinweise1',
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'hinweise_aufstellort': 'Hinweise2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'feuerwehrzufahrt': str(feuerwehrzufahrt.pk),
      'typ': str(typ.pk),
      'hinweise_aufstellort': 'Hinweise3',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'feuerwehrzufahrt': str(feuerwehrzufahrt.pk),
      'typ': str(typ.pk),
      'hinweise_aufstellort': 'Hinweise4',
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'hinweise_aufstellort': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


#
# Freizeitsport
#


class FreizeitsportTest(DefaultComplexModelTestCase):
  """
  Freizeitsport:
  Freizeitsport
  """

  model = Freizeitsport
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    bodenart1 = Bodenarten_Freizeitsport.objects.create(bodenart='Bodenart1')
    bodenart2 = Bodenarten_Freizeitsport.objects.create(bodenart='Bodenart2')
    sportart1 = Freizeitsportarten.objects.create(bezeichnung='Sportart1')
    sportart2 = Freizeitsportarten.objects.create(bezeichnung='Sportart2')
    besonderheit1 = Besonderheiten_Freizeitsport.objects.create(besonderheit='Besonderheit1')
    besonderheit2 = Besonderheiten_Freizeitsport.objects.create(besonderheit='Besonderheit2')
    cls.attributes_values_db_initial = {
      'staedtisch': True,
      'bodenarten': [bodenart1, bodenart2],
      'sportarten': [sportart1, sportart2],
      'besonderheiten': [besonderheit1, besonderheit2],
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'staedtisch': False}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'staedtisch': True,
      'bodenarten': [bodenart1, bodenart2],
      'sportarten': [sportart1, sportart2],
      'besonderheiten': [besonderheit1, besonderheit2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'staedtisch': False,
      'bodenarten': [bodenart1, bodenart2],
      'sportarten': [sportart1, sportart2],
      'besonderheiten': [besonderheit1, besonderheit2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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
class FreizeitsportFotosTest(DefaultComplexModelTestCase):
  """
  Freizeitsport:
  Fotos
  """

  model = Freizeitsport_Fotos
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    sportart1 = Freizeitsportarten.objects.create(bezeichnung='Sportart1')
    sportart2 = Freizeitsportarten.objects.create(bezeichnung='Sportart2')
    freizeitsport = Freizeitsport.objects.create(
      staedtisch=True, sportarten=[sportart1, sportart2], geometrie=VALID_POINT_DB
    )
    foto = File(open(VALID_IMAGE_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'freizeitsport': freizeitsport,
      'oeffentlich_sichtbar': True,
      'bemerkungen': 'Bemerkung1',
      'foto': foto,
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {'bemerkungen': 'Bemerkung2'}
    cls.attributes_values_db_assigned_aufnahmedatum = {'aufnahmedatum': VALID_DATE}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'freizeitsport': str(freizeitsport.pk),
      'oeffentlich_sichtbar': True,
      'bemerkungen': 'Bemerkung3',
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'freizeitsport': str(freizeitsport.pk),
      'oeffentlich_sichtbar': True,
      'bemerkungen': 'Bemerkung4',
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_invalid = {'bemerkungen': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()
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

  def test_view_add_multiple_files(self):
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
      True,
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
      False, self.model, self.attributes_values_db_initial_cleaned, 302, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_assigned_aufnahmedatum,
      'aufnahmedatum',
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


#
# Geh- und Radwegereinigung
#


class GehRadwegereinigungTest(DefaultComplexModelTestCase):
  """
  Geh- und Radwegereinigung:
  Geh- und Radwegereinigung
  """

  model = Geh_Radwegereinigung
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    gemeindeteil = Gemeindeteile.objects.create(
      gemeindeteil='Gemeindeteil', geometrie=VALID_MULTIPOLYGON_DB
    )
    wegeart = Arten_Wege.objects.create(art='Art')
    cls.attributes_values_db_initial = {
      'gemeindeteil': gemeindeteil,
      'beschreibung': 'Beschreibung1',
      'wegeart': wegeart,
      'geometrie': VALID_MULTILINE_DB,
    }
    cls.attributes_values_db_updated = {'beschreibung': 'Beschreibung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': '0000000000-000',
      'gemeindeteil': str(gemeindeteil.pk),
      'beschreibung': 'Beschreibung3',
      'wegeart': str(wegeart.pk),
      'laenge': 0,
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': '0000000000-000',
      'gemeindeteil': str(gemeindeteil.pk),
      'beschreibung': 'Beschreibung4',
      'wegeart': str(wegeart.pk),
      'laenge': 0,
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_invalid = {'beschreibung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class GehRadwegereinigungFlaechenTest(DefaultComplexModelTestCase):
  """
  Geh- und Radwegereinigung:
  Flächen
  """

  model = Geh_Radwegereinigung_Flaechen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    gemeindeteil = Gemeindeteile.objects.create(
      gemeindeteil='Gemeindeteil', geometrie=VALID_MULTIPOLYGON_DB
    )
    wegeart = Arten_Wege.objects.create(art='Art')
    geh_und_radwegereinigung = Geh_Radwegereinigung.objects.create(
      gemeindeteil=gemeindeteil,
      beschreibung='Beschreibung',
      wegeart=wegeart,
      geometrie=VALID_MULTILINE_DB,
    )
    cls.attributes_values_db_initial = {
      'geh_und_radwegereinigung': geh_und_radwegereinigung,
      'geometrie': VALID_MULTIPOLYGON_DB,
    }
    cls.attributes_values_db_updated = {'aktiv': False}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'geh_und_radwegereinigung': str(geh_und_radwegereinigung.pk),
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': False,
      'geh_und_radwegereinigung': str(geh_und_radwegereinigung.pk),
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


#
# Haltestellenkataster
#


class HaltestellenkatasterHaltestellenTest(DefaultComplexModelTestCase):
  """
  Haltestellenkataster:
  Haltestellen
  """

  model = Haltestellenkataster_Haltestellen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    verkehrsmittelklasse1 = Verkehrsmittelklassen.objects.create(
      verkehrsmittelklasse='Verkehrsmittelklasse1'
    )
    verkehrsmittelklasse2 = Verkehrsmittelklassen.objects.create(
      verkehrsmittelklasse='Verkehrsmittelklasse2'
    )
    cls.attributes_values_db_initial = {
      'hst_bezeichnung': 'Haltestellenbezeichnung1',
      'hst_verkehrsmittelklassen': [verkehrsmittelklasse1, verkehrsmittelklasse2],
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'hst_bezeichnung': 'Haltestellenbezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': 2,
      'hst_bezeichnung': 'Haltestellenbezeichnung3',
      'hst_verkehrsmittelklassen': [verkehrsmittelklasse1, verkehrsmittelklasse2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': 3,
      'hst_bezeichnung': 'Haltestellenbezeichnung4',
      'hst_verkehrsmittelklassen': [verkehrsmittelklasse1, verkehrsmittelklasse2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'hst_bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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
class HaltestellenkatasterFotosTest(DefaultComplexModelTestCase):
  """
  Haltestellenkataster:
  Fotos
  """

  model = Haltestellenkataster_Fotos
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    verkehrsmittelklasse1 = Verkehrsmittelklassen.objects.create(
      verkehrsmittelklasse='Verkehrsmittelklasse1'
    )
    verkehrsmittelklasse2 = Verkehrsmittelklassen.objects.create(
      verkehrsmittelklasse='Verkehrsmittelklasse2'
    )
    haltestelle = Haltestellenkataster_Haltestellen.objects.create(
      hst_bezeichnung='Haltestellenbezeichnung',
      hst_verkehrsmittelklassen=[verkehrsmittelklasse1, verkehrsmittelklasse2],
      geometrie=VALID_POINT_DB,
    )
    motiv1 = Fotomotive_Haltestellenkataster.objects.create(fotomotiv='Fotomotiv 1')
    motiv2 = Fotomotive_Haltestellenkataster.objects.create(fotomotiv='Fotomotiv 2')
    cls.motiv2 = motiv2
    motiv3 = Fotomotive_Haltestellenkataster.objects.create(fotomotiv='Fotomotiv 3')
    motiv4 = Fotomotive_Haltestellenkataster.objects.create(fotomotiv='Fotomotiv 4')
    foto = File(open(VALID_IMAGE_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'haltestellenkataster_haltestelle': haltestelle,
      'motiv': motiv1,
      'aufnahmedatum': VALID_DATE,
      'foto': foto,
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {'motiv': motiv2}
    cls.attributes_values_db_assigned_aufnahmedatum = {'aufnahmedatum': VALID_DATE}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'haltestellenkataster_haltestelle': str(haltestelle.pk),
      'motiv': str(motiv3.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'haltestellenkataster_haltestelle': str(haltestelle.pk),
      'motiv': str(motiv4.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()
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

  def test_view_add_multiple_files(self):
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
      True,
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
      False, self.model, self.attributes_values_db_initial_cleaned, 302, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign_status(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_updated,
      'motiv',
      str(self.motiv2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign_aufnahmedatum(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_assigned_aufnahmedatum,
      'aufnahmedatum',
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


#
# Kleinkläranlagen
#


class KleinklaeranlagenTest(DefaultComplexModelTestCase):
  """
  Kleinkläranlagen:
  Kleinkläranlagen
  """

  model = Kleinklaeranlagen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    typ = Typen_Kleinklaeranlagen.objects.create(typ='Typ')
    cls.attributes_values_db_initial = {
      'd3': '538.111-047',
      'we_datum': VALID_DATE,
      'typ': typ,
      'einleitstelle': 'Einleitstelle1',
      'gewaesser_berichtspflichtig': True,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'einleitstelle': 'Einleitstelle2'}
    cls.attributes_values_view_initial = {
      'd3': '538.111-047',
      'we_datum': VALID_DATE,
      'typ': str(typ.pk),
      'einleitstelle': 'Einleitstelle3',
      'gewaesser_berichtspflichtig': True,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'd3': '538.111-047',
      'we_datum': VALID_DATE,
      'typ': str(typ.pk),
      'einleitstelle': 'Einleitstelle4',
      'gewaesser_berichtspflichtig': True,
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'einleitstelle': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class KleinklaeranlagenGewaessereinleitungsorteTest(DefaultComplexModelTestCase):
  """
  Kleinkläranlagen:
  Orte der Gewässereinleitung
  """

  model = Kleinklaeranlagen_Gewaessereinleitungsorte
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    typ = Typen_Kleinklaeranlagen.objects.create(typ='Typ')
    kleinklaeranlage1 = Kleinklaeranlagen.objects.create(
      d3='538.111-047',
      we_datum=VALID_DATE,
      typ=typ,
      einleitstelle='Einleitstelle1',
      gewaesser_berichtspflichtig=True,
      geometrie=VALID_POINT_DB,
    )
    kleinklaeranlage2 = Kleinklaeranlagen.objects.create(
      d3='538.111-047',
      we_datum=VALID_DATE,
      typ=typ,
      einleitstelle='Einleitstelle2',
      gewaesser_berichtspflichtig=False,
      geometrie=VALID_POINT_DB,
    )
    cls.attributes_values_db_initial = {
      'kleinklaeranlage': kleinklaeranlage1,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'kleinklaeranlage': kleinklaeranlage2}
    cls.attributes_values_view_initial = {
      'kleinklaeranlage': str(kleinklaeranlage1.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'kleinklaeranlage': str(kleinklaeranlage2.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


#
# Lichtwellenleiterinfrastruktur
#


class LichtwellenleiterinfrastrukturAbschnitteTest(DefaultComplexModelTestCase):
  """
  Lichtwellenleiterinfrastruktur:
  Abschnitte
  """

  model = Lichtwellenleiterinfrastruktur_Abschnitte
  attributes_values_db_initial = {'bezeichnung': 'Bezeichnung1'}
  attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
  attributes_values_view_initial = {'bezeichnung': 'Bezeichnung3'}
  attributes_values_view_updated = {'bezeichnung': 'Bezeichnung4'}
  attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class LichtwellenleiterinfrastrukturTest(DefaultComplexModelTestCase):
  """
  Lichtwellenleiterinfrastruktur:
  Lichtwellenleiterinfrastruktur
  """

  model = Lichtwellenleiterinfrastruktur
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    abschnitt1 = Lichtwellenleiterinfrastruktur_Abschnitte.objects.create(
      bezeichnung='Bezeichnung1'
    )
    abschnitt2 = Lichtwellenleiterinfrastruktur_Abschnitte.objects.create(
      bezeichnung='Bezeichnung2'
    )
    cls.abschnitt2 = abschnitt2
    objektart1 = Objektarten_Lichtwellenleiterinfrastruktur.objects.create(objektart='Objektart1')
    objektart2 = Objektarten_Lichtwellenleiterinfrastruktur.objects.create(objektart='Objektart2')
    cls.objektart2 = objektart2
    kabeltyp1 = Kabeltypen_Lichtwellenleiterinfrastruktur.objects.create(kabeltyp='Kabeltyp1')
    kabeltyp2 = Kabeltypen_Lichtwellenleiterinfrastruktur.objects.create(kabeltyp='Kabeltyp2')
    cls.kabeltyp2 = kabeltyp2
    cls.attributes_values_db_initial = {
      'abschnitt': abschnitt1,
      'objektart': objektart1,
      'kabeltyp': kabeltyp1,
      'geometrie': VALID_MULTILINE_DB,
    }
    cls.attributes_values_db_updated = {
      'abschnitt': abschnitt2,
      'objektart': objektart2,
      'kabeltyp': kabeltyp2,
    }
    cls.attributes_values_db_assigned_abschnitt = {'abschnitt': abschnitt2}
    cls.attributes_values_db_assigned_objektart = {'objektart': objektart2}
    cls.attributes_values_db_assigned_kabeltyp = {'kabeltyp': kabeltyp2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'abschnitt': str(abschnitt1.pk),
      'objektart': str(objektart1.pk),
      'kabeltyp': str(kabeltyp1.pk),
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'abschnitt': str(abschnitt2.pk),
      'objektart': str(objektart2.pk),
      'kabeltyp': str(kabeltyp2.pk),
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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

  def test_view_assign_abschnitt(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_abschnitt,
      'abschnitt',
      str(self.abschnitt2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_objektart(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_objektart,
      'objektart',
      str(self.objektart2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_kabeltyp(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_kabeltyp,
      'kabeltyp',
      str(self.kabeltyp2.pk),
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


#
# Parkscheinautomaten
#


class ParkscheinautomatenTarifeTest(DefaultComplexModelTestCase):
  """
  Parkscheinautomaten:
  Tarife
  """

  model = Parkscheinautomaten_Tarife
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    normaltarif_parkdauer_min_einheit = Zeiteinheiten.objects.create(zeiteinheit='Zeiteinheit1')
    normaltarif_parkdauer_max_einheit = Zeiteinheiten.objects.create(zeiteinheit='Zeiteinheit2')
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'zeiten': 'Bewirtschaftungszeiten1',
      'normaltarif_parkdauer_min': 1,
      'normaltarif_parkdauer_min_einheit': normaltarif_parkdauer_min_einheit,
      'normaltarif_parkdauer_max': 2,
      'normaltarif_parkdauer_max_einheit': normaltarif_parkdauer_max_einheit,
      'zugelassene_muenzen': 'zugelassene Münzen 1',
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'zeiten': 'Bewirtschaftungszeiten3',
      'normaltarif_parkdauer_min': 1,
      'normaltarif_parkdauer_min_einheit': str(normaltarif_parkdauer_min_einheit.pk),
      'normaltarif_parkdauer_max': 2,
      'normaltarif_parkdauer_max_einheit': str(normaltarif_parkdauer_max_einheit.pk),
      'zugelassene_muenzen': 'zugelassene Münzen 2',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'zeiten': 'Bewirtschaftungszeiten4',
      'normaltarif_parkdauer_min': 1,
      'normaltarif_parkdauer_min_einheit': str(normaltarif_parkdauer_min_einheit.pk),
      'normaltarif_parkdauer_max': 2,
      'normaltarif_parkdauer_max_einheit': str(normaltarif_parkdauer_max_einheit.pk),
      'zugelassene_muenzen': 'zugelassene Münzen 3',
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class ParkscheinautomatenParkscheinautomatenTest(DefaultComplexModelTestCase):
  """
  Parkscheinautomaten:
  Parkscheinautomaten
  """

  model = Parkscheinautomaten_Parkscheinautomaten
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    normaltarif_parkdauer_min_einheit = Zeiteinheiten.objects.create(zeiteinheit='Zeiteinheit1')
    normaltarif_parkdauer_max_einheit = Zeiteinheiten.objects.create(zeiteinheit='Zeiteinheit2')
    tarif = Parkscheinautomaten_Tarife.objects.create(
      bezeichnung='Bezeichnung',
      zeiten='Bewirtschaftungszeiten',
      normaltarif_parkdauer_min=1,
      normaltarif_parkdauer_min_einheit=normaltarif_parkdauer_min_einheit,
      normaltarif_parkdauer_max=2,
      normaltarif_parkdauer_max_einheit=normaltarif_parkdauer_max_einheit,
      zugelassene_muenzen='zugelassene Münzen',
    )
    zone = Zonen_Parkscheinautomaten.objects.create(zone='A')
    e_anschluss = E_Anschluesse_Parkscheinautomaten.objects.create(e_anschluss='E-Anschluss')
    cls.attributes_values_db_initial = {
      'parkscheinautomaten_tarif': tarif,
      'nummer': 1,
      'bezeichnung': 'Bezeichnung1',
      'zone': zone,
      'handyparkzone': 456789,
      'geraetenummer': '34_56789',
      'e_anschluss': e_anschluss,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'parkscheinautomaten_tarif': str(tarif.pk),
      'nummer': 3,
      'bezeichnung': 'Bezeichnung3',
      'zone': str(zone.pk),
      'handyparkzone': 456789,
      'geraetenummer': '34_56789',
      'e_anschluss': str(e_anschluss.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'parkscheinautomaten_tarif': str(tarif.pk),
      'nummer': 4,
      'bezeichnung': 'Bezeichnung4',
      'zone': str(zone.pk),
      'handyparkzone': 456789,
      'geraetenummer': '34_56789',
      'e_anschluss': str(e_anschluss.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


@override_settings(
  PC_MEDIA_ROOT=TEST_PC_MEDIA_DIR,
  VCP_API_URL=TEST_VCP_API_URL,
  CELERY_BROKER_URL=TEST_CELERY_BROKER_URL,
  CELERY_RESULT_BACKEND=TEST_CELERY_RESULT_BACKEND,
)
class PunktwolkenTest(DefaultComplexModelTestCase):
  """
  Punktwolken Projekte:
  Punktwolken Tests
  """

  model = Punktwolken
  create_test_object_in_classmethod = False
  create_test_sebset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    punktwolken_projekt = Punktwolken_Projekte.objects.create(
      bezeichnung='Test-Projekt', beschreibung='Beschreibung des Test-Projekts'
    )
    with Path(VALID_POINTCLOUD_FILE).open('rb') as f:
      valid_pointcloud_file_content = f.read()
    punktwolke = SimpleUploadedFile(name='las_valid.las', content=valid_pointcloud_file_content)
    cls.attributes_values_db_initial = {
      'projekt': punktwolken_projekt,
      'dateiname': punktwolke.name,
      'punktwolke': punktwolke,
      'geometrie': VALID_POLYGON_DB,
      'file_size': 2000,
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()
    remove_uploaded_test_files(Path(settings.PC_MEDIA_ROOT))

  def test_create(self):
    self.generic_create_test(self.model, self.attributes_values_db_initial_cleaned)
    remove_uploaded_test_files(Path(settings.PC_MEDIA_ROOT))

  def test_delete(self):
    self.generic_delete_test(self.model)
    remove_uploaded_test_files(Path(settings.PC_MEDIA_ROOT))


@override_settings(
  PC_MEDIA_ROOT=TEST_PC_MEDIA_DIR,
  VCP_API_URL=TEST_VCP_API_URL,
  CELERY_BROKER_URL=TEST_CELERY_BROKER_URL,
  CELERY_RESULT_BACKEND=TEST_CELERY_RESULT_BACKEND,
)
class PunktwolkenProjekteTest(DefaultComplexModelTestCase):
  """
  Punktwolken Projekte:
  Punktwolken Projekte Tests
  """

  model = Punktwolken_Projekte
  attributes_values_db_initial = {
    'bezeichnung': 'Test-Projekt',
    'beschreibung': 'Beschreibung des Test-Projekts',
  }
  attributes_values_db_updated = {
    'bezeichnung': 'Test-Projekt2',
    'beschreibung': 'Neue Beschreibung',
  }
  attributes_values_view_initial = {
    'bezeichnung': 'Test-Projekt3',
    'beschreibung': 'Beschreibung des Test-Projekts',
  }
  attributes_values_view_updated = {
    'bezeichnung': 'Test-Projekt4',
    'beschreibung': 'Neue Beschreibung',
  }

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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

  def test_view_map(self):
    self.generic_view_test(
      self.model,
      self.model.__name__ + '_map',
      {},
      200,
      'text/html; charset=utf-8',
      MAP_VIEW_STRING,
    )


#
# RSAG
#


class RSAGGleiseTest(GenericRSAGTestCase):
  """
  RSAG:
  Gleise
  """

  model = RSAG_Gleise

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class RSAGMastenTest(DefaultComplexModelTestCase):
  """
  RSAG:
  Masten
  """

  model = RSAG_Masten
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    masttyp = Masttypen_RSAG.objects.create(typ='Typ', erlaeuterung='Erläuterung')
    cls.attributes_values_db_initial = {
      'mastnummer': 'Mastnummer1',
      'masttyp': masttyp,
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'mastnummer': 'Mastnummer2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'mastnummer': 'Mastnummer3',
      'masttyp': str(masttyp.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'mastnummer': 'Mastnummer4',
      'masttyp': str(masttyp.pk),
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'mastnummer': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class RSAGLeitungenTest(DefaultComplexModelTestCase):
  """
  RSAG:
  Oberleitungen
  """

  model = RSAG_Leitungen
  attributes_values_db_initial = {'aktiv': True, 'geometrie': VALID_LINE_DB}
  attributes_values_db_updated = {'aktiv': False}
  attributes_values_view_initial = {'aktiv': True, 'geometrie': VALID_LINE_VIEW}
  attributes_values_view_updated = {'aktiv': False, 'geometrie': VALID_LINE_VIEW}
  attributes_values_view_invalid = {}

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class RSAGQuertraegerTest(DefaultComplexModelTestCase):
  """
  RSAG:
  Querträger
  """

  model = RSAG_Quertraeger
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    masttyp = Masttypen_RSAG.objects.create(typ='Typ', erlaeuterung='Erläuterung')
    mast = RSAG_Masten.objects.create(
      mastnummer='Mastnummer', masttyp=masttyp, geometrie=VALID_POINT_DB
    )
    cls.attributes_values_db_initial = {
      'mast': mast,
      'quelle': 'Quelle1',
      'geometrie': VALID_LINE_DB,
    }
    cls.attributes_values_db_updated = {'quelle': 'Quelle2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'mast': str(mast.pk),
      'quelle': 'Quelle3',
      'geometrie': VALID_LINE_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'mast': str(mast.pk),
      'quelle': 'Quelle4',
      'geometrie': VALID_LINE_VIEW,
    }
    cls.attributes_values_view_invalid = {'quelle': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class RSAGSpanndraehteTest(GenericRSAGTestCase):
  """
  RSAG:
  Spanndrähte
  """

  model = RSAG_Spanndraehte

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


#
# Spielplätze
#


class SpielplaetzeTest(DefaultComplexModelTestCase):
  """
  Spielplätze:
  Spielplätze
  """

  model = Spielplaetze
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    bodenart1 = Bodenarten_Spielplaetze.objects.create(bodenart='Bodenart1')
    bodenart2 = Bodenarten_Spielplaetze.objects.create(bodenart='Bodenart2')
    spielgeraet1 = Spielgeraete.objects.create(bezeichnung='Spielgeraet1')
    spielgeraet2 = Spielgeraete.objects.create(bezeichnung='Spielgeraet2')
    besonderheit1 = Besonderheiten_Spielplaetze.objects.create(besonderheit='Besonderheit1')
    besonderheit2 = Besonderheiten_Spielplaetze.objects.create(besonderheit='Besonderheit2')
    cls.attributes_values_db_initial = {
      'staedtisch': True,
      'bodenarten': [bodenart1, bodenart2],
      'spielgeraete': [spielgeraet1, spielgeraet2],
      'besonderheiten': [besonderheit1, besonderheit2],
      'geometrie': VALID_POINT_DB,
    }
    cls.attributes_values_db_updated = {'staedtisch': False}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'staedtisch': True,
      'bodenarten': [bodenart1, bodenart2],
      'spielgeraete': [spielgeraet1, spielgeraet2],
      'besonderheiten': [besonderheit1, besonderheit2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'staedtisch': False,
      'bodenarten': [bodenart1, bodenart2],
      'spielgeraete': [spielgeraet1, spielgeraet2],
      'besonderheiten': [besonderheit1, besonderheit2],
      'geometrie': VALID_POINT_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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
class SpielplaetzeFotosTest(DefaultComplexModelTestCase):
  """
  Spielplätze:
  Fotos
  """

  model = Spielplaetze_Fotos
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    spielplatz = Spielplaetze.objects.create(staedtisch=True, geometrie=VALID_POINT_DB)
    foto = File(open(VALID_IMAGE_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'spielplatz': spielplatz,
      'oeffentlich_sichtbar': True,
      'bemerkungen': 'Bemerkung1',
      'foto': foto,
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {'bemerkungen': 'Bemerkung2'}
    cls.attributes_values_db_assigned_aufnahmedatum = {'aufnahmedatum': VALID_DATE}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'spielplatz': str(spielplatz.pk),
      'oeffentlich_sichtbar': True,
      'bemerkungen': 'Bemerkung3',
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'spielplatz': str(spielplatz.pk),
      'oeffentlich_sichtbar': True,
      'bemerkungen': 'Bemerkung4',
      'dateiname_original': 'image_valid.jpg',
    }
    cls.attributes_values_view_invalid = {'bemerkungen': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()
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

  def test_view_add_multiple_files(self):
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
      True,
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
      False, self.model, self.attributes_values_db_initial_cleaned, 302, 'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_assign(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial_cleaned,
      self.attributes_values_db_assigned_aufnahmedatum,
      'aufnahmedatum',
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


#
# Straßen
#


class StrassenSimpleTest(DefaultComplexModelTestCase):
  """
  Straßen:
  Straßen
  """

  model = Strassen_Simple
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    kategorie1 = Kategorien_Strassen.objects.create(
      code=1, bezeichnung='Bezeichnung1', erlaeuterung='Erläuterung1'
    )
    kategorie2 = Kategorien_Strassen.objects.create(
      code=2, bezeichnung='Bezeichnung2', erlaeuterung='Erläuterung2'
    )
    cls.kategorie2 = kategorie2
    cls.attributes_values_db_initial = {
      'kategorie': kategorie1,
      'bezeichnung': 'Bezeichnung1',
      'schluessel': '12345',
      'geometrie': VALID_MULTILINE_DB,
    }
    cls.attributes_values_db_updated = {'kategorie': kategorie2, 'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_db_assigned = {'kategorie': kategorie2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'kategorie': str(kategorie1.pk),
      'bezeichnung': 'Bezeichnung3',
      'schluessel': '54321',
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'kategorie': str(kategorie2.pk),
      'bezeichnung': 'Bezeichnung4',
      'schluessel': '35142',
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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
      'kategorie',
      str(self.kategorie2.pk),
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


class StrassenSimpleHistorieTest(DefaultComplexModelTestCase):
  """
  Straßen:
  Historie
  """

  model = Strassen_Simple_Historie
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    kategorie = Kategorien_Strassen.objects.create(
      code=1, bezeichnung='Bezeichnung', erlaeuterung='Erläuterung'
    )
    strasse_simple = Strassen_Simple.objects.create(
      kategorie=kategorie,
      bezeichnung='Bezeichnung',
      schluessel='12345',
      geometrie=VALID_MULTILINE_DB,
    )
    cls.attributes_values_db_initial = {
      'strasse_simple': strasse_simple,
      'beschluss': 'Beschluss1',
    }
    cls.attributes_values_db_updated = {'beschluss': 'Beschluss2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse_simple': str(strasse_simple.pk),
      'beschluss': 'Beschluss3',
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse_simple': str(strasse_simple.pk),
      'beschluss': 'Beschluss4',
    }
    cls.attributes_values_view_invalid = {'beschluss': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class StrassenSimpleNamensanalyseTest(DefaultComplexModelTestCase):
  """
  Straßen:
  Namensanalyse
  """

  model = Strassen_Simple_Namensanalyse
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    kategorie = Kategorien_Strassen.objects.create(
      code=1, bezeichnung='Bezeichnung', erlaeuterung='Erläuterung'
    )
    strasse_simple = Strassen_Simple.objects.create(
      kategorie=kategorie,
      bezeichnung='Bezeichnung',
      schluessel='12345',
      geometrie=VALID_MULTILINE_DB,
    )
    cls.attributes_values_db_initial = {'strasse_simple': strasse_simple, 'beruf': True}
    cls.attributes_values_db_updated = {'orte_landschaften': False}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strasse_simple': str(strasse_simple.pk),
      'historisch': True,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'strasse_simple': str(strasse_simple.pk),
      'religion': False,
    }
    cls.attributes_values_view_invalid = {'erlaeuterungen_richter': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


#
# Straßenreinigung
#


class StrassenreinigungTest(DefaultComplexModelTestCase):
  """
  Straßenreinigung:
  Straßenreinigung
  """

  model = Strassenreinigung
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    gemeindeteil = Gemeindeteile.objects.create(
      gemeindeteil='Gemeindeteil', geometrie=VALID_MULTIPOLYGON_DB
    )
    cls.attributes_values_db_initial = {
      'gemeindeteil': gemeindeteil,
      'beschreibung': 'Beschreibung1',
      'ausserhalb': False,
      'geometrie': VALID_MULTILINE_DB,
    }
    cls.attributes_values_db_updated = {'beschreibung': 'Beschreibung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': '0000000000-000',
      'gemeindeteil': str(gemeindeteil.pk),
      'beschreibung': 'Beschreibung3',
      'ausserhalb': False,
      'laenge': 0,
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': '0000000000-000',
      'gemeindeteil': str(gemeindeteil.pk),
      'beschreibung': 'Beschreibung4',
      'ausserhalb': False,
      'laenge': 0,
      'geometrie': VALID_MULTILINE_VIEW,
    }
    cls.attributes_values_view_invalid = {'beschreibung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class StrassenreinigungFlaechenTest(DefaultComplexModelTestCase):
  """
  Straßenreinigung:
  Flächen
  """

  model = Strassenreinigung_Flaechen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    gemeindeteil = Gemeindeteile.objects.create(
      gemeindeteil='Gemeindeteil', geometrie=VALID_MULTIPOLYGON_DB
    )
    strassenreinigung = Strassenreinigung.objects.create(
      gemeindeteil=gemeindeteil,
      beschreibung='Beschreibung',
      ausserhalb=False,
      geometrie=VALID_MULTILINE_DB,
    )
    cls.attributes_values_db_initial = {
      'strassenreinigung': strassenreinigung,
      'geometrie': VALID_MULTIPOLYGON_DB,
    }
    cls.attributes_values_db_updated = {'aktiv': False}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'strassenreinigung': str(strassenreinigung.pk),
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': False,
      'strassenreinigung': str(strassenreinigung.pk),
      'geometrie': VALID_MULTIPOLYGON_VIEW,
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


#
# UVP
#


class UVPVorhabenTest(DefaultComplexModelTestCase):
  """
  UVP:
  Vorhaben
  """

  model = UVP_Vorhaben
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    vorgangsart = Vorgangsarten_UVP_Vorhaben.objects.create(vorgangsart='Vorgangsart')
    genehmigungsbehoerde = Genehmigungsbehoerden_UVP_Vorhaben.objects.create(
      genehmigungsbehoerde='Genehmigungsbehörde'
    )
    rechtsgrundlage = Rechtsgrundlagen_UVP_Vorhaben.objects.create(
      rechtsgrundlage='Rechtsgrundlage'
    )
    typ = Typen_UVP_Vorhaben.objects.create(typ='Typ')
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'vorgangsart': vorgangsart,
      'genehmigungsbehoerde': genehmigungsbehoerde,
      'datum_posteingang_genehmigungsbehoerde': VALID_DATE,
      'rechtsgrundlage': rechtsgrundlage,
      'typ': typ,
      'geometrie': VALID_POLYGON_DB,
    }
    cls.attributes_values_db_updated = {'bezeichnung': 'Bezeichnung2'}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'vorgangsart': str(vorgangsart.pk),
      'genehmigungsbehoerde': str(genehmigungsbehoerde.pk),
      'datum_posteingang_genehmigungsbehoerde': VALID_DATE,
      'rechtsgrundlage': str(rechtsgrundlage.pk),
      'typ': str(typ.pk),
      'geometrie': VALID_POLYGON_VIEW,
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'vorgangsart': str(vorgangsart.pk),
      'genehmigungsbehoerde': str(genehmigungsbehoerde.pk),
      'datum_posteingang_genehmigungsbehoerde': VALID_DATE,
      'rechtsgrundlage': str(rechtsgrundlage.pk),
      'typ': str(typ.pk),
      'geometrie': VALID_POLYGON_VIEW,
    }
    cls.attributes_values_view_invalid = {'bezeichnung': INVALID_STRING}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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


class UVPVorpruefungenTest(DefaultComplexModelTestCase):
  """
  UVP:
  Vorprüfungen
  """

  model = UVP_Vorpruefungen
  create_test_object_in_classmethod = False
  create_test_subset_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    super().setUpTestData()
    vorgangsart = Vorgangsarten_UVP_Vorhaben.objects.create(vorgangsart='Vorgangsart')
    genehmigungsbehoerde = Genehmigungsbehoerden_UVP_Vorhaben.objects.create(
      genehmigungsbehoerde='Genehmigungsbehörde'
    )
    rechtsgrundlage = Rechtsgrundlagen_UVP_Vorhaben.objects.create(
      rechtsgrundlage='Rechtsgrundlage'
    )
    typ = Typen_UVP_Vorhaben.objects.create(typ='Typ')
    uvp_vorhaben = UVP_Vorhaben.objects.create(
      bezeichnung='Bezeichnung',
      vorgangsart=vorgangsart,
      genehmigungsbehoerde=genehmigungsbehoerde,
      datum_posteingang_genehmigungsbehoerde=VALID_DATE,
      rechtsgrundlage=rechtsgrundlage,
      typ=typ,
      geometrie=VALID_POLYGON_DB,
    )
    art1 = Arten_UVP_Vorpruefungen.objects.create(art='Art1')
    art2 = Arten_UVP_Vorpruefungen.objects.create(art='Art2')
    cls.art2 = art2
    ergebnis1 = Ergebnisse_UVP_Vorpruefungen.objects.create(ergebnis='Ergebnis1')
    ergebnis2 = Ergebnisse_UVP_Vorpruefungen.objects.create(ergebnis='Ergebnis2')
    cls.ergebnis2 = ergebnis2
    ergebnis3 = Ergebnisse_UVP_Vorpruefungen.objects.create(ergebnis='Ergebnis3')
    ergebnis4 = Ergebnisse_UVP_Vorpruefungen.objects.create(ergebnis='Ergebnis4')
    cls.attributes_values_db_initial = {
      'uvp_vorhaben': uvp_vorhaben,
      'art': art1,
      'datum_posteingang': VALID_DATE,
      'datum': VALID_DATE,
      'ergebnis': ergebnis1,
    }
    cls.attributes_values_db_updated = {'art': art2, 'ergebnis': ergebnis2}
    cls.attributes_values_db_assigned_art = {'art': art2}
    cls.attributes_values_db_assigned_datum_posteingang = {'datum_posteingang': VALID_DATE}
    cls.attributes_values_db_assigned_datum = {'datum': VALID_DATE}
    cls.attributes_values_db_assigned_ergebnis = {'ergebnis': ergebnis2}
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'uvp_vorhaben': str(uvp_vorhaben.pk),
      'art': str(art1.pk),
      'datum_posteingang': VALID_DATE,
      'datum': VALID_DATE,
      'ergebnis': str(ergebnis3.pk),
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'uvp_vorhaben': str(uvp_vorhaben.pk),
      'art': str(art2.pk),
      'datum_posteingang': VALID_DATE,
      'datum': VALID_DATE,
      'ergebnis': str(ergebnis4.pk),
    }
    cls.attributes_values_view_invalid = {}
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test()

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

  def test_view_assign_art(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_art,
      'art',
      str(self.art2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_assign_datum_posteingang(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_datum_posteingang,
      'datum_posteingang',
      str(VALID_DATE),
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

  def test_view_assign_ergebnis(self):
    self.generic_assign_view_test(
      self.model,
      self.attributes_values_db_initial,
      self.attributes_values_db_assigned_ergebnis,
      'ergebnis',
      str(self.ergebnis2.pk),
      204,
      'text/html; charset=utf-8',
      1,
    )

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True, self.model, self.attributes_values_db_initial, 204, 'text/html; charset=utf-8'
    )
