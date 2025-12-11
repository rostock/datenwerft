# Rechte-Management KiJu App

## Übersicht

Dieses Dokument beschreibt das Rollen- und Berechtigungskonzept für die KiJu AngebotsDB. Die Anwendung wird sowohl von Mitarbeitern des Jugendamtes (bzw. anderer Ämter) als auch von Mitarbeitern sozialer Einrichtungen genutzt.

---

## Rollenübersicht

| Rolle | Beschreibung | Bereich |
|-------|--------------|---------|
| **Global Admin** | Systemweiter Administrator der gesamten Datenwerft-Software | Gesamtsystem |
| **KiJu App Admin** | Administrator der KiJu App (Amt) | KiJu App |
| **Amts-Sachbearbeiter** | Prüft und gibt Angebote frei (Amt), zugeordnet zu einer OE | KiJu App / OE |
| **Einrichtungs-Moderator** | Moderator einer spezifischen Einrichtung | Einrichtung |
| **Einrichtungs-Nutzer** | Standard-Nutzer einer Einrichtung | Einrichtung |

---

## Organisations-Einheiten (OE)

### Konzept

Organisations-Einheiten (OE) bilden die Struktur des Amtes ab und ermöglichen eine fachliche Zuordnung im Redaktionsprozess. Sie dienen dazu, Prüfaufträge an die zuständige Fachabteilung zu routen.

### Anwendungsfälle

1. **Sachbearbeiter-Zuordnung:** Jeder Sachbearbeiter ist einer OE zugeordnet und sieht nur Prüfaufträge seiner OE in der Inbox.
2. **Service-Klassen-Zuordnung:** Jede Service-Klasse (z.B. `PreventionService`, zukünftige Service-Typen) ist einer OE zugeordnet.
3. **Automatisches Routing:** Beim Einreichen eines Angebots wird der Prüfauftrag automatisch an die OE der jeweiligen Service-Klasse weitergeleitet.

### Beispiel-Struktur

```
Amt für Jugend und Familie
├── OE: Jugendförderung
│   ├── zuständig für: HolidayService (Ferienangebote)
│   └── Sachbearbeiter: Müller, Schmidt
├── OE: Prävention
│   ├── zuständig für: PreventionService (Präventionsangebote)
│   └── Sachbearbeiter: Weber, Fischer
└── OE: Familienberatung
    ├── zuständig für: CounselingService (Beratungsangebote) [zukünftig]
    └── Sachbearbeiter: Meyer
```

### Workflow mit OE-Zuordnung

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   EINRICHTUNG       │     │   AMT (OE-basiert)  │     │   ÖFFENTLICH        │
│                     │     │                     │     │                     │
│  PreventionService  │────▶│  Inbox OE Prävention│────▶│  Angebot aktiv      │
│  erstellen          │     │  Sachbearbeiter     │     │  und sichtbar       │
│                     │     │  prüft              │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
```

---

## Workflow: Angebots-Freigabe

### Übersicht

```
┌─────────────────────┐     ┌─────────────────────┐     ┌─────────────────────┐
│   EINRICHTUNG       │     │   AMT               │     │   ÖFFENTLICH        │
│                     │     │                     │     │                     │
│  Angebot erstellen  │────▶│  Inbox: Prüfauftrag │────▶│  Angebot aktiv      │
│  oder bearbeiten    │     │  Freigabe erteilen  │     │  und sichtbar       │
│                     │     │                     │     │                     │
└─────────────────────┘     └─────────────────────┘     └─────────────────────┘
        │                           │
        │                           │ Ablehnung mit
        │◀──────────────────────────│ Begründung
        │  Überarbeitung            │
        │  erforderlich             │
        └───────────────────────────┘
