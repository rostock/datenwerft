from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.viewsets import ModelViewSet


# create a dynamic serializer for any model
def create_serializer_class(model_class):
  class GenericSerializer(HyperlinkedModelSerializer):
    class Meta:
      model = model_class
      fields = '__all__'
  return GenericSerializer

# generic viewset using dynamic serializer
class GenericModelViewSet(ModelViewSet):
  """
  default viewset that gets replaced dynamically for each model
  """
  def get_queryset(self):
    return self.model.objects.all()

  def get_serializer_class(self):
    return create_serializer_class(self.model)
