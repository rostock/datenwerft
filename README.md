# _Datenwerft.HRO_

Web-Anwendung zur einfachen Erfassung von (Geo-)Daten, die auf [_Django_](https://www.djangoproject.com/) aufsetzt

## Inhalt

1. [Voraussetzungen](#voraussetzungen)
1. [Installation](#installation)
   - [Anwendung](#anwendung)
   - [Datenbanken](#datenbanken)
1. [Konfiguration](#konfiguration)
1. [Initialisierung](#initialisierung)
1. [Start](#start)
1. [Deployment](#deployment)
1. [UML-Klassendiagramme](#uml-klassendiagramme)
1. [Hilfe](hilfe) (für Administration und Nutzung)
1. [Cronjobs](#cronjobs)
1. [PDF-Export mit eigenen Templates](#pdf-export-mit-eigenen-templates)
1. [Entwicklung](#entwicklung)
   - [Grundsätzliches](#grundsätzliches)
   - [Python](#python)
   - [JavaScript](#javascript)
   - [Anpassungen Datenbankschema App _Datenmanagement_](#anpassungen-datenbankschema-app-_datenmanagement_)
1. [Linting](#linting)
1. [Tests](#tests)
1. [CI/CD](#cicd)
   - [Ablauf](#ablauf)
   - [_GitHub_-Actions](#github-actions)

## Voraussetzungen

- [_Python_](https://www.python.org/) (>=3.13)
- [_pip_](https://pip.pypa.io/)
- [_GDAL_](https://gdal.org/)
- [_PostgreSQL_](https://www.postgresql.org/) mit der Erweiterung [_PostGIS_](https://postgis.net/)
- [_npm_](https://www.npmjs.com/)
- optional [_Redis_](https://redis.io/)
- optional für App _Toolbox_ siehe [hier](toolbox/README.md)

## Installation

### Anwendung

1. _Git_-Repository klonen:

```bash
git clone https://github.com/rostock/datenwerft
cd datenwerft
```

2. neue virtuelle _Python_-Umgebung anlegen:

```bash
# ohne Projektmanagement durch uv
python3 -m venv .venv

# mit Projektmanagement durch uv
uv venv
```

3. benötigte _Python_-Module (unter anderem _Django_) installieren via _pip_:

```bash
# ohne uv
source .venv/bin/activate
pip install -r datenwerft/requirements.txt

# mit uv
uv sync
```

### Datenbanken

1. leere _PostgreSQL_-Datenbank für die Anwendungsadministration anlegen
2. leere _PostgreSQL_-Datenbank für die App _GDI.HRO Codelists_ anlegen
2. leere _PostgreSQL_-Datenbank für die App _GDI.HRO Metadata_ anlegen
3. leere _PostgreSQL_-Datenbank mit der Erweiterung _PostGIS_ für die App _Antragsmanagement_ anlegen
4. leere _PostgreSQL_-Datenbank mit der Erweiterung _PostGIS_ für die App _BEMAS_ anlegen
5. leere _PostgreSQL_-Datenbank mit der Erweiterung _PostGIS_ für die App _Datenmanagement_ anlegen
5. leere _PostgreSQL_-Datenbank mit der Erweiterung _PostGIS_ für die App _FMM_ anlegen
6. Datenbankschema in Datenbank für die App _Datenmanagement_ installieren (da keines der Datenmodelle in dieser App von _Django_ verwaltet wird):

```bash
psql -h [Datenbankhost] -U [Datenbanknutzer] -d [Datenbankname] -f datenmanagement/sql/schema.sql
```

## Konfiguration

1. Konfigurationsdatei auf Basis der entsprechenden Vorlage erstellen:

```bash
cp datenwerft/secrets.template datenwerft/secrets.py
```

2. Konfigurationsdatei `datenwerft/secrets.py` entsprechend anpassen
3. Service-Datei für [_RQ_](https://python-rq.org/)-Worker auf Basis der entsprechenden Vorlage erstellen:

```bash
cp rq-worker.service /etc/systemd/system/rq-worker.service
```

4. Service-Datei für _RQ_-Worker entsprechend anpassen

## Initialisierung

1. JavaScript-Module via _npm_ installieren:

```bash
npm install
```

2. Anwendung initialisieren:

```bash
# ohne uv
source .venv/bin/activate
python manage.py migrate --database=antragsmanagement antragsmanagement
python manage.py migrate --database=bemas bemas
python manage.py migrate --database=fmm fmm
python manage.py migrate --database=gdihrocodelists gdihrocodelists
python manage.py migrate --database=gdihrometadata gdihrometadata
python manage.py migrate
python manage.py antragsmanagement_roles_permissions
python manage.py bemas_roles_permissions
python manage.py fmm_roles_permissions
python manage.py gdihrocodelists_roles_permissions
python manage.py gdihrometadata_roles_permissions
python manage.py loaddata --database=gdihrometadata gdihrometadata_initial-data.json

# mit uv
uv run manage.py migrate --database=antragsmanagement antragsmanagement
uv run manage.py migrate --database=bemas bemas
uv run manage.py migrate --database=fmm fmm
uv run manage.py migrate --database=gdihrocodelists gdihrocodelists
uv run manage.py migrate --database=gdihrometadata gdihrometadata
uv run manage.py migrate
uv run manage.py antragsmanagement_roles_permissions
uv run manage.py bemas_roles_permissions
uv run manage.py fmm_roles_permissions
uv run manage.py gdihrocodelists_roles_permissions
uv run manage.py gdihrometadata_roles_permissions
uv run manage.py loaddata --database=gdihrometadata gdihrometadata_initial-data.json
```

3. Administrator initialisieren:

```bash
# ohne uv
python manage.py createsuperuser

# mit uv
uv run manage.py createsuperuser
```

4. statische Dateien initialisieren:

```bash
# ohne uv
python manage.py collectstatic -c

# mit uv
uv run manage.py collectstatic -c
```

## Start

Start der Anwendung (zum Testen oder während der Entwicklung):

1. _RQ_-Worker starten:

```bash
# ohne uv
source .venv/bin/activate
python manage.py rqworker default

# mit uv
uv run manage.py rqworker default
```

2. Entwicklungsserver starten:

```bash
# ohne uv
python manage.py runserver

# mit uv
uv run manage.py runserver
```

## Deployment

Deployment am Beispiel des [_Apache HTTP Servers_](https://httpd.apache.org/):

1. Besitzer und Gruppe des Anwendungsverzeichnisses entsprechend des _Apache HTTP Servers_ anpassen:

```bash
sudo chown -R wwwrun:www /path/to/datenwerft
```

2. _RQ_-Worker-Service aktivieren und starten:

```bash
sudo systemctl daemon-reload
sudo systemctl enable rq-worker.service
sudo systemctl start rq-worker.service
```

3. Wenn das Deployment mittels _Apache HTTP Server_ realisiert werden soll, **muss** dessen Modul [_mod_wsgi_](https://modwsgi.readthedocs.io) (für _Python_ 3.x) installiert sein, das ein Web Server Gateway Interface (WSGI) für das Hosting von _Python_-Anwendungen zur Verfügung stellt.
4. Konfigurationsdatei des _Apache HTTP Servers_ öffnen und in etwa folgenden Inhalt einfügen (in diesem Beispiel nutzt die virtuelle _Python_-Umgebung einen _Python_-Interpreter der Version 3.x):

```apache
Alias                 /datenwerft/static /path/to/datenwerft/datenwerft/static
Alias                 /datenwerft/uploads /path/to/datenwerft/datenwerft/uploads
WSGIDaemonProcess     datenwerft processes=[Anzahl CPU x 2] threads=[Anzahl GB RAM x 3] connect-timeout=150 deadlock-timeout=300 eviction-timeout=0 graceful-timeout=150 inactivity-timeout=300 queue-timeout=300 request-timeout=300 shutdown-timeout=5 socket-timeout=300 startup-timeout=15 restart-interval=0 python-path=/path/to/datenwerft:/path/to/datenwerft/.venv/lib64/python3.1x/site-packages:/path/to/datenwerft/.venv/lib/python3.1x/site-packages
WSGIProcessGroup      datenwerft
WSGIScriptAlias       /datenwerft /path/to/datenwerft/datenwerft/wsgi.py process-group=datenwerft
WSGIApplicationGroup  %{GLOBAL}

<Directory /path/to/datenwerft/datenwerft>
  <Files wsgi.py>
    Order deny,allow
    Require all granted
  </Files>
</Directory>
<Directory /path/to/datenwerft/static>
  Order deny,allow
  Require all granted
</Directory>
<Directory /path/to/datenwerft/uploads>
  Order deny,allow
  Require all granted
</Directory>
```

## UML-Klassendiagramme

Für die Visualisierung der nachfolgend verlinkten UML-Klassendiagramme kann zum Beispiel [dieses Online-Tool](https://plantuml-editor.kkeisuke.com) genutzt werden.

### App _Antragsmanagement_

Klassenstruktur als UML-Diagramm siehe [PlantUML-Datei](antragsmanagement/models/class-structure.puml)

### App _BEMAS_

Klassenstruktur als UML-Diagramm siehe [PlantUML-Datei](bemas/models/class-structure.puml)

### App _FMM_

Klassenstruktur als UML-Diagramm siehe [PlantUML-Datei](fmm/models/class-structure.puml)

### App _GDI.HRO Codelists_

Klassenstruktur als UML-Diagramm siehe [PlantUML-Datei](gdihrocodelists/models/class-structure.puml)

### App _GDI.HRO Metadata_

Klassenstruktur als UML-Diagramm siehe [PlantUML-Datei](gdihrometadata/models/class-structure.puml)

## Cronjobs

Für die App _BEMAS_ kann optional ein Cronjob eingerichtet werden, der folgenden Befehl ausführt:

```bash
# ohne uv
source .venv/bin/activate
python manage.py deletepersons

# mit uv
uv run manage.py deletepersons
```

Zum Hintergrund dieses Befehls siehe [hier](hilfe/bemas/admin.md#datenschutz).

## PDF-Export mit eigenen Templates

Für den Export von PDF-Dateien mit eigenen Templates aus der App _Datenmanagement_ mittels der App _Toolbox_ siehe [hier](toolbox/README.md).

## Entwicklung

### Grundsätzliches

Bei Einrückungen werden generell zwei Leerzeichen verwendet, bei Umbrucheinrückungen vier.

### Python

Der Python-Code orientiert sich an der Python-Styling-Konvention [_PEP8_](https://pep8.org/). Es empfiehlt sich ein Tool wie [_ruff_](https://docs.astral.sh/ruff/) zur Überprüfung des Codes zu nutzen.

Die Python-Dokumentation wird mittels [Docstrings](https://en.wikipedia.org/wiki/Docstring) in [_reStructuredText_](https://docutils.sourceforge.io/rst.html) geschrieben.

Nützliche Tools für eine Entwicklungsumgebung, wie etwa _ruff,_ können zusätzlich via _pip_ installiert werden:

```bash
# ohne uv
source .venv/bin/activate
pip install -r requirements-dev.txt

# mit uv
uv sync --dev
```

#### _PEP8_-Durchsetzung

Die Vorgaben von _PEP8_ finden mit zwei Ausnahmen vollständig Anwendung:

1. Zeilenlänge wird von 79 auf 99 erhöht
2. Anzahl der Leerzeichen bei der Einrückung wird von vier auf zwei reduziert (ergibt zudem eine Umbrucheinrückung von vier statt acht)

Die entsprechende Konfigurationsdatei `pyproject.toml` für (zum Beispiel) _ruff_ ist bereits im Wurzelverzeichnis des Projekts angelegt.

### JavaScript

JavaScript-Funktionen werden mittels [JSDoc](https://en.wikipedia.org/wiki/JSDoc) dokumentiert, angelehnt an [diese Übersicht](https://devhints.io/jsdoc).

### Anpassungen Datenbankschema App _Datenmanagement_

```bash
pg_dump -U [Datenbanknutzer] -O -x -s -N public -N topology -e postgis -e uuid-ossp -f datenmanagement/sql/schema.sql [Datenbankname]
```

> [!WARNING]
> Sobald die Datei `datenmanagement/sql/schema.sql` überschrieben wurde, muss darin die Zeile `SELECT pg_catalog.set_config('search_path', '', false);` in `SELECT pg_catalog.set_config('search_path', 'public', false);` geändert werden!

## Linting

- Python-Prüfungen mittels [_ruff_](https://docs.astral.sh/ruff/):

```bash
sh linting/ruff
```

- _Django_-Prüfungen mittels [_djLint_](https://github.com/Riverside-Healthcare/djlint):

```bash
sh linting/djlint
```

- CSS-Prüfungen mittels [_Stylelint_](https://stylelint.io/):

```bash
sh linting/stylelint
```

- JavaScript-Prüfungen mittels [_ESLint_](https://eslint.org/):

```bash
sh linting/eslint
```

- alle vorgenannten Prüfungen nacheinander:

```bash
sh linting/lint
```

## Tests

- Tests der App _Accounts_ durchführen:

```bash
# ohne uv
python manage.py test accounts

# mit uv
uv run manage.py test accounts
```

- Tests der App _Toolbox_ durchführen:

```bash
# ohne uv
python manage.py test toolbox

# mit uv
uv run manage.py test toolbox
```

- Tests der App _Datenmanagement_ durchführen:
  - Einzeltest (Beispiel):
  ```bash
  # ohne uv
  python manage.py test datenmanagement.tests.StrassenTest.test_create

  # mit uv
  uv run manage.py test datenmanagement.tests.StrassenTest.test_create
  ```

  - alle Tests:
  ```bash
  # ohne uv
  python manage.py test datenmanagement

  # mit uv
  uv run manage.py test datenmanagement
  ```

- Tests der App _Antragsmanagement_ durchführen:
  - Einzeltest (Beispiel):
  ```bash
  # ohne uv
  python manage.py test antragsmanagement.tests.CleanupEventRequestCommentCreateViewTest.test_post_create_success

  # mit uv
  uv run manage.py test antragsmanagement.tests.CleanupEventRequestCommentCreateViewTest.test_post_create_success
  ```

  - alle Tests:
  ```bash
  # ohne uv
  python manage.py test antragsmanagement

  # mit uv
  uv run manage.py test antragsmanagement

- Tests der App _BEMAS_ durchführen:
  - Einzeltest (Beispiel):
  ```bash
  # ohne uv
  python manage.py test bemas.tests.OriginatorModelTest.test_delete

  # mit uv
  uv run manage.py test bemas.tests.OriginatorModelTest.test_delete
  ```

  - alle Tests:
  ```bash
  # ohne uv
  python manage.py test bemas

  # mit uv
  uv run manage.py test bemas

- Tests der App _FMM_ durchführen:
  - Einzeltest (Beispiel):
  ```bash
  # ohne uv
  python manage.py test fmm.tests.FmfModelTest.test_create

  # mit uv
  uv run manage.py test fmm.tests.FmfModelTest.test_create
  ```

  - alle Tests:
  ```bash
  # ohne uv
  python manage.py test fmm

  # mit uv
  uv run manage.py test fmm

- Tests der App _GDI.HRO Codelists_ durchführen:
  - Einzeltest (Beispiel):
  ```bash
  # ohne uv
  python manage.py test gdihrocodelists.tests.CodelistValueModelTest.test_create

  # mit uv
  uv run manage.py test gdihrocodelists.tests.CodelistValueModelTest.test_create
  ```

  - alle Tests:
  ```bash
  # ohne uv
  python manage.py test gdihrocodelists

  # mit uv
  uv run manage.py test gdihrocodelists

- Tests der App _GDI.HRO Metadata_ durchführen:
  - Einzeltest (Beispiel):
  ```bash
  # ohne uv
  python manage.py test gdihrometadata.tests.DataTypeModelTest.test_create

  # mit uv
  uv run manage.py test gdihrometadata.tests.DataTypeModelTest.test_create
  ```

  - alle Tests:
  ```bash
  # ohne uv
  python manage.py test gdihrometadata

  # mit uv
  uv run manage.py test gdihrometadata

## CI/CD

### Ablauf

1. neuen Branch erstellen – Name des Branches:
   - bei Features: `feature/<app-name>/<feature-name>` (Beispiel: `feature/datenmanagement/edit-model-foobar`)
   - bei Bugfixes: `bugfix/<app-name>/<bugfix-name>` (Beispiel: `bugfix/accounts/emails`)
2. Änderungen linten und testen (siehe oben)
3. Änderungen committen und Commit(s) pushen
4. Pull-Request im Branch `main` erstellen
5. Review anfordern und durchführen lassen
6. ggf. Änderungen im Nachgang des Reviews committen und Commit(s) pushen
7. Pull-Request im Branch `main` abschließen:
   - Commit-Message gemäß der Syntax der [Conventional-Commit](https://www.conventionalcommits.org/) gestalten
   - mit der Option _Squash and merge_ mergen

### _GitHub_-Actions

Bei Commits und Pull-Requests in der Branch `main` werden folgende _GitHub_-Actions ausgeführt:

- _Linting:_ Linting gemäß `.github/workflows/linting.yml`
- _Tests:_ Tests gemäß `.github/workflows/tests.yml`
- _Release:_ Release gemäß `.github/workflows/release.yml`
