# *pygeoapi*-Konfiguration → Leserechte

Ein **Leserecht** ist die Verbindung einer [Rolle](rollenkatalog.md) mit einem
Eintrag des [Attributinventars](attributinventar.md) einer Kollektion. Besteht
diese Verbindung, darf die Rolle das Attribut lesen; besteht sie nicht, darf sie
es nicht.

Es gibt ausschließlich **„erlauben"** – ein „verweigern" existiert nicht und wird
nicht gebraucht: Verweigerung ist der Normalzustand. Damit kann ein Recht auch
nicht versehentlich durch eine falsch gesetzte Kennzeichnung entstehen.

## Eindeutigkeit

Je Rolle und Attribut existiert **höchstens ein** Leserecht. Der Versuch, dasselbe
Recht ein zweites Mal zu vergeben, wird abgelehnt. Umgekehrt gilt: dieselbe Rolle
darf Rechte an beliebig vielen Attributen haben, und dasselbe Attribut darf für
beliebig viele Rollen lesbar sein.

Über die [Attributübersicht](attribute-verwalten.md) kann eine doppelte Vergabe
gar nicht erst entstehen: Eine bereits zugewiesene Rolle steht dort nicht noch
einmal zur Auswahl. Die Regel greift damit vor allem gegen Zugriffe an der Maske
vorbei.

## Ein Attribut ohne jede Rolle

Solange einem Attribut **keine** Rolle zugewiesen ist, darf es niemand lesen. Das
ist der beabsichtigte Ausgangszustand jedes neuen Attributs und kein Fehler.

Unbemerkt bleiben soll er trotzdem nicht: Sonst fehlt ein neu hinzugekommenes
Attribut nach der Veröffentlichung stillschweigend in allen Antworten, und die
Ursache wird erst bei der Fehlersuche im laufenden Betrieb gefunden. Die
[Attributübersicht](attribute-verwalten.md) weist solche Attribute deshalb mit
**„von keiner Rolle lesbar"** aus und benennt sie beim Sichern in einer Meldung.
Gespeichert wird trotzdem – die Begründung steht dort unter *„Warnung statt
Sperre"*.

## Nicht mehr vorhandene Attribute

