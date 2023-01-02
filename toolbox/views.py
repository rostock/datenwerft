import json
import re
import requests

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseServerError, JsonResponse
from django.views import generic
from django.views.decorators.csrf import csrf_exempt

from .models import Subsets


class AddSubsetView(generic.View):
  """
  Add a new subset
  """
  http_method_names = ['post']

  def __init__(self):
    self.app_label = None
    self.model_name = None
    self.pk_field = None
    self.pk_values = None
    super().__init__()

  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    """
    ``dispatch()`` is called via ``AddSubsetView.as_view()`` in ``urls.py``;
    ``dispatch()`` forwards to ``post()`` since a **POST** request has been executed
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    self.app_label = request.POST.get('app_label', None)
    self.model_name = request.POST.get('model_name', None)
    self.pk_field = request.POST.get('pk_field', None)
    pk_values = request.POST.get('pk_values', None)
    self.pk_values = json.loads(pk_values)
    return super(AddSubsetView, self).dispatch(request, *args, **kwargs)

  @csrf_exempt
  def post(self, request, *args, **kwargs):
    """
    ``post()`` is called automatically by ``dispatch()``

    :param request:
    :param args:
    :param kwargs:
    :return: JSON response with ID of newly created subset or simple HTTP error response
    """
    try:
      content_type = ContentType.objects.filter(app_label=self.app_label, model=self.model_name)[0]
      subset = Subsets.objects.create(
        model=content_type,
        pk_field=self.pk_field,
        pk_values=self.pk_values
      )
      subset.save()
      response = {
          'id': str(subset.pk)
      }
      return JsonResponse(status=200, data=json.dumps(response), safe=False)
    except (IntegrityError, MultipleObjectsReturned):
      return HttpResponseServerError()
    except Exception:
      return HttpResponseServerError()


class OWSProxyView(generic.View):
  """
  proxy for OGC web services (OWS)
  """
  http_method_names = ['get']

  def __init__(self):
    self.destination_url = None
    super().__init__()

  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    """
    ``dispatch()`` is called via ``OWSProxyView.as_view()`` in ``urls.py``;
    ``dispatch()`` forwards to ``get()`` since a **GET** request has been executed
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

  @csrf_exempt
  def get(self, request, *args, **kwargs):
    """
    ``get()`` is called automatically by ``dispatch()``

    :param request:
    :param args:
    :param kwargs:
    :return: HTTP response with proxied OWS
    """
    try:
      response = requests.get(self.destination_url, timeout=60)
      return HttpResponse(response, content_type=response.headers['content-type'])
    except Exception:
      return HttpResponseServerError()


class AddressSearchView(generic.View):
  """
  address search
  """
  http_method_names = ['get']

  def __init__(self):
    self.addresssearch_type = None
    self.addresssearch_class = None
    self.addresssearch_query = None
    self.addresssearch_out_epsg = None
    self.addresssearch_shape = None
    self.addresssearch_limit = None
    super().__init__()

  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    """
    ``dispatch()`` is called via ``AddressSearchView.as_view()`` in ``urls.py``;
    ``dispatch()`` forwards to ``get()`` since a **GET** request has been executed
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
    return super(AddressSearchView, self).dispatch(request, *args, **kwargs)

  @csrf_exempt
  def get(self, request, *args, **kwargs):
    """
    ``get()`` is called automatically by ``dispatch()``

    :param request:
    :param args:
    :param kwargs:
    :return: HTTP response with address search result
    """
    try:
      response = requests.get(
        url=settings.ADDRESS_SEARCH_URL
        + "key=" + settings.ADDRESS_SEARCH_KEY
        + "&type=" + self.addresssearch_type
        + "&class=" + self.addresssearch_class
        + "&query=" + self.addresssearch_query
        + "&out_epsg=" + self.addresssearch_out_epsg
        + "&shape=" + self.addresssearch_shape
        + "&limit=" + self.addresssearch_limit,
        timeout=3
      )
      return HttpResponse(response, content_type='application/json')
    except Exception:
      return HttpResponseServerError()


class ReverseSearchView(generic.View):
  """
  search for objects in specified radius around given coordinates
  """
  http_method_names = ['get']

  def __init__(self):
    self.reversesearch_type = None
    self.reversesearch_class = None
    self.reversesearch_x = None
    self.reversesearch_y = None
    self.reversesearch_in_epsg = None
    super().__init__()

  @csrf_exempt
  def dispatch(self, request, *args, **kwargs):
    """
    ``dispatch()`` is called via ``ReverseSearchView.as_view()`` in ``urls.py``;
    ``dispatch()`` forwards to ``get()`` since a **GET** request has been executed
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
    return super(ReverseSearchView, self).dispatch(request, *args, **kwargs)

  @csrf_exempt
  def get(self, request, *args, **kwargs):
    """
    ``get()`` is called automatically by ``dispatch()``

    :param request:
    :param args:
    :param kwargs:
    :return: HTTP response with objects in specified radius around given coordinates
    """
    try:
      response = requests.get(
        url=settings.ADDRESS_SEARCH_URL
        + "key=" + settings.ADDRESS_SEARCH_KEY
        + "&type=" + self.reversesearch_type
        + "&class=" + self.reversesearch_class
        + "&query=" + self.reversesearch_x + "," + self.reversesearch_y
        + "&in_epsg=" + self.reversesearch_in_epsg
        + "&radius=" + str(settings.REVERSE_SEARCH_RADIUS),
        timeout=3
      )
      return HttpResponse(response, content_type='application/json')
    except Exception:
      return HttpResponseServerError()
