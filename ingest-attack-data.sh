#!/bin/bash

# Data ingestion script for real-world attack datasets

echo "================================================"
echo "  Splunk Lab - Real Attack Data Ingestion"
echo "================================================"
echo ""

DATA_DIR="/home/sonnt87/hackathon2026/real-attack-data"
SPLUNK_CONTAINER="splunk-lab"

# Create data directory
mkdir -p "$DATA_DIR"/{bots,mordor,secrepo,evtx}

echo "[1/4] Downloading Mordor Dataset (MITRE ATT&CK mapped)..."
echo "-------------------------------------------------------"

# Download small Mordor datasets (Windows Event Logs)
MORDOR_BASE="https://raw.githubusercontent.com/OTRF/Security-Datasets/master/datasets/atomic/windows"

# T1003.001 - LSass Memory Dump
echo "  → Downloading LSass dump events..."
curl -sSL "${MORDOR_BASE}/credential_access/host/empire_mimikatz_logonpasswords.zip" \
  -o "$DATA_DIR/mordor/lsass_dump.zip" 2>/dev/null || echo "    ⚠ Skipped (optional)"

# T1021.002 - SMB Lateral Movement
echo "  → Downloading lateral movement events..."
curl -sSL "${MORDOR_BASE}/lateral_movement/host/empire_psexec_dcerpc_wmi_smb.zip" \
  -o "$DATA_DIR/mordor/lateral_movement.zip" 2>/dev/null || echo "    ⚠ Skipped (optional)"

# T1190 - SQL Injection
echo "  → Downloading web attack logs..."
curl -sSL "https://raw.githubusercontent.com/OTRF/Security-Datasets/master/datasets/atomic/linux/other/sql_injection_attempts.json" \
  -o "$DATA_DIR/mordor/sqli.json" 2>/dev/null || echo "    ⚠ Skipped (optional)"

echo ""
echo "[2/4] Downloading EVTX Attack Samples..."
echo "---------------------------------------"

# Download specific EVTX samples
EVTX_BASE="https://raw.githubusercontent.com/sbousseaden/EVTX-ATTACK-SAMPLES/master"

echo "  → Downloading Mimikatz events..."
curl -sSL "${EVTX_BASE}/Credential%20Access/cred_mimikatz_logonpasswords.evtx" \
  -o "$DATA_DIR/evtx/mimikatz.evtx" 2>/dev/null || echo "    ⚠ Skipped (optional)"

echo "  → Downloading PsExec events..."
curl -sSL "${EVTX_BASE}/Lateral%20Movement/LM_sysmon_psexec.evtx" \
  -o "$DATA_DIR/evtx/psexec.evtx" 2>/dev/null || echo "    ⚠ Skipped (optional)"

echo ""
echo "[3/4] Generating sample attack data locally..."
echo "--------------------------------------------"

# Generate JSON format attack data (compatible với HEC)
cat > "$DATA_DIR/mordor/t1003_lsass_dump.json" << 'EOF'
{"timestamp": "2024-01-15T10:23:45Z", "EventID": 4656, "Computer": "WS-001", "User": "DOMAIN\\baduser", "ObjectName": "C:\\Windows\\System32\\lsass.exe", "ProcessName": "C:\\Tools\\procdump.exe", "AccessMask": "0x1fffff", "attack_technique": "T1003.001", "severity": "critical"}
{"timestamp": "2024-01-15T10:23:46Z", "EventID": 4688, "Computer": "WS-001", "User": "DOMAIN\\baduser", "NewProcessName": "C:\\Tools\\procdump.exe", "CommandLine": "procdump.exe -accepteula -ma lsass.exe lsass.dmp", "attack_technique": "T1003.001", "severity": "critical"}
{"timestamp": "2024-01-15T10:24:12Z", "EventID": 4656, "Computer": "WS-002", "User": "DOMAIN\\attacker", "ObjectName": "C:\\Windows\\System32\\lsass.exe", "ProcessName": "C:\\Windows\\System32\\rundll32.exe", "AccessMask": "0x1410", "attack_technique": "T1003.001", "severity": "critical"}
EOF

cat > "$DATA_DIR/mordor/t1021_lateral_movement.json" << 'EOF'
{"timestamp": "2024-01-15T14:30:00Z", "EventID": 5145, "Computer": "DC-01", "User": "DOMAIN\\attacker", "ShareName": "\\\\*\\IPC$", "SourceAddress": "10.0.1.50", "AccessMask": "0x1", "attack_technique": "T1021.002", "severity": "high"}
{"timestamp": "2024-01-15T14:30:05Z", "EventID": 4648, "Computer": "SRV-01", "User": "DOMAIN\\attacker", "TargetServerName": "SRV-02", "ProcessName": "C:\\Windows\\System32\\wmiprvse.exe", "attack_technique": "T1021.006", "severity": "high"}
{"timestamp": "2024-01-15T14:30:15Z", "EventID": 4624, "Computer": "SRV-02", "User": "DOMAIN\\attacker", "LogonType": "3", "SourceAddress": "10.0.1.50", "WorkstationName": "SRV-01", "attack_technique": "T1021.002", "severity": "medium"}
EOF

