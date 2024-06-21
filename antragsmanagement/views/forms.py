from django.contrib.gis.forms.fields import PointField, PolygonField
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
      if issubclass(field.__class__, EmailField):
        field.error_messages['invalid'] = email_message
      elif issubclass(field.__class__, PointField) or issubclass(field.__class__, PolygonField):
        field.error_messages['required'] = None
        if issubclass(field.__class__, PointField):
          text = 'Marker für <strong><em>{}</em></strong> muss in Karte gesetzt werden!'.format(
            field.label)
        else:
          text = '<strong><em>{}</em></strong> muss in Karte gezeichnet werden!'.format(
            field.label)
        field.error_messages['invalid_geom'] = text
        field.error_messages['invalid_geom_type'] = text

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
      if '(0 0)' in str(geometry):
        text = 'Marker für <strong><em>{}</em></strong> muss in Karte gesetzt werden!'.format(
          self._meta.model._meta.get_field(geometry_field).verbose_name)
        raise ValidationError(text)
      else:
        cleaned_data[geometry_field] = geometry


class RequesterForm(ObjectForm):
  """
  form for creating or updating an instance of general object:
  requester (Antragsteller:in)
  """

  def clean_last_name(self):
    """
    cleans specific field
    """
    organization = self.cleaned_data.get('organization')
    first_name = self.cleaned_data.get('first_name')
    last_name = self.cleaned_data.get('last_name')
    if not organization and not first_name and not last_name:
      text = '<strong><em>{}</em></strong> muss gesetzt sein,'.format(
        self._meta.model._meta.get_field('organization').verbose_name)
      text += ' wenn <em>{}</em> und <em>{}</em> nicht gesetzt sind!'.format(
        self._meta.model._meta.get_field('first_name').verbose_name,
        self._meta.model._meta.get_field('last_name').verbose_name)
      text += ' <strong><em>{}</em></strong> und <strong><em>{}</em></strong>'.format(
        self._meta.model._meta.get_field('first_name').verbose_name,
        self._meta.model._meta.get_field('last_name').verbose_name)
      text += ' müssen gesetzt sein, wenn <em>{}</em> nicht gesetzt ist!'.format(
        self._meta.model._meta.get_field('organization').verbose_name)
      raise ValidationError(text)
    elif (not first_name and last_name) or (first_name and not last_name):
      text = '<strong><em>{}</em></strong> und <strong><em>{}</em></strong>'.format(
        self._meta.model._meta.get_field('first_name').verbose_name,
        self._meta.model._meta.get_field('last_name').verbose_name)
      text += ' müssen immer gemeinsam gesetzt sein!'
      raise ValidationError(text)
    return last_name


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
    if self.request_field and self.request_object:
      self.fields[self.request_field].queryset = self.request_object


#
# objects for request type:
# clean-up events (Müllsammelaktionen)
#

class CleanupEventEventForm(RequestFollowUpForm):
  """
  form for creating or updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  event (Aktion)
  """

  def clean_to_date(self):
    """
    cleans specific field
    """
    from_date = self.cleaned_data.get('from_date')
    to_date = self.cleaned_data.get('to_date')
    if from_date and to_date and to_date <= from_date:
      text = '<strong><em>{}</em></strong> muss nach <em>{}</em> liegen!'.format(
        self._meta.model._meta.get_field('to_date').verbose_name,
        self._meta.model._meta.get_field('from_date').verbose_name)
      text += ' <em>{}</em> weglassen, falls Aktion an nur einem Tag stattfinden soll.'.format(
        self._meta.model._meta.get_field('to_date').verbose_name)
      raise ValidationError(text)
    return to_date


class CleanupEventDetailsForm(RequestFollowUpForm):
  """
  form for creating or updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  details (Detailangaben)
  """

  def clean_waste_types_annotation(self):
    """
    cleans specific field
    """
    waste_types = self.cleaned_data.get('waste_types')
    waste_types_annotation = self.cleaned_data.get('waste_types_annotation')
    if not waste_types and not waste_types_annotation:
      text = 'Wenn keine <strong><em>{}</em></strong> ausgewählt ist/sind,'.format(
        self._meta.model._meta.get_field('waste_types').verbose_name)
      text += ' müssen zwingend <strong><em>{}</em></strong> angegeben werden!'.format(
        self._meta.model._meta.get_field('waste_types_annotation').verbose_name)
      raise ValidationError(text)
    return waste_types_annotation


class CleanupEventContainerForm(RequestFollowUpForm):
  """
  form for creating or updating an instance of object for request type clean-up events
  (Müllsammelaktionen):
  container (Container)
  """

  def clean_pickup_date(self):
    """
    cleans specific field
    """
    delivery_date = self.cleaned_data.get('delivery_date')
    pickup_date = self.cleaned_data.get('pickup_date')
    if delivery_date and pickup_date and pickup_date < delivery_date:
      text = '<strong><em>{}</em></strong> muss gleich <em>{}</em> sein'.format(
        self._meta.model._meta.get_field('pickup_date').verbose_name,
        self._meta.model._meta.get_field('delivery_date').verbose_name)
      text += ' oder nach <em>{}</em> liegen!'.format(
        self._meta.model._meta.get_field('delivery_date').verbose_name)
      raise ValidationError(text)
    return pickup_date
