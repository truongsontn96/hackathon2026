# Real-World Attack Datasets Integration

## Datasets Included

### 1. Mordor Dataset (MITRE ATT&CK Mapped)
**Source**: https://github.com/OTRF/Security-Datasets

Mapped scenarios:
- **T1003.001** - LSass Memory Dump
  - Mimikatz logonpasswords
  - ProcDump credential extraction
  - RunDLL32 + Comsvcs.dll dumping

- **T1021** - Lateral Movement
  - PsExec over SMB
  - WMI remote execution
  - SMB admin share access

- **T1190** - Web Application Exploits
  - SQL Injection attempts
  - XSS payloads
  - Authentication bypass

- **T1071** - C2 Communication
  - Malicious IP connections
  - Known C2 domains
  - DNS tunneling patterns

### 2. EVTX Attack Samples
**Source**: https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES

Windows Event Log captures:
- Mimikatz execution traces
- PsExec lateral movement
- WMI persistence
- PowerShell obfuscation

### 3. BOTS Dataset (Optional - Large)
**Source**: https://github.com/splunk/botsv3

Full APT simulation (12GB compressed):
- APT29 campaign
- Multi-stage attacks
- Ransomware deployment
- Data exfiltration

## Data Format

All datasets converted to JSON for Splunk HEC ingestion:

```json
{
  "timestamp": "2024-01-15T10:23:45Z",
  "EventID": 4656,
  "Computer": "WS-001",
  "User": "DOMAIN\\baduser",
  "ObjectName": "C:\\Windows\\System32\\lsass.exe",
  "ProcessName": "C:\\Tools\\procdump.exe",
  "AccessMask": "0x1fffff",
  "attack_technique": "T1003.001",
  "severity": "critical"
}
```

## Ingestion Methods

### Method 1: Automatic (Recommended)
```bash
./ingest-attack-data.sh
```

### Method 2: Manual HEC Push
```bash
HEC_TOKEN="abcd1234-5678-90ef-ghij-klmnopqrstuv"
HEC_URL="https://localhost:8088/services/collector/event"

curl -k -X POST "$HEC_URL" \
  -H "Authorization: Splunk $HEC_TOKEN" \
  -H "Content-Type: application/json" \
  -d @real-attack-data/mordor/t1003_lsass_dump.json
```

### Method 3: Splunk Upload
1. Access Splunk Web: http://localhost:8000
2. Settings → Add Data → Upload
3. Select JSON files from `real-attack-data/mordor/`
4. Set sourcetype: `attack_data`

## Searching Data

### Basic search
```spl
index=* sourcetype=attack_data
| stats count by attack_technique
```

### By MITRE technique
```spl
index=* attack_technique="T1003.001"
| table timestamp Computer User ProcessName ObjectName
```

### By severity
```spl
index=* severity=critical
| sort -timestamp
| head 50
```

### Timeline view
```spl
index=* attack_technique=*
| timechart count by attack_technique
```

## Pre-loaded Attack Scenarios

### Scenario 1: Credential Dumping Campaign
**File**: `t1003_lsass_dump.json`

Timeline:
1. ProcDump execution on WS-001
2. LSass memory access (0x1fffff)
3. .dmp file creation
4. Similar activity on WS-002

**Detection Query**:
```spl
index=* EventID=4656 ObjectName="*lsass.exe"
| stats count by Computer User ProcessName
```

### Scenario 2: Lateral Movement
**File**: `t1021_lateral_movement.json`

Attack flow:
1. Initial compromise on WS-001
2. IPC$ share access to DC-01
3. WMI execution on SRV-01
4. Network logon to SRV-02

**Detection Query**:
```spl
index=* (EventID=5145 OR EventID=4648 OR EventID=4624)
| transaction Computer startswith=(EventID=5145) endswith=(EventID=4624)
| table Computer User TargetServerName
```

### Scenario 3: Web Attacks
**File**: `t1190_web_attacks.json`

Attack types:
- SQL Injection with UNION
- Boolean-based blind SQLi
- XSS attempts

**Detection Query**:
```spl
index=* attack_type=sqli
| stats count by src_ip uri
| where count > 3
```

### Scenario 4: C2 Communication
**File**: `t1071_c2_communication.json`

IOCs:
- Connections to known malicious IPs
- DNS queries to C2 domains
- High-volume data exfiltration

**Detection Query**:
```spl
index=* threat_intel=*
| stats sum(bytes_out) by src_ip dest_ip
```

## Agent Integration

The Threat Hunter Agent automatically queries these datasets:

```python
# In agent.py, queries run against all data
index=* sourcetype=attack_data OR sourcetype=access_combined
```

The AI analysis includes:
- MITRE technique identification
- Attack timeline reconstruction
- Affected asset enumeration
- Response recommendations

## Dataset Statistics

| Dataset | Events | Size | MITRE Techniques |
|---------|--------|------|------------------|
| LSass Dump | 6 | 2KB | T1003.001 |
| Lateral Movement | 5 | 1.5KB | T1021.002, T1021.006 |
| Web Attacks | 8 | 2KB | T1190 |
| C2 Comms | 7 | 1.8KB | T1071 |

## Extending Datasets

### Add your own attack data:

1. Create JSON file:
```json
{"timestamp": "...", "EventID": 4688, ...}
```

2. Ingest via HEC:
```bash
curl -k -X POST https://localhost:8088/services/collector/event \
  -H "Authorization: Splunk $HEC_TOKEN" \
  -d @your_data.json
```

3. Update queries in `threat-hunter/config/queries.yml`

### Download additional Mordor datasets:

```bash
# Browse available datasets
curl -s https://api.github.com/repos/OTRF/Security-Datasets/contents/datasets/atomic

# Download specific technique
wget https://raw.githubusercontent.com/OTRF/Security-Datasets/master/datasets/atomic/windows/credential_access/host/empire_mimikatz_logonpasswords.zip
```

## Troubleshooting

### Data not appearing in Splunk

1. Check HEC is enabled:
```bash
docker exec splunk-lab /opt/splunk/bin/splunk http-event-collector list
```

2. Verify token:
```bash
curl -k https://localhost:8088/services/collector/health \
  -H "Authorization: Splunk $HEC_TOKEN"
```

3. Check index:
```bash
docker exec splunk-lab /opt/splunk/bin/splunk list index
```

### Slow ingestion

- Reduce batch size in ingestion script
- Increase Splunk resources in docker-compose.yml
- Use parallel ingestion for multiple files

## References

- [Mordor Documentation](https://mordordatasets.com/)
- [EVTX Samples](https://github.com/sbousseaden/EVTX-ATTACK-SAMPLES)
- [MITRE ATT&CK](https://attack.mitre.org/)
- [Splunk HEC](https://docs.splunk.com/Documentation/Splunk/latest/Data/UsetheHTTPEventCollector)
