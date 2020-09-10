.. index:: Adresse, Adressensuche, Attribute, Datensatz anlegen, Fläche, Linie, neuer Datensatz, Pflichtattribute, Punkt, Sachdaten, Speichern, Straße, Syntax, Verortung

Datensatz anlegen
=================

Auf die *Anlegeseite* eines neuen Datensatzes gelangen Sie immer dann, wenn Sie entweder auf der :doc:`Startseite <../nav/datenthema-startseite>`, in der :doc:`Datensätze-Tabelle <../nav/datensaetze-tabelle>` oder auf der :doc:`Datensätze-Karte <../nav/datensaetze-karte>` eines Datenthemas auf den Button *neuen Datensatz anlegen* geklickt haben. Die Anlegeseite ist nichts anderes als eine Eingabemaske mit Karte für einen neuen Datensatz.


.. _datensatz_anlegen_attribute:

Wo muss ich die Attribute (Sachdaten) eingeben?
-----------------------------------------------

Die Attribute (also die Sachdaten) für den neuen Datensatz sind im linken Seitenbereich einzugeben, in dem alle vorgesehenen Attribute in sinnvoller Reihenfolge untereinander aufgeführt sind, und zwar jeweils ausgestattet mit dem entsprechenden Eingabefeld: Dies kann ein Texteingabefeld sein, eine Auswahlliste, ein Kalender zur Datumsauswahl usw. – je nach Datentyp des entsprechenden Attributs.


.. _datensatz_anlegen_pflichtattribute:

Muss ich alle Attribute (Sachdaten) eingeben?
---------------------------------------------

Wenn ein Attribut *Pflicht* ist, seine Eingabe also unbedingt erforderlich ist, dann ist der Titel des Attributs **fett** hervorgehoben. Versuchen Sie den neuen Datensatz zu :ref:`speichern <datensatz_anlegen_speichern>`, ohne ein oder mehrere Pflichtattribute ausgefüllt zu haben, dann erscheint eine entsprechende Meldung und der Speichervorgang wird abgebrochen: Nun haben Sie die Möglichkeit, das/die Pflichtattribut(e) auszufüllen und den Speichervorgang danach erneut zu versuchen.


.. _datensatz_anlegen_syntax:

Woher weiß ich, ob ich Attribute (Sachdaten) korrekt eingegeben habe?
---------------------------------------------------------------------

Ob die *Syntax* von Attributen stimmt, ob Sie Attribute also korrekt eingegeben haben oder nicht, zeigt sich, wenn Sie versuchen den neuen Datensatz zu :ref:`speichern <datensatz_anlegen_speichern>`: Das/die Attribut(e), das/die nicht korrekt eingegeben worden ist/sind, wird/werden entsprechend hervorgehoben und mit detaillierten Hinweisen zur korrekten Eingabe versehen.


.. _datensatz_anlegen_oeffnungszeiten:

Wie gebe ich Öffnungszeiten (bzw. Betreuungs-, Lauf-, Leerungs-, Sprech- oder sonstige Zeiten) korrekt ein?
-----------------------------------------------------------------------------------------------------------

Die :ref:`Syntax-Prüfung <datensatz_anlegen_syntax>` greift auf Grund der hier gegebenen Komplexität **nicht**; stattdessen sind Sie selbst dafür verantwortlich Öffnungszeiten (bzw. Betreuungs-, Lauf-, Leerungs-, Sprech- oder sonstige Zeiten) korrekt einzugeben:

Grundsätzliches
^^^^^^^^^^^^^^^

Die Öffnungszeiten sind **einzeilig** einzutragen, es dürfen also keine Zeilenumbrüche oder Ähnliches verwendet werden. Für Wochentage und Monate werden die offiziellen **deutschsprachigen** Abkürzungen verwendet, also zum Beispiel *Di* für den Wochentag Dienstag, *Okt* für den Monat Oktober und *Mär* für den Monat März.

Beispiele
^^^^^^^^^

Vorab eininge einfache und komplexere Beispiele:

