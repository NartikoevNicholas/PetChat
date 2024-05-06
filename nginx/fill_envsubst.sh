#!/bin/bash
# shellcheck disable=SC2164,SC2016

function fill_env() {
  cd "$1"
  for file in *.conf.tmp
  do
    envsubst "$2" <"$file"> "$3${file%%.*}".conf
  done
}

fill_env "/etc/nginx_tmp/conf.d/" '${SERVICE_DOMAIN} ${APPLICATION_DOMAIN}' "/etc/nginx/conf.d/"
fill_env "/etc/nginx_tmp/" '${CERT_NAME}' "/etc/nginx/"

nginx -g "daemon off;"
