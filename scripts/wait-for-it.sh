#!/usr/bin/env bash
SCRIPT_DIR="$(dirname "$0")"
MAX_ATTEMPTS="${MAX_ATTEMPTS:-30}"

for i in $(seq 1 "$MAX_ATTEMPTS"); do
  if bash "$SCRIPT_DIR/healthcheck.sh" > /dev/null; then
    echo "Service is up (attempt $i)"
    exit 0
  fi
  echo " Waiting... ($i/$MAX_ATTEMPTS)"
  sleep 1
done

echo "Service did not start in time"
exit 1
