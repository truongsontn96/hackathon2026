#!/usr/bin/env python3
import json
import time
import os
import random
import schedule
from datetime import datetime
from scenarios import sqli, ldap_injection, lsass_dump, iocs, lateral_movement
import requests
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class ThreatDataGenerator:
    def __init__(self):
        self.splunk_hec_url = os.getenv('SPLUNK_HEC_URL', 'https://splunk:8088/services/collector/event')
        self.splunk_hec_token = os.getenv('SPLUNK_HEC_TOKEN', 'abcd1234-5678-90ef-ghij-klmnopqrstuv')
        self.generation_interval = int(os.getenv('GENERATION_INTERVAL', '60'))
        self.output_dir = '/output'

        os.makedirs(self.output_dir, exist_ok=True)

        print(f"[INFO] Threat Data Generator initialized")
        print(f"[INFO] HEC URL: {self.splunk_hec_url}")
        print(f"[INFO] Generation interval: {self.generation_interval}s")

    def wait_for_splunk(self, max_retries=30, retry_delay=10):
        """Wait for Splunk HEC to be ready"""
        print("[INFO] Waiting for Splunk HEC to be ready...")

        health_url = self.splunk_hec_url.replace('/services/collector/event', '/services/collector/health')

        for attempt in range(1, max_retries + 1):
            try:
                response = requests.get(health_url, verify=False, timeout=5)
                if response.status_code == 200:
                    print(f"[SUCCESS] Splunk HEC is ready!")
                    return True
            except Exception:
                print(f"[WAIT] Attempt {attempt}/{max_retries}: Splunk not ready yet...")

            time.sleep(retry_delay)

        print("[WARN] Splunk HEC still not ready after max retries. Will continue anyway.")
        return False

    def send_to_splunk(self, events, sourcetype):
        """Send events to Splunk HEC"""
        headers = {
            'Authorization': f'Splunk {self.splunk_hec_token}',
            'Content-Type': 'application/json'
        }

        for event in events:
            payload = {
                'time': event.get('timestamp', time.time()),
                'sourcetype': sourcetype,
                'event': event
            }

            try:
                response = requests.post(
                    self.splunk_hec_url,
                    headers=headers,
                    json=payload,
                    verify=False,
                    timeout=10
                )

                if response.status_code == 200:
                    print(f"[SUCCESS] Sent {sourcetype} event to Splunk")
                else:
                    print(f"[ERROR] Failed to send to Splunk: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"[ERROR] Exception sending to Splunk: {e}")

    def save_to_file(self, events, filename):
        """Save events to file"""
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, 'a') as f:
            for event in events:
                f.write(json.dumps(event) + '\n')

        print(f"[INFO] Saved {len(events)} events to {filepath}")

    def generate_threats(self):
        """Generate threat events"""
        print(f"\n[{datetime.now()}] Generating threat scenarios...")

        # SQL Injection attacks
        sqli_events = sqli.generate_sql_injection_events(count=random.randint(10, 30))
        self.send_to_splunk(sqli_events, 'access_combined')
        self.save_to_file(sqli_events, 'sqli_attacks.json')

        # LDAP Injection attempts
        ldap_events = ldap_injection.generate_ldap_injection_events(count=random.randint(5, 15))
        self.send_to_splunk(ldap_events, 'web_application')
        self.save_to_file(ldap_events, 'ldap_injection.json')

        # LSass dumping
        if random.random() > 0.7:
            lsass_events = lsass_dump.generate_lsass_dump_events(count=random.randint(1, 5))
            self.send_to_splunk(lsass_events, 'WinEventLog:Security')
            self.save_to_file(lsass_events, 'lsass_dumps.json')

        # IOC matching
        ioc_events = iocs.generate_ioc_events(count=random.randint(5, 20))
        self.send_to_splunk(ioc_events, 'firewall')
        self.save_to_file(ioc_events, 'ioc_matches.json')

        # Lateral movement
        if random.random() > 0.8:
            lateral_events = lateral_movement.generate_lateral_movement_events(count=random.randint(2, 8))
            self.send_to_splunk(lateral_events, 'WinEventLog:Security')
            self.save_to_file(lateral_events, 'lateral_movement.json')

        print(f"[DONE] Threat generation complete\n")

    def run(self):
        """Run generator on schedule"""
        print("[INFO] Starting scheduled threat generation...")

        # Wait for Splunk to be ready before generating
        self.wait_for_splunk()

        # Run immediately on start
        self.generate_threats()

        # Schedule regular generation
        schedule.every(self.generation_interval).seconds.do(self.generate_threats)

        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    generator = ThreatDataGenerator()
    generator.run()
