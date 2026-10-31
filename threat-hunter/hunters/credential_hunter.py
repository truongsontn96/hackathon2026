#!/usr/bin/env python3
"""
Credential Dumping Hunter Module
"""

def get_query():
    return """
index=* sourcetype="WinEventLog:Security" EventCode=4656
| search Object_Name="*lsass.exe"
| search Access_Mask="0x1fffff" OR Access_Mask="0x1410"
| stats count by hostname, user, Process_Name
| eval severity="critical", attack_type="credential_dumping"
"""

def analyze_findings(findings):
    """Analyze credential dumping findings"""
    analysis = {
        'total_attempts': len(findings),
        'affected_hosts': list(set([f.get('hostname') for f in findings])),
        'suspicious_users': list(set([f.get('user') for f in findings])),
        'tools_detected': []
    }

    for finding in findings:
        process = finding.get('Process_Name', '').lower()
        if 'mimikatz' in process:
            analysis['tools_detected'].append('Mimikatz')
        elif 'procdump' in process:
            analysis['tools_detected'].append('ProcDump')
        elif 'rundll32' in process:
            analysis['tools_detected'].append('RunDLL32 (Comsvcs.dll)')

    return analysis
