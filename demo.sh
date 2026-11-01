#!/bin/bash

# Quick demo script - shows the system in action

echo "================================================"
echo "  Splunk Lab Demo - Automated Threat Hunting"
echo "================================================"
echo ""

# Check if services are running
if ! docker ps | grep -q splunk-lab; then
    echo "❌ Splunk lab is not running!"
    echo ""
    echo "Start it first with: ./start.sh"
    exit 1
fi

echo "[1/5] Checking Splunk status..."
docker exec splunk-lab /opt/splunk/bin/splunk status 2>/dev/null || echo "⏳ Splunk still starting..."
echo ""

echo "[2/5] Checking data generator..."
docker logs --tail 10 threat-data-generator
echo ""

echo "[3/5] Ingesting real attack datasets..."
./ingest-attack-data.sh
echo ""

echo "[4/5] Triggering threat hunt..."
docker exec threat-hunter-agent python agent.py --hunt-now
echo ""

echo "[5/5] Viewing results..."
echo ""
echo "Reports generated:"
ls -lh threat-hunter/reports/ 2>/dev/null || echo "No reports yet"
echo ""

echo "================================================"
echo "  Demo Complete!"
echo "================================================"
echo ""
echo "View in Splunk Web:"
echo "  URL: http://localhost:8000"
echo "  Login: admin / Admin@123456"
echo ""
echo "Search for threat data:"
echo "  index=* sourcetype=attack_data | stats count by attack_technique"
echo ""
echo "View latest report:"
LATEST_REPORT=$(ls -t threat-hunter/reports/*.html 2>/dev/null | head -1)
if [ -n "$LATEST_REPORT" ]; then
    echo "  file://$PWD/$LATEST_REPORT"
else
    echo "  (No reports generated yet)"
fi
echo ""
