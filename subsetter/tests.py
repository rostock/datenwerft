import json
import random
import uuid

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Subsets


class SubsetsTestCase(TestCase):
  USERNAME = 'foobar'
  PASSWORD = 'secret42'
  APP_LABEL = 'contenttypes'
  MODEL = 'contenttype'
  PK_FIELD = 'uuid'
  PKS = '["42", "3e029807-86de-4ac0-aea3-9cd1c6db45a3", "foobar"]'
  PK_1 = '42'
  PK_2 = str(uuid.uuid4())
  PK_3 = 'foobar'

  def init(self):
    self.test_user = User.objects.create_user(
      username=self.USERNAME,
      password=self.PASSWORD,
    )
    self.content_types = list(ContentType.objects.all())
    self.random_content_type = random.choice(self.content_types)
    self.subset = Subsets.objects.create(
      model=self.random_content_type,
      pk_field=self.PK_FIELD,
      pks=[
        self.PK_1,
        self.PK_2,
        self.PK_3
      ]
    )


class SubsetsTest(SubsetsTestCase):

  def setUp(self):
    self.init()

  def test_create(self):
    # exactly one object created?
    self.assertEqual(Subsets.objects.all().count(), 1)
    # object created exactly as it should have been created?
    subset = Subsets.objects.get(pk_field=self.PK_FIELD)
    self.assertEqual(subset, self.subset)
    # object created contains specific value in one of its fields?
    self.assertEqual(Subsets.objects.filter(pks__contains=[self.PK_2]).count(), 1)

  @override_settings(AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'])
  def test_add_view(self):
    self.client.login(
      username=self.USERNAME,
      password=self.PASSWORD
    )
    response = self.client.post(
      reverse('subsetter:add'),
      data={
        'app_label': self.APP_LABEL,
        'model': self.MODEL,
        'pk_field': self.PK_FIELD,
        'pks': self.PKS
      }
    )
    self.assertEqual(response.status_code, 200)
    response_json = json.loads(response.content.decode('utf-8'))
    response_dict = json.loads(response_json)
    self.assertIsNotNone(response_dict['id'])
