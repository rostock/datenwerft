"""
Zentrale Dashboard-Konfiguration für die Angebotsdatenbank.

Definiert die Container-Gruppen, in denen Dashboard-Buttons gruppiert werden.
"""

DASHBOARD_CONTAINERS = {
  'basisdaten': {
    'verbose_name': 'Zusätzliche Tabellen',
    'icon': 'fa-solid fa-list-ul',
    'color': 'primary',
    'admin_only': False,
  },
  'benutzerverwaltung': {
    'verbose_name': 'Benutzerverwaltung',
    'icon': 'fa-solid fa-users-gear',
    'color': 'warning',
    'admin_only': True,
  },
}
