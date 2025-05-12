from rest_framework.serializers import HyperlinkedModelSerializer
from rest_framework.viewsets import ModelViewSet
from ..models import Punktwolken, Angelverbotsbereiche  # Import Punktwolken and Angelverbotsbereiche
from ..api_filters import PunktwolkenFilter, AngelverbotsbereicheFilter  # Import PunktwolkenFilter and AngelverbotsbereicheFilter


class DatenmanagementViewSet(ModelViewSet):
  model = None
  filterset_class = None  # Add filterset_class attribute

  @classmethod
  def create_custom(cls, **kwargs):
    _model = kwargs['model']
    # Initialisiere filterset_class hier, um Scope-Probleme zu vermeiden
    _filterset_class = None
    if _model == Punktwolken:
      _filterset_class = PunktwolkenFilter
    elif _model == Angelverbotsbereiche:
      _filterset_class = AngelverbotsbereicheFilter

    class CustomViewSet(cls):
      model = _model
      queryset = _model.objects.all()
      filterset_class = _filterset_class # Weise die initialisierte Variable zu

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
