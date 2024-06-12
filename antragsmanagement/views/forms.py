from django.forms import ModelForm, ValidationError

from antragsmanagement.models import GeometryObject


class GenericObjectForm(ModelForm):
  """
  generic form for instances of general objects
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)
    # customize messages
    for field in self.fields.values():
      required_message = 'Das Attribut <strong><em>{}</em></strong> ' \
                         'ist Pflicht!'.format(field.label)
      field.error_messages = {
        'required': required_message
      }

  def clean(self):
    """
    cleans fields
    """
    cleaned_data = super().clean()
    # if object class contains geometry:
    # clean geometry fields
    if issubclass(self._meta.model, GeometryObject):
      geometry_field = self._meta.model.BaseMeta.geometry_field
      geometry = cleaned_data.get(geometry_field)
      error_text = 'Es muss ein Marker in der Karte gesetzt werden!'
      if '(0 0)' in str(geometry):
        raise ValidationError(error_text)
      else:
        cleaned_data[geometry_field] = geometry
