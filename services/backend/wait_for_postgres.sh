#!/bin/bash

set -e

host="$1"
shift
cmd="$@"

# Timeout after 15 seconds
timeout=15
count=0

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
  count=$((count + 1))
  if [ $count -ge $timeout ]; then
    >&2 echo "Timeout reached, exiting"
    exit 1
  fi
done

>&2 echo "Postgres is up - executing command update "
eval $cmd
