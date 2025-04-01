from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers


class PermissionSerializer(serializers.HyperlinkedModelSerializer):
  url = serializers.HyperlinkedIdentityField(
    view_name='permission-detail', lookup_field='codename'
  )
  content_type = serializers.HyperlinkedRelatedField(
    view_name='contenttype-detail',
    lookup_field='model',
    many=False,
    read_only=True,
  )

  class Meta:
    model = Permission
    fields = '__all__'


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
    fields = '__all__'


class ContentTypeSerializer(serializers.HyperlinkedModelSerializer):
  class Meta:
    model = ContentType
    lookup_field = 'model'
    fields = '__all__'
