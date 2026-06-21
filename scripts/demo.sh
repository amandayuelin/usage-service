#!/usr/bin/env bash
set -euo pipefail

# Demo script for Usage Events service
# Usage: ./scripts/demo.sh

BASE_URL=${1:-https://amanda-usage-api-hguu4.ondigitalocean.app}

echo "Checking health..."
curl -sS -w "\nHTTP_STATUS:%{http_code}\n" "$BASE_URL/health"

echo "\nPosting smoke event..."
curl -sS -X POST "$BASE_URL/events" \
  -H "Content-Type: application/json" \
  -d '{"event_id":"smoke-1","customer_id":"demo","resource_id":"r1","resource_type":"vm","usage":1.5,"usage_unit":"vcpu-hour","timestamp":"2026-06-20T00:00:00Z"}' | jq || true

echo "\nListing events for demo customer..."
curl -sS "$BASE_URL/events?customer_id=demo" | jq || true

echo "\nDone. If you have doctl configured you can stream logs with:" 
echo "doctl apps logs $(doctl apps list --format ID --no-header | head -n1) usage-service --type run -f"
