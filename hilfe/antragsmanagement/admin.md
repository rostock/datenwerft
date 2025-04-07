# Antragsmanagement → Administration

## Gruppen und Benutzer:innen

Während der [Initialisierung](../../README.md#initialisierung) der Anwendung *Datenwerft.HRO*
werden die Gruppen `ANTRAGSMANAGEMENT_REQUESTER_GROUP_NAME`,
`ANTRAGSMANAGEMENT_AUTHORITY_GROUPS_NAMES` und `ANTRAGSMANAGEMENT_ADMIN_GROUP_NAME` angelegt
und automatisch mit den passenden [Berechtigungen](permissions.md) versehen.
Zu diesen Gruppen müssen dann manuell die entsprechenden
[Benutzer:innen hinzugefügt](../datenwerft/admin.md#benutzerin-hinzufügen) werden.

## Objektklasse *Behörde*

Die Objektklasse *Behörde* umfasst alle Behörden, denen Anträge zugewiesen werden (können).
Wenn Sie einer Gruppe in der [Rolle](permissions.md) *Administrator:innen* angehören,
können Sie je Behörde die E-Mail-Adresse bearbeiten, an die automatische E-Mails versandt werden,
zum Beispiel über den Eingang eines neuen Antrags.

**Hinweis:** Neue Behörden können **nicht** im Antragsmanagement selbst,
sondern **müssen durch die/den Administrator:in** der *Datenwerft.HRO* hinzugefügt werden.
Dasselbe gilt für die Löschung vorhandener Behörden
sowie für die Bearbeitung der übrigen Attribute.

## Objektklasse *E-Mail*

Die Objektklasse *E-Mail* umfasst die E-Mail-Vorlagen, die für alle automatisch versandten
E-Mails herangezogen werden.
Wenn Sie einer Gruppe in der [Rolle](permissions.md) *Administrator:innen* angehören,
können Sie je E-Mail-Vorlage deren Betreff und Inhalt bearbeiten. Dabei ist jedoch
stets auf die korrekte Verwendung der **Platzhalter** (Variablen) zu achten!

**Hinweis:** Neue E-Mail-Vorlagen können **nicht** im Antragsmanagement selbst,
sondern **müssen durch die/den Administrator:in** der *Datenwerft.HRO* hinzugefügt werden.
Dasselbe gilt für die Löschung vorhandener E-Mail-Vorlagen
sowie für die Bearbeitung der übrigen Attribute.
