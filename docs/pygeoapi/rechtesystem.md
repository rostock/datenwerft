# Rechtesystem der App _pygeoapi_ (Entwicklerdokumentation)

Diese Seite richtet sich an Entwickler:innen und beschreibt das Datenmodell hinter
den attributbezogenen Leserechten sowie die Gründe für die getroffenen
Entscheidungen.

Die Beschreibung des **Verhaltens** für Anwender:innen steht in der Hilfe unter
[`hilfe/pygeoapi/`](../../hilfe/pygeoapi/) – dort werden die Zusagen gegeben, hier
stehen ihre Begründungen. Merksatz: `hilfe/` ist die Referenz für
Verhaltensversprechen, `docs/` für die Modellbegründung.

## Datenmodell

Drei Modelle in `pygeoapi/models.py`, angelegt durch die Migrationen `0002` bis
`0004` (jeweils ausschließlich `CreateModel`); `0005` ergänzt eine Spalte an
`pygeoapi_collection_attribute`. Dass keine Migration nach `0001` die
vorbestehenden Tabellen `pygeoapi_collection` und `pygeoapi_database_connection`
anfasst, sichert
[`pygeoapi/tests/test_migrations.py`](../../pygeoapi/tests/test_migrations.py) ab.

### `Role` – Tabelle `pygeoapi_role`

| Feld         | Typ                        | Anmerkung                                            |
| ------------ | -------------------------- | ---------------------------------------------------- |
| `identifier` | `CharField(255)`, `unique` | Bezeichner des Identity Providers, unverändert       |
| `label`      | `CharField(255)`           | sprechende Bezeichnung                               |
| `parent`     | `ForeignKey('self')`       | `null=True`, `on_delete=PROTECT`, höchstens ein Wert |

Constraint `pygeoapi_role_no_self_parent`: `CheckConstraint(~Q(parent=F('id')))`.
Mehrstufige Zyklen lassen sich nicht als Datenbank-Constraint ausdrücken; sie
werden in `Role.clean()` durch Hochlaufen der Elternkette abgefangen.

Bewusst **kein** Bezug zu `User`: der Katalog ist Referenzdatenhaltung, die
Zuordnung Person → Rolle bleibt beim Identity Provider.

### `CollectionAttribute` – Tabelle `pygeoapi_collection_attribute`

| Feld         | Typ                             | Anmerkung                     |
| ------------ | ------------------------------- | ----------------------------- |
| `collection` | `FK(Collection)`                | `on_delete=CASCADE`           |
| `name`       | `CharField(100)`                | Attributname der Quelle       |
| `data_type`  | `CharField(100)`, `blank`, `''` | Datentyp in der Quelle        |
| `is_present` | `BooleanField(True)`            | in der Quelle noch vorhanden? |

Constraint `pygeoapi_collection_attribute_unique_name_per_collection`:
`UniqueConstraint(collection, name)`.

`is_present` statt Löschen: eine verschwundene Spalte darf die daran vergebenen
Rechte nicht stillschweigend beseitigen, sonst käme eine versehentlich gelöschte
und wiederhergestellte Spalte rechtefrei zurück.

