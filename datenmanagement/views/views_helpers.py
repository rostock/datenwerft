import json
import re
import requests

from datenwerft.secrets import FME_TOKEN, FME_URL
from django.conf import settings
from django.db import connections
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from jsonview.views import JsonView


class OWSProxyView(generic.View):
  """
  Proxy für OGC Web Services (OWS)

  mit diesem können auch interne OWS nach außen bereitgestellt werden
  """
  http_method_names = ['get', ]

  def __init__(self):
    self.destination_url = None
    super().__init__()

  def dispatch(self, request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    self.destination_url = settings.OWS_BASE + re.sub(
        pattern='^.*owsproxy',
        repl='',
        string=str(request.get_full_path)
    )
    return super(OWSProxyView, self).dispatch(request, *args, **kwargs)

  def get(self, request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    response = requests.get(self.destination_url, timeout=60)
    return HttpResponse(response,
                        content_type=response.headers['content-type'])


class AddressSearchView(generic.View):
  """
  Adressensuche

  API-Key bleibt nach außen verborgen
  """
  http_method_names = ['get', ]

  def __init__(self):
    self.addresssearch_type = None
    self.addresssearch_class = None
    self.addresssearch_query = None
    self.addresssearch_out_epsg = None
    self.addresssearch_shape = None
    self.addresssearch_limit = None
    super().__init__()

  def dispatch(self, request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    self.addresssearch_type = 'search'
    self.addresssearch_class = 'address_hro'
    self.addresssearch_query = request.GET.get('query', '')
    self.addresssearch_out_epsg = '4326'
    self.addresssearch_shape = 'bbox'
    self.addresssearch_limit = '5'
    return super(
        AddressSearchView,
        self).dispatch(
        request,
        *
        args,
        **kwargs)

  def get(self, request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    response = requests.get(
        settings.ADDRESS_SEARCH_URL + 'key=' + settings.ADDRESS_SEARCH_KEY
        + '&type=' + self.addresssearch_type + '&class='
        + self.addresssearch_class + '&query=' + self.addresssearch_query
        + '&out_epsg=' + self.addresssearch_out_epsg + '&shape='
        + self.addresssearch_shape + '&limit=' + self.addresssearch_limit,
        timeout=3
    )
    return HttpResponse(response, content_type='application/json')


class ReverseSearchView(generic.View):
  """
  Suche nach Objekten in bestimmtem Radius um gegebene Koordinaten

  API-Key bleibt nach außen verborgen
  """
  http_method_names = ['get', ]

  def __init__(self):
    self.reversesearch_type = None
    self.reversesearch_class = None
    self.reversesearch_x = None
    self.reversesearch_y = None
    self.reversesearch_in_epsg = None
    super().__init__()

  def dispatch(self, request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    self.reversesearch_type = 'reverse'
    self.reversesearch_class = request.GET.get('search_class', '')
    self.reversesearch_x = request.GET.get('x', '')
    self.reversesearch_y = request.GET.get('y', '')
    self.reversesearch_in_epsg = '4326'
    return super(
        ReverseSearchView,
        self).dispatch(
        request,
        *
        args,
        **kwargs)

  def get(self, request, *args, **kwargs):
    """

    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    response = requests.get(
        url=settings.ADDRESS_SEARCH_URL + 'key=' +
        settings.ADDRESS_SEARCH_KEY + '&type=' +
        self.reversesearch_type + '&class=' +
        self.reversesearch_class + '&query=' +
        self.reversesearch_x + ',' +
        self.reversesearch_y + '&in_epsg=' +
        self.reversesearch_in_epsg + '&radius=' +
        str(settings.REVERSE_SEARCH_RADIUS),
        timeout=3)
    return HttpResponse(response, content_type='application/json')


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
        context['model_name'] = self.model.__name__
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
        row = cursor.fetchall()
        uuids = []
        geom = []
        for i in range(len(row)):
          uuids.append(row[i][0])
          geom.append(str(row[i][1]))
        context['uuids'] = uuids
        context['object_list'] = geom
        context['model_name'] = self.model.__name__
    else:
      with connections['datenmanagement'].cursor() as cursor:
        cursor.execute(
            'SELECT uuid, st_astext(st_transform(geometrie, 4326)) FROM ' +
            self.model._meta.db_table.replace(
                '"',
                '') +
            ';',
            [])
        row = cursor.fetchall()
        uuids = []
        geom = []
        for i in range(len(row)):
          uuids.append(row[i][0])
          geom.append(str(row[i][1]))
        context['uuids'] = uuids
        context['object_list'] = geom
        context['model_name'] = self.model.__name__

    return context


class GPXtoGeoJSON(generic.View):
  """
  Übergabe einer GPX-Datei an FME Server und Rückgabe des generierten GeoJSON
  """
  http_method_names = ['post', ]

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
