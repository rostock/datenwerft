# Implementierungsplan: Draft-Copy bei Bearbeitung veröffentlichter Services

## Kontext & Ziel

Wenn ein Service den Status `published` hat und ein Nutzer (Provider **oder** Admin) ihn
bearbeitet, darf die veröffentlichte Version nicht direkt verändert werden. Stattdessen
wird eine **Kopie (Draft-Copy)** des Service-Objekts erstellt. Der originale Datensatz
bleibt mit `status='published'` unberührt und öffentlich sichtbar. Die Kopie durchläuft
den kompletten Review-Prozess. Wird sie freigegeben, werden die Felder des
Original-Datensatzes mit den Werten der Kopie überschrieben und die Kopie wird gelöscht.

**Gilt für alle Nutzer** — auch Admins und Superuser erhalten den Redirect zur Draft-Copy
und müssen den Review-Prozess durchlaufen. Direkte Änderungen am veröffentlichten Original
ohne Review sind nicht möglich.

---

## Aktueller Zustand der relevanten Dateien

### `kiju/models/services.py`
- Abstrakte Klasse `Service` mit Feldern: `name`, `description`, `image`, `topic`,
  `target_group`, `tags`, `geometry`, `street`, `zip`, `city`, `email`, `host`,
  `legal_basis`, `status`
- `status`-Choices: `draft`, `in_review`, `revision_needed`, `published`
- Konkrete Klassen: `ChildrenAndYouthService`, `FamilyService`, `WoftGService`
  (alle mit zusätzlichen Feldern: `setting`, `application_needed`, `phone`, `costs`;
  `WoftGService` zusätzlich `handicap_accessible`)
- Bestehende Importe aus `django.db.models`:
  `CASCADE, BooleanField, CharField, EmailField, FloatField, ForeignKey,
   ImageField, IntegerField, ManyToManyField, TextField`

### `kiju/models/base.py`
- `ReviewTask`: Verweist auf einen Service über `service_type` (lowercase Modellname)
  und `service_id` (PK). Enthält `task_status`, `comments` (JSONField),
  `approved_snapshot`, `submitted_snapshot`, `assigned_org_unit`.
- `InboxMessage`: Verweist auf `ReviewTask`, hat `target_org_unit` oder `target_provider`.

### `kiju/views/forms.py`
- `GenericUpdateView.dispatch()`: Ruft aktuell `self.get_object()` auf und setzt
  `self._service_locked = True` wenn `status == 'in_review'`. Ruft danach
  `super().dispatch()` auf. Django's `UpdateView` ruft `get_object()` intern nochmals
  auf → das Ergebnis soll in `self._cached_object` gecacht werden.
- `GenericUpdateView.get_context_data()`: Liefert `service_status`, `service_locked`,
  `revision_comments` an den Template-Context.
- `GenericCreateView`: Setzt `host` automatisch aus dem UserProfile.
  Schließt `host` und `status` aus dem Formular aus.
- `GenericUpdateView.get_form_class()`: Schließt `host` und `status` aus dem Formular aus.

### `kiju/views/review.py`
- `SubmitForReviewView`: Setzt `service.status = 'in_review'`, erstellt `ReviewTask`
  und `InboxMessage`(s).
- `ReviewServiceView._approve()`: Setzt `service.status = 'published'`,
  speichert `approved_snapshot`.
- `ReviewServiceView._get_review_fields()`: Nutzt `EXCLUDED_FIELDS`-Set um interne
  Felder aus der Review-Tabelle auszublenden. Aktuell:
  `EXCLUDED_FIELDS = {'id', 'created_at', 'updated_at', 'host', 'status'}`

### `kiju/views/listView.py`
- `ListView.get_context_data()`: Gibt aktuell `queryset = self.model.objects.all()`
  zurück — zeigt also alle Objekte inklusive künftiger Draft-Copies.

### `kiju/views/base.py`
- `GenericMapDataView`: Filtert bereits auf `status='published'` — kein Draft-Copy
  kann also auf der Karte erscheinen. Keine Änderung nötig.

### `kiju/templates/kiju/form.html`
- Zeigt "Zur Prüfung freigeben"-Button wenn `service_status in ('draft', 'revision_needed')`.
- Zeigt Sperr-Hinweis (`service_locked=True`) wenn `status='in_review'`.
- Zeigt `revision_comments` neben den Feldern.

### `kiju/templates/kiju/list.html`
- Zeigt alle Objekte in einer Tabelle mit Status-Badge.
- Löschen-Button nur sichtbar wenn `user_provider == '__all__'` oder
  `user_provider == obj.host`.

### `kiju/urls.py`
- URL-Namen folgen dem verifizierten Muster `kiju:<model_lower>_update`, z.B.:
  `kiju:childrenandyouthservice_update`, `kiju:familyservice_update`, etc.
  Der Redirect in `dispatch()` kann also direkt
  `reverse(f'kiju:{self.model.__name__.lower()}_update', args=[draft.pk])` nutzen.

---

## Schritt 1: Datenmodell-Erweiterung (`kiju/models/services.py`)

### 1.1 Neues Feld `published_version` auf dem abstrakten `Service`-Modell

```python
# Zu den bestehenden Importen hinzufügen:
from django.db.models import (
  CASCADE,
  SET_NULL,          # NEU
  BooleanField,
  CharField,
  EmailField,
  FloatField,
  ForeignKey,
  ImageField,
  IntegerField,
  ManyToManyField,
  TextField,
)
```

```python
# In der abstrakten Service-Klasse, nach dem status-Feld einfügen:
published_version = ForeignKey(
    'self',
    on_delete=SET_NULL,
    null=True,
    blank=True,
    related_name='draft_copies',
    verbose_name='Veröffentlichte Version',
    help_text=(
        'Zeigt auf den originalen published-Datensatz, von dem diese '
        'Draft-Copy abgeleitet wurde. Null bei normalen Services.'
    ),
)
```

**Semantik:**
- `published_version = None` → normaler Service (Original), kein Ableger
- `published_version = <pk>` → diese Instanz ist eine Draft-Copy

**Technischer Hinweis:** `ForeignKey('self', ...)` in einer abstrakten Klasse
funktioniert korrekt — Django löst `'self'` beim Erstellen der Migration für
jede konkrete Unterklasse auf den jeweiligen Tabellennamen auf.

### 1.2 `published_version` aus `list_fields` heraushalten

Das Feld soll **nicht** in `list_fields` der `Service`-Basisklasse erscheinen.
Es wird bereits durch den neuen Status-Badge in der ListView kenntlich gemacht.
Keine Änderung an `list_fields` nötig.

---

## Schritt 2: Migration

```bash
python manage.py makemigrations kiju --name draft_copy_published_version
python manage.py migrate
```

Für alle drei konkreten Modelle (`ChildrenAndYouthService`, `FamilyService`,
`WoftGService`) wird je eine neue Spalte `published_version_id` (nullable FK,
Self-Referenz) angelegt.

---

## Schritt 3: Hilfsfunktionen in `kiju/utils.py`

Die drei neuen Funktionen werden am Ende von `utils.py` vor den bestehenden
Funktionen oder in einem neuen Abschnitt ergänzt. Alle drei benötigen kein
neues Top-Level-Import — die nötigen Importe erfolgen lokal in den Funktionen.

### 3.1 `create_draft_copy(service, user) -> Service`

```python
def create_draft_copy(service, user):
    """
    Erstellt eine Draft-Copy eines published Service-Objekts.

    - Kopiert alle konkreten Felder außer: id, created_at, updated_at,
      status, published_version.
    - Setzt status='draft' und published_version=service auf der Kopie.
    - Überträgt alle ManyToMany-Felder nach dem Speichern.
    - Das image-Feld (ImageField) wird als Dateipfad kopiert — die Datei
      selbst wird nicht verschoben oder dupliziert.
    - Gibt die gespeicherte Draft-Copy-Instanz zurück.

    :param service: Die published Service-Instanz (Original)
    :param user: Der anfragende User (für Logging)
    :return: Neue, gespeicherte Draft-Copy-Instanz
    """
    import logging
    logger = logging.getLogger(__name__)

    SKIP_FIELDS = {'id', 'created_at', 'updated_at', 'status', 'published_version_id'}

    new = service.__class__()

    # Konkrete Felder kopieren
    for field in service._meta.concrete_fields:
        if field.name in SKIP_FIELDS or field.attname in SKIP_FIELDS:
            continue
        setattr(new, field.attname, getattr(service, field.attname))

    new.status = 'draft'
    new.published_version = service
    new.save()

    # ManyToMany-Felder übertragen
    for field in service._meta.many_to_many:
        getattr(new, field.name).set(getattr(service, field.name).all())

    logger.info(
        'Draft-Copy #%s erstellt von User %s für published Service #%s (%s)',
        new.pk, user, service.pk, service.__class__.__name__,
    )
    return new
```

