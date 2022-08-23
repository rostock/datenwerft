#import json
import os
import re
#import requests
#import time
#import uuid
#from datetime import datetime, timezone
#from datenerfassung.secrets import FME_TOKEN, FME_URL
from django.apps import apps
#from django.conf import settings
#from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
#from django.db import connection
#from django.db.models import Q
from django.forms import CheckboxSelectMultiple, TextInput
#from django.forms import CheckboxSelectMultiple, ChoiceField, ModelForm, \
 #   UUIDField, ValidationError, TextInput
#from django.forms.models import modelform_factory
from django.http import HttpResponse
#from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
#from django.urls import reverse
#from django.utils.html import escape
#from django.views import generic
#from django.views.decorators.csrf import csrf_exempt
#from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.core import ObjectPermissionChecker
#from jsonview.views import JsonView
from leaflet.forms.widgets import LeafletWidget
#from operator import attrgetter
from tempus_dominus.widgets import DatePicker, DateTimePicker
#from zoneinfo import ZoneInfo


def assign_widgets(field):
    """
    Liefert zu field passendes Formularwidget.

    :param field:
    :return: Widget für Formular
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
    Löschen eines Datensatzes aus der DB. Bei fehlenden Berechtigungen wird eine
    PermissionDenied() Exception geworfen.

    :param request: WSGI Request
    :param pk: Primärschlüssel des zu löschenden Objekts
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
    Gibt für gegebene Bild-URL, die dazugehörige Thumbnail-URL zurück.

    :param url: URL eines Bildes
    :return: URL des zugehörigen Thumbnails
    """
    head, tail = os.path.split(url)
    return head + '/thumbs/' + tail