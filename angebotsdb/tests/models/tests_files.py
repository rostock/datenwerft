from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.conf import settings

from angebotsdb.models.base import Provider
from angebotsdb.models.services import ServiceImage
from datenmanagement.tests.constants_vars import VALID_IMAGE_FILE

from ..abstract import DefaultTestCase

TEST_MEDIA_DIR = Path(__file__).resolve().parent / 'temp'


def remove_uploaded_test_files(path):
  """
  löscht das Verzeichnis mit den hochgeladenen Testdateien

  :param path: Pfad des Verzeichnisses mit den hochgeladenen Testdateien
  """
  from shutil import rmtree

  if path.exists():
    rmtree(path)


@override_settings(MEDIA_ROOT=TEST_MEDIA_DIR)
class UuidUploadTest(DefaultTestCase):
  """
  Testet, dass Bild-Uploads in der AngebotsDB als <uuid>.<ext> abgelegt werden.
  """

  databases = {'default', 'angebotsdb'}

  def setUp(self):
    self.init()

  def tearDown(self):
    remove_uploaded_test_files(Path(settings.MEDIA_ROOT))

  def test_provider_logo_upload_gets_uuid_name(self):
    """
    Prüft, dass ein Provider-Logo unter angebotsdb/hosts/ mit UUID-Basename
    und kleingeschriebener Endung gespeichert wird.
    """
    content = Path(VALID_IMAGE_FILE).read_bytes()
    provider = Provider.objects.create(
      name='TestTräger',
      logo=SimpleUploadedFile('logo.png', content, content_type='image/png'),
    )
    name = provider.logo.name
    self.assertTrue(name.startswith('angebotsdb/hosts/'))
    stem = Path(name).stem
    ext = Path(name).suffix
    self.assertEqual(ext, '.png')
    # UUID-Basename: 36 Zeichen inkl. Bindestriche
    self.assertEqual(len(stem), 36)
    self.assertEqual(stem.count('-'), 4)
    self.assertTrue((Path(settings.MEDIA_ROOT) / name).exists())
    self.assertEqual(provider.dateiname_original, 'logo.png')

  def test_service_image_uploads_with_same_original_name_get_different_paths(self):
    """
    Prüft, dass zwei ServiceImage-Uploads mit identischem Originalnamen
    unterschiedliche Speicherpfade erhalten.
    """
    content = Path(VALID_IMAGE_FILE).read_bytes()
    image1 = ServiceImage.objects.create(
      service_type='childrenyouthandfamilyservice',
      service_id=1,
      image=SimpleUploadedFile('bild.jpg', content, content_type='image/jpeg'),
    )
    image2 = ServiceImage.objects.create(
      service_type='childrenyouthandfamilyservice',
      service_id=1,
      image=SimpleUploadedFile('bild.jpg', content, content_type='image/jpeg'),
    )
    self.assertNotEqual(image1.image.name, image2.image.name)
    self.assertTrue(image1.image.name.startswith('angebotsdb/services/'))
    self.assertTrue(image2.image.name.startswith('angebotsdb/services/'))
    self.assertTrue((Path(settings.MEDIA_ROOT) / image1.image.name).exists())
    self.assertTrue((Path(settings.MEDIA_ROOT) / image2.image.name).exists())
    self.assertEqual(image1.dateiname_original, 'bild.jpg')
    self.assertEqual(image2.dateiname_original, 'bild.jpg')

  def test_upload_extension_is_lowercased(self):
    """
    Prüft, dass die Dateiendung bei Upload kleingeschrieben wird.
    """
    content = Path(VALID_IMAGE_FILE).read_bytes()
    provider = Provider.objects.create(
      name='TestTräger',
      logo=SimpleUploadedFile('logo.JPEG', content, content_type='image/jpeg'),
    )
    self.assertTrue(provider.logo.name.endswith('.jpeg'))
