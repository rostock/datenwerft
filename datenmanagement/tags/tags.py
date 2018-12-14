from django import template
from django.conf import settings
from django.contrib.gis import forms
import os
import time


register = template.Library()


@register.filter
def get_class_name(value):
    return value.__class__.__name__


@register.filter
def get_class_description(value):
    return value.__class__._meta.description


@register.filter
def get_class_verbose_name_plural(value):
    return value.__class__._meta.verbose_name_plural


@register.filter
def get_class_object_title(value):
    if hasattr(value.__class__._meta, 'object_title'):
        return value.__class__._meta.object_title
    else:
        return None


@register.filter
def get_class_foreign_key_label(value):
    if hasattr(value.__class__._meta, 'foreign_key_label'):
        return value.__class__._meta.foreign_key_label
    else:
        return None


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


@register.simple_tag
def get_version_date():
    if os.path.isdir(os.path.join(settings.BASE_DIR, '.git')):
        return time.strftime('%d.%m.%Y', time.gmtime(os.path.getmtime(os.path.join(settings.BASE_DIR, '.git'))))
    else:
        return '?'


@register.filter
def is_field_address_related_field(field):
    if field.name == 'strasse_name' or field.name == 'hausnummer' or field.name == 'hausnummer_zusatz':
        return True
    else:
        return False


@register.filter
def is_field_foreign_key_field(field):
    if field.field.__class__ == forms.ModelChoiceField:
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
def user_has_model_permission(user, obj):
    permission_add = user.has_perm('datenmanagement.add_' + obj.__class__.__name__.lower())
    permission_change = user.has_perm('datenmanagement.change_' + obj.__class__.__name__.lower())
    permission_delete = user.has_perm('datenmanagement.delete_' + obj.__class__.__name__.lower())
    if permission_change or permission_add or permission_delete:
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
