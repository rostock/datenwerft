# Entwicklungsplan: Review-Prozess & Inbox

## Gesamter Workflow im Überblick

```
PROVIDER-NUTZER                          REVIEWER (OrgUnit-Nutzer)
─────────────────                        ─────────────────────────
Erstellt Service (Status: "Entwurf")
  │
  ├─ Klickt "Zur Prüfung freigeben"
  │    → Status: "In Prüfung" (Service gesperrt)
  │    → ReviewTask erstellt
  │    → InboxMessage → OrgUnit-Inbox
  │                                      Sieht Auftrag in Inbox
  │                                        │
  │                                        ├─ Prüft Felder, hinterlässt ggf. Kommentare
  │                                        │    → Kommentare vorhanden? → Zurückweisen
  │                                        │    → Keine Kommentare?     → Freigeben
  │                                        │
  │  ← InboxMessage (Zurückweisung)       (Status: "Überarbeitung nötig")
  │
  ├─ Sieht Kommentare, bearbeitet Service
  ├─ Klickt erneut "Zur Prüfung freigeben"  ← DIFF wird beim nächsten Review angezeigt
  └─ ... Zyklus wiederholt sich
```

---

## Phase 1: Datenmodell-Erweiterungen

### 1.1 Status-Feld auf dem abstrakten `Service`-Modell (`kiju/models/services.py`)

```python
STATUS_CHOICES = [
    ('draft', 'Entwurf'),
    ('in_review', 'In Prüfung'),
    ('revision_needed', 'Überarbeitung nötig'),
    ('published', 'Veröffentlicht'),
]

status = CharField(max_length=20, choices=STATUS_CHOICES, default='draft', verbose_name='Status')
```

- Wird im `GenericCreateView` und `GenericUpdateView` über `exclude` aus dem Formular ausgeschlossen (wie `host`)
- Wird in `list_fields` der Service-Modelle als Spalte aufgenommen (mit farbigem Badge)

### 1.2 Neues Modell `ReviewTask` (`kiju/models/base.py`)

```python
class ReviewTask(Base):
    """
    Ein Prüfauftrag für einen Service.
    Wird erstellt wenn ein Provider-Nutzer einen Service zur Prüfung freigibt.
    Pro Service existiert maximal ein aktiver ReviewTask.
    """
    # Generische Referenz auf den Service (ohne ContentType wg. Cross-DB)
    service_type = CharField(max_length=100, verbose_name='Angebotstyp')
    service_id = IntegerField(verbose_name='Service-ID')

    # Zuordnung
    assigned_org_unit = ForeignKey('OrgUnit', on_delete=CASCADE, verbose_name='Zuständige OE')
    created_by_user_id = IntegerField(verbose_name='Erstellt von (User-ID)')

    # Task-Status
    TASK_STATUS_CHOICES = [
        ('pending', 'Offen'),
        ('approved', 'Freigegeben'),
        ('rejected', 'Zurückgewiesen'),
    ]
    task_status = CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='pending')

    # Kommentare: { "field_name": "Kommentartext", ... }
    comments = JSONField(default=dict, blank=True, verbose_name='Feld-Kommentare')

    # Snapshot: JSON-Abbild aller Feldwerte zum Zeitpunkt der letzten Freigabe.
    # Wird beim Approven gespeichert und beim nächsten Review als Diff-Basis verwendet.
    approved_snapshot = JSONField(default=dict, blank=True, verbose_name='Freigegebener Snapshot')

    # Snapshot der aktuellen Einreichung (zum Diff-Vergleich)
    submitted_snapshot = JSONField(default=dict, blank=True, verbose_name='Eingereichter Snapshot')
```

**Diff-Mechanismus:** Wenn ein Service erneut zur Prüfung eingereicht wird, wird ein Snapshot aller
Feldwerte in `submitted_snapshot` gespeichert. Der `approved_snapshot` enthält den Stand der letzten
Freigabe. Im Review-Template werden beide verglichen und Unterschiede farblich hervorgehoben.

### 1.3 Neues Modell `InboxMessage` (`kiju/models/base.py`)

