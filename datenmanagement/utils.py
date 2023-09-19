from django.contrib.gis.db.models.fields import LineStringField as ModelLineStringField
from django.contrib.gis.db.models.fields import MultiLineStringField as ModelMultiLineStringField
from django.contrib.gis.db.models.fields import MultiPolygonField as ModelMultiPolygonField
from django.contrib.gis.db.models.fields import PointField as ModelPointField
from django.contrib.gis.db.models.fields import PolygonField as ModelPolygonField
from django.contrib.gis.forms.fields import LineStringField as FormLineStringField
from django.contrib.gis.forms.fields import MultiLineStringField as FormMultiLineStringField
from django.contrib.gis.forms.fields import MultiPolygonField as FormMultiPolygonField
from django.contrib.gis.forms.fields import PointField as FormPointField
from django.contrib.gis.forms.fields import PolygonField as FormPolygonField


def is_geometry_field(field):
  """
  checks if passed field is a geometry related field

  :param field: field
  :return: passed field is a geometry related field?
  """
  if (
      issubclass(field, FormLineStringField)
      or issubclass(field, ModelLineStringField)
      or issubclass(field, FormMultiLineStringField)
      or issubclass(field, ModelMultiLineStringField)
      or issubclass(field, FormMultiPolygonField)
      or issubclass(field, ModelMultiPolygonField)
      or issubclass(field, FormPointField)
      or issubclass(field, ModelPointField)
      or issubclass(field, FormPolygonField)
      or issubclass(field, ModelPolygonField)
  ):
    return True
  else:
    return False
