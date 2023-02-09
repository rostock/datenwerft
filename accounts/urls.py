from django.urls import path
from django.contrib.auth.views import LogoutView
from rest_framework import routers
from django.views.generic import TemplateView

from .views import ContentTypeViewSet, GroupViewSet, PermissionViewSet, UserViewSet, \
  ExternalLoginView, PreLoginView

router = routers.DefaultRouter()
router.register(prefix=r'user', viewset=UserViewSet)
router.register(prefix=r'group', viewset=GroupViewSet)
router.register(prefix=r'permission', viewset=PermissionViewSet)
router.register(prefix=r'content_type', viewset=ContentTypeViewSet)

api_urlpatterns = router.urls

app_name = 'accounts'
urlpatterns = [
  path('login/', PreLoginView.as_view(
    template_name='accounts/login.html',
    redirect_authenticated_user=True
  ), name='login'),

  path('login/<url_token>', ExternalLoginView.as_view(), name='external_login'),

  path('logout/', view=LogoutView.as_view(template_name='accounts/logout.html'), name='logout'),

  path('test', view=TemplateView.as_view(template_name='accounts/test.html'), name='test'),
]
