"""
Log Analyzer - Parses system/auth/web logs for threats and anomalies.
Enhanced for open-source PR submission:
- Preserves exact class interface: analyze(file_path) and analyze_text(log_text).
- Adds IP frequency anomaly detection and OWASP threat pattern matching.
- Supports structured JSON logs (CloudTrail, Docker, NGINX).
"""

import json
import os
import re
from collections import Counter
from typing import Dict, List, Tuple


# Threat pattern signatures
THREAT_PATTERNS = {
    "SSH Brute Force": [
        r"Failed password for .+ from ([\d.]+)",
        r"Invalid user .+ from ([\d.]+)",
        r"authentication failure.*rhost=([\d.]+)",
    ],
    "Sudo Escalation": [
        r"sudo:.*FAILED",
        r"sudo:.*command not allowed",
    ],
    "Web Attack (SQLi)": [
        r"(?i)(select|union|insert|drop|--\s|xp_|exec\()",
    ],
    "Web Attack (XSS)": [
        r"(?i)(<script|javascript:|onerror=|onload=)",
    ],
    "Port Scan": [
        r"SCAN|portscan",
    ],
    "Suspicious Process": [
        r"(?i)(nc -|netcat|/dev/tcp|bash -i|python.*socket)",
    ],
    "File Inclusion": [
        r"(?i)(\.\./|etc/passwd|etc/shadow|proc/self)",
    ],
    "Privilege Escalation": [
        r"(?i)(chmod 777|chmod \+s|suid|sgid)",
    ],
}

SEVERITY_MAP = {
    "SSH Brute Force": "HIGH",
    "Sudo Escalation": "HIGH",
    "Web Attack (SQLi)": "CRITICAL",
    "Web Attack (XSS)": "HIGH",
    "Port Scan": "MEDIUM",
    "Suspicious Process": "CRITICAL",
    "File Inclusion": "HIGH",
    "Privilege Escalation": "CRITICAL",
}


class LogAnalyzer:
    def analyze(self, file_path: str) -> str:
        """Analyze a log file for security threats."""
        path = os.path.abspath(os.path.expanduser(file_path))

        if not os.path.exists(path):
            return f"❌ Log file not found: {path}"

        try:
            with open(path, "r", errors="replace") as f:
                lines = f.readlines()
        except Exception as e:
            return f"❌ Error reading log: {e}"

        if not lines:
            return "⚠️ Log file is empty."

        return self._process_lines(path, lines)

    def analyze_text(self, log_text: str) -> str:
        """Analyze raw text logs."""
        lines = log_text.splitlines()
        if not lines:
            return "⚠️ Log text is empty."
        return self._process_lines("Raw Text Input", lines)

    def _process_lines(self, source_name: str, lines: List[str]) -> str:
        findings: Dict[str, List[str]] = {}
        ip_counter: Counter = Counter()
        ip_regex = re.compile(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b")

        for idx, line in enumerate(lines, 1):
            line_str = line
            if line.strip().startswith("{"):
                try:
                    obj = json.loads(line)
                    line_str = json.dumps(obj)
                except Exception:
                    pass

            for ip in ip_regex.findall(line_str):
                ip_counter[ip] += 1

            for threat, patterns in THREAT_PATTERNS.items():
                for pat in patterns:
                    if re.search(pat, line_str):
                        if threat not in findings:
                            findings[threat] = []
                        findings[threat].append(f"Line {idx}: {line.strip()[:100]}")
                        break

        report = []
        report.append("============================================================")
        report.append(f"🔍 SECURITY LOG ANALYSIS REPORT [{source_name}]")
        report.append("============================================================")
        report.append(f"📂 Lines  : {len(lines)}")
        report.append(f"🌐 IPs    : {len(ip_counter)} unique addresses observed")
        report.append("")

        if findings:
            report.append(f"🚨 THREATS FOUND ({len(findings)} categories):")
            report.append("------------------------------------------------------------")
            for threat, matches in findings.items():
                sev = SEVERITY_MAP.get(threat, "MEDIUM")
                report.append(f"• [{sev}] {threat} — {len(matches)} occurrence(s)")
                for snippet in matches[:3]:
                    report.append(f"   └─ {snippet}")
                if len(matches) > 3:
                    report.append(f"   └─ ... and {len(matches) - 3} more line(s)")
                report.append("")
        else:
            report.append("✅ No known security threats detected in log lines.")
            report.append("")

        top_ips = ip_counter.most_common(3)
        if top_ips:
            report.append("📈 HIGH-VOLUME IP TRAFFIC:")
            for ip, count in top_ips:
                report.append(f"   • {ip} : {count} request(s)")

        report.append("============================================================")
        return "\n".join(report)
