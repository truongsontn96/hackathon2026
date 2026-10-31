#!/usr/bin/env python3
"""
SQL Injection Hunter Module
"""

def get_query():
    return """
index=* sourcetype=access_combined OR sourcetype=web_application
| regex _raw="(?i)(union|select|insert|update|delete|drop|;--|'--|\bor\b.*=.*)"
| stats count by src_ip, uri_path, user_agent
| where count > 5
| eval severity="high", attack_type="sql_injection"
"""

def analyze_findings(findings):
    """Analyze SQL injection findings"""
    analysis = {
        'total_attacks': len(findings),
        'unique_attackers': len(set([f.get('src_ip') for f in findings])),
        'targeted_endpoints': list(set([f.get('uri_path') for f in findings])),
        'attack_patterns': []
    }

    for finding in findings:
        if 'union' in finding.get('uri_path', '').lower():
            analysis['attack_patterns'].append('UNION-based SQL injection')
        if 'or' in finding.get('uri_path', '').lower():
            analysis['attack_patterns'].append('Boolean-based blind SQL injection')

    return analysis
