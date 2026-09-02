# *pygeoapi*-Konfiguration → Attributinventar

Das Attributinventar führt je Kollektion die **Attributnamen**, die ihre
Quelltabelle beziehungsweise ihr Quell-View bereitstellt. Rechte werden je
Attribut vergeben (eigener Schritt), also muss die Datenwerft zunächst wissen,
welche Attribute eine Kollektion überhaupt hat.

Jeder Inventareintrag hat einen **Namen,** den **Datentyp in der Quelle** und
eine Kennzeichnung **„in der Quelle vorhanden"**. Darüber hinaus werden keine
weiteren Metadaten (Beschreibung o. Ä.) erfasst.

Der Datentyp wird beim **[Abgleich](attribute-verwalten.md#attribute-abgleichen)**
gegen die Quelltabelle mitgeschrieben, in der Schreibweise der Quelldatenbank.
Lässt er sich nicht ermitteln, bleibt das Feld leer.

## Eindeutigkeit

Je Kollektion und Attributname existiert **höchstens ein** Inventareintrag. Ein
zweiter Eintrag mit demselben Namen in derselben Kollektion wird abgelehnt.
Derselbe Name in einer *anderen* Kollektion ist zulässig.

## Deny-by-default

Ein Inventareintrag trägt **kein** Lese-/Rechte-Flag. Ein inventarisiertes
Attribut ist damit für **keine** Rolle lesbar; Verweigerung ist der Standard.
Lesbar wird ein Attribut erst, wenn ausdrücklich ein
**[Leserecht](leserechte.md)** vergeben wird.

## Löschverhalten

Wird eine **Kollektion gelöscht**, wird ihr **gesamtes Attributinventar**
mitgelöscht – und damit später auch die daran hängenden Rechte. Das ist gewollt,
damit das Löschen einer Kollektion nicht durch das Inventar blockiert wird und
keine Inventareinträge ohne zugehörige Kollektion zurückbleiben.

## Befüllung und Rechtevergabe

Das Inventar wird auf der Änderungsseite einer Kollektion angezeigt, siehe
**[Attribute verwalten](attribute-verwalten.md)**. Dort werden je Attribut auch
die **Leserechte** vergeben und entzogen.

**Befüllt** wird es an derselben Stelle über den Knopf *Attribute abgleichen*
(siehe **[Attribute
abgleichen](attribute-verwalten.md#attribute-abgleichen)**). Der Abgleich ergänzt
fehlende Attribute, kennzeichnet nicht mehr vorhandene als solche statt sie zu
löschen und entkennzeichnet wieder aufgetauchte – vergebene Leserechte bleiben
dabei erhalten. Er läuft nur, wenn er angestoßen wird; ohne einen Abgleich bleibt
das Inventar einer neuen Kollektion leer.