```python
class InboxMessage(Base):
    """
    Nachricht in der Inbox. Wird an OrgUnit (Reviewer) oder Provider (Einrichtung) gerichtet.
    """
    MESSAGE_TYPE_CHOICES = [
        ('review_request', 'Prüfauftrag'),
        ('revision_request', 'Überarbeitungsauftrag'),
    ]
    message_type = CharField(max_length=30, choices=MESSAGE_TYPE_CHOICES, verbose_name='Typ')
    review_task = ForeignKey('ReviewTask', on_delete=CASCADE, verbose_name='Prüfauftrag')

    # Empfänger — genau eines der beiden Felder ist gesetzt:
    target_org_unit = ForeignKey('OrgUnit', null=True, blank=True, on_delete=CASCADE,
                                 verbose_name='Empfänger-OE')
    target_provider = ForeignKey('Provider', null=True, blank=True, on_delete=CASCADE,
                                 verbose_name='Empfänger-Einrichtung')

    is_read = BooleanField(default=False, verbose_name='Gelesen')
    is_resolved = BooleanField(default=False, verbose_name='Erledigt')
```

---

## Phase 2: Snapshot & Diff-Logik (`kiju/utils.py`)

### 2.1 Neue Hilfsfunktionen

```python
def create_service_snapshot(service):
    """
    Erzeugt ein JSON-serialisierbares Dict aller Feldwerte eines Service.
    ManyToMany-Felder werden als sortierte Listen von IDs + Display-Strings gespeichert.
    Geometrie wird als WKT gespeichert.
    """

def compute_diff(old_snapshot, new_snapshot):
    """
    Vergleicht zwei Snapshots und gibt ein Dict zurück:
    { field_name: {'old': old_value, 'new': new_value} }
    Nur Felder, die sich tatsächlich geändert haben, werden aufgelistet.
    """

def get_service_instance(service_type, service_id):
    """Löst service_type + service_id zu einer konkreten Service-Instanz auf."""

def get_inbox_messages(user):
    """Liefert alle offenen InboxMessages für den User (basierend auf OrgUnit oder Provider)."""

def get_inbox_count(user):
    """Zählt unerledigte InboxMessages für den User."""
```

---

## Phase 3: Views (Backend)

### 3.1 `SubmitForReviewView` – Service zur Prüfung freigeben

- **URL:** `POST <service_type>/<int:service_id>/submit-review/`
- **Logik:**
  1. Prüft, ob der User der Provider des Services ist
  2. Prüft, ob Status `draft` oder `revision_needed` ist (sonst Fehler)
  3. Erzeugt Snapshot mit `create_service_snapshot(service)` → speichert in `submitted_snapshot`
  4. Wenn ein vorheriger abgeschlossener ReviewTask mit `approved_snapshot` existiert, wird dieser übernommen (als Diff-Basis)
  5. Setzt `service.status = 'in_review'`
  6. Erstellt `ReviewTask` mit `task_status='pending'`
  7. Ermittelt zuständige OrgUnit(s) via `OrgUnitServicePermission`
  8. Erstellt `InboxMessage(message_type='review_request', target_org_unit=...)` für jede zuständige OrgUnit
  9. Redirect zurück zur Service-List

### 3.2 `ReviewServiceView` – Review durchführen (für OrgUnit-Reviewer)

- **URL:** `GET/POST review/<int:task_id>/`
- **Template:** `kiju/templates/kiju/review.html`
- **GET:**
  1. Lädt `ReviewTask` und den zugehörigen Service
  2. Iteriert über alle Felder des Service und baut eine `review_fields`-Datenstruktur:
     - `label`, `field_name`, `value`, `comment`, `has_diff`, `old_value`
  3. Berechnet Diff zwischen `approved_snapshot` und `submitted_snapshot`
- **POST:**
  1. Liest Kommentare aus dem Formular: `{ field_name: comment_text, ... }`
  2. Speichert in `ReviewTask.comments`
  3. **Aktion "Freigeben"** (nur möglich wenn keine Kommentare):
     - `service.status = 'published'`
     - `review_task.task_status = 'approved'`
     - `review_task.approved_snapshot = review_task.submitted_snapshot`
     - `InboxMessage.is_resolved = True`
  4. **Aktion "Zurückweisen"** (nur möglich wenn Kommentare vorhanden):
     - `service.status = 'revision_needed'`
     - `review_task.task_status = 'rejected'`
     - Neue `InboxMessage` an `target_provider=service.host`

### 3.3 `InboxListView` – Inbox-Übersicht