```

### Status-Workflow eines Angebots

| Status | Beschreibung | Sichtbarkeit |
|--------|--------------|--------------|
| `ENTWURF` | Angebot wird erstellt/bearbeitet | Nur Einrichtung |
| `EINGEREICHT` | Zur Prüfung beim Amt | Einrichtung + Amt |
| `IN_PRUEFUNG` | Sachbearbeiter prüft aktiv | Einrichtung + Amt |
| `FREIGEGEBEN` | Angebot ist aktiv | Öffentlich |
| `AENDERUNG_ERFORDERLICH` | Überarbeitung erforderlich | Nur Einrichtung |
| `AENDERUNG_EINGEREICHT` | Änderung zur Prüfung | Einrichtung + Amt |
| `DEAKTIVIERT` | Temporär nicht sichtbar | Nur Einrichtung + Amt |

### Detaillierter Ablauf

#### 1. Neues Angebot erstellen

1. Einrichtungs-Nutzer/Moderator erstellt ein neues Angebot
2. Angebot erhält Status `ENTWURF`
3. Nutzer kann beliebig bearbeiten
4. Nutzer reicht Angebot ein → Status wird `EINGEREICHT`
5. **Automatisch:** Prüfauftrag erscheint in der Inbox des Amts

#### 2. Prüfung durch Amt

1. Sachbearbeiter sieht neuen Auftrag in seiner Inbox
2. Sachbearbeiter öffnet Auftrag → Status wird `IN_PRUEFUNG`
3. Sachbearbeiter prüft alle Angaben
4. **Entscheidung:**
   - ✅ **Freigabe:** Status wird `FREIGEGEBEN` → Angebot ist öffentlich sichtbar
   - ❌ **Ablehnung:** Status wird `AENDERUNG_ERFORDERLICH` + Begründung → zurück an Einrichtung

#### 3. Änderungen an bestehenden Angeboten

1. Einrichtung bearbeitet ein bereits freigegebenes Angebot
2. **Wichtig:** Das aktive Angebot bleibt unverändert öffentlich sichtbar
3. Änderungen werden als "Änderungsentwurf" gespeichert
4. Nach Einreichung → Status `AENDERUNG_EINGEREICHT`
5. Sachbearbeiter prüft die Änderungen
6. Bei Freigabe: Änderungen werden übernommen, Angebot bleibt `FREIGEGEBEN`

---

## Rollenbeschreibungen im Detail

### 1. Global Admin (Datenwerft)

- **Nicht Teil der KiJu App** – separates Berechtigungssystem
- Verwaltet die gesamte Datenwerft-Plattform
- Hat keinen direkten Einfluss auf die KiJu-spezifische Nutzerverwaltung

---

### 2. KiJu App Admin

**Zuordnung:** Mitarbeiter des Amtes (z.B. Jugendamt)

**Berechtigungen:**

| Aktion | Berechtigung |
|--------|--------------|
| Nutzer für KiJu App erstellen | ✅ |
| Nutzer bearbeiten/löschen | ✅ |
| Nutzer einer Einrichtung zuweisen | ✅ |
| Rollen an Nutzer vergeben | ✅ |
| Einrichtungen erstellen/bearbeiten | ✅ |
| Träger erstellen/bearbeiten | ✅ |
| Stammdaten verwalten (Themenfelder, Zielgruppen, Gesetze, Schlagworte) | ✅ |
| Alle Angebote einsehen | ✅ |
| Alle Angebote bearbeiten/löschen | ✅ |
| Angebote freigeben/ablehnen | ✅ |

**Technische Umsetzung:**
- Django-Gruppe: `kiju_admin`
- Benötigte Permissions:
  - `kiju.add_user` / `kiju.change_user` / `kiju.delete_user`
  - `kiju.add_host` / `kiju.change_host` / `kiju.delete_host`
  - `kiju.add_provider` / `kiju.change_provider` / `kiju.delete_provider`
  - `kiju.add_*` / `kiju.change_*` / `kiju.delete_*` für alle Models
  - `kiju.approve_service` / `kiju.reject_service` (Custom Permissions)

---

### 3. Amts-Sachbearbeiter

**Zuordnung:** Mitarbeiter des Amtes (z.B. Jugendamt), der Angebote prüft. **Jeder Sachbearbeiter ist einer Organisations-Einheit (OE) zugeordnet** und sieht nur Prüfaufträge für Service-Klassen, die seiner OE zugeordnet sind.

**Berechtigungen:**

| Aktion | Berechtigung |
|--------|--------------|
| Inbox mit Prüfaufträgen der eigenen OE einsehen | ✅ |
| Angebote der eigenen OE prüfen | ✅ |
| Angebote der eigenen OE freigeben | ✅ |
| Angebote der eigenen OE ablehnen (mit Begründung) | ✅ |
| Alle Angebote einsehen | ✅ |
| Angebote bearbeiten | ❌ |
| Angebote erstellen | ❌ |
| Nutzerverwaltung | ❌ |
| Stammdaten verwalten | ❌ |

**Technische Umsetzung:**
- Django-Gruppe: `kiju_sachbearbeiter`
- **OE-Zuordnung über `KijuUserProfile.organisations_einheit`**
- Benötigte Permissions:
  - `kiju.view_service` / `kiju.view_holidayservice` / `kiju.view_preventionservice`
  - `kiju.approve_service` (Custom Permission)
  - `kiju.reject_service` (Custom Permission)
  - `kiju.view_pruefauftrag`
  - `kiju.change_pruefauftrag`

---

### 4. Einrichtungs-Moderator

**Zuordnung:** Mitarbeiter einer sozialen Einrichtung mit erweiterten Rechten

**Berechtigungen:**

| Aktion | Berechtigung |
|--------|--------------|
| Angebote der eigenen Einrichtung erstellen | ✅ |
| Angebote der eigenen Einrichtung bearbeiten | ✅ |
| Angebote der eigenen Einrichtung löschen | ✅ |
| Angebote zur Freigabe einreichen | ✅ |
| Angebote anderer Einrichtungen bearbeiten | ❌ |
| **Einrichtungsdaten bearbeiten** | ✅ |
| Einrichtungen erstellen/löschen | ❌ |
| Nutzerverwaltung | ❌ |
| Angebote freigeben | ❌ |

**Technische Umsetzung:**
- Django-Gruppe: `kiju_einrichtung_moderator`
- Zusätzliches Feld am User: `einrichtung` (ForeignKey zu `Host`)
- Benötigte Permissions:
  - `kiju.add_service` / `kiju.change_service` / `kiju.delete_service`
  - `kiju.add_holidayservice` / `kiju.change_holidayservice` / `kiju.delete_holidayservice`
  - `kiju.add_preventionservice` / `kiju.change_preventionservice` / `kiju.delete_preventionservice`
  - `kiju.submit_service` (Custom Permission)
  - `kiju.change_host` (nur eigene Einrichtung!)

**Wichtig:** Object-Level-Permission erforderlich, um sicherzustellen, dass nur Angebote der eigenen Einrichtung bearbeitet werden können.

---

### 5. Einrichtungs-Nutzer

**Zuordnung:** Standard-Mitarbeiter einer sozialen Einrichtung

**Berechtigungen:**

| Aktion | Berechtigung |
|--------|--------------|
| Angebote der eigenen Einrichtung erstellen | ✅ |
| Angebote der eigenen Einrichtung bearbeiten | ✅ |
| Angebote der eigenen Einrichtung löschen | ✅ |
| Angebote zur Freigabe einreichen | ✅ |
| Angebote anderer Einrichtungen bearbeiten | ❌ |
| Einrichtungsdaten bearbeiten | ❌ |
| Nutzerverwaltung | ❌ |
| Angebote freigeben | ❌ |

**Technische Umsetzung:**
- Django-Gruppe: `kiju_einrichtung_nutzer`
- Zusätzliches Feld am User: `einrichtung` (ForeignKey zu `Host`)
- Benötigte Permissions:
  - `kiju.add_service` / `kiju.change_service` / `kiju.delete_service`
  - `kiju.add_holidayservice` / `kiju.change_holidayservice` / `kiju.delete_holidayservice`
  - `kiju.add_preventionservice` / `kiju.change_preventionservice` / `kiju.delete_preventionservice`
  - `kiju.submit_service` (Custom Permission)

---

## Technische Umsetzung: Freigabe-System

### 1. Status-Feld für Angebote

```python
# kiju/models/services.py

class ServiceStatus(models.TextChoices):
    ENTWURF = 'entwurf', 'Entwurf'
    EINGEREICHT = 'eingereicht', 'Eingereicht'
    IN_PRUEFUNG = 'in_pruefung', 'In Prüfung'
    FREIGEGEBEN = 'freigegeben', 'Freigegeben'
    AENDERUNG_ERFORDERLICH = 'AENDERUNG_ERFORDERLICH', 'AENDERUNG_ERFORDERLICH'
    AENDERUNG_EINGEREICHT = 'aenderung_eingereicht', 'Änderung eingereicht'
    DEAKTIVIERT = 'deaktiviert', 'Deaktiviert'


class Service(Base):
    # ... bestehende Felder ...
    
    status = models.CharField(
        max_length=25,
        choices=ServiceStatus.choices,
        default=ServiceStatus.ENTWURF,
        verbose_name='Status'
    )
    
    # Für Änderungen an freigegebenen Angeboten
    published_version = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Veröffentlichte Version',
        help_text='Speichert die aktive Version während Änderungen geprüft werden'
    )
    
    class Meta:
        permissions = [
            ('submit_service', 'Kann Angebot zur Prüfung einreichen'),
            ('approve_service', 'Kann Angebot freigeben'),
            ('reject_service', 'Kann Angebot ablehnen'),
        ]
```

### 2. Organisations-Einheit-Model

```python
# kiju/models/organisation.py

