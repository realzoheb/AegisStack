"""
Nmap Parser - Parse and analyze nmap scan output for security insights.
"""

import re
from typing import List, Dict, Tuple
from datetime import datetime


# Port risk database
PORT_RISK = {
    21: ("FTP", "HIGH", "Clear-text protocol. Use SFTP instead."),
    22: ("SSH", "LOW", "Secure shell - verify key-based auth is enforced."),
    23: ("Telnet", "CRITICAL", "Unencrypted. Disable immediately."),
    25: ("SMTP", "MEDIUM", "Check relay settings to prevent spam abuse."),
    53: ("DNS", "MEDIUM", "Verify DNS is not open resolver."),
    80: ("HTTP", "MEDIUM", "Consider redirecting to HTTPS."),
    110: ("POP3", "HIGH", "Clear-text mail protocol."),
    111: ("RPCbind", "HIGH", "Often exploited. Restrict access."),
    135: ("MS-RPC", "HIGH", "Windows RPC — ensure properly firewalled."),
    139: ("NetBIOS", "HIGH", "Legacy Windows file sharing. Restrict."),
    143: ("IMAP", "HIGH", "Clear-text mail. Use IMAPS instead."),
    443: ("HTTPS", "LOW", "Verify SSL/TLS config and certificate."),
    445: ("SMB", "CRITICAL", "EternalBlue vulnerability vector. Patch and restrict."),
    1433: ("MSSQL", "HIGH", "DB exposed. Restrict network access."),
    1521: ("Oracle DB", "HIGH", "DB exposed. Restrict network access."),
    3306: ("MySQL", "HIGH", "DB exposed. Restrict network access."),
    3389: ("RDP", "HIGH", "Brute force and BlueKeep risk. Restrict access."),
    4444: ("Metasploit", "CRITICAL", "Default Metasploit listener port. Investigate."),
    5432: ("PostgreSQL", "HIGH", "DB exposed. Restrict network access."),
    5900: ("VNC", "HIGH", "Weak auth common. Restrict or use SSH tunnel."),
    6379: ("Redis", "CRITICAL", "Often misconfigured with no auth. Restrict immediately."),
    8080: ("HTTP-Alt", "MEDIUM", "Alternate web port. Check for admin panels."),
    8443: ("HTTPS-Alt", "LOW", "Alternate HTTPS port."),
    27017: ("MongoDB", "CRITICAL", "Often exposed with no auth. Restrict immediately."),
}


class NmapParser:
    def parse(self, raw_output: str = None, file_path: str = None) -> str:
        """Parse nmap scan output and return a structured security summary."""
        if file_path:
            try:
                with open(file_path, "r") as f:
                    raw_output = f.read()
            except Exception as e:
                return f"❌ Error reading nmap file: {e}"

        if not raw_output:
            return "❌ No nmap output provided. Pass raw_output= or file_path=."

        target = self._extract_target(raw_output)
        open_ports = self._extract_ports(raw_output)
        os_info = self._extract_os(raw_output)
        risk_analysis = self._analyze_risks(open_ports)

        return self._build_report(target, open_ports, os_info, risk_analysis)

    def _extract_target(self, text: str) -> str:
        match = re.search(r"Nmap scan report for (.+)", text)
        return match.group(1).strip() if match else "Unknown target"

    def _extract_ports(self, text: str) -> List[Dict]:
        ports = []
        pattern = re.compile(r"(\d+)/(tcp|udp)\s+(open|filtered|closed)\s+(\S+)(?:\s+(.*))?")
        for match in pattern.finditer(text):
            port_num = int(match.group(1))
            ports.append({
                "port": port_num,
                "protocol": match.group(2),
                "state": match.group(3),
                "service": match.group(4),
                "version": (match.group(5) or "").strip(),
            })
        return ports

    def _extract_os(self, text: str) -> str:
        match = re.search(r"OS details?: (.+)", text)
        if match:
            return match.group(1).strip()
        match = re.search(r"Aggressive OS guesses?: (.+)", text)
        if match:
            return match.group(1).split(",")[0].strip() + " (guess)"
        return "Unknown"

    def _analyze_risks(self, ports: List[Dict]) -> List[Dict]:
        risks = []
        for p in ports:
            if p["state"] != "open":
                continue
            port_num = p["port"]
            if port_num in PORT_RISK:
                service, severity, note = PORT_RISK[port_num]
                risks.append({
                    "port": port_num,
                    "service": service,
                    "severity": severity,
                    "note": note,
                })
            else:
                risks.append({
                    "port": port_num,
                    "service": p["service"],
                    "severity": "UNKNOWN",
                    "note": "Unknown service — investigate manually.",
                })
        # Sort by severity
        order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "UNKNOWN": 4}
        risks.sort(key=lambda r: order.get(r["severity"], 5))
        return risks

    def _build_report(self, target: str, ports: List[Dict], os_info: str, risks: List[Dict]) -> str:
        report = []
        report.append("=" * 60)
        report.append("🗺  NMAP SCAN ANALYSIS REPORT")
        report.append("=" * 60)
        report.append(f"🎯 Target    : {target}")
        report.append(f"💻 OS        : {os_info}")
        report.append(f"🔓 Open Ports: {sum(1 for p in ports if p['state'] == 'open')}")
        report.append(f"🕐 Analyzed  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        if not ports:
            report.append("ℹ No open ports found (or output not recognized).")
        else:
            report.append("📋 OPEN PORTS:")
            report.append("-" * 50)
            report.append(f"{'PORT':<10} {'PROTO':<8} {'STATE':<10} {'SERVICE':<15} VERSION")
            report.append("-" * 50)
            for p in ports:
                if p["state"] == "open":
                    report.append(f"{p['port']:<10} {p['protocol']:<8} {p['state']:<10} {p['service']:<15} {p['version'][:20]}")

        if risks:
            report.append("\n\n🚨 RISK ANALYSIS:")
            report.append("-" * 50)
            for r in risks:
                sev = r["severity"]
                icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(sev, "⚪")
                report.append(f"\n{icon} Port {r['port']} — {r['service']} [{sev}]")
                report.append(f"   ⚠ {r['note']}")

        report.append("\n\n💡 GENERAL RECOMMENDATIONS:")
        report.append("-" * 50)
        critical = [r for r in risks if r["severity"] == "CRITICAL"]
        if critical:
            report.append(f"• URGENT: {len(critical)} critical port(s) require immediate attention.")
        report.append("• Close all ports not required for normal operations.")
        report.append("• Ensure all services are patched and up to date.")
        report.append("• Use a firewall to restrict access by source IP where possible.")

        report.append("\n" + "=" * 60)
        return "\n".join(report)
