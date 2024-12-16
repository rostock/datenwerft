# _Datenwerft.HRO_

Web-Anwendung zur einfachen Erfassung von Geodaten, die auf [_Django_](https://www.djangoproject.com/) aufsetzt

## Voraussetzungen

-   [_Python_](https://www.python.org/) (>= v3.10)
-   [_pip_](https://pip.pypa.io/)
-   [_GDAL_](https://gdal.org/)
-   [_PostgreSQL_](https://www.postgresql.org/) mit der Erweiterung [_PostGIS_](https://postgis.net/)
-   [_npm_](https://www.npmjs.com/)
-   optional [_Redis_](https://redis.io/)
-   optional für App _Toolbox_ siehe [hier](toolbox/README.md)

## Installation

1. neue virtuelle _Python_-Umgebung:

```bash
python3 -m venv /usr/local/datenwerft/venv
```

2. Projekt klonen:

```bash
git clone https://github.com/rostock/datenwerft /usr/local/datenwerft/datenwerft
```

3. virtuelle _Python_-Umgebung aktivieren:

```bash
source /usr/local/datenwerft/venv/bin/activate
```

4. benötigte _Python_-Module (unter anderem _Django_) installieren via _pip_:

```bash
pip install -r /usr/local/datenwerft/datenwerft/requirements.txt
```

5. leere _PostgreSQL_-Datenbank für die Anwendungsadministration anlegen
6. leere _PostgreSQL_-Datenbank mit der Erweiterung _PostGIS_ für die App _Antragsmanagement_ anlegen
7. leere _PostgreSQL_-Datenbank mit der Erweiterung _PostGIS_ für die App _BEMAS_ anlegen
8. leere _PostgreSQL_-Datenbank mit der Erweiterung _PostGIS_ für die App _Datenmanagement_ anlegen
9. Datenbankschema in Datenbank für die App _Datenmanagement_ installieren (da keines der Datenmodelle in dieser App von _Django_ verwaltet wird):

```bash
psql -h [Datenbankhost] -U [Datenbanknutzer] -d [Datenbankname] -f datenmanagement/sql/schema.sql
```

## Konfiguration

1. Konfigurationsdatei auf Basis der entsprechenden Vorlage erstellen:

```bash
cp /usr/local/datenwerft/datenwerft/secrets.template /usr/local/datenwerft/datenwerft/secrets.py
```

2. Konfigurationsdatei `/usr/local/datenwerft/datenwerft/settings.py` entsprechend anpassen
3. Service-Datei für [_Celery_](https://github.com/celery/celery) auf Basis der entsprechenden Vorlage erstellen:

```bash
cp /usr/local/datenwerft/datenwerft/celery.service.template /etc/systemd/system/celery.service
```

4. Service-Datei für _Celery_ entsprechend anpassen

## Initialisierung

1. virtuelle _Python_-Umgebung aktivieren:

```bash
source /usr/local/datenwerft/venv/bin/activate
```

2. JavaScript-Module via _npm_ installieren:

```bash
npm install
```

3. Anwendung initialisieren:

```bash
cd /usr/local/datenwerft/datenwerft
python manage.py migrate --database=antragsmanagement antragsmanagement
python manage.py migrate --database=bemas bemas
python manage.py migrate
python manage.py antragsmanagement_roles_permissions
python manage.py bemas_roles_permissions
```

4. Administrator initialisieren:

```bash
python manage.py createsuperuser
```

5. Webseiten für Hilfe bauen:

```bash
cd /usr/local/datenwerft/datenwerft/hilfe
make html
```

6. statische Dateien initialisieren:

```bash
cd /usr/local/datenwerft/datenwerft
python manage.py collectstatic -c
```

7. Besitzer und Gruppe des Anwendungsverzeichnisses entsprechend des genutzten HTTP-Servers anpassen – siehe unten:

```bash
sudo chown -R wwwrun:www /usr/local/datenwerft/datenwerft
```

8. _Celery_-Worker-Service aktivieren und starten:

```bash
sudo systemctl daemon-reload
sudo systemctl start celery.service
sudo systemctl enable celery.service
```

## Deployment (am Beispiel des [_Apache HTTP Servers_](https://httpd.apache.org/))

Wenn das Deployment mittels _Apache HTTP Server_ realisiert werden soll, **muss** dessen Modul [_mod_wsgi_](https://modwsgi.readthedocs.io) (für _Python_ v3.x) installiert sein, das ein Web Server Gateway Interface (WSGI) für das Hosting von _Python_-Anwendungen zur Verfügung stellt.

Konfigurationsdatei des _Apache HTTP Servers_ öffnen und in etwa folgenden Inhalt einfügen (in diesem Beispiel nutzt die virtuelle _Python_-Umgebung einen _Python_-Interpreter der Version 3.10):

```apache
Alias               /datenwerft/static /usr/local/datenwerft/datenwerft/static
Alias               /datenwerft/uploads /usr/local/datenwerft/datenwerft/uploads
WSGIDaemonProcess   datenwerft processes=[Anzahl CPU x 2] threads=[Anzahl GB RAM x 3] connect-timeout=150 deadlock-timeout=300 eviction-timeout=0 graceful-timeout=150 inactivity-timeout=300 queue-timeout=300 request-timeout=300 shutdown-timeout=5 socket-timeout=300 startup-timeout=15 restart-interval=0 python-path=/usr/local/datenwerft/datenwerft:/usr/local/datenwerft/venv/lib64/python3.11/site-packages:/usr/local/datenwerft/venv/lib/python3.11/site-packages
WSGIProcessGroup    datenwerft
WSGIScriptAlias     /datenwerft /usr/local/datenwerft/datenwerft/datenwerft/wsgi.py process-group=datenwerft

<Directory /usr/local/datenwerft/datenwerft/datenwerft>
  <Files wsgi.py>
      Order deny,allow
      Require all granted
  </Files>
</Directory>
<Directory /usr/local/datenwerft/datenwerft/static>
  Order deny,allow
  Require all granted
</Directory>
<Directory /usr/local/datenwerft/datenwerft/uploads>
  Order deny,allow
  Require all granted
</Directory>
```

## Cronjobs

Für die App _BEMAS_ kann optional ein Cronjob eingerichtet werden, der folgenden Befehl ausführt:

```bash
python manage.py deletepersons
```

Dieser Befehl führt dazu, dass alle Personen gelöscht werden, die nicht als Ansprechpartner:innen mit Organisationen verknüpft sind, nicht als Betreiber:innen mit Verursachern verknüpft sind und die als Beschwerdeführer:innen nur noch mit Beschwerden verknüpft sind, die seit `BEMAS_STATUS_CHANGE_DEADLINE_DAYS` (siehe `secrets.template`) abgeschlossen sind.

## PDF-Export mit eigenen Templates

Für den Export von PDF-Dateien mit eigenen Templates aus der App _Datenmanagement_ mittels der App _Toolbox_ siehe [hier](toolbox/README.md).

## Entwicklung

### Grundsätzliches

Bei Einrückungen werden generell zwei Leerzeichen verwendet, bei Umbrucheinrückungen vier.

### Python

Der Python-Code orientiert sich an der Python-Styling-Konvention [_PEP8_](https://pep8.org/). Es empfiehlt sich ein Tool wie [_pycodestyle_](https://pypi.org/project/pycodestyle/) zur Überprüfung des Codes zu nutzen. Mit Hilfe von zum Beispiel [_autopep8_](https://pypi.org/project/autopep8/) können Python-Dateien auch im Nachhinein noch automatisch korrigiert werden, können dadurch allerdings auch unleserlich werden.

Die Python-Dokumentation wird mittels [Docstrings](https://en.wikipedia.org/wiki/Docstring) in [_reStructuredText_](https://docutils.sourceforge.io/rst.html) geschrieben.

Nützliche Tools für eine Entwicklungsumgebung, wie etwa _pycodestyle_ oder _ruff_ können zusätzlich via _pip_ installiert werden:

```bash
source /usr/local/datenwerft/venv/bin/activate
pip install -r /usr/local/datenwerft/datenwerft/requirements-dev.txt
```

#### _PEP8_-Durchsetzung

Die Vorgaben von _PEP8_ finden mit zwei Ausnahmen vollständig Anwendung:

1. Zeilenlänge wird von 79 auf 99 erhöht
2. Anzahl der Leerzeichen bei der Einrückung wird von vier auf zwei reduziert (ergibt zudem eine Umbrucheinrückung von vier statt acht)

Die entsprechende Konfigurationsdatei `setup.cfg` für _pycodestyle_ ist bereits im Wurzelverzeichnis des Projekts angelegt.

### JavaScript

JavaScript-Funktionen werden mittels [JSDoc](https://en.wikipedia.org/wiki/JSDoc) dokumentiert, angelehnt an [diese Übersicht](https://devhints.io/jsdoc).

## Linting

-   Python-Prüfungen mittels _pycodestyle:_

    ```bash
    cd /usr/local/datenwerft/datenwerft
    sh linting/pycodestyle
    ```

-   _Django_-Prüfungen mittels [_djLint_](https://github.com/Riverside-Healthcare/djlint):

    ```bash
    cd /usr/local/datenwerft/datenwerft
    sh linting/djlint
    ```

-   CSS-Prüfungen mittels [_Stylelint_](https://stylelint.io/):

    ```bash
    cd /usr/local/datenwerft/datenwerft
    sh linting/stylelint
    ```

-   JavaScript-Prüfungen mittels [_ESLint_](https://eslint.org/):

    ```bash
    cd /usr/local/datenwerft/datenwerft
    sh linting/eslint
    ```

-   alle vorgenannten Prüfungen nacheinander:

    ```bash
    cd /usr/local/datenwerft/datenwerft
    sh linting/lint
    ```

## Tests

-   Tests der App _Accounts_ durchführen:

    ```bash
    source /usr/local/datenwerft/venv/bin/activate
    cd /usr/local/datenwerft/datenwerft
    python manage.py test accounts
    ```

-   Tests der App _Toolbox_ durchführen:

    ```bash
    source /usr/local/datenwerft/venv/bin/activate
    cd /usr/local/datenwerft/datenwerft
    python manage.py test toolbox
    ```

-   Tests der App _Datenmanagement_ durchführen:

    -   Einzeltest (Beispiel):

        ```bash
        source /usr/local/datenwerft/venv/bin/activate
        cd /usr/local/datenwerft/datenwerft
        python manage.py test datenmanagement.tests.StrassenTest.test_create
        ```

    -   alle Tests:
        ```bash
        source /usr/local/datenwerft/venv/bin/activate
        cd /usr/local/datenwerft/datenwerft
        python manage.py test datenmanagement
        ```

-   Tests der App _Antragsmanagement_ durchführen:

    ```bash
    source /usr/local/datenwerft/venv/bin/activate
    cd /usr/local/datenwerft/datenwerft
    python manage.py test antragsmanagement
    ```

-   Tests der App _BEMAS_ durchführen:
    ```bash
    source /usr/local/datenwerft/venv/bin/activate
    cd /usr/local/datenwerft/datenwerft
    python manage.py test bemas
    ```

## CI/CD

### Ablauf

1. neuen Branch erstellen – Name des Branches:

    - bei Features: `features/<app-name>/<feature-name>` (Beispiel: `features/datenmanagement/edit-photos`)
    - bei Bugfixes: `bugfixes/<app-name>/<bugfix-name>` (Beispiel: `bugfixes/accounts/emails`)

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

-   _Linting:_ Linting gemäß `.github/workflows/linting.yml`
-   _Tests:_ Tests gemäß `.github/workflows/tests.yml`
-   _Release:_ Release gemäß `.github/workflows/release.yml`
