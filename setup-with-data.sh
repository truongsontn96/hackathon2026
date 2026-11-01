#!/bin/bash

# Enhanced setup with real attack data

echo "========================================="
echo "Hackathon 2026 - Enhanced Splunk Lab"
echo "With Real-World Attack Datasets"
echo "========================================="
echo ""

# Run original setup
./setup.sh

echo ""
echo "[BONUS] Downloading real attack datasets..."
echo "========================================="
echo ""

# Run data ingestion
./ingest-attack-data.sh

echo ""
echo "========================================="
echo "✓ Enhanced Setup Complete!"
echo "========================================="
echo ""
echo "Real-world datasets loaded:"
echo "  • MITRE ATT&CK mapped scenarios"
echo "  • Mordor credential dumping logs"
echo "  • Lateral movement events"
echo "  • Web attack samples"
echo "  • C2 communication patterns"
echo ""
echo "Start hunting: docker exec threat-hunter-agent python agent.py --hunt-now"
echo ""
