# *Stadtbereichskatalog* → Bereich *Daten* → Import

Auf dieser Seite haben Sie die Möglichkeit Daten zu **importieren.**

## Ablauf

1. **Zielschema auswählen:**
   In welche Domäne sollen die Inhalte (Faktendaten) importiert werden?
   Entsprechend muss das passende Datenbankschema gewählt werden.
2. **Zieltabelle auswählen:**
   In welches konkrete Ziel sollen die Inhalte (Faktendaten) importiert werden?
   Entsprechend muss die passende Datenbanktabelle
   innerhalb des zuvor selektierten Datenbankschemas gewählt werden.
   **Hinweis:** Sobald eine Zieltabelle ausgewählt wurde, erscheint deren Struktur
   (das heißt deren Spalten mit Angabe des jeweiligen Datentyps usw.) automatisch
   darunter im Bereich *Zielspalten.*
3. **Quelldatei auswählen** – folgende Dateitypen werden akzeptiert:
   - CSV-Datei, die vollständig konform ist zum offiziellen
     Standard [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180)
     (UTF-8 ohne BOM, Unix-Zeilenenden, Komma als Datentrennzeichen, Punkt als Dezimaltrennzeichen)
   - CSV-Datei, die sich direkt in *Microsoft Excel*
     öffnen lässt (UTF-8 mit BOM, Windows-Zeilenenden, Semikolon als Datentrennzeichen
     Komma als Dezimaltrennzeichen)
   - XLSX-Datei für *Microsoft Excel*
4. auf Button ***Upload* klicken,** um ausgewählte Quelldatei hochzuladen
5. **Mapping durchführen:**
   Durch den Upload der ausgewählten Quelldatei wurde im Hintergrund bereits eine Analyse 
   der Quellspalten durchgeführt und ein entsprechendes Mapping auf die Zielspalten
   voreingestellt. Dieses muss nun **geprüft und bei Bedarf angepasst** werden. Die Färbung
   der Zeilen in der Mappingtabelle sowie die Angaben in der Spalte *Status* der Mappingtabelle
   geben dazu entsprechende Hinweise.
6. Sobald das Mapping passt, müssen Sie auf den Button ***Import* klicken,** um den Datenimport
   durchzuführen. Es erscheint daraufhin ein Dialog, der entweder über den Erfolg oder über
   den Misserfolg des Datenimports berichtet – in letzterem Fall werden dann die Fehlermeldungen
   aufgelistet, die entweder beim Einlesen der Quelldatei oder aber beim Import in die Datenbank
   aufgetreten sind.