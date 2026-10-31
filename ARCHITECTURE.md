# Architecture Documentation

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                    │
│                                                               │
│  ┌──────────────────┐         ┌──────────────────┐          │
│  │  Data Generator  │────────▶│   Splunk SIEM    │          │
│  │                  │  HEC    │                  │          │
│  │  - SQL Injection │  8088   │  - Index logs    │          │
│  │  - LDAP Inject   │         │  - Store data    │          │
│  │  - LSass Dump    │         │  - Web UI :8000  │          │
│  │  - IOCs          │         │  - API :8089     │          │
│  │  - Lateral Move  │         │                  │          │
│  └──────────────────┘         └──────────┬───────┘          │
│                                           │                   │
│                                           │ Query             │
│                                           │                   │
│  ┌──────────────────┐         ┌──────────▼───────┐          │
│  │  Anthropic API   │◀────────│ Threat Hunter    │          │
│  │  (Claude)        │  API    │     Agent        │          │
│  │                  │         │                  │          │
│  │  - AI Analysis   │         │  - Run queries   │          │
│  │  - Context       │         │  - AI analysis   │          │
│  │  - Recommend     │         │  - Generate      │          │
│  └──────────────────┘         │    reports       │          │
│                                └──────────────────┘          │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Splunk SIEM (Port 8000, 8088, 8089)
- **Purpose**: Central log aggregation and search
- **Image**: `splunk/splunk:latest`
- **Volumes**: 
  - `splunk_data/etc`: Configuration
  - `splunk_data/var`: Indexes and data
- **Credentials**: admin / Admin@123456

### 2. Data Generator
- **Purpose**: Generate realistic threat scenario data
- **Language**: Python 3.11
- **Scenarios**:
  - SQL Injection (UNION, Boolean-based)
  - LDAP Injection
  - Credential dumping (Mimikatz, ProcDump)
  - IOC matching (malicious IPs, domains, hashes)
  - Lateral movement (PsExec, WMI, SMB)
- **Output**: 
  - Sends to Splunk HEC (HTTP Event Collector)
  - Saves JSON files to `/data` volume
- **Interval**: 60 seconds (configurable)

### 3. Threat Hunter Agent
- **Purpose**: AI-powered automated threat hunting
- **Language**: Python 3.11
- **Key Libraries**:
  - `anthropic`: Claude AI integration
  - `splunk-sdk`: Splunk query execution
  - `pyyaml`: Configuration management
  - `schedule`: Scheduled execution

#### Agent Workflow
```
┌─────────────┐
│   Startup   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Connect to │
│   Splunk    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Load      │
│  Queries &  │
│   MITRE     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Execute    │
│  Scheduled  │
│   Hunts     │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Query     │
│   Splunk    │
│    (SPL)    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Parse     │
│  Findings   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Claude    │
│   Analysis  │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Generate   │
│   Report    │
│ (HTML/JSON) │
└─────────────┘
```

## Data Flow

### Ingestion Pipeline
```
Attack Scenario → Faker Data → JSON Event → HEC API → Splunk Index
```

### Detection Pipeline
```
Splunk Index → SPL Query → Results → AI Analysis → Report
```

### Query Execution
```python
# Example SPL query
index=* sourcetype=access_combined
| regex _raw="(?i)(union|select|insert).*"
| stats count by src_ip, uri_path
| where count > 5
```

## MITRE ATT&CK Mapping

| Hunt Name | MITRE Technique | Tactic |
|-----------|----------------|--------|
| SQL Injection | T1190 | Initial Access |
| LDAP Injection | T1078 | Defense Evasion |
| LSass Dumping | T1003.001 | Credential Access |
| IOC Detection | T1071 | Command & Control |
| Lateral Movement | T1021 | Lateral Movement |

## Configuration Files

### queries.yml
Định nghĩa các scheduled hunts:
- Hunt name
- SPL query
- Schedule (cron)
- Severity level
- MITRE technique mapping

### mitre_mapping.yml
Map giữa hunts và MITRE framework:
- Technique ID
- Tactic
- Description
- Response actions by severity

## AI Integration

### Claude API Usage
```python
# Prompt structure
context = {
    'hunt_name': 'SQL Injection Hunt',
    'mitre': 'T1190 - Exploit Public-Facing Application',
    'findings': [...],
}

response = anthropic.messages.create(
    model="claude-sonnet-4-20250514",
    messages=[{
        "role": "user",
        "content": analyze_prompt
    }]
)
```

### AI Response Format
```json
{
  "summary": "Executive summary of threat",
  "risk_level": "Critical/High/Medium/Low",
  "analysis": "Detailed analysis",
  "impact": "Affected assets and impact",
  "immediate_actions": ["Action 1", "Action 2"],
  "preventive_measures": ["Measure 1", "Measure 2"],
  "mitre_techniques": ["T1190", "T1059"]
}
```

## Scaling Considerations

### Data Volume
- Current: ~100 events/minute
- Splunk Free: 500MB/day limit
- Scale up: Use Splunk Enterprise or distributed deployment

### Query Performance
- Indexed fields: src_ip, dest_ip, hostname, user
- Time range: Default -24h (configurable)
- Concurrent queries: Limited by Splunk search head

### Agent Scheduling
- Default: Every 6 hours
- CPU: ~100MB memory per hunt
- Parallel hunts: Sequential execution to avoid overload

## Security Considerations

### Credentials
- Stored in `.env` file (gitignored)
- Splunk: Strong password required
- API keys: Anthropic key required for AI features

### Network
- Internal Docker network
- No external exposure except ports 8000, 8088, 8089
- HEC uses HTTPS (self-signed cert in dev)

### Data Sensitivity
- Synthetic data only (Faker library)
- No real credentials or PII
- IOCs are examples, not actual threats

## Monitoring

### Health Checks
```bash
# Splunk health
curl -k https://localhost:8089/services/server/health

# Agent status
docker logs threat-hunter-agent | tail -20

# Data generation rate
ls -lh data/ && wc -l data/*.json
```

### Logs
- Splunk: `/opt/splunk/var/log/splunk`
- Generator: stdout (docker logs)
- Agent: stdout + reports directory

## Extension Points

### Adding New Threat Scenarios
1. Create `data-generator/scenarios/new_threat.py`
2. Implement `generate_*_events()` function
3. Import in `generator.py`
4. Add to generation loop

### Adding New Hunts
1. Add query to `threat-hunter/config/queries.yml`
2. Map to MITRE in `mitre_mapping.yml`
3. Optional: Create hunter module in `threat-hunter/hunters/`

### Custom AI Prompts
Modify `analyze_with_ai()` in `agent.py`:
- Change prompt structure
- Adjust model parameters
- Add custom analysis logic