- **URL:** `GET inbox/`
- **Template:** `kiju/templates/kiju/inbox.html`
- **Logik:**
  1. Ermittelt über `UserProfile`, ob der User einer OrgUnit oder einem Provider zugeordnet ist
  2. Filtert `InboxMessage.objects.filter(is_resolved=False, ...)` entsprechend
  3. Zeigt tabellarische Übersicht

### 3.4 Anpassung `GenericUpdateView` – Sperre bei `in_review`

- Wenn das Objekt ein Service ist und `status == 'in_review'`:
  - Alle Formularfelder werden auf `disabled` gesetzt
  - `user_can_save` wird auf `False` gesetzt
  - Template zeigt Hinweis: _"Dieser Service befindet sich in Prüfung und kann nicht bearbeitet werden."_

### 3.5 Anpassung `GenericCreateView` / `GenericUpdateView` – Status aus Formular ausschließen

- Das Feld `status` wird in die `exclude`-Liste aufgenommen (analog zu `host`)

### 3.6 Anpassung `IndexView` – Inbox-Count

```python
from ..utils import get_inbox_count
# in get_context_data:
context['inbox_count'] = get_inbox_count(self.request.user)
```

### 3.7 Anpassung `GenericMapDataView` – nur veröffentlichte Services auf der Karte

```python
# Nur veröffentlichte Services anzeigen
objects = self.model.objects.filter(status='published')
```

---

## Phase 4: URL-Routing (`kiju/urls.py`)

```python
# Inbox
path('inbox/', login_required(InboxListView.as_view()), name='inbox_list'),

# Review-Workflow
path('<str:service_type>/<int:service_id>/submit-review/',
     login_required(SubmitForReviewView.as_view()), name='submit_for_review'),
path('review/<int:task_id>/',
     login_required(ReviewServiceView.as_view()), name='review_service'),
```

---

## Phase 5: Templates

### 5.1 `kiju/templates/kiju/inbox.html` (NEU)

Tabellarische Darstellung aller offenen `InboxMessages`:

| # | Typ | Angebot | Angebotstyp | Status | Eingegangen am | Aktion |
|---|-----|---------|-------------|--------|----------------|--------|
| 1 | 🔍 Prüfauftrag | Jugendberatung XY | Kinder & Jugendliche | Offen | 01.06.2025 | [Prüfen] |
| 2 | ✏️ Überarbeitung | Familienberatung Z | Familien | Kommentare | 30.05.2025 | [Bearbeiten] |

- "Prüfen"-Link → `review_service` URL
- "Bearbeiten"-Link → `GenericUpdateView` des Services (mit Kommentar-Anzeige)

### 5.2 `kiju/templates/kiju/review.html` (NEU)

Basiert auf der Struktur von `form.html`, aber im Read-Only-Modus:

- Alle Service-Felder werden als Klartextwerte dargestellt (kein `<input>`)
- Neben jedem Feld ein aufklappbares Kommentar-Textfeld
- Diff-Anzeige wenn sich das Feld seit der letzten Freigabe geändert hat (farbliche Hervorhebung + alter Wert)
- Am Ende: **Freigeben**-Button (nur aktiv wenn keine Kommentare) und **Zurückweisen**-Button (nur aktiv wenn Kommentare vorhanden)

### 5.3 Erweiterung `form.html`

1. **Kommentar-Anzeige:** Wenn `revision_comments` im Context vorhanden ist, wird neben jedem Feld ein gelbes Alert mit dem Reviewer-Kommentar angezeigt
2. **"Zur Prüfung freigeben"-Button:** Erscheint neben "Speichern" wenn Status `draft` oder `revision_needed`
3. **Sperr-Hinweis** bei `in_review`: Info-Banner am oberen Formular-Rand

### 5.4 Erweiterung `list.html` – Status-Badge-Spalte

Farbige Status-Badges für Service-Modelle:

| Status | Badge-Farbe |
|--------|-------------|
| Entwurf | Grau (`bg-secondary`) |
| In Prüfung | Blau (`bg-info`) |
| Überarbeitung nötig | Gelb (`bg-warning`) |
| Veröffentlicht | Grün (`bg-success`) |

### 5.5 Erweiterung `index.html` – Inbox-Card aktivieren