* ``24/7`` → geöffnet täglich rund um die Uhr
* ``08:00-02:00`` → geöffnet täglich von 8:00 bis 2:00 Uhr
* ``18:30+`` → geöffnet täglich ab 18:30 Uhr (bei unbekannter Schließzeit bzw. „open end“)
* ``Mo-Fr 06:30-17:00`` → geöffnet von Montag bis Freitag, jeweils von 6:30 bis 17:00 Uhr
* ``Sa-So 00:00-24:00`` → geöffnet am Wochenende rund um die Uhr
* ``Mo-Sa 06:30-17:00,19:00-21:00`` → geöffnet von Montag bis Freitag, jeweils von 6:30 bis 17:00 Uhr und von 19:00 bis 21:00 Uhr
* ``Mo-Fr 10:00-14:00; Sa 21:00+`` → geöffnet von Montag bis Freitag, jeweils von 10:00 bis 14:00 Uhr, sowie Samstag ab 21:00 Uhr (bei unbekannter Schließzeit bzw. „open end“)
* ``Mo-Mi 06:15-16:30; Do 08:00-17:30; Fr 10:00-14:00`` → geöffnet von Montag bis Mittwoch, jeweils von 6:15 bis 16:30 Uhr, Donnerstag, von 8:00 bis 17:30 Uhr, sowie Freitag, von 10:00 bis 14:00 Uhr
* ``Mo,Mi 06:15-16:30; Di,Do 08:00-17:30; Fr 10:00-14:00`` → geöffnet Montag und Mittwoch, jeweils von 6:15 bis 16:30 Uhr, Dienstag und Donnerstag, jeweils von 8:00 bis 17:30 Uhr, sowie Freitag, von 10:00 bis 14:00 Uhr
* ``Mo-Do 09:00-12:00; Mo 13:00-16:00; Di,Do 13:00-18:00`` → geöffnet von Montag bis Donnerstag, jeweils von 9:00 bis 12:00 Uhr, Montag, von 13:00 bis 16:00 Uhr, sowie Dienstag und Donnerstag, jeweils von 13:00 bis 18:00 Uhr
* ``Mo-Do 08:00-11:30,13:00-17:00; Fr 08:00-12:00,14:00-16:00; Sa 08:00-12:00`` → geöffnet von Montag bis Donnerstag, jeweils von 8:00 bis 11:30 Uhr und von 13:00 bis 17:00 Uhr, Freitag, von 8:00 bis 12:00 Uhr und von 14:00 bis 16:00 Uhr, sowie Samstag, von 8:00 bis 12:00 Uhr
* ``Mo-Di 09:45-18:00; Do-Fr 09:45-18:00`` → geöffnet von Montag bis Dienstag, jeweils von 9:45 bis 18:00 Uhr, sowie von Donnerstag bis Freitag, jeweils von 9:45 bis 18:00 Uhr
* ``Mo-Sa 07:00-18:30; Jun-Aug: Mo-Sa 07:00-21:00; So,Feiertag 07:00-18:00`` → geöffnet von Montag bis Samstag, jeweils von 07:00 bis 18:30 Uhr (von Juni bis August geöffnet von Montag bis Samstag, jeweils von 07:00 bis 21:00 Uhr), sowie Sonntag und an Feiertagen, jeweils von 07:00 bis 18:00 Uhr
* ``Jul-Aug: Mo-So 10:00-18:00; Apr-Jun,Sep-Okt: Di-So 10:00-18:00; Nov-Mär: Di-So 10:00-16:00`` → von Juli bis August geöffnet von Montag bis Sonntag, jeweils von 10:00 bis 18:00 Uhr, von April bis Juni und von September bis Oktober geöffnet von Dienstag bis Sonntag, jeweils von 10:00 bis 18:00 Uhr, sowie von November bis März geöffnet von Dienstag bis Sonntag, jeweils von 10:00 bis 16:00 Uhr
* ``Mo-Fr 07:00-18:30; Nov-Mar: So 07:00-18:30`` → geöffnet von Montag bis Freitag, jeweils von 07:00 bis 18:30 Uhr; von November bis März geöffnet auch Sonntag, von 07:00 bis 18:30 Uhr
* ``Mo-Fr 10:00-14:00; Schulferien: Mo-Fr 10:00-18:00`` → geöffnet von Montag bis Freitag, jeweils von 10:00 bis 14:00 Uhr; während der Schulferien geöffnet von Montag bis Freitag, jeweils von 10:00 bis 18:00 Uhr
* ``Mo-Fr 10:00-14:00; vorlesungsfreie Zeit: Mo-Fr,Events 10:00-18:00`` → geöffnet von Montag bis Freitag, jeweils von 10:00 bis 14:00 Uhr; während der vorlesungsfreien Zeit geöffnet von Montag bis Freitag, jeweils von 10:00 bis 18:00 Uhr, sowie bei Events, von 10:00 bis 18:00 Uhr
* ``30 Apr-04 Okt: 10:00-20:00`` → vom 30. April bis zum 4. Oktober geöffnet täglich von 10:00 bis 20:00 Uhr (eher bei Laufzeiten, zum Beispiel von Brunnen, relevant)
* ``Ostersonntag-03 Okt: 10:00-13:00`` → von Ostersonntag bis zum 3. Oktober geöffnet täglich von 10:00 bis 13:00 Uhr (eher bei Laufzeiten, zum Beispiel von Brunnen, relevant)
* ``Mo-Fr 11:30,12:00,15:00,17:30; Sa 11:00`` → geöffnet von Montag bis Freitag, jeweils um 11:30, 12:00, 15:00 und 17:30 Uhr, sowie Samstag, um 11:00 Uhr (eher bei Leerungszeiten, zum Beispiel von Postbriefkästen, relevant)
* ``Mo-Do 08:00-11:30,13:00-17:00; Fr nach Vereinbarung; Sa 08:00-12:00`` → geöffnet von Montag bis Donnerstag, jeweils von 8:00 bis 11:30 Uhr und von 13:00 bis 17:00 Uhr, Freitag, nach Vereinbarung, sowie Samstag, von 8:00 bis 12:00 Uhr
* ``Mai-Sep: So[2],So[3] 10:00-15:00`` → von Mai bis September geöffnet jeden 1. und 3. Sonntag im Monat, jeweils von 10:00 bis 15:00 Uhr 
* ``nach Vereinbarung`` → geöffnet nach Vereinbarung

