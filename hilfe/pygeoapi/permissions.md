# *pygeoapi*-Konfiguration → Berechtigungen

Bei den Berechtigungen sind **zwei Dinge zu unterscheiden,** die leicht
verwechselt werden:

1. Wer die *pygeoapi*-Konfiguration in *Datenwerft.HRO* **pflegen** darf.
2. Welche Daten die über *pygeoapi* bereitgestellten Dienste **herausgeben** –
   das regeln die Leserechte an den Attributen.

## Wer die Konfiguration pflegen darf

Dafür gibt es genau **eine** Gruppe: `PYGEOAPI_GROUP_NAME` (siehe
[Administration](admin.md)). Wer in dieser Gruppe ist, darf die **gesamte**
*pygeoapi*-Konfiguration pflegen:

- Kollektionen,
- Datenbankverbindungen,
- den [Rollenkatalog](rollenkatalog.md),
- das [Attributinventar](attributinventar.md) und
- die [Leserechte](leserechte.md).

Wer **nicht** in dieser Gruppe ist, hat auf keinen dieser Bereiche Zugriff.

**Wichtig:** Eine feinere Abstufung gibt es **nicht.** Insbesondere ist
„Konfiguration pflegen" nicht von „Rechte vergeben" getrennt: Jedes Mitglied der
Gruppe kann Rollen anlegen und sich selbst Leserechte an beliebigen Attributen
zuschreiben. Ein Vier-Augen-Prinzip lässt sich damit nicht abbilden. Das ist bei
der Frage zu berücksichtigen, wen man in die Gruppe aufnimmt.

**Hinweis:** Für Benutzer:innen der Gruppe `PYGEOAPI_GROUP_NAME` **muss** der
*Mitarbeiter-Status* aktiviert werden.

## Welche Daten die Dienste herausgeben

Diese Ebene hat mit der Gruppe oben nichts zu tun. Sie betrifft nicht die
Mitarbeitenden in *Datenwerft.HRO,* sondern die Abrufenden der Dienste.

- Rechte werden je **Attribut** und je **[Rolle](rollenkatalog.md)** vergeben.
- Welche Attribute eine Kollektion überhaupt hat, führt das
  **[Attributinventar](attributinventar.md)**.
- Ein **[Leserecht](leserechte.md)** verbindet eine Rolle mit einem Attribut.
  Solange kein Leserecht vergeben ist, gilt das Attribut für diese Rolle als
  **nicht lesbar** – Verweigerung ist der Normalzustand.
- Eine höherrangige Rolle **erbt** die Leserechte ihrer untergeordneten Rollen.
  Erfasst wird die Rangfolge schon heute; aufgelöst wird sie erst, wenn die
  Auslieferung die Rechte auswertet (siehe unten).

Welche Person welche Rolle hat, entscheidet ausschließlich der Identity Provider;
*Datenwerft.HRO* speichert dazu nichts.

## Ab wann die Leserechte wirken

**Die Leserechte sind derzeit nur erfasst und schützen noch keine Daten.**

Sie sind vollständig pflegbar und bleiben erhalten, wirken sich aber erst dann
auf die Antworten der Dienste aus, wenn die Auslieferung sie auswertet. Das
geschieht in zwei weiteren Ausbaustufen. Bis dahin gilt: Ein vergebenes oder
entzogenes Leserecht verändert nicht, was ein Dienst herausgibt.

Wer heute Daten schützen muss, darf sich also **nicht** auf die Leserechte
verlassen.

## Noch keine Pflegemasken

Die Rechtelage ist bereits **einsehbar:** Auf der Änderungsseite einer
Kollektion zeigt eine Tabelle je Attribut, welche Rollen es lesen dürfen – siehe
**[Attribute verwalten](attribute-verwalten.md)**.

**Bearbeiten** lässt sich dort noch nichts. Für Rollenkatalog, Attributinventar
und Leserechte gibt es weiterhin **keine** Bearbeitungsmasken in der Oberfläche.
Die Berechtigungen daran sind bereits vergeben, laufen aber noch ins Leere. Die
Masken entstehen mit den Ausbaustufen, die auch die Wirksamkeit bringen.
