from django.conf import settings
from pathlib import Path, PurePath
from PIL import ExifTags, Image

from datenmanagement.utils import get_path


def delete_duplicate_photos_with_other_suffixes(path):
  """
  deletes duplicate photo files that have the same path as the passed photo file path
  but have a different file extension

  :param path: photo file path
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
  deletes PDF file connected with passed object of sending model

  :param sender: sending model
  :param instance: object
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
  deletes photo file connected with passed object of sending model
  (and the related thumbnail photo file as well, if existing)
  if photo is mandatory

  :param sender: sending model
  :param instance: object
  :param **kwargs
  """
  if hasattr(instance, 'foto') and instance.foto:
    if sender.BasemodelMeta.thumbs:
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
  deletes photo file connected with passed object of sending model
  (and the related thumbnail photo file as well, if existing)
  if photo is not mandatory

  :param sender: sending model
  :param instance: object
  :param created: object created?
  :param **kwargs
  """
  pre_save_instance = instance._pre_save_instance
  # execute only if a photo file previously existed, if no more photo file was transferred
  # and if object was not created but updated
  if pre_save_instance.foto and not instance.foto and not created:
    path = get_path(pre_save_instance.foto.url)
    if sender.BasemodelMeta.thumbs:
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


def photo_post_processing(sender, instance, **kwargs):
  """
  handles photo file connected with passed object of sending model
  after passed object is finally saved

  :param sender: sending model
  :param instance: object
  :param **kwargs
  """
  if instance.foto:
    if settings.MEDIA_ROOT and settings.MEDIA_URL:
      path = Path(settings.MEDIA_ROOT) / instance.foto.url[len(settings.MEDIA_URL):]
    else:
      path = Path(settings.BASE_DIR) / instance.foto.url
    rotate_image(path)
    # delete duplicate photo files that have the same path as the current photo file
    # but have a different file extension
    # (and the related thumbnail photo files as well, if existing)
    delete_duplicate_photos_with_other_suffixes(path)
    if sender.BasemodelMeta.thumbs:
      thumb_path = Path(PurePath(path).parent / 'thumbs')
      if not thumb_path.exists():
        if path.exists():
          Path.mkdir(thumb_path)
      thumb_path = thumb_path / PurePath(path).name
      thumb_image(path, thumb_path)
      delete_duplicate_photos_with_other_suffixes(thumb_path)


def rotate_image(path):
  """
  rotates photo file with passed photo file path

  :param path: photo file path
  """
  try:
    if path.exists():
      image = Image.open(path)
      orientation = None
      for orientation in list(ExifTags.TAGS.keys()):
        if ExifTags.TAGS[orientation] == 'Orientation':
          break
      exif = dict(list(image.getexif().items()))
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


def set_pre_save_instance(sender, instance, **kwargs):
  """
  sets passed object of sending model before final saving

  :param sender: sending model
  :param instance: object
  :param **kwargs
  """
  try:
    instance._pre_save_instance = sender.objects.get(pk=instance.uuid)
  except sender.DoesNotExist:
    instance._pre_save_instance = instance


def thumb_image(path, thumb_path):
  """
  creates thumbnail photo file with passed thumbnail photo file path
  related to photo file with passed photo file path

  :param path: photo file path
  :param thumb_path: thumbnail photo file path
  """
  try:
    if path.exists():
      image = Image.open(path)
      image.thumbnail((70, 70), Image.Resampling.LANCZOS)
      image.save(thumb_path, optimize=True, quality=20)
      image.close()
  except (AttributeError, KeyError, IndexError):
    pass
