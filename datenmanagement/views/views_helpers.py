import json
import requests

from datenwerft.secrets import FME_TOKEN, FME_URL
from django.db import connections
from django.http import JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from jsonview.views import JsonView

from . import functions


class GeometryView(JsonView):
  """
  Abfrage von Geometrien bestimmter Modelle

  zur Filterung können folgende Angaben gemacht werden:
  * lat, lng, (rad): Koordinaten eines Punktes (EPSG:4326) und Radius
  * pk: Primärschlüssel eines Datenbankobjekts

  :param model: Datenmodell
  """
  model = None

  def __init__(self, model):
    self.model = model
    super(GeometryView, self).__init__()

  def get_context_data(self, **kwargs):
    """
    liefert Dictionary mit Kontextelementen des Views

    :param kwargs:
    :return: Dictionary mit Kontextelementen des Views
    """
    context = super(GeometryView, self).get_context_data(**kwargs)
    # Filtern nach angegebenen Kriterien
    if self.request.GET.get('pk'):
      # Bei Angaben von 'pk'
      pk = self.request.GET.get('pk')
      with connections['datenmanagement'].cursor() as cursor:
        cursor.execute(
            'SELECT uuid, st_astext(st_transform(geometrie, 4326)) FROM ' +
            self.model._meta.db_table.replace(
                '"',
                '') +
            ' WHERE uuid = %s;',
            [pk])
        uuid, geom = cursor.fetchone()  # Tupel
        context['uuid'] = uuid
        context['geometry'] = geom
    elif self.request.GET.get('lat') and self.request.GET.get('lng'):
      # Bei Angabe von Koordinaten (rad standardmäßig 0)
      lat = float(self.request.GET.get('lat'))
      lng = float(self.request.GET.get('lng'))
      if self.request.GET.get('rad'):
        rad = float(self.request.GET.get('rad'))
      else:
        rad = 0
      with connections['datenmanagement'].cursor() as cursor:
        cursor.execute(
            'SELECT uuid, st_astext(st_transform(geometrie, 4326)) FROM ' +
            self.model._meta.db_table.replace('"', '') +
            ' WHERE st_buffer(st_transform(st_setsrid(' +
            'st_makepoint(%s, %s),4326)::geometry,25833),%s) && geometrie;',
            [lng, lat, rad]
        )
        uuids_geometries = functions.get_uuids_geometries_from_sql(cursor.fetchall())
        context['uuids'] = uuids_geometries[0]
        context['object_list'] = uuids_geometries[1]
    else:
      with connections['datenmanagement'].cursor() as cursor:
        cursor.execute(
            'SELECT uuid, st_astext(st_transform(geometrie, 4326)) FROM ' +
            self.model._meta.db_table.replace(
                '"',
                '') +
            ';',
            [])
        uuids_geometries = functions.get_uuids_geometries_from_sql(cursor.fetchall())
        context['uuids'] = uuids_geometries[0]
        context['object_list'] = uuids_geometries[1]
    context['model_name'] = self.model.__name__

    return context


class GPXtoGeoJSON(generic.View):
  """
  Übergabe einer GPX-Datei an FME Server und Rückgabe des generierten GeoJSON
  """
  http_method_names = ['post']

  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    """
    ``dispatch()`` wird von ``GPXtoGeoJSON.as_view()`` in ``urls.py`` aufgerufen;
    ``dispatch()`` leitet auf ``post()`` weiter, da ein **POST**-Request ausgeführt wurde
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    return super(GPXtoGeoJSON, self).dispatch(request, *args, **kwargs)

  @csrf_exempt
  def post(self, request, *args, **kwargs):
    """
    ``post()`` wird automatisch von ``dispatch()`` aufgerufen

    :param request:
    :param args:
    :param kwargs:
    :return: GeoJSON der übergebenen GPX-Datei oder FME-Server-Fehler
    """
    # Name 'gpx' Kommt aus dem Inputfeld im Template
    gpx_file = request.FILES['gpx']
    x = requests.post(
        url=FME_URL,
        headers={
            "Authorization": FME_TOKEN,
            "Content-Type": "application/gpx+xml",
            "Accept": "application/geo+json",
        },
        data=gpx_file,
    )
    if x.status_code != 200:
      response = {
          "StatusCode": str(x.status_code),
          "FMELog": str(x.text)
      }
      return JsonResponse(data=json.dumps(response))
    else:
      return JsonResponse(data=x.json())
