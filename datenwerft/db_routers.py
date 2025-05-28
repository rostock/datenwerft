class DatabaseRouter:
  """
  router to control all database operations
  on various apps
  """

  route_app_labels = {
    'antragsmanagement',
    'bemas',
    'datenmanagement',
    'gdihrocodelists',
    'gdihrometadata',
  }

  def db_for_read(self, model, **hints):
    """
    all read access to models of various apps
    are routed to the corresponding database
    """
    if model._meta.app_label in self.route_app_labels:
      if model._meta.app_label == 'antragsmanagement':
        return 'antragsmanagement'
      elif model._meta.app_label == 'bemas':
        return 'bemas'
      elif model._meta.app_label == 'datenmanagement':
        return 'datenmanagement'
      elif model._meta.app_label == 'gdihrocodelists':
        return 'gdihrocodelists'
      elif model._meta.app_label == 'gdihrometadata':
        return 'gdihrometadata'
    return 'default'

  def db_for_write(self, model, **hints):
    """
    all write access to models of various apps
    are routed to the corresponding database
    """
    if model._meta.app_label in self.route_app_labels:
      if model._meta.app_label == 'antragsmanagement':
        return 'antragsmanagement'
      elif model._meta.app_label == 'bemas':
        return 'bemas'
      elif model._meta.app_label == 'datenmanagement':
        return 'datenmanagement'
      elif model._meta.app_label == 'gdihrocodelists':
        return 'gdihrocodelists'
      elif model._meta.app_label == 'gdihrometadata':
        return 'gdihrometadata'
    return 'default'

  def allow_relation(self, obj1, obj2, **hints):
    """
    always allow relations
    """
    return True

  def allow_migrate(self, db, app_label, model_name=None, **hints):
    """
    ensure that all models of Datenmanagement app are never subject to migration
    """
    if app_label in self.route_app_labels:
      if app_label == 'datenmanagement' or db == 'datenmanagement':
        return False
      else:
        return db == app_label
    return None
