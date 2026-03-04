* [x] Profile Model, OrgUnit Model
  * [x] Profile Model
  * [x] OrgUnit Model
  * [x] Profile Model -> OrgUnit Model
  * [ ] Profile Model -> User Model (Anzeige im Formular ist noch nicht richtig)
  * [x] Profile Model, OrgUnit Model in Views und Index Template einbinden
* [x] simple Rechte Beschränkungen
  * [x] Funktion `is_angebotsdb_user` in Utils
  * [x] Funktion `is_angebotsdb_admin` in Utils
  * [x] Funktion `add_permission_context_elements` für Views
  * [x] Rechtemanagement in Views einfügen
  * [x] Rechte Variablen in Templates
* [ ] erweiterte Rechte Beschränkungen
  * [x] Zuordnung OrgUnit -> Service-Model-Klasse
  * [x] Zuordnung Einrichtung -> Service-Objekt
  * [x] Automatische Zuweisung von Host zu Service auf Basis von Nutzer. (FE) -> Reglung im BE, dass andere Kombination auch nicht möglich ist, für mögliche Zuküftige API konfiguration.
  * [x] Neue Funktion `is_authorized_to_edit` in Utils
  * [ ] Neue Funktion `is_authorized_to_review` in Utils
  * [ ] Erweiterung `add_permissione_context_elements` um User-Object permission
* [ ] Inbox mit Redaktion
  * [ ] Form View zum Attribute Prüfen
  * [ ] Model Review mit `dict[field -> Note]`
* [ ] Dashboard auf Basis von Modell Attributen
* [ ] Modellanpassungen
  * [x] Familien und WoftG Angebote erstellen
  * [ ] Multi-Images überarbeiten -> Bilder im FE an API senden
  * [ ] Adressen in Services werden nicht richtig gesetzt
  * [ ] Service-Link
  * [ ] Einzugsgebiet Auf Stadtteilbasis.
  * [ ] Ablaufdatum


## In Zukunft
* Welche Modell Attribute sind nach außen sichtbar?
