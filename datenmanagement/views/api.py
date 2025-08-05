from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.viewsets import ModelViewSet

from ..api_filters import PunktwolkenFilter
from ..models import Punktwolken


class DatenmanagementViewSet(ModelViewSet):
  model = None
  # add filterset_class attribute
  filterset_class = None

  @classmethod
  def create_custom(cls, **kwargs):
    _model = kwargs['model']
    # initialize filterset_class here to avoid scope problems
    _filterset_class = None
    if _model == Punktwolken:
      _filterset_class = PunktwolkenFilter

    class CustomViewSet(cls):
      model = _model
      queryset = _model.objects.all()
      # assign initialized variable
      filterset_class = _filterset_class

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
