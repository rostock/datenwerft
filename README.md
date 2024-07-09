# *Datenwerft.HRO*

Web-Anwendung zur einfachen Erfassung von Geodaten, die auf [*Django*](https://www.djangoproject.com/) aufsetzt

## Voraussetzungen

* [*Python*](https://www.python.org/) (>= v3.10)
* [*pip*](https://pip.pypa.io/)
* [*GDAL*](https://gdal.org/)
* [*PostgreSQL*](https://www.postgresql.org/) mit der Erweiterung [*PostGIS*](https://postgis.net/)
* [*npm*](https://www.npmjs.com/)
* optional für App _Toolbox_ siehe [hier](toolbox/README.md)

## Installation

1.  neue virtuelle *Python*-Umgebung:

        python3 -m venv /usr/local/datenwerft/venv

2.  Projekt klonen:

        git clone https://github.com/rostock/datenwerft /usr/local/datenwerft/datenwerft

3.  virtuelle *Python*-Umgebung aktivieren:

        source /usr/local/datenwerft/venv/bin/activate

4.  benötigte *Python*-Module (unter anderem *Django*) installieren via *pip*:

        pip install -r /usr/local/datenwerft/datenwerft/requirements.txt

5.  leere *PostgreSQL*-Datenbank für die Anwendungsadministration anlegen
6.  leere *PostgreSQL*-Datenbank mit der Erweiterung *PostGIS* für die App *Antragsmanagement* anlegen
7.  leere *PostgreSQL*-Datenbank mit der Erweiterung *PostGIS* für die App *BEMAS* anlegen
8.  leere *PostgreSQL*-Datenbank mit der Erweiterung *PostGIS* für die App *Datenmanagement* anlegen
9.  leere *PostgreSQL*-Datenbank für die App *Metadatenmanagement* anlegen

## Konfiguration

1.  Konfigurationsdatei `/usr/local/datenwerft/datenwerft/settings.py` entsprechend anpassen
2.  weitere Konfigurationsdatei erstellen auf Basis der entsprechenden Vorlage:

        cp /usr/local/datenwerft/datenwerft/secrets.template /usr/local/datenwerft/datenwerft/secrets.py

3.  weitere Konfigurationsdatei `/usr/local/datenwerft/datenwerft/settings.py` 
    entsprechend anpassen

## Initialisierung

1.  Datenbankschema in Datenbank für die App *Datenmanagement* installieren (da keines der Datenmodelle in dieser App von *Django* verwaltet wird):

        psql -h [Datenbankhost] -U [Datenbanknutzer] -d [Datenbankname] -f datenmanagement/sql/schema.sql

2.  JavaScript-Module via *npm* installieren:

        npm install

3.  virtuelle *Python*-Umgebung aktivieren:

        source /usr/local/datenwerft/venv/bin/activate

4.  Anwendung initialisieren:

        cd /usr/local/datenwerft/datenwerft
        python manage.py migrate --database=antragsmanagement antragsmanagement
        python manage.py migrate --database=bemas bemas
        python manage.py migrate --database=metadatenmanagement metadatenmanagement
        python manage.py migrate
        python manage.py antragsmanagement_roles_permissions
        python manage.py bemas_roles_permissions

5.  Administrator initialisieren:

        python manage.py createsuperuser

6.  Dateien-Upload-Verzeichnis erstellen (und dessen Besitzer sowie Gruppe entsprechend des 
    genutzten HTTP-Servers anpassen – siehe unten):

        mkdir /usr/local/datenwerft/datenwerft/uploads
        chown -R wwwrun:www /usr/local/datenwerft/datenwerft/uploads

7.  Webseiten für Hilfe bauen:

        cd /usr/local/datenwerft/datenwerft/hilfe
        mkdir source/_static
        make html

8.  statische Dateien initialisieren:

        cd /usr/local/datenwerft/datenwerft
        python manage.py collectstatic -c

## Deployment (am Beispiel des [*Apache HTTP Servers*](https://httpd.apache.org/))

Wenn das Deployment mittels *Apache HTTP Server* realisiert werden soll, **muss** dessen Modul [*mod_wsgi*](https://modwsgi.readthedocs.io) (für *Python* v3.x) installiert sein, das ein Web Server Gateway Interface (WSGI) für das Hosting von *Python*-Anwendungen zur Verfügung stellt.

Konfigurationsdatei des *Apache HTTP Servers* öffnen und in etwa folgenden Inhalt einfügen (in diesem Beispiel nutzt die virtuelle *Python*-Umgebung einen *Python*-Interpreter der Version 3.6):

        Alias               /datenwerft/static /usr/local/datenwerft/datenwerft/static
        Alias               /datenwerft/uploads /usr/local/datenwerft/datenwerft/uploads
        WSGIDaemonProcess   datenwerft processes=2 threads=128 python-path=/usr/local/datenwerft/datenwerft:/usr/local/datenwerft/venv/lib/python3.10/site-packages
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

## Cronjobs

Für die App *BEMAS* kann optional ein Cronjob eingerichtet werden, der folgenden Befehl ausführt:

        python manage.py deletepersons

Dieser Befehl führt dazu, dass alle Personen gelöscht werden, die nicht als Ansprechpartner:innen mit Organisationen verknüpft sind, nicht als Betreiber:innen mit Verursachern verknüpft sind und die als Beschwerdeführer:innen nur noch mit Beschwerden verknüpft sind, die seit `BEMAS_STATUS_CHANGE_DEADLINE_DAYS` (siehe `secrets.template`) abgeschlossen sind.

## PDF-Export mit eigenen Templates

Für den Export von PDF-Dateien mit eigenen Templates aus der App *Datenmanagement* mittels der App *Toolbox* siehe [hier](toolbox/README.md).

## Entwicklung

### Grundsätzliches

Bei Einrückungen werden generell zwei Leerzeichen verwendet, bei Umbrucheinrückungen vier.

### Python

Der Python-Code orientiert sich an der Python-Styling-Konvention [*PEP8*](https://pep8.org/). Es empfiehlt sich ein Tool wie [*pycodestyle*](https://pypi.org/project/pycodestyle/) zur Überprüfung des Codes zu nutzen. Mit Hilfe von zum Beispiel [*autopep8*](https://pypi.org/project/autopep8/) können Python-Dateien auch im Nachhinein noch automatisch korrigiert werden, können dadurch allerdings auch unleserlich werden.

Die Python-Dokumentation wird mittels [Docstrings](https://en.wikipedia.org/wiki/Docstring) in [*reStructuredText*](https://docutils.sourceforge.io/rst.html) geschrieben.

Nützliche Tools für eine Entwicklungsumgebung, wie etwa *pycodestyle,* können zusätzlich via *pip* installiert werden:

        source /usr/local/datenwerft/venv/bin/activate
        pip install -r /usr/local/datenwerft/datenwerft/requirements-dev.txt

#### *PEP8*-Durchsetzung

Die Vorgaben von *PEP8* finden mit zwei Ausnahmen vollständig Anwendung:

1.  Zeilenlänge wird von 79 auf 99 erhöht
2.  Anzahl der Leerzeichen bei der Einrückung wird von vier auf zwei reduziert (ergibt zudem eine Umbrucheinrückung von vier statt acht)

Die entsprechende Konfigurationsdatei `setup.cfg` für *pycodestyle* ist bereits im Wurzelverzeichnis des Projekts angelegt.

### JavaScript

JavaScript-Funktionen werden mittels [JSDoc](https://en.wikipedia.org/wiki/JSDoc) dokumentiert, angelehnt an [diese Übersicht](https://devhints.io/jsdoc).

## Linting

-  Python-Prüfungen mittels *pycodestyle:*

        cd /usr/local/datenwerft/datenwerft
        sh linting/pycodestyle

-  *Django*-Prüfungen mittels [*djLint*](https://github.com/Riverside-Healthcare/djlint):

        cd /usr/local/datenwerft/datenwerft
        sh linting/djlint

-  CSS-Prüfungen mittels [*Stylelint*](https://stylelint.io/):

        cd /usr/local/datenwerft/datenwerft
        sh linting/stylelint

-  JavaScript-Prüfungen mittels [*ESLint*](https://eslint.org/):

        cd /usr/local/datenwerft/datenwerft
        sh linting/eslint

-  alle vorgenannten Prüfungen nacheinander:

        cd /usr/local/datenwerft/datenwerft
        sh linting/lint

## Tests

-  Tests der App *Accounts* durchführen:

        source /usr/local/datenwerft/venv/bin/activate
        cd /usr/local/datenwerft/datenwerft
        python manage.py test accounts

-  Tests der App *Toolbox* durchführen:

        source /usr/local/datenwerft/venv/bin/activate
        cd /usr/local/datenwerft/datenwerft
        python manage.py test toolbox

-  Tests der App *Datenmanagement* durchführen:
   -  Einzeltest (Beispiel):

          source /usr/local/datenwerft/venv/bin/activate
          cd /usr/local/datenwerft/datenwerft
          python manage.py test datenmanagement.tests.StrassenTest.test_create

   -  alle Tests:

          source /usr/local/datenwerft/venv/bin/activate
          cd /usr/local/datenwerft/datenwerft
          python manage.py test datenmanagement

-  Tests der App *Antragsmanagement* durchführen:

        source /usr/local/datenwerft/venv/bin/activate
        cd /usr/local/datenwerft/datenwerft
        python manage.py test antragsmanagement

-  Tests der App *BEMAS* durchführen:

        source /usr/local/datenwerft/venv/bin/activate
        cd /usr/local/datenwerft/datenwerft
        python manage.py test bemas

## CI/CD

### Ablauf

1.  neuen Branch erstellen – Name des Branches:
    - bei Features: `features/APPNAME_worschdsupp` (Beispiel: `features/datenmanagement_fotos-bearbeiten`)
    - bei Bugfixes: `bugfixes/APPNAME_worschdsupp` (Beispiel: `features/accounts_emails`)
2.  Änderungen linten und testen (siehe oben)
3.  Änderungen committen und Commit(s) pushen
4.  Pull-Request erstellen
5.  Review anfordern und durchführen lassen
6.  ggf. Änderungen im Nachgang des Reviews committen und Commit(s) pushen
7.  Pull-Request in Branch `master` mit der Option *Squash and merge* mergen

### *GitHub*-Actions

Bei Commits und Pull-Requests in der Branch `master` werden folgende *GitHub*-Actions in dieser Reihenfolge ausgeführt:

1.  *CodeQL:* CodeQL-Analyse gemäß `.github/workflows/codeql.yml`
2.  *Linting:* Linting gemäß `.github/workflows/linting.yml`
3.  *Tests:* Tests gemäß `.github/workflows/tests.yml`