### 3.2 `get_draft_copy_for_user(service, user) -> Service | None`

```python
def get_draft_copy_for_user(service, user):
    """
    Gibt eine bereits existierende aktive Draft-Copy für diesen Service und
    den Provider des Users zurück, oder None wenn keine existiert.

    Verhindert, dass mehrere Draft-Copies desselben Service angelegt werden.

    :param service: Das Original (published) Service-Objekt
    :param user: Der anfragende User
    :return: Existierende Draft-Copy oder None
    """
    provider = get_user_provider(user)
    if provider is None:
        return None

    return service.__class__.objects.filter(
        published_version=service,
        host=provider,
        status__in=['draft', 'in_review', 'revision_needed'],
    ).first()
```

**Hinweis:** Admins haben keinen Provider im UserProfile. Für Admins wird
`get_user_provider()` `None` zurückgeben. Der Dispatch-Code muss daher
für Admins einen eigenen Pfad haben (s. Schritt 4).

### 3.3 `apply_draft_to_published(draft, published) -> None`

```python
def apply_draft_to_published(draft, published):
    """
    Überträgt alle inhaltlichen Felder der Draft-Copy auf den published-Datensatz.

    - Kopiert alle konkreten Felder außer: id, created_at, updated_at,
      status, published_version, host.
    - Das image-Feld wird als Dateipfad kopiert. Das alte Bild des Originals
      wird NICHT vom Filesystem gelöscht (Bereinigung ist separates Thema).
    - Überträgt alle ManyToMany-Felder via .set().
    - Setzt published.status = 'published' explizit.
    - Speichert den published-Datensatz.
    - Löscht die Draft-Copy anschließend.

    :param draft: Die freigegebene Draft-Copy
    :param published: Das Original (published) Service-Objekt
    """
    import logging
    logger = logging.getLogger(__name__)

    SKIP_FIELDS = {
        'id', 'created_at', 'updated_at',
        'status', 'published_version_id', 'host_id',
    }

    # Konkrete Felder übertragen
    for field in draft._meta.concrete_fields:
        if field.attname in SKIP_FIELDS:
            continue
        setattr(published, field.attname, getattr(draft, field.attname))

    published.status = 'published'
    published.save()

    # ManyToMany-Felder übertragen
    for field in draft._meta.many_to_many:
        getattr(published, field.name).set(getattr(draft, field.name).all())

    draft_pk = draft.pk
    draft.delete()

    logger.info(
        'Draft-Copy #%s auf published Service #%s (%s) übertragen und gelöscht.',
        draft_pk, published.pk, published.__class__.__name__,
    )
```

---

## Schritt 4: `kiju/views/forms.py` — `GenericUpdateView`

### 4.1 Object-Caching via `_cached_object`

Das aktuelle Problem: `dispatch()` ruft `self.get_object()` bereits auf,
Django's `UpdateView` ruft es intern nochmals auf — das ergibt mehrere
redundante DB-Abfragen. Lösung: Das Objekt in `get_object()` cachen.

```python
def get_object(self, queryset=None):
    """
    Gibt das angeforderte Objekt zurück. Cached das Ergebnis in self._cached_object
    um mehrfache DB-Abfragen innerhalb desselben Requests zu vermeiden.
    """
    if hasattr(self, '_cached_object') and self._cached_object is not None:
        return self._cached_object
    self._cached_object = super().get_object(queryset)
    return self._cached_object
```

### 4.2 `dispatch()` — Redirect auf Draft-Copy bei `published`

Die vollständige neue `dispatch()`-Methode (ersetzt die bestehende):

