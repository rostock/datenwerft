from django.conf import settings
from django.core.files import File
from django.test import override_settings
from datenmanagement.models import Arten_Fallwildsuchen_Kontrollen, Arten_UVP_Vorpruefungen, \
  Auftraggeber_Baustellen, Baustellen_Fotodokumentation_Baustellen, \
  Baustellen_Fotodokumentation_Fotos, Baustellen_geplant, Baustellen_geplant_Dokumente, \
  Baustellen_geplant_Links, Durchlaesse_Durchlaesse, Durchlaesse_Fotos, \
  E_Anschluesse_Parkscheinautomaten, Ergebnisse_UVP_Vorpruefungen, \
  Fallwildsuchen_Kontrollgebiete, Fallwildsuchen_Nachweise, Fotomotive_Haltestellenkataster, \
  Genehmigungsbehoerden_UVP_Vorhaben, Haltestellenkataster_Fotos, \
  Haltestellenkataster_Haltestellen, Masttypen_RSAG, Parkscheinautomaten_Tarife, \
  Parkscheinautomaten_Parkscheinautomaten, Rechtsgrundlagen_UVP_Vorhaben, RSAG_Gleise, \
  RSAG_Leitungen, RSAG_Masten, RSAG_Quertraeger, RSAG_Spanndraehte, Sparten_Baustellen, \
  Status_Baustellen_Fotodokumentation_Fotos, Status_Baustellen_geplant, Tierseuchen, \
  Typen_UVP_Vorhaben, UVP_Vorhaben, UVP_Vorpruefungen, Verkehrliche_Lagen_Baustellen, \
  Verkehrsmittelklassen, Vorgangsarten_UVP_Vorhaben, Zeiteinheiten, Zonen_Parkscheinautomaten

