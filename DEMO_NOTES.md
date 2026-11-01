# Hackathon 2026 - Demo Presentation Notes

## Elevator Pitch (30 seconds)
"Tôi xây dựng một AI-powered threat hunting platform tự động phát hiện các cuộc tấn công mạng. Hệ thống sử dụng Splunk SIEM để thu thập logs, generate realistic attack scenarios, và dùng Claude AI để phân tích threats theo MITRE ATT&CK framework - tất cả chạy tự động 24/7."

## Live Demo Flow (5 phút)

### 1. Giới thiệu Kiến trúc (1 phút)
**Hiển thị**: ARCHITECTURE.md diagram

"Hệ thống có 3 components chính:
- **Data Generator**: Tự động tạo attack scenarios (SQL injection, credential dumping, lateral movement)
- **Splunk SIEM**: Central log aggregation
- **AI Threat Hunter**: Claude AI phân tích và tạo reports"

### 2. Show Data Generation (1 phút)
```bash
# Terminal 1: Show data being generated
docker logs -f threat-data-generator --tail 20
```

**Nói**: "Generator đang tạo synthetic attacks mỗi 60 giây - SQL injection, LSass dumps, lateral movement - giống như real attacks trong enterprise environment."

### 3. Splunk Dashboard (1 phút)
**Browser**: http://localhost:8000

```spl
index=* sourcetype=attack_data OR sourcetype=access_combined
| stats count by attack_technique
| sort -count
```

**Nói**: "Splunk đã collect được [X] events. Mỗi event được map với MITRE ATT&CK techniques."

Show visualization:
```spl
index=* attack_technique=*
| timechart count by attack_technique
```

### 4. Trigger AI Hunt (1 phút)
```bash
# Terminal 2: Manual hunt trigger
docker exec threat-hunter-agent python agent.py --hunt-now
```

**Nói**: "AI Agent đang chạy 6 scheduled hunts - query Splunk, phân tích patterns, và gọi Claude API để generate insights."

### 5. Show AI Report (1 phút)
**Browser**: Open latest HTML report

**Walk through**:
- ✅ Executive summary with risk assessment
- ✅ MITRE ATT&CK technique mapping
- ✅ AI analysis with recommendations
- ✅ Sample findings with raw logs

**Nói**: "Claude AI đã phân tích [X] findings, identified [Y] attack campaigns, và recommend immediate actions - tất cả tự động."

## Key Talking Points

### Technical Highlights
- ✅ **Fully Dockerized**: Một lệnh `docker-compose up` là chạy
- ✅ **Real Attack Data**: Sử dụng Mordor datasets - MITRE ATT&CK mapped
- ✅ **Production-Ready Architecture**: Scalable, modular, extensible
- ✅ **AI-Powered**: Claude Sonnet 5 integration cho intelligent analysis

### Business Value
- ⏰ **24/7 Automated Hunting**: Không cần SOC analyst thức đêm
- 🎯 **Reduce False Positives**: AI context-aware analysis
- 📊 **MITRE Mapping**: Compliance-ready reporting
- 💰 **Cost Effective**: Splunk Free + Claude API << Full SOC team

### Innovation Points
- 🆕 **AI + SIEM Integration**: First-of-its-kind automated hunting
- 🆕 **Synthetic Threat Lab**: Realistic training environment
- 🆕 **Auto Campaign Reconstruction**: AI reconstructs attack timeline

## Q&A Preparation

**Q: Làm sao scale với production data volume?**
A: "Hiện tại dùng Splunk Free (500MB/day). Production có thể dùng Splunk Enterprise hoặc Elastic Stack, agent architecture vẫn giữ nguyên - chỉ cần đổi data source."

**Q: False positive rate như thế nào?**
A: "AI analysis giúp reduce false positives qua context correlation. Trong demo, agent cross-reference multiple data sources và apply MITRE context trước khi alert."

**Q: Cost của Claude API?**
A: "Mỗi hunt ~2K tokens input + 1K output = ~$0.01/hunt. Chạy 4 lần/ngày = $0.30/month. So với SOC analyst salary ($80K+/year), ROI là enormous."

**Q: Có thể add custom detections không?**
A: "Có - chỉ cần add query vào `queries.yml` và map với MITRE technique. Agent sẽ tự động pick up và run."

**Q: Làm sao verify AI recommendations?**
A: "Mỗi recommendation link với raw logs và MITRE ATT&CK reference. Security team có thể verify trước khi action."

## Demo Backup Plan

### Nếu Splunk chưa ready:
- Show pre-generated reports từ `threat-hunter/reports/`
- Walk through architecture diagrams
- Explain code flow trong `agent.py`

### Nếu Docker issues:
- Show code walkthrough
- Explain data generation scenarios
- Demo SPL queries trên slides

### Nếu network issues:
- Run offline demo (no Claude API)
- Show synthetic data generation
- Explain how AI integration works

## Post-Demo Follow-up

**Để lại impression**:
"Full source code + documentation available tại GitHub. Hệ thống này có thể deploy trong < 30 minutes, và tôi đã included real-world attack datasets để start hunting ngay."

**Call to action**:
"Nếu quan tâm về AI security automation hoặc muốn collaborate, tôi rất sẵn lòng discuss further!"

## Metrics to Highlight

Generate these before demo:
```bash
# Lines of code
find . -name "*.py" -o -name "*.yml" | xargs wc -l

# Number of threat scenarios
ls -1 data-generator/scenarios/*.py | wc -l

# Attack techniques covered
grep -r "T[0-9]" threat-hunter/config/ | wc -l

# Events generated
wc -l data/*.json
```

Expected outputs:
- ~2,500 lines of code
- 5 threat scenarios
- 8+ MITRE techniques
- 1,000+ synthetic events

## Slides Outline (Optional)

**Slide 1**: Title + "AI-Powered Automated Threat Hunting"

**Slide 2**: Problem Statement
- Manual threat hunting is slow
- Alert fatigue in SOCs
- Skills shortage in cybersecurity

**Slide 3**: Solution Architecture
- Diagram from ARCHITECTURE.md

**Slide 4**: Key Features
- Automated 24/7 hunting
- AI-powered analysis
- MITRE ATT&CK mapping
- Production-ready

**Slide 5**: Live Demo
(Switch to terminal)

**Slide 6**: Results & Impact
- Metrics dashboard
- Sample findings

**Slide 7**: Future Enhancements
- Integration với SOAR platforms
- Custom ML models
- Multi-tenant support

**Slide 8**: Thank You + GitHub link
