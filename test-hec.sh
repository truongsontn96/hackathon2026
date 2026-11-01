#!/bin/bash

# Test HEC connectivity and re-ingest data

echo "Testing Splunk HEC connectivity..."
echo ""

HEC_TOKEN="abcd1234-5678-90ef-ghij-klmnopqrstuv"
HEC_URL="https://localhost:8088/services/collector/event"

# Test HEC health endpoint
echo "[1/3] Checking HEC health endpoint..."
curl -k https://localhost:8088/services/collector/health 2>/dev/null
echo ""
echo ""

# Test HEC with sample event
echo "[2/3] Sending test event..."
curl -k -X POST "$HEC_URL" \
    -H "Authorization: Splunk $HEC_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"sourcetype":"test", "event":{"message":"test event"}}' 2>/dev/null
echo ""
echo ""

# Re-ingest all generated data files
echo "[3/3] Re-ingesting data files..."
DATA_DIR="./data"

if [ -d "$DATA_DIR" ]; then
    for file in "$DATA_DIR"/*.json; do
        if [ -f "$file" ]; then
            filename=$(basename "$file")
            echo "  Ingesting $filename..."

            count=0
            while IFS= read -r line; do
                curl -k -X POST "$HEC_URL" \
                    -H "Authorization: Splunk $HEC_TOKEN" \
                    -H "Content-Type: application/json" \
                    -d "{\"sourcetype\": \"threat_data\", \"event\": $line}" \
                    2>/dev/null && ((count++))
            done < "$file"

            echo "    ✓ Sent $count events from $filename"
        fi
    done
else
    echo "  No data directory found"
fi

echo ""
echo "Done! Check Splunk at http://localhost:8000"
echo "Search: index=* sourcetype=threat_data"
