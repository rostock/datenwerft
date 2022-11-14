from django.urls import path, reverse_lazy
from django.contrib.auth.views import LogoutView
from rest_framework import routers
from accounts import views
from django.views.generic import TemplateView

router = routers.DefaultRouter()
router.register(prefix=r'user', viewset=views.UserViewSet)
router.register(prefix=r'group', viewset=views.GroupViewSet)
router.register(prefix=r'permission', viewset=views.PermissionViewSet)
router.register(prefix=r'content_type', viewset=views.ContentTypeViewSet)
router.register(prefix=r'user_object_permission',
                viewset=views.UserObjectPermissionViewSet)
router.register(prefix=r'group_object_permission',
                viewset=views.GroupObjectPermissionViewSet)

api_urlpatterns = router.urls

app_name = 'accounts'
urlpatterns = [
  path('login/', views.PreLoginView.as_view(
    template_name='accounts/login.html',
    redirect_authenticated_user=True
  ), name='login'),

  path('login/<url_token>', views.ExternalLoginView.as_view(), name='external_login'),

  path('logout/', view=LogoutView.as_view(
    template_name='accounts/logout.html'
  ), name='logout'),

  path('test', view=TemplateView.as_view(
    template_name='accounts/test.html'
  ), name='test'),
]
