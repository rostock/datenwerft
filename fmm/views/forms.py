from django.contrib.gis.forms.fields import PolygonField
from django.forms import ModelForm, ValidationError


class ObjectForm(ModelForm):
  """
  form for instances of an object

  :param required_css_class: CSS class for required field
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)
    # customize messages
    for field in self.fields.values():
      text = 'Das Attribut <strong><em>{}</em></strong> ist Pflicht!'.format(field.label)
      field.error_messages['required'] = text
      if issubclass(field.__class__, PolygonField):
        field.error_messages['required'] = ''
        text = '<strong><em>{}</em></strong> muss in Karte gezeichnet werden!'.format(field.label)
        field.error_messages['invalid_geom'] = text
        field.error_messages['invalid_geom_type'] = text

  def clean(self):
    """
    cleans fields
    """
    cleaned_data = super().clean()
    # clean geometry field, if necessary
    if self._meta.model.BaseMeta.geometry_field is not None:
      geometry_field = self._meta.model.BaseMeta.geometry_field
      geometry = cleaned_data.get(geometry_field)
      if 'EMPTY' in str(geometry):
        raise ValidationError(
          '<strong><em>Flächengeometrie</em></strong> muss in Karte gezeichnet werden!'
        )
      cleaned_data[geometry_field] = geometry
    return cleaned_data
