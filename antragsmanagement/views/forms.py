from django.forms import ModelForm, ValidationError
from django.forms.fields import EmailField

from antragsmanagement.models import GeometryObject
from toolbox.constants_vars import email_message


class ObjectForm(ModelForm):
  """
  generic form for instances of general objects
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)
    # customize messages
    for field in self.fields.values():
      field.error_messages['required'] = 'Das Attribut <strong><em>{}</em></strong> ' \
                                         'ist Pflicht!'.format(field.label)
      if issubclass(field.__class__, EmailField):
        field.error_messages['invalid'] = email_message

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
