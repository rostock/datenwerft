from datetime import date
from django.conf import settings
from pathlib import Path, PurePath
from PIL import ExifTags, Image
from uuid import uuid4


def current_year():
  """
  liefert aktuelles Jahr zurück

  :return: aktuelles Jahr
  """
  return int(date.today().year)


def delete_duplicate_photos_with_other_suffixes(path):
  """
  löscht Duplikate von Fotos, die zwar denselben Pfad aufweisen wie der übergebene Pfad,
  die jedoch eine andere Dateiendung aufweisen

  :param path: Pfad
  """
  filename = PurePath(path).name
  pathname = Path(PurePath(path).parent)
  filename_ext = PurePath(filename).suffix
  filename_without_ext = PurePath(filename).stem
  if pathname.exists():
    for file in pathname.iterdir():
      if PurePath(file).stem == filename_without_ext and PurePath(file).suffix != filename_ext:
        (pathname / file).unlink()


def delete_pdf(sender, instance, **kwargs):
  """
  löscht PDF zu übergebenenem Datenobjekt

  :param sender: Datenmodell
  :param instance: Datenobjekt
  :param **kwargs
  """
  if hasattr(instance, 'pdf') and instance.pdf:
    instance.pdf.delete()
    instance.delete()
  elif hasattr(instance, 'dokument') and instance.dokument:
    instance.dokument.delete()
    instance.delete()


def delete_photo(sender, instance, **kwargs):
  """
  löscht Foto zu übergebenenem Datenobjekt und, falls vorhanden, auch das entsprechende Thumbnail

  :param sender: Datenmodell
  :param instance: Datenobjekt
  :param **kwargs
  """
  if hasattr(instance, 'foto') and instance.foto:
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs:
      path = get_path(instance.foto.url)
      thumb = Path(PurePath(path).parent / 'thumbs' / PurePath(path).name)
      try:
        delete_duplicate_photos_with_other_suffixes(thumb)
        thumb.unlink()
      except OSError:
        pass
      delete_duplicate_photos_with_other_suffixes(path)
    instance.foto.delete()
    instance.delete()


def delete_photo_after_emptied(sender, instance, created, **kwargs):
  """
  löscht Foto zu übergebenenem Datenobjekt und, falls vorhanden, auch das entsprechende Thumbnail;
  greift bei Datenmodellen, bei denen das Foto optional ist

  :param sender: Datenmodell
  :param instance: Datenobjekt
  :param created: Datenobjekt neu hinzugefügt?
  :param **kwargs
  """
  pre_save_instance = instance._pre_save_instance
  # nur ausführen, wenn zuvor ein Foto existiert hat, wenn nun kein Foto mehr übergeben wurde
  # und wenn Datenobjekt nicht neu hinzugefügt, sondern aktualisiert wurde
  if pre_save_instance.foto and not instance.foto and not created:
    path = get_path(pre_save_instance.foto.url)
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs:
      thumb = Path(PurePath(path).parent / 'thumbs' / PurePath(path).name)
      try:
        delete_duplicate_photos_with_other_suffixes(thumb)
        thumb.unlink()
      except OSError:
        pass
    try:
      delete_duplicate_photos_with_other_suffixes(path)
      path.unlink()
    except OSError:
      pass


def get_path(url):
  """
  gibt Pfad zur übergebenenen URL zurück

  :param url: URL
  :return: Pfad zur übergebenenen URL
  """
  if settings.MEDIA_ROOT and settings.MEDIA_URL:
    path = Path(settings.MEDIA_ROOT) / url[len(settings.MEDIA_URL):]
  else:
    path = Path(settings.BASE_DIR) / url
  return path


def get_pre_save_instance(sender, instance, **kwargs):
  """
  setzt übergebenenes Datenobjekt vor dem finalen Speichern

  :param sender: Datenmodell
  :param instance: Datenobjekt
  :param **kwargs
  """
  try:
    instance._pre_save_instance = sender.objects.get(pk=instance.uuid)
  except sender.DoesNotExist:
    instance._pre_save_instance = instance


def path_and_rename(path):
  """
  bereinigt übergebenenen Pfad und gibt diesen zurück

  :param path: Pfad
  :return: bereinigter, übergebenener Pfad
  """
  def wrapper(instance, filename):
    """
    setzt Pfad anhand des übergebenen Datenobjekts sowie des übergebenen Dateinamens
    und gibt den gesetzten Pfad zurück

    :param instance: Datenobjekt
    :param filename: Dateiname
    :return: anhand des übergebenen Datenobjekts und des übergebenen Dateinamens gesetzter Pfad
    """
    if hasattr(instance, 'dateiname_original'):
      instance.dateiname_original = filename
    ext = filename.split('.')[-1]
    if hasattr(instance, 'uuid'):
      filename = '{0}.{1}'.format(str(instance.uuid), ext.lower())
    else:
      filename = '{0}.{1}'.format(str(uuid4()), ext.lower())
    return Path(path) / filename

  return wrapper


def photo_post_processing(sender, instance, **kwargs):
  """
  behandelt Foto des übergebenenen Datenobjekts nach dem finalen Speichern des Datenobjekts

  :param sender: Datenmodell
  :param instance: Datenobjekt
  :param **kwargs
  """
  if instance.foto:
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = Path(settings.MEDIA_ROOT) / instance.foto.url[len(settings.MEDIA_URL):]
    else:
      path = Path(settings.BASE_DIR) / instance.foto.url
    rotate_image(path)
    # falls Foto(s) mit derselben UUID, aber unterschiedlichem Dateityp (also Suffix), vorhanden:
    # diese(s) löschen und natürlich auch das/die entsprechende(n) Thumbnail(s)
    delete_duplicate_photos_with_other_suffixes(path)
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs:
      thumb_path = Path(PurePath(path).parent / 'thumbs')
      if not thumb_path.exists():
        if path.exists():
          Path.mkdir(thumb_path)
      thumb_path = thumb_path / PurePath(path).name
      thumb_image(path, thumb_path)
      delete_duplicate_photos_with_other_suffixes(thumb_path)


def rotate_image(path):
  """
  dreht Foto unter dem übergebenenen Pfad

  :param path: Pfad
  """
  try:
    if path.exists():
      image = Image.open(path)
      orientation = None
      for orientation in list(ExifTags.TAGS.keys()):
        if ExifTags.TAGS[orientation] == 'Orientation':
          break
      exif = dict(list(image._getexif().items()))
      if exif[orientation] == 3:
        image = image.rotate(180, expand=True)
      elif exif[orientation] == 6:
        image = image.rotate(270, expand=True)
      elif exif[orientation] == 8:
        image = image.rotate(90, expand=True)
      image.save(path)
      image.close()
  except (AttributeError, KeyError, IndexError):
    pass


def thumb_image(path, thumb_path):
  """
  erstellt Thumbnail unter dem übergebenenem Thumbnail-Pfad zum Foto unter dem übergebenenen Pfad

  :param path: Pfad
  :param thumb_path: Thumbnail-Pfad
  """
  try:
    if path.exists():
      image = Image.open(path)
      image.thumbnail((70, 70), Image.ANTIALIAS)
      image.save(thumb_path, optimize=True, quality=20)
      image.close()
  except (AttributeError, KeyError, IndexError):
    pass
