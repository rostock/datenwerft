from django.apps import apps
from django.forms import DateField, UUIDField


class AddressUUIDField(UUIDField):
  """
  verstecktes Input-Feld für Adresse

  Verwendung in Klasse DataForm
  """

  def to_python(self, value):
    """

    :param value: UUID
    :return: Adresse
    """
    if value in self.empty_values:
      return None
    adressen = apps.get_app_config('datenmanagement').get_model('Adressen')
    return adressen.objects.get(pk=value)


class StreetUUIDField(UUIDField):
  """
  verstecktes Input-Feld für Straße

  Verwendung in Klasse DataForm
  """

  def to_python(self, value):
    """

    :param value: UUID
    :return: Straße
    """
    if value in self.empty_values:
      return None
    strassen = apps.get_app_config('datenmanagement').get_model('Strassen')
    return strassen.objects.get(pk=value)


class QuarterUUIDField(UUIDField):
  """
  verstecktes Input-Feld für Gemeindeteil

  Verwendung in Klasse DataForm
  """

  def to_python(self, value):
    """

    :param value: UUID
    :return: Gemeindeteil
    """
    if value in self.empty_values:
      return None
    gemeindeteile = apps.get_app_config('datenmanagement').get_model('Gemeindeteile')
    return gemeindeteile.objects.get(pk=value)


class ArrayDateField(DateField):
  """
  Input-Feld für ein Datum innerhalb eines Array-Feld-Komplexes

  Verwendung in Klasse DataForm
  """

  def to_python(self, value):
    """

    :param value: Datum
    :return: Datum
    """
    if not value:
      return None
    return value
