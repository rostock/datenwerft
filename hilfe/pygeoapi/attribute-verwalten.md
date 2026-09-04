# *pygeoapi*-Konfiguration → Attribute verwalten

Auf der **Änderungsseite einer Kollektion** steht unterhalb der bisherigen
Felder eine Tabelle mit allen Attributen dieser Kollektion. Sie beantwortet an
einer Stelle die Frage, **welche Attribute** eine Kollektion hat und **wer sie
lesen darf.**

In der Spalte **zugewiesene Rollen** wird die Rechtelage auch **gepflegt:** Dort
lassen sich Rollen zuweisen und entziehen. Wirksam wird beides erst mit dem
**Sichern** der Kollektion.

## Die Spalten

| Spalte | Bedeutung |
| ------ | --------- |
| **Name des Attributs** | Der Name, unter dem das Attribut in der Quelltabelle beziehungsweise im Quell-View steht. |
| **Datentyp in der Quelle** | Der Datentyp in der Schreibweise der Quelldatenbank, zum Beispiel `text` oder `integer`. |
| **Hinweis** | Besonderheiten des Attributs, siehe unten. Bei einem Attribut ohne jede Rolle steht hier immer etwas. |
| **zugewiesene Rollen** | Alle Rollen, die dieses Attribut lesen dürfen – und das Feld, über das sie vergeben werden. |

Die Zeilen sind **alphabetisch nach dem Attributnamen** sortiert. Bei
unveränderter Datenlage sieht die Tabelle bei jedem Aufruf gleich aus.

## Attribute abgleichen

Über der Tabelle steht der Knopf **Attribute abgleichen.** Er holt die aktuelle
Spaltenliste der Quelltabelle und schreibt sie ins
[Attributinventar](attributinventar.md). Das ist der Weg, auf dem die Tabelle
überhaupt Zeilen bekommt – und der Weg, auf dem sie aktuell bleibt, wenn sich die
Quelltabelle geändert hat.

Der Abgleich **sichert die Kollektion mit.** Wer vorher etwas geändert hat – eine
Rollenzuweisung, ein Feld oben im Formular –, sichert es damit ebenfalls. Danach
bleibt die Maske auf der Änderungsseite, sodass die Tabelle den neuen Stand
zeigt.

Abgeglichen wird gegen **Datenbankverbindung, Schema und Tabelle/View, wie sie
gerade im Formular stehen** – nicht gegen den zuletzt gesicherten Stand. Wer eine
Kollektion auf eine andere Tabelle umstellt, kann also umstellen und in einem
Schritt abgleichen. Sind die drei Angaben leer, weist ein Hinweis am Knopf darauf
hin und es passiert nichts.

### Was der Abgleich zurückmeldet

Oben erscheint eine Meldung mit vier Zahlen:

| Zahl | Bedeutung |
| ---- | --------- |
| **neu aufgenommen** | Spalten, die die Quelle hat und das Inventar noch nicht. Sie sind ohne Zutun **rechtefrei** – hier steht die Rechtevergabe noch aus. |
| **als „nicht mehr vorhanden" gekennzeichnet** | Attribute, die das Inventar führt, die Quelle aber nicht mehr hat. Sie werden **nicht gelöscht.** |
| **wieder aufgetaucht** | Attribute, die als „nicht mehr vorhanden" gekennzeichnet waren und in der Quelle wieder da sind. |
| **Datentyp aktualisiert** | Attribute, deren Datentyp sich in der Quelle geändert hat. |

Hat sich nichts geändert, steht dort **„Der Abgleich hat keine Änderung
ergeben."** Ein zweiter Abgleich ohne Änderung in der Quelle meldet also nichts
und fasst das Inventar nicht an.

Die **Namen** stehen nicht in der Meldung – sie stehen in der Tabelle, die direkt
darunter den neuen Stand zeigt. Vollständig nachvollziehbar ist jeder Abgleich in
der **Objekt-Historie** (siehe unten); ein Abgleich ohne Änderung erzeugt dort
keinen Eintrag.

> **Vergebene Leserechte überlebt jeder Abgleich.** Das gilt auch für ein
> Attribut, das gerade als „nicht mehr vorhanden" gekennzeichnet wurde, und für
> eines, das wieder aufgetaucht ist: Es ist dieselbe Zeile mit denselben Rollen,
> nicht eine neue ohne. Ein versehentlich gelöschtes und wiederhergestelltes
> Attribut kommt deshalb nicht rechtefrei zurück.

