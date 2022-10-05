from django.apps import apps
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth.models import User, Permission, Group, ContentType
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, re_path
from django.views.generic import RedirectView
from guardian.models import UserObjectPermission, GroupObjectPermission
from rest_framework import routers, serializers, viewsets


#
# Definition von Serializer-Klassen mit Feldern passend zu den Models
#
class PermissionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='permission-detail',
        lookup_field='codename'
    )
    content_type = serializers.HyperlinkedRelatedField(
        view_name='contenttype-detail',
        lookup_field='model',
        many=False,
        read_only=True,
    )

    class Meta:
        model = Permission


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name='user-detail')
    user_permissions = serializers.HyperlinkedRelatedField(
        view_name='permission-detail',
        lookup_field='codename',
        many=True,
        read_only=True,
    )

    class Meta:
        model = User
        exclude = ('password',)


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    permissions = serializers.HyperlinkedRelatedField(
        view_name='permission-detail',
        lookup_field='codename',
        many=True,
        read_only=True,
    )

    class Meta:
        model = Group


class ContentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ContentType
        lookup_field = 'model'


class UserObjectPermissionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='userobjectpermission-detail'
    )
    content_type = serializers.HyperlinkedRelatedField(
        view_name='contenttype-detail',
        lookup_field='model',
        many=False,
        read_only=True,
    )
    user = serializers.HyperlinkedRelatedField(
        view_name='user-detail',
        many=False,
        read_only=True
    )
    permission = serializers.HyperlinkedRelatedField(
        view_name='permission-detail',
        lookup_field='codename',
        many=False,
        read_only=True,
    )

    class Meta:
        model = UserObjectPermission


class GroupObjectPermissionSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(
        view_name='groupobjectpermission-detail'
    )
    content_type = serializers.HyperlinkedRelatedField(
        view_name='contenttype-detail',
        lookup_field='model',
        many=False,
        read_only=True,
    )
    group = serializers.HyperlinkedRelatedField(
        view_name='group-detail',
        many=False,
        read_only=True
    )
    permission = serializers.HyperlinkedRelatedField(
        view_name='permission-detail',
        lookup_field='codename',
        many=False,
        read_only=True,
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

        class DatenmanagementSerializer(
                serializers.HyperlinkedModelSerializer):
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


# Dient zum Routen der Anfragen Abhängig von beispielsweise Nutzergruppen und
# Berechtigungen
router = routers.DefaultRouter()
router.register(prefix=r'user', viewset=UserViewSet)
router.register(prefix=r'group', viewset=GroupViewSet)
router.register(prefix=r'permission', viewset=PermissionViewSet)
router.register(prefix=r'content_type', viewset=ContentTypeViewSet)
router.register(prefix=r'user_object_permission',
                viewset=UserObjectPermissionViewSet)
router.register(prefix=r'group_object_permission',
                viewset=GroupObjectPermissionViewSet)


app_models = apps.get_app_config('datenmanagement').get_models()
for model in app_models:
    modelname = model.__name__.lower()
    router.register(
        modelname,
        DatenmanagementViewSet.create_custom(model=model),
        basename=modelname
    )

# Routen der URLs zu Views
urlpatterns = [
    # '' -> Redirect auf 'datenwerft/datenmanagement'
    re_path(route=r'^$',
        view=RedirectView.as_view(url='/datenwerft/datenmanagement')),
    # 'admin/' -> Django Adminpanel
    re_path(route=r'^admin/',
        view=admin.site.urls),
    # Einloggen: 'accounts/login'
    # mit Redirect für angemeldete Nutzer
    re_path(route=r'^accounts/login/$',
        view=LoginView.as_view(
            template_name='_registration/login.html',
            redirect_authenticated_user=True
        ),
        name='login'),
    # Ausloggen: 'accounts/logout/'
    re_path(route=r'^accounts/logout/$',
        view=LogoutView.as_view(template_name='_registration/logout.html'),
        name='logout'),
    # Routen von Api URLs
    re_path(route=r'^api/',
        view=include(router.urls)),
    # Routen der Api Authentifizierung
    re_path(route=r'^api-auth/',
        view=include('rest_framework.urls')),
    # 'datenmanagement' -> Datenmanagement App
    re_path(route=r'^datenmanagement/',
        view=include('datenmanagement.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
