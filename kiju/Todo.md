* [x] Profile Model, OrgUnit Model
  * [x] Profile Model
  * [x] OrgUnit Model
  * [x] Profile Model -> OrgUnit Model
  * [x] Profile Model -> User Model (Anzeige im Formular ist noch nicht richtig)
  * [x] Profile Model, OrgUnit Model in Views und Index Template einbinden
* [x] simple Rechte Beschränkungen
  * [x] Funktion `is_angebotsdb_user` in Utils
  * [x] Funktion `is_angebotsdb_admin` in Utils
  * [x] Funktion `add_permission_context_elements` für Views
  * [x] Rechtemanagement in Views einfügen
  * [x] Rechte Variablen in Templates
* [x] erweiterte Rechte Beschränkungen
  * [x] Zuordnung OrgUnit -> Service-Model-Klasse
  * [x] Zuordnung Einrichtung -> Service-Objekt
  * [x] Automatische Zuweisung von Host zu Service auf Basis von Nutzer. (FE) -> Reglung im BE, dass andere Kombination auch nicht möglich ist, für mögliche Zuküftige API konfiguration.
  * [x] Neue Funktion `is_authorized_to_edit` in Utils
  * [x] Neue Funktion `is_authorized_to_review` in Utils
  * [x] Erweiterung `add_permissione_context_elements` um User-Object permission
* [x] Inbox mit Redaktion
  * [x] Form View zum Attribute Prüfen
  * [ ] Model Review mit `dict[field -> Note]`
  * [x] Kategorien und Gesetze werden von OEs gepflegt.
  * [x] Nur App Admin darf Träger hinzufügen und löschen.
  * [x] Träger nur von eigenem Nutzer bearbeitbar.
  * [x] 'Auftragsstate'
  * [x] Typ Überarbeitung: Felder mit Kommentar kein Verbose name
  * [x] In der Korrektur/Bearbeitung rutsch die karte in die Kommentarspalte -> selbes verhalten bei nearbeitung nach freigabe
* [ ] Modellanpassungen
  * [x] Familien und WoftG Angebote erstellen
  * [x] Multi-Images überarbeiten -> Bilder im FE an API senden
  * [x] Adressen in Services werden nicht richtig gesetzt
  * [x] Service-Link
  * [x] Einzugsgebiet Auf Stadtteilbasis.
  * [x] Ablaufdatum -> keine Datumsselektor
* [ ] Hinweis nach Freigabe (Bitte Email an OE senden.) -> Zur Prüfung
* [x] Bugs
  * [x] Sichtbarkeit von Angeboten prüfen (OEs können nicht lesen.)
  * [x] Inbox-Aufträge löschen sich nicht.
  * [x] Formular: 'Zurück zu Kiju-Dashboard'


## In Zukunft
* Welche Modell Attribute sind nach außen sichtbar?
  * [ ] sichtbarkeit im Formular kennzeichnen
* [x] Dashboard auf Basis von Modell Attributen