Ein Attribut, das als „nicht mehr vorhanden" gekennzeichnet ist, behält auch
seinen **zuletzt ermittelten Datentyp.** Lässt sich für ein Attribut kein Typ
ermitteln, bleibt die Spalte *Datentyp in der Quelle* **leer** – dort steht nie
ein Ersatzwert, der einen Typ vortäuscht.

### Wenn keine Spaltenliste ermittelt werden kann

Am Knopf erscheint ein Hinweis, der die Ursache so genau benennt, wie sie sich
unterscheiden lässt:

| Hinweis | Was dahintersteckt |
| ------- | ------------------ |
| **„Die Quelle antwortet nicht."** | Die Anfrage kam gar nicht durch – Datenbank nicht erreichbar, Netz weg oder Server nicht ansprechbar. |
| **„Die Spaltenauskunft meldet einen Fehler."** | Die Anfrage kam an, die Antwort war aber fehlerhaft – etwa falsche Zugangsdaten in der Datenbankverbindung oder eine nicht lesbare Antwort. |
| **„Die Quelle liefert keine Spalten – bitte Schema und Tabelle/View prüfen."** | Die Quelle war erreichbar und hat geantwortet, kennt die angegebene Tabelle/View aber nicht (oder sie hat keine Spalten). |

Jeder dieser Hinweise endet mit **„Das Attributinventar bleibt unverändert."**
Aus Sicherheitsgründen nennt keiner davon Host, Benutzername oder Passwort der
Datenbankverbindung.

Das Inventar bleibt dann genau so, wie es war. Ein leeres Ergebnis wird
**ausdrücklich nicht** als „alle Attribute sind verschwunden" gedeutet – sonst
verlöre eine kurzzeitig unerreichbare Datenbank die ganze Rechtelage aus dem
Blick. Prüfen Sie in diesem Fall Datenbankverbindung, Schema und Tabelle oben im
Formular und stoßen Sie den Abgleich erneut an.

Wird die Kollektion in diesem Fall gar nicht erst gesichert, ist das gewollt: Ein
Sichern ohne Ergebnis brächte nichts.

### Grenzen

- Der Abgleich läuft **je Kollektion** und wird von Hand angestoßen. Es gibt
  keinen Zeitplan und keinen Abgleich über alle Kollektionen in einem Schritt.
- Er **liest** die Quelle nur. Weder Daten noch Struktur der Quelldatenbank
  werden verändert.
- Er vergibt **keine Rechte.** Neu aufgenommene Attribute sind rechtefrei und
  werden beim nächsten Aufruf der Maske als *„von keiner Rolle lesbar"*
  gekennzeichnet.
- Die Spaltenliste ist auf **100 Einträge** begrenzt. Eine breitere Quelltabelle
  wird mit einer Meldung abgelehnt statt teilweise übernommen. Die Meldung nennt
  die gerade geltende Zahl; die Grenze ist eine Einstellung und kann für Ihre
  Installation heraufgesetzt werden – melden Sie den Fall.

#### Wenn JavaScript abgeschaltet ist

Der Knopf wird vollständig im Browser bedient. Ist JavaScript abgeschaltet,
**passiert beim Klick nichts.** Verloren geht dabei nichts, es fehlt nur der
Einstieg – wie bei der Suche unten.

## Ein Attribut suchen

Über der Tabelle steht das Feld **Attribut suchen.** Eine Eingabe dort grenzt die
Tabelle auf die Attribute ein, deren **Name** die Eingabe enthält. Das ist
gedacht für Kollektionen mit vielen Attributen, wo Scrollen zu langsam ist und
leicht die falsche Zeile trifft.

- Gesucht wird nach einem **Teil** des Namens: `stra` findet `strasse` und
  `strassenname`.
- **Groß- und Kleinschreibung** spielt keine Rolle.
- Neben dem Feld steht, wie viele Attribute gerade angezeigt werden.
- **Zurücksetzen** leert das Feld und zeigt wieder alle Attribute.
- **Enter** im Suchfeld sichert die Kollektion **nicht** – es passiert nichts.

Passt zur Eingabe kein Attribut, erscheint statt einer kommentarlos leeren
Tabelle der Hinweis, dass kein Attribut die Eingabe enthält.

> **Ausgeblendete Zeilen werden mitgespeichert.** Die Suche blendet Zeilen nur
> aus – sie entfernt sie nicht. Wer bei aktiver Suche eine Rolle ändert und dann
> sichert, ändert **genau diese** Zeile; alle ausgeblendeten Attribute behalten
> ihre Rollen unverändert.

