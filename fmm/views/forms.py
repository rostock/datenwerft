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
      required_message = 'Das Attribut <strong><em>{}</em></strong> ist Pflicht!'.format(
        field.label
      )
      unique_message = '{} mit angegebenem Wert im Attribut <strong><em>{}</em></strong>'.format(
        self._meta.model._meta.verbose_name, field.label
      )
      unique_message += ' existiert bereits!'
      field.error_messages = {'required': required_message, 'unique': unique_message}
      if issubclass(field.__class__, PolygonField):
        required_message = '<strong><em>{}</em></strong> muss in Karte gezeichnet werden!'.format(
          field.label
        )
        field.error_messages = {
          'required': '',
          'invalid_geom': required_message,
          'invalid_geom_type': required_message,
        }

  def clean(self):
    """
    cleans fields
    """
    cleaned_data = super().clean()
    # clean geometry field, if necessary
    if self._meta.model.BaseMeta.geometry_field is not None:
      geometry_field_name = self._meta.model.BaseMeta.geometry_field
      geometry = cleaned_data.get(geometry_field_name)
      if 'EMPTY' in str(geometry):
        geometry_field = self.fields[geometry_field_name]
        raise ValidationError(
          '<strong><em>{}</em></strong> muss in Karte gezeichnet werden!'.format(
            geometry_field.label
          )
        )
      cleaned_data[geometry_field_name] = geometry
    return cleaned_data
