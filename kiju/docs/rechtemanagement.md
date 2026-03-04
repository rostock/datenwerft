# Rechte-Management

## Nutzerrollen

Die Anwendung hat 4 Nutzergruppen:
* `angebotsdb_admin`
* Verwaltungsnutzer
* Einrichtungsnutzer
* `is_angebotsdb_user`

Jeder Nutzer der Angebotsdatenbank hat die Rolle `is_angebotsdb_user`.

## Modelspezifische Rechte

Die Rolle `is_angebotsdb_user` hat die Berechtigung alle Models zu sehen.

### Träger
* Verwaltungsnutzer und App-Admins können Träger erstellen, bearbeiten und Löschen

### Einrichtungen
* Verwaltungsnutzer und App-Admins können Einrichtungen erstellen.
* Jedem Einrichtungsnutzer ist exakt eine Einrichtung zugewiesen.
* Die Einrichtungsnutzer können ihre eigene Einrichtung editieren.
* Einrichtungen können von ein App-Admins gelöscht werden.

### Angebote(Präventionsangebote)
* Angebote können von Einrichtungsnutzern erstellt werden.
* Dem Angebot wird automatisch die Einrichtung des Erstellers zugewiesen.
* Verwaltungsnutzer können Angebote prüfen und freigeben.
* Angebote können von Einrichtungsnutzern der gleichen Einrichtung gelöscht werden.
* Der App-Admin kann Angebote löschen.

### Gesetze, Zielgruppen & Kategorien
* Verwaltungsnutzer, Einrichtungen und App-Admins können Gesetze, Zielgruppen und Kategorien erstellen, editieren und löschen

## Redaktionsprozess
Ein Angebot wird von einem Einrichtungsnutzer erstellt. Wenn es erstellt wurde ist es erstmal noch inaktiv. Es soll zur Prüfung an einen Verwaltungsnutzer weitergeleitet werden. Der Verwaltungsnutzer erhält dann einen Auftrag in der Inbox. Dort kann er den Auftrag abrufen und die Eingaben der Einrichtung prüfen. Er soll pro Attribut des Angebots einen Kommentar hinterlassen können, falls dort etwas fehlerhaft ist. Ist das Angebot korrekt, wird es vom Verwaltungsnutzer freigegeben und aktiv geschalten. Wird der ganze Fall zurück an die Einrichtung geleitet und ein Einrichtungsnutzer muss das Angebot noch einmal überprüfen. Dabei sieht er die Kommentare des Verwaltungsnutzers. Die Zuordung Angebot -> Verwaltungsnutzer soll über die Arte des Angebots (Klasse PrevetionService, weitere Service KLassen folgen) erfolgen. Jeder Verwaltungsnutzer muss dementspechend einer OE zugeordnet sein. Eine Bsp. OE wäre "OE 62.15". Alle Verwaltungsnutzer der selben OE sehen neue Aufträge für ihre OE in der Inbox.