Die Suche allein ändert also nichts: Filtern, zurücksetzen und sichern, ohne
sonst etwas anzufassen, lässt die Rechtelage genau so, wie sie war.

Gesucht wird **ausschließlich** über den Attributnamen. Eine Suche nach einer
zugewiesenen Rolle – etwa *„zeige alle Attribute, die Rolle X lesen darf"* – gibt
es hier nicht.

### Wenn JavaScript abgeschaltet ist

Die Suche läuft vollständig im Browser. Ist JavaScript abgeschaltet, **filtert
das Feld nicht** – die Tabelle zeigt dann durchgehend alle Attribute. Verloren
geht dabei nichts; es fehlt nur die Eingrenzung.

Die Maske ist ohne JavaScript ohnehin nur eingeschränkt bedienbar (siehe unten).
Arbeiten Sie deshalb mit eingeschaltetem JavaScript.

## Eine leere Rollen-Spalte

Bleibt die Spalte **zugewiesene Rollen** bei einem Attribut leer, dann darf es
**keine** Rolle lesen. Das ist der Normalzustand: Ein Attribut wird erst
lesbar, wenn ausdrücklich ein [Leserecht](leserechte.md) vergeben wird.

Es steht dort bewusst **kein** Platzhalterzeichen, damit nichts als Rollenname
missverstanden werden kann. Solange keine Rolle zugewiesen ist, steht im Feld
der Hinweis *„Rolle zuweisen …".*

Damit dieser Zustand nicht unbemerkt bleibt, wird er an zwei Stellen
ausgewiesen: in der Spalte **Hinweis** mit *„von keiner Rolle lesbar"* und beim
**Sichern** durch eine Meldung, die die betroffenen Attribute benennt. Beides
ist kein Fehler, sondern eine Erinnerung.

## Eine Rolle zuweisen

In das Feld der gewünschten Zeile klicken und die Rolle aus der Liste wählen.
Tippen grenzt die Liste ein.

Auswählbar sind **ausschließlich** Rollen aus dem
[Rollenkatalog](rollenkatalog.md). Eine freie Texteingabe legt **keine** Rolle
an – wer eine noch nicht vorhandene Rolle braucht, muss sie zuerst im Katalog
anlegen.

Ein Attribut darf beliebig viele Rollen haben. Eine bereits zugewiesene Rolle
lässt sich nicht ein zweites Mal auswählen; ein doppelter Eintrag kann so gar
nicht erst entstehen.

## Eine Rolle entziehen

Jede zugewiesene Rolle erscheint als eigenes Feldchen mit einem **✕** links.
Ein Klick darauf entzieht das Recht – aber erst nach einer **Rückfrage**, die
Rolle und Attribut benennt.

Das ist Absicht: Ein versehentlicher Entzug kann einen Dienst für eine ganze
Nutzergruppe unbrauchbar machen.

- **Abbrechen** – die Zuweisung bleibt unverändert stehen.
- **OK** – das Feldchen verschwindet aus der Zeile.

> **Die Rückfrage bestätigt die Absicht, nicht das Schreiben.** Auch nach einem
> **OK** ist noch nichts geändert. Erst **Sichern** schreibt den Entzug.

Ein Entzug wirkt **nur** auf die gewählte Kombination aus Attribut und Rolle.
Andere Rollen an demselben Attribut und dieselbe Rolle an anderen Attributen
bleiben unberührt.

### Wenn keine Rückfrage erscheint

Manche Browser bieten in solchen Dialogen an, *„diese Seite keine weiteren
Dialoge erstellen zu lassen".* Wurde das angekreuzt, gilt die Rückfrage als
abgelehnt und **Entzüge funktionieren nicht mehr** – das Feldchen bleibt beim
Klick einfach stehen. Abhilfe: die Seite in einem neuen Tab öffnen oder die
Einstellung im Browser zurücksetzen.

Der Fehlerfall geht damit immer in die sichere Richtung: Im Zweifel bleibt ein
Recht bestehen, statt still zu verschwinden.

### Wenn JavaScript abgeschaltet ist

Die Rückfrage läuft im Browser. Ist JavaScript abgeschaltet, erscheint sie
**nicht** – ein Entzug wird dann ohne Nachfrage übernommen, sobald Sie sichern.