```python
def dispatch(self, request, *args, **kwargs):
    if not (
        is_angebotsdb_user(request.user)
        or request.user.is_superuser
        or request.user.is_staff
    ):
        return HttpResponseForbidden("You don't have permission to access this resource")

    self.fields = '__all__'

    from django.shortcuts import redirect
    from django.urls import reverse
    from ..models.services import Service
    from ..utils import create_draft_copy, get_draft_copy_for_user, get_user_provider

    obj = self.get_object()  # nutzt Cache ab jetzt
    is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)

    if is_service_model:
        status = getattr(obj, 'status', None)

        # ── Sperre bei in_review ─────────────────────────────────────────────
        if status == 'in_review':
            self._service_locked = True

        # ── Redirect bei published → Draft-Copy ─────────────────────────────
        elif status == 'published':
            # Gilt für ALLE Nutzer (auch Admins) — niemand darf published
            # Services direkt bearbeiten.
            provider = get_user_provider(request.user)

            if provider is not None:
                # Provider-Nutzer: Draft-Copy unter eigenem Provider suchen/anlegen
                draft = get_draft_copy_for_user(obj, request.user)
                if draft is None:
                    draft = create_draft_copy(obj, request.user)
            else:
                # Admin/Superuser ohne Provider: Draft-Copy unter host des Originals
                # suchen oder neu anlegen (host bleibt der Original-Provider)
                draft = obj.__class__.objects.filter(
                    published_version=obj,
                    status__in=['draft', 'in_review', 'revision_needed'],
                ).first()
                if draft is None:
                    draft = create_draft_copy(obj, request.user)

            draft_url = reverse(
                f'kiju:{self.model.__name__.lower()}_update',
                args=[draft.pk],
            )
            return redirect(draft_url)

        else:
            self._service_locked = False
    else:
        self._service_locked = False

    return super().dispatch(request, *args, **kwargs)
```

**Wichtig:** Der `return redirect(...)` wird VOR `super().dispatch()` ausgeführt.
Django's Dispatch-Mechanismus wertet den Rückgabewert korrekt als
`HttpResponseRedirect` aus.

### 4.3 `get_context_data()` — Draft-Copy-Context

Im `is_service_model`-Block ergänzen:

```python
# Nach der bestehenden service_status / revision_comments Logik:
context['is_draft_copy'] = (
    getattr(self.object, 'published_version_id', None) is not None
)
context['published_version'] = getattr(self.object, 'published_version', None)
```

### 4.4 `form_valid()` — kein Handlungsbedarf

`status` ist bereits aus dem Formular ausgeschlossen (`exclude: ['host', 'status']`).
Beim Speichern einer Draft-Copy bleibt `status='draft'` unverändert erhalten.

---

## Schritt 5: `kiju/views/review.py` — `_approve()` und `EXCLUDED_FIELDS`

### 5.1 `EXCLUDED_FIELDS` in `_get_review_fields()` erweitern

```python
# Bestehend:
EXCLUDED_FIELDS = {'id', 'created_at', 'updated_at', 'host', 'status'}

# Neu — published_version hinzufügen:
EXCLUDED_FIELDS = {'id', 'created_at', 'updated_at', 'host', 'status', 'published_version'}
```

`published_version` ist ein internes Verwaltungsfeld und gehört nicht in die
inhaltliche Prüfung durch den Reviewer.

### 5.2 `_approve()` für Draft-Copy-Flow anpassen

Die vollständige neue `_approve()`-Methode (ersetzt die bestehende):

