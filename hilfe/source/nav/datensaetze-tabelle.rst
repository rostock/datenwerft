.. index:: Aktionen, Auge, Bleistift, CSV, Datensätze-Tabelle, Excel, Export, Filtermenge, Filterung, Paginierung, Papierkorb, PDF, Sortierung, Tabelle, Tabellenspalten

Datensätze-Tabelle
==================

Auf die *Datensätze-Tabelle* eines Datenthemas gelangen Sie immer dann, wenn Sie entweder auf der :doc:`Startseite <datenthema-startseite>` oder in der :doc:`Datensätze-Karte <datensaetze-karte>` eines Datenthemas auf den Button *alle Datensätze in Tabelle auflisten* (bzw. *aktuelle Filtermenge in Tabelle übernehmen)* geklickt haben. In der Tabelle sind alle Datensätze als Zeilen aufgelistet, für die wir Ihnen (mindestens) :ref:`Leserechte <leserechte>` gegeben haben: In der Regel sind dies **alle** Datensätze des Datenthemas.

**Hinweis:** Es sind in der Regel **nicht alle Attribute** des Datenthemas in Form von Tabellenspalten vertreten, sondern nur die für das Zurechtfinden notwendigen (wie zum Beispiel die Bezeichnung), sonst würde die Tabelle viel zu breit.

Je nach :doc:`Rechten <../auth/rechte>` weist die Spalte *Aktionen* ganz rechts in der Tabelle unterschiedliche oder keine Symbole auf:

* Wenn Sie das entsprechende :ref:`Bearbeitungsrecht <schreibrechte>` besitzen, finden Sie in der Spalte *Aktionen* einer Zeile einen Bleistift. Klicken Sie auf den Bleistift, gelangen Sie auf die :doc:`Bearbeitungsseite <../work/datensatz-bearbeiten>` des Datensatzes.
* Wenn Sie das entsprechende Bearbeitungsrecht nicht besitzen, wohl aber das entsprechende Leserecht, finden Sie in der Spalte *Aktionen* einer Zeile ein Auge. Klicken Sie auf das Auge, gelangen Sie zwar auf die Bearbeitungsseite des Datensatzes, haben dort jedoch keine Möglichkeit Bearbeitungen vorzunehmen.
* Wenn Sie das entsprechende :ref:`Löschrecht <schreibrechte>` besitzen, finden Sie in der Spalte *Aktionen* einer Zeile einen Papierkorb. Klicken Sie auf den Papierkorb, gelangen Sie auf die :doc:`Löschseite <../work/datensatz-loeschen>` des Datensatzes.

**Tipp:** Sie können auch **mehrere Datensätze auf einmal löschen**, indem Sie zunächst in jeder gewünschten Zeile der Tabelle – also für jeden Datensatz, der gelöscht werden soll – das Auswahlfeld in der Spalte ganz links aktivieren (also „anhaken“). Anschließend wählen Sie links unterhalb der Tabelle als *Aktion* den Eintrag *ausgewählte Datensätze löschen* aus und klicken danach auf den Button *Aktion ausführen* rechts daneben.

.. _tabelle_sortieren:

Wie kann ich die Tabelle sortieren?
-----------------------------------

Die Tabelle können Sie sortieren, indem Sie auf den Titel der Spalte klicken, nach der Sie sortieren möchten – somit wird die Tabelle **aufsteigend** nach dieser Spalte sortiert. Wenn Sie nochmals auf denselben Spaltentitel klicken, wird die Tabelle **absteigend** nach dieser Spalte sortiert.

.. _tabelle_filtern:

Wie kann ich den Tabelleninhalt filtern?
----------------------------------------

Den Tabelleninhalt können Sie filtern, indem Sie in dem Eingabefeld mit der Bezeichnung *Suche/Filter* rechts über der Tabelle einen Begriff eintragen, nach dem gefiltert werden soll: Bereits während Ihrer Eingabe wird der Tabelleninhalt dynamisch nach denjenigen Zeilen gefiltert, die die Eingabe in irgendeiner Spalte enthalten.

.. _tabelle_alle_datensaetze:

Wie kann ich alle Datensätze in der Tabelle anzeigen?
-----------------------------------------------------

Falls Sie alle Datensätze in der Tabelle anzeigen möchten, setzen Sie einfach das Auswahlfeld links unterhalb der Tabelle auf *alle* (Datensätze anzeigen). Beachten Sie dabei jedoch einen gegebenenfalls gesetzten :ref:`Filter <tabelle_filtern>`.

.. _tabelle_paginieren:

Wie kann ich die Zahl der Datensätze in der Tabelle reduzieren?
---------------------------------------------------------------

Gerade bei Datenthemen mit sehr vielen Datensätzen bietet es sich an, den Tabelleninhalt zu reduzieren bzw. übersichtlicher zu gestalten. Dies können Sie tun, indem Sie die sogenannte *Paginierung* nutzen: Links unterhalb der Tabelle ist wählbar, wie viele Einträge pro Seite angezeigt werden sollen; rechts unterhalb der Tabelle können Sie dann durch die einzelnen Seiten blättern. Beachten Sie dabei jedoch einen gegebenenfalls gesetzten :ref:`Filter <tabelle_filtern>`.

.. _tabelle_exportieren:

Kann die Tabelle auch als CSV-Datei, als Datei für *Microsoft Excel* oder als PDF exportiert werden?
----------------------------------------------------------------------------------------------------

Für den Export der Tabelle als CSV-Datei, als Datei für *Microsoft Excel* oder als PDF stehen Ihnen die entsprechenden Buttons links oberhalb der Tabelle zur Verfügung.

Exportiert wird dabei allerdings immer **nur der aktuelle Tabelleninhalt,** der – wie oben beschrieben – von der :ref:`Paginierung <tabelle_paginieren>`, der :ref:`Filterung <tabelle_filtern>` und der :ref:`Sortierung <tabelle_sortieren>` abhängt.

**Tipp:** Wenn Sie **alle Datensätze exportieren** möchten, setzen Sie einfach das Auswahlfeld links unterhalb der Tabelle auf *alle* (Datensätze anzeigen), sodass der aktuelle Tabelleninhalt auch alle Datensätze umfasst. Beachten Sie dabei jedoch einen gegebenenfalls gesetzten :ref:`Filter <tabelle_filtern>`.

.. _tabelle_in_karte_uebernehmen:

Kann die aktuelle Tabelle auch als Filtermenge in die Karte übernommen werden?
------------------------------------------------------------------------------

Sofern das Datenthema einen räumlichen Bezug aufweist, kann der **aktuelle Tabelleninhalt** kann über den Button *aktuelle Filtermenge auf Karte übernehmen* oben auf der Seite in die :doc:`Datensätze-Karte <datensaetze-karte>` des Datenthemas übernommen werden. Es werden dort dann folgerichtig nicht alle Datensätze auf der Karte angezeigt, sondern nur die aus der Tabelle übernommenen Datensätze.
