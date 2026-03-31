from .constant_vars import DATABASES, PASSWORD, USERNAME


class DefaultTestCase(TestCase):
  """
  default abstract test class
  """

  databases = DATABASES

  def init(self):
    self.test_user = User.objects.create_user(username=USERNAME, password=PASSWORD)