Die Maske ist ohne JavaScript ohnehin nur eingeschränkt bedienbar: Auch die
Auswahllisten für Schema, Tabelle und die Attribute darüber füllen sich nicht.
Arbeiten Sie deshalb mit eingeschaltetem JavaScript.

## Änderungen verwerfen

Alle Zuweisungen und Entzüge stehen bis zum **Sichern** nur im Formular. Wer die
Seite verlässt oder neu lädt, ohne zu sichern, verwirft sie vollständig – die
Rechtelage bleibt dann exakt so, wie sie war.

> **Es gibt keine Warnung beim Verlassen der Seite.** Ungespeicherte Änderungen
> gehen ohne Rückfrage verloren.

Schlägt das Sichern fehl – etwa weil im oberen Teil des Formulars eine Angabe
fehlt –, wird **nichts** geschrieben. Es entsteht kein Zustand, in dem ein Teil
der Änderungen gespeichert ist und ein anderer nicht.

## Gesperrte Zeilen

Beim **ID-Attribut** und beim **Geometrie-Attribut** ist das Feld nicht
bedienbar. Diese beiden werden von den Diensten unabhängig von allen Leserechten
ausgeliefert; eine Zuweisung wäre wirkungslos. Näheres unter
[Leserechte](leserechte.md).

## Die Hinweise

**„nicht mehr vorhanden"** – Das Attribut steht im
[Attributinventar](attributinventar.md), wurde in der Quelltabelle aber nicht
mehr gefunden. Die Zeile wird trotzdem angezeigt und die bisher vergebenen
Rollen bleiben sichtbar: Sie sollen nicht stillschweigend verschwinden, falls
die Spalte in der Quelle zurückkehrt. Solange das Attribut fehlt, geben die
Dienste dazu nichts heraus.

**„immer ausgeliefert"** – Das Attribut ist das **ID-Attribut** oder das
**Geometrie-Attribut** der Kollektion. Diese beiden tragen die Kollektion
technisch und werden von den Diensten unabhängig von allen Leserechten
herausgegeben. Ein Leserecht darauf hätte keine Wirkung.

Das **Bezeichnungs-Attribut** trägt diesen Hinweis **nicht.** Es ist ein
gewöhnliches Attribut und ohne Leserecht nicht lesbar – eine Kollektion bleibt
dann gültig, zeigt aber keine Bezeichnung.

**„wirkungsloses Recht"** – Die Zeile ist gesperrt und trägt trotzdem noch eine
Rolle. Das entsteht, wenn das ID- oder Geometrie-Attribut einer Kollektion
**nachträglich umbenannt** wird: Ein zuvor regulär vergebenes Recht fällt dadurch
auf eine Zeile, die nun als strukturell gilt.

Das Recht ist folgenlos, aber es soll nicht unbemerkt liegen bleiben. Weil die
Zeile gesperrt ist, lässt es sich über die Maske auch nicht mehr entfernen. Weg
zurück: den Attributnamen bei der Kollektion zurücksetzen; danach ist die Zeile
wieder eine gewöhnliche und das Recht entziehbar.

**„von keiner Rolle lesbar"** – Dem Attribut ist **keine einzige** Rolle
zugewiesen. Das ist der **Normalzustand** eines neuen Attributs und **kein
Fehler:** Ein Attribut wird erst lesbar, wenn ausdrücklich ein Leserecht vergeben
wird. Der Hinweis erinnert nur daran, dass hier noch eine Entscheidung aussteht.

Beim **ID-Attribut** und beim **Geometrie-Attribut** erscheint er **nie** – die
beiden haben planmäßig keine Rolle und werden trotzdem ausgeliefert.

Zusammen mit *„nicht mehr vorhanden"* kann er auftreten. Das Attribut wird dann
**nicht** in der Meldung beim Sichern genannt: Solange die Spalte in der Quelle
fehlt, gibt der Dienst ohnehin nichts dazu heraus, es ist also nichts zu tun.

Der Hinweis wird beim **Aufbau der Seite** berechnet. Wer eine Rolle zuweist,
sieht ihn deshalb erst nach dem **Sichern** verschwinden, nicht schon beim
Auswählen.

Auf ein Attribut können mehrere Hinweise zugleich zutreffen.

## Die Meldung beim Sichern

Enthält eine Kollektion beim **Sichern** mindestens ein Attribut ohne jede Rolle,
erscheint oben eine **gelbe Meldung.** Sie nennt

