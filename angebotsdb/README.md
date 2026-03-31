# AngebotsDB

Die **AngebotsDB** (Angebotsdatenbank) ist eine Django-App innerhalb von *Datenwerft.HRO* zur
zentralen Verwaltung sozialer Angebote der Hanse- und Universitätsstadt Rostock. Sie richtet sich
an Träger sozialer Einrichtungen sowie an die kommunale Verwaltung und bildet den gesamten
Lebenszyklus eines Angebots ab – vom Entwurf über die redaktionelle Prüfung bis zur
Veröffentlichung.

## Fachlicher Überblick

Die AngebotsDB ermöglicht es **Trägern** (z. B. freien Jugendhilfeträgern, Beratungsstellen),
ihre Angebote eigenständig in einem webbasierten Formular zu erfassen und zu pflegen.
**Verwaltungsmitarbeitende** (organisiert in Organisationseinheiten) prüfen eingereichte Angebote
inhaltlich, geben sie frei oder weisen sie mit Kommentaren zur Überarbeitung zurück.

Veröffentlichte Angebote können anschließend über Schnittstellen (z. B. OGC API / PyGeoAPI) in
städtische Portale und Kartenanwendungen eingebunden werden.

## Angebotstypen

Alle Angebotstypen erben von der abstrakten Basisklasse `Service` und teilen sich gemeinsame
Felder wie Name, Beschreibung, Adresse, Geometrie (Punkt), Kategorien, Zielgruppen und Status.

| Modell                     | Beschreibung                        | Besondere Felder                               |
| -------------------------- | ----------------------------------- | ---------------------------------------------- |
| `ChildrenAndYouthService`  | Angebote für Kinder und Jugendliche | Einzugsgebiet (PyGeoAPI), Kosten, Setting      |
| `FamilyService`            | Angebote für Familien               | Einzugsgebiet (PyGeoAPI), Kosten, Setting      |
| `WoftGService`             | Angebote im Rahmen des WoftG        | Kosten, Setting, barrierefreier Zugang (Bool.) |

Neue Angebotstypen können durch Ableitung von `Service` ergänzt werden – die generischen
CRUD-Views, die URL-Registrierung und der Redaktionsprozess greifen automatisch.

## Dokumentation

Ausführliche technische Dokumentation befindet sich im Verzeichnis [`docs/`](docs/):

| Dokument | Inhalt |
| -------- | ------ |
| [Rechte und Rollen](docs/rechte-und-rollen.md) | Gruppen, Rollen-Hierarchie, Berechtigungsmatrix, OrgUnit-Service-Berechtigungen |
| [Redaktionsprozess](docs/redaktionsprozess.md) | Status-Übergänge, Review-Workflow, Draft-Copy-Mechanismus, Inbox-System |
| [Technische Details](docs/technik.md) | Datenmodell (DBML/SVG), Datenbank-Routing, Cross-DB-Workarounds, CRUD-Views, PyGeoAPI |