#!/usr/bin/env python3
"""
Threat Hunter AI Agent
Main agent orchestrating threat hunting with Claude AI
"""
import os
import sys
import time
import json
import yaml
import schedule
from datetime import datetime
from pathlib import Path
import anthropic
import splunklib.client as client
import splunklib.results as results

class ThreatHunterAgent:
    def __init__(self):
        self.splunk_host = os.getenv('SPLUNK_HOST', 'splunk')
        self.splunk_port = int(os.getenv('SPLUNK_PORT', '8089'))
        self.splunk_username = os.getenv('SPLUNK_USERNAME', 'admin')
        self.splunk_password = os.getenv('SPLUNK_PASSWORD', 'Admin@123456')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.schedule_cron = os.getenv('SCHEDULE_CRON', '0 */6 * * *')

        self.config_dir = Path('/app/config')
        self.reports_dir = Path('/app/reports')
        self.reports_dir.mkdir(exist_ok=True)

        # Load configurations
        self.queries = self.load_queries()
        self.mitre_mapping = self.load_mitre_mapping()

        # Initialize clients
        self.splunk_service = None
        self.anthropic_client = None

        print(f"[INFO] Threat Hunter Agent initialized")
        print(f"[INFO] Splunk: {self.splunk_host}:{self.splunk_port}")
        print(f"[INFO] Schedule: {self.schedule_cron}")

    def load_queries(self):
        """Load threat hunting queries"""
        queries_file = self.config_dir / 'queries.yml'
        if queries_file.exists():
            with open(queries_file) as f:
                return yaml.safe_load(f)
        return {'scheduled_hunts': []}

    def load_mitre_mapping(self):
        """Load MITRE ATT&CK mapping"""
        mitre_file = self.config_dir / 'mitre_mapping.yml'
        if mitre_file.exists():
            with open(mitre_file) as f:
                return yaml.safe_load(f)
        return {}

    def connect_splunk(self):
        """Connect to Splunk"""
        try:
            self.splunk_service = client.connect(
                host=self.splunk_host,
                port=self.splunk_port,
                username=self.splunk_username,
                password=self.splunk_password
            )
            print("[SUCCESS] Connected to Splunk")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to connect to Splunk: {e}")
            return False

    def connect_anthropic(self):
        """Initialize Anthropic client"""
        if not self.anthropic_api_key:
            print("[WARN] No ANTHROPIC_API_KEY provided, AI features disabled")
            return False

        try:
            self.anthropic_client = anthropic.Anthropic(api_key=self.anthropic_api_key)
            print("[SUCCESS] Anthropic client initialized")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to initialize Anthropic: {e}")
            return False

    def execute_splunk_query(self, query, earliest_time='-24h', latest_time='now'):
        """Execute SPL query and return results"""
        if not self.splunk_service:
            if not self.connect_splunk():
                return []

        try:
            kwargs_search = {
                'earliest_time': earliest_time,
                'latest_time': latest_time,
                'exec_mode': 'normal'
            }

            job = self.splunk_service.jobs.create(query, **kwargs_search)

            # Wait for job to complete
            while not job.is_done():
                time.sleep(0.5)

            # Get results
            result_stream = job.results(output_mode='json')
            result_data = json.loads(result_stream.read())

            return result_data.get('results', [])

        except Exception as e:
            print(f"[ERROR] Query execution failed: {e}")
            return []

    def analyze_with_ai(self, findings, hunt_name):
        """Analyze findings with Claude AI"""
        if not self.anthropic_client:
            print("[WARN] AI analysis skipped - no API key")
            return {"analysis": "AI analysis unavailable", "recommendations": []}

        try:
            # Get MITRE context
            mitre_context = self.get_mitre_context(hunt_name)

            prompt = f"""You are a cybersecurity threat analyst. Analyze the following threat hunting findings:

Hunt Name: {hunt_name}
MITRE ATT&CK Context: {json.dumps(mitre_context, indent=2)}

Findings:
{json.dumps(findings, indent=2)}

Please provide:
1. Executive summary of the threat
2. Risk assessment (Critical/High/Medium/Low)
3. Detailed analysis of attack patterns
4. Affected assets and potential impact
5. Recommended immediate actions
6. Recommended preventive measures
7. Related MITRE ATT&CK techniques

Format your response as JSON with keys: summary, risk_level, analysis, impact, immediate_actions, preventive_measures, mitre_techniques"""

            message = self.anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = message.content[0].text

            # Try to parse as JSON, fallback to text
            try:
                analysis = json.loads(response_text)
            except:
                analysis = {
                    "summary": response_text,
                    "risk_level": "Unknown",
                    "analysis": response_text
                }

            return analysis

        except Exception as e:
            print(f"[ERROR] AI analysis failed: {e}")
            return {"analysis": "AI analysis failed", "error": str(e)}

    def get_mitre_context(self, hunt_name):
        """Get MITRE ATT&CK context for a hunt"""
        mitre_techniques = self.mitre_mapping.get('mitre_techniques', {})

        for technique_id, technique_info in mitre_techniques.items():
            if hunt_name.lower() in [h.lower() for h in technique_info.get('hunts', [])]:
                return {
                    'technique_id': technique_id,
                    'name': technique_info.get('name'),
                    'tactic': technique_info.get('tactic'),
                    'description': technique_info.get('description'),
                    'severity': technique_info.get('severity')
                }

        return {}

    def generate_report(self, hunt_results):
        """Generate HTML report"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.reports_dir / f'threat_hunt_report_{timestamp}.html'

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Threat Hunt Report - {timestamp}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1 {{ color: #d32f2f; border-bottom: 3px solid #d32f2f; padding-bottom: 10px; }}
        h2 {{ color: #1976d2; margin-top: 30px; }}
        .hunt {{ background: #f9f9f9; padding: 15px; margin: 15px 0; border-left: 4px solid #1976d2; }}
        .critical {{ border-left-color: #d32f2f; }}
        .high {{ border-left-color: #f57c00; }}
        .medium {{ border-left-color: #fbc02d; }}
        .finding {{ background: white; padding: 10px; margin: 10px 0; border: 1px solid #ddd; }}
        .severity {{ display: inline-block; padding: 5px 10px; border-radius: 3px; color: white; font-weight: bold; }}
        .severity.critical {{ background: #d32f2f; }}
        .severity.high {{ background: #f57c00; }}
        .severity.medium {{ background: #fbc02d; color: black; }}
        .mitre {{ background: #e3f2fd; padding: 10px; margin: 10px 0; border-radius: 5px; }}
        pre {{ background: #263238; color: #aed581; padding: 10px; overflow-x: auto; }}
        .recommendations {{ background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 15px 0; }}
        .timestamp {{ color: #666; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Automated Threat Hunt Report</h1>
        <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
"""

        for hunt in hunt_results:
            severity = hunt.get('severity', 'medium')
            html += f"""
        <div class="hunt {severity}">
            <h2>{hunt['name']}</h2>
            <span class="severity {severity}">{severity.upper()}</span>
            <p><strong>Findings:</strong> {len(hunt['findings'])} events detected</p>
"""

            if hunt.get('mitre_context'):
                mitre = hunt['mitre_context']
                html += f"""
            <div class="mitre">
                <strong>MITRE ATT&CK:</strong> {mitre.get('technique_id')} - {mitre.get('name')}<br>
                <strong>Tactic:</strong> {mitre.get('tactic')}<br>
                <strong>Description:</strong> {mitre.get('description')}
            </div>
"""

            if hunt.get('ai_analysis'):
                ai = hunt['ai_analysis']
                html += f"""
            <div class="recommendations">
                <h3>🤖 AI Analysis</h3>
                <p><strong>Summary:</strong> {ai.get('summary', 'N/A')}</p>
                <p><strong>Risk Level:</strong> {ai.get('risk_level', 'Unknown')}</p>
"""

                if ai.get('immediate_actions'):
                    html += "<p><strong>Immediate Actions:</strong></p><ul>"
                    actions = ai.get('immediate_actions')
                    if isinstance(actions, list):
                        for action in actions:
                            html += f"<li>{action}</li>"
                    else:
                        html += f"<li>{actions}</li>"
                    html += "</ul>"

                html += "</div>"

            # Show sample findings
            if hunt['findings']:
                html += "<h3>Sample Findings:</h3>"
                for finding in hunt['findings'][:5]:
                    html += f'<div class="finding"><pre>{json.dumps(finding, indent=2)}</pre></div>'

            html += "</div>"

        html += """
    </div>
</body>
</html>
"""

        with open(report_file, 'w') as f:
            f.write(html)

        print(f"[SUCCESS] Report saved: {report_file}")
        return report_file

    def run_scheduled_hunts(self):
        """Execute all scheduled hunts"""
        print(f"\n{'='*60}")
        print(f"[{datetime.now()}] Starting scheduled threat hunts")
        print(f"{'='*60}\n")

        all_results = []

        for hunt in self.queries.get('scheduled_hunts', []):
            hunt_name = hunt['name']
            query = hunt['query']
            severity = hunt.get('severity', 'medium')

            print(f"[HUNT] {hunt_name} (severity: {severity})")

            # Execute query
            findings = self.execute_splunk_query(query)

            print(f"[RESULT] Found {len(findings)} events")

            if findings:
                # Get MITRE context
                mitre_context = self.get_mitre_context(hunt_name.lower().replace(' ', '_'))

                # AI analysis
                print(f"[AI] Analyzing with Claude...")
                ai_analysis = self.analyze_with_ai(findings, hunt_name)

                result = {
                    'name': hunt_name,
                    'severity': severity,
                    'findings': findings,
                    'mitre_context': mitre_context,
                    'ai_analysis': ai_analysis,
                    'timestamp': datetime.now().isoformat()
                }

                all_results.append(result)
            else:
                print(f"[INFO] No threats detected")

            print()

        # Generate report
        if all_results:
            report_file = self.generate_report(all_results)
            print(f"\n[SUCCESS] Threat hunting complete!")
            print(f"[REPORT] {report_file}")

            # Save JSON version
            json_file = report_file.with_suffix('.json')
            with open(json_file, 'w') as f:
                json.dump(all_results, f, indent=2)
            print(f"[REPORT] {json_file}")
        else:
            print("\n[INFO] No threats detected in any hunt")

        print(f"\n{'='*60}\n")

        return all_results

    def run(self):
        """Main loop"""
        print("[INFO] Threat Hunter Agent starting...")

        # Connect to services
        self.connect_splunk()
        self.connect_anthropic()

        # Wait for Splunk to be ready
        print("[INFO] Waiting for Splunk to be ready...")
        for i in range(30):
            if self.connect_splunk():
                break
            print(f"[WAIT] Retry {i+1}/30...")
            time.sleep(10)

        # Run immediately on start
        self.run_scheduled_hunts()

        # Schedule regular runs (every 6 hours)
        schedule.every(6).hours.do(self.run_scheduled_hunts)

        print("[INFO] Scheduled hunting active (every 6 hours)")
        print("[INFO] Press Ctrl+C to stop")

        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == '__main__':
    import sys

    agent = ThreatHunterAgent()

    if len(sys.argv) > 1 and sys.argv[1] == '--hunt-now':
        # Manual trigger
        agent.connect_splunk()
        agent.connect_anthropic()
        agent.run_scheduled_hunts()
    else:
        # Scheduled mode
        try:
            agent.run()
        except KeyboardInterrupt:
            print("\n[INFO] Shutting down gracefully...")
            sys.exit(0)
