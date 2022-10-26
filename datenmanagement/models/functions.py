import os
import re
import uuid

from datetime import date
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.db import connection
from guardian.shortcuts import assign_perm, remove_perm
from PIL import Image, ExifTags


def assign_permissions(sender, instance, created, **kwargs):
  """
  weist Rechte am übergebenenen Datenobjekts zu

  :param sender: Datenmodell
  :param instance: Datenobjekt
  :param created: Datenobjekt neu hinzugefügt?
  :param **kwargs
  """
  model_name = instance.__class__.__name__.lower()
  user = getattr(instance, 'current_authenticated_user', None)
  if created:
    assign_perm('datenmanagement.change_' + model_name, user, instance)
    assign_perm('datenmanagement.delete_' + model_name, user, instance)
    if (hasattr(instance.__class__._meta, 'admin_group') and
        Group.objects.filter(
          name=instance.__class__._meta.admin_group
        ).exists()):
      group = Group.objects.filter(
        name=instance.__class__._meta.admin_group)
      assign_perm(
        'datenmanagement.change_' +
        model_name,
        group,
        instance)
      assign_perm(
        'datenmanagement.delete_' +
        model_name,
        group,
        instance)
    else:
      for group in Group.objects.all():
        if group.permissions.filter(codename='change_' + model_name):
          assign_perm(
            'datenmanagement.change_' +
            model_name,
            group,
            instance)
        if group.permissions.filter(codename='delete_' + model_name):
          assign_perm(
            'datenmanagement.delete_' +
            model_name,
            group,
            instance)
  elif hasattr(
      instance.__class__._meta,
      'group_with_users_for_choice_field'
  ) and Group.objects.filter(
    name=instance.__class__._meta.group_with_users_for_choice_field
  ).exists():
    mail = instance.ansprechpartner.split()[-1]
    mail = re.sub(r'\(', '', re.sub(r'\)', '', mail))
    if User.objects.filter(email__iexact=mail).exists():
      user = User.objects.get(email__iexact=mail)
      assign_perm('datenmanagement.change_' + model_name, user, instance)
      assign_perm('datenmanagement.delete_' + model_name, user, instance)


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
  filename = os.path.basename(path)
  ext = filename.split('.')[-1]
  filename_without_ext = os.path.splitext(filename)[0]
  for file in os.listdir(os.path.dirname(path)):
    if (os.path.splitext(file)[0] == filename_without_ext and
        file.split('.')[-1] != ext):
      os.remove(os.path.dirname(path) + '/' + file)


def delete_pdf(sender, instance, **kwargs):
  """
  löscht PDF zu übergebenenem Datenobjekt

  :param sender: Datenmodell
  :param instance: Datenobjekt
  :param **kwargs
  """
  if hasattr(instance, 'pdf') and instance.pdf:
    instance.pdf.delete(False)
  elif hasattr(instance, 'dokument') and instance.dokument:
    instance.dokument.delete(False)


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
      thumb = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      try:
        os.remove(thumb)
      except OSError:
        pass
    instance.foto.delete(False)


def delete_photo_after_emptied(sender, instance, created, **kwargs):
  """
  löscht Foto zu übergebenenem Datenobjekt und, falls vorhanden, auch das entsprechende Thumbnail;
  greift bei Datenmodellen, bei denen das Foto optional ist

  :param sender: Datenmodell
  :param instance: Datenobjekt
  :param created: Datenobjekt neu hinzugefügt?
  :param **kwargs
  """
  if not instance.foto and not created:
    pre_save_instance = instance._pre_save_instance
    path = get_path(pre_save_instance.foto.url)
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs:
      thumb = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
      try:
        os.remove(thumb)
      except OSError:
        pass
    try:
      os.remove(path)
    except OSError:
      pass


def get_path(url):
  """
  löscht Pfad zur übergebenenen URL zurück

  :param url: URL
  :return: Pfad zur übergebenenen URL
  """
  if settings.MEDIA_ROOT and settings.MEDIA_URL:
    path = settings.MEDIA_ROOT + '/' + \
           url[len(settings.MEDIA_URL):]
  else:
    base_dir = os.path.dirname(
      os.path.dirname(os.path.abspath(__file__)))
    path = base_dir + url
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
      filename = '{0}.{1}'.format(str(uuid.uuid4()), ext.lower())
    return os.path.join(path, filename)

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
      path = settings.MEDIA_ROOT + '/' + \
             instance.foto.url[len(settings.MEDIA_URL):]
    else:
      base_dir = os.path.dirname(
        os.path.dirname(
          os.path.abspath(__file__)))
      path = base_dir + instance.foto.url
    rotate_image(path)
    # falls Foto(s) mit derselben UUID, aber unterschiedlichem Dateityp (also Suffix), vorhanden:
    # diese(s) löschen und natürlich auch das/die entsprechende(n) Thumbnail(s)
    delete_duplicate_photos_with_other_suffixes(path)
    if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs:
      thumb_path = os.path.dirname(path) + '/thumbs'
      if not os.path.exists(thumb_path):
        os.mkdir(thumb_path)
      thumb_path = os.path.dirname(
        path) + '/thumbs/' + os.path.basename(path)
      thumb_image(path, thumb_path)
      delete_duplicate_photos_with_other_suffixes(thumb_path)


def remove_permissions(sender, instance, **kwargs):
  """
  entfernt Rechte am übergebenenen Datenobjekt

  :param sender: Datenmodell
  :param instance: Datenobjekt
  :param **kwargs
  """
  model_name = instance.__class__.__name__.lower()
  for user in User.objects.all():
    remove_perm('datenmanagement.change_' + model_name, user, instance)
    remove_perm('datenmanagement.delete_' + model_name, user, instance)
  for group in Group.objects.all():
    remove_perm('datenmanagement.change_' + model_name, group, instance)
    remove_perm('datenmanagement.delete_' + model_name, group, instance)


def rotate_image(path):
  """
  dreht Foto unter dem übergebenenen Pfad

  :param path: Pfad
  """
  try:
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


def sequence_id(sequence_name):
  with connection.cursor() as cursor:
    cursor.execute("""SELECT nextval('""" + sequence_name + """')""")
    return cursor.fetchone()[0]


def thumb_image(path, thumb_path):
  """
  erstellt Thumbnail unter dem übergebenenem Thumbnail-Pfad zum Foto unter dem übergebenenen Pfad

  :param path: Pfad
  :param thumb_path: Thumbnail-Pfad
  """
  try:
    image = Image.open(path)
    image.thumbnail((70, 70), Image.ANTIALIAS)
    image.save(thumb_path, optimize=True, quality=20)
    image.close()
  except (AttributeError, KeyError, IndexError):
    pass
