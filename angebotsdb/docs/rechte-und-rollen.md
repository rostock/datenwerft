# Rechte und Rollen

[← Zurück zur Übersicht](../README.md)

Die Zugriffsteuerung basiert auf **Django-Gruppen** und dem Zusammenspiel
von `UserProfile`, `OrgUnit` und `OrgUnitServicePermission`.

## Gruppen

| Gruppe             | Beschreibung                                                     |
| ------------------ | ---------------------------------------------------------------- |
| `angebotsdb_admin` | Vollzugriff auf alle Angebote, Stammdaten und Benutzerverwaltung |
| `angebotsdb_user`  | Eingeschränkter Zugriff, abhängig vom zugewiesenen Profil        |

## Rollen-Hierarchie

```mermaid
graph TD
    SU["<b>Superuser</b><br/>Vollzugriff auf alles"]
    ADMIN["<b>App-Admin</b><br/>(Gruppe: angebotsdb_admin)<br/>Vollzugriff innerhalb der App"]
    REVIEWER["<b>Reviewer / Verwaltung</b><br/>(UserProfile → OrgUnit)<br/>Prüft &amp; gibt Angebote frei"]
    PROVIDER_USER["<b>Träger-Nutzer</b><br/>(UserProfile → Provider)<br/>Erstellt &amp; bearbeitet eigene Angebote"]

    SU --- ADMIN
    ADMIN --- REVIEWER
    ADMIN --- PROVIDER_USER

    style SU fill:#d4edda,stroke:#155724
    style ADMIN fill:#fff3cd,stroke:#856404
    style REVIEWER fill:#cce5ff,stroke:#004085
    style PROVIDER_USER fill:#e2d9f3,stroke:#6f42c1
```

## Berechtigungsmatrix

| Aktion                      | Superuser | App-Admin | Reviewer (OrgUnit) | Träger-Nutzer (Provider) |
| --------------------------- | :-------: | :-------: | :----------------: | :----------------------: |
| Angebot erstellen           |     ✅     |     ✅     |         ❌          |            ✅             |
| Eigenes Angebot bearbeiten  |     ✅     |     ✅     |         ❌          |            ✅             |
| Fremdes Angebot bearbeiten  |     ✅     |     ✅     |         ❌          |            ❌             |
| Zur Prüfung einreichen      |     ✅     |     ✅     |         ❌          |            ✅             |
| Angebot prüfen (Review)     |     ✅     |     ✅     |         ✅          |            ❌             |
| Angebot freigeben/ablehnen  |     ✅     |     ✅     |         ✅          |            ❌             |
| Stammdaten verwalten        |     ✅     |     ✅     |         ✅          |            ❌             |
| Benutzerverwaltung          |     ✅     |     ✅     |         ❌          |            ❌             |

> **Hinweis:** Reviewer können nur Angebote prüfen, deren Typ über eine
> `OrgUnitServicePermission` ihrer Organisationseinheit zugeordnet ist.

## OrgUnit-Service-Berechtigungen

Die Zuordnung, welche OrgUnit welche Angebotstypen prüfen darf, wird
über das Modell `OrgUnitServicePermission` gesteuert:

```mermaid
graph LR
    OE1["OrgUnit: Jugendamt"] -->|ChildrenAndYouthService| P1["Prüfberechtigung"]
    OE1 -->|FamilyService| P2["Prüfberechtigung"]
    OE2["OrgUnit: Sozialamt"] -->|WoftGService| P3["Prüfberechtigung"]

    style OE1 fill:#cce5ff,stroke:#004085
    style OE2 fill:#cce5ff,stroke:#004085
    style P1 fill:#d4edda,stroke:#155724
    style P2 fill:#d4edda,stroke:#155724
    style P3 fill:#d4edda,stroke:#155724
```
