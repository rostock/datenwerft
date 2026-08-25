from django.contrib.auth.views import (
  LogoutView,
  PasswordResetCompleteView,
  PasswordResetConfirmView,
  PasswordResetDoneView,
  PasswordResetView,
)
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from rest_framework import routers

from .views import (
  ContentTypeViewSet,
  ExternalLoginView,
  GroupViewSet,
  PermissionViewSet,
  PreLoginView,
  UserSettingsView,
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
    route='password-reset/',
    view=PasswordResetView.as_view(
      template_name='accounts/password_reset.html',
      email_template_name='accounts/password_reset_email.txt',
      subject_template_name='accounts/password_reset_email_subject.txt',
      html_email_template_name='accounts/password_reset_email.html',
      success_url=reverse_lazy('accounts:password_reset_done'),
    ),
    name='password_reset',
  ),
  path(
    route='password-reset/sent/',
    view=PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
    name='password_reset_done',
  ),
  path(
    route='password-reset/confirm/<uidb64>/<token>/',
    view=PasswordResetConfirmView.as_view(
      template_name='accounts/password_reset_confirm.html',
      success_url=reverse_lazy('accounts:password_reset_complete'),
    ),
    name='password_reset_confirm',
  ),
  path(
    route='password-reset/complete/',
    view=PasswordResetCompleteView.as_view(
      template_name='accounts/password_reset_complete.html'
    ),
    name='password_reset_complete',
  ),
  path(
    route='settings/',
    view=UserSettingsView.as_view(),
    name='settings',
  ),
]
