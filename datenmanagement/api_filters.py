import django_filters
from .models import Punktwolken, Punktwolken_Projekte, Angelverbotsbereiche # Hinzufügen von Angelverbotsbereiche

class PunktwolkenFilter(django_filters.FilterSet):
  projekt = django_filters.ModelChoiceFilter(
    queryset=Punktwolken_Projekte.objects.all(),
    field_name='projekt',
    to_field_name='uuid'  # Oder der entsprechende Feldname in Punktwolken_Projekte
  )

  class Meta:
    model = Punktwolken
    fields = ['projekt']