from django.db import models


class OrganisationsEinheit(models.Model):
    """
    Organisations-Einheit (OE) des Amtes.
    Dient zur Zuordnung von Sachbearbeitern und Service-Klassen.
    """
    name = models.CharField(
        max_length=255,
        verbose_name='Name'
    )
    beschreibung = models.TextField(
        blank=True,
        verbose_name='Beschreibung'
    )
    aktiv = models.BooleanField(
        default=True,
        verbose_name='Aktiv'
    )
    
    class Meta:
        db_table = 'kiju_organisations_einheit'
        verbose_name = 'Organisations-Einheit'
        verbose_name_plural = 'Organisations-Einheiten'
        ordering = ['name']
    
    def __str__(self):
        return self.name
```

### 3. Service-Klassen-Zuordnung zu OE

Die Zuordnung von Service-Klassen zu Organisations-Einheiten erfolgt über eine Konfigurationstabelle:

```python
# kiju/models/organisation.py

from django.contrib.contenttypes.models import ContentType


class ServiceKlasseOEZuordnung(models.Model):
    """
    Zuordnung von Service-Klassen (Model-Typen) zu Organisations-Einheiten.
    Bestimmt, welche OE für welche Art von Angeboten zuständig ist.
    """
    service_content_type = models.OneToOneField(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='Service-Klasse',
        limit_choices_to={'app_label': 'kiju', 'model__endswith': 'service'},
        help_text='Die Service-Klasse (z.B. PreventionService, HolidayService)'
    )
    organisations_einheit = models.ForeignKey(
        OrganisationsEinheit,
        on_delete=models.PROTECT,
        related_name='service_klassen',
        verbose_name='Zuständige OE'
    )
    
    class Meta:
        db_table = 'kiju_service_klasse_oe_zuordnung'
        verbose_name = 'Service-Klassen-Zuordnung'
        verbose_name_plural = 'Service-Klassen-Zuordnungen'
    
    def __str__(self):
        return f'{self.service_content_type.model} → {self.organisations_einheit}'
```

### 4. Prüfauftrag-Model (Inbox)

```python
# kiju/models/workflow.py

from django.contrib.auth.models import User
from django.db import models
from .services import Service


class AuftragTyp(models.TextChoices):
    NEUES_ANGEBOT = 'neu', 'Neues Angebot'
    AENDERUNG = 'aenderung', 'Änderung'
    REAKTIVIERUNG = 'reaktivierung', 'Reaktivierung'


class AuftragStatus(models.TextChoices):
    OFFEN = 'offen', 'Offen'
    IN_BEARBEITUNG = 'in_bearbeitung', 'In Bearbeitung'
    ABGESCHLOSSEN = 'abgeschlossen', 'Abgeschlossen'


class Pruefauftrag(models.Model):
    """
    Ein Prüfauftrag wird automatisch der OE zugeordnet,
    die für die Service-Klasse des Angebots zuständig ist.
    """
    """
    Repräsentiert einen Prüfauftrag in der Inbox des Sachbearbeiters.
    """
    id = models.AutoField(primary_key=True)
    
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name='pruefauftraege',
        verbose_name='Angebot'
    )
    
    typ = models.CharField(
        max_length=20,
        choices=AuftragTyp.choices,
        verbose_name='Auftragstyp'
    )
    
    status = models.CharField(
        max_length=20,
        choices=AuftragStatus.choices,
        default=AuftragStatus.OFFEN,
        verbose_name='Status'
    )
    
    eingereicht_von = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='eingereichte_auftraege',
        verbose_name='Eingereicht von'
    )
    
    eingereicht_am = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Eingereicht am'
    )
    
    bearbeiter = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='zugewiesene_auftraege',
        verbose_name='Bearbeiter'
    )
    
    bearbeitet_am = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Bearbeitet am'
    )
    
    entscheidung = models.CharField(
        max_length=20,
        choices=[
            ('freigegeben', 'Freigegeben'),
            ('AENDERUNG_ERFORDERLICH', 'AENDERUNG_ERFORDERLICH'),
        ],
        null=True,
        blank=True,
        verbose_name='Entscheidung'
    )
    
    ablehnungsgrund = models.TextField(
        null=True,
        blank=True,
        verbose_name='Ablehnungsgrund'
    )
    
    class Meta:
        db_table = 'kiju_pruefauftrag'
        verbose_name = 'Prüfauftrag'
        verbose_name_plural = 'Prüfaufträge'
        ordering = ['-eingereicht_am']
    
    def __str__(self):
        return f'{self.get_typ_display()}: {self.service.name}'
```

### 3. Service für Workflow-Aktionen

```python
# kiju/services/workflow_service.py

from django.utils import timezone
from django.db import transaction
from ..models import Pruefauftrag, AuftragTyp, AuftragStatus, ServiceStatus


class WorkflowService:
    """
    Service für Workflow-Aktionen.
    Berücksichtigt OE-Zuordnung beim Erstellen von Prüfaufträgen.
    """
    """
    Service-Klasse für Workflow-Operationen.
    """
    
    @staticmethod
    @transaction.atomic
    def einreichen(service, user):
        """
        Reicht ein Angebot zur Prüfung ein.
        """
        if service.status == ServiceStatus.FREIGEGEBEN:
            # Änderung an bestehendem Angebot
            service.status = ServiceStatus.AENDERUNG_EINGEREICHT
            auftrag_typ = AuftragTyp.AENDERUNG
        else:
            # Neues Angebot
            service.status = ServiceStatus.EINGEREICHT
            auftrag_typ = AuftragTyp.NEUES_ANGEBOT
        
        service.save()
        
        # Prüfauftrag erstellen
        Pruefauftrag.objects.create(
            service=service,
            typ=auftrag_typ,
            eingereicht_von=user
        )
        
        return service
    
    @staticmethod
    @transaction.atomic
    def freigeben(pruefauftrag, bearbeiter):
        """
        Gibt ein Angebot frei.
        """
        service = pruefauftrag.service
        
        # Falls es eine Änderung war, published_version löschen
        service.published_version = None
        service.status = ServiceStatus.FREIGEGEBEN
        service.save()
        
        # Auftrag abschließen
        pruefauftrag.status = AuftragStatus.ABGESCHLOSSEN
        pruefauftrag.bearbeiter = bearbeiter
        pruefauftrag.bearbeitet_am = timezone.now()
        pruefauftrag.entscheidung = 'freigegeben'
        pruefauftrag.save()
        
        return service
    
    @staticmethod
    @transaction.atomic
    def ablehnen(pruefauftrag, bearbeiter, grund):
        """
        Lehnt ein Angebot ab.
        """
        service = pruefauftrag.service
        service.status = ServiceStatus.AENDERUNG_ERFORDERLICH
        service.save()
        
        # Auftrag abschließen
        pruefauftrag.status = AuftragStatus.ABGESCHLOSSEN
        pruefauftrag.bearbeiter = bearbeiter
        pruefauftrag.bearbeitet_am = timezone.now()
        pruefauftrag.entscheidung = 'AENDERUNG_ERFORDERLICH'
        pruefauftrag.ablehnungsgrund = grund
        pruefauftrag.save()
        
        # TODO: Benachrichtigung an Einrichtung senden
        
        return service
    
    @staticmethod
    def get_inbox(user):
        """
        Gibt die offenen Prüfaufträge für einen Sachbearbeiter zurück.
        """
        return Pruefauftrag.objects.filter(
            status__in=[AuftragStatus.OFFEN, AuftragStatus.IN_BEARBEITUNG]
        ).select_related('service', 'service__host', 'eingereicht_von')
```

### 4. Berechtigungsprüfung

```python
# kiju/permissions.py

from rest_framework import permissions


class CanSubmitService(permissions.BasePermission):
    """
    Erlaubt das Einreichen von Angeboten zur Prüfung.
    """
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        
        # Prüfe ob User zur Einrichtung gehört
        user_einrichtung = getattr(
            user.kiju_profile, 
            'einrichtung', 
            None
        )
        
        if user_einrichtung is None:
            return False
        
        return obj.host == user_einrichtung


class CanApproveService(permissions.BasePermission):
    """
    Erlaubt das Freigeben/Ablehnen von Angeboten.
    Nur für Amts-Sachbearbeiter und Admins.
    """
    
    def has_permission(self, request, view):
        return request.user.groups.filter(
            name__in=['kiju_admin', 'kiju_sachbearbeiter']
        ).exists()


class IsOwnEinrichtungOrAdmin(permissions.BasePermission):
    """
    Erlaubt Zugriff nur auf Angebote der eigenen Einrichtung
    oder für KiJu Admins/Sachbearbeiter.
    """
    
    def has_object_permission(self, request, view, obj):
        # Amt hat vollen Lesezugriff
        if request.user.groups.filter(
            name__in=['kiju_admin', 'kiju_sachbearbeiter']
        ).exists():
            return True
        
        # Prüfe Einrichtungszugehörigkeit
        user_einrichtung = getattr(
            request.user.kiju_profile, 
            'einrichtung', 
            None
        )
        
        if user_einrichtung is None:
            return False
            
        return obj.host == user_einrichtung


