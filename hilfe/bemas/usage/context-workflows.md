# *BEMAS* → Zusammenhänge und Workflows

## Zusammenhänge

In *BEMAS* sind mehrere sogenannte **Objektklassen** definiert, deren einzelne Datensätze
miteinander in Beziehung stehen (siehe hierzu auch das [Glossar](../glossary.md)):

-   *Person:*
    -   heißt *Betreiber:in,* wenn sie mit einem Verursacher verknüpft ist
    -   heißt *Beschwerdeführer:in,* wenn sie mit einer Beschwerde verknüpft ist
-   *Organisation:*
    -   heißt *Betreiberin,* wenn sie mit einem Verursacher verknüpft ist
    -   heißt *Beschwerdeführerin,* wenn sie mit einer Beschwerde verknüpft ist
-   *Ansprechpartner:in:* Verknüpfung zwischen einer Person und einer Organisation
-   *Verursacher:*
    -   Verursacher einer Emission mit punkthaftem Emissionsort
    -   optional mit beliebig vielen Organisationen als Betreiberinnen verknüpft
    -   optional mit beliebig vielen Personen als Betreiber:innen verknüpft
-   *Beschwerde:*
    -   Folge einer Immission mit punkthaftem Immissionsort
    -   immer mit genau einem Verursacher verknüpft
    -   optional mit beliebig vielen Organisationen als Beschwerdeführerinnen verknüpft
    -   optional mit beliebig vielen Personen als Beschwerdeführer:innen verknüpft
-   *Journalereignis:*
    -   Ereignis im Journal zu einer Beschwerde
    -   immer mit genau einer Beschwerde verknüpft
-   *Eintrag im Bearbeitungsverlauf:* Aktivität im System bzw. „Logbucheintrag“,
    der durch ausgewählte Ereignisse ausgelöst wird

## Workflows

Die Arbeit mit und in *BEMAS* sei hier anhand zweier grundlegender,
exemplarischer Workflows erläutert.

### Wie nehme ich eine neue Beschwerde auf, die (zum Beispiel) per E-Mail eingegangen ist?

Bei diesem beispielhaften Workflow wird davon ausgegangen, dass es sich um eine Person
als Beschwerdeführer:in handelt.

1. prüfen, ob die Person (also die/der Beschwerdeführer:in) bereits im System eingetragen ist:
   1. [Startseite (Dashboard)](dashboard.md) aufrufen
   2. [Tabellenansicht](table.md) mit allen Personen aufrufen
   3. Person suchen – falls gefunden, mit Schritt 3 fortfahren
2. falls nicht gefunden, Person neu im System anlegen:
   1. in [Tabellenansicht](table.md) mit allen Personen
      auf blauen Button *neue Person anlegen* klicken
   2. Eingabemaske auf [Anlegeseite](dataset-create.md) für neue Person
      entsprechend ausfüllen und neuen Datensatz speichern
3. prüfen, ob der Verursacher mit seinem Emissionsort bereits im System eingetragen ist:
   1. [Startseite (Dashboard)](dashboard.md) aufrufen
   2. [Tabellenansicht](table.md) mit allen Verursachern (Emissionsorten)
      und/oder [Übersichtskarte](map.md) mit allen Immissions- und Emissionsorten aufrufen
   3. Verursacher suchen – falls gefunden, mit Schritt 5 fortfahren
4. falls nicht gefunden, Verursacher mit seinem Emissionsort neu im System anlegen:
   1. in [Tabellenansicht](table.md) mit allen Verursachern (Emissionsorten)
      auf blauen Button *neuen Verursacher anlegen* klicken
      oder auf [Startseite (Dashboard)](dashboard.md) Link auf die [Anlegeseite](dataset-create.md)
      für einen neuen Verursacher öffnen
   2. Eingabemaske auf [Anlegeseite](dataset-create.md) für neuen Verursacher
      entsprechend ausfüllen (*), Emissionsort in Karte markieren und neuen Datensatz speichern
5. eigentliche Beschwerde mit ihrem Immissionsort neu im System anlegen:
   1. [Startseite (Dashboard)](dashboard.md) aufrufen
   2. Link auf die [Anlegeseite](dataset-create.md) für eine neue Beschwerde öffnen
   3. Eingabemaske für neue Beschwerde entsprechend ausfüllen,
      Immissionsort in Karte markieren und neuen Datensatz speichern

(*) Hier kann es natürlich sein, dass auch die Betreiberin (= betreibende Organisation)
oder der/die Betreiber:in (= betreibende Person) noch im System fehlt. Falls dem so ist,
müssen die obigen Schritte 2 und 3 entsprechend auch hierfür durchgeführt werden.

### Wie nehme ich ein Telefonat im Zusammenhang mit einer bereits im System bestehenden Beschwerde auf?

#### falls ID der Beschwerde bekannt

1. [Startseite (Dashboard)](dashboard.md) aufrufen
2. auf den blauen Button mit der Heftklammer rechts unterhalb der Liste mit den letzten
   Aktivitäten klicken, um [Tabellenansicht](table.md) mit allen Journalereignissen
   aller Beschwerden aufzurufen
3. auf blauen Button *neues Journalereignis anlegen* klicken
4. Eingabemaske für neues Journalereignis entsprechend ausfüllen und neuen Datensatz speichern 

#### falls ID der Beschwerde nicht bekannt

1. [Startseite (Dashboard)](dashboard.md) aufrufen
2. [Tabellenansicht](table.md) mit allen Beschwerden (Immissionsorte)
   und/oder [Übersichtskarte](map.md) mit allen Immissions- und Emissionsorten aufrufen
3. Beschwerde suchen (und anklicken, falls man sich auf der Übersichtskarte befindet)
4. auf blauen Button mit Heftklammer klicken, um alle Journalereignisse zur Beschwerde aufzurufen
5. auf blauen Button *neues Journalereignis anlegen* klicken
6. Eingabemaske für neues Journalereignis entsprechend ausfüllen und neuen Datensatz speichern 