Elemente
^^^^^^^^

Die folgenden Elemente können in der Syntax verwendet werden (in Klammern teilweise die Bedeutung):

* ``wd`` → Wochentag, verfügbare Werte: ``Mo`` (Montag), ``Di`` (Dienstag), ``Mi`` (Mittwoch), ``Do`` (Donnerstag), ``Fr`` (Freitag), ``Sa`` (Samstag), ``So`` (Sonntag) (Beispiel: ``Mo,Mi,Fr 10:00-12:00,14:00-16:00``)
* ``hh`` → Stunde, immer eine Nummer aus zwei Ziffern (im 24-Stunden-Format) in der Form ``hh:mm`` (Beispiel: ``Fr 14:00-15:00``)
* ``mm`` → Minute, immer eine Nummer aus zwei Ziffern in der Form ``hh:mm`` (Beispiel: ``Mo-Do 17:35-03:45``)
* ``mo`` → Monat, verfügbare Werte: ``Jan`` (Januar), ``Feb`` (Februar), ``Mär`` (März), ``Apr`` (April), ``Mai`` (Mai), ``Jun`` (Juni), ``Jul`` (Juli), ``Aug`` (August), ``Sep`` (September), ``Okt`` (Oktober), ``Nov`` (November) ``Dez`` (Dezember) (Beispiel: ``Dez-Mai: So 10:00-12:00,14:00-16:00``)
* ``md`` → Tag des Monats, immer eine Nummer aus zwei Ziffern in der Form ``md mo:`` (Beispiel: ``30 Apr-04 Okt: 10:00-20:00``)
* ``ph`` → Name eines bestimmten Feiertags, dient der Angabe von unterschiedlichen Öffnungszeiten an genau diesem Feiertag (Beispiel: ``Ostersonntag-03 Okt: 10:00-13:00``)
* ``wd[n]`` → n-ter Wochentag im Monat (Beispiel: ``Sa[2] 14:00-16:00``)
* ``Events`` → Events, dient der Angabe von unterschiedlichen Öffnungszeiten bei Events (Beispiel: ``Mo-Sa 07:00-18:30; So,Events 08:00-16:00``)
* ``Feiertag`` → Feiertag, dient der Angabe von unterschiedlichen Öffnungszeiten an gesetzlichen Feiertagen (Beispiel: ``Mo-Sa 07:00-18:30; So 07:00-18:00; Feiertag 08:00-16:00``)
* ``nach Vereinbarung`` → geöffnet nach Vereinbarung, dient der Angabe von unterschiedlichen Öffnungszeiten nach Vereinbarung (Beispiel: ``Mo-Do 08:00-11:30,13:00-17:00; Fr nach Vereinbarung; Sa 08:00-12:00``)
* ``Schulferien`` → Schulferien, dient der Angabe von unterschiedlichen Öffnungszeiten während der Schulferien (Beispiel: ``Mo-Sa 07:00-18:30; Schulferien: 08:00-19:00``)
* ``vorlesungsfreie Zeit`` → vorlesungsfreie Zeit, dient der Angabe von unterschiedlichen Öffnungszeiten während der vorlesungsfreien Zeit (Beispiel: ``Mo-Sa 07:00-18:30; vorlesungsfreie Zeit: 08:00-19:00``)