from .base import DefaultComplexModelTestCase, GenericRSAGTestCase
from .constants_vars import *
from .functions import create_test_subset, remove_file_attributes_from_object_filter, \
  remove_uploaded_test_files


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
  sparte1 = Sparten_Baustellen.objects.create(
    sparte='Sparte 1'
  )
  sparte2 = Sparten_Baustellen.objects.create(
    sparte='Sparte 2'
  )
  auftraggeber = Auftraggeber_Baustellen.objects.create(
    auftraggeber='Auftraggeber'
  )
  return verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber


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
    verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber = baustelle_data()
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'auftraggeber': auftraggeber,
      'ansprechpartner': 'Ansprechpartner1',
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'auftraggeber': str(auftraggeber.pk),
      'ansprechpartner': 'Ansprechpartner3',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'auftraggeber': str(auftraggeber.pk),
      'ansprechpartner': 'Ansprechpartner4',
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
    verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber = \
      baustelle_data()
    baustelle = Baustellen_Fotodokumentation_Baustellen.objects.create(
      bezeichnung='Bezeichnung',
      verkehrliche_lagen=[verkehrliche_lage1, verkehrliche_lage2],
      sparten=[sparte1, sparte2],
      auftraggeber=auftraggeber,
      ansprechpartner='Ansprechpartner',
      geometrie=VALID_POINT_DB
    )
    status1 = Status_Baustellen_Fotodokumentation_Fotos.objects.create(
      status='Status 1'
    )
    status2 = Status_Baustellen_Fotodokumentation_Fotos.objects.create(
      status='Status 2'
    )
    status3 = Status_Baustellen_Fotodokumentation_Fotos.objects.create(
      status='Status 3'
    )
    status4 = Status_Baustellen_Fotodokumentation_Fotos.objects.create(
      status='Status 4'
    )
    foto = File(open(VALID_IMAGE_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'baustellen_fotodokumentation_baustelle': baustelle,
      'status': status1,
      'aufnahmedatum': VALID_DATE,
      'foto': foto
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {
      'status': status2
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'baustellen_fotodokumentation_baustelle': str(baustelle.pk),
      'status': str(status3.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_valid.jpg'
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'baustellen_fotodokumentation_baustelle': str(baustelle.pk),
      'status': str(status4.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_valid.jpg'
    }
    cls.attributes_values_view_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)
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
      True
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
      self.attributes_values_db_initial_cleaned,
      302,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial_cleaned,
      204,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))


#
# Baustellen (geplant)
#

def create_baustelle_geplant():
  verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber = baustelle_data()
  status = Status_Baustellen_geplant.objects.create(
    status='Status'
  )
  return Baustellen_geplant.objects.create(
    bezeichnung='Bezeichnung',
    verkehrliche_lagen=[verkehrliche_lage1, verkehrliche_lage2],
    sparten=[sparte1, sparte2],
    beginn=VALID_DATE,
    ende=VALID_DATE,
    auftraggeber=auftraggeber,
    ansprechpartner='Ansprechpartner',
    status=status,
    geometrie=VALID_MULTIPOLYGON_DB
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
    verkehrliche_lage1, verkehrliche_lage2, sparte1, sparte2, auftraggeber = baustelle_data()
    status = Status_Baustellen_geplant.objects.create(
      status='Status'
    )
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'beginn': VALID_DATE,
      'ende': VALID_DATE,
      'auftraggeber': auftraggeber,
      'ansprechpartner': 'Ansprechpartner1',
      'status': status,
      'geometrie': VALID_MULTIPOLYGON_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'beginn': VALID_DATE,
      'ende': VALID_DATE,
      'auftraggeber': str(auftraggeber.pk),
      'ansprechpartner': 'Ansprechpartner3',
      'status': str(status.pk),
      'geometrie': VALID_MULTIPOLYGON_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'verkehrliche_lagen': [verkehrliche_lage1, verkehrliche_lage2],
      'sparten': [sparte1, sparte2],
      'beginn': VALID_DATE,
      'ende': VALID_DATE,
      'auftraggeber': str(auftraggeber.pk),
      'ansprechpartner': 'Ansprechpartner4',
      'status': str(status.pk),
      'geometrie': VALID_MULTIPOLYGON_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
    dokument = File(open(VALID_PDF_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'baustelle_geplant': baustelle,
      'bezeichnung': 'Bezeichnung1',
      'dokument': dokument
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'baustelle_geplant': str(baustelle.pk),
      'bezeichnung': 'Bezeichnung3'
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'baustelle_geplant': str(baustelle.pk),
      'bezeichnung': 'Bezeichnung4'
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)
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

  def test_view_add_success(self):
    self.generic_add_update_view_test(
      False,
      self.model,
      self.attributes_values_view_initial,
      302,
      'text/html; charset=utf-8',
      1,
      VALID_PDF_FILE,
      'dokument',
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
      'dokument',
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
      self.attributes_values_db_initial_cleaned,
      302,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial_cleaned,
      204,
      'text/html; charset=utf-8'
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
      'link': 'https://worschdsupp.1.de'
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'baustelle_geplant': str(baustelle.pk),
      'bezeichnung': 'Bezeichnung3',
      'link': 'https://worschdsupp.3.de'
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'baustelle_geplant': str(baustelle.pk),
      'bezeichnung': 'Bezeichnung4',
      'link': 'https://worschdsupp.4.de'
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
    'geometrie': VALID_POINT_DB
  }
  attributes_values_db_updated = {
    'bearbeiter': 'Bearbeiter2'
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'aktenzeichen': 'STR-E.20-1-1',
    'zustaendigkeit': 'Zuständigkeit3',
    'bearbeiter': 'Bearbeiter3',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': True,
    'aktenzeichen': 'DL.28-4',
    'zustaendigkeit': 'Zuständigkeit4',
    'bearbeiter': 'Bearbeiter4',
    'geometrie': VALID_POINT_VIEW
  }
  attributes_values_view_invalid = {
    'zustaendigkeit': INVALID_STRING
  }

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
      geometrie=VALID_POINT_DB
    )
    foto = File(open(VALID_IMAGE_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'durchlaesse_durchlass': durchlass,
      'bemerkungen': 'Bemerkung1',
      'foto': foto
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {
      'bemerkungen': 'Bemerkung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'durchlaesse_durchlass': str(durchlass.pk),
      'bemerkungen': 'Bemerkung3',
      'dateiname_original': 'image_valid.jpg'
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'durchlaesse_durchlass': str(durchlass.pk),
      'bemerkungen': 'Bemerkung4',
      'dateiname_original': 'image_valid.jpg'
    }
    cls.attributes_values_view_invalid = {
      'bemerkungen': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)
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
      True
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
      self.attributes_values_db_initial_cleaned,
      302,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial_cleaned,
      204,
      'text/html; charset=utf-8'
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
    tierseuche = Tierseuchen.objects.create(
      bezeichnung='Bezeichnung'
    )
    cls.attributes_values_db_initial = {
      'tierseuche': tierseuche,
      'bezeichnung': 'Bezeichnung1',
      'geometrie': VALID_POLYGON_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'tierseuche': str(tierseuche.pk),
      'bezeichnung': 'Bezeichnung3',
      'geometrie': VALID_POLYGON_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'tierseuche': str(tierseuche.pk),
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

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
    tierseuche = Tierseuchen.objects.create(
      bezeichnung='Bezeichnung'
    )
    kontrollgebiet = Fallwildsuchen_Kontrollgebiete.objects.create(
      tierseuche=tierseuche,
      bezeichnung='Bezeichnung',
      geometrie=VALID_POLYGON_DB
    )
    art_kontrolle1 = Arten_Fallwildsuchen_Kontrollen.objects.create(
      art='Art1'
    )
    art_kontrolle2 = Arten_Fallwildsuchen_Kontrollen.objects.create(
      art='Art2'
    )
    art_kontrolle3 = Arten_Fallwildsuchen_Kontrollen.objects.create(
      art='Art3'
    )
    art_kontrolle4 = Arten_Fallwildsuchen_Kontrollen.objects.create(
      art='Art4'
    )
    cls.attributes_values_db_initial = {
      'kontrollgebiet': kontrollgebiet,
      'art_kontrolle': art_kontrolle1,
      'startzeitpunkt': VALID_DATETIME,
      'endzeitpunkt': VALID_DATETIME,
      'geometrie': VALID_MULTILINE_DB
    }
    cls.attributes_values_db_updated = {
      'art_kontrolle': art_kontrolle2
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'kontrollgebiet': str(kontrollgebiet.pk),
      'art_kontrolle': str(art_kontrolle3.pk),
      'startzeitpunkt': VALID_DATETIME,
      'endzeitpunkt': VALID_DATETIME,
      'geometrie': VALID_MULTILINE_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'kontrollgebiet': str(kontrollgebiet.pk),
      'art_kontrolle': str(art_kontrolle4.pk),
      'startzeitpunkt': VALID_DATETIME,
      'endzeitpunkt': VALID_DATETIME,
      'geometrie': VALID_MULTILINE_VIEW
    }
    cls.attributes_values_view_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'hst_bezeichnung': 'Haltestellenbezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'id': 2,
      'hst_bezeichnung': 'Haltestellenbezeichnung3',
      'hst_verkehrsmittelklassen': [verkehrsmittelklasse1, verkehrsmittelklasse2],
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'id': 3,
      'hst_bezeichnung': 'Haltestellenbezeichnung4',
      'hst_verkehrsmittelklassen': [verkehrsmittelklasse1, verkehrsmittelklasse2],
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'hst_bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
      geometrie=VALID_POINT_DB
    )
    motiv1 = Fotomotive_Haltestellenkataster.objects.create(
      fotomotiv='Fotomotiv 1'
    )
    motiv2 = Fotomotive_Haltestellenkataster.objects.create(
      fotomotiv='Fotomotiv 2'
    )
    motiv3 = Fotomotive_Haltestellenkataster.objects.create(
      fotomotiv='Fotomotiv 3'
    )
    motiv4 = Fotomotive_Haltestellenkataster.objects.create(
      fotomotiv='Fotomotiv 4'
    )
    foto = File(open(VALID_IMAGE_FILE, 'rb'))
    cls.attributes_values_db_initial = {
      'haltestellenkataster_haltestelle': haltestelle,
      'motiv': motiv1,
      'aufnahmedatum': VALID_DATE,
      'foto': foto
    }
    cls.attributes_values_db_initial_cleaned = remove_file_attributes_from_object_filter(
      cls.attributes_values_db_initial.copy()
    )
    cls.attributes_values_db_updated = {
      'motiv': motiv2
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'haltestellenkataster_haltestelle': str(haltestelle.pk),
      'motiv': str(motiv3.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_valid.jpg'
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'haltestellenkataster_haltestelle': str(haltestelle.pk),
      'motiv': str(motiv4.pk),
      'aufnahmedatum': VALID_DATE,
      'dateiname_original': 'image_valid.jpg'
    }
    cls.attributes_values_view_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)
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
      True
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
      self.attributes_values_db_initial_cleaned,
      302,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_view_deleteimmediately(self):
    self.generic_delete_view_test(
      True,
      self.model,
      self.attributes_values_db_initial_cleaned,
      204,
      'text/html; charset=utf-8'
    )
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))


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
    normaltarif_parkdauer_min_einheit = Zeiteinheiten.objects.create(
      zeiteinheit='Zeiteinheit1'
    )
    normaltarif_parkdauer_max_einheit = Zeiteinheiten.objects.create(
      zeiteinheit='Zeiteinheit2'
    )
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'zeiten': 'Bewirtschaftungszeiten1',
      'normaltarif_parkdauer_min': 1,
      'normaltarif_parkdauer_min_einheit': normaltarif_parkdauer_min_einheit,
      'normaltarif_parkdauer_max': 2,
      'normaltarif_parkdauer_max_einheit': normaltarif_parkdauer_max_einheit,
      'zugelassene_muenzen': 'zugelassene Münzen 1'
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'zeiten': 'Bewirtschaftungszeiten3',
      'normaltarif_parkdauer_min': 1,
      'normaltarif_parkdauer_min_einheit': str(normaltarif_parkdauer_min_einheit.pk),
      'normaltarif_parkdauer_max': 2,
      'normaltarif_parkdauer_max_einheit': str(normaltarif_parkdauer_max_einheit.pk),
      'zugelassene_muenzen': 'zugelassene Münzen 2'
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'zeiten': 'Bewirtschaftungszeiten4',
      'normaltarif_parkdauer_min': 1,
      'normaltarif_parkdauer_min_einheit': str(normaltarif_parkdauer_min_einheit.pk),
      'normaltarif_parkdauer_max': 2,
      'normaltarif_parkdauer_max_einheit': str(normaltarif_parkdauer_max_einheit.pk),
      'zugelassene_muenzen': 'zugelassene Münzen 3'
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
    normaltarif_parkdauer_min_einheit = Zeiteinheiten.objects.create(
      zeiteinheit='Zeiteinheit1'
    )
    normaltarif_parkdauer_max_einheit = Zeiteinheiten.objects.create(
      zeiteinheit='Zeiteinheit2'
    )
    tarif = Parkscheinautomaten_Tarife.objects.create(
      bezeichnung='Bezeichnung',
      zeiten='Bewirtschaftungszeiten',
      normaltarif_parkdauer_min=1,
      normaltarif_parkdauer_min_einheit=normaltarif_parkdauer_min_einheit,
      normaltarif_parkdauer_max=2,
      normaltarif_parkdauer_max_einheit=normaltarif_parkdauer_max_einheit,
      zugelassene_muenzen='zugelassene Münzen'
    )
    zone = Zonen_Parkscheinautomaten.objects.create(
      zone='A'
    )
    e_anschluss = E_Anschluesse_Parkscheinautomaten.objects.create(
      e_anschluss='E-Anschluss'
    )
    cls.attributes_values_db_initial = {
      'parkscheinautomaten_tarif': tarif,
      'nummer': 1,
      'bezeichnung': 'Bezeichnung1',
      'zone': zone,
      'handyparkzone': 456789,
      'geraetenummer': '34_56789',
      'e_anschluss': e_anschluss,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'parkscheinautomaten_tarif': str(tarif.pk),
      'nummer': 3,
      'bezeichnung': 'Bezeichnung3',
      'zone': str(zone.pk),
      'handyparkzone': 456789,
      'geraetenummer': '34_56789',
      'e_anschluss': str(e_anschluss.pk),
      'geometrie': VALID_POINT_VIEW
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
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
    self.generic_is_complexmodel_test(self.model)

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
    masttyp = Masttypen_RSAG.objects.create(
      typ='Typ',
      erlaeuterung='Erläuterung'
    )
    cls.attributes_values_db_initial = {
      'mastnummer': 'Mastnummer1',
      'masttyp': masttyp,
      'geometrie': VALID_POINT_DB
    }
    cls.attributes_values_db_updated = {
      'mastnummer': 'Mastnummer2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'mastnummer': 'Mastnummer3',
      'masttyp': str(masttyp.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'mastnummer': 'Mastnummer4',
      'masttyp': str(masttyp.pk),
      'geometrie': VALID_POINT_VIEW
    }
    cls.attributes_values_view_invalid = {
      'mastnummer': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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


class RSAGLeitungenTest(DefaultComplexModelTestCase):
  """
  RSAG:
  Oberleitungen
  """

  model = RSAG_Leitungen
  attributes_values_db_initial = {
    'aktiv': True,
    'geometrie': VALID_LINE_DB
  }
  attributes_values_db_updated = {
    'aktiv': False
  }
  attributes_values_view_initial = {
    'aktiv': True,
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_updated = {
    'aktiv': False,
    'geometrie': VALID_LINE_VIEW
  }
  attributes_values_view_invalid = {
  }

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
    masttyp = Masttypen_RSAG.objects.create(
      typ='Typ',
      erlaeuterung='Erläuterung'
    )
    mast = RSAG_Masten.objects.create(
      mastnummer='Mastnummer',
      masttyp=masttyp,
      geometrie=VALID_POINT_DB
    )
    cls.attributes_values_db_initial = {
      'mast': mast,
      'quelle': 'Quelle1',
      'geometrie': VALID_LINE_DB
    }
    cls.attributes_values_db_updated = {
      'quelle': 'Quelle2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'mast': str(mast.pk),
      'quelle': 'Quelle3',
      'geometrie': VALID_LINE_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'mast': str(mast.pk),
      'quelle': 'Quelle4',
      'geometrie': VALID_LINE_VIEW
    }
    cls.attributes_values_view_invalid = {
      'quelle': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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


class RSAGSpanndraehteTest(GenericRSAGTestCase):
  """
  RSAG:
  Spanndrähte
  """

  model = RSAG_Spanndraehte

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
    vorgangsart = Vorgangsarten_UVP_Vorhaben.objects.create(
      vorgangsart='Vorgangsart'
    )
    genehmigungsbehoerde = Genehmigungsbehoerden_UVP_Vorhaben.objects.create(
      genehmigungsbehoerde='Genehmigungsbehörde'
    )
    rechtsgrundlage = Rechtsgrundlagen_UVP_Vorhaben.objects.create(
      rechtsgrundlage='Rechtsgrundlage'
    )
    typ = Typen_UVP_Vorhaben.objects.create(
      typ='Typ'
    )
    cls.attributes_values_db_initial = {
      'bezeichnung': 'Bezeichnung1',
      'vorgangsart': vorgangsart,
      'genehmigungsbehoerde': genehmigungsbehoerde,
      'datum_posteingang_genehmigungsbehoerde': VALID_DATE,
      'rechtsgrundlage': rechtsgrundlage,
      'typ': typ,
      'geometrie': VALID_POLYGON_DB
    }
    cls.attributes_values_db_updated = {
      'bezeichnung': 'Bezeichnung2'
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung3',
      'vorgangsart': str(vorgangsart.pk),
      'genehmigungsbehoerde': str(genehmigungsbehoerde.pk),
      'datum_posteingang_genehmigungsbehoerde': VALID_DATE,
      'rechtsgrundlage': str(rechtsgrundlage.pk),
      'typ': str(typ.pk),
      'geometrie': VALID_POLYGON_VIEW
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'bezeichnung': 'Bezeichnung4',
      'vorgangsart': str(vorgangsart.pk),
      'genehmigungsbehoerde': str(genehmigungsbehoerde.pk),
      'datum_posteingang_genehmigungsbehoerde': VALID_DATE,
      'rechtsgrundlage': str(rechtsgrundlage.pk),
      'typ': str(typ.pk),
      'geometrie': VALID_POLYGON_VIEW
    }
    cls.attributes_values_view_invalid = {
      'bezeichnung': INVALID_STRING
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
    vorgangsart = Vorgangsarten_UVP_Vorhaben.objects.create(
      vorgangsart='Vorgangsart'
    )
    genehmigungsbehoerde = Genehmigungsbehoerden_UVP_Vorhaben.objects.create(
      genehmigungsbehoerde='Genehmigungsbehörde'
    )
    rechtsgrundlage = Rechtsgrundlagen_UVP_Vorhaben.objects.create(
      rechtsgrundlage='Rechtsgrundlage'
    )
    typ = Typen_UVP_Vorhaben.objects.create(
      typ='Typ'
    )
    uvp_vorhaben = UVP_Vorhaben.objects.create(
      bezeichnung='Bezeichnung',
      vorgangsart=vorgangsart,
      genehmigungsbehoerde=genehmigungsbehoerde,
      datum_posteingang_genehmigungsbehoerde=VALID_DATE,
      rechtsgrundlage=rechtsgrundlage,
      typ=typ,
      geometrie=VALID_POLYGON_DB
    )
    art = Arten_UVP_Vorpruefungen.objects.create(
      art='Art'
    )
    ergebnis1 = Ergebnisse_UVP_Vorpruefungen.objects.create(
      ergebnis='Ergebnis1'
    )
    ergebnis2 = Ergebnisse_UVP_Vorpruefungen.objects.create(
      ergebnis='Ergebnis2'
    )
    ergebnis3 = Ergebnisse_UVP_Vorpruefungen.objects.create(
      ergebnis='Ergebnis3'
    )
    ergebnis4 = Ergebnisse_UVP_Vorpruefungen.objects.create(
      ergebnis='Ergebnis4'
    )
    cls.attributes_values_db_initial = {
      'uvp_vorhaben': uvp_vorhaben,
      'art': art,
      'datum_posteingang': VALID_DATE,
      'datum': VALID_DATE,
      'ergebnis': ergebnis1
    }
    cls.attributes_values_db_updated = {
      'ergebnis': ergebnis2
    }
    cls.attributes_values_view_initial = {
      'aktiv': True,
      'uvp_vorhaben': str(uvp_vorhaben.pk),
      'art': str(art.pk),
      'datum_posteingang': VALID_DATE,
      'datum': VALID_DATE,
      'ergebnis': str(ergebnis3.pk)
    }
    cls.attributes_values_view_updated = {
      'aktiv': True,
      'uvp_vorhaben': str(uvp_vorhaben.pk),
      'art': str(art.pk),
      'datum_posteingang': VALID_DATE,
      'datum': VALID_DATE,
      'ergebnis': str(ergebnis4.pk)
    }
    cls.attributes_values_view_invalid = {
    }
    cls.test_object = cls.model.objects.create(**cls.attributes_values_db_initial)
    cls.test_subset = create_test_subset(cls.model, cls.test_object)

  def setUp(self):
    self.init()

  def test_is_complexmodel(self):
    self.generic_is_complexmodel_test(self.model)

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
