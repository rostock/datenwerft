from django.db.models.fields import TextField
from django.forms import Textarea


class NullTextField(TextField):
  """
  TextField writing NULL values to database instead of empty strings
  """

  def get_internal_type(self):
    return 'TextField'

  def to_python(self, value):
    if value is None or value in self.empty_values:
      return None
    elif isinstance(value, str):
      return value
    return str(value)

  def get_prep_value(self, value):
    value = super(NullTextField, self).get_prep_value(value)
    return self.to_python(value)

  def formfield(self, **kwargs):
    defaults = {
      'max_length': self.max_length,
      **({} if self.choices is not None else {'widget': Textarea})
    }
    defaults.update(kwargs)
    return super().formfield(**defaults)
