# Redaktionsprozess

[← Zurück zur Übersicht](../README.md)

Jedes Angebot durchläuft einen definierten Statuslebenszyklus. Die vier möglichen Status sind:

| Status             | Bedeutung                                             |
| ------------------ | ----------------------------------------------------- |
| `draft`            | Entwurf – wird vom Träger bearbeitet                  |
| `in_review`        | Zur Prüfung eingereicht – wartet auf Reviewer         |
| `revision_needed`  | Vom Reviewer zurückgewiesen – Überarbeitung nötig     |
| `published`        | Freigegeben und veröffentlicht                        |

## Status-Übergänge

```mermaid
stateDiagram-v2
    [*] --> draft : Angebot anlegen

    draft --> in_review : Träger reicht ein
    in_review --> published : Reviewer gibt frei
    in_review --> revision_needed : Reviewer weist zurück

    revision_needed --> in_review : Träger reicht erneut ein

    note right of published
        Bearbeitung erzeugt ein neues Draft-Copy-Objekt\n(status=draft, published_version → Original).\nDas Original selbst bleibt published.
    end note
```

## Ablauf im Detail

```mermaid
sequenceDiagram
    actor T as Träger-Nutzer
    participant App as AngebotsDB
    actor R as Reviewer

    T->>App: Angebot erstellen
    Note over App: Service anlegen (status=draft)
    T->>App: Felder ausfüllen & speichern

    T->>App: Zur Prüfung einreichen
    Note over App: Service.status → in_review<br/>ReviewTask erstellen (pending)<br/>InboxMessage → OrgUnit (review_request)

    R->>App: Inbox öffnen
    App->>R: Prüfauftrag anzeigen (mit Diff)

    alt Freigabe
        R->>App: Freigeben (approve)
        Note over App: Service.status → published<br/>ReviewTask → approved<br/>InboxMessages erledigt
    else Zurückweisung
        R->>App: Zurückweisen + Kommentare (reject)
        Note over App: Service.status → revision_needed<br/>ReviewTask → rejected<br/>InboxMessage → Provider (revision_request)
        T->>App: Inbox öffnen
        App->>T: Kommentare des Reviewers anzeigen
        T->>App: Angebot überarbeiten & erneut einreichen
        Note over App: Service.status → in_review<br/>Neuer ReviewTask (pending)
    end
```

## Review mit Diff-Anzeige

Bei jeder Einreichung wird ein **Snapshot** des aktuellen Zustands erstellt
(`submitted_snapshot`). Wurde das Angebot zuvor bereits einmal freigegeben, wird der damalige
Snapshot als `approved_snapshot` gespeichert. Auf dieser Basis kann der Reviewer eine
**Diff-Ansicht** nutzen, die geänderte Felder hervorhebt.

---

## Draft-Copy-Mechanismus

Wird ein bereits **veröffentlichtes** Angebot bearbeitet, bleibt das Original unverändert
öffentlich sichtbar. Stattdessen wird eine **Draft-Copy** erstellt:

```mermaid
flowchart TD
    PUB["Veröffentlichtes Angebot<br/>(status=published)"]
    COPY["Draft-Copy<br/>(status=draft)<br/>published_version → Original"]
    EDIT["Träger bearbeitet<br/>die Draft-Copy"]
    SUBMIT["Einreichung zur Prüfung<br/>(status=in_review)"]
    REVIEW{"Reviewer-<br/>Entscheidung"}
    APPROVE["Freigabe:<br/>Felder auf Original übertragen,<br/>Draft-Copy löschen"]
    REJECT["Zurückweisung:<br/>Draft-Copy → revision_needed"]

    PUB -->|"Bearbeiten"| COPY
    COPY --> EDIT
    EDIT --> SUBMIT
    SUBMIT --> REVIEW
    REVIEW -->|"approve"| APPROVE
    REVIEW -->|"reject"| REJECT
    REJECT -->|"Überarbeiten & erneut einreichen"| SUBMIT
    APPROVE --> PUB

    style PUB fill:#d4edda,stroke:#155724
    style COPY fill:#fff3cd,stroke:#856404
    style APPROVE fill:#d4edda,stroke:#155724
    style REJECT fill:#f8d7da,stroke:#721c24
```

**Wichtige Eigenschaften:**

- Pro veröffentlichtem Angebot und Träger existiert **maximal eine aktive Draft-Copy**.
- Die Draft-Copy verweist über `published_version` auf das Original.
- Bei **Freigabe** werden alle Felder der Draft-Copy via `apply_draft_to_published()` auf das
  Original übertragen und die Draft-Copy gelöscht.
- Bei **Zurückweisung** bleibt die Draft-Copy erhalten und kann überarbeitet werden.
- `ServiceImage`-Einträge werden bei der Erstellung der Draft-Copy mitkopiert und bei der
  Freigabe auf das Original umgehängt.

---

## Inbox und Benachrichtigungen

Die App verfügt über ein internes **Inbox-System** (`InboxMessage`), das Reviewer und
Träger-Nutzer über anstehende Aufgaben informiert:

| Nachrichtentyp      | Empfänger | Auslöser                              |
| -------------------- | --------- | ------------------------------------- |
| `review_request`     | OrgUnit   | Träger reicht Angebot zur Prüfung ein |
| `revision_request`   | Provider  | Reviewer weist Angebot zurück         |

Nachrichten haben die Flags `is_read` und `is_resolved`. Nach Abschluss eines Review-Vorgangs
werden die zugehörigen Nachrichten automatisch als `is_resolved=True` markiert.