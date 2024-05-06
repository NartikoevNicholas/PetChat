#!/bin/bash
set -e

umask 0002

if [[ "$1" == "eswrapper" || $(basename "$1") == "elasticsearch" ]]; then
  set -- "${@:2}"
else
  # Run whatever command the user wanted
  "$@"
  set -- "${@:2}"
fi

source /usr/share/elasticsearch/bin/elasticsearch-env-from-file

if [[ -f bin/elasticsearch-users ]]; then
  if [[ -n "$ELASTIC_PASSWORD" ]]; then
    [[ -f /usr/share/elasticsearch/config/elasticsearch.keystore ]] || (elasticsearch-keystore create)
    if ! (elasticsearch-keystore has-passwd --silent) ; then
      # keystore is unencrypted
      if ! (elasticsearch-keystore list | grep -q '^bootstrap.password$'); then
        (echo "$ELASTIC_PASSWORD" | elasticsearch-keystore add -x 'bootstrap.password')
      fi
    else
      # keystore requires password
      if ! (echo "$KEYSTORE_PASSWORD" \
          | elasticsearch-keystore list | grep -q '^bootstrap.password$') ; then
        COMMANDS="$(printf "%s\n%s" "$KEYSTORE_PASSWORD" "$ELASTIC_PASSWORD")"
        (echo "$COMMANDS" | elasticsearch-keystore add -x 'bootstrap.password')
      fi
    fi
  fi
fi

if [[ -n "$ES_LOG_STYLE" ]]; then
  case "$ES_LOG_STYLE" in
    console)
      # This is the default. Nothing to do.
      ;;
    file)
      cp -f /usr/share/elasticsearch/config/log4j2.file.properties /usr/share/elasticsearch/config/log4j2.properties
      ;;
    *)
      echo "ERROR: ES_LOG_STYLE set to [$ES_LOG_STYLE]. Expected [console] or [file]" >&2
      exit 1 ;;
  esac
fi

if [[ -n "$ENROLLMENT_TOKEN" ]]; then
  POSITIONAL_PARAMETERS="--enrollment-token $ENROLLMENT_TOKEN"
else
  POSITIONAL_PARAMETERS=""
fi

exec /usr/share/elasticsearch/bin/elasticsearch "$@" $POSITIONAL_PARAMETERS <<<"$KEYSTORE_PASSWORD"