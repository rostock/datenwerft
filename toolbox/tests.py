import json
import random

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Subsets


USERNAME = 'foobar'
PASSWORD = 'secret42'
INVALID_API_KEY = 'foobar'


class SubsetsTestCase(TestCase):
  APP_LABEL = 'contenttypes'
  MODEL_NAME = 'contenttype'
  PK_FIELD_INITIAL = 'uuid'
  PK_FIELD_UPDATED = 'oid'
  PK_VALUE_1 = '42'
  PK_VALUE_2 = '3e029807-86de-4ac0-aea3-9cd1c6db45a3'
  PK_VALUE_3 = 'foobar'
  PK_VALUES = '["42", "3e029807-86de-4ac0-aea3-9cd1c6db45a3", "foobar"]'

  def init(self):
    self.test_user = User.objects.create_user(
      username=USERNAME,
      password=PASSWORD
    )
    self.content_types = list(ContentType.objects.all())
    self.random_content_type = random.choice(self.content_types)
    self.subset = Subsets.objects.create(
      model=self.random_content_type,
      pk_field=self.PK_FIELD_INITIAL,
      pk_values=[
        self.PK_VALUE_1,
        self.PK_VALUE_2,
        self.PK_VALUE_3
      ]
    )


class SubsetsTest(SubsetsTestCase):

  def setUp(self):
    self.init()

  def test_create(self):
    # exactly one object created?
    self.assertEqual(Subsets.objects.all().count(), 1)
    # object created exactly as it should have been created?
    subset = Subsets.objects.get(pk_field=self.PK_FIELD_INITIAL)
    self.assertEqual(subset, self.subset)
    # created object contains specific value in one of its fields?
    self.assertEqual(Subsets.objects.filter(pk_values__contains=[self.PK_VALUE_2]).count(), 1)

  def test_update(self):
    self.subset.pk_field = self.PK_FIELD_UPDATED
    self.subset.save()
    # still exactly one object?
    self.assertEqual(Subsets.objects.all().count(), 1)
    # object updated exactly as it should have been updated?
    subset = Subsets.objects.get(pk_field=self.PK_FIELD_UPDATED)
    self.assertEqual(subset, self.subset)
    # exactly one (i.e. the updated) object contains specific value in one of its fields?
    self.assertEqual(Subsets.objects.filter(pk_field=self.PK_FIELD_UPDATED).count(), 1)

  def test_delete(self):
    # still exactly one object?
    self.assertEqual(Subsets.objects.all().count(), 1)
    # no more objects left?
    self.subset.delete()
    self.assertEqual(Subsets.objects.all().count(), 0)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_add_success(self):
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # try to create object via POSTing its attributes
    response = self.client.post(
      reverse('toolbox:subset_add'),
      data={
        'app_label': self.APP_LABEL,
        'model_name': self.MODEL_NAME,
        'pk_field': self.PK_FIELD_INITIAL,
        'pk_values': self.PK_VALUES
      }
    )
    # POST successful and thus object created?
    self.assertEqual(response.status_code, 200)
    response_json = json.loads(response.content.decode('utf-8'))
    response_dict = json.loads(response_json)
    # response contains ID of created object?
    self.assertIsNotNone(response_dict['id'])
    # ID of created object contained in response is numerical?
    self.assertIsInstance(int(response_dict['id']), int)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_view_add_error(self):
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # try to create object via POSTing its attributes
    # but forcing an error by omitting the obligatory attribute ``pk_field``
    response = self.client.post(
      reverse('toolbox:subset_add'),
      data={
        'app_label': self.APP_LABEL,
        'model_name': self.MODEL_NAME,
        'pk_values': self.PK_VALUES
      }
    )
    # POST not successful?
    self.assertEqual(response.status_code, 500)


class OWSProxyTestCase(TestCase):
  OWS_URL_PATH_VALID = '/luftbild_mv-20/tiles/1.0.0/hro.luftbild_mv-20.luftbild_mv-20/' \
                       'GLOBAL_WEBMERCATOR/18/139921/84058.png'
  OWS_URL_PATH_INVALID = '/foobar/wms'

  def init(self):
    self.test_user = User.objects.create_user(
      username=USERNAME,
      password=PASSWORD
    )


class OWSProxyTest(OWSProxyTestCase):

  def setUp(self):
    self.init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_ows_proxy_view_success(self):
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # try GETting an OWS via proxy
    response = self.client.get(reverse('toolbox:owsproxy') + self.OWS_URL_PATH_VALID)
    # GET successful?
    self.assertEqual(response.status_code, 200)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), 'image/png')

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_ows_proxy_view_error(self):
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # try GETting an OWS via proxy
    # but using an invalid URL path
    response = self.client.get(reverse('toolbox:owsproxy') + self.OWS_URL_PATH_INVALID)
    # GET successful?
    self.assertEqual(response.status_code, 200)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), 'text/html')
    # specific string contained in response?
    self.assertIn('nicht vorhanden', str(response.content))


class SearchesTestCase(TestCase):
  ADDRESS_SEARCH_PARAMS = {
    'query': 'Holbeinplatz 14'
  }
  REVERSE_SEARCH_PARAMS = {
    'search_class': 'address',
    'x': 12.09786,
    'y': 54.09303
  }
  CONTAINED_STRING_SUCCESS = 'Reutershagen'
  CONTAINED_STRING_ERROR = 'API key is invalid'

  def init(self):
    self.test_user = User.objects.create_user(
      username=USERNAME,
      password=PASSWORD
    )

  def generic_searches_test(self, url, params, string):
    self.client.login(
      username=USERNAME,
      password=PASSWORD
    )
    # try GETting a search result
    response = self.client.get(reverse(url), params)
    # GET successful?
    self.assertEqual(response.status_code, 200)
    # content type of response as expected?
    self.assertEqual(response['content-type'].lower(), 'application/json')
    # specific string contained in response?
    self.assertIn(string, str(json.loads(response.content)))


class SearchesTest(SearchesTestCase):

  def setUp(self):
    self.init()

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_address_search_view_success(self):
    self.generic_searches_test(
      'toolbox:addresssearch',
      self.ADDRESS_SEARCH_PARAMS,
      self.CONTAINED_STRING_SUCCESS
    )

  @override_settings(ADDRESS_SEARCH_KEY=INVALID_API_KEY)
  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_address_search_view_error(self):
    self.generic_searches_test(
      'toolbox:addresssearch',
      self.ADDRESS_SEARCH_PARAMS,
      self.CONTAINED_STRING_ERROR
    )

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_reverse_search_view_success(self):
    self.generic_searches_test(
      'toolbox:reversesearch',
      self.REVERSE_SEARCH_PARAMS,
      self.CONTAINED_STRING_SUCCESS
    )

  @override_settings(ADDRESS_SEARCH_KEY=INVALID_API_KEY)
  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_reverse_search_view_error(self):
    self.generic_searches_test(
      'toolbox:reversesearch',
      self.REVERSE_SEARCH_PARAMS,
      self.CONTAINED_STRING_ERROR
    )
