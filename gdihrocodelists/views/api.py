from django.apps import apps
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.viewsets import ModelViewSet

from toolbox.utils import is_valid_uuid

from ..models import Codelist, CodelistValue


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

  for model in apps.get_app_config('gdihrocodelists').get_models():
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


@api_view(['GET'])
@permission_classes([AllowAny])
def get_codelistvalue_by_codelist_and_uuid(request, codelist_name, codelistvalue_uuid):
  """
  looks up the CodelistValue model instance by the passed codelist name and UUID
  and returns an HTTP redirect to the corresponding object's canonical API detail URL

  :param request: request object
  :param codelist_name: name of Codelist model instance of corresponding CodelistValue object
  :param codelistvalue_uuid: UUID of corresponding CodelistValue object
  """

  if not is_valid_uuid(codelistvalue_uuid):
    return JsonResponse(
      data={'detail': f'Die angegebene UUID {codelistvalue_uuid} weist kein gültiges Format auf.'},
      status=status.HTTP_400_BAD_REQUEST,
    )

  try:
    codelist = Codelist.objects.get(name=codelist_name)
    try:
      obj = CodelistValue.objects.get(codelist=codelist, uuid=codelistvalue_uuid)
      # construct canonical API detail URL
      obj_api_detail_url = reverse(
        viewname='codelistvalue-detail',
        kwargs={'pk': f'{obj.pk}'},
      )
      return HttpResponseRedirect(f'{obj_api_detail_url.rstrip("/")}.json')
    except CodelistValue.DoesNotExist:
      return JsonResponse(
        data={
          'detail': f'Kein Codelistenwert mit der UUID {codelistvalue_uuid} in der Codeliste {codelist_name} gefunden.'  # noqa: E501
        },
        status=status.HTTP_404_NOT_FOUND,
      )
  except Codelist.DoesNotExist:
    return JsonResponse(
      data={'detail': f'Keine Codeliste mit dem Namen {codelist_name} gefunden.'},
      status=status.HTTP_404_NOT_FOUND,
    )


@api_view(['GET'])
@permission_classes([AllowAny])
def get_codelistvalues_by_codelist(request, codelist_name):
  """
  looks up the Codelist model instance by the passed codelist name
  and returns an HTTP redirect to the CodelistValue model's canonical API list URL
  filtered by the CodelistValue objects associated with the Codelist model instance

  :param request: request object
  :param codelist_name: name of Codelist model instance
  """

  try:
    codelist = Codelist.objects.get(name=codelist_name)
    # construct canonical API list URL
    obj_api_detail_url = reverse(
      viewname='codelistvalue-list',
    )
    return HttpResponseRedirect(
      f'{obj_api_detail_url.rstrip("/")}.json?codelist={str(codelist.pk)}'
    )
  except Codelist.DoesNotExist:
    return JsonResponse(
      data={'detail': f'Keine Codeliste mit dem Namen {codelist_name} gefunden.'},
      status=status.HTTP_404_NOT_FOUND,
    )


class CodelistViewSet(ModelViewSet):
  """
  viewset for model:
  codelist (Codeliste)
  """

  # grant anonymous users read-only (GET) access,
  # while keeping write access (POST, PUT, DELETE, etc.) restricted to authenticated users
  permission_classes = [IsAuthenticatedOrReadOnly]

  def get_queryset(self):
    return self.model.objects.all()

  def get_serializer_class(self):
    return create_serializer_class(self.model)


class CodelistValueViewSet(ModelViewSet):
  """
  viewset for model:
  codelist value (Codelistenwert)
  """

  filter_backends = [DjangoFilterBackend]
  filterset_fields = ['codelist']
  # grant anonymous users read-only (GET) access,
  # while keeping write access (POST, PUT, DELETE, etc.) restricted to authenticated users
  permission_classes = [IsAuthenticatedOrReadOnly]

  def get_queryset(self):
    return self.model.objects.all()

  def get_serializer_class(self):
    return create_serializer_class(self.model)