Allgemeine Syntax
^^^^^^^^^^^^^^^^^

* ``hh:mm-hh:mm`` → Angabe, die täglich gilt (Beispiel: ``10:00-16:00``)
* ``wd hh:mm-hh:mm`` → Angabe für einen Wochentag, gilt also für jeden dieser Wochentage im Jahr (Beispiel: ``Fr 08:30-20:00``)
* ``md mo: hh:mm-hh:mm`` → Angabe für einen bestimmten Tag in einem bestimmten Monat (Beispiel: ``24 Dez: 08:30-20:00``)
* ``mo: hh:mm-hh:mm`` → Angabe für einen Monat (Beispiel: ``Dez: 08:30-20:00``)

Zusätzliche Regeln
^^^^^^^^^^^^^^^^^^

* Bereiche:

    * aufeinanderfolgende Stunden getrennt durch „-“ (Beispiel: ``08:30-20:00``)
    * aufeinanderfolgende Wochentage getrennt durch „-“ (Beispiel: ``Mo-Do``)
    * aufeinanderfolgende Tage im Monat getrennt durch „-“ (Beispiele: ``20-24 Dez``, ``24 Dez-06 Jan``)
    
* Lücken in den Bereichen, also mehrere einzelne Bereiche angeben:

    * einzelne Stundenbereiche getrennt durch „,“ (Beispiel: ``08:30-14:00,16:30-20:00``)
    * einzelne Tage getrennt durch „,“ (Beispiel: ``Mo,Di,Do``)
    
* verschiedene Stunden an verschiedenen Tagen werden getrennt durch „;“ (Beispiel: ``Mo 10:00-12:00,12:30-15:00; Di-Fr 08:00-12:00,12:30-15:00; Sa 08:00-12:00``)
* Ausnahmen zu einem Bereich von Tagen: erst der Bereich, dann die Ausnahme (Beispiel: ``Mo-Sa 10:00-20:00; Di 10:00-14:00``)
* Falls sich die Ausnahme am Rand des Bereiches befindet (erster oder letzter Tag), dann sollte man nicht die Ausnahmeregelung benutzten, sondern es direkt richtig angeben (Beispiel: ``Mo-Fr 10:00-20:00; Sa 10:00-14:00``)
* Für 24-Stunden-Öffnung ``00:00-24:00`` angeben, für 24-Stunden-Öffnung 7 Tage die Woche kann der spezielle Wert ``24/7`` angegeben werden.
* Bei Öffnungszeiten ohne Schließzeiten, wie etwa „22:00 Uhr bis open end“ oder „Sonntag ab 9:00 Uhr“, wird der Startzeit ein „+“ angehängt (Beispiele: ``22:00+``, ``So 09:00-14:00,19:00+``)

Häufig gemachte Fehler
^^^^^^^^^^^^^^^^^^^^^^

* ``7/8-23`` (Fehler) → ``Mo-So 08:00-23:00`` (korrekt)
* ``0600-1800`` (Fehler) → ``06:00-18:00`` (korrekt)
* ``07;00-14;00`` (Fehler) → ``07:00-14:00`` (korrekt)
* ``07:00 - 14:00 Uhr`` (Fehler) → ``07:00-14:00`` (korrekt)
* ``08.00-16.00, ferien 03.00`` (Fehler) → ``08:00-16:00; Schulferien: 08:00-03:00`` (korrekt)
* ``10:00 - 13:30 / 17:00 - 20:30`` (Fehler) → ``10:00-13:30,17:00-20:30`` (korrekt)
* ``10:00-13:30 u. 17:00-20:30`` (Fehler) → ``10:00-13:30,17:00-20:30`` (korrekt)
* ``April-September; Mo-Fr 09:00-13:00, 14:00-18:00, Sa 10:00-13:00`` (Fehler) → ``Apr-Sep: Mo-Fr 09:00-13:00,14:00-18:00; Apr-Sep: Sa 10:00-13:00`` (korrekt)
* ``MoMiDoFr: 1200-1800; SaSo: 1200-1700`` (Fehler) → ``Mo,Mi,Do,Fr 12:00-18:00; Sa-So 12:00-17:00`` (korrekt)


.. _datensatz_anlegen_karte:

Wozu dient die Karte?
---------------------

