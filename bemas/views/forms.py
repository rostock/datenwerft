from django.contrib.postgres.fields.array import ArrayField
from django.forms import ModelForm

from bemas.models import Codelist


class GenericForm(ModelForm):
  """
  generic form
  """

  required_css_class = 'required'

  def __init__(self, *args, **kwargs):
    kwargs.setdefault('label_suffix', '')
    super().__init__(*args, **kwargs)
    # customize messages
    for field in self.fields.values():
      required_message = 'Das Attribut <strong><em>{label}</em></strong> ' \
                         'ist Pflicht!'.format(label=field.label)
      if issubclass(self._meta.model, Codelist):
        title = 'ein Codelisteneintrag'
      else:
        title = self._meta.model.BasemodelMeta.indefinite_article + ' ' + \
                self._meta.model._meta.verbose_name
      item_invalid_message = 'Der Wert an Stelle %(nth)s im Attribut ' \
                             '<strong><em>ATTRIBUTE</em></strong> war ungültig! ' \
                             'Daher wurde das gesamte Attribut zurückgesetzt. Hinweis:'
      ArrayField.default_error_messages['item_invalid'] = item_invalid_message
      unique_message = 'Es existiert bereits ' + title + ' mit dem angegebenen Wert im Attribut' \
                       ' <strong><em>{label}</em></strong>!'.format(label=field.label)
      field.error_messages = {
        'required': required_message,
        'unique': unique_message
      }
