from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.viewsets import ModelViewSet


class DatenmanagementViewSet(ModelViewSet):
  model = None

  @classmethod
  def create_custom(cls, **kwargs):
    class CustomViewSet(cls):
      model = kwargs['model']
      queryset = kwargs['model'].objects.all()

    return CustomViewSet

  def get_serializer_class(self):
    if self.serializer_class is not None:
      return self.serializer_class

    class DatenmanagementSerializer(HyperlinkedModelSerializer):
      class Meta:
        model = self.model
        fields = '__all__'

    self.serializer_class = DatenmanagementSerializer
    return self.serializer_class
