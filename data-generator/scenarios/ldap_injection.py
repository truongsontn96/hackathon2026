#!/usr/bin/env python3
"""
LDAP Injection Attack Data Generator
"""
import random
import time
from datetime import datetime
from faker import Faker

fake = Faker()

LDAP_PAYLOADS = [
    "*",
    "*)(&",
    "*)(uid=*))(|(uid=*",
    "admin)(&",
    "*))(|(objectClass=*",
    "*)(objectClass=*))(&(objectClass=*",
    "*)(&(password=*))",
    "admin)(|(password=*))",
]

def generate_ldap_injection_events(count=10):
    """Generate LDAP injection attack events"""
    events = []

    attacker_ips = [fake.ipv4() for _ in range(max(1, count // 3))]

    for i in range(count):
        src_ip = random.choice(attacker_ips)
        payload = random.choice(LDAP_PAYLOADS)

        event = {
            'timestamp': time.time() - random.randint(0, 86400),
            'src_ip': src_ip,
            'dest_ip': '10.0.1.101',
            'application': 'ldap_auth',
            'username': payload,
            'auth_result': random.choice(['failed', 'success', 'error']),
            'attack_type': 'ldap_injection',
            'severity': 'high',
            'ldap_filter': f'(&(uid={payload})(objectClass=person))',
            'raw_log': f'LDAP AUTH: src={src_ip} user="{payload}" result=failed filter="(&(uid={payload})(objectClass=person))"'
        }

        events.append(event)

    return events

if __name__ == '__main__':
    events = generate_ldap_injection_events(10)
    for event in events:
        print(event)
