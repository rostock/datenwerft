from django.apps import apps
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.viewsets import ModelViewSet


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

    def to_representation(self, instance):
      representation = super().to_representation(instance)
      request = self.context.get('request')

      # hide field connection_info of Source and Repository models for anonymous users
      if (model_class.__name__ == 'Source' or model_class.__name__ == 'Repository') and isinstance(
        representation, dict
      ):
        if not request or not request.user or not request.user.is_authenticated:
          representation['connection_info'] = '*** hidden on read-only access ***'

      return representation

  return GenericSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def get_by_uuid(request):
  """
  looks up the model instance by the passed UUID
  and returns an HTTP redirect to the corresponding object's canonical API detail URL

  :param request: request object
  """

  uuid_value = request.GET.get('uuid')
  if not uuid_value:
    return Response(
      data={'detail': 'Pflichtparameter uuid fehlt.'},
      status=status.HTTP_400_BAD_REQUEST,
    )

  for model in apps.get_app_config('gdihrometadata').get_models():
    if not hasattr(model, 'uuid'):
      continue
    try:
      obj = model.objects.get(uuid=uuid_value)
      model_name = model.__name__.lower()
      # construct canonical API detail URL
      obj_api_detail_url = reverse(
        viewname=f'{model_name}-detail',
        kwargs={'pk': f'{obj.pk}'},
      )
      return HttpResponseRedirect(obj_api_detail_url.rstrip('/') + '.json')
    except model.DoesNotExist:
      continue
    except model.MultipleObjectsReturned:
      return JsonResponse(
        data={'detail': f'Mehrere Objekte mit derselben UUID {uuid_value} gefunden.'},
        status=status.HTTP_409_CONFLICT,
      )

  return JsonResponse(
    data={'detail': f'Kein Objekt mit der UUID {uuid_value} gefunden.'},
    status=status.HTTP_404_NOT_FOUND,
  )


# generic viewset using dynamic serializer
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