Jeder Datensatz **muss** :ref:`verortet <datensatz_anlegen_verorten>`, also auf der Karte markiert werden. In der Regel geschieht dies über einen Marker, der auf einem bestimmten Punkt liegt. Falls ein Datenthema hingegen aus linien- oder flächenhaft repräsentierten Datensätzen besteht, geschieht dies nicht über einen Marker, sondern über eine Linie oder eine Fläche, die die Geometrie des Datensatzes darstellt (zum Beispiel würde in einem Datenthema *Fließgewässer* ein Datensatz stets den Verlauf des Fließgewässers durch eine Linie darstellen; in einem Datenthema *Gebäude* würde ein Datensatz stets den Umriss des Gebäudes durch eine Fläche darstellen).

Bei manchen Datenthemen ist es sogar so, dass deren Datensätze durch **mehrteilige** Punkte, Linien oder Flächen repräsentiert werden, also durch sogenannte *Multi*-Punkte, -Linien oder -Flächen


.. _datensatz_anlegen_karte_navigieren:

Wie kann ich in der Karte navigieren?
-------------------------------------

Das können Sie :ref:`hier <karte_navigieren>` nachlesen.


.. _datensatz_anlegen_karte_hintergrund:

Wie kann ich in den Kartenhintergrund bzw. die Hintergrundkarte wechseln?
-------------------------------------------------------------------------

Das können Sie :ref:`hier <karte_hintergrund>` nachlesen.


.. _datensatz_anlegen_verorten:

Wie kann ich den neuen Datensatz auf der Karte verorten (Punkte)?
-----------------------------------------------------------------

Wie bereits erwähnt **muss** jeder Datensatz verortet, also auf der Karte markiert werden. Da die meisten Datenthemen aus punkthaft repräsentierten Datensätzen bestehen, ist diese Verortung in der Regel ganz einfach: Sie :ref:`navigieren <karte_navigieren>` in der Karte an die gewünschte Stelle, klicken auf den Button mit dem Marker-Symbol links oben in der Karte und klicken dann an den gewünschten Punkt in der Karte, an dem der Marker liegen soll.

Wird ein Datensatz durch **mehrteilige** Punkte repräsentiert, **kann** man den zuvor beschriebenen Vorgang übrigens beliebig oft wiederholen.

Die Verortung ist **immer** Pflicht: Versuchen Sie den neuen Datensatz zu :ref:`speichern <datensatz_anlegen_speichern>`, ohne die Verortung vorgenommen zu haben, dann erscheint eine entsprechende Meldung und der Speichervorgang wird abgebrochen: Nun haben Sie die Möglichkeit, die Verortung durchzuführen und den Speichervorgang danach erneut zu versuchen.

**Tipp:** Bei Datenthemen aus punkthaft repräsentierten Datensätzen können Sie auch verorten, indem Sie das Eingabefeld unterhalb der Karte als :ref:`Suchfeld nutzen <karte_adressensuche>` und dann auf den Button *Marker setzen* klicken: Der Marker wird dann genau auf die gewünschte Adresse (falls der betreffende Datensatz eine Referenz zu einer Adresse vorsieht) oder die geometrische Mitte der gewünschten Straße (falls der betreffende Datensatz eine Referenz zu einer Straße vorsieht) gesetzt.


.. _datensatz_anlegen_verorten_linie:

Wie kann ich den neuen Datensatz auf der Karte verorten (Linien)?
-----------------------------------------------------------------

Wenn ein Datenthema aus linienhaft repräsentierten Datensätzen besteht, ist die Verortung etwas aufwendiger als für Punkte, aber immer noch sehr einfach: Sie :ref:`navigieren <karte_navigieren>` in der Karte an die gewünschte Stelle und klicken auf den Button mit dem Linien-Symbol links oben in der Karte. Daraufhin können Sie durch Klicks in die Karte Ihre Linie fortlaufend (also Stützpunkt für Stützpunkt) zeichnen. Um die Linie abzuschließen, klicken Sie für den letzten Stützpunkt doppelt.

Wird ein Datensatz durch **mehrteilige** Linien repräsentiert, **kann** man den zuvor beschriebenen Vorgang übrigens beliebig oft wiederholen.

Die Verortung ist **immer** Pflicht: Versuchen Sie den neuen Datensatz zu :ref:`speichern <datensatz_anlegen_speichern>`, ohne die Verortung vorgenommen zu haben, dann erscheint eine entsprechende Meldung und der Speichervorgang wird abgebrochen: Nun haben Sie die Möglichkeit, die Verortung durchzuführen und den Speichervorgang danach erneut zu versuchen.