class CanEditEinrichtung(permissions.BasePermission):
    """
    Erlaubt Bearbeitung der Einrichtung nur für Moderatoren
    der jeweiligen Einrichtung oder KiJu Admins.
    """
    
    def has_object_permission(self, request, view, obj):
        # KiJu Admin hat vollen Zugriff
        if request.user.groups.filter(name='kiju_admin').exists():
            return True
        
        # Nur Moderatoren dürfen Einrichtungen bearbeiten
        if not request.user.groups.filter(
            name='kiju_einrichtung_moderator'
        ).exists():
            return False
        
        # Prüfe ob es die eigene Einrichtung ist
        user_einrichtung = getattr(
            request.user.kiju_profile, 
            'einrichtung', 
            None
        )
        
        return obj == user_einrichtung
```

---

## Einrichtungsbezogene Berechtigungen (Object-Level Permissions)

### Problemstellung

Django's Standard-Permission-System arbeitet auf Model-Ebene. Für die KiJu App benötigen wir jedoch Object-Level-Permissions, um sicherzustellen, dass Nutzer nur Angebote ihrer eigenen Einrichtung bearbeiten können.

### Lösungsansatz

**Option A: Django Guardian**
```
pip install django-guardian
```
- Ermöglicht Object-Level-Permissions
- Etablierte Lösung mit guter Dokumentation

**Option B: Eigene Implementierung (empfohlen)**
- Prüfung im View/Serializer
- Filterung der QuerySets basierend auf Einrichtungszugehörigkeit
- Leichtgewichtiger, kein zusätzliches Package erforderlich

### Empfohlene Implementierung

#### 1. Erweiterung des User-Modells (User-Profil)

```python
# kiju/models/user_profile.py

from django.contrib.auth.models import User
from django.db import models
from .base import Host
from .organisation import OrganisationsEinheit


class KijuUserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='kiju_profile'
    )
    # Für Einrichtungs-Nutzer: Zuordnung zur Einrichtung
    einrichtung = models.ForeignKey(
        Host,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='nutzer',
        verbose_name='Einrichtung',
        help_text='Nur für Einrichtungs-Nutzer und -Moderatoren'
    )
    # Für Sachbearbeiter: Zuordnung zur Organisations-Einheit
    organisations_einheit = models.ForeignKey(
        OrganisationsEinheit,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sachbearbeiter',
        verbose_name='Organisations-Einheit',
        help_text='Nur für Amts-Sachbearbeiter'
    )
    
    class Meta:
        db_table = 'kiju_user_profile'
        verbose_name = 'KiJu Nutzerprofil'
        verbose_name_plural = 'KiJu Nutzerprofile'
    
    def __str__(self):
        if self.einrichtung:
            return f'{self.user.username} - Einrichtung: {self.einrichtung}'
        elif self.organisations_einheit:
            return f'{self.user.username} - OE: {self.organisations_einheit}'
        return f'{self.user.username} - Keine Zuordnung'
    
    def clean(self):
        """
        Validierung: Ein Nutzer kann entweder einer Einrichtung
        ODER einer OE zugeordnet sein, aber nicht beiden.
        """
        from django.core.exceptions import ValidationError
        if self.einrichtung and self.organisations_einheit:
            raise ValidationError(
                'Ein Nutzer kann nicht gleichzeitig einer Einrichtung '
                'und einer Organisations-Einheit zugeordnet sein.'
            )
```

#### 2. Filterung der QuerySets

```python
# kiju/views/mixins.py

class EinrichtungFilterMixin:
    """
    Filtert QuerySets basierend auf der Einrichtung des Nutzers.
    """
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admin und Sachbearbeiter sehen alles
        if user.groups.filter(
            name__in=['kiju_admin', 'kiju_sachbearbeiter']
        ).exists():
            return queryset
        
        # Andere Nutzer sehen nur Angebote ihrer Einrichtung
        user_einrichtung = getattr(
            user.kiju_profile,
            'einrichtung',
            None
        )
        
        if user_einrichtung:
            return queryset.filter(host=user_einrichtung)
        
        return queryset.none()


