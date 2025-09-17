#!/bin/bash

createdb -Upostgres --encoding=UTF8 --owner=postgres datenwerft
createdb -Upostgres --encoding=UTF8 --owner=postgres antragsmanagement
createdb -Upostgres --encoding=UTF8 --owner=postgres bemas
createdb -Upostgres --encoding=UTF8 --owner=postgres datenmanagement
createdb -Upostgres --encoding=UTF8 --owner=postgres gdihrometadata

echo "CREATE EXTENSION postgis;" | psql -Upostgres -dantragsmanagement
echo "CREATE EXTENSION postgis;" | psql -Upostgres -dbemas
echo "CREATE EXTENSION postgis;" | psql -Upostgres -ddatenmanagement
