"""
Log Analyzer - Parses system/auth/web logs for threats and anomalies.
"""

import re
import os
from collections import Counter
from datetime import datetime
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
        r"(?i)(\.\.\/|etc\/passwd|etc\/shadow|proc\/self)",
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
            return "⚠ Log file is empty."

        findings = self._scan_threats(lines)
        ip_stats = self._extract_ips(lines)
        summary = self._build_report(path, lines, findings, ip_stats)
        return summary

    def analyze_text(self, log_text: str) -> str:
        """Analyze raw log text (not a file)."""
        lines = log_text.splitlines(keepends=True)
        findings = self._scan_threats(lines)
        ip_stats = self._extract_ips(lines)
        return self._build_report("(raw input)", lines, findings, ip_stats)

    def _scan_threats(self, lines: List[str]) -> Dict[str, List[Tuple[int, str]]]:
        """Scan lines for threat patterns."""
        findings = {threat: [] for threat in THREAT_PATTERNS}
        for i, line in enumerate(lines, 1):
            for threat, patterns in THREAT_PATTERNS.items():
                for pattern in patterns:
                    if re.search(pattern, line):
                        findings[threat].append((i, line.strip()))
                        break
        return findings

    def _extract_ips(self, lines: List[str]) -> Counter:
        """Extract and count IP addresses from log lines."""
        ip_pattern = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
        ips = []
        for line in lines:
            ips.extend(ip_pattern.findall(line))
        return Counter(ips)

    def _build_report(self, source: str, lines: List[str], findings: dict, ip_stats: Counter) -> str:
        report = []
        report.append("=" * 60)
        report.append("🔍 SECURITY LOG ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"📂 Source : {source}")
        report.append(f"📋 Lines  : {len(lines):,}")
        report.append(f"🕐 Time   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # Threat summary
        active_threats = {k: v for k, v in findings.items() if v}
        if not active_threats:
            report.append("✅ No known threat patterns detected.")
        else:
            report.append(f"🚨 THREATS FOUND ({len(active_threats)} categories):")
            report.append("-" * 40)
            for threat, matches in active_threats.items():
                severity = SEVERITY_MAP.get(threat, "MEDIUM")
                icon = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟡"
                report.append(f"\n{icon} {threat} [{severity}] — {len(matches)} occurrence(s)")
                for lineno, line in matches[:3]:  # show up to 3 examples
                    report.append(f"   Line {lineno}: {line[:100]}")
                if len(matches) > 3:
                    report.append(f"   ... and {len(matches) - 3} more")

        # Top IPs
        if ip_stats:
            report.append("\n\n📡 TOP SOURCE IPs:")
            report.append("-" * 40)
            for ip, count in ip_stats.most_common(10):
                bar = "█" * min(count, 20)
                report.append(f"  {ip:<18} {count:>5}x  {bar}")

        # Recommendations
        report.append("\n\n💡 RECOMMENDATIONS:")
        report.append("-" * 40)
        if "SSH Brute Force" in active_threats:
            report.append("• Consider implementing fail2ban or IP blocking for repeated SSH failures.")
        if "Web Attack (SQLi)" in active_threats or "Web Attack (XSS)" in active_threats:
            report.append("• Review and sanitize all web inputs. Consider a WAF.")
        if "Privilege Escalation" in active_threats:
            report.append("• Audit SUID/SGID binaries. Review sudo rules.")
        if not active_threats:
            report.append("• Continue routine log monitoring.")

        report.append("\n" + "=" * 60)
        return "\n".join(report)
