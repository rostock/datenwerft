#!/bin/bash

psql -Upostgres -ddatenmanagement -f /opt/datenmanagement/schema.sql
