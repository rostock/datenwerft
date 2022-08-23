import os
import re

from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.forms import CheckboxSelectMultiple, TextInput
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from guardian.core import ObjectPermissionChecker
from leaflet.forms.widgets import LeafletWidget
from tempus_dominus.widgets import DatePicker, DateTimePicker



def assign_widgets(field):
    """
    liefert passendes Formularelement oder Widget zu field

    :param field: Feld
    :return: Formularelement oder Widget
    """
    if field.name == 'geometrie':
        return field.formfield(widget=LeafletWidget())
    elif field.__class__.__name__ == 'CharField' and field.name == 'farbe':
        return field.formfield(widget=TextInput(attrs={
            'type': 'color'
        }))
    elif field.__class__.__name__ == 'ChoiceArrayField':
        return field.formfield(empty_value=None,
                               widget=CheckboxSelectMultiple())
    elif field.__class__.__name__ == 'DateField':
        return field.formfield(widget=DatePicker(attrs={
            'input_toggle': False,
            'append': 'fas fa-calendar'
        }))
    elif field.__class__.__name__ == 'DateTimeField':
        return field.formfield(widget=DateTimePicker(attrs={
            'input_toggle': False,
            'append': 'fas fa-clock'
        }))
    else:
        return field.formfield()


def delete_object_immediately(request, pk):
    """
    löscht ein Objekt aus der Datenbank; wirft eine
    entsprechende Exception bei fehlenden Berechtigungen

    :param request: WSGI-Request
    :param pk: Primärschlüssel des zu löschenden Datenbankobjekts
    :return: HTTP 204 No Content
    """
    model_name = re.sub(
        pattern='^.*\\/',
        repl='',
        string=re.sub(
            pattern='\\/deleteimmediately.*$',
            repl='',
            string=request.path_info
        )
    )
    model = apps.get_app_config('datenmanagement').get_model(model_name)
    obj = get_object_or_404(model, pk=pk)
    if ObjectPermissionChecker(request.user).has_perm(
            'delete_' + model_name.lower(), obj):
        obj.delete()
    else:
        raise PermissionDenied()
    return HttpResponse(status=204)


def get_thumb_url(url):
    """
    gibt für url die zugehörige Thumbnail-URL zurück

    :param url: URL eines Bildes
    :return: URL des zugehörigen Thumbnails
    """
    head, tail = os.path.split(url)
    return head + '/thumbs/' + tail
