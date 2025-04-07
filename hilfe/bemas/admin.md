# *BEMAS* → Administration

## Gruppen und Benutzer:innen

Während der [Initialisierung](../../README.md#initialisierung) der Anwendung *Datenwerft.HRO*
werden die Gruppen `BEMAS_ADMIN_GROUP_NAME` und `BEMAS_USERS_GROUP_NAME` angelegt
und automatisch mit den passenden [Berechtigungen](permissions.md) versehen.
Zu diesen Gruppen müssen dann manuell die entsprechenden
[Benutzer:innen hinzugefügt](../datenwerft/admin.md#benutzerin-hinzufügen) werden.

## Datenschutz

Über die Direktive `BEMAS_STATUS_CHANGE_DEADLINE_DAYS` kann folgendes Verhalten
des Befehls `deletepersons` eingestellt werden:

Es werden alle Personen gelöscht, die nicht als Ansprechpartner:innen
mit Organisationen verknüpft sind, nicht als Betreiber:innen mit Verursachern verknüpft sind
und die als Beschwerdeführer:innen nur noch mit Beschwerden verknüpft sind, die seit
`BEMAS_STATUS_CHANGE_DEADLINE_DAYS` Tagen abgeschlossen sind.

Diese Einstellung kann jedoch **nicht** in *BEMAS* selbst, sondern **muss durch die/den
Administrator:in** der *Datenwerft.HRO* vorgenommen werden.

## Codelisten

Bei Codelisten handelt es sich um Datensätze, deren Inhalte als Auswahlwerte in anderen
Datensätzen verwendet werden. Beispiel: Die Codeliste *Immissionsarten* besteht aus mehreren
Einträgen, die im Freitext-Attribut *Titel* zum Beispiel die Werte *Lärm* oder *Erschütterungen*
aufweisen. Im Datensatz *Beschwerden* schließlich sind diese Werte dann als Codeliste für das
Auswahl-Attribut *Immissionsart* eingebunden, sodass man dort eben zwischen
*Lärm, Erschütterungen* und anderen Werten wählen kann.

Die Inhalte von Codelisten können in *BEMAS* selbst bearbeitet werden.
Hierfür müssen Sie allerdings der [Berechtigungsstufe](permissions.md) *Admin* angehören.