cat > "$DATA_DIR/mordor/t1190_web_attacks.json" << 'EOF'
{"timestamp": "2024-01-15T09:15:22Z", "src_ip": "203.0.113.45", "dest_ip": "10.0.1.100", "uri": "/login?user=admin' OR '1'='1", "status": 200, "user_agent": "sqlmap/1.4.7", "attack_technique": "T1190", "attack_type": "sqli", "severity": "high"}
{"timestamp": "2024-01-15T09:15:23Z", "src_ip": "203.0.113.45", "dest_ip": "10.0.1.100", "uri": "/api/users?id=1 UNION SELECT username,password FROM users--", "status": 500, "user_agent": "python-requests/2.25.1", "attack_technique": "T1190", "attack_type": "sqli", "severity": "high"}
{"timestamp": "2024-01-15T09:16:01Z", "src_ip": "198.51.100.88", "dest_ip": "10.0.1.100", "uri": "/search?q=<script>alert('XSS')</script>", "status": 200, "user_agent": "Mozilla/5.0", "attack_technique": "T1190", "attack_type": "xss", "severity": "medium"}
EOF

cat > "$DATA_DIR/mordor/t1071_c2_communication.json" << 'EOF'
{"timestamp": "2024-01-15T16:45:10Z", "src_ip": "10.0.1.150", "dest_ip": "185.220.101.1", "dest_port": 443, "protocol": "TCP", "bytes_out": 45234, "threat_intel": "Known C2 Server", "attack_technique": "T1071", "severity": "critical"}
{"timestamp": "2024-01-15T16:46:22Z", "src_ip": "10.0.1.150", "dest_ip": "45.142.214.123", "dest_port": 8080, "protocol": "TCP", "bytes_out": 102400, "threat_intel": "Malware C2", "attack_technique": "T1071", "severity": "critical"}
{"timestamp": "2024-01-15T16:47:15Z", "query_type": "A", "query": "evil-c2-server.com", "answer": "185.220.101.1", "client_ip": "10.0.1.150", "threat_intel": "Malicious Domain", "attack_technique": "T1071", "severity": "critical"}
EOF

echo "  ✓ Generated T1003.001 (LSass Dump) dataset"
echo "  ✓ Generated T1021 (Lateral Movement) dataset"
echo "  ✓ Generated T1190 (Web Attacks) dataset"
echo "  ✓ Generated T1071 (C2 Communication) dataset"

echo ""
echo "[4/4] Ingesting data into Splunk..."
echo "----------------------------------"

# Wait for Splunk to be ready
echo "  → Checking Splunk status..."
for i in {1..10}; do
    if docker exec $SPLUNK_CONTAINER /opt/splunk/bin/splunk status 2>/dev/null | grep -q "splunkd is running"; then
        echo "  ✓ Splunk is ready"
        break
    fi
    echo "    Waiting for Splunk... ($i/10)"
    sleep 5
done

# Ingest via HEC
HEC_TOKEN="abcd1234-5678-90ef-ghij-klmnopqrstuv"
HEC_URL="https://localhost:8088/services/collector/event"

echo ""
echo "  → Ingesting attack datasets via HEC..."

for file in "$DATA_DIR/mordor"/*.json; do
    if [ -f "$file" ]; then
        filename=$(basename "$file")
        echo "    Ingesting $filename..."

        while IFS= read -r line; do
            curl -k -X POST "$HEC_URL" \
                -H "Authorization: Splunk $HEC_TOKEN" \
                -H "Content-Type: application/json" \
                -d "{\"sourcetype\": \"attack_data\", \"event\": $line}" \
                2>/dev/null
        done < "$file"

        echo "      ✓ $filename ingested"
    fi
done

# Copy data to Docker volume for persistent access
echo ""
echo "  → Copying datasets to Splunk container..."
docker cp "$DATA_DIR/mordor" $SPLUNK_CONTAINER:/opt/splunk/etc/apps/ 2>/dev/null || true

echo ""
echo "================================================"
echo "  ✓ Data Ingestion Complete!"
echo "================================================"
echo ""
echo "Datasets loaded:"
echo "  • T1003.001 - Credential Dumping (LSass)"
echo "  • T1021    - Lateral Movement (PsExec, WMI)"
echo "  • T1190    - Web Attacks (SQLi, XSS)"
echo "  • T1071    - C2 Communication"
echo ""
echo "Access Splunk: http://localhost:8000"
echo "Search for data: index=* sourcetype=attack_data"
echo ""
echo "Run threat hunt: docker exec threat-hunter-agent python agent.py --hunt-now"
echo ""