```python
def _approve(self, review_task: ReviewTask, service):
    """
    Gibt den Service frei.

    Wenn der Service eine Draft-Copy ist (published_version_id gesetzt):
    - Überträgt alle Felder der Draft-Copy auf den Original-Datensatz
      via apply_draft_to_published() (löscht die Draft-Copy).
    - Zeigt den ReviewTask auf die PK des Originals um.

    Wenn der Service ein normaler Draft ist:
    - Setzt service.status = 'published' direkt.

    In beiden Fällen:
    - approved_snapshot ← submitted_snapshot (Basis für nächsten Diff)
    - Alle InboxMessages dieses Tasks als erledigt markieren
    """
    from ..utils import apply_draft_to_published

    is_draft_copy = getattr(service, 'published_version_id', None) is not None

    if is_draft_copy:
        published = service.published_version

        if published is not None:
            # Felder übertragen, Draft-Copy löschen
            apply_draft_to_published(draft=service, published=published)

            # ReviewTask auf Original-Service umzeigen
            review_task.service_id = published.pk
            review_task.task_status = 'approved'
            review_task.comments = {}
            review_task.approved_snapshot = review_task.submitted_snapshot
            review_task.save(update_fields=[
                'task_status', 'comments', 'approved_snapshot', 'service_id',
            ])

            InboxMessage.objects.filter(review_task=review_task).update(is_resolved=True)

            logger.info(
                'ReviewTask #%s freigegeben (Draft-Copy) – '
                'Original service_type=%s service_id=%s',
                review_task.pk, review_task.service_type, published.pk,
            )
            return

        else:
            # Fallback: Original wurde inzwischen gelöscht →
            # Draft-Copy wird selbst zum neuen published Service
            logger.warning(
                'ReviewTask #%s: published_version wurde gelöscht. '
                'Draft-Copy #%s wird direkt als published behandelt.',
                review_task.pk, service.pk,
            )
            # Fallthrough in normalen Approve-Flow

    # Normaler Approve-Flow (kein Draft-Copy oder Fallback)
    service.published_version = None  # sicherstellen dass kein verwaister FK bleibt
    service.status = 'published'
    service.save(update_fields=['status', 'published_version'])

    review_task.task_status = 'approved'
    review_task.comments = {}
    review_task.approved_snapshot = review_task.submitted_snapshot
    review_task.save(update_fields=['task_status', 'comments', 'approved_snapshot'])

    InboxMessage.objects.filter(review_task=review_task).update(is_resolved=True)

    logger.info(
        'ReviewTask #%s freigegeben – service_type=%s service_id=%s',
        review_task.pk, review_task.service_type, review_task.service_id,
    )
```

### 5.3 `_reject()` — kein Handlungsbedarf

Die Draft-Copy erhält `status='revision_needed'` und bleibt als Draft-Copy
erhalten. Der Provider überarbeitet die Draft-Copy und gibt sie erneut zur
Prüfung frei. Der bestehende Code ist korrekt.

---

## Schritt 6: `kiju/views/listView.py` — Queryset-Filterung

### `ListView.get_context_data()` anpassen

Den bestehenden `queryset = self.model.objects.all()`-Aufruf für Service-Modelle
durch folgende Logik ersetzen:

```python
from ..models.services import Service
from django.db import models as db_models

is_service_model = not self.model._meta.abstract and issubclass(self.model, Service)

if is_service_model:
    if self.request.user.is_superuser or is_angebotsdb_admin(self.request.user):
        # Admins sehen nur die Originale — Draft-Copies sind über die
        # Review-Inbox zugänglich, nicht über die normale Listenansicht.
        queryset = self.model.objects.filter(published_version__isnull=True)
    else:
        provider = get_user_provider(self.request.user)
        if provider:
            # Provider sehen:
            # 1. Alle eigenen originalen Services (published_version=None)
            # 2. Eigene Draft-Copies (published_version!=None) als
            #    separate Einträge mit eigenem Status-Badge
            queryset = self.model.objects.filter(host=provider)
        else:
            queryset = self.model.objects.none()
else:
    queryset = self.model.objects.all()

context['object_list'] = queryset
context['objects'] = queryset
```

**Begründung der Entscheidungen:**
- **Admins** sehen keine Draft-Copies in der Liste. Diese sind über die Inbox
  zugänglich (`/kiju/inbox/` → Prüfauftrag → Review-View). Dadurch keine
  Verwirrung durch doppelte Einträge.
- **Provider** sehen ihre Draft-Copies als eigene Tabellenzeilen mit
  Status-Badge `Überarbeitung (Entwurf)` etc. So haben sie ihren Bearbeitungsstand
  immer im Blick ohne extra in die Inbox zu schauen.
