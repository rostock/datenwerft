# Allgemein → API

## Übersicht

Anhand der folgenden Übersicht wird deutlich, für welche Bereiche (= Apps)
der Anwendung *Datenwerft.HRO* ein Zugriff via API besteht:

| Bereich (= App) | URL-Bereich | Vollzugriff gemäß Berechtigungen | Lesezugriff für anonyme Benutzer:innen |
| --- | --- | --- | --- |
| Datenmanagement | `/api/datenmanagement` | ja | nein |
| *GDI.HRO Metadata* | `/api/gdihrometadata` | ja | ja |

*Vollzugriff gemäß Berechtigungen* bedeutet hier, dass es von den jeweiligen Berechtigungen
der/des Benutzers/-in im Bereich (also in der App) und dort am betreffenden Datenmodell abhängt,
welche API-Anfragemethoden konkret genutzt werden können. *Lesezugriff für anonyme Benutzer:innen*
hingegen bedeutet, dass anonyme Benutzer:innen (also **ohne** [Anmeldung](login.md) und/oder
**ohne** [API-Token](../admin.md#api-token-hinzufügen)) die API-Anfragemethode `GET` nutzen können,
um Lesezugriff auf die Objekte im Bereich (also in der App) zu erhalten.

## Nutzung

Gemäß obiger Übersicht kann die API entweder anonym genutzt werden oder aber nach vorheriger
[Anmeldung](login.md) in derselben Session
bzw. mittels [API-Token](../admin.md#api-token-hinzufügen). Wird ein API-Token verwendet, so
muss dieser als HTTP-Header mit dem Namen `Authorization` und dem Inhalt
`Token [API-Token]` (Beispiel: `Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`) übergeben werden.

## Beispiele

### Datenmanagement

Ein einfaches Beispiel für den Bereich (also die App) Datenmanagement wäre die via `GET`
im Browser angefragte Liste aller Objekte des Datenmodells *Feuerwachen* im JSON-Format:

```
https://geo.sv.rostock.de/datenwerft/api/datenmanagement/feuerwachen.json
```

Dasselbe Beispiel als Aufruf in der Kommandozeile:

```
curl -X GET -k -i 'https://geo.sv.rostock.de/datenwerft/api/datenmanagement/feuerwachen.json'
```

### *GDI.HRO Metadata*

Ein einfaches Beispiel für den Bereich (also die App) *GDI.HRO Metadata* wäre die via `GET`
im Browser angefragte Detailseite des Objekts mit dem Primärschlüssel `1`
des Datenmodells *Datensatz* im JSON-Format:

```
https://geo.sv.rostock.de/datenwerft/api/gdihrometadata/dataset/1.json
```

Dasselbe Beispiel als Aufruf in der Kommandozeile:

```
curl -X GET -k -i 'https://geo.sv.rostock.de/datenwerft/api/gdihrometadata/dataset/1.json'
```