**Tipp:** Eine vorhandene Linie können Sie auch nachträglich bearbeiten, indem Sie den Button mit dem Bleistift-Symbol links oben in der Karte klicken: Die einzelnen Stützpunkte der Linie sind jetzt anfassbar und verschiebbar. Sobald Sie mit dem Resultat zufrieden sind, klicken Sie auf den Button *Sichern*. Oder klicken Sie auf *Abbrechen*, um die Bearbeitung zu verwerfen.


.. _datensatz_anlegen_verorten_flaeche:

Wie kann ich den neuen Datensatz auf der Karte verorten (Fläche)?
-----------------------------------------------------------------

Wenn ein Datenthema aus flächenhaft repräsentierten Datensätzen besteht, ist die Verortung etwas aufwendiger als für Punkte, aber immer noch sehr einfach: Sie :ref:`navigieren <karte_navigieren>` in der Karte an die gewünschte Stelle und klicken auf den Button mit dem Polygon-Symbol links oben in der Karte. Daraufhin können Sie durch Klicks in die Karte Ihre Fläche fortlaufend (also Stützpunkt für Stützpunkt) zeichnen. Um die Fläche abzuschließen, klicken Sie zuletzt den ersten Stützpunkt nochmals an.

Wird ein Datensatz durch **mehrteilige** Flächen repräsentiert, **kann** man den zuvor beschriebenen Vorgang übrigens beliebig oft wiederholen.

Die Verortung ist **immer** Pflicht: Versuchen Sie den neuen Datensatz zu :ref:`speichern <datensatz_anlegen_speichern>`, ohne die Verortung vorgenommen zu haben, dann erscheint eine entsprechende Meldung und der Speichervorgang wird abgebrochen: Nun haben Sie die Möglichkeit, die Verortung durchzuführen und den Speichervorgang danach erneut zu versuchen.

**Tipp:** Statt einer frei zeichenbaren Fläche können Sie auch ein einfaches Rechteck aufziehen, indem Sie statt des Buttons mit dem Polygon-Symbol links oben in der Karte den Button mit dem Rechteck-Symbol wählen.

**Tipp:** Eine vorhandene Fläche können Sie auch nachträglich bearbeiten, indem Sie den Button mit dem Bleistift-Symbol links oben in der Karte klicken: Die einzelnen Stützpunkte der Fläche sind jetzt anfassbar und verschiebbar. Sobald Sie mit dem Resultat zufrieden sind, klicken Sie auf den Button *Sichern*. Oder klicken Sie auf *Abbrechen*, um die Bearbeitung zu verwerfen.


.. _datensatz_anlegen_adresse:

Wie funktioniert das Attribut *Adresse*?
----------------------------------------

Falls der betreffende Datensatz eine Referenz zu einer Adresse vorsieht und diese Pflicht ist, wird bei der :ref:`Verortung <datensatz_anlegen_verorten>` automatisch die dem Punkt der Verortung nächstgelegene Adresse bestimmt und in das Attribut *Adresse* eingetragen.

Sofern die Referenz zu einer Adresse keine Pflicht ist, sondern optional, wird das Attribut *Adresse* nicht automatisch ausgefüllt. Stattdessen können Sie, wenn Sie möchten, mittels des Buttons *Adresse übernehmen* die der aktuellen Verortung in der Karte nächstgelegene Adresse in das Attribut *Adresse* eintragen lassen.


.. _datensatz_anlegen_strasse:

Wie funktioniert das Attribut *Straße*?
---------------------------------------

Falls der betreffende Datensatz eine Referenz zu einer Straße vorsieht und diese Pflicht ist, wird bei der :ref:`Verortung <datensatz_anlegen_verorten>` automatisch die dem Punkt der Verortung nächstgelegene Straße bestimmt und in das Attribut *Straße* eingetragen.

Sofern die Referenz zu einer Straße keine Pflicht ist, sondern optional, wird das Attribut *Straße* nicht automatisch ausgefüllt. Stattdessen können Sie, wenn Sie möchten, mittels des Buttons *Straße übernehmen* die der aktuellen Verortung in der Karte nächstgelegene Straße in das Attribut *Straße* eintragen lassen.


.. _datensatz_anlegen_speichern:

Wie kann ich den neuen Datensatz speichern?
-------------------------------------------

Sie können den neuen Datensatz speichern, indem Sie auf den orangen Button *speichern* links unten auf der Seite klicken.