- Der "Bearbeiten"-Button in `list.html` zeigt auf den original pk. Da
  `GenericUpdateView.dispatch()` bei `published`-Services transparent zur
  Draft-Copy weiterleitet, muss `list.html` **nicht** geändert werden um
  den richtigen Link anzuzeigen.

---

## Schritt 7: Templates

### 7.1 `kiju/templates/kiju/form.html` — Hinweis-Banner für Draft-Copies

Direkt nach dem bestehenden `service_locked`-Alert einfügen:

```html
{# ── Hinweis bei Draft-Copy (Überarbeitungsversion eines published Service) ── #}
{% if is_draft_copy %}
  <div class="alert alert-info mt-4" role="alert">
    <i class="fa-solid fa-code-branch me-2"></i>
    <strong>Überarbeitungsversion:</strong>
    Sie bearbeiten eine Kopie des veröffentlichten Angebots
    <strong>„{{ published_version }}"</strong>.
    Die veröffentlichte Version bleibt unverändert, bis diese Überarbeitung
    den Freigabeprozess erfolgreich durchlaufen hat.
  </div>
{% endif %}
```

### 7.2 `kiju/templates/kiju/list.html` — Status-Badge für Draft-Copies

Die bestehende `{% elif key == 'status' %}`-Verzweigung erweitern. Der
`get_attribute`-Templatefilter gibt bei `published_version` das FK-Objekt
zurück (truthy wenn gesetzt, falsy wenn None), sodass direkt damit verglichen
werden kann:

```html
{% elif key == 'status' %}
  {% with status_val=obj|get_attribute:'status' is_copy=obj|get_attribute:'published_version' %}
    {% if is_copy %}
      {# Draft-Copy eines veröffentlichten Service #}
      {% if status_val == 'draft' %}
        <span class="badge bg-secondary">
          <i class="fa-solid fa-code-branch me-1"></i>Überarbeitung (Entwurf)
        </span>
      {% elif status_val == 'in_review' %}
        <span class="badge bg-info text-dark">
          <i class="fa-solid fa-code-branch me-1"></i>Überarbeitung (In Prüfung)
        </span>
      {% elif status_val == 'revision_needed' %}
        <span class="badge bg-warning text-dark">
          <i class="fa-solid fa-code-branch me-1"></i>Überarbeitung (Kommentare)
        </span>
      {% else %}
        <span class="badge bg-light text-dark">
          <i class="fa-solid fa-code-branch me-1"></i>{{ status_val }}
        </span>
      {% endif %}
    {% else %}
      {# Normaler (originaler) Service #}
      {% if status_val == 'draft' %}
        <span class="badge bg-secondary">
          <i class="fa-solid fa-pencil me-1"></i>Entwurf
        </span>
      {% elif status_val == 'in_review' %}
        <span class="badge bg-info text-dark">
          <i class="fa-solid fa-magnifying-glass me-1"></i>In Prüfung
        </span>
      {% elif status_val == 'revision_needed' %}
        <span class="badge bg-warning text-dark">
          <i class="fa-solid fa-triangle-exclamation me-1"></i>Überarbeitung nötig
        </span>
      {% elif status_val == 'published' %}
        <span class="badge bg-success">
          <i class="fa-solid fa-circle-check me-1"></i>Veröffentlicht
        </span>
      {% else %}
        <span class="badge bg-light text-dark">{{ status_val }}</span>
      {% endif %}
    {% endif %}
  {% endwith %}
```

**Hinweis:** Der bestehende `{% with %}` in `list.html` muss um `is_copy`
erweitert werden. Die `{% endwith %}`-Tag-Struktur muss entsprechend angepasst
werden.

---

## Zusammenfassung der zu ändernden Dateien

| Datei | Art | Was |
|---|---|---|
| `kiju/models/services.py` | **Ändern** | `SET_NULL` in Importe; `published_version`-FK auf abstrakter `Service`-Klasse |
| `kiju/utils.py` | **Ändern** | Drei neue Funktionen: `create_draft_copy`, `get_draft_copy_for_user`, `apply_draft_to_published` |
| `kiju/views/forms.py` | **Ändern** | `get_object()` mit Cache; `dispatch()` mit Redirect-Logik; `get_context_data()` mit `is_draft_copy` + `published_version` |
| `kiju/views/review.py` | **Ändern** | `EXCLUDED_FIELDS` um `published_version` erweitern; `_approve()` für Draft-Copy-Flow |
| `kiju/views/listView.py` | **Ändern** | Queryset für Service-Modelle: Admins sehen keine Draft-Copies; Provider sehen alle eigenen |
| `kiju/templates/kiju/form.html` | **Ändern** | Hinweis-Banner für Draft-Copies |
| `kiju/templates/kiju/list.html` | **Ändern** | Status-Badge für Draft-Copies vs. Originale |
| `kiju/migrations/` | **Neu** | `0003_draft_copy_published_version.py` |

