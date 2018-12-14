# Datenerfassung

Web-Anwendung zur einfachen Erfassung von Geodaten, die auf [*Django*](https://www.djangoproject.com) aufsetzt

## Voraussetzungen

*   [*Python*](https://www.python.org)
*   [*Virtualenv*](https://virtualenv.pypa.io)
*   [*pip*](http://pip.pypa.io)
*   [*PostgreSQL*](https://www.postgresql.org) mit den Erweiterungen [*PostGIS*](http://postgis.net) und [*uuid-ossp*](https://www.postgresql.org/docs/current/static/uuid-ossp.html)

## Installation

1.  neue virtuelle *Python*-Umgebung anlegen, zum Beispiel:

        virtualenv /usr/local/datenerfassung/virtualenv

1.  Projekt klonen:

        git clone https://github.com/rostock/datenerfassung /usr/local/datenerfassung/datenerfassung

1.  virtuelle *Python*-Umgebung aktivieren:

        source /usr/local/datenerfassung/virtualenv/bin/activate

1.  benötigte *Python*-Module (unter anderem *Django*) installieren via *pip*, dem Paketverwaltungsprogramm für *Python*-Pakete:

        pip install -r requirements.txt

## Konfiguration

1.  Konfigurationsdatei /usr/local/datenerfassung/datenerfassung/settings.py bearbeiten
1.  weitere Konfigurationsdatei erstellen auf Basis der entsprechenden Vorlage:

        cp /usr/local/datenerfassung/datenerfassung/secrets.template /usr/local/datenerfassung/datenerfassung/secrets.py

1.  weitere Konfigurationsdatei /usr/local/datenerfassung/datenerfassung/settings.py bearbeiten

## Initialisierung

1.  in um *PostGIS* erweiterter *PostgreSQL*-Datenbank Schema `django` für die Anwendungsadministration und Schema `daten` für die Daten anlegen
1.  virtuelle *Python*-Umgebung aktivieren:

        source /usr/local/datenerfassung/virtualenv/bin/activate

1.  Anwendungsadministration initialisieren:

        cd /usr/local/datenerfassung/datenerfassung
        python manage.py migrate

1.  Administrator initialisieren:

        python manage.py createsuperuser

1.  Dateien-Upload-Verzeichnis erstellen (und dessen Besitzer sowie Gruppe entsprechend des genutzten HTTP-Servers anpassen – siehe unten):

        mkdir /srv/www/htdocs/datenerfassung_uploads
        chown -R wwwrun:www /srv/www/htdocs/datenerfassung_uploads

1.  Hilfe initialisieren:

        cd /usr/local/django_datenerfassung/datenerfassung/hilfe
        make html

1.  statische Dateien initialisieren:

        cd /usr/local/django_datenerfassung/datenerfassung
        python manage.py collectstatic

## Deployment (am Beispiel des [*Apache HTTP Servers*](https://httpd.apache.org))

Wenn das Deployment mittels *Apache HTTP Server* realisiert werden soll, **muss** dessen Modul [*mod_wsgi*](https://modwsgi.readthedocs.io) installiert sein, das ein Web Server Gateway Interface (WSGI) für das Hosting von *Python*-Anwendungen zur Verfügung stellt.

Konfigurationsdatei des *Apache HTTP Servers* öffnen und in etwa folgenden Inhalt einfügen:
    
        RewriteRule         ^/datenerfassung_static/?(hilfe)$ /datenerfassung_static/$1/ [R,NC,L]
        Alias               /datenerfassung_static  /usr/local/datenerfassung/datenerfassung/static
        Alias               /datenerfassung_uploads /srv/www/htdocs/datenerfassung_uploads
        WSGIDaemonProcess   datenerfassung processes=4 threads=128 python-path=/usr/local/datenerfassung/datenerfassung:/usr/local/datenerfassung/virtualenv/lib/python2.7/site-packages
        WSGIProcessGroup    datenerfassung
        WSGIScriptAlias     /datenerfassung /usr/local/datenerfassung/datenerfassung/datenerfassung/wsgi.py process-group=datenerfassung

        <Directory /usr/local/datenerfassung/datenerfassung/datenerfassung>
            <Files wsgi.py>
                Order deny,allow
                Require all granted
            </Files>
        </Directory>
        <Directory /usr/local/datenerfassung/datenerfassung/static>
            Order deny,allow
            Require all granted
        </Directory>
