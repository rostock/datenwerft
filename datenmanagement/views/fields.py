from django.apps import apps
from django.forms import UUIDField


class AddressUUIDField(UUIDField):
    """
    verstecktes Input-Feld für die Adressensuche

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
    verstecktes Input-Feld für die Straßensuche

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
