#!/bin/sh
# vim:sw=4:ts=4:et

set -e

python3 -m venv .venv

npm install

source .venv/bin/activate

if [ ! -f datenwerft/secrets.py ]; then
  cp docker/container/web/secrets.py datenwerft/secrets.py
  chown $USER_ID:$GROUP_ID datenwerft/secrets.py
fi

# Solange die Konfiguration noch den Platzhalter der Vorlage enthaelt, einen SECRET_KEY erzeugen.
# Bewusst ohne Djangos get_random_secret_key(), da die Python-Module erst weiter unten installiert
# werden; Zeichensatz und Laenge entsprechen der Django-Implementierung.
if grep -q '^SECRET_KEY = None$' datenwerft/secrets.py; then
  python3 <<'EOF'
import secrets
from pathlib import Path

chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
key = ''.join(secrets.choice(chars) for _ in range(50))

path = Path('datenwerft/secrets.py')
path.write_text(
  path.read_text(encoding='utf-8').replace('SECRET_KEY = None', f'SECRET_KEY = {key!r}', 1),
  encoding='utf-8',
)
EOF
fi

pip install -r requirements.txt

python manage.py migrate --database=angebotsdb angebotsdb
python manage.py migrate --database=antragsmanagement antragsmanagement
python manage.py migrate --database=bemas bemas
python manage.py migrate --database=fmm fmm
python manage.py migrate --database=gdihrocodelists gdihrocodelists
python manage.py migrate --database=gdihrometadata gdihrometadata
python manage.py migrate
python manage.py angebotsdb_roles_permissions
python manage.py antragsmanagement_roles_permissions
python manage.py bemas_roles_permissions
python manage.py fmm_roles_permissions
python manage.py gdihrocodelists_roles_permissions
python manage.py gdihrometadata_roles_permissions
python manage.py pygeoapi_roles_permissions
python manage.py stadtbereichskatalog_roles_permissions
python manage.py loaddata --database=gdihrometadata gdihrometadata_initial-data.json

python manage.py createsuperuser --noinput || true
rm -Rf static
python manage.py collectstatic -c

exec "$@"
