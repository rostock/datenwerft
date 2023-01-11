from django.contrib.auth.models import User
from django.test import TestCase

from . import constants_vars


class DefaultModelTestCase(TestCase):
  databases = constants_vars.DATABASES

  def init(self):
    self.test_user = User.objects.create_user(
      username=constants_vars.USERNAME,
      password=constants_vars.PASSWORD
    )
