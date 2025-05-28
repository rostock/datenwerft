#!/bin/sh
# vim:sw=4:ts=4:et

set -e

if [ ! -f datenwerft/secrets.py ]; then

  cp docker/container/web/secrets.py datenwerft/secrets.py
  chown $USER_ID:$GROUP_ID datenwerft/secrets.py
fi

python3 -m venv .venv

npm install

source .venv/bin/activate
pip install -r requirements.txt

python manage.py migrate --database=antragsmanagement antragsmanagement
python manage.py migrate --database=bemas bemas
python manage.py migrate --database=gdihrometadata gdihrometadata
python manage.py migrate
python manage.py antragsmanagement_roles_permissions
python manage.py bemas_roles_permissions
python manage.py gdihrometadata_roles_permissions
python manage.py loaddata --database=gdihrometadata gdihrometadata_initial-data.json

python manage.py createsuperuser --noinput || true
rm -fR static
python manage.py collectstatic -c

exec "$@"
