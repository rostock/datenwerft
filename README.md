# Datenerfassung

Web-Anwendung zur einfachen Erfassung von Geodaten, die auf [*Django*](https://www.djangoproject.com) aufsetzt

## Voraussetzungen

* [*Python*](https://www.python.org) (v3.x)
* [*Virtualenv*](https://virtualenv.pypa.io) (for *Python* 3)
* [*pip*](http://pip.pypa.io) (for *Python* 3)
* [*PostgreSQL*](https://www.postgresql.org) mit den Erweiterungen [*PostGIS*](http://postgis.net) und [*uuid-ossp*](https://www.postgresql.org/docs/current/static/uuid-ossp.html)

## Installation

1.  neue virtuelle *Python*-Umgebung anlegen, zum Beispiel:

        virtualenv -p python3 /usr/local/django_datenerfassung/virtualenv

1.  Projekt klonen:

        git clone https://github.com/rostock/datenerfassung /usr/local/django_datenerfassung/datenerfassung

1.  virtuelle *Python*-Umgebung aktivieren:

        source /usr/local/django_datenerfassung/virtualenv/bin/activate

1.  benötigte *Python*-Module (unter anderem *Django*) installieren via *pip*, dem Paketverwaltungsprogramm für *Python*-Pakete:

        pip install -r /usr/local/django_datenerfassung/datenerfassung/requirements.txt

## Konfiguration

1.  Konfigurationsdatei `/usr/local/django_datenerfassung/datenerfassung/settings.py` bearbeiten
1.  weitere Konfigurationsdatei erstellen auf Basis der entsprechenden Vorlage:

        cp /usr/local/django_datenerfassung/datenerfassung/secrets.template /usr/local/django_datenerfassung/datenerfassung/secrets.py

1.  weitere Konfigurationsdatei `/usr/local/django_datenerfassung/datenerfassung/settings.py` bearbeiten

## Initialisierung

1.  in um *PostGIS* erweiterter *PostgreSQL*-Datenbank Schema `django` für die Anwendungsadministration und Schema `daten` für die Daten anlegen
1.  virtuelle *Python*-Umgebung aktivieren:

        source /usr/local/django_datenerfassung/virtualenv/bin/activate

1.  Anwendungsadministration initialisieren:

        cd /usr/local/django_datenerfassung/datenerfassung
        python manage.py migrate

1.  Administrator initialisieren:

        python manage.py createsuperuser

1.  Dateien-Upload-Verzeichnis erstellen (und dessen Besitzer sowie Gruppe entsprechend des genutzten HTTP-Servers anpassen – siehe unten):

        mkdir /usr/local/django_datenerfassung/datenerfassung/uploads
        chown -R wwwrun:www /usr/local/django_datenerfassung/datenerfassung/uploads

1.  Hilfe initialisieren:

        cd /usr/local/django_datenerfassung/datenerfassung/hilfe
        make html

1.  statische Dateien initialisieren:

        cd /usr/local/django_datenerfassung/datenerfassung
        python manage.py collectstatic -c

## Deployment (am Beispiel des [*Apache HTTP Servers*](https://httpd.apache.org))

Wenn das Deployment mittels *Apache HTTP Server* realisiert werden soll, **muss** dessen Modul [*mod_wsgi*](https://modwsgi.readthedocs.io) installiert sein, das ein Web Server Gateway Interface (WSGI) für das Hosting von *Python*-Anwendungen zur Verfügung stellt.

Konfigurationsdatei des *Apache HTTP Servers* öffnen und in etwa folgenden Inhalt einfügen (in diesem Beispiel nutzt die virtuelle *Python*-Umgebung einen *Python*-Interpreter der Version 3.6):
    
        Alias               /datenerfassung/static /usr/local/django_datenerfassung/datenerfassung/static
        Alias               /datenerfassung/uploads /usr/local/django_datenerfassung/datenerfassung/uploads
        WSGIDaemonProcess   datenerfassung processes=2 threads=128 python-path=/usr/local/django_datenerfassung/datenerfassung:/usr/local/django_datenerfassung/virtualenv/lib/python3.7/site-packages
        WSGIProcessGroup    datenerfassung
        WSGIScriptAlias     /datenerfassung /usr/local/django_datenerfassung/datenerfassung/datenerfassung/wsgi.py process-group=datenerfassung

        <Directory /usr/local/django_datenerfassung/datenerfassung/datenerfassung>
          <Files wsgi.py>
              Order deny,allow
              Require all granted
          </Files>
        </Directory>
        <Directory /usr/local/django_datenerfassung/datenerfassung/static>
          Order deny,allow
          Require all granted
        </Directory>
        <Directory /usr/local/django_datenerfassung/datenerfassung/uploads>
          Order deny,allow
          Require all granted
        </Directory>
