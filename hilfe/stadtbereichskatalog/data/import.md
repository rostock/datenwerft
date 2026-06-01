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
3. Übersicht über die **Zielspalten** – siehe dazu nachfolgenden Abschnitt
4. passenden Export-**Button klicken:**
   - *CSV (Standard-konform):* Export in CSV-Datei, die vollständig konform ist zum offiziellen
     Standard [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180)
     (UTF-8 ohne BOM, Unix-Zeilenenden, Komma als Trennzeichen)
   - *CSV (Excel-freundlich):* Export in CSV-Datei, die sich direkt in *Microsoft Excel*
     öffnen lässt (UTF-8 mit BOM, Windows-Zeilenenden, Semikolon als Trennzeichen)
   - *Excel:* Export in XLSX-Datei für *Microsoft Excel*
5. Es wird nun im Hintergrund eine Datei erzeugt und direkt von Ihrem Browser heruntergeladen,
   sodass diese sich nunmehr im eingestellten Download-Ordner befindet.

## Filter setzen

Je nach gewähltem Quellschema und/oder gewählter Quelltabelle werden verschiedene Filter
aktiviert, die beliebig verwendet werden können – zum Beispiel ein Filter auf das Jahr
oder den Stadtbereich.

**Hinweis:** Sind mehrere Filter gesetzt, so wirken diese additiv (wie „UND“).
