from django.forms import ModelForm


class MetadataForm(ModelForm):
  """
  generic form for instances of a metadata model class

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