- die **Anzahl** der betroffenen Attribute,
- ihre **Namen** – bei mehr als zehn die ersten zehn und dazu, wie viele weitere
  es sind; die vollständige Liste steht in der Spalte *Hinweis* – und
- den Zusatz **„Gespeichert wurde trotzdem alles."**

Das ist **keine Fehlermeldung.** Die Kollektion ist vollständig gespeichert,
einschließlich aller Zuweisungen und Entzüge desselben Vorgangs. Wer in genau
diesem Vorgang das letzte Recht eines Attributs entzieht, findet es in der
Meldung wieder; wer eines vergibt, nicht mehr.

> **Die Warnung steht über der grünen Erfolgsmeldung.** Beide gelten: gewarnt
> **und** gespeichert.

Nicht genannt werden das **ID-** und das **Geometrie-Attribut** sowie Attribute,
die **nicht mehr vorhanden** sind. Hat jedes übrige Attribut mindestens eine
Rolle, erscheint keine Meldung.

### Warnung statt Sperre

Das Speichern wird **nicht** blockiert – bewusst, obwohl die ursprüngliche
Anforderung eine Sperre vorsah.

Eine Sperre würde sich selbst im Weg stehen: Ein Attribut, das der
[Abgleich](attributinventar.md) neu ins Inventar aufnimmt, entsteht
zwangsläufig **ohne** Rolle. Eine Sperre würde damit genau den Abgleich
verhindern, der solche Attribute überhaupt erst einträgt – und ließe sich nur
umgehen, indem man vorab Rechte vergibt, die man vielleicht gar nicht vergeben
will. Verweigerung ist der [Normalzustand](leserechte.md), kein Fehlerzustand;
darum wird er sichtbar gemacht statt erzwungen.

## Änderungen sind nachvollziehbar

Jede Zuweisung und jeder Entzug erscheint in der **Objekt-Historie** der
Kollektion – erreichbar über **Geschichte** oben rechts. Festgehalten werden
Zeitpunkt, ausführende Person sowie Attribut, Rolle und Richtung
(*zugewiesen* oder *entzogen*).

Auch jeder **Abgleich** erscheint dort, mit den Namen der Attribute je Kategorie
(*aufgenommen*, *nicht mehr vorhanden*, *wieder aufgetaucht*, *Datentyp
aktualisiert*).

Ein Speichervorgang, bei dem sich an der Rechtelage nichts geändert hat, und ein
Abgleich ohne Änderung erzeugen dazu **keinen** Eintrag.

## Wenn noch keine Attribute bekannt sind

Steht statt der Tabelle der Hinweis **„Noch kein Attributinventar – der
Abgleich steht aus"**, dann ist für diese Kollektion noch nicht ermittelt
worden, welche Attribute ihre Quelle hat. Das ist kein Fehler.

Abhilfe ist der Knopf **Attribute abgleichen** (siehe oben) – er steht auch in
diesem Fall über dem Hinweis. Solange kein Attribut im Inventar steht, gibt es
nichts, woran eine Rolle vergeben werden könnte, und die Spalte *Datentyp in der
Quelle* bleibt leer.

Beim Sichern erscheint dann auch **keine** Meldung über Attribute ohne Rolle –
es gibt keine, die sie betreffen könnte.

## Beim Anlegen einer neuen Kollektion

Auf der Anlageseite erscheinen die Tabelle und der Abgleich **nicht.** Welche
Attribute eine Kollektion hat, lässt sich erst ermitteln, wenn
Datenbankverbindung, Schema und Tabelle gespeichert sind. Es entsteht deshalb auch
kein Zustand, in dem Rechte an einer noch nicht existierenden Kollektion vergeben
würden. Nach dem ersten Sichern steht der Knopf auf der Änderungsseite bereit.

Das erste Sichern meldet folglich auch keine Attribute ohne Rolle. Sobald das
Inventar gefüllt ist, tut das nächste Sichern es.

## Wer die Tabelle sieht und pflegen darf

Dieselben Personen, die auch sonst die *pygeoapi*-Konfiguration pflegen dürfen:
die Mitglieder der Gruppe `PYGEOAPI_GROUP_NAME` (siehe
[Berechtigungen](permissions.md)). Wer nicht in dieser Gruppe ist, erreicht
schon die Änderungsseite der Kollektion nicht und kann damit weder zuweisen noch
entziehen noch einen Abgleich anstoßen.

Die Tabelle zeigt die **Struktur der Quelltabelle** – auch das ist ein Grund,
den Kreis der Gruppenmitglieder klein zu halten.
