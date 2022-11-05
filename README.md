# *Datenwerft.HRO*

Web-Anwendung zur einfachen Erfassung von Geodaten, die auf [*Django*](https://www.djangoproject.com/) aufsetzt

## Voraussetzungen

* [*Python*](https://www.python.org/) (v3.x)
* [*pip*](https://pip.pypa.io/) (für *Python* v3.x)
* [*GDAL*](https://gdal.org/)
* [*PostgreSQL*](https://www.postgresql.org/) mit den Erweiterungen [*PostGIS*](https://postgis.net/) und [*uuid-ossp*](https://www.postgresql.org/docs/current/uuid-ossp.html)
* [*npm*](https://www.npmjs.com/)

## Installation

1.  neue virtuelle *Python*-Umgebung:

        python3 -m venv /usr/local/datenwerft/venv

2.  Projekt klonen:

        git clone https://github.com/rostock/datenwerft /usr/local/datenwerft/datenwerft

3.  virtuelle *Python*-Umgebung aktivieren:

        source /usr/local/datenwerft/venv/bin/activate

4.  benötigte *Python*-Module (unter anderem *Django*) installieren via *pip*:

        pip install -r /usr/local/datenwerft/datenwerft/requirements.txt

## Konfiguration

1.  Konfigurationsdatei `/usr/local/datenwerft/datenwerft/settings.py` entsprechend anpassen
2.  weitere Konfigurationsdatei erstellen auf Basis der entsprechenden Vorlage:

        cp /usr/local/datenwerft/datenwerft/secrets.template /usr/local/datenwerft/datenwerft/secrets.py

3.  weitere Konfigurationsdatei `/usr/local/datenwerft/datenwerft/settings.py` 
    entsprechend anpassen

## Initialisierung

1.  in *PostgreSQL*-Datenbank (mit den Erweiterungen *PostGIS* und *uuid-ossp*) Schema `django` für die Anwendungsadministration und Schema `daten` für die Datenbasis anlegen
2.  virtuelle *Python*-Umgebung aktivieren:

        source /usr/local/datenwerft/venv/bin/activate

3.  Anwendungsadministration initialisieren:

        cd /usr/local/datenwerft/datenwerft
        python manage.py migrate

4.  Administrator initialisieren:

        python manage.py createsuperuser

5.  Dateien-Upload-Verzeichnis erstellen (und dessen Besitzer sowie Gruppe entsprechend des 
    genutzten HTTP-Servers anpassen – siehe unten):

        mkdir /usr/local/datenwerft/datenwerft/uploads
        chown -R wwwrun:www /usr/local/datenwerft/datenwerft/uploads

6.  Webseiten für Hilfe bauen:

        cd /usr/local/datenwerft/datenwerft/hilfe
        mkdir source/_static
        make html

7.  JavaScript-Module via *npm* installieren:

        npm install

8.  statische Dateien initialisieren:

        cd /usr/local/datenwerft/datenwerft
        python manage.py collectstatic -c

## Deployment (am Beispiel des [*Apache HTTP Servers*](https://httpd.apache.org/))

Wenn das Deployment mittels *Apache HTTP Server* realisiert werden soll, **muss** dessen Modul [*mod_wsgi*](https://modwsgi.readthedocs.io) (für *Python* v3.x) installiert sein, das ein Web Server Gateway Interface (WSGI) für das Hosting von *Python*-Anwendungen zur Verfügung stellt.

Konfigurationsdatei des *Apache HTTP Servers* öffnen und in etwa folgenden Inhalt einfügen (in diesem Beispiel nutzt die virtuelle *Python*-Umgebung einen *Python*-Interpreter der Version 3.6):

        RewriteCond         %{REQUEST_URI} ^/datenwerft$
        RewriteRule         ^.*$ %{REQUEST_URI}/ [R=301,L]
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

## Entwicklung

### Grundsätzliches

Der Python-Code orientiert sich an der Python-Styling-Konvention [*PEP8*](https://pep8.org/). Es empfiehlt sich ein Tool wie [*pycodestyle*](https://pypi.org/project/pycodestyle/) zur Überprüfung des Codes zu nutzen. Mit Hilfe von zum Beispiel [*autopep8*](https://pypi.org/project/autopep8/) können Python-Dateien auch im Nachhinein noch automatisch korrigiert werden, können dadurch allerdings auch unleserlich werden.

Die Python-Dokumentation wird mittels [Docstrings](https://en.wikipedia.org/wiki/Docstring) in [*reStructuredText*](https://docutils.sourceforge.io/rst.html) geschrieben.

Nützliche Tools für eine Entwicklungsumgebung, wie etwa *pycodestyle,* können zusätzlich via *pip* installiert werden:

        pip install -r /usr/local/datenwerft/datenwerft/requirements-dev.txt

### *PEP8*-Durchsetzung

Die Vorgaben von *PEP8* finden mit zwei Ausnahmen vollständig Anwendung:

1.  Zeilenlänge wird von 79 auf 99 erhöht
2.  Anzahl der Leerzeichen bei der Einrückung wird von 4 auf 2 reduziert (beinhaltet die 
    Einrückung und ergibt zudem eine Umbrucheinrückung von 4 statt 8)

Die entsprechende Konfigurationsdatei `setup.cfg` für *pycodestyle* ist bereits im 
Wurzelverzeichnis des Projekts angelegt.