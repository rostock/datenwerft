from django.forms import ModelForm, ValidationError
from django.forms.fields import EmailField

from antragsmanagement.models import GeometryObject, CodelistRequestStatus, Requester
from antragsmanagement.utils import get_corresponding_requester
from toolbox.constants_vars import email_message


#
# general objects
#

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


class RequestForm(ObjectForm):
  """
  form for instances of general object:
  request (Antrag)
  """

  def __init__(self, *args, **kwargs):
    self.user = kwargs.pop('user', None)
    super().__init__(*args, **kwargs)
    # limit the status field queryset to exactly one entry (= default status)
    self.fields['status'].queryset = CodelistRequestStatus.get_status_new(as_queryset=True)
    # limit the requester field queryset to exactly one entry (= user)
    user = get_corresponding_requester(self.user, only_primary_key=False)
    self.fields['requester'].queryset = user if user else Requester.objects.order_by('-id')[:1]


class RequestFollowUpForm(ObjectForm):
  """
  form for follow-up instances of general object:
  request (Antrag)
  """

  def __init__(self, *args, **kwargs):
    self.request_field = kwargs.pop('request_field', None)
    self.request_object = kwargs.pop('request_object', None)
    super().__init__(*args, **kwargs)
    # limit the request field queryset to exactly one entry (= corresponding request)
    self.fields[self.request_field].queryset = self.request_object
