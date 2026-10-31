# Quick Start Guide

## Khởi động nhanh

```bash
# Bước 1: Setup (chỉ cần chạy lần đầu)
./setup.sh

# Bước 2: Start services
./start.sh

# Bước 3: Truy cập Splunk
# Mở browser: http://localhost:8000
# Login: admin / Admin@123456
```

## Kiểm tra hệ thống

```bash
# Xem logs của tất cả services
docker-compose logs -f

# Xem logs của từng service
docker-compose logs -f splunk-lab
docker-compose logs -f threat-data-generator
docker-compose logs -f threat-hunter-agent

# Kiểm tra service status
docker-compose ps
```

## Chạy threat hunt thủ công

```bash
# Trigger threat hunt ngay lập tức
docker exec threat-hunter-agent python agent.py --hunt-now

# Xem reports được tạo ra
ls -lh threat-hunter/reports/
```

## Data được generate

Hệ thống tự động tạo các loại attack data:
- SQL Injection attacks
- LDAP Injection attempts  
- LSass memory dumping
- IOC matching (malicious IPs, domains, hashes)
- Lateral movement activities

Xem data đã generate:
```bash
ls -lh data/
cat data/sqli_attacks.json | head -5
```

## Dừng hệ thống

```bash
./stop.sh
```

## Troubleshooting

### Splunk không khởi động
```bash
docker-compose down
sudo rm -rf splunk_data/var/*
docker-compose up -d splunk
```

### Agent không kết nối được Splunk
Chờ 2-3 phút để Splunk hoàn tất khởi động, sau đó restart agent:
```bash
docker-compose restart threat-hunter-agent
```

### Thêm Anthropic API key
```bash
nano .env
# Thêm: ANTHROPIC_API_KEY=your_key_here
docker-compose restart threat-hunter-agent
```

## Cấu trúc Reports

Reports được tạo ở `threat-hunter/reports/`:
- HTML report: `threat_hunt_report_YYYYMMDD_HHMMSS.html`
- JSON data: `threat_hunt_report_YYYYMMDD_HHMMSS.json`

Mở HTML report trong browser để xem phân tích chi tiết với AI insights.
