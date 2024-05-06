#!/bin/bash

if [ ! -f "/usr/share/elasticsearch/config/certs/ca.zip" ]; then
  bin/elasticsearch-certutil ca --silent --pem -out config/certs/ca.zip
  unzip config/certs/ca.zip -d config/certs

  bin/elasticsearch-certutil cert \
                              --silent \
                              --pem \
                              --ca-cert config/certs/ca/ca.crt \
                              --ca-key config/certs/ca/ca.key \
                              -out /usr/share/elasticsearch/config/certs/certs.zip \
                              -in /instances.yml
  unzip config/certs/certs.zip -d config/certs
fi
