import os
import re
import uuid

from datetime import date, datetime, timezone
from decimal import *
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.contrib.gis.db import models
from django.db import connection
from django.db.models import options, signals
from guardian.shortcuts import assign_perm, remove_perm
from PIL import Image, ExifTags
from zoneinfo import ZoneInfo



def assign_permissions(sender, instance, created, **kwargs):
    model_name = instance.__class__.__name__.lower()
    user = getattr(instance, 'current_authenticated_user', None)
    if created:
        assign_perm('datenmanagement.change_' + model_name, user, instance)
        assign_perm('datenmanagement.delete_' + model_name, user, instance)
        if hasattr(
                instance.__class__._meta,
                'admin_group') and Group.objects.filter(
            name=instance.__class__._meta.admin_group).exists():
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
    liefert aktuelles Jahr
  
    :return: current year
    :rtype: int
    """
    return int(date.today().year)


def delete_pdf(sender, instance, **kwargs):
    if hasattr(instance, 'pdf') and instance.pdf:
        instance.pdf.delete(False)
    elif hasattr(instance, 'dokument') and instance.dokument:
        instance.dokument.delete(False)


def delete_photo(sender, instance, **kwargs):
    if hasattr(instance, 'foto') and instance.foto:
        if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs:
            if settings.MEDIA_ROOT and settings.MEDIA_URL:
                path = settings.MEDIA_ROOT + '/' + \
                       instance.foto.url[len(settings.MEDIA_URL):]
            else:
                BASE_DIR = os.path.dirname(
                    os.path.dirname(os.path.abspath(__file__)))
                path = BASE_DIR + instance.foto.url
            thumb = os.path.dirname(path) + '/thumbs/' + os.path.basename(path)
            try:
                os.remove(thumb)
            except OSError:
                pass
        instance.foto.delete(False)


def delete_photo_after_emptied(sender, instance, created, **kwargs):
    if not instance.foto and not created:
        pre_save_instance = instance._pre_save_instance
        if settings.MEDIA_ROOT and settings.MEDIA_URL:
            path = settings.MEDIA_ROOT + '/' + \
                   pre_save_instance.foto.url[len(settings.MEDIA_URL):]
        else:
            BASE_DIR = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)))
            path = BASE_DIR + pre_save_instance.foto.url
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


def get_pre_save_instance(sender, instance, **kwargs):
    try:
        instance._pre_save_instance = sender.objects.get(pk=instance.uuid)
    except sender.DoesNotExist:
        instance._pre_save_instance = instance


def path_and_rename(path):
    def wrapper(instance, filename):
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
    if instance.foto:
        if settings.MEDIA_ROOT and settings.MEDIA_URL:
            path = settings.MEDIA_ROOT + '/' + \
                   instance.foto.url[len(settings.MEDIA_URL):]
        else:
            BASE_DIR = os.path.dirname(
                os.path.dirname(
                    os.path.abspath(__file__)))
            path = BASE_DIR + instance.foto.url
        rotate_image(path)
        # falls Foto(s) mit derselben UUID, aber unterschiedlichem Suffix,
        # vorhanden: diese(s) löschen (und natürlich auch die entsprechenden
        # Thumbnails)!
        filename = os.path.basename(path)
        ext = filename.split('.')[-1]
        filename_without_ext = os.path.splitext(filename)[0]
        for file in os.listdir(os.path.dirname(path)):
            if os.path.splitext(
                    file)[0] == filename_without_ext and file.split('.')[
                -1] != ext:
                os.remove(os.path.dirname(path) + '/' + file)
        if hasattr(sender._meta, 'thumbs') and sender._meta.thumbs:
            thumb_path = os.path.dirname(path) + '/thumbs'
            if not os.path.exists(thumb_path):
                os.mkdir(thumb_path)
            thumb_path = os.path.dirname(
                path) + '/thumbs/' + os.path.basename(path)
            thumb_image(path, thumb_path)
            filename = os.path.basename(thumb_path)
            ext = filename.split('.')[-1]
            filename_without_ext = os.path.splitext(filename)[0]
            for file in os.listdir(os.path.dirname(thumb_path)):
                if os.path.splitext(
                        file)[0] == filename_without_ext and file.split('.')[
                    -1] != ext:
                    os.remove(os.path.dirname(thumb_path) + '/' + file)


def remove_permissions(sender, instance, **kwargs):
    model_name = instance.__class__.__name__.lower()
    user = getattr(instance, 'current_authenticated_user', None)
    for user in User.objects.all():
        remove_perm('datenmanagement.change_' + model_name, user, instance)
        remove_perm('datenmanagement.delete_' + model_name, user, instance)
    for group in Group.objects.all():
        remove_perm('datenmanagement.change_' + model_name, group, instance)
        remove_perm('datenmanagement.delete_' + model_name, group, instance)


def rotate_image(path):
    try:
        image = Image.open(path)
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
    try:
        image = Image.open(path)
        image.thumbnail((70, 70), Image.ANTIALIAS)
        image.save(thumb_path, optimize=True, quality=20)
        image.close()
    except (AttributeError, KeyError, IndexError):
        pass
