#!/usr/bin/env python3
"""
SQL Injection Attack Data Generator
Generates realistic SQL injection attack patterns
"""
import random
import time
from datetime import datetime
from faker import Faker

fake = Faker()

# SQL Injection payloads
SQLI_PAYLOADS = [
    "' OR '1'='1",
    "' OR 1=1--",
    "admin'--",
    "' UNION SELECT NULL--",
    "' UNION SELECT username, password FROM users--",
    "'; DROP TABLE users--",
    "' AND 1=2 UNION SELECT table_name FROM information_schema.tables--",
    "1' ORDER BY 1--",
    "1' ORDER BY 2--",
    "1' UNION ALL SELECT NULL,NULL,NULL--",
    "' OR 'x'='x",
    "' AND id IS NULL; --",
    "1'; WAITFOR DELAY '00:00:05'--",
    "' OR SLEEP(5)--",
    "' UNION SELECT @@version--",
    "admin' OR '1'='1'/*",
    "' UNION SELECT NULL, username, password, NULL FROM users--",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "sqlmap/1.4.7#stable",
    "python-requests/2.25.1",
    "Havij Advanced SQL Injection",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1)",
]

def generate_sql_injection_events(count=20):
    """Generate SQL injection attack events"""
    events = []

    attacker_ips = [fake.ipv4() for _ in range(max(1, count // 5))]

    for i in range(count):
        src_ip = random.choice(attacker_ips)
        payload = random.choice(SQLI_PAYLOADS)
        user_agent = random.choice(USER_AGENTS)

        # Target endpoints
        endpoints = [
            f"/login?username={payload}&password=test",
            f"/search?q={payload}",
            f"/product?id={payload}",
            f"/admin?id={payload}",
            f"/api/users?filter={payload}",
            f"/dashboard?sort={payload}",
        ]

        uri_path = random.choice(endpoints)

        event = {
            'timestamp': time.time() - random.randint(0, 86400),  # Last 24 hours
            'src_ip': src_ip,
            'dest_ip': '10.0.1.100',
            'method': 'GET' if random.random() > 0.3 else 'POST',
            'uri_path': uri_path,
            'status_code': random.choice([200, 500, 403, 401]),
            'user_agent': user_agent,
            'payload': payload,
            'attack_type': 'sql_injection',
            'severity': 'high',
            'raw_log': f'{src_ip} - - [{datetime.now().strftime("%d/%b/%Y:%H:%M:%S +0000")}] "GET {uri_path} HTTP/1.1" 200 1234 "-" "{user_agent}"'
        }

        events.append(event)

    return events

if __name__ == '__main__':
    events = generate_sql_injection_events(50)
    for event in events[:5]:
        print(event)
