import hashlib
import logging

import httpx
from django.core.cache import cache
from django.forms import MultipleChoiceField, widgets

logger = logging.getLogger(__name__)

_PYGEOAPI_CACHE_TTL = 600  # 10 Minuten


def _fetch_pygeoapi_label_map(endpoint, params_tuple, label_property):
  """
  Lädt alle Features vom PyGeoAPI-Endpunkt und gibt ein URI→Label-Dict zurück.
  Gecacht für :data:`_PYGEOAPI_CACHE_TTL` Sekunden über Djangos Cache-Framework.
  """
  cache_key = (
    'pygeoapi_' + hashlib.md5(f'{endpoint}|{params_tuple}|{label_property}'.encode()).hexdigest()
  )
  cached = cache.get(cache_key)
  if cached is not None:
    return cached
  try:
    response = httpx.get(endpoint, params=dict(params_tuple), timeout=10)
    response.raise_for_status()
    data = response.json()
    base_url = endpoint.rstrip('/')
    uri_to_label = {}
    for feature in data.get('features', []):
      label = feature.get('properties', {}).get(label_property, '')
      feature_id = feature.get('id')
      uri = next(
        (link['href'] for link in feature.get('links', []) if link.get('rel') == 'self'),
        None,
      )
      if uri is None and feature_id is not None:
        uri = f'{base_url}/{feature_id}'
      if uri and label:
        uri_to_label[uri] = label
    cache.set(cache_key, uri_to_label, timeout=_PYGEOAPI_CACHE_TTL)
    return uri_to_label
  except httpx.HTTPError as e:
    logger.error('PyGeoAPI fetch failed for %s: %s', endpoint, e)
    return {}


def resolve_pygeoapi_uris(uris, endpoint, params, label_property):
  """
  Löst eine Liste von PyGeoAPI-URIs zu lesbaren Labels auf.
  Gibt bei Fehler die rohen URIs zurück (Fallback).
  """
  label_map = _fetch_pygeoapi_label_map(
    endpoint,
    tuple(sorted(params.items())),
    label_property,
  )
  return [label_map.get(u, u) for u in uris]


class PyGeoAPIMultipleChoiceField(MultipleChoiceField):
  """
  A MultipleChoiceField that fetches its choices from a PyGeoAPI items endpoint.

  Configuration is done via the model's PYGEOAPI_FIELDS class attribute:

    PYGEOAPI_FIELDS = {
      'field_name': {
        'endpoint': 'https://example.com/ogcapi/collections/foo/items',
        'params': {'f': 'json', 'some_filter': 'value'},
        'label_property': 'bezeichnung',
      }
    }

  Values are the self-link URIs of the selected features. Labels are taken from
  the specified property in the feature's properties dict.

  If existing saved URIs are no longer present in the API response (e.g. due to
  data changes), they are appended as choices labelled "(nicht mehr verfügbar)"
  so the user can see and remove them explicitly.
  """

  def __init__(self, endpoint, params, label_property, initial_values=None, **kwargs):
    kwargs.setdefault('required', False)
    kwargs.setdefault(
      'widget',
      widgets.SelectMultiple(
        attrs={'class': 'form-select select2-multiple catchment-area-select'}
      ),
    )
    choices = self._fetch_choices(endpoint, params, label_property)
    if initial_values:
      known_uris = {uri for uri, _ in choices}
      for uri in initial_values:
        if uri not in known_uris:
          choices.append((uri, '(nicht mehr verfügbar)'))
    super().__init__(choices=choices, **kwargs)

  def _fetch_choices(self, endpoint, params, label_property):
    label_map = _fetch_pygeoapi_label_map(
      endpoint,
      tuple(sorted(params.items())),
      label_property,
    )
    choices = list(label_map.items())
    choices.sort(key=lambda x: x[1])
    return choices