class PublishedOnlyMixin:
    """
    Zeigt nur freigegebene Angebote für öffentliche Ansichten.
    """
    
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(status='freigegeben')
```

---

## Berechtigungsmatrix

| Aktion | Global Admin | KiJu Admin | Sachbearbeiter | Einr.-Moderator | Einr.-Nutzer |
|--------|:------------:|:----------:|:--------------:|:---------------:|:------------:|
| **Nutzerverwaltung** |
| Nutzer erstellen | ✅ | ✅ | ❌ | ❌ | ❌ |
| Nutzer bearbeiten | ✅ | ✅ | ❌ | ❌ | ❌ |
| Nutzer löschen | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Stammdaten** |
| Themenfelder verwalten | ✅ | ✅ | ❌ | ❌ | ❌ |
| Zielgruppen verwalten | ✅ | ✅ | ❌ | ❌ | ❌ |
| Gesetze verwalten | ✅ | ✅ | ❌ | ❌ | ❌ |
| Schlagworte verwalten | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Träger** |
| Träger erstellen | ✅ | ✅ | ❌ | ❌ | ❌ |
| Träger bearbeiten | ✅ | ✅ | ❌ | ❌ | ❌ |
| Träger löschen | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Einrichtungen** |
| Einrichtung erstellen | ✅ | ✅ | ❌ | ❌ | ❌ |
| Eigene Einrichtung bearbeiten | ✅ | ✅ | ❌ | ✅ | ❌ |
| Andere Einrichtung bearbeiten | ✅ | ✅ | ❌ | ❌ | ❌ |
| Einrichtung löschen | ✅ | ✅ | ❌ | ❌ | ❌ |
| **Angebote (Services)** |
| Angebot erstellen (eigene Einr.) | ✅ | ✅ | ❌ | ✅ | ✅ |
| Angebot bearbeiten (eigene Einr.) | ✅ | ✅ | ❌ | ✅ | ✅ |
| Angebot löschen (eigene Einr.) | ✅ | ✅ | ❌ | ✅ | ✅ |
| Angebot einreichen | ✅ | ✅ | ❌ | ✅ | ✅ |
| Angebot bearbeiten (andere Einr.) | ✅ | ✅ | ❌ | ❌ | ❌ |
| Alle Angebote einsehen (freigegeben) | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Freigabe-Workflow** |
| Inbox einsehen | ✅ | ✅ | ✅ | ❌ | ❌ |
| Angebot freigeben | ✅ | ✅ | ✅ | ❌ | ❌ |
| Angebot ablehnen | ✅ | ✅ | ✅ | ❌ | ❌ |

---

## Django Gruppen-Setup

### Management Command

```python
# kiju/management/commands/kiju_roles_permissions.py