---

## Implementierungsreihenfolge

1. `kiju/models/services.py` — `published_version`-FK ergänzen
2. Migration erstellen und ausführen
3. `kiju/utils.py` — drei neue Hilfsfunktionen
4. `kiju/views/forms.py` — Object-Cache + Dispatch-Redirect + Context
5. `kiju/views/review.py` — `EXCLUDED_FIELDS` + `_approve()`
6. `kiju/views/listView.py` — Queryset-Filterung
7. Templates — Hinweis-Banner + Status-Badge

---

## Grenzfälle und Hinweise für die Implementierung

### Mehrfache Draft-Copies verhindern
`get_draft_copy_for_user()` prüft ob bereits eine aktive Draft-Copy
(`status in ['draft', 'in_review', 'revision_needed']`) für diesen Provider
existiert. Wenn ja, wird zur bestehenden weitergeleitet — keine neue wird
erstellt. Für Admins prüft `dispatch()` direkt über `published_version=obj`
ohne Provider-Filter.

### Draft-Copy löschen vor Freigabe
Der Provider kann die Draft-Copy über den Löschen-Button im Formular entfernen.
Das Original bleibt erhalten, da `published_version` auf dem gelöschten Draft
`on_delete=SET_NULL` nutzt (hier: SET_NULL wirkt rückwärts nicht, da der FK
von Draft auf Original zeigt). Der Original-Datensatz hat keine direkte
FK-Abhängigkeit zur Draft-Copy — er bleibt immer unberührt.

### Original wurde gelöscht während Draft-Copy in Prüfung ist
In `_approve()` wird `service.published_version` geprüft. Wenn das Original
`None` ist (weil es inzwischen gelöscht wurde), wird die Draft-Copy direkt
als neuer `published` Service behandelt (Fallback-Pfad).

### `apply_draft_to_published` und das `image`-Feld
Nur der Dateipfad (String) wird kopiert — die Datei selbst bleibt an ihrem
Ort im Filesystem. Das alte Bild des Originals wird nicht gelöscht. Eine
systematische Bereinigung von verwaisten Mediadateien ist ein separates
Thema (z.B. via `django-cleanup` oder einem Management-Command).

### `approved_snapshot` im ReviewTask nach Draft-Copy-Approve
`review_task.service_id` wird auf die PK des Originals umgeschrieben.
Der `approved_snapshot` enthält den Stand der Draft-Copy zum Zeitpunkt
der Einreichung — das ist der neue Referenzstand für den nächsten Diff-Vergleich
wenn das Original erneut bearbeitet und eingereicht wird. Das ist korrekt.

### ListView: "Bearbeiten"-Button bei published Services
Der bestehende `dynamic_url`-Link in `list.html` zeigt auf die PK des
published-Originals. `GenericUpdateView.dispatch()` fängt das transparent ab
und leitet zur Draft-Copy weiter. **Keine Änderung an `list.html`-Links nötig.**

### `create_service_snapshot` und `published_version`
`create_service_snapshot()` in `utils.py` iteriert über alle `concrete_fields`
und würde `published_version_id` in den Snapshot aufnehmen. Das ist unkritisch
für die Snapshot-Speicherung, aber `published_version` wurde bereits zu
`EXCLUDED_FIELDS` in `_get_review_fields()` hinzugefügt — es erscheint also
nicht in der Review-Tabelle des Reviewers. Im Diff könnte `published_version_id`
theoretisch auftauchen (z.B. `None` vs. `<pk>`), aber da beide Felder in
`EXCLUDED_FIELDS` stehen, ist das kein praktisches Problem.