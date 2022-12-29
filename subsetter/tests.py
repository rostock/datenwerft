import random
import uuid

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from .models import Subsets


class SubsetsTestCase(TestCase):
  PK_FIELD = 'uuid'
  PK_1 = '42'
  PK_2 = str(uuid.uuid4())
  PK_3 = 'foobar'

  def init(self):
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
    # ID of object created exactly equals '1'?
    self.assertEqual(str(subset), '1')
    # object created contains certain value in one of its fields?
    self.assertEqual(Subsets.objects.filter(pks__contains=[self.PK_2]).count(), 1)
