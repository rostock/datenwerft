import logging

import requests
from django.forms import MultipleChoiceField, widgets

logger = logging.getLogger(__name__)


def resolve_pygeoapi_uris(uris, endpoint, params, label_property):
  """
  Löst eine Liste von PyGeoAPI-URIs zu lesbaren Labels auf.
  Gibt bei Fehler die rohen URIs zurück (Fallback).
  """
  try:
    response = requests.get(endpoint, params=params, timeout=10)
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
    return [uri_to_label.get(u, u) for u in uris]
  except requests.RequestException as e:
    logger.error('PyGeoAPI resolve failed for %s: %s', endpoint, e)
    return list(uris)


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
      'widget', widgets.SelectMultiple(attrs={'class': 'form-select select2-multiple catchment-area-select'})
    )
    choices = self._fetch_choices(endpoint, params, label_property)
    if initial_values:
      known_uris = {uri for uri, _ in choices}
      for uri in initial_values:
        if uri not in known_uris:
          choices.append((uri, '(nicht mehr verfügbar)'))
    super().__init__(choices=choices, **kwargs)

  def _fetch_choices(self, endpoint, params, label_property):
    try:
      response = requests.get(endpoint, params=params, timeout=10)
      response.raise_for_status()
      data = response.json()
      base_url = endpoint.rstrip('/')
      choices = []
      for feature in data.get('features', []):
        label = feature.get('properties', {}).get(label_property, '')
        feature_id = feature.get('id')
        # Prefer self link if present, otherwise construct URI from endpoint + id
        uri = next(
          (link['href'] for link in feature.get('links', []) if link.get('rel') == 'self'),
          None,
        )
        if uri is None and feature_id is not None:
          uri = f'{base_url}/{feature_id}'
        if uri and label:
          choices.append((uri, label))
      choices.sort(key=lambda x: x[1])
      return choices
    except requests.RequestException as e:
      logger.error('PyGeoAPI fetch failed for %s: %s', endpoint, e)
      return []