`data_type` wird vom [Abgleich](#abgleich-des-attributinventars) aus der
Spaltenliste geschrieben, die `get_database_columns` samt
`format_type(a.atttypid, a.atttypmod)` liefert. Der Wert wird ausschließlich
gespeichert und angezeigt, nie ausgewertet; abgesichert ist er durch die
Längenbegrenzung und das Escaping in der Anzeige.

Das Feld kommt mit der eigenen Migration `0005` als `AddField` nach, weil `0003`
zu diesem Zeitpunkt bereits auf `dev` lag. Eine Migration, deren Name in
`django_migrations` steht, führt _Django_ nicht erneut aus: in eine
veröffentlichte Migration hineingeschrieben hätte die Spalte in jeder bereits
migrierten Datenbank **still gefehlt** und wäre erst zur Laufzeit als
`ProgrammingError` aufgefallen – auch in _Docker_, denn das `migrate` im
Entrypoint wiederholt eine angewendete Migration nicht. Auf _PostgreSQL_ ist das
`AddField` mit Default `''` reine Metadatenänderung, also ohne Tabellen-Rewrite
und ohne langen Lock.

### `AttributeReadPermission` – Tabelle `pygeoapi_attribute_read_permission`

| Feld        | Typ                       | Anmerkung           |
| ----------- | ------------------------- | ------------------- |
| `role`      | `FK(Role)`                | `on_delete=CASCADE` |
| `attribute` | `FK(CollectionAttribute)` | `on_delete=CASCADE` |

Constraint `pygeoapi_attribute_read_permission_unique_role_attribute`:
`UniqueConstraint(role, attribute)`.

Es gibt **kein** `granted`-Flag: die Existenz der Zeile _ist_ das Recht. Dadurch
ist Deny-by-default strukturell und kann nicht durch eine falsch gesetzte
Kennzeichnung aufgeweicht werden. Die Property `is_effective` liest
`attribute.is_present` – beim Iterieren `select_related('attribute')` verwenden.

## Validierung: `save()` ruft `full_clean()`

Alle drei Modelle überschreiben `save()` und rufen `full_clean()`. Django tut das
von sich aus **nicht**; ohne diesen Aufruf würden `objects.create()`, die Shell und
die Tests an der Validierung vorbeischreiben.

Folgen:

- Ein Duplikat erscheint als `ValidationError`, nicht als `IntegrityError`.
- `ForeignKey.validate()` weist eine nicht existierende Rolle bzw. einen nicht
  existierenden Inventareintrag ab.
- Der Zyklus-Check in `Role.clean()` greift auch außerhalb von Formularen.

**Bewusste Grenze:** `bulk_create()` und `bulk_update()` umgehen `save()` und
damit die gesamte Prüfung. Für Massenoperationen – die Rechtevergabe und die
Inventarbefüllung – muss die Prüfung entweder vorgezogen erfolgen oder es ist
zeilenweise zu speichern. Beide Stellen ziehen sie vor; siehe unten und
[Abgleich](#abgleich-des-attributinventars).

### Wo `bulk_create()` bewusst genutzt wird

`CollectionAttributeFormSet.save_permissions()` schreibt neue Leserechte mit
`bulk_create(..., ignore_conflicts=True)` statt zeilenweise. Zeilenweises
Speichern kostet bei 100 Attributen mal 3 Rollen rund 1200 Abfragen; so ist es
**eine**.

Die drei Prüfungen, die `full_clean()` leisten würde, sind an dieser Stelle
vorher garantiert:

| Prüfung                       | warum sie hier nicht nötig ist                                                    |
| ----------------------------- | --------------------------------------------------------------------------------- |
| Rolle existiert               | sie stammt aus dem je Request geladenen Rollenkatalog, nicht aus dem POST           |
| Inventareintrag existiert     | er stammt aus dem Queryset des Formsets                                             |
| Kombination noch nicht vorhanden | eingefügt wird nur, was der Soll-Ist-Vergleich als fehlend ausweist               |

`ignore_conflicts=True`, weil bei diesem Modell die **Existenz der Zeile das
Recht ist**: Eine von einem parallelen Speichervorgang eingefügte Zeile ist der
gewünschte Endzustand, kein Fehler. Ohne das Flag endete dieser Wettlauf in einem
`IntegrityError` mit vollständigem Rollback des gesamten Speichervorgangs.

## Löschverhalten

- `Role.parent` ist `PROTECT`: eine Rolle mit Kind-Rollen kann nicht gelöscht
  werden, es entsteht also nie ein Verweis auf eine nicht mehr vorhandene Rolle.
- Die Fremdschlüssel der Rechte sind `CASCADE`: es gibt keine Rechte ohne Rolle
  und keine ohne Inventareintrag. Das Löschen einer Kollektion nimmt ihr
  Inventar und damit die daran hängenden Rechte mit.

Es gibt keine Änderungshistorie und kein Backup: was kaskadiert gelöscht wird,
ist nicht mehr nachvollziehbar.

## `id_field` und `geom_field`: keine Rechte

In der GeoJSON-Antwort liegen `id` und `geometry` auf der **Wurzelebene** eines
Features, alle übrigen Attribute unter `properties`. Der `access_control`-Block
wirkt ausschließlich auf `properties`. Für die in `Collection.id_field` und
`Collection.geom_field` benannten Attribute sind Leserechte deshalb folgenlos und
werden nicht vergeben.

Ein Verbot in `clean()` – „für diese beiden Attributnamen darf kein Recht
existieren" – wurde **bewusst nicht** gebaut: `id_field` ist ein ungeprüftes
Freitextfeld der Kollektion. Wird es umbenannt, würden bereits gespeicherte
Rechtezeilen rückwirkend ungültig und die betroffenen Objekte unspeicherbar,
ohne dass jemand etwas falsch gemacht hätte.

## `title_field`

`Collection.title_field` ist ein **gewöhnliches** `properties`-Attribut und wird
nicht implizit mitgeführt; ohne ausdrücklich vergebenes Leserecht ist es nicht
lesbar. Zugleich ist es ein Konfigurationsschlüssel des Providers – eine
Kollektion ohne lesbares `title_field` bleibt gültig, zeigt aber keine
Bezeichnung.

## Attributübersicht im Kollektions-Formular

`CollectionAttributeInline` in [`pygeoapi/admin.py`](../../pygeoapi/admin.py) ist
ein `TabularInline` auf der Änderungsseite einer Kollektion. Alle Modellfelder
sind `readonly`; **editierbar ist ausschließlich die Rollenzuweisung.**

- `get_queryset()` lädt mit `select_related('collection')` und einem `Prefetch`
  der Rechte inklusive Rolle vor. Ohne das wächst die Zahl der Abfragen mit der
  Zahl der Attribute und Rollen – gemessen 509 statt 34 Abfragen bei 100
  Attributen mit je 3 Rollen. Abgesichert durch einen Vergleichstest mit 5 und
  mit 100 Attributen in
  [`pygeoapi/tests/test_collection_admin.py`](../../pygeoapi/tests/test_collection_admin.py).
- Sortiert wird ausdrücklich mit `.order_by('name')` statt über `Meta.ordering`,
  weil die wiederholbare Reihenfolge ein zugesagtes Verhalten ist. Eindeutig ist
  sie durch `UniqueConstraint(collection, name)`. Die Reihenfolge der Spalten in
  der Quelltabelle wird nicht persistiert und daher nicht abgebildet.
- `empty_value_display = ''`: der Admin-Site setzt sonst einen Bindestrich in
  die Rollen-Spalte eines rechtefreien Attributs, der als Rollenname gelesen
  werden kann.
- Auf der Anlageseite liefert `get_inlines()` eine leere Liste und
  `get_fieldsets()` hängt ein Fieldset ohne Felder mit reiner `description` an.
  Beides ist bewusst in _Python_ gelöst, damit das app-weite
  `admin/pygeoapi/change_form.html` und die darin eingebundene `changeForm.js`
  von der Fallunterscheidung Anlegen/Ändern frei bleiben. Django lädt für das
  Inline zusätzlich `admin/js/inlines.js`; es arbeitet auf `django.jQuery` und
  wird vor dem projekteigenen jQuery/select2 geladen. Das Template selbst hat
  seither zwei Ergänzungen erhalten: `changeForm.css` (Rollen-Spalte) und das
  Modul-Skript der Suche.
- Der Leer-Zustand steckt in
  [`pygeoapi/templates/admin/pygeoapi/edit_inline/collection_attributes.html`](../../pygeoapi/templates/admin/pygeoapi/edit_inline/collection_attributes.html).
  Unterschieden wird über `formset.initial_forms` und nicht über
  `queryset.exists()`, das eine zusätzliche Abfrage kostet. Das Management-Form
  wird auch im Leer-Zweig gerendert – ohne es scheitert jedes Speichern der
  Kollektion an der fehlenden Formset-Verwaltung.
- Ein eigener Zugriffsschutz war nicht nötig: das Inline ist an
  `pygeoapi.view_collectionattribute` gebunden, und sämtliche Berechtigungen der
  App hängen geschlossen an der Gruppe `PYGEOAPI_GROUP_NAME`.

## Zuweisen und Entziehen von Rollen

### Rollenkatalog genau einmal je Request

`CollectionAttributeFormSet` lädt den Katalog in `cached_property roles` und
reicht ihn über `get_form_kwargs(index)` an jede Zeile durch (`index is None`
für das `empty_form`). `RoleField` ist ein `ModelMultipleChoiceField` mit
**leerem** Queryset; die Optionen werden als **fertige Liste** gesetzt und
`_check_values()` löst die geposteten Schlüssel gegen ein `dict` auf.

Ohne diese Vorkehrung entstünde je Zeile eine Abfrage beim Rendern **und** je
Zeile eine beim Speichern. Beschriftet wird einheitlich mit `str(role)`, also
`'Bezeichnung (Bezeichner)'` – nur `identifier` ist unique, zwei Rollen dürfen
sich eine Bezeichnung teilen.

`Meta.fields = []`: Kein Modellfeld des Inventars ist hier editierbar.
`save_existing()` gibt die Instanz unverändert zurück, statt ein identisches
`UPDATE` samt `full_clean()` je geänderter Zeile zu kosten; die Zeile steht zu
diesem Zeitpunkt bereits in `changed_objects`, der Log-Eintrag verliert nichts.

Die Methode `roles(obj)` des Inlines bleibt daneben bestehen: Sie ist der
Anzeige-Fallback für Nutzer:innen ohne `pygeoapi.change_collectionattribute`,
für die `InlineAdminFormSet` sämtliche Felder readonly rendert.

### `disabled` ist die serverseitige Absicherung

Für `id_field` und `geom_field` wird `field.disabled = True` gesetzt. Das ist
**kein** reiner Anzeigeeffekt und braucht keinen eigenen Prüfcode: Ein
deaktiviertes Feld wird aus `initial` statt aus den POST-Daten gesäubert und
meldet sich nie als geändert. Ein gefälschter POST ist damit nicht „abgewehrt",
sondern **strukturell wirkungslos**.

Die Namen stammen aus `self.instance.collection`, also aus dem Datenbankstand,
mit dem die Seite gerendert wurde – nicht aus dem POST.

Ein `clean()`, das Rechte an solchen Zeilen ablehnt, wurde bewusst **nicht**
gebaut; das widerspräche der oben festgehaltenen Entscheidung zu `id_field` und
`geom_field`. Stattdessen weist `hint()` sie als **„wirkungsloses Recht"** aus.

### Objekt-Historie

Djangos Standardmeldung nennt für ein Nicht-Modell-Feld nur das Attribut, nicht
die Rolle, und erfüllt die Zusage der Hilfe damit nicht.
`save_permissions()` legt den Diff deshalb auf dem **Formset** ab –
request-privat, im Gegensatz zum prozessweiten `ModelAdmin`-Singleton – und
`CollectionAdmin.construct_change_message()` hängt daraus eigene
`{'changed': {...}}`-Einträge an; die übrigen Formsets reicht es unverändert an
`super()` durch.

Die Reihenfolge stimmt: `save_related()` läuft vor `construct_change_message()`.
Strukturierte Einträge statt freier Klartextmeldung, weil
`LogEntry.get_change_message()` einen String, der nicht mit `[` beginnt,
unverändert zurückgibt – die Angaben des Elternformulars gingen sonst verloren.

### Reload nach `save_related()` und auf `transaction.on_commit`

Zwei getrennte Punkte:

1. **Reihenfolge.** `save_model()` läuft **vor** `save_related()`, das die
   Inline-Formsets schreibt. Der Aufruf gehört deshalb nach `save_related()` –
   sonst liefe der Reload, bevor die Rechte geschrieben sind. `save_related()`
   ist zugleich die richtige Stelle für „genau einmal": Es wird je gültigem POST
   einmal erreicht, für Anlegen wie Ändern und unabhängig davon, welcher
   Sichern-Knopf benutzt wurde.
2. **Commit-Rennen.** `reload_pygeoapi()` startet einen Thread, der bisher
   **innerhalb** der noch offenen Transaktion loslief. Die Gegenstelle liest die
   Datenwerft-Datenbank über eine **eigene** Verbindung und sieht nicht
   committete Daten prinzipiell nicht – der Reload konnte also aus veraltetem
   Stand erzeugen. Alle Einstiegspunkte des Admin sind atomar, deshalb
   `transaction.on_commit(reload_pygeoapi)` an allen Aufrufstellen.

> **Folge für Tests:** `django.test.TestCase` committet nie, `on_commit`-Callbacks
> laufen dort **nicht**. Jeder Test, der den Reload zählt, braucht
> `self.captureOnCommitCallbacks(execute=True)` – sonst steht der Zähler immer
> auf null, und ein Test, der prüft, dass *kein* Reload stattfand, wäre wertlos,
> weil er immer grün ist.

### Konventionsabweichung: `window.confirm`

Bestätigungen sind im Projekt sonst Zwischenseiten mit POST-Formular oder
Bootstrap-Modals; `confirm(` kam in eigenem Projekt-JS bisher nirgends vor. Hier
scheiden beide Muster aus:

- Eine **Zwischenseite** verlässt das Formular und bräche damit die Zusage
  „wirkt erst mit dem Sichern" – sie müsste den kompletten ungespeicherten
  Formularzustand mitschleusen.
- **Bootstrap** existiert im Django-Admin nicht, nur in
  `datenwerft/templates/base.html`.
- `select2:unselecting` verlangt eine **synchrone** Antwort, damit
  `preventDefault()` noch wirkt; ein `dialog`-Element wäre asynchron.

Der Fehlermodus ist fail-closed: Unterdrückt jemand die Dialoge im Browser,
funktionieren Entzüge nicht mehr – ein Recht bleibt bestehen, statt still zu
verschwinden.

Der Preis dieser Entscheidung: Die Rückfrage existiert **ausschließlich im
Browser**. Serverseitig ist ein bestätigter von einem unbestätigten Entzug nicht
zu unterscheiden. Ohne JavaScript initialisiert select2 nicht, das rohe
`<select multiple>` lässt sich abwählen, und das Sichern schreibt den Entzug
ohne jede Rückfrage. Das ist vertretbar, weil die Maske ohne JavaScript ohnehin
nur eingeschränkt bedienbar ist – auch die Kaskade aus Schema-, Tabellen- und
Feldauswahl hängt daran. Die Zusage darf nur nicht stärker klingen, als sie
technisch ist.

#### Abdeckungslücke: die Rückfrage ist nicht automatisiert geprüft

Der Handler in `pygeoapi/static/pygeoapi/js/changeForm.js` ist durch **keinen
automatisierten Test** gedeckt. Das Projekt hat mit eslint und oxlint nur
statische Prüfung und keinen JS-Testrunner; Selenium oder Playwright sind nicht
vorhanden, und sie allein für diesen Dialog einzuführen wäre unverhältnismäßig.

Das Akzeptanzkriterium nennt die abgebrochene Bestätigung ausdrücklich als
Testgegenstand. Automatisiert geprüft ist davon nur die **serverseitige
Entsprechung** – dass eine unveränderte Zeile die Primärschlüssel ihrer Rechte
behält (`test_an_unchanged_row_keeps_the_primary_keys_of_its_permissions`).

Ersetzt wird die Lücke durch eine **Handprobe**, die bei jeder Änderung an
`changeForm.js` oder am Rollenfeld zu wiederholen ist:

1. Bei einem Attribut mit zugewiesener Rolle das **✕** des Feldchens anklicken.
2. Die Rückfrage **abbrechen** → das Feldchen bleibt stehen.
3. Die Kollektion **sichern** und die Änderungsseite erneut aufrufen → die
   Zuweisung steht unverändert.
4. Zur Gegenprobe dasselbe mit **OK** → das Feldchen verschwindet, das Recht ist
   aber erst nach dem Sichern fort.

### Sackgasse: ein wirkungsloses Recht ist über die Maske nicht entfernbar

Wird `Collection.id_field` oder `geom_field` nachträglich auf ein Attribut
umbenannt, das bereits ein regulär vergebenes Leserecht trägt, fällt dieses Recht
auf eine strukturelle Zeile. Die Maske weist es als **„wirkungsloses Recht"**
aus – entfernen lässt es sich dort aber nicht: Bei `field.disabled` unterdrückt
select2 das **✕** des Feldchens sowohl im Klick-Handler
(`static/select2/select2.js`, `isDisabled()`) als auch per CSS
(`static/select2/select2.css`, `.select2-container--disabled
.select2-selection__choice__remove { display: none }`).

Bewusst so belassen, weil der Schaden begrenzt ist: `id` und `geom` liegen auf
der Wurzelebene der GeoJSON-Antwort und werden unabhängig von jedem Leserecht
ausgeliefert – das Recht ist also ohne Wirkung, nur unschön. Die Alternative
wäre, das Feld editierbar zu lassen und in `clean()` jede Auswahl abzulehnen, die
über die gespeicherten Rollen hinausgeht; das gäbe die serverseitige Absicherung
durch `disabled` gegen selbst geschriebenen Prüfcode auf und lädt an einer Zeile
ohne Recht zu einer Eingabe ein, die nur wieder abgelehnt wird.

Rückwege: den Attributnamen zurücksetzen (dann ist die Zeile wieder gewöhnlich
und das Recht entziehbar) oder den Abgleich abwarten. Der Hinweis in der Maske
sorgt dafür, dass der Zustand sichtbar bleibt statt unbemerkt.

### CSS-Kollision mit dem Admin

`pygeoapi/static/pygeoapi/css/changeForm.css` korrigiert zwei Regeln, die erst
greifen, seit select2 in einem Inline steht: `base.css` setzt
`.module ul { margin-left: 1.5em }`, und select2 rendert die Chip-Liste als
`display: inline` – bei einem Inline-Element wirkt `margin-left` nur auf die
erste Zeilenbox und schiebt damit genau den ersten Chip aus dem Feld.

### Abfragezahl beim Speichern

Das Schreiben der Rechte kostet **konstant** eine `bulk_create`- und eine
`delete`-Abfrage, unabhängig von der Zahl geänderter Zeilen und Rollen.

Die Gesamtzahl der Abfragen eines POST wächst dennoch um **eine je
Attributzeile** – das ist Djangos eigenes Primärschlüsselfeld im Formset
(`ModelChoiceField` über den Default-Manager) und **vorbestehend**: auf dem Stand
vor dieser Änderung gemessen 30 gegenüber 125 Abfragen bei 5 gegenüber 100
Attributen. Die Zusage „wächst nicht mit der Datenmenge" gilt daher weiterhin für
den **Aufruf** der Seite, nicht für das Speichern.

## Hinweis auf Attribute ohne jede Rolle

Ein Attribut ohne jedes Leserecht ist der **beabsichtigte Ausgangszustand** und
kein Fehler. Sichtbar gemacht wird er an zwei Stellen, beide rein serverseitig in
[`pygeoapi/admin.py`](../../pygeoapi/admin.py) – ohne Modell-, Migrations-,
Template-, CSS- oder JS-Änderung.

### Kennzeichnung: `elif` am strukturellen Zweig

`CollectionAttributeInline.hint()` hängt `'von keiner Rolle lesbar'` als **`elif`**
an die Prüfung auf `id_field`/`geom_field`. Damit ist die Ausnahme für die
strukturellen Attribute **strukturell** und nicht durch eine zweite Bedingung
nachgebildet: Eine Zeile, die ohnehin immer ausgeliefert wird, kann den Hinweis
nicht tragen. `title_field` ist nicht ausgenommen – es ist ein gewöhnliches
`properties`-Attribut.

`obj.read_permissions.all()` gibt das **vorgeladene** QuerySet selbst zurück und
kostet daher keine Abfrage – auf GET wie auf POST. Ein `.filter()`, `.exclude()`
oder `.order_by()` an dieser Stelle würde es klonen und den Prefetch verwerfen:
eine Abfrage **je Zeile**. Ebenso teuer wäre ein Zugriff auf `obj.collection`
ohne das `select_related()` aus `get_queryset()`. Abgesichert durch die
Vergleichstests der Abfragezahl.

Kein CSS und kein `<span>`: Alle Bestandshinweise sind Klartext, ein farbiger
vierter würde eine Schweregrad-Hierarchie einführen, die es hier nicht gibt. Der
Hinweis steht auch nicht in der Rollen-Spalte – deren `empty_value_display = ''`
ist eine zugesagte und getestete Eigenschaft.

### Meldung: `cleaned_data` statt Prefetch

`CollectionAttributeFormSet.attributes_without_role()` liest den **Soll-Zustand**
dieses POST aus `form.cleaned_data`, nicht `attribute.read_permissions.all()`.
Grund: Der Prefetch ist der Stand **vor** dem Speichern und wird von
`bulk_create()`/`delete()` in `save_permissions()` nicht invalidiert. Wer in genau
diesem Vorgang das letzte Recht entzieht, muss aber genannt werden – und wer eines
vergibt, nicht mehr. Der Regressionsschutz dafür ist
`test_assigning_the_last_role_silences_the_warning_in_the_same_save`; mit dem
Prefetch als Quelle ist er rot.

Drei Robustheitsregeln: nur `initial_forms` **und** ein `pk`-Guard (ein gefälschter
`INITIAL_FORMS`-Zähler erzeugt Initialformulare ohne Attribut), `.get('roles')`
statt Indexzugriff (bei einem gefälschten Schlüssel fehlt er), und ausschliesslich
**Truthiness** – der Wert enthält je nach Pfad `Role`-Objekte, `int`s oder ein
leeres QuerySet. Die Reihenfolge folgt dem Inline-Queryset (`.order_by('name')`),
kein eigenes `sorted()`.

Die Berechnung wohnt am **Formset**, weil sie request-privat ist und nicht an das
prozessweite `ModelAdmin`-Singleton gehört. Anders als `permission_changes` ist sie
eine Methode ohne gespeichertes Attribut, damit der Filter in
`construct_change_message()` unberührt bleibt – die Warnung gehört nicht in die
Objekt-Historie.

### Aufruf in `save_related()`

Der Aufruf sitzt in `CollectionAdmin.save_related()` nach `super()`, über
`for formset in formsets or []` mit `isinstance`-Prüfung – dasselbe Muster, das
`construct_change_message()` schon nutzt, und damit auf der Anlageseite
(`formsets == []`) absturz- und meldungsfrei. `save_related()` wird je gültigem
POST genau einmal erreicht, für Anlegen wie Ändern, unabhängig vom Sichern-Knopf,
und läuft **nach** `save_permissions()` – kann also keinen Zustand behaupten, der
nicht geschrieben wurde. Verworfen: `save_formset()` (Meldungsausgabe ist kein
Speichern) und `response_change()` (hat die Formsets nicht und deckt
`response_add` nicht mit ab).

`messages.WARNING`, nicht `ERROR`: Es ist nichts fehlgeschlagen, und `ERROR` würde
die Frage „ist es gespeichert?" provozieren. Nicht `INFO`, weil es neben der
Erfolgsmeldung unterginge. Präzedenz im Repo ist `messages.warning` in
`antragsmanagement/views/views.py`.

### Meldungstext

`attributes_without_role_message()` schreibt bis `MESSAGE_ATTRIBUTE_LIMIT = 10`
Namen aus, darüber die ersten zehn und die Restzahl; die **Gesamtzahl** wird immer
genannt. Der eigentliche Grund für die Kappung ist nicht Kosmetik, sondern die
**Cookie-Grenze von 2048 Byte**: Darüber greift der Session-Fallback, kostet eine
zusätzliche Abfrage und macht die Abfragezahl datenabhängig.

Der Text nutzt `ngettext` **nicht lazy** – er wird sofort interpoliert. Ein
`locale/` ist dafür nicht zu pflegen: Ohne Katalog fällt Django auf die msgid
zurück, und die Pluralregel `n != 1` entspricht der deutschen. Er beginnt mit
feststehender Prosa, weil `admin/base.html` `{{ message|capfirst }}` rendert –
stünde ein Attributname vorn, würde er grossgeschrieben und wäre ein Name, den es
in der Quelle nicht gibt (Attributnamen sind case-sensitiver Freitext aus einer
Fremd-Datenbank). Bewusst ein **roher `str`** ohne `mark_safe()`/`format_html()`:
Das Template autoescaped, ein `SafeString` würde Cookie und Session bis ins
Template überleben und wäre ein XSS-Vektor.

### Warnung statt Sperre

Backlog-Eintrag DW-04 fordert wörtlich eine **Sperre**. Umgesetzt ist eine
**Warnung** – eine bewusste Abweichung: Eine Sperre würde genau den
Attribut-Abgleich blockieren, der rechtefreie Attribute überhaupt erst einträgt,
und widerspräche dem Grundsatz „Verweigerung ist der Standard". Begründet auch
für Endnutzer:innen in
[`hilfe/pygeoapi/attribute-verwalten.md`](../../hilfe/pygeoapi/attribute-verwalten.md).

Zwei akzeptierte Folgen: Die Warnung steht **über** der Erfolgsmeldung, weil
`save_related()` vor `response_change()` läuft – der Nachsatz „Gespeichert wurde
trotzdem alles" fängt die Leserichtung ab. Und sie erscheint nicht dort, wo die
Tabelle steht: Bei „Sichern" landet sie auf der Changelist, bei „Sichern und neu
hinzufügen" auf der Anlageseite. Die Namen stehen deshalb in der Meldung selbst.

**Solange der Rollenkatalog leer ist, warnt jedes Sichern einer Kollektion mit
Inventar** – es lässt sich dann gar keine Rolle zuweisen (siehe *Roadmap*). Das
ist erwartetes Verhalten dieser Ausbaustufe und kein Defekt. Bewusst **keine**
Notabschaltung bei leerem Katalog: Die Aussage ist dann ja zutreffend, und eine
Sonderregel nähme genau die Sichtbarkeit, um die es geht.

## Suche über den Attributnamen

Die Suche über der Attributtabelle wirkt **ausschließlich im Browser**:
`pygeoapi/static/pygeoapi/js/attributeFilter.js` blendet Zeilen aus, deren
Attributname die Eingabe nicht enthält. Der Suchblock steht in
`collection_attributes.html` **vor** dem Include von
`admin/edit_inline/tabular.html`.

### Browserseitig statt serverseitig

Eine serverseitige Filterung müsste den **ungespeicherten Formularzustand** über
den Seitenwechsel tragen: Wer eine Rolle wählt und dann sucht, würde die Auswahl
sonst verlieren. Sie bräche damit dieselbe Zusage, an der schon die Zwischenseite
für die Rückfrage gescheitert ist – „wirkt erst mit dem Sichern". Hinzu käme eine
Blätterung, die die Formset-Verwaltung (`TOTAL_FORMS`, `INITIAL_FORMS`) je Seite
zerlegen müsste; ein Teil-POST würde die Rechte der nicht geladenen Zeilen
löschen.

Der Preis ist die Abhängigkeit von JavaScript. Vertretbar, weil die Maske ohnehin
daran hängt (Kaskade aus Schema-, Tabellen- und Feldauswahl, select2). In
[`hilfe/pygeoapi/attribute-verwalten.md`](../../hilfe/pygeoapi/attribute-verwalten.md)
ist benannt, dass ohne JavaScript nicht gefiltert wird.

### `classList` statt DOM-Entfernung – das Kernrisiko

Ausgeblendet wird **nur** über die Klasse `.attribute-filter-hidden`
(`display: none` in `changeForm.css`). Kein `remove()`, kein `disabled`, keine
Änderung an `TOTAL_FORMS`/`INITIAL_FORMS`.

Der Grund ist der eigentliche Schaden, den das Ticket benennt: Wäre eine
gefilterte Zeile aus dem DOM entfernt oder ihr Feld deaktiviert, fehlte ihre
Rollenauswahl im POST. `CollectionAttributeFormSet.save_permissions()` läse für
sie „keine Rolle gewählt" und **löschte die Rechte still** – ohne Fehler, ohne
Meldung, mit einem korrekt aussehenden Eintrag in der Objekt-Historie.

Eine **eigene** Klasse statt Djangos `.hidden`, damit im Inspektor erkennbar
bleibt, wer die Zeile ausblendet, und damit eine Änderung an `.hidden` im Admin
die Filterung nicht mitnimmt.

### Markup-Vertrag des Suchblocks

- Weder Suchfeld noch Zurücksetzen-Knopf tragen ein **`name`-Attribut**. Mit
  `name` landeten beide als fremde Schlüssel im POST der Änderungsseite.
- Der Knopf ist `type="button"`. Der Standardwert `submit` würde die Kollektion
  sichern.
- `Enter` im Suchfeld wird per `preventDefault()` abgefangen: Ein Textfeld im
  Änderungsformular löst sonst die **implizite Absendung** aus und würde die
  Kollektion samt aller Nebenwirkungen sichern, darunter der
  Konfigurations-Reload.
- Der Statustext wird über **`textContent`** gesetzt, nie über `innerHTML` – die
  Eingabe erscheint darin und darf nicht als Markup ins Dokument gelangen.
- `data-group` am Block nennt die zu filternde Gruppe, damit der Formset-Präfix
  nicht im JavaScript wiederholt wird.
- Der Name wird aus **`td.field-name > p`** gelesen, die Zeilen über
  `tr.form-row:not(.empty-form)`. Das `empty-form` kann hier nicht auftreten –
  Django rendert es nur mit Add-Recht, das das Inline verweigert –, der Ausschluss
  ist reine Vorsorge.

Der Block steht bewusst **vor** dem Include und nicht in einer Kopie von
`tabular.html`: Eine Kopie nur für eine eingeschobene Zeile wäre bei jedem
Django-Upgrade nachzuziehen.

### Konventionsabweichung: eigenes ESM-Modul ohne jQuery

`changeForm.js` ist ein klassisches Skript ohne Exporte und damit **nicht
importierbar**; eine Ergänzung dort wäre nicht testbar. Deshalb ein eigenes
Modul, eingebunden in `change_form.html` als `<script type="module">`. Der Aufruf
`initAttributeFilter()` steht im Template und nicht im Modul, damit der Import
selbst nebenwirkungsfrei bleibt und der Unit-Test die Funktion gezielt aufrufen
kann.

Bewusst **vanilla DOM** statt jQuery, obwohl der Nachbarcode jQuery nutzt: So
läuft der Unit-Test in Node ohne jQuery-Aufbau. Die Funktion ist nebenwirkungsfrei
aufrufbar und gibt zurück, ob ein Suchblock gefunden wurde – auf der Anlageseite
und bei leerem Inventar gibt es keinen.

### Zwei Testebenen, die sich gegenseitig halten

Neu eingeführt sind **vitest** und **jsdom** als `devDependencies` samt
`npm run test:js` und einem Schritt in `tests.yml`. Das betrifft das ganze
Repository, nicht nur diese App – DH-74 hatte einen JS-Testrunner für die
`confirm`-Rückfrage noch ausdrücklich als unverhältnismäßig verworfen. Hier fällt
die Abwägung anders aus, weil das Verhalten nahezu vollständig im Browser liegt
und das Kernrisiko des Tickets serverseitig gar nicht prüfbar ist.

| Ebene | Datei | prüft |
| ----- | ----- | ----- |
| JS-Unit | `pygeoapi/tests/js/attributeFilter.test.js` | Filterlogik gegen eine jsdom-Fixture, die Djangos Inline-Markup nachbildet |
| Django | `pygeoapi/tests/test_collection_admin.py` | dass Djangos Markup wirklich so aussieht, und dass ein Sichern unberührt bleibt |

Keine Ebene genügt allein: Änderte ein Django-Upgrade die Form einer
Readonly-Zelle, bliebe der JS-Test **grün**, während die Maske nicht mehr
filterte. Der Django-Test
`test_every_row_offers_the_name_cell_the_filter_reads` prüft denselben Selektor
über die bereits vorhandene `CELL`-Regex und fängt genau das ab.

Der wichtigste JS-Test ist `keeps the posted state identical through filtering and
resetting`: Er nimmt alle `name`/`value`-Paare der Formularelemente samt
`disabled`-Zustand vor dem Filtern, nach dem Filtern, nach einer Eingabe ohne
Treffer und nach dem Zurücksetzen auf und vergleicht sie. Bleiben sie identisch,
kann die Filterung die Rechtelage **strukturell** nicht verändern. Die
serverseitige Entsprechung ist
`test_a_post_of_the_rendered_state_changes_no_right`.

Gegengeprüft durch Mutation: `remove()` statt `classList.toggle()` lässt sieben
JS-Tests scheitern, ein fehlendes `preventDefault()` einen, ein `name`-Attribut am
Suchfeld den zugehörigen Django-Test.

#### Abdeckungsgrenze

Geprüft ist die **Modullogik gegen jsdom**, nicht der echte Browser. Nicht
abgedeckt sind damit: die implizite Formularabsendung bei `Enter` (jsdom
implementiert sie nicht – der Test prüft nur, dass das Ereignis
`defaultPrevented` ist), das Zusammenspiel mit select2, die tatsächliche Wirkung
von `display: none` und das Laufzeitverhalten unter echter Renderlast. Die
Laufzeitprobe mit 500 Zeilen sichert gegen einen versehentlich quadratischen
Durchlauf ab und ist **keine** Performance-Zusage. Diese Lücken deckt die
Handprobe unten; sie ist für DH-76 vollständig und ohne Befund durchlaufen.

### Handprobe

Bei jeder Änderung an `attributeFilter.js` oder am Suchblock zu wiederholen, an
einer Kollektion mit mindestens 100 Attributen:

1. Eingrenzen und Zurücksetzen – ohne merkliche Verzögerung.
2. Eingabe ohne Treffer – der Hinweis erscheint statt einer leeren Tabelle.
3. Bei aktiver Filterung eine Rolle in einer **sichtbaren** Zeile ändern,
   sichern, Seite neu aufrufen: Die geänderte Zeile stimmt, **alle
   ausgeblendeten Zeilen haben ihre Rollen unverändert.**
4. Filtern, zurücksetzen, sichern: keine Änderung an der Rechtelage und kein
   Eintrag über eine Rolle in der Objekt-Historie.
5. `Enter` im Suchfeld sendet das Formular nicht ab.
6. Dabei mitmessen, ob die select2-Initialisierung die Maske spürbar verzögert.

## Abgleich des Attributinventars

`reconcile_collection_inventory(collection, columns)` in
[`pygeoapi/services.py`](../../pygeoapi/services.py) gleicht das Inventar einer
Kollektion gegen eine Spaltenliste ab und meldet vier Kategorien zurück
(`ReconcileResult`): `added`, `vanished`, `reappeared`, `retyped`. Angestoßen wird
er über den Knopf *Attribute abgleichen* über der Attributübersicht.

| Fall | Wirkung |
| ---- | ------- |
| in der Quelle, nicht im Inventar | neuer Eintrag samt `data_type` |
| im Inventar, nicht in der Quelle | `is_present=False`; Eintrag, `data_type` und Rechte bleiben |
| in der Quelle, `is_present=False` | `is_present=True` **unter derselben PK**, die Rechte gelten weiter |
| abweichender `data_type` | wird fortgeschrieben, Rechte unberührt |
| identisch | nichts angefasst (No-op) |

Eine **leere Spaltenliste** lässt das Inventar unverändert und wird niemals als
„alle Attribute verschwunden" gedeutet – sonst nähme eine kurzzeitig unerreichbare
Quelle die gesamte Rechtelage aus dem Blick. Die Kategorien schließen sich nicht
aus: Ein Attribut, das wieder auftaucht und seinen Typ geändert hat, steht in
beiden Listen.

### Datenweg über den Browser – das akzeptierte Risiko

Der Server öffnet zum Abgleichzeitpunkt **keine** Verbindung zur Quelle. Die
Spalten kommen aus dem Browser: `attributeReconcile.js` holt sie beim Klick über
den bestehenden Endpunkt `pygeoapi:get_database_columns` und legt sie als JSON in
ein verstecktes Feld des Änderungsformulars.

Das ist die Vorgabe des Tickets und dort ausdrücklich als akzeptiertes Risiko
benannt, weil die Maske hinter einem Admin-Konto liegt. **Ein serverseitiges
Nachlesen wäre technisch möglich und ist bewusst nicht umgesetzt.** Was das Risiko
begrenzt:

- Die Liste wird vollständig validiert (siehe unten), bevor sie geschrieben wird.
- Eine **erfundene Attributzeile verschafft kein Recht.** Leserechte werden
  ausschließlich ausdrücklich vergeben, Verweigerung bleibt der Standard; eine
  Zeile ohne Entsprechung in der Quelle liefert nichts aus.
- Attributnamen erscheinen ausschließlich escaped in der Anzeige.
- Wer die Maske erreicht, ist Mitglied von `PYGEOAPI_GROUP_NAME` und darf die
  Kollektion ohnehin auf eine beliebige Tabelle zeigen lassen.

Was das Risiko **nicht** abdeckt: Ein manipulierter POST kann Inventarzeilen
anlegen, die es in der Quelle nicht gibt, und vorhandene als „nicht mehr
vorhanden" kennzeichnen. Letzteres macht bestehende Rechte wirkungslos, ohne sie
zu löschen – ein Abgleich mit der echten Liste stellt den Zustand wieder her.

Die Prämisse des Tickets, das Formular habe die Spaltenliste „ohnehin schon
geladen", trifft übrigens **nicht** zu: `changeForm.js` lädt beim Aufbau der Seite
nur die Schemata nach, `fetchColumns()` läuft erst, wenn jemand Schema und Tabelle
von Hand neu wählt. Deshalb holt der Knopf die Liste beim Klick selbst; am
Ladeverhalten des Formulars ist nichts geändert.

### Geänderte Antwortform der Spaltenauskunft

`get_database_columns()` liefert statt einer Liste von Strings eine Liste von
Dicts (`{'name': …, 'type': …}`). Innerhalb der App gibt
es genau einen Konsumenten: `populateFieldSelects()` in `changeForm.js`, im selben
Commit mitgezogen. Die gleichnamige Funktion in `stadtbereichskatalog` ist eine
eigene Implementierung mit anderer Signatur und nicht betroffen.

#### Nicht auflösbarer Datentyp

`format_type()` liefert **kein** `NULL`, wenn es eine Typ-OID nicht auflösen kann:
Mit zwei Nicht-NULL-Argumenten – und `atttypid` ist nie `NULL` – gibt es den
Platzhalter `'???'` zurück (an der Entwicklungsdatenbank gegengeprüft:
`select format_type(999999, 1)` → `???`). Das ist eine gültige Zeichenkette, die
jede nachgelagerte Prüfung bestünde und als Datentyp im Inventar landete.

`get_database_columns()` bildet deshalb sowohl `'???'` als auch einen fehlenden
Wert auf `''` ab; die Konstante `UNRESOLVABLE_TYPE` steht dort, wo die Semantik
von `format_type()` bekannt ist, und nicht in der Formularvalidierung. Damit gilt
die Zusage „kein Ersatzwert, der einen Typ vortäuscht" auch auf diesem Weg.
Voraussetzung des Falls ist eine kaputte oder gerade abgeräumte Typ-Registrierung
im Katalog der Quelle; er ist in der Praxis sehr selten, aber nicht unmöglich.
Festgeschrieben in `pygeoapi/tests/test_database_columns.py`.

### Validierung im Formularfeld

`CollectionForm.clean_reconcile_columns()` ist die **einzige** Stelle, die
entscheidet, was der Abgleich annimmt – kein Rohzugriff auf `request.POST` im
Admin. Abgewiesen wird: kein JSON, keine Liste, Eintrag kein Objekt, Name fehlt
oder ist leer, Name länger als 100 Zeichen, doppelter Name innerhalb der Liste,
mehr als `MAX_COLUMNS` Einträge. Jeder Fall macht das **ganze Formular** ungültig:
nichts gespeichert, kein Abgleich, Inventar unverändert.

Die Obergrenze ist keine technische, sondern eine fachliche Grenze: Die größte
Kollektion des Fachbereichs hat rund 30 Attribute. Eine Liste weit darüber deutet
auf die falsche Tabelle oder einen manipulierten POST.

Weil eine breite Fachverfahrens-View diese Zahl durchaus überschreiten kann und
eine Ablehnung das **ganze Formular** ungültig macht, ist die Grenze eine
Einstellung und keine Konstante: `PYGEOAPI_MAX_COLUMNS`, Vorgabe
`MAX_COLUMNS_DEFAULT = 100` in `pygeoapi/constants_vars.py` – dasselbe Muster wie
`PYGEOAPI_GROUP_NAME`. Ein Deployment kann sie damit ohne Codeänderung anheben.

`constants_vars.max_columns()` liest die Einstellung **bei jedem Aufruf** und
nicht beim Import. Ein Modulkonstanten-`getattr(settings, …)` wird genau einmal
ausgewertet, wenn Django das Modul lädt; `override_settings` im Test käme dann zu
spät und griffe nicht. Die Zahl steht auch in der Hilfe – dort ohne
Einstellungsnamen, weil sie sich an die bedienende Person richtet.

Ein `data_type` über 100 Zeichen wird zu `''` und **nicht gekürzt** – ein
gekürzter Wert täuschte einen Typ vor, den die Quelle nicht ausweist. Das
Attribut selbst wird aufgenommen, nur ohne Typ. Bewusst keine fünfte Zahl in der
Rückmeldung: Der Fall ist mit realen `format_type()`-Werten praktisch
ausgeschlossen und in `hilfe/` benannt.

#### Fehler der versteckten Felder gehören auf Formularebene

`clean()` verschiebt die Fehler von `reconcile` und `reconcile_columns` nach
`add_error(None, …)`. Grund: Djangos `admin/change_form.html` rendert oben
ausschließlich `adminform.form.non_field_errors`, und Feldfehler erscheinen nur
innerhalb eines Fieldsets. Die beiden Felder stehen aber bewusst **außerhalb**
aller Fieldsets (siehe unten) – ihre Meldung erschiene sonst **nirgends**, und
eine abgelehnte Liste wäre ein blankes „Bitte den Fehler korrigieren" ohne Grund.

### Mengenbasierter Schreibweg

Eine Lesung plus höchstens vier Schreibvorgänge, alles in `transaction.atomic()`:
`bulk_create(ignore_conflicts=True)` für Neuaufnahmen, je ein
`filter(pk__in=…).update(is_present=…)` für verschwundene und wieder aufgetauchte,
`bulk_update(objs, ['data_type'])` für Typänderungen. Die Abfragezahl wächst damit
**nicht** mit der Attributzahl; zeilenweise wären es bei 100 Spalten 100 Abfragen.

`bulk_create()`/`bulk_update()` umgehen `save()` und damit `full_clean()` – die
oben dokumentierte bewusste Grenze. Zulässig, weil die Prüfung ins Formularfeld
vorgezogen ist, die Kollektion existiert und nur Namen eingefügt werden, die der
Soll-Ist-Vergleich als fehlend ausweist. `ignore_conflicts=True` aus demselben
Grund wie bei `save_permissions()`: Eine von einem parallelen Speichervorgang
eingefügte Zeile ist der gewünschte Endzustand, kein Fehler. Akzeptierte
Ungenauigkeit: Eine so übersprungene Zeile zählt trotzdem als „neu aufgenommen".

### Auslösung, Rückmeldung und Objekt-Historie

Der Abgleich läuft in `CollectionAdmin.save_related()` – nach `super()`, damit die
Pfade von Rollenzuweisung und Hinweis unberührt bleiben, und vor
`reload_after_commit()`. Es bleibt bei **genau einem** Konfigurations-Reload je
Speichervorgang; `test_the_reload_happens_once_per_save_regardless_of_the_changes`
deckt das weiterhin ab.

Das Ergebnis liegt am `form` (`form.reconcile_result`) und **nicht** an `self`: Ein
`ModelAdmin` ist ein prozessweites Singleton, ein Wert an `self` leckte in den
nächsten Request. `self._service_cache` in `get_queryset()` ist ein bestehender
Fehler dieser Art und ausdrücklich kein Vorbild. `construct_change_message()`
läuft nach `save_related()` und liest das Ergebnis von dort.

Die Rückmeldung nennt nur die vier Zahlen – die Namen stehen in der Tabelle, auf
die das vom Knopf angehängte `_continue` zurückführt. Der Eintrag in der
Objekt-Historie nennt sie dagegen vollständig und ist **strukturiert**, aus dem
schon bei der Rechtevergabe dokumentierten Grund: Ein String ohne führendes `[`
verdrängt die Einträge des Elternformulars. Ein No-op erzeugt keinen Eintrag.

Aus `form.changed_data` werden `reconcile` und `reconcile_columns` vor dem Aufbau
der Meldung entfernt. Ohne das nennt Djangos eigener Teil der Meldung die beiden
Trägerfelder bei jedem Abgleich als geänderte Felder der Kollektion.

### Markup-Vertrag des Abgleichs

- Der Knopf trägt **kein `name`-Attribut** und `type="button"`: Mit `name` landete
  er im POST, mit `submit` sicherte er die Kollektion, statt erst die Spaltenliste
  zu holen.
- Die URL der Spaltenauskunft steht als **`data-columns-url`** am Knopf. Die
  globale Konstante `GET_DATABASE_COLUMNS_URL` steht in einem klassischen
  Inline-Skript und wäre aus einem Modul nur über den globalen Scope erreichbar.
- Gelesen werden **`#id_database_connection`, `#id_schema`, `#id_table`** – die
  echten Modellfelder. Die `*_select`-Hilfslisten sind beim Seitenaufbau leer.
- Knopf und Statusabsatz stehen **vor** der Verzweigung in
  `collection_attributes.html`, damit sie auch im Leer-Zweig erscheinen.
- Die beiden versteckten Felder stehen in `{% block after_related_objects %}` und
  damit innerhalb des `<form>`, aber **außerhalb** der Fieldsets: In einem
  Fieldset erzeugten sie eine leere versteckte Zeile in *Datenbankquelle*. Mit
  `{% if change %}` geklammert, denn die Anlageseite hat kein Inventar.
- `initAttributeReconcile()` **leert beide Felder beim Laden.** Browser stellen
  Feldwerte bei Zurück-Navigation wieder her; ein wiederhergestellter Marker
  machte das nächste gewöhnliche Sichern zu einem Abgleich.
- Bei leerem oder fehlerhaftem Ergebnis wird **nicht** abgesendet: Sichern und
  Reload für nichts wären die falsche Antwort auf eine unerreichbare Quelle. Der
  serverseitige Zweig bleibt als Absicherung bestehen und ist getestet.

#### Die Ursache benennen, ohne die Verbindungsdaten preiszugeben

Das Akzeptanzkriterium verlangt, dass die Meldung „die Ursache verständlich"
nennt. `fetchColumns()` gibt deshalb `{columns}` **oder** `{cause}` zurück und
unterscheidet drei Ursachen:

| Ursache | Konstante | Fall |
| ------- | --------- | ---- |
| `Die Quelle antwortet nicht.` | `UNREACHABLE` | `fetch()` lehnt ab – die Anfrage kam nicht durch |
| `Die Spaltenauskunft meldet einen Fehler.` | `FAULTY_ANSWER` | `!response.ok`, unlesbares JSON oder eine Antwort ohne `columns` |
| `Die Quelle liefert keine Spalten – …` | `NO_COLUMNS` | erreichbar und geantwortet, aber eine leere Liste |

Der Zusatz `UNCHANGED` hängt der Handler an, statt ihn in jede der drei
Konstanten zu schreiben. **Keine** der Meldungen nennt Host, Benutzername oder
Passwort; unterschieden wird ausschließlich nach der Art des Fehlschlags, nie
nach seinem Inhalt. Ein unlesbares JSON zählt bewusst zu `FAULTY_ANSWER` und
nicht zu `UNREACHABLE` – die Quelle hat ja geantwortet.

Der serverseitige Absicherungszweig trägt seit dieser Auffächerung einen eigenen,
knapperen Text („Der Abgleich kam ohne Spaltenliste an; …"): Er beschreibt einen
anderen Fall – einen POST mit Marker, aber ohne Liste – und die frühere wörtliche
Doppelung zwischen JS-Konstante und `gettext`-String ist damit aufgelöst.

### Drei Testebenen

| Ebene | Datei | prüft |
| ----- | ----- | ----- |
| Dienst | `pygeoapi/tests/test_collection_reconcile.py` | die Abgleichslogik gegen die Datenbank, inkl. Abfragezahl |
| Django | `pygeoapi/tests/test_collection_admin.py` | den ganzen POST samt Validierung, Meldung, Historie, Berechtigung und Markup-Vertrag |
| JS-Unit | `pygeoapi/tests/js/attributeReconcile.test.js` | das Browser-Modul gegen eine jsdom-Fixture |

Bei der Abfragezahl werden die **Savepoints** herausgerechnet, die der `TestCase`
um jeden Test legt; gemessen wird an einem Abgleich, der alle vier Kategorien
auslöst – sonst deckte der Vergleich nur die eine Abfrage des Inserts ab.

Gegengeprüft durch Mutation: eine leere Liste als „alle verschwunden" gedeutet,
Löschen statt Kennzeichnen, ein fehlendes Leeren der Felder beim Laden und ein
Absenden trotz leeren Ergebnisses lassen jeweils die zugehörigen Tests scheitern.

#### Abdeckungsgrenze

Nicht automatisiert geprüft sind der echte Netzwerkweg zur Quelldatenbank
(`format_type()` gegen eine echte PostGIS-Tabelle), das Zusammenspiel mit select2
und die tatsächliche Navigation nach `form.submit()` – jsdom implementiert keine
Formularabsendung, der Test prüft den Aufruf gegen einen Spy. Diese Lücken deckt
die Handprobe unten.

### Handprobe

Bei jeder Änderung an `attributeReconcile.js`, an `services.py` oder an der
Spaltenauskunft zu wiederholen, an einer Kollektion auf einer echten
PostGIS-Tabelle; Probedaten anschließend zurückbauen:

1. Änderungsseite einer Kollektion mit leerem Inventar – Leer-Hinweis **und** Knopf
   sind sichtbar.
2. Abgleichen: Die Seite bleibt auf der Änderungsseite, die Meldung nennt vier
   Zahlen, die Tabelle zeigt alle Spalten samt Datentyp.
3. Zweiter Abgleich ohne Änderung in der Quelle: „keine Änderung ergeben".
4. Spalte in der Quelle umbenennen und abgleichen: alte Zeile „nicht mehr
   vorhanden" **mit erhaltenen Rollen**, neue Zeile rechtefrei. Zurückbenennen und
   abgleichen: dieselbe Zeile ist wieder vorhanden und hat ihre Rollen noch.
5. Spaltentyp in der Quelle ändern und abgleichen: Datentyp fortgeschrieben,
   Rollen unverändert.
6. Mit falschem Datenbank-Host abgleichen: „Die Quelle antwortet nicht", Inventar
   unverändert, kein Sichern. Mit falschem Tabellennamen: „Die Quelle liefert keine
   Spalten".
7. Objekt-Historie prüfen: ein Eintrag zum *Attributinventar* mit den Namen je
   Kategorie, keine Nennung der Trägerfelder.

Für DH-77 vollständig und **ohne Befund** durchlaufen, an einer eigens angelegten
Tabelle in der Quelldatenbank des Entwicklungssystems (danach zurückgebaut).
`format_type()` lieferte dabei genau die Schreibweise der Quelle:

```
integer · character varying(50) · numeric(5,2) · text · geometry(Point,25833)
```

Belegt sind damit auch die Punkte, die keine Testebene abdeckt: Der Umbenennungs-
und Rückbenennungslauf behielt Primärschlüssel und Leserecht (`is_present`
wechselte, `data_type` blieb `text`), ein `integer` → `bigint` in der Quelle wurde
fortgeschrieben, ohne Rechte anzutasten, und die Objekt-Historie lautete

```
Aufgenommen: hinweis und nicht mehr vorhanden: bemerkung für Attributinventar „…“ geändert.
Datentyp aktualisiert: pflanzjahr für Attributinventar „…“ geändert.
```

Ein Abgleich ohne Änderung hinterließ dort nur Djangos „Keine Felder geändert." –
die beiden Trägerfelder erscheinen nicht mehr. Bei einem nicht auflösbaren Host
lieferte die Spaltenauskunft `[]`, die Maske meldete „keine Spaltenliste
ermittelt" und das Inventar blieb unverändert.

## Grenzen des Modells

- Keine Rechte auf **einzelne Datensätze**: die Prüfung beschränkt die
  ausgelieferten Eigenschaften, nicht die Objektmenge. Ein einziges Leserecht an
  einer Kollektion legt damit Existenz, `id` und exakte Geometrie jeder Zeile
  offen – siehe [`hilfe/pygeoapi/leserechte.md`](../../hilfe/pygeoapi/leserechte.md).
- Änderungshistorie nur über die **Objekt-Historie** der Kollektion, also nur für
  Vergabe und Entzug über die Attributübersicht. Kaskadierte Löschungen und
  Schreibzugriffe an der Maske vorbei sind darin nicht enthalten.
- `id_field` und `geom_field` sind ungeprüfte Freitextfelder und werden nicht
  gegen die Quelle validiert. Eine Umbenennung kann ein bestehendes Recht auf
  eine gesperrte Zeile fallen lassen; es wird dann als „wirkungsloses Recht"
  ausgewiesen und ist über die Maske nicht mehr entfernbar.
- Die Maske ist **attributzentriert** und beantwortet „welche Rollen dürfen
  dieses Attribut lesen". Die umgekehrte Betriebsfrage „welche Attribute darf
  diese Rolle lesen" lässt sich nur durch Vergleich aller Zeilen beantworten.
  Eine rollenzentrierte Sicht ist ausdrücklich Nicht-Ziel dieser Ausbaustufe.
- Jede Zeile trägt die **vollständige** Optionsliste; es entstehen Attributzahl
  mal Rollenzahl `option`-Elemente. Gemessen: 100 Attribute mal 30 Rollen ergeben
  rund 340 KiB und 3007 Elemente. Bei deutlich mehr Rollen wäre ein Nachladen per
  AJAX nötig – ein Muster, das das Projekt bisher nirgends verwendet.
- Die **Vererbung** ist hier nur gespeichert, nicht aufgelöst; das Auflösen
  gehört zur Durchsetzung. Ein Attribut ohne jedes Recht wird davon nicht geheilt:
  Geerbt werden nur vorhandene Rechte.
- Der Hinweis auf Attribute ohne Rolle wirkt nur **innerhalb der Pflegemaske**
  einer Kollektion. Es gibt keine Auswertung über alle Kollektionen hinweg, keinen
  Bericht und keine Meldung an Dritte; ob dieselbe Prüfung bei einer
  **Veröffentlichung** greifen soll, ist offen und gehört zur Durchsetzung.
- Die Meldung beim Sichern nennt höchstens **zehn** Namen. Die vollständige Liste
  steht nur in der Spalte *Hinweis* der Tabelle – nach einem Abgleich mit vielen
  neuen Attributen ist das eine bewusste Kappung, keine Vollständigkeitszusage.
- Die Suche greift **nur über den Attributnamen** und nur über die Zeilen, die die
  Seite ohnehin geladen hat. Eine Filterung nach zugewiesener Rolle und ein Filter
  „nur Attribute ohne Rolle" sind ausdrücklich Nicht-Ziel dieser Ausbaustufe; für
  beides müssten die Rollen je Zeile maschinenlesbar im Markup stehen (siehe
  *Roadmap*).
- **Ohne JavaScript gibt es keine Suche und keinen Abgleich.** Die Tabelle zeigt
  dann durchgehend alle Attribute, und der Knopf tut beim Klick nichts; verloren
  geht nichts, es fehlt nur die Eingrenzung beziehungsweise der Einstieg.
- Der Abgleich läuft **je Kollektion und von Hand.** Es gibt keinen Zeitplan, keine
  Sammelaktion über alle Kollektionen und keine Auslösung bei einer Änderung von
  Datenbankverbindung, Schema oder Tabelle. Wer eine Kollektion umstellt, muss den
  Abgleich selbst anstoßen; bis dahin beschreibt das Inventar die vorige Quelle.
- Ein neu aufgenommenes Attribut erscheint erst **nach dem Neuaufbau der Seite** in
  der Tabelle: Der Abgleich läuft in `save_related()`, die gerenderten Zeilen sind
  der Stand davor. Das `_continue` des Knopfes deckt das ab. Akzeptierte
  kosmetische Nebenfolge: Ein rechtefreies Attribut, das derselbe Abgleich gerade
  als „nicht mehr vorhanden" kennzeichnet, kann in der Warnung **dieses**
  Speichervorgangs noch auftauchen; beim nächsten Aufruf der Maske ist es korrekt.
- Ein `data_type` über 100 Zeichen bleibt **leer**, ohne dass die Rückmeldung das
  als eigene Zahl ausweist.
- Die **Zebra-Streifung** der Inline-Zeilen wird durch das Ausblenden unregelmäßig:
  `{% cycle %}` in `tabular.html` läuft beim Rendern, das Ausblenden erst danach.
  Rein kosmetisch, von keinem Akzeptanzkriterium berührt und bewusst nicht
  nachgezogen – eine Korrektur bräuchte eine Neuvergabe der Zeilenklassen bei jedem
  Tastendruck.
- **Bis 120 Attribute ist die Maske belegt bedienbar.** Handprobe an einer
  Kollektion mit **120 Attributen und 25 Rollen** auf einem Entwicklungssystem:
  411 KiB Seite, 3008 `option`-Elemente, 120 select2-Felder, 217 ms serverseitige
  Renderzeit. Im Browser waren Seitenaufbau und Filterung ohne merkliche
  Verzögerung; die select2-Initialisierung fiel dabei **nicht** ins Gewicht, eine
  verzögerte Initialisierung ist damit vorerst kein Folgeticket.

  Der Filterdurchlauf selbst skaliert gutmütig: Er indexiert einmal und schaltet je
  Eingabe nur `classList` um; über 500 Zeilen bleibt er in jsdom weit unter der
  Wahrnehmungsschwelle. **Eine obere Grenze ist damit nicht bestimmt** – 120 ist
  der geprüfte Stand, nicht das Maximum. Wächst eine Quelltabelle deutlich darüber
  hinaus, ist zuerst die select2-Initialisierung zu messen und nicht die Filterung;
  sie trägt die Ladezeit und stammt aus DH-74.

## Roadmap

| Ticket | Inhalt                                                                         |
| ------ | ------------------------------------------------------------------------------ |
| DH-67  | `access_control`-Block der Konfiguration erzeugen, dabei die Vererbung auflösen |
| DH-68  | Filterung der Antworten zur Laufzeit                                            |

Noch nicht eingeplant, als Folgetickets aus DH-76 vorgeschlagen: eine Filterung
nach **zugewiesener Rolle** („welche Attribute darf Rolle X lesen") und ein Filter
**„nur Attribute ohne Rolle"**, der den Hinweis oben gezielt abarbeitbar macht.
Beide brauchen die Rollen je Zeile maschinenlesbar im Markup und eigene
Akzeptanzkriterien; die rollenzentrierte Sicht ist zudem als Nicht-Ziel der
heutigen Maske festgehalten.

**Das Inventar füllt sich nur, wenn jemand den Abgleich anstößt.** Eine neu
angelegte Kollektion zeigt bis dahin den Leer-Hinweis – das ist der beabsichtigte
Ausgangszustand und kein Defekt.

**Zwei Voraussetzungen sind noch offen und begrenzen die Maske heute:** Es gibt
keine Pflegemaske für den **Rollenkatalog** – `Role` ist in keinem Admin
registriert –, und die Basisrolle `public` wird nirgends angelegt. Ohne Rollen im
Katalog ist die Auswahlliste jeder Zeile leer – und weil dann keine Rolle
zuweisbar ist, trägt jede Zeile den Hinweis *„von keiner Rolle lesbar"* und jedes
Sichern warnt. Beides ist zutreffend, nicht defekt. Wann der Rollenkatalog eine
Pflegemaske und `public` ein Seeding erhält, ist als eigenes Ticket noch nicht
eingeplant.

## Ausrollen

Migrationsweg, Rückweg und die Dev-Fixture sind im
[README](../../README.md#einführung-des-rechtesystems-in-bestehenden-instanzen)
beschrieben.
