#!/usr/bin/env python3
"""
Lateral Movement Hunter Module
"""

def get_query():
    return """
index=* sourcetype="WinEventLog:Security"
(EventCode=4648 OR EventCode=5145 OR EventCode=4624)
| search (Share_Name="*IPC$" OR Process_Name="*psexec*" OR Process_Name="*wmi*")
| transaction src_hostname dest_hostname maxspan=30m
| where eventcount > 3
| eval severity="high", attack_type="lateral_movement"
"""

def analyze_findings(findings):
    """Analyze lateral movement findings"""
    analysis = {
        'total_movements': len(findings),
        'movement_paths': [],
        'techniques_used': [],
        'compromised_hosts': set()
    }

    for finding in findings:
        src = finding.get('src_hostname')
        dest = finding.get('dest_hostname')

        if src and dest:
            analysis['movement_paths'].append(f"{src} → {dest}")
            analysis['compromised_hosts'].add(src)
            analysis['compromised_hosts'].add(dest)

        if 'psexec' in str(finding).lower():
            analysis['techniques_used'].append('PsExec')
        if 'wmi' in str(finding).lower():
            analysis['techniques_used'].append('WMI')

    analysis['compromised_hosts'] = list(analysis['compromised_hosts'])
    analysis['techniques_used'] = list(set(analysis['techniques_used']))

    return analysis