from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Erstellt Gruppen und Berechtigungen für die KiJu App'

    def handle(self, *args, **options):
        app_label = 'kiju'
        
        # Gruppe: KiJu Admin
        admin_group, created = Group.objects.get_or_create(name='kiju_admin')
        if created:
            self.stdout.write(self.style.SUCCESS('Gruppe kiju_admin erstellt'))
        
        # Gruppe: Sachbearbeiter
        sachbearbeiter_group, created = Group.objects.get_or_create(
            name='kiju_sachbearbeiter'
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Gruppe kiju_sachbearbeiter erstellt'))
        
        # Gruppe: Einrichtungs-Moderator
        mod_group, created = Group.objects.get_or_create(
            name='kiju_einrichtung_moderator'
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Gruppe kiju_einrichtung_moderator erstellt'))
        
        # Gruppe: Einrichtungs-Nutzer
        user_group, created = Group.objects.get_or_create(
            name='kiju_einrichtung_nutzer'
        )
        if created:
            self.stdout.write(self.style.SUCCESS('Gruppe kiju_einrichtung_nutzer erstellt'))
        
        # Admin bekommt alle Permissions
        admin_permissions = Permission.objects.filter(
            content_type__app_label=app_label
        )
        admin_group.permissions.set(admin_permissions)
        
        # Sachbearbeiter-Permissions
        sachbearbeiter_codenames = [
            'view_service', 'view_holidayservice', 'view_preventionservice',
            'approve_service', 'reject_service',
            'view_pruefauftrag', 'change_pruefauftrag',
            'view_host', 'view_provider', 'view_topic', 
            'view_targetgroup', 'view_law', 'view_tag',
        ]
        sachbearbeiter_permissions = Permission.objects.filter(
            content_type__app_label=app_label,
            codename__in=sachbearbeiter_codenames
        )
        sachbearbeiter_group.permissions.set(sachbearbeiter_permissions)
        
        # Moderator-Permissions
        moderator_codenames = [
            'add_service', 'change_service', 'delete_service', 'view_service',
            'submit_service',
            'add_holidayservice', 'change_holidayservice', 
            'delete_holidayservice', 'view_holidayservice',
            'add_preventionservice', 'change_preventionservice',
            'delete_preventionservice', 'view_preventionservice',
            'change_host', 'view_host',
            'view_provider', 'view_topic', 'view_targetgroup', 
            'view_law', 'view_tag',
        ]
        mod_permissions = Permission.objects.filter(
            content_type__app_label=app_label,
            codename__in=moderator_codenames
        )
        mod_group.permissions.set(mod_permissions)
        
        # Nutzer-Permissions
        user_codenames = [
            'add_service', 'change_service', 'delete_service', 'view_service',
            'submit_service',
            'add_holidayservice', 'change_holidayservice',
            'delete_holidayservice', 'view_holidayservice',
            'add_preventionservice', 'change_preventionservice',
            'delete_preventionservice', 'view_preventionservice',
            'view_host', 'view_provider', 'view_topic', 
            'view_targetgroup', 'view_law', 'view_tag',
        ]
        user_permissions = Permission.objects.filter(
            content_type__app_label=app_label,
            codename__in=user_codenames
        )
        user_group.permissions.set(user_permissions)
        
        self.stdout.write(self.style.SUCCESS('Berechtigungen erfolgreich gesetzt'))
```

**Ausführung:**
```bash
python manage.py kiju_roles_permissions
```

---

## Benachrichtigungen (optional)

Für eine bessere User Experience können Benachrichtigungen implementiert werden:

| Ereignis | Empfänger | Benachrichtigung |
|----------|-----------|------------------|
| Angebot eingereicht | Sachbearbeiter | "Neuer Prüfauftrag: [Angebotname]" |
| Angebot freigegeben | Einrichtung | "Ihr Angebot wurde freigegeben" |
| Angebot AENDERUNG_ERFORDERLICH | Einrichtung | "Ihr Angebot wurde AENDERUNG_ERFORDERLICH: [Grund]" |
| Änderung freigegeben | Einrichtung | "Ihre Änderungen wurden übernommen" |

---

## Zusammenfassung

1. **Strikte Trennung** zwischen Global Admin und KiJu App Admin
2. **Organisations-Einheiten (OE)** zur Strukturierung des Amtes:
   - Sachbearbeiter sind einer OE zugeordnet
   - Service-Klassen sind einer OE zugeordnet
   - Prüfaufträge werden automatisch an die zuständige OE geroutet
3. **Freigabe-Workflow** mit Prüfaufträgen (Inbox) – OE-basiert für Sachbearbeiter
4. **Einrichtungsbezogene Rechte** durch User-Profil mit Einrichtungszuordnung
5. **Object-Level-Permissions** durch View-basierte Prüfung
6. **Vier Rollen-Gruppen** innerhalb der KiJu App:
   - `kiju_admin` – Voller Zugriff
   - `kiju_sachbearbeiter` – Prüfung und Freigabe von Angeboten **der eigenen OE**
   - `kiju_einrichtung_moderator` – Angebote der eigenen Einrichtung bearbeiten + Einrichtungsdaten bearbeiten
   - `kiju_einrichtung_nutzer` – Angebote der eigenen Einrichtung bearbeiten (alle freigegebenen Angebote einsehen)

---

## Nächste Schritte

- [ ] **Organisations-Einheit-Model erstellen** (`OrganisationsEinheit`)
- [ ] **Service-Klassen-Zuordnung-Model erstellen** (`ServiceKlasseOEZuordnung`)
- [ ] User-Profil-Model erstellen (`KijuUserProfile`) mit OE-Feld
- [ ] Status-Feld zu Service-Models hinzufügen
- [ ] Prüfauftrag-Model erstellen (mit OE-Zuordnung)
- [ ] Workflow-Service implementieren (mit OE-Routing)
- [ ] Management Command für Gruppen/Permissions erstellen
- [ ] **Admin-Interface für OE-Verwaltung erstellen**
- [ ] **Admin-Interface für Service-Klassen-Zuordnung erstellen**
- [ ] Permission-Classes in Views integrieren
- [ ] QuerySet-Filterung implementieren (OE-basiert für Sachbearbeiter)
- [ ] Inbox-View für Sachbearbeiter erstellen (OE-gefiltert)
- [ ] Admin-Interface für Nutzerverwaltung durch KiJu Admin
- [ ] Benachrichtigungssystem (optional)
- [ ] Tests für Berechtigungsprüfung und Workflow schreiben
- [ ] Tests für OE-basiertes Routing schreiben
