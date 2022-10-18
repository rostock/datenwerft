import os
import re

from datetime import date, datetime
from django.apps import apps
from django.core.exceptions import PermissionDenied
from django.forms import CheckboxSelectMultiple, TextInput
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from guardian.core import ObjectPermissionChecker
from leaflet.forms.widgets import LeafletWidget


def assign_widgets(field):
  """
  liefert passendes Formularelement (Widget) zu field

  :param field: Feld
  :return: Formularelement (Widget)
  """
  form_field = field.formfield()
  if form_field.widget.__class__.__name__ == 'Select':
    form_field.widget.attrs['class'] = 'form-select'
    return form_field
  elif form_field.widget.__class__.__name__ == 'Textarea':
    form_field.widget.attrs['class'] = 'form-control'
    return form_field
  elif field.name == 'geometrie':
    return field.formfield(widget=LeafletWidget())
  elif field.__class__.__name__ == 'CharField' and field.name == 'farbe':
    return field.formfield(widget=TextInput(attrs={
      'type': 'color',
      'class': 'form-control-color'
    }))
  elif field.__class__.__name__ == 'ChoiceArrayField':
    return field.formfield(empty_value=None,
                           widget=CheckboxSelectMultiple())
  elif field.__class__.__name__ == 'DateField':
    return field.formfield(widget=TextInput(attrs={
      'type': 'date',
      'class': 'form-control'
    }))
  elif field.__class__.__name__ == 'DateTimeField':
    return field.formfield(widget=TextInput(attrs={
      'type': 'datetime-local',
      'class': 'form-control',
      'step': '1'
    }))
  elif field.__class__.__name__ == 'TimeField':
    return field.formfield(widget=TextInput(attrs={
      'type': 'time',
      'class': 'form-control',
      'step': '1'
    }))
  else:
    if hasattr(form_field.widget, 'input_type'):
      if form_field.widget.input_type == 'checkbox':
        form_field.widget.attrs['class'] = 'form-check-input'
      else:
        form_field.widget.attrs['class'] = 'form-control'
    return form_field


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


def get_data(curr_object, field):
  """
  gibt für Datenobjekt die Daten eines bestimmten Feldes zurück

  :param curr_object: Datenobjekt
  :param field: Feld
  :return: Daten
  """
  data = getattr(curr_object, field)
  if isinstance(data, date):
    data = data.strftime('%Y-%m-%d')
  elif isinstance(data, datetime):
    data = data.strftime('%Y-%m-%d %H:%M:%S')
  return data


def get_thumb_url(url):
  """
  gibt für url die zugehörige Thumbnail-URL zurück

  :param url: URL eines Bildes
  :return: URL des zugehörigen Thumbnails
  """
  head, tail = os.path.split(url)
  return head + '/thumbs/' + tail
