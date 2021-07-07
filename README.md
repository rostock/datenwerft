# Datenerfassung

Web-Anwendung zur einfachen Erfassung von Geodaten, die auf [*Django*](https://www.djangoproject.com) aufsetzt

## Voraussetzungen

* [*Python*](https://www.python.org/) (v3.x)
* [*Virtualenv*](https://virtualenv.pypa.io/) (für *Python* v3.x)
* [*pip*](https://pip.pypa.io/) (für *Python* v3.x)
* [*PostgreSQL*](https://www.postgresql.org/) mit den Erweiterungen [*PostGIS*](https://postgis.net/) und [*uuid-ossp*](https://www.postgresql.org/docs/current/uuid-ossp.html)

## Installation

1.  neue virtuelle *Python*-Umgebung erstellen via *Virtualenv*, zum Beispiel:

        virtualenv /srv/www/htdocs/datenerfassung/virtualenv

1.  Projekt klonen:

        git clone https://github.com/rostock/datenerfassung /srv/www/htdocs/datenerfassung/datenerfassung

1.  virtuelle *Python*-Umgebung aktivieren:

        source /srv/www/htdocs/datenerfassung/virtualenv/bin/activate

1.  benötigte *Python*-Module (unter anderem [*Django*](https://www.djangoproject.com/)) installieren via *pip*:

        pip install -r /srv/www/htdocs/datenerfassung/datenerfassung/requirements.txt

## Konfiguration

1.  Konfigurationsdatei `/srv/www/htdocs/datenerfassung/datenerfassung/settings.py` entsprechend anpassen
1.  weitere Konfigurationsdatei erstellen auf Basis der entsprechenden Vorlage:

        cp /srv/www/htdocs/datenerfassung/datenerfassung/secrets.template /srv/www/htdocs/datenerfassung/datenerfassung/secrets.py

1.  weitere Konfigurationsdatei `/srv/www/htdocs/datenerfassung/datenerfassung/settings.py` entsprechend anpassen

## Initialisierung

1.  in *PostgreSQL*-Datenbank (mit den Erweiterungen *PostGIS* und *uuid-ossp*) Schema `django` für die Anwendungsadministration und Schema `daten` für die Datenbasis anlegen
1.  virtuelle *Python*-Umgebung aktivieren:

        source /srv/www/htdocs/datenerfassung/virtualenv/bin/activate

1.  Anwendungsadministration initialisieren:

        cd /srv/www/htdocs/datenerfassung/datenerfassung
        python manage.py migrate

1.  Administrator initialisieren:

        python manage.py createsuperuser

1.  Dateien-Upload-Verzeichnis erstellen (und dessen Besitzer sowie Gruppe entsprechend des genutzten HTTP-Servers anpassen – siehe unten):

        mkdir /srv/www/htdocs/datenerfassung/datenerfassung/uploads
        chown -R wwwrun:www /srv/www/htdocs/datenerfassung/datenerfassung/uploads

1.  Webseiten für Hilfe bauen:

        cd /srv/www/htdocs/datenerfassung/datenerfassung/hilfe
        mkdir source/_static
        make html

1.  statische Dateien initialisieren:

        cd /srv/www/htdocs/datenerfassung/datenerfassung
        python manage.py collectstatic -c

## Deployment (am Beispiel des [*Apache HTTP Servers*](https://httpd.apache.org/))

Wenn das Deployment mittels *Apache HTTP Server* realisiert werden soll, **muss** dessen Modul [*mod_wsgi*](https://modwsgi.readthedocs.io) (für *Python* v3.x) installiert sein, das ein Web Server Gateway Interface (WSGI) für das Hosting von *Python*-Anwendungen zur Verfügung stellt.

Konfigurationsdatei des *Apache HTTP Servers* öffnen und in etwa folgenden Inhalt einfügen (in diesem Beispiel nutzt die virtuelle *Python*-Umgebung einen *Python*-Interpreter der Version 3.6):
    
        Alias               /datenerfassung/static /srv/www/htdocs/datenerfassung/datenerfassung/static
        Alias               /datenerfassung/uploads /srv/www/htdocs/datenerfassung/datenerfassung/uploads
        WSGIDaemonProcess   datenerfassung processes=2 threads=128 python-path=/srv/www/htdocs/datenerfassung/datenerfassung:/srv/www/htdocs/datenerfassung/virtualenv/lib/python3.6/site-packages
        WSGIProcessGroup    datenerfassung
        WSGIScriptAlias     /datenerfassung /srv/www/htdocs/datenerfassung/datenerfassung/datenerfassung/wsgi.py process-group=datenerfassung

        <Directory /srv/www/htdocs/datenerfassung/datenerfassung/datenerfassung>
          <Files wsgi.py>
              Order deny,allow
              Require all granted
          </Files>
        </Directory>
        <Directory /srv/www/htdocs/datenerfassung/datenerfassung/static>
          Order deny,allow
          Require all granted
        </Directory>
        <Directory /srv/www/htdocs/datenerfassung/datenerfassung/uploads>
          Order deny,allow
          Require all granted
        </Directory>
