class DatenmanagementRouter:
  """
  Router zur Steuerung aller Datenbankoperationen
  auf Datenmodellen der Anwendung datenmanagement
  """
  route_app_labels = {
    'datenmanagement'
  }

  def db_for_read(self, model, **hints):
    """
    alle Lesezugriffe auf Datenmodelle der Anwendung datenmanagement
    werden in die entsprechende Datenbank geroutet
    """
    if model._meta.app_label in self.route_app_labels:
      if model._meta.app_label == 'datenmanagement':
        return 'datenmanagement'
    return 'default'

  def db_for_write(self, model, **hints):
    """
    alle Schreibzugriffe auf Datenmodelle der Anwendung datenmanagement
    werden in die entsprechende Datenbank geroutet
    """
    if model._meta.app_label in self.route_app_labels:
      if model._meta.app_label == 'datenmanagement':
        return 'datenmanagement'
    return 'default'

  def allow_relation(self, obj1, obj2, **hints):
    """
    Relationen grundsätzlich immer erlauben
    """
    return True

  def allow_migrate(self, db, app_label, model_name=None, **hints):
    """
    sicherstellen, dass alle Datenmodelle der Anwendung datenmanagement
    immer in die entsprechende Datenbank geroutet werden
    """
    if app_label in self.route_app_labels:
      if app_label == 'datenmanagement' or db == 'datenmanagement':
        return False
      else:
        return True
    return None
