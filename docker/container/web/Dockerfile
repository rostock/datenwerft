FROM python:3.13-alpine

RUN apk --no-cache add nodejs npm gcc g++ openldap-dev gdal-dev geos-dev


COPY docker-entrypoint.sh /
ENTRYPOINT ["/docker-entrypoint.sh"]
