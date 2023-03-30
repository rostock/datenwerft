from django.forms import ModelForm


class CodelistForm(ModelForm):
  """
  form for a codelist instance
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)
    # customize messages
    for field in self.fields.values():
      required_message = 'Das Attribut <strong><em>{label}</em></strong> ' \
                         'ist Pflicht!'.format(label=field.label)
      unique_message = 'Es existiert bereits ein Codelisteneintrag mit dem angegebenen Wert ' \
                       'im Attribut <strong><em>{label}</em></strong>!'.format(label=field.label)
      field.error_messages = {
        'required': required_message,
        'unique': unique_message
      }


class GenericObjectclassForm(ModelForm):
  """
  generic form for an instance of an object class
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)
    # customize messages
    for field in self.fields.values():
      required_message = 'Das Attribut <strong><em>{label}</em></strong> ' \
                         'ist Pflicht!'.format(label=field.label)
      unique_message = 'Es existiert bereits ein(e) ' + self._meta.model._meta.verbose_name +\
                       ' mit dem angegebenen Wert im Attribut <strong><em>{label}' \
                       '</em></strong>!'.format(label=field.label)
      field.error_messages = {
        'required': required_message,
        'unique': unique_message
      }
