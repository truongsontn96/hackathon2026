# Hackathon 2026 - Scheduled Threat Hunting Script

## Chủ đề 1: Automated Threat Hunting với AI Agent

Hệ thống tự động săn tìm và phát hiện các mối đe dọa an ninh mạng sử dụng Splunk SIEM và AI Agent được xây dựng với Claude API.

## Kiến trúc hệ thống

```
┌─────────────────────┐
│  Threat Hunter AI   │
│     Agent           │◄─── Anthropic Claude API
└──────────┬──────────┘
           │
           │ Query & Analysis
           ▼
┌─────────────────────┐
│   Splunk SIEM       │
│   (Docker)          │
└──────────┬──────────┘
           │
           │ Ingest Logs
           ▼
┌─────────────────────┐
│  Data Generator     │
│  (Threat Scenarios) │
└─────────────────────┘
```

## Tính năng

### 1. Data Generation
- SQL Injection attacks
- LDAP Injection attempts
- LSass dumping activities
- Suspicious login patterns
- Network anomalies
- Malware IOCs

### 2. Threat Detection
- **Automated Scheduled Queries**: Chạy tự động theo lịch (mặc định: mỗi 6 giờ)
- **MITRE ATT&CK Mapping**: Tự động ánh xạ findings với MITRE framework
- **Risk Scoring**: Tính điểm rủi ro dựa trên impact và likelihood
- **Kill Chain Reconstruction**: Tái dựng cyber kill chain từ alerts

### 3. AI-Powered Analysis
- Phân tích context của alerts
- Đề xuất response actions
- Generate investigation reports
- Tự động pivot investigation

## Cài đặt

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Anthropic API Key

### Bước 1: Clone và Setup
```bash
cd /home/sonnt87/hackathon2026

# Copy environment file
cp .env.example .env

# Chỉnh sửa .env và thêm ANTHROPIC_API_KEY
nano .env
```

### Bước 2: Start Splunk Lab
```bash
# Build và start tất cả services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Bước 3: Truy cập Splunk
- URL: http://localhost:8000
- Username: `admin`
- Password: `Admin@123456`

### Bước 4: Verify Data Generation
```bash
# Check data generator logs
docker logs threat-data-generator

# Check generated data
ls -lh data/
```

### Bước 5: Monitor Threat Hunter Agent
```bash
# View threat hunter logs
docker logs -f threat-hunter-agent

# Check generated reports
ls -lh threat-hunter/reports/
```

## Cấu trúc thư mục

```
hackathon2026/
├── docker-compose.yml          # Orchestration
├── .env                         # Environment variables
├── data-generator/             
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── generator.py            # Main data generator
│   └── scenarios/              # Threat scenarios
│       ├── sqli.py
│       ├── ldap_injection.py
│       ├── lsass_dump.py
│       └── iocs.py
├── threat-hunter/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── agent.py                # Main AI agent
│   ├── hunters/                # Threat hunting modules
│   │   ├── sqli_hunter.py
│   │   ├── credential_hunter.py
│   │   └── lateral_movement.py
│   ├── config/
│   │   ├── queries.yml         # SPL queries
│   │   └── mitre_mapping.yml   # MITRE ATT&CK mapping
│   └── reports/                # Generated reports
├── data/                       # Generated log data
└── splunk_data/               # Splunk persistent data
    ├── etc/                    # Splunk configs
    └── var/                    # Splunk indexes
