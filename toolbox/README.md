# App *Toolbox*

Die App *Toolbox* enthält neben generellen „Helferlein“ für *Datenwerft.HRO* auch eine Vorrichtung zum Exportieren von Datensätzen als PDF-Dateien mit eigenen Templates. Dies erfolgt mit Hilfe der schon mit *Django* installierten Bilbiothek [*Jinja2*](https://jinja.palletsprojects.com/) zum Befüllen der Templates und dem Textsatzsystem [*LaTeX*](https://latex-project.org), das aus den befüllten Templates PDF-Dateien erzeugt.

## Voraussetzungen

-  *tex* (Paket `texlive-base`)
-  *pdflatex* (Paket `texlive-latex-base`)
-  in Templates verwendete *LaTeX*-Pakete – für die bisher geschriebenen Templates werden benötigt:
   - `texlive-lang-german` (stellt `[ngerman]{babel}` bereit: deutsche Silbentrennung, Umlaute)
   - `texlive-latex-recommended` (wichtigste *LaTeX*-Pakete; enthält Goodies wie `xcolors` und `fancyhdr`)

Es wird davon abgeraten den Gebrauch des Systempaketmanagers und des *Texlive*-Paketmanagers `tlmgr` zu mischen. Viele der wichtigen *LaTeX*-Pakete finden sich auch in den zum Beispiel mit `apt` nutzbaren Archiven.

### Herstellung der Voraussetzungen unter [*SUSE Linux Enterprise Server*](https://www.suse.com/products/server/)

1.  `zypper install --no-recommends latexmk` (installiert auch gleich grundlegende *LaTeX*-Pakete; ca. 144 MB)
2.  `zypper install --no-recommends texlive-geometry` (ca. 30 kB)
3.  `zypper install --no-recommends texlive-fancyhdr` (ca. 27 kB)
4.  `zypper install texlive-babel-german` (ca. 534 kB)
5.  `zypper install --no-recommends texlive-lastpage` (ca. 25 kB)

## Installation

1.  Verzeichnis `toolbox/mkpdf` mit `rwx`-Rechten für den Benutzer ausstatten, unter dem der HTTP-Server läuft
2.  ggf. zusätzliche Bilder, die in den Templates verwendet werden sollen (Logos etc.), nach `toolbox/mkpdf` kopieren
3.  sicherstellen (z.B. per Cronjob), dass der Befehl `python manage.py cleanpdfdir` mindestens täglich ausgeführt wird – Die Exportfunktion erzeugt temporäre Dateien, die sie nicht selbst beräumt. Alle haben das Präfix `tmp_`. Der Befehl `python manage.py cleanpdfdir` löscht alle Dateien in `toolbox/mkpdf` mit diesem Präfix.
4.  Tabellen für diese Anwendung in der Datenbank anlegen; diese werden von *Djangos* ORM verwaltet, also: `python manage.py migrate toolbox`

Perspektivisch soll der Pfad `toolbox/mkpdf` zu einer Konfigurationsdirektive werden.

## Gebrauch

Die Verwaltung der Templates erfolgt im Django-Admin. Es gibt zwei Datenmodelle: `PdfTemplate` und `SuitableFor`. 

### PdfTemplate

* werden hochgeladen, und müssen einen sprechenden Namen bekommen. Dieser wird dem User bei geeigneten Datenthemen zur Auswahl angezeigt. 
* Sind LaTeX-Dateien mit Jinja2-TemplateTags. 

### SuitableFor

* Sind eine Verknüpfung zwischen Datenthemen (mittels `ContentTypes`) und PdfTemplates. 
* Können direkt im Admin für die Templates erzeugt werden.
* Pflichtfelder sind:
	+ `Datenthema`: für welches Thema das Template als geeignet bezeichnet werden soll.
	+ `Template`: von welchem Template das `SuitableFor` handelt. Bei Verwendung des Inline-Admin im PdfTemplate-Admin ist klar, dass es um das gerade bearbeitete Template geht.

* Das Feld `ins Template zu speisende Attribute` ist kein Pflichtfeld, eventuelle Einträge müssen das Format `[[feld, breite]]` haben.
	+ `feld` muss ein Attributname des gewählten Datenthemas sein
	+ `breite` muss eine von LaTeX verarbeitbare Längenangabe sein (zB `12mm`, `10pt`, `2in`). Dies wird (noch) nicht geprüft. Auch noch nicht geprüft wird, ob die Summe der Einträge die Breite einer Seite überschreitet. 
	+ Diese Angaben stehen im Templatekontext *zur Verfügung*, nur die angegebenen Spalten zu nutzen, ist Aufgabe des Templateautors.

* Das Feld `Sortierung der Einträge` verlangt das Format `[Sortierschlüssel]`, wobei Sortierschlüssel ein Feld des gewählten Datenthemas sein muss. Es darf ein "minus", - , vorangestellt werden. Nach diesem Feld wird dann aufsteigend sortiert. Es können mehrere Sortierschlüssel angegeben werden, dann wird von links nach rechts geschachtelt sortiert. Also in der Art `["baujahr", "-nutzfläche"]`. 

* Existiert für ein Datenthema ein `SuitableFor`-Objekt, dann wird in der Listenansicht zu diesem Thema das verknüpfte Template zur Auswahl stehen.

## Templates

Grundsätzlich sind die Templates LaTeX-Dokumente, in welchen Jinja-Template-Tags genutzt werden können. Die jinja-Marker {% STATEMENT %} und {{ DATA }} sind ersetzt durch \JINJA{STATEMENT} und \VAR{DATA}.

Im Kontext-Dictionary stehen die folgenden Daten zur Verfügung:

* `jetzt` - Ein deutsch formatierter Datumsstempel (dd.mm.jjjj).
* `datenthema` - Der Name des gerade zu verarbeitenden Datenthemas (für den Titel des Dokuments).
* `usedkeys` - Die im Abschnitt [SuitableFor](.SuitableFor) beschriebenen zu verarbeitenden Tupel aus Schlüssel und wie breit die Tabellenspalte für diesen Schlüssel sein soll.
* `display_names` - Ein dictionary `{attrnamen: displaynamen}`. `attrnamen` sind die internen Namen der Felder des Datenthemas, wie sie auch in `usedkeys` auftauchen, `displaynamen` sind die anzuzeigenden Kurzbeschreibungen/Darstellnamen der Felder.
* `records` - Ein Django-Queryset, sortiert wie im `SuitableFor` eingestellt.

* Sollte das Erzeugen des PDFs fehlschlagen, so wird `stdout` von `pdflatex` als Antwort zurückgegeben. Es empfiehlt sich trotzdem, die Templates vorerst auf dem eigenen Rechner zu schreiben und zu testen. 

* es können mithilfe der Jinja-Sprache nun die verschiedenen Daten ins Template gepumpt werden. Besonders hervorgehoben seien hier 
	+ der LaTeX-Befehl `\begin{longtable}`
	+ jinjas for-Schleife, bei uns mit `\JINJA{for}, \JINJA{endfor}`
	+ die Möglichkeit, im Template Variablen zu setzen, so kann über eine Liste von Schlüsseln iteriert werden, welche im Schleifenkörper nochmals als Schlüssel verwendet werden (zB für die Verarbeitung baumartiger Strukturen. Sie `pdfs.py: sortforbaudenkmale()` und das Template `Custom-Baudenkmale`

Für eine Einführung in Jinja sei auf die die Jinja-Dokumentation, [Abschnitt Template-Designer](https://jinja.palletsprojects.com/en/3.0.x/templates/), verwiesen und für LaTeX auf die große Menge an brauchbarer Literatur und Handbüchern, insbesondere [diesen Kurzeinstieg](https://www.ctan.org/pkg/lshort-german). Für gewöhnlich gibt es zu jeder erdenklichen Frage, die einem beim \LaTeX-Schreiben einfallen könnte, einen Thread in einem Forum, oder einen Artikel in den [Hilfeseiten von Overleaf](https://overleaf.com/learn/).


## TODO
In der Klasse *SuitableFor* existiert ein Feld *Bemerkungen*, sodass bei mehreren Verknüpfungen desselben Datenthemas mit demselben Template jeweils im Auswahlmenü ein eigener Text angezeigt werden kann. Im Moment wird der Template-Name angezeigt. Dies gilt es noch zu ändern. Außerdem zur Diskussion stand, die Objekte auch in Karten einzutragen und diese Karten in die Exporte einzubetten.
