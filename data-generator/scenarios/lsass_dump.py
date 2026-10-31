#!/usr/bin/env python3
"""
LSass Dumping Attack Data Generator
Simulates credential dumping activities
"""
import random
import time
from datetime import datetime
from faker import Faker

fake = Faker()

ATTACK_TOOLS = [
    'mimikatz.exe',
    'procdump.exe',
    'powershell.exe',
    'rundll32.exe',
    'comsvcs.dll',
]

def generate_lsass_dump_events(count=5):
    """Generate LSass dumping events"""
    events = []

    hostnames = [f'WS-{fake.random_number(digits=4)}' for _ in range(max(1, count // 2))]
    usernames = [fake.user_name() for _ in range(3)]

    for i in range(count):
        hostname = random.choice(hostnames)
        username = random.choice(usernames)
        tool = random.choice(ATTACK_TOOLS)

        event = {
            'timestamp': time.time() - random.randint(0, 86400),
            'hostname': hostname,
            'user': username,
            'EventCode': 4656,  # Handle to object requested
            'Object_Name': 'C:\\Windows\\System32\\lsass.exe',
            'Process_Name': f'C:\\Windows\\System32\\{tool}',
            'Access_Mask': '0x1fffff' if random.random() > 0.5 else '0x1410',
            'attack_type': 'credential_dumping',
            'severity': 'critical',
            'mitre_technique': 'T1003.001',  # LSASS Memory
            'raw_log': f'EventCode=4656 Hostname={hostname} User={username} ObjectName=lsass.exe ProcessName={tool} AccessMask=0x1fffff'
        }

        events.append(event)

        # Add corresponding process creation event
        if random.random() > 0.5:
            proc_event = {
                'timestamp': event['timestamp'] - 5,
                'hostname': hostname,
                'user': username,
                'EventCode': 4688,  # Process created
                'Process_Name': f'C:\\Windows\\System32\\{tool}',
                'CommandLine': f'{tool} -accepteula -ma lsass.exe lsass.dmp' if 'procdump' in tool else f'{tool} sekurlsa::logonpasswords',
                'Parent_Process': 'C:\\Windows\\System32\\cmd.exe',
                'attack_type': 'credential_dumping',
                'severity': 'critical',
                'raw_log': f'EventCode=4688 Hostname={hostname} User={username} NewProcessName={tool}'
            }
            events.append(proc_event)

    return events

if __name__ == '__main__':
    events = generate_lsass_dump_events(5)
    for event in events:
        print(event)
