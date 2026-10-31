#!/usr/bin/env python3
"""
Lateral Movement Attack Data Generator
Simulates lateral movement techniques (PsExec, WMI, SMB)
"""
import random
import time
from datetime import datetime
from faker import Faker

fake = Faker()

LATERAL_MOVEMENT_TECHNIQUES = [
    'psexec',
    'wmi',
    'smb',
    'rdp',
    'winrm',
]

def generate_lateral_movement_events(count=8):
    """Generate lateral movement events"""
    events = []

    # Simulate attacker moving through network
    source_host = f'WS-{fake.random_number(digits=4)}'
    attacker_user = fake.user_name()
    target_hosts = [f'SRV-{fake.random_number(digits=3)}' for _ in range(count)]

    for i, target_host in enumerate(target_hosts[:count]):
        technique = random.choice(LATERAL_MOVEMENT_TECHNIQUES)

        if technique == 'psexec':
            event = {
                'timestamp': time.time() - random.randint(0, 3600) - (i * 300),  # Sequential attacks
                'src_hostname': source_host,
                'dest_hostname': target_host,
                'user': attacker_user,
                'EventCode': 5145,  # Network share accessed
                'Share_Name': '\\\\*\\IPC$',
                'Process_Name': 'psexec.exe',
                'attack_type': 'lateral_movement',
                'technique': 'T1021.002',  # SMB/Windows Admin Shares
                'severity': 'high',
                'raw_log': f'EventCode=5145 src={source_host} dest={target_host} share=IPC$ user={attacker_user}'
            }

        elif technique == 'wmi':
            event = {
                'timestamp': time.time() - random.randint(0, 3600) - (i * 300),
                'src_hostname': source_host,
                'dest_hostname': target_host,
                'user': attacker_user,
                'EventCode': 4648,  # Logon with explicit credentials
                'Target_Server': target_host,
                'Process_Name': 'wmiprvse.exe',
                'attack_type': 'lateral_movement',
                'technique': 'T1021.006',  # Windows Remote Management
                'severity': 'high',
                'raw_log': f'EventCode=4648 src={source_host} dest={target_host} user={attacker_user} process=wmiprvse.exe'
            }

        else:  # smb
            event = {
                'timestamp': time.time() - random.randint(0, 3600) - (i * 300),
                'src_hostname': source_host,
                'dest_hostname': target_host,
                'user': attacker_user,
                'EventCode': 4624,  # Account logon
                'Logon_Type': 3,  # Network
                'Source_IP': f'10.0.{random.randint(1,10)}.{random.randint(1,254)}',
                'attack_type': 'lateral_movement',
                'technique': 'T1021.002',
                'severity': 'medium',
                'raw_log': f'EventCode=4624 LogonType=3 src={source_host} dest={target_host} user={attacker_user}'
            }

        events.append(event)

        # Update source for next hop
        if random.random() > 0.5:
            source_host = target_host

    return events

if __name__ == '__main__':
    events = generate_lateral_movement_events(8)
    for event in events:
        print(event)
