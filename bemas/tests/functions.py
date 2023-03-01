def clean_object_filter(object_filter):
  """
  cleans given object filter and returns it

  :param object_filter: object filter
  :return: cleaned version of given object filter
  """
  cleaned_object_filter = object_filter.copy()
  # remove GIS attribute(s) from object filter
  cleaned_object_filter.pop('location', None)
  return cleaned_object_filter


def get_object(model, object_filter):
  """
  fetches object of given model from the database according to given object filter and returns it

  :param model: model
  :param object_filter: object filter
  :return: object of given model from the database according to given object filter
  """
  return model.objects.get(**object_filter)
