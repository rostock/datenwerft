# *pygeoapi*-Konfiguration → Rollenkatalog

Der Rollenkatalog führt die Rollen, auf die sich Leserechte beziehen können.
Jede Rolle hat einen eindeutigen **Bezeichner**, eine sprechende **Bezeichnung**
und optional eine **Eltern-Rolle**.

## Bezeichner und Identity Provider

Der Bezeichner wird **unverändert** so geführt, wie er im Identity Provider
steht – es gibt keine Übersetzungstabelle und keine automatische Anpassung der
Schreibweise. So passen Rechtevergabe und Anmeldung ohne Zwischenschicht
zusammen.

**Wichtig:** Wird ein Bezeichner im Identity Provider **oder** im Rollenkatalog
umbenannt, passen beide Seiten nicht mehr zusammen und die Rechtewirkung
entfällt still. Eine Umbenennung muss daher auf beiden Seiten gleich erfolgen.

## Hierarchie (Vererbung)

- Eine Rolle hat **höchstens eine** Eltern-Rolle oder keine. Eine Rolle ohne
  Eltern-Rolle bildet die Wurzel einer Hierarchie.
- Eine höherrangige Rolle erbt die Leserechte ihrer untergeordneten Rollen; die
  Rechte müssen dort nicht erneut vergeben werden.
- Eine Rolle kann sich **nicht selbst** als Eltern-Rolle haben.
- Eine **ringförmige** Vererbung – unmittelbar oder über mehrere Ebenen – wird
  abgelehnt, weil sich die Rechte sonst nicht eindeutig auflösen ließen.

## Öffentliche Basisrolle

Die öffentliche Basisrolle (Bezeichner `public`) ist eine **gewöhnliche Rolle**
im Katalog und unterscheidet sich technisch nicht von anderen Rollen.

## Kein Bezug zu Benutzer:innen

Der Rollenkatalog speichert **keine** Zuordnung von Personen zu Rollen. Welche
Person welche Rolle hat, entscheidet ausschließlich der Identity Provider.

## Löschverhalten

- Eine Rolle, die **Eltern-Rolle** anderer Rollen ist, kann **nicht gelöscht**
  werden, solange Kind-Rollen auf sie verweisen (Schutz vor Verweisen auf eine
  nicht mehr vorhandene Rolle). Zuerst müssen die Kind-Rollen entfernt oder
  umgehängt werden.
- Die an einer Rolle hängenden **[Leserechte](leserechte.md)** werden beim Löschen
  der Rolle **mitgelöscht**; es entstehen keine Rechte ohne zugehörige Rolle.
