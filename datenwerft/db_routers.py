class DatabaseRouter:
  """
  Router zur Steuerung aller Datenbankoperationen
  auf Datenmodellen der Apps BEMAS und Datenmanagement
  """
  route_app_labels = {
    'bemas',
    'datenmanagement'
  }

  def db_for_read(self, model, **hints):
    """
    alle Lesezugriffe auf Datenmodelle der Apps BEMAS und Datenmanagement
    werden in die entsprechende Datenbank geroutet
    """
    if model._meta.app_label in self.route_app_labels:
      if model._meta.app_label == 'bemas':
        return 'bemas'
      elif model._meta.app_label == 'datenmanagement':
        return 'datenmanagement'
    return 'default'

  def db_for_write(self, model, **hints):
    """
    alle Schreibzugriffe auf Datenmodelle der Apps BEMAS und Datenmanagement
    werden in die entsprechende Datenbank geroutet
    """
    if model._meta.app_label in self.route_app_labels:
      if model._meta.app_label == 'bemas':
        return 'bemas'
      elif model._meta.app_label == 'datenmanagement':
        return 'datenmanagement'
    return 'default'

  def allow_relation(self, obj1, obj2, **hints):
    """
    Relationen grundsätzlich immer erlauben
    """
    return True

  def allow_migrate(self, db, app_label, model_name=None, **hints):
    """
    sicherstellen, dass alle Datenmodelle der App Datenmanagement
    niemals einer Migration unterzogen werden
    """
    if app_label in self.route_app_labels:
      if app_label == 'datenmanagement' or db == 'datenmanagement':
        return False
      else:
        return db == app_label
    return None
