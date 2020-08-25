from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.gis import forms
from guardian.core import ObjectPermissionChecker
import os
import re
import time


register = template.Library()


@register.filter
def get_class_description(value):
    return value.__class__._meta.description


@register.filter
def get_class_codelist(value):
    if hasattr(value.__class__._meta, 'codelist'):
        return value.__class__._meta.codelist
    else:
        return None


@register.filter
def get_class_foreign_key_label(value):
    if hasattr(value.__class__._meta, 'foreign_key_label'):
        return value.__class__._meta.foreign_key_label
    else:
        return None


@register.filter
def get_class_name(value):
    return value.__class__.__name__


@register.filter
def get_class_object_title(value):
    if hasattr(value.__class__._meta, 'object_title'):
        return value.__class__._meta.object_title
    else:
        return None


@register.filter
def get_class_verbose_name_plural(value):
    return value.__class__._meta.verbose_name_plural


@register.filter
def get_list_item_by_index(list, i):
    return list[i]


@register.filter
def get_thumb_url(value):
    head, tail = os.path.split(value)
    return head + '/thumbs/' + tail


@register.filter
def get_type_of_field(field_name, model_name):
    model = apps.get_app_config('datenmanagement').get_model(model_name)
    type_of_field = re.sub('\'>$', '', re.sub('^.*\.', '', str(model._meta.get_field(field_name).__class__)))
    return type_of_field


@register.filter
def get_type_of_geometry_field(field):
    if field.field.__class__ == forms.PointField:
        return 1
    elif field.field.__class__ == forms.LineStringField:
        return 2
    elif field.field.__class__ == forms.MultiLineStringField:
        return 3
    elif field.field.__class__ == forms.PolygonField:
        return 4
    elif field.field.__class__ == forms.MultiPolygonField:
        return 5
    else:
        return ["None"]


@register.filter
def get_value_of_field(value, field):
    return getattr(value, field)


@register.filter
def get_values(value):
    valuelist = []
    fieldlist = value.__class__._meta.list_fields
    if fieldlist:
        for field in fieldlist:
            item = getattr(value, field)
            if (isinstance(item, list)):
                item = ', '.join(sorted(item))
            valuelist.append(item)
        return valuelist
    else:
        return ["None"]


@register.filter
def get_value_of_map_feature_tooltip_field(value):
    field = value.__class__._meta.map_feature_tooltip_field
    if field:
        return getattr(value, field)
    else:
        return ["None"]


@register.filter
def get_and_concat_values_of_map_feature_tooltip_fields(value):
    tooltip_value = ''
    index = 0
    for field in value.__class__._meta.map_feature_tooltip_fields:
        tooltip_value = (tooltip_value + ' ' + getattr(value, field) if index > 0 else getattr(value, field))
        index += 1
    return tooltip_value


@register.simple_tag
def get_version_date():
    if os.path.isdir(os.path.join(settings.BASE_DIR, '.git')):
        return time.strftime('%d.%m.%Y', time.gmtime(os.path.getmtime(os.path.join(settings.BASE_DIR, '.git'))))
    else:
        return '?'


@register.filter
def is_field_address_related_field(field):
    if field.name == 'adresse' or field.name == 'strasse':
        return True
    else:
        return False


@register.filter
def is_field_geometry_field(field):
    if field.field.__class__ == forms.PointField or field.field.__class__ == forms.LineStringField or field.field.__class__ == forms.MultiLineStringField or field.field.__class__ == forms.PolygonField or field.field.__class__ == forms.MultiPolygonField:
        return True
    else:
        return False


@register.filter
def is_field_hours_related_field(field):
    if field.name.endswith('zeiten'):
        return True
    else:
        return False


@register.filter
def is_field_nullable(field_name, model_name):
    model = apps.get_app_config('datenmanagement').get_model(model_name)
    return model._meta.get_field(field_name).null


@register.filter
def is_user_in_group_by_user_name(user_name, group_name):
    user_mail = re.sub('^.*\(', '', user_name)
    user_mail = re.sub('\)$', '', user_mail)
    users = User.objects.filter(groups__name = group_name)
    for user in users:
        if user.email.lower() == user_mail:
            return True
    return False


@register.filter
def is_user_in_group_by_user_object(user, group_name):
    return user.groups.filter(name = group_name).exists()


@register.filter
def user_has_model_permissions(user):
    models = apps.get_app_config('datenmanagement').get_models()
    for model in models:
        if user.has_perm('datenmanagement.add_' + model.__name__.lower()) or user.has_perm('datenmanagement.change_' + model.__name__.lower()) or user.has_perm('datenmanagement.delete_' + model.__name__.lower()) or user.has_perm('datenmanagement.view_' + model.__name__.lower()):
            return True
    return False


@register.filter
def user_has_model_permission(user, obj):
    permission_add = user.has_perm('datenmanagement.add_' + obj.__class__.__name__.lower())
    permission_change = user.has_perm('datenmanagement.change_' + obj.__class__.__name__.lower())
    permission_delete = user.has_perm('datenmanagement.delete_' + obj.__class__.__name__.lower())
    permission_view = user.has_perm('datenmanagement.view_' + obj.__class__.__name__.lower())
    if permission_change or permission_add or permission_delete or permission_view:
        return True
    else:
        return False


@register.filter
def user_has_model_add_permission(user, model_name_lower):
    if user.has_perm('datenmanagement.add_' + model_name_lower):
        return True
    else:
        return False


@register.filter
def user_has_model_change_permission(user, model_name_lower):
    if user.has_perm('datenmanagement.change_' + model_name_lower):
        return True
    else:
        return False


@register.filter
def user_has_model_delete_permission(user, model_name_lower):
    if user.has_perm('datenmanagement.delete_' + model_name_lower):
        return True
    else:
        return False


@register.filter
def user_has_model_view_permission(user, model_name_lower):
    if user.has_perm('datenmanagement.view_' + model_name_lower):
        return True
    else:
        return False


@register.filter
def user_has_object_change_permission(user, obj):
    if ObjectPermissionChecker(user).has_perm('change_' + obj.__class__.__name__.lower(), obj):
        return True
    else:
        return False


@register.filter
def user_has_object_delete_permission(user, obj):
    if ObjectPermissionChecker(user).has_perm('delete_' + obj.__class__.__name__.lower(), obj):
        return True
    else:
        return False
