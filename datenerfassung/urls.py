"""datenerfassung URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
  https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
  1. Add an import:  from my_app import views
  2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
  1. Add an import:  from other_app.views import Home
  2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
  1. Import the include() function: from django.urls import include, path
  2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.apps import apps
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.models import User, Permission, Group, ContentType
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import RedirectView
from guardian.models import UserObjectPermission, GroupObjectPermission
from rest_framework import routers, serializers, viewsets


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
  url = serializers.HyperlinkedIdentityField(view_name = 'permission-detail', lookup_field = 'codename')
  content_type = serializers.HyperlinkedRelatedField(
    view_name = 'contenttype-detail',
    lookup_field = 'model',
    many = False,
    read_only = True,
  )
  class Meta:
    model = Permission


class UserSerializer(serializers.HyperlinkedModelSerializer):
  url = serializers.HyperlinkedIdentityField(view_name = 'user-detail')
  user_permissions = serializers.HyperlinkedRelatedField(
    view_name = 'permission-detail',
    lookup_field = 'codename',
    many = True,
    read_only = True,
  )
  class Meta:
    model = User
    exclude = ('password',)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
  permissions = serializers.HyperlinkedRelatedField(
    view_name = 'permission-detail',
    lookup_field = 'codename',
    many = True,
    read_only = True,
  )
  class Meta:
    model = Group


class ContentTypeSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = ContentType
    lookup_field = 'model'


class UserObjectPermissionSerializer(serializers.HyperlinkedModelSerializer):
  url = serializers.HyperlinkedIdentityField(view_name = 'userobjectpermission-detail')
  content_type = serializers.HyperlinkedRelatedField(
    view_name = 'contenttype-detail',
    lookup_field = 'model',
    many = False,
    read_only = True,
  )
  user = serializers.HyperlinkedRelatedField(view_name = 'user-detail', many = False, read_only = True)
  permission = serializers.HyperlinkedRelatedField(
    view_name = 'permission-detail',
    lookup_field = 'codename',
    many = False,
    read_only = True,
  )
  class Meta:
    model = UserObjectPermission


class GroupObjectPermissionSerializer(serializers.HyperlinkedModelSerializer):
  url = serializers.HyperlinkedIdentityField(view_name = 'groupobjectpermission-detail')
  content_type = serializers.HyperlinkedRelatedField(
    view_name = 'contenttype-detail',
    lookup_field = 'model',
    many = False,
    read_only = True,
  )
  group = serializers.HyperlinkedRelatedField(view_name = 'group-detail', many = False, read_only = True)
  permission = serializers.HyperlinkedRelatedField(
    view_name = 'permission-detail',
    lookup_field = 'codename',
    many = False,
    read_only = True,
  )
  class Meta:
    model = GroupObjectPermission


class DatenmanagementViewSet(viewsets.ModelViewSet):
  @classmethod
  def create_custom(cls, **kwargs):
    class CustomViewSet(cls):
      model = kwargs["model"]
      queryset = kwargs["model"].objects.all()
    return CustomViewSet

  def get_serializer_class(self):
    if self.serializer_class is not None:
      return self.serializer_class
    class DatenmanagementSerializer(serializers.HyperlinkedModelSerializer):
      class Meta:
        model = self.model
    self.serializer_class = DatenmanagementSerializer
    return self.serializer_class


class PermissionViewSet(viewsets.ModelViewSet):
  queryset = Permission.objects.all()
  serializer_class = PermissionSerializer
  lookup_field = 'codename'


class UserViewSet(viewsets.ModelViewSet):
  queryset = User.objects.all()
  serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
  queryset = Group.objects.all()
  serializer_class = GroupSerializer


class ContentTypeViewSet(viewsets.ModelViewSet):
  queryset = ContentType.objects.all()
  serializer_class = ContentTypeSerializer
  lookup_field = 'model'


class UserObjectPermissionViewSet(viewsets.ModelViewSet):
  queryset = UserObjectPermission.objects.all()
  serializer_class = UserObjectPermissionSerializer


class GroupObjectPermissionViewSet(viewsets.ModelViewSet):
  queryset = GroupObjectPermission.objects.all()
  serializer_class = GroupObjectPermissionSerializer


router = routers.DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'group', GroupViewSet)
router.register(r'permission', PermissionViewSet)
router.register(r'content_type', ContentTypeViewSet)
router.register(r'user_object_permission', UserObjectPermissionViewSet)
router.register(r'group_object_permission', GroupObjectPermissionViewSet)


app_models = apps.get_app_config('datenmanagement').get_models()
for model in app_models:
  modelname = model.__name__.lower()
  router.register(modelname, DatenmanagementViewSet.create_custom(model = model), basename = modelname)


urlpatterns = [
  url(r'^$', RedirectView.as_view(url = '/datenerfassung/datenmanagement')),
  url(r'^admin/', admin.site.urls),
  url(r'^accounts/login/$', LoginView.as_view(template_name = '_registration/login.html', redirect_authenticated_user = True), name = 'login'),
  url(r'^accounts/logout/$', LogoutView.as_view(template_name = '_registration/logout.html'), name = 'logout'),
  url(r'^api/', include(router.urls)),
  url(r'^api-auth/', include('rest_framework.urls')),
  url(r'^datenmanagement/', include('datenmanagement.urls')),
]
