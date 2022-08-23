import re
import requests

from datenerfassung.secrets import FME_TOKEN, FME_URL
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt



class OWSProxyView(generic.View):
    """
    Proxy für OGC Web Services (OWS)

    auch interne OWS können nach außen bereitgestellt werden
    """
    http_method_names = ['get', ]

    def dispatch(self, request, *args, **kwargs):
        self.destination_url = settings.OWS_BASE + re.sub(
            pattern='^.*owsproxy',
            repl='',
            string=str(request.get_full_path)
        )
        return super(OWSProxyView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        response = requests.get(self.destination_url, timeout=60)
        return HttpResponse(response,
                            content_type=response.headers['content-type'])


class AddressSearchView(generic.View):
    """
    Adressen-/Straßensuche

    API-Key bleibt nach außen verborgen
    """
    http_method_names = ['get', ]

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

    def dispatch(self, request, *args, **kwargs):
        """

        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.reversesearch_type = 'reverse'
        self.reversesearch_class = 'address'
        self.reversesearch_x = request.GET.get('x', '')
        self.reversesearch_y = request.GET.get('y', '')
        self.reversesearch_in_epsg = '4326'
        self.reversesearch_radius = '200'
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
            self.reversesearch_radius,
            timeout=3)
        return HttpResponse(response, content_type='application/json')


class GPXtoGeoJSON(generic.View):
    """
    Weiterleiten einer GPX-Datei an FME Server und zurückgeben des generierten GeoJSON
    """
    http_method_names = ['post', ]

    @csrf_exempt
    def dispatch(self, request, *args, **kwargs):
        """
        ``dispatch()`` wird von ``GPXtoGeoJSON.as_view()`` in ``urls.py``
        aufgerufen. ``dispatch()`` leitet auf ``post()`` weiter, da ein
        **POST** Request ausgeführt wurde.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        return super(GPXtoGeoJSON, self).dispatch(request, *args, **kwargs)

    @csrf_exempt
    def post(self, request, *args, **kwargs):
        """
        Automatisch von ``dispatch()`` aufgerufen.
        :param request:
        :param args:
        :param kwargs:
        :return: GeoJSON der übergebenen GPX-Datei oder FME-Server-Fehler
        """
        # Name 'gpx' Kommt aus dem Inputfeld im Template
        gpxFile = request.FILES['gpx']
        x = requests.post(
            url=FME_URL,
            headers={
                "Authorization": FME_TOKEN,
                "Content-Type": "application/gpx+xml",
                "Accept": "application/geo+json",
            },
            data=gpxFile,
        )
        if (x.status_code != 200):
            response = {
                "StatusCode": str(x.status_code),
                "FMELog": str(x.text)
            }
            return JsonResponse(data=response.json())
        else:
            return JsonResponse(data=x.json())
