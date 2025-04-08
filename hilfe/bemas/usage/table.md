# *BEMAS* → Bereiche und Aktionen → Tabellenansichten

In der Tabellenansicht einer Objektklasse (zum Beispiel *Personen* oder *Beschwerden)*
sind **alle** Datensätze der Objektklasse als Zeilen aufgelistet. Die Attribute der Objektklasse
(zum Beispiel *Titel* oder *Beschreibung)* bilden dabei die Tabellenspalten.
Die Inhalte der Tabelle können gefiltert, durchsucht und exportiert werden.

Die Spalte *Redaktion* ganz rechts in der Tabelle weist folgende Symbole auf:

-   Bleistift: [Bearbeitungsseite](dataset-edit.md) des entsprechenden Datensatzes öffnen
-   Papierkorb: [Löschseite](dataset-delete.md) des entsprechenden Datensatzes öffnen
-   Heftklammer (nur Objektklasse *Beschwerden)*: neue Tabellenansicht mit allen
    Journalereignissen zur entsprechenden Beschwerde öffnen
-   Uhr: neue Tabellenansicht mit allen Einträgen im Bearbeitungsverlauf
    zum entsprechenden Datensatz öffnen
-   Karte (nur Objektklassen *Verursacher* und *Beschwerden)*:
    [Übersichtskarte](map.md) mit allen Immissions- und Emissionsorten öffnen
    und auf entsprechende(n) Verursacher (Emissionsort) oder Beschwerde (Immissionsort) zoomen

## Wie kann ich die Tabelle sortieren?

Die Tabelle können Sie sortieren, indem Sie auf den Titel der Spalte
klicken, nach der Sie sortieren möchten – somit wird die Tabelle
**aufsteigend** nach dieser Spalte sortiert. Wenn Sie nochmals auf
denselben Spaltentitel klicken, wird die Tabelle **absteigend** nach
dieser Spalte sortiert.

## Wie kann ich den Tabelleninhalt filtern?

Den Tabelleninhalt können Sie filtern, indem Sie in dem Eingabefeld mit
der Bezeichnung *Suche/Filter* rechts über der Tabelle einen Begriff
eintragen, nach dem gefiltert werden soll: Bereits während Ihrer Eingabe
wird der Tabelleninhalt dynamisch nach denjenigen Zeilen gefiltert, die
die Eingabe in irgendeiner Spalte enthalten.

## Wie kann ich alle Datensätze in der Tabelle anzeigen?

Falls Sie alle Datensätze in der Tabelle anzeigen möchten, setzen Sie
einfach das Auswahlfeld links unterhalb der Tabelle auf *alle*
(Datensätze anzeigen). Beachten Sie dabei jedoch einen gegebenenfalls
gesetzten Filter.

## Wie kann ich die Zahl der Datensätze in der Tabelle reduzieren?

Gerade bei Datenthemen mit sehr vielen Datensätzen bietet es sich an,
den Tabelleninhalt zu reduzieren bzw. übersichtlicher zu gestalten. Dies
können Sie tun, indem Sie die sogenannte *Paginierung* nutzen: Links
unterhalb der Tabelle ist wählbar, wie viele Einträge pro Seite
angezeigt werden sollen; rechts unterhalb der Tabelle können Sie dann
durch die einzelnen Seiten blättern. Beachten Sie dabei jedoch einen
gegebenenfalls gesetzten Filter.

## Kann die Tabelle auch als CSV-Datei, als Datei für *Microsoft Excel* oder als PDF exportiert werden?

Für den Export der Tabelle als CSV-Datei, als Datei für *Microsoft
Excel* oder als PDF stehen Ihnen die entsprechenden Buttons links
oberhalb der Tabelle zur Verfügung.

Exportiert wird dabei allerdings immer **nur der aktuelle
Tabelleninhalt,** der – wie oben beschrieben – von der
Paginierung, der Filterung und der Sortierung abhängt.

**Tipp:** Wenn Sie **alle Datensätze exportieren** möchten, setzen Sie
einfach das Auswahlfeld links unterhalb der Tabelle auf *alle*
(Datensätze anzeigen), sodass der aktuelle Tabelleninhalt auch alle
Datensätze umfasst. Beachten Sie dabei jedoch einen gegebenenfalls
gesetzten Filter.

## Kann die aktuelle Tabelle auch als Filtermenge in die Karte übernommen werden?

Bei den Objektklassen *Verursacher* und *Beschwerden,* die jeweils
einen räumlichen Bezug aufweisen, kann der
**aktuelle Tabelleninhalt** über den grauen Button *aktuell gefiltere
Verursacher* bzw. *aktuell gefiltere Beschwerden*
oben auf der Seite in die [Übersichtskarte](map.md) übernommen werden.
Es werden dort dann folgerichtig nicht alle Datensätze
der Objektklassen *Verursacher* oder *Beschwerden* auf der Karte angezeigt,
sondern nur die aus der Tabelle übernommenen Datensätze.
