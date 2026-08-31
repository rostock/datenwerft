from django.apps import apps
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.serializers import (
  HyperlinkedModelSerializer,
  HyperlinkedRelatedField,
  ManyRelatedField,
)
from rest_framework.viewsets import ModelViewSet

from toolbox.utils import is_valid_uuid


class NullableManyRelatedField(ManyRelatedField):
  """
  returns None instead of [] when the relationship is empty
  """

  def to_representation(self, iterable):
    if not iterable.exists():
      return None

    return super().to_representation(iterable)


class NullableHyperlinkedRelatedField(HyperlinkedRelatedField):
  """
  HyperlinkedRelatedField which uses NullableManyRelatedField when many=True
  """

  many_init = classmethod(
    lambda cls, *args, **kwargs: NullableManyRelatedField(child_relation=cls(*args, **kwargs))
  )


def create_serializer_class(model_class):
  """
  creates a dynamic serializer for any model and returns it

  :param model_class: model class
  :return: dynamic serializer for any model
  """

  class GenericSerializer(HyperlinkedModelSerializer):
    class Meta:
      model = model_class
      fields = '__all__'

    def get_fields(self):
      fields = super().get_fields()
      for relation in model_class._meta.related_objects:
        field_name = relation.get_accessor_name()
        # don't add it if DRF already knows about it
        if field_name in fields:
          continue
        related_model = relation.related_model
        view_name = f'{related_model._meta.model_name}-detail'
        # reverse M2M or reverse FK
        if relation.many_to_many or relation.one_to_many:
          fields[field_name] = NullableHyperlinkedRelatedField(
            many=True,
            read_only=True,
            view_name=view_name,
          )
        # reverse OneToOne
        elif relation.one_to_one:
          fields[field_name] = NullableHyperlinkedRelatedField(
            read_only=True,
            view_name=view_name,
          )
      return fields

    def to_representation(self, instance):
      representation = super().to_representation(instance)
      request = self.context.get('request')

      # hide field connection_info of Source and Repository models for anonymous users
      if model_class.__name__ in ('Repository', 'Source') and isinstance(representation, dict):
        if not request or not request.user or not request.user.is_authenticated:
          representation['connection_info'] = '*** hidden on read-only access ***'

      return representation

  return GenericSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_by_uuid(request, uuid):
  """
  looks up the model instance by the passed UUID
  and returns an HTTP redirect to the corresponding object's canonical API detail URL

  :param request: request object
  :param uuid: UUID of corresponding object
  """

  if not is_valid_uuid(uuid):
    return JsonResponse(
      data={'detail': f'Die angegebene UUID {uuid} weist kein gültiges Format auf.'},
      status=status.HTTP_400_BAD_REQUEST,
    )

  for model in apps.get_app_config('gdihrometadata').get_models():
    if not hasattr(model, 'uuid'):
      continue
    try:
      obj = model.objects.get(uuid=uuid)
      model_name = model.__name__.lower()
      # construct canonical API detail URL
      obj_api_detail_url = reverse(
        viewname=f'{model_name}-detail',
        kwargs={'pk': f'{obj.pk}'},
      )
      return HttpResponseRedirect(f'{obj_api_detail_url.rstrip("/")}.json')
    except model.DoesNotExist:
      continue

  return JsonResponse(
    data={'detail': f'Kein Objekt mit der UUID {uuid} gefunden.'},
    status=status.HTTP_404_NOT_FOUND,
  )


class GenericModelViewSet(ModelViewSet):
  """
  generic viewset using dynamic serializer that gets replaced dynamically for each model
  """

  # grant anonymous users read-only (GET) access,
  # while keeping write access (POST, PUT, DELETE, etc.) restricted to authenticated users
  permission_classes = [IsAuthenticatedOrReadOnly]

  def get_queryset(self):
    return self.model.objects.all()

  def get_serializer_class(self):
    return create_serializer_class(self.model)
