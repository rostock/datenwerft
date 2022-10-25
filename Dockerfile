FROM python:3.10-buster

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        # python-ldap
        build-essential python3-dev libmemcached-dev libldap2-dev libsasl2-dev libzbar-dev ldap-utils tox lcov valgrind \
        # gis
        binutils libproj-dev gdal-bin \
        npm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set workdir
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

COPY . .
EXPOSE 8000

RUN npm install

#RUN ./manage.py collectstatic --noinput && \
#    gzip --keep --best --force --recursive /app/static/
    # chown -R app:app /app/media/ /app/static/CACHE && \
    # chmod -R go+rw /app/media/ /app/static/CACHE

# Reduce default permissions
# USER app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
