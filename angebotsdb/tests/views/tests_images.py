from pathlib import Path
from unittest.mock import patch

from django.conf import settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.urls import reverse

from angebotsdb.models.base import Law, Provider, Tag, TargetGroup, Topic, UserProfile
from angebotsdb.models.services import ChildrenYouthAndFamilyService, ServiceImage

from datenmanagement.tests.constants_vars import VALID_IMAGE_FILE

from ..abstract import FormViewTestCase, MockResponse
from ..constant_vars import (
  USERNAME,
  USERNAME_PROVIDER,
  USERNAME_REVIEWER,
  VALID_DATE_A,
  VALID_GEOJSON_4326,
  VALID_POINT_DB,
  VALID_STRING_A,
  VALID_STRING_B,
  VALID_ZIP,
)
from ..functions import login_as_admin, login_as_provider
from .tests_services import PYGEOAPI_PATCH, _base_service_form_data

TEST_MEDIA_DIR = Path(__file__).resolve().parent / 'temp'


def remove_uploaded_test_files(path):
  """
  löscht das Verzeichnis mit den hochgeladenen Testdateien

  :param path: Pfad des Verzeichnisses mit den hochgeladenen Testdateien
  """
  from shutil import rmtree

  if path.exists():
    rmtree(path)


def create_test_image(filename):
  """
  erzeugt eine SimpleUploadedFile mit gültigem Bildinhalt

  :param filename: Dateiname für den Upload
  :return: SimpleUploadedFile-Instanz
  """
  return SimpleUploadedFile(
    filename,
    Path(VALID_IMAGE_FILE).read_bytes(),
    content_type='image/jpeg',
  )


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class ServiceImageFormFlowTest(FormViewTestCase):
  """
  Testklasse für den Bild-Flow im Angebotsformular:

  - Uploads eines weiteren Speichervorgangs dürfen zuvor gespeicherte Bilder
    nicht entfernen (additiver Upload).
  - AJAX-Lösch-Endpoint entfernt Zeile und Datei, behält aber geteilte
    Dateipfade (Draft-Copies) bei.
  """

  model = ChildrenYouthAndFamilyService
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.admin_user = User.objects.create_user(username=USERNAME)
    cls.provider_user = User.objects.create_user(username=USERNAME_PROVIDER)
    cls.reviewer_user = User.objects.create_user(username=USERNAME_REVIEWER)
    cls.test_provider = Provider.objects.create(name=VALID_STRING_A)
    cls.test_topic = Topic.objects.create(name=VALID_STRING_A)
    cls.test_law = Law.objects.create(law_book='SGB VIII', paragraph='8a')
    cls.test_tag = Tag.objects.create(name=VALID_STRING_A)
    cls.test_target_group = TargetGroup.objects.create(name=VALID_STRING_A)
    service = ChildrenYouthAndFamilyService.objects.create(
      name=VALID_STRING_A,
      description='Testbeschreibung',
      street='Teststraße 1',
      zip=VALID_ZIP,
      city='Rostock',
      email='test@test.de',
      host=cls.test_provider,
      expiry_date=VALID_DATE_A,
      application_needed=False,
      handicap_accessible=False,
      phone='0381 123456',
      costs=0.0,
      geometry=VALID_POINT_DB,
      status='draft',
    )
    service.topic.set([cls.test_topic])
    service.legal_basis.set([cls.test_law])
    service.tags.set([cls.test_tag])
    service.target_group.set([cls.test_target_group])
    cls.test_object = service

  def setUp(self):
    self.init()
    # je Test zwei gespeicherte Bilder anlegen (Dateien landen im Test-MEDIA_ROOT)
    self.initial_images = [
      ServiceImage.objects.create(
        service_type=self._service_type(),
        service_id=self.test_object.pk,
        image=create_test_image(f'bild{index}.jpg'),
      )
      for index in (1, 2)
    ]

  def tearDown(self):
    remove_uploaded_test_files(TEST_MEDIA_DIR)

  def _service_type(self):
    return self.test_object.__class__.__name__.lower()

  def _image_file_exists(self, image):
    return (Path(settings.MEDIA_ROOT) / image.image.name).exists()

  def _valid_form_data_with_new_image(self):
    data = _base_service_form_data(
      self.test_topic.pk,
      self.test_law.pk,
      self.test_tag.pk,
      target_group_pk=self.test_target_group.pk,
    )
    data['images'] = create_test_image('neu.jpg')
    return data

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_update_with_new_upload_keeps_existing_images(self, mock_get):
    """
    Update-POST mit einem neuen Bild: zuvor gespeicherte Bilder (Zeilen und
    Dateien) bleiben erhalten, das neue Bild kommt hinzu.
    """
    login_as_provider(self)
    response = self.client.post(
      reverse(
        'angebotsdb:childrenyouthandfamilyservice_update',
        kwargs={'pk': self.test_object.pk},
      ),
      self._valid_form_data_with_new_image(),
    )
    self.assertEqual(response.status_code, 302)
    images = ServiceImage.objects.filter(
      service_type=self._service_type(),
      service_id=self.test_object.pk,
    )
    self.assertEqual(images.count(), 3)
    for image in self.initial_images:
      self.assertTrue(self._image_file_exists(image))
    new_image = images.exclude(pk__in=[i.pk for i in self.initial_images]).first()
    self.assertIsNotNone(new_image)
    self.assertTrue(self._image_file_exists(new_image))

  @patch(PYGEOAPI_PATCH, return_value=MockResponse())
  def test_update_without_upload_keeps_existing_images(self, mock_get):
    """
    Update-POST ohne Bild-Upload: gespeicherte Bilder bleiben unverändert.
    """
    login_as_provider(self)
    data = _base_service_form_data(
      self.test_topic.pk,
      self.test_law.pk,
      self.test_tag.pk,
      target_group_pk=self.test_target_group.pk,
    )
    response = self.client.post(
      reverse(
        'angebotsdb:childrenyouthandfamilyservice_update',
        kwargs={'pk': self.test_object.pk},
      ),
      data,
    )
    self.assertEqual(response.status_code, 302)
    self.assertEqual(
      ServiceImage.objects.filter(
        service_type=self._service_type(),
        service_id=self.test_object.pk,
      ).count(),
      2,
    )

  def test_service_image_ajax_delete_success(self):
    """
    AJAX-Lösch-Endpoint als berechtigter Träger-Nutzer: Zeile und Datei
    werden entfernt.
    """
    login_as_provider(self)
    image = self.initial_images[0]
    response = self.client.post(
      reverse('angebotsdb:service_image_delete', kwargs={'pk': image.pk})
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json()['success'], True)
    self.assertFalse(
      ServiceImage.objects.filter(service_type=self._service_type(), pk=image.pk).exists()
    )
    self.assertFalse(self._image_file_exists(image))
    # zweites Bild unangetastet
    self.assertTrue(
      ServiceImage.objects.filter(
        service_type=self._service_type(), pk=self.initial_images[1].pk
      ).exists()
    )

  def test_service_image_ajax_delete_shared_file_kept(self):
    """
    Wird ein Dateipfad von einer zweiten ServiceImage-Zeile geteilt
    (Muster Draft-Copy), bleibt die Datei beim Löschen der ersten Zeile
    erhalten.
    """
    login_as_provider(self)
    image = self.initial_images[0]
    shared = ServiceImage.objects.create(
      service_type=self._service_type(),
      service_id=self.test_object.pk + 1,
      image=image.image,
    )
    response = self.client.post(
      reverse('angebotsdb:service_image_delete', kwargs={'pk': image.pk})
    )
    self.assertEqual(response.status_code, 200)
    self.assertEqual(response.json()['success'], True)
    self.assertFalse(ServiceImage.objects.filter(pk=image.pk).exists())
    self.assertTrue(ServiceImage.objects.filter(pk=shared.pk).exists())
    self.assertTrue(self._image_file_exists(image))

  def test_service_image_ajax_delete_forbidden_for_other_provider(self):
    """
    Träger-Nutzer eines fremden Trägers erhalten 403, Bild bleibt bestehen.
    """
    other_user = User.objects.create_user(username='other_provider_user')
    other_provider = Provider.objects.create(name=VALID_STRING_B)
    UserProfile.objects.create(user_id=other_user.id, provider=other_provider)
    self.users_group.user_set.add(other_user)
    self.client.force_login(other_user)
    image = self.initial_images[0]
    response = self.client.post(
      reverse('angebotsdb:service_image_delete', kwargs={'pk': image.pk})
    )
    self.assertEqual(response.status_code, 403)
    self.assertEqual(response.json()['success'], False)
    self.assertTrue(ServiceImage.objects.filter(pk=image.pk).exists())

  def test_service_image_ajax_delete_requires_login(self):
    """
    Anonymer Aufruf des Lösch-Endpoints wird auf die Anmeldung umgeleitet.
    """
    image = self.initial_images[0]
    response = self.client.post(
      reverse('angebotsdb:service_image_delete', kwargs={'pk': image.pk})
    )
    self.assertEqual(response.status_code, 302)
    self.assertTrue(ServiceImage.objects.filter(pk=image.pk).exists())


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class ProviderLogoClearTest(FormViewTestCase):
  """
  Testklasse für das Löschen des Träger-Logos über die
  logo-clear-Mechanik des ClearableFileInput.
  """

  model = Provider
  create_test_object_in_classmethod = False

  @classmethod
  def setUpTestData(cls):
    cls.admin_user = User.objects.create_user(username=USERNAME)
    cls.provider_user = User.objects.create_user(username=USERNAME_PROVIDER)
    cls.reviewer_user = User.objects.create_user(username=USERNAME_REVIEWER)
    cls.test_object = Provider.objects.create(
      name=VALID_STRING_A,
      logo=create_test_image('logo.png'),
    )

  def setUp(self):
    self.init()

  def tearDown(self):
    remove_uploaded_test_files(TEST_MEDIA_DIR)

  def test_provider_logo_clear_via_form(self):
    """
    Update-POST mit logo-clear=on: Logo-Feld wird geleert und die Datei vom
    Dateisystem entfernt.
    """
    logo_name = self.test_object.logo.name
    login_as_admin(self)
    response = self.client.post(
      reverse('angebotsdb:provider_update', kwargs={'pk': self.test_object.pk}),
      {
        'name': VALID_STRING_B,
        'street': 'Teststraße 1',
        'zip': VALID_ZIP,
        'city': 'Rostock',
        'geometry': VALID_GEOJSON_4326,
        'logo-clear': 'on',
      },
    )
    self.assertEqual(response.status_code, 302)
    self.test_object.refresh_from_db()
    self.assertFalse(self.test_object.logo)
    self.assertFalse((Path(settings.MEDIA_ROOT) / logo_name).exists())

  def test_provider_logo_upload_replaces_file(self):
    """
    Update-POST mit neuem Logo: altes Logo-Feld wird ersetzt und die alte
    Datei entfernt, neuer Upload erhält UUID-Dateinamen.
    """
    old_logo_name = self.test_object.logo.name
    login_as_admin(self)
    response = self.client.post(
      reverse('angebotsdb:provider_update', kwargs={'pk': self.test_object.pk}),
      {
        'name': VALID_STRING_B,
        'street': 'Teststraße 1',
        'zip': VALID_ZIP,
        'city': 'Rostock',
        'geometry': VALID_GEOJSON_4326,
        'logo': create_test_image('logo_neu.png'),
      },
    )
    self.assertEqual(response.status_code, 302)
    self.test_object.refresh_from_db()
    self.assertTrue(self.test_object.logo)
    self.assertNotEqual(self.test_object.logo.name, old_logo_name)
    self.assertFalse((Path(settings.MEDIA_ROOT) / old_logo_name).exists())
    self.assertTrue((Path(settings.MEDIA_ROOT) / self.test_object.logo.name).exists())
    self.assertEqual(self.test_object.dateiname_original, 'logo_neu.png')
