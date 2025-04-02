from re import sub


def store_complaint_search_content(sender, instance, **kwargs):
  """
  extends search content for object class complaint in designated field
  (via signal since the many-to-many-relationship is needed here)

  :param sender: signal sending object class model
  :param instance: object
  :param **kwargs
  """
  if kwargs['action'] == 'post_add' or kwargs['action'] == 'post_remove':
    complainers_str = ''
    if kwargs['model'].__name__ == 'Organization':
      complainers = instance.complainers_organizations.all()
      prefix, suffix = 'O-- ', ' --O'
    else:
      complainers = instance.complainers_persons.all()
      prefix, suffix = 'P-- ', ' --P'
    if complainers:
      for index, complainer in enumerate(complainers):
        complainers_str += ' | ' if index > 0 else ''
        complainers_str += str(complainer)
      complainers_str = prefix + complainers_str + suffix
    if instance.search_content == 'anonyme Beschwerde' and complainers_str:
      instance.search_content = complainers_str
      instance.save()
    elif prefix not in instance.search_content and complainers_str:
      instance.search_content += complainers_str
      instance.save()
    elif prefix in instance.search_content:
      instance.search_content = sub(
        prefix + '.*' + suffix, complainers_str, instance.search_content
      )
      if not instance.search_content:
        instance.search_content = 'anonyme Beschwerde'
      instance.save()
