import json

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.urls import reverse

register = template.Library()


@register.simple_tag
def dynamic_url(model_lower, action, *args):
  """
  Generates a dynamic URL based on the model name and action.
  Example: {% dynamic_url model_lower 'create' %}
  Example with parameter: {% dynamic_url model_lower 'delete' obj.pk %}
  """
  try:
    url_name = f'kiju:{model_lower}_{action}'
    return reverse(url_name, args=args)
  except Exception as e:
    return f'#Error: {str(e)}'


@register.filter
def to_json(obj):
  """
  Converts a Django model instance to JSON string using verbose_name as keys.
  Example: {{ obj|to_json }}
  """
  try:
    # Create a dictionary with all field values using verbose_name as keys
    data = {}
    for field in obj._meta.fields:
      field_name = field.name
      field_value = getattr(obj, field_name)

      # Use verbose_name as key, fallback to field_name if not available
      display_name = getattr(field, 'verbose_name', None) or field_name
      # Ensure verbose_name is properly capitalized
      if isinstance(display_name, str):
        display_name = (
          display_name.capitalize() if display_name == display_name.lower() else display_name
        )

      # Handle different field types
      if field_value is None:
        data[display_name] = None
      elif hasattr(field_value, 'isoformat'):  # DateTime, Date, Time fields
        data[display_name] = field_value.isoformat()
      else:
        data[display_name] = str(field_value)

    return json.dumps(data, cls=DjangoJSONEncoder)
  except Exception as e:
    return json.dumps({'error': str(e)})


@register.filter
def get_item(dictionary, key):
  """
  Gibt den Wert eines Dicts für den gegebenen Schlüssel zurück.
  Wird im Template für Dict-Lookups mit variablen Schlüsseln verwendet.
  Beispiel: {{ revision_comments|get_item:field.name }}

  :param dictionary: Dict-Objekt
  :param key: Schlüssel
  :return: Wert oder None
  """
  if not isinstance(dictionary, dict):
    return None
  return dictionary.get(key)


@register.filter
def get_attribute(obj, attr):
  """
  Returns the value of the attribute of the object.

  Für CharField-Felder mit choices wird automatisch get_FOO_display() verwendet,
  damit der lesbare Anzeigename statt des rohen DB-Wertes zurückgegeben wird.
  Hintergrund: z.B. OrgUnitServicePermission.service_type speichert den lowercase
  Model-Namen ('childrenandyouthservice'), soll aber den verbose_name_plural anzeigen.
  Django's get_FOO_display() löst das generisch für alle Choice-Felder auf.
  """
  try:
    # Prüfen ob das Feld ein CharField mit choices ist — dann get_FOO_display() nutzen
    display_method = f'get_{attr}_display'
    if hasattr(obj, display_method):
      field = obj._meta.get_field(attr)
      if field.get_internal_type() == 'CharField' and field.choices:
        return getattr(obj, display_method)()

    attribute = getattr(obj, attr)
    if callable(attribute):
      return attribute()
    return attribute
  except (AttributeError, Exception):
    return None