Verschwindet ein Attribut aus der Quelle (Kennzeichnung **„in der Quelle
vorhanden"** = nein), bleibt ein daran vergebenes Leserecht **erhalten**, wirkt
aber **nicht**. Kehrt die Spalte zurück, wird das Recht wieder wirksam, ohne dass
es erneut vergeben werden muss.

## Löschverhalten

Leserechte werden **mitgelöscht**, wenn

- die **Rolle** gelöscht wird (siehe [Rollenkatalog](rollenkatalog.md)),
- der **Inventareintrag** gelöscht wird oder
- die **Kollektion** gelöscht wird – sie nimmt ihr gesamtes Attributinventar und
  damit auch die daran hängenden Rechte mit (siehe
  [Attributinventar](attributinventar.md)).

Das geschieht ohne Rückfrage und ohne Historie: Welche Rechte dabei entfallen,
lässt sich hinterher nicht mehr nachvollziehen.

## ID- und Geometrie-Attribut

Für das **ID-Attribut** und das **Geometrie-Attribut** einer Kollektion werden
**keine** Leserechte vergeben. Beide sind Teil des Gerüsts, mit dem die API jedes
Objekt ausliefert, und nicht Teil der abfragbaren Eigenschaften, auf die die
Rechteprüfung wirkt. Sie werden deshalb **immer** ausgeliefert, und eine
Rechteangabe zu ihnen bliebe folgenlos.

In der [Attributübersicht](attribute-verwalten.md) tragen beide daher den Hinweis
**„immer ausgeliefert"**, und ihr Rollenfeld ist gesperrt. Das hat einen
erwünschten Nebeneffekt: Eine Kollektion kann für eine Rolle, die sonstige
Leserechte an ihr hat, durch keine Konfiguration unbrauchbar werden.

## Was ein Leserecht mindestens offenlegt

Sobald eine Rolle **ein einziges** Leserecht an einer Kollektion hat, sieht sie

- die **Existenz jeder Zeile** der Kollektion – die Rechteprüfung beschränkt die
  ausgelieferten Eigenschaften, nicht die Menge der Objekte,
- deren **Kennung**, die ein fachlicher Schlüssel sein kann, und
- deren **exakte Geometrie**, also den Standort.

**„Attribute ja, Standort nein" ist mit Leserechten nicht ausdrückbar.** Wer den
Standort der Objekte nicht sehen darf, darf an dieser Kollektion **kein** Leserecht
erhalten. Wird genau das gebraucht, führt der Weg über eine **zweite Kollektion**
auf einem eigenen View – ohne Geometrie oder mit vergröberter Geometrie.

Für die Dimension „Standort" gilt der Grundgedanke, einen Datenbestand **einmal**
bereitzustellen statt in mehreren zugeschnittenen Varianten, damit ausdrücklich
**nicht**. Das ist eine bewusste Grenze des Rechtemodells und keine Lücke in der
Umsetzung – Attributrechte sind kein Mittel zur Standort-Steuerung.

## Bezeichnungs-Attribut

Das Attribut mit der Bezeichnung wird **nicht** automatisch mitgeführt. Es ist ein
gewöhnliches Attribut, kann personenbezogen sein und ist nur mit einem
ausdrücklich vergebenen Leserecht lesbar.

## Grenzen

- **Vererbung** wird hier nicht aufgelöst: Gespeichert werden Rechte je Rolle. Dass
  eine höherrangige Rolle die Rechte ihrer untergeordneten Rollen erbt, entsteht
  erst bei der Durchsetzung. Ein Attribut **ohne jede** Rolle wird davon nicht
  geheilt: Geerbt werden nur vorhandene Rechte, und wo keines ist, entsteht durch
  Vererbung auch keines. Der Hinweis *„von keiner Rolle lesbar"* bleibt damit auch
  dann zutreffend, wenn der Rollenkatalog eine Hierarchie hat.
- Es gibt **keine Rechte auf einzelne Datensätze**, also keine Filterung von Zeilen.
  „Leserecht je Attribut" ist gröber, als es klingt – siehe den Abschnitt oben.
- Die Änderungshistorie reicht nur so weit wie die **Objekt-Historie** der
  Kollektion: Vergabe und Entzug über die
  [Attributübersicht](attribute-verwalten.md) werden dort mit Zeitpunkt, Person,
  Attribut und Rolle festgehalten. **Nicht** erfasst sind Rechte, die durch das
  Löschen einer Rolle, eines Inventareintrags oder einer Kollektion mitentfallen,
  sowie Änderungen an der Datenbank vorbei.
- ID- und Geometrie-Attribut werden bei der Kollektion als **Freitext** angegeben und
  nicht gegen die Quelle geprüft. Ein Tippfehler oder eine Umbenennung verschiebt
  still, welches Attribut als strukturell gilt. Ein zuvor regulär vergebenes Recht
  fällt dann auf eine gesperrte Zeile; die Attributübersicht weist es als
  **„wirkungsloses Recht"** aus, entfernen lässt es sich dort aber nicht mehr.

## Durchsetzung

Die Leserechte sind hier zunächst nur **erfasst**; sie schützen noch keine Daten.
Wirksam werden sie in zwei weiteren Ausbaustufen: Zuerst werden die Rechte in die
Konfiguration des Dienstes übernommen (und dabei die Vererbung aufgelöst), danach
filtert der Dienst die Antworten zur Laufzeit. Eine Kollektion, an der eine Rolle
kein einziges lesbares Attribut hat, verhält sich für diese Rolle dann so, als
würde sie nicht angeboten.

**Vergeben** lassen sich die Rechte dagegen bereits: über die
[Attributübersicht](attribute-verwalten.md) auf der Änderungsseite einer
Kollektion. Was dort eingetragen wird, ist bis zu diesen Ausbaustufen erfasst,
aber noch ohne Wirkung auf die ausgelieferten Daten.
