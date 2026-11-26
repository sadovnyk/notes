#!/usr/bin/env bash
BASE_URL="${BASE_URL:-http://localhost:8000}"

code=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/health")
status=$(curl -s "$BASE_URL/health" | jq -r ".status")

if [ "$code" = "200" ] && [ "$status" = "ok" ]; then
  echo "Service is healthy"
  exit 0
else
  echo "Service is unhealthy (code=$code, status=$status)"
  exit 1
fi