```

## Sử dụng

### Manual Threat Hunt
```bash
docker exec -it threat-hunter-agent python agent.py --hunt-now
```

### Query Splunk từ CLI
```bash
docker exec -it threat-hunter-agent python -c "
from agent import ThreatHunterAgent
agent = ThreatHunterAgent()
results = agent.hunt_sql_injection()
print(results)
"
```

### Generate Custom Report
```bash
docker exec -it threat-hunter-agent python agent.py --report --output custom_report.html
```

## Threat Hunting Queries

Hệ thống bao gồm các queries tự động cho:

1. **SQL Injection Detection**
   - Pattern matching với common SQL injection payloads
   - Anomaly detection trên query parameters
   - Volume-based detection

2. **LDAP Injection**
   - LDAP filter injection patterns
   - Authentication bypass attempts

3. **LSass Dumping**
   - Process access to lsass.exe
   - Credential dumping tools (Mimikatz signatures)

4. **Lateral Movement**
   - PsExec usage
   - WMI remote execution
   - Suspicious SMB activities

5. **IOC Matching**
   - Known malicious IPs
   - Malware file hashes
   - C2 domains

## AI Agent Capabilities

### 1. Context Analysis
Agent sử dụng Claude để phân tích:
- Alert context và correlation
- Historical patterns
- MITRE ATT&CK techniques

### 2. Auto Investigation
- Tự động pivot từ initial alert
- Build event timeline
- Identify affected assets

### 3. Response Recommendation
- Đề xuất containment actions
- Remediation steps
- Prevention measures

## Configuration

### Scheduled Hunting
Edit `threat-hunter/config/queries.yml`:
```yaml
scheduled_hunts:
  - name: SQL Injection Hunt
    schedule: "0 */6 * * *"  # Every 6 hours
    query: |
      index=web sourcetype=access_combined
      | regex _raw="(?i)(union|select|insert).*"
    severity: high
```

### MITRE Mapping
Edit `threat-hunter/config/mitre_mapping.yml`:
```yaml
techniques:
  T1190:
    name: Exploit Public-Facing Application
    hunts:
      - sqli
      - rce
      - xxe
```

## Monitoring & Alerts

### Splunk Dashboards
- Real-time threat detection dashboard
- IOC matching visualization
- Hunt campaign timeline

### Notifications
Configure trong `.env`:
- Slack webhook
- Email SMTP
- PagerDuty integration

## Troubleshooting

### Splunk không start
```bash
docker-compose down
sudo rm -rf splunk_data/var/*
docker-compose up -d splunk
```

### Data generator không gửi data
```bash
# Check HEC token
docker exec splunk-lab /opt/splunk/bin/splunk http-event-collector list

# Restart generator
docker-compose restart data-generator
```

### Agent không chạy queries
```bash
# Check Splunk connectivity
docker exec threat-hunter-agent python -c "
from splunklib import client
service = client.connect(host='splunk', port=8089, username='admin', password='Admin@123456')
print('Connected:', service.apps.list())
"
```

## Performance Tuning

### Data Volume
Điều chỉnh trong `.env`:
```bash
GENERATION_INTERVAL=60        # seconds between batches
THREAT_VOLUME=medium          # low/medium/high
```

### Agent Schedule
Edit docker-compose.yml:
```yaml
environment:
  - SCHEDULE_CRON=0 */6 * * *  # Adjust frequency
```

## Demo Scenarios

### Scenario 1: SQL Injection Campaign
```bash
# Generate SQL injection attacks
docker exec data-generator python scenarios/sqli.py --volume 100

# Trigger hunt
docker exec threat-hunter-agent python agent.py --hunt sqli

# View report
cat threat-hunter/reports/sqli_$(date +%Y%m%d).json
```

### Scenario 2: Credential Dumping
```bash
# Generate lsass dump events
docker exec data-generator python scenarios/lsass_dump.py --count 50

# Auto-detect with AI
docker exec threat-hunter-agent python agent.py --hunt credential_access
```

## API Documentation

### Agent API
```python
from threat_hunter.agent import ThreatHunterAgent

agent = ThreatHunterAgent(
    splunk_host='localhost',
    splunk_port=8089,
    anthropic_api_key='your-key'
)

# Run specific hunt
results = agent.hunt('sqli')

# Analyze with AI
analysis = agent.analyze_findings(results)

# Generate report
report = agent.generate_report(analysis)
```

## Contributing

Các bước để thêm threat hunting module mới:

1. Tạo hunter file trong `threat-hunter/hunters/`
2. Implement detection logic
3. Add SPL query vào `config/queries.yml`
4. Map với MITRE technique trong `config/mitre_mapping.yml`
5. Test với synthetic data

## License

MIT License - Hackathon 2026

## References

- [MITRE ATT&CK Framework](https://attack.mitre.org/)
- [Splunk SPL Reference](https://docs.splunk.com/Documentation/Splunk/latest/SearchReference)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## Support

- GitHub Issues: https://github.com/yourusername/hackathon2026/issues
- Email: sonnt87@example.com
