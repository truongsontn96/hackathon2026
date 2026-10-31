#!/usr/bin/env python3
"""
IOC (Indicators of Compromise) Event Generator
Generates events matching known malicious indicators
"""
import random
import time
from datetime import datetime
from faker import Faker

fake = Faker()

# Known malicious IPs (examples - not real C2 servers)
MALICIOUS_IPS = [
    '185.220.101.1',
    '45.142.214.123',
    '91.219.237.244',
    '198.54.117.215',
    '104.244.79.94',
]

# Malicious domains
MALICIOUS_DOMAINS = [
    'evil-c2-server.com',
    'malware-download.net',
    'phishing-site.org',
    'ransomware-c2.biz',
    'data-exfil-server.ru',
]

# Malware hashes (MD5)
MALWARE_HASHES = [
    '44d88612fea8a8f36de82e1278abb02f',
    '5d41402abc4b2a76b9719d911017c592',
    '098f6bcd4621d373cade4e832627b4f6',
    'e99a18c428cb38d5f260853678922e03',
]

def generate_ioc_events(count=15):
    """Generate IOC matching events"""
    events = []

    internal_ips = [f'10.0.{random.randint(1,10)}.{random.randint(1,254)}' for _ in range(5)]

    for i in range(count):
        ioc_type = random.choice(['ip', 'domain', 'hash'])
        src_ip = random.choice(internal_ips)

        if ioc_type == 'ip':
            dest_ip = random.choice(MALICIOUS_IPS)
            event = {
                'timestamp': time.time() - random.randint(0, 86400),
                'src_ip': src_ip,
                'dest_ip': dest_ip,
                'dest_port': random.choice([443, 8080, 4444, 1337]),
                'protocol': 'TCP',
                'bytes_out': random.randint(1024, 102400),
                'ioc_type': 'malicious_ip',
                'severity': 'critical',
                'threat_name': 'C2_Communication',
                'raw_log': f'FIREWALL: src={src_ip} dst={dest_ip} proto=TCP action=allowed'
            }

        elif ioc_type == 'domain':
            domain = random.choice(MALICIOUS_DOMAINS)
            event = {
                'timestamp': time.time() - random.randint(0, 86400),
                'src_ip': src_ip,
                'query': domain,
                'query_type': 'A',
                'answer': random.choice(MALICIOUS_IPS),
                'ioc_type': 'malicious_domain',
                'severity': 'high',
                'threat_name': 'Malware_Callback',
                'raw_log': f'DNS: client={src_ip} query={domain} type=A answer={random.choice(MALICIOUS_IPS)}'
            }

        else:  # hash
            file_hash = random.choice(MALWARE_HASHES)
            event = {
                'timestamp': time.time() - random.randint(0, 86400),
                'hostname': f'WS-{fake.random_number(digits=4)}',
                'file_path': f'C:\\Users\\{fake.user_name()}\\Downloads\\{fake.file_name()}',
                'file_hash': file_hash,
                'hash_type': 'MD5',
                'action': random.choice(['quarantined', 'blocked', 'allowed']),
                'ioc_type': 'malicious_hash',
                'severity': 'critical',
                'threat_name': 'Known_Malware',
                'raw_log': f'AV: file={file_hash} action=quarantined threat=TrojanDownloader'
            }

        events.append(event)

    return events

if __name__ == '__main__':
    events = generate_ioc_events(20)
    for event in events[:5]:
        print(event)
