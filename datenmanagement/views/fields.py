from django.apps import apps
from django.forms import DateField, UUIDField


class AddressUUIDField(UUIDField):
  """
  hidden input field for address reference type address
  """

  def to_python(self, value):
    if value in self.empty_values:
      return None
    adressen = apps.get_app_config('datenmanagement').get_model('Adressen')
    return adressen.objects.get(pk=value)


class StreetUUIDField(UUIDField):
  """
  hidden input field for address reference type street
  """

  def to_python(self, value):
    if value in self.empty_values:
      return None
    strassen = apps.get_app_config('datenmanagement').get_model('Strassen')
    return strassen.objects.get(pk=value)


class DistrictUUIDField(UUIDField):
  """
  hidden input field for address reference type district
  """

  def to_python(self, value):
    if value in self.empty_values:
      return None
    gemeindeteile = apps.get_app_config('datenmanagement').get_model('Gemeindeteile')
    return gemeindeteile.objects.get(pk=value)


class ArrayDateField(DateField):
  """
  input field for a date within an array field complex
  """

  def to_python(self, value):
    if not value:
      return None
    return value
