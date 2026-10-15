#!/usr/bin/env bash
# Generates traffic so Grafana panels and the HPA have something to show.
# usage: scripts/load-test.sh http://localhost:8000 [seconds]
set -euo pipefail
BASE="${1:-http://localhost:8000}"
DURATION="${2:-60}"
end=$((SECONDS + DURATION))
while [ $SECONDS -lt $end ]; do
  curl -s -o /dev/null "$BASE/api/tickets" &
  curl -s -o /dev/null "$BASE/api/tickets/stats" &
  curl -s -o /dev/null -X POST "$BASE/api/tickets" -H 'Content-Type: application/json' \
    -d '{"title":"load test","requester":"load@test"}' &
  curl -s -o /dev/null "$BASE/api/tickets/999999" &   # 404s so the error panel has data
  wait
done
echo "done"
