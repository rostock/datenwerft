# Antragsmanagement → Berechtigungen

Die Berechtigungen im Antragsmanagement sind auf vier unterschiedliche Rollen aufgeteilt:

1. *anonyme Benutzer:innen*
2. *Antragsteller:innen*
3. *Behördenmitarbeiter:innen*
4. *Administrator:innen*

Die Verteilung der Berechtigungen im Antragsmanagement über diese vier unterschiedliche Rollen
spiegelt folgende Tabelle wieder:

| Rolle | Objektklasse *Antragsteller:in* | Objektklasse *Antrag* (und damit verknüpfte Objektklassen) |
| --- | --- | --- |
| *anonyme Benutzer:innen* | erstellen | erstellen |
| *Antragsteller:innen* | ansehen (nur eigenen Datensatz), erstellen, bearbeiten (nur eigenen Datensatz) | ansehen (pseudonymisiert), erstellen |
| *Behördenmitarbeiter:innen* | | ansehen, bearbeiten (nur zugewiesene Datensätze) |
| *Administrator:innen* | | ansehen |

Die Rolle *Administrator:innen* gestattet es zudem, Datensätze der Objektklassen *Behörde*
und *E-Mail* anzusehen und zu bearbeiten – siehe auch [hier](admin.md).
