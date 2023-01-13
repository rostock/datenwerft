from django.contrib.auth.models import User
from django.test import TestCase

from .constants_vars import *


class DefaultTestCase(TestCase):
  databases = DATABASES

  def init(self):
    self.test_user = User.objects.create_user(
      username=USERNAME,
      password=PASSWORD
    )
