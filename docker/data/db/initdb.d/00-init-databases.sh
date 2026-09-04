#!/bin/bash

createdb -Upostgres --encoding=UTF8 --owner=postgres datenwerft
createdb -Upostgres --encoding=UTF8 --owner=postgres angebotsdb
createdb -Upostgres --encoding=UTF8 --owner=postgres antragsmanagement
createdb -Upostgres --encoding=UTF8 --owner=postgres bemas
createdb -Upostgres --encoding=UTF8 --owner=postgres datenmanagement
createdb -Upostgres --encoding=UTF8 --owner=postgres fmm
createdb -Upostgres --encoding=UTF8 --owner=postgres gdihrocodelists
createdb -Upostgres --encoding=UTF8 --owner=postgres gdihrometadata
createdb -Upostgres --encoding=UTF8 --owner=postgres stadtbereichskatalog

echo "CREATE EXTENSION postgis;" | psql -Upostgres -dangebotsdb
echo "CREATE EXTENSION postgis;" | psql -Upostgres -dantragsmanagement
echo "CREATE EXTENSION postgis;" | psql -Upostgres -dbemas
echo "CREATE EXTENSION postgis;" | psql -Upostgres -ddatenmanagement
echo "CREATE EXTENSION postgis;" | psql -Upostgres -dfmm