Die bereits vorhandene Inbox-Card (aktuell mit `disabled`-Buttons) wird aktiviert und der Counter dynamisch aus dem Context befüllt.

---

## Phase 6: Frontend-Logik (JavaScript & CSS)

### 6.1 `kiju/static/kiju/js/review.js` (NEU)

- Toggle-Logik für Kommentar-Textfelder (ein-/ausklappen bei Klick auf Kommentar-Icon)
- Event-Listener auf allen Kommentar-Feldern:
  - Mindestens ein Kommentar vorhanden → **Freigeben** `disabled`, **Zurückweisen** `enabled`
  - Alle Kommentare leer → **Freigeben** `enabled`, **Zurückweisen** `disabled`
- Initiale Auswertung beim Seitenload (für vorhandene gespeicherte Kommentare)

### 6.2 `kiju/static/kiju/css/review.css` (NEU)

- Styling für Diff-Anzeige (geänderte Felder farblich hervorgehoben)
- Styling für Kommentar-Bereiche
- Übergangsanimationen für das Ein-/Ausklappen der Kommentarfelder

---

## Phase 7: Migrations & Admin

1. `python manage.py makemigrations kiju`
2. `python manage.py migrate`
3. Admin-Registrierung für `ReviewTask` und `InboxMessage`

---

## Datei-Übersicht: Neue & geänderte Dateien

| Datei | Aktion | Beschreibung |
|---|---|---|
| `kiju/models/services.py` | **Ändern** | `status`-Feld, `list_fields` um Status erweitern |
| `kiju/models/base.py` | **Ändern** | Neue Modelle `ReviewTask`, `InboxMessage` |
| `kiju/views/review.py` | **Neu** | `SubmitForReviewView`, `ReviewServiceView` |
| `kiju/views/inbox.py` | **Neu** | `InboxListView` |
| `kiju/views/forms.py` | **Ändern** | Status excluden, Sperrlogik bei `in_review`, Kommentar-Context |
| `kiju/views/indexView.py` | **Ändern** | `inbox_count` im Context |
| `kiju/views/base.py` | **Ändern** | Filter auf `status='published'` in `GenericMapDataView` |
| `kiju/urls.py` | **Ändern** | Neue URL-Patterns für Inbox und Review |
| `kiju/utils.py` | **Ändern** | Snapshot-, Diff- und Inbox-Hilfsfunktionen |
| `kiju/templatetags/angebotsdb_tags.py` | **Ändern** | `get_item`-Filter für Dict-Lookup im Template |
| `kiju/templates/kiju/inbox.html` | **Neu** | Inbox-Übersicht |
| `kiju/templates/kiju/review.html` | **Neu** | Review-Formular (Read-Only + Kommentare + Diff) |
| `kiju/templates/kiju/form.html` | **Ändern** | Kommentar-Anzeige, Workflow-Buttons, Sperr-Hinweis |
| `kiju/templates/kiju/list.html` | **Ändern** | Status-Badge-Spalte |
| `kiju/templates/kiju/index.html` | **Ändern** | Inbox-Card aktivieren |
| `kiju/static/kiju/js/review.js` | **Neu** | JS für Review-Kommentar-Logik & Button-States |
| `kiju/static/kiju/css/review.css` | **Neu** | Styling für Review & Diff |
| `kiju/admin.py` | **Ändern** | `ReviewTask`, `InboxMessage` registrieren |

---

## Empfohlene Implementierungsreihenfolge

1. **Phase 1** – Datenmodelle + Migration (Fundament für alles)
2. **Phase 2** – Snapshot/Diff Utilities
3. **Phase 3.5** – `status` aus Formularen ausschließen + `list_fields` anpassen
4. **Phase 3.1** – `SubmitForReviewView`
5. **Phase 3.2** – `ReviewServiceView`
6. **Phase 5.2** – Review-Template
7. **Phase 6** – JavaScript & CSS für Review
8. **Phase 3.3** – `InboxListView` + Inbox-Template
9. **Phase 5.3** – `form.html` Erweiterungen
10. **Phase 3.4** – Sperrlogik in `GenericUpdateView`
11. **Phase 3.6 / 3.7** – IndexView Inbox-Count + MapDataView Filter
12. **Phase 5.4 / 5.5** – List- und Dashboard-Anpassungen
13. **Phase 7** – Migrations & Admin