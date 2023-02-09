from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.urls import path
from rest_framework import routers

from .views.views import IndexView

router = routers.DefaultRouter()

api_urlpatterns = router.urls

app_name = 'bemas'


def is_bemas_user():
  """
  checks if a user is a BEMAS user (or an admin)

  :return: user is a BEMAS user (or an admin)?
  """
  return user_passes_test(
    lambda u: u.groups.filter(
      name__in=[settings.BEMAS_ADMIN_GROUP_NAME, settings.BEMAS_USERS_GROUP_NAME]
    ) or u.is_superuser,
    login_url='/',
    redirect_field_name=None
  )


urlpatterns = [
  # IndexView:
  # main page
  path(
    '',
    view=is_bemas_user()(IndexView.as_view()),
    name='index'
  )
]
