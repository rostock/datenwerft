# *Stadtbereichskatalog* → Bereich *Daten* → Export

Auf dieser Seite haben Sie die Möglichkeit Daten zu **exportieren.**

## Ablauf

1. **Schema auswählen:**
   In welcher Domäne befinden sich die zu exportierenden Inhalte (Faktendaten)?
   Entsprechend muss das passende Datenbankschema gewählt werden.
2. **Tabelle auswählen:**
   Welche konkrete Quelle umfasst die zu exportierenden Inhalte (Faktendaten)?
   Entsprechend muss die passende Datenbanktabelle
   innerhalb des zuvor selektierten Datenbankschemas gewählt werden.
3. bei Bedarf entsprechende **Filter setzen** – siehe dazu nachfolgenden Abschnitt
4. auf passenden **Export-Button klicken:**
   - *CSV (Standard-konform):* Export in CSV-Datei, die vollständig konform ist zum offiziellen
     Standard [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180)
     (UTF-8 ohne BOM, Unix-Zeilenenden, Komma als Datentrennzeichen, Punkt als Dezimaltrennzeichen)
   - *CSV (Excel-freundlich):* Export in CSV-Datei, die sich direkt in *Microsoft Excel*
     öffnen lässt (UTF-8 mit BOM, Windows-Zeilenenden, Semikolon als Datentrennzeichen,
     Komma als Dezimaltrennzeichen)
   - *Excel:* Export in XLSX-Datei für *Microsoft Excel*
5. Es wird nun im Hintergrund eine Datei erzeugt und direkt von Ihrem Browser **heruntergeladen,**
   sodass diese sich nunmehr im eingestellten **Download-Ordner** befindet.

## Filter setzen

Je nach gewähltem Schema und/oder gewählter Tabelle werden verschiedene Filter
aktiviert, die beliebig verwendet werden können – zum Beispiel ein Filter auf das Jahr
oder den Stadtbereich.

**Hinweis:** Sind mehrere Filter gesetzt, so wirken diese additiv (wie „UND“).
