from django.contrib.auth.views import LogoutView, PasswordChangeDoneView
from django.urls import path
from django.views.generic import TemplateView
from rest_framework import routers

from .views import (
  ContentTypeViewSet,
  ExternalLoginView,
  GroupViewSet,
  LocalUserPasswordChangeView,
  PermissionViewSet,
  PreLoginView,
  UserViewSet,
)

router = routers.DefaultRouter()
router.register(prefix=r'user', viewset=UserViewSet)
router.register(prefix=r'group', viewset=GroupViewSet)
router.register(prefix=r'permission', viewset=PermissionViewSet)
router.register(prefix=r'content_type', viewset=ContentTypeViewSet)

api_urlpatterns = router.urls

app_name = 'accounts'


urlpatterns = [
  path(
    route='login/',
    view=PreLoginView.as_view(
      template_name='accounts/login.html', redirect_authenticated_user=True
    ),
    name='login',
  ),
  path(route='login/<url_token>', view=ExternalLoginView.as_view(), name='external_login'),
  path(
    route='logout/', view=LogoutView.as_view(template_name='accounts/logout.html'), name='logout'
  ),
  path(route='test', view=TemplateView.as_view(template_name='accounts/test.html'), name='test'),
  path(
    route='password-change/',
    view=LocalUserPasswordChangeView.as_view(),
    name='password_change',
  ),
  path(
    route='password-change/done/',
    view=PasswordChangeDoneView.as_view(template_name='accounts/password_change_done.html'),
    name='password_change_done',
  ),
]
