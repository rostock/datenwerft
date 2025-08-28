FROM postgres:17-bookworm

RUN apt update && \
    apt install -y postgresql-17-postgis-3 && \
    rm -rf /var/lib/apt/lists/* \
