import json
import re
import time
import uuid

from datetime import datetime, timezone
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.core.exceptions import PermissionDenied
from django.db import connection
from django.db.models import Q
from django.forms import ChoiceField, ModelForm, TextInput, \
    UUIDField, ValidationError
from django.forms.models import modelform_factory
from django.http import HttpResponse
from django.urls import reverse
from django.utils.html import escape
from django.views import generic
from django_datatables_view.base_datatable_view import BaseDatatableView
from guardian.core import ObjectPermissionChecker
from jsonview.views import JsonView
from operator import attrgetter
from zoneinfo import ZoneInfo

from . import functions



class AddressUUIDField(UUIDField):
    """
    verstecktes Input-Feld bei der Adressensuche

    Verwendung in Klasse DataForm
    """

    def to_python(self, value):
        """

        :param value: UUID
        :return: Adresse
        """
        if value in self.empty_values:
            return None
        adressen = apps.get_app_config('datenmanagement').get_model('Adressen')
        return adressen.objects.get(pk=value)


class StreetUUIDField(UUIDField):
    """
    verstecktes Input-Feld bei der Straßensuche

    Verwendung in Klasse DataForm
    """

    def to_python(self, value):
        """

        :param value: UUID
        :return: Straße
        """
        if value in self.empty_values:
            return None
        strassen = apps.get_app_config('datenmanagement').get_model('Strassen')
        return strassen.objects.get(pk=value)
