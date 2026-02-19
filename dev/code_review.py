"""
Code Reviewer - Static analysis for security vulnerabilities and code quality.
"""

import re
from typing import List, Dict
from datetime import datetime


# Security vulnerability patterns by language
SECURITY_PATTERNS = {
    "all": [
        (r"(?i)password\s*=\s*['\"][^'\"]+['\"]", "CRITICAL", "Hardcoded password detected"),
        (r"(?i)secret\s*=\s*['\"][^'\"]+['\"]", "CRITICAL", "Hardcoded secret detected"),
        (r"(?i)api_?key\s*=\s*['\"][^'\"]+['\"]", "HIGH", "Hardcoded API key detected"),
        (r"(?i)token\s*=\s*['\"][^'\"]+['\"]", "HIGH", "Hardcoded token detected"),
        (r"TODO|FIXME|HACK|XXX", "LOW", "Developer note found - review before production"),
    ],
    "python": [
        (r"eval\s*\(", "CRITICAL", "eval() usage — potential code injection"),
        (r"exec\s*\(", "CRITICAL", "exec() usage — potential code injection"),
        (r"os\.system\s*\(", "HIGH", "os.system() — use subprocess with args list instead"),
        (r"subprocess\.call\(.+shell\s*=\s*True", "HIGH", "subprocess with shell=True — injection risk"),
        (r"pickle\.loads?\s*\(", "HIGH", "Unsafe deserialization with pickle"),
        (r"yaml\.load\s*\([^)]+\)", "HIGH", "yaml.load() without Loader — use yaml.safe_load()"),
        (r"input\s*\(", "MEDIUM", "input() in Python 2 is dangerous; verify Python version"),
        (r"hashlib\.(md5|sha1)\s*\(", "MEDIUM", "Weak hash algorithm (MD5/SHA1) for security purposes"),
        (r"random\.", "LOW", "Use secrets module instead of random for security tokens"),
        (r"assert\s+", "LOW", "Assertions can be disabled with -O flag, don't use for security checks"),
    ],
    "javascript": [
        (r"eval\s*\(", "CRITICAL", "eval() — code injection risk"),
        (r"innerHTML\s*=", "HIGH", "innerHTML assignment — XSS risk, use textContent or DOMPurify"),
        (r"document\.write\s*\(", "HIGH", "document.write() — XSS risk"),
        (r"\.html\s*\(", "HIGH", "jQuery .html() — XSS risk"),
        (r"dangerouslySetInnerHTML", "HIGH", "React dangerouslySetInnerHTML — ensure input is sanitized"),
        (r"localStorage\.(setItem|getItem)", "MEDIUM", "localStorage is accessible to all scripts on page"),
        (r"Math\.random\s*\(\)", "MEDIUM", "Math.random() not cryptographically secure"),
        (r"console\.log\s*\(", "LOW", "console.log in production — may leak sensitive data"),
    ],
    "c": [
        (r"\bgets\s*\(", "CRITICAL", "gets() — always causes buffer overflow, use fgets()"),
        (r"\bsprintf\s*\(", "HIGH", "sprintf() — buffer overflow risk, use snprintf()"),
        (r"\bstrcpy\s*\(", "HIGH", "strcpy() — buffer overflow risk, use strncpy()"),
        (r"\bstrcat\s*\(", "HIGH", "strcat() — buffer overflow risk, use strncat()"),
        (r"\bscanf\s*\([^,]+\"[^%]", "MEDIUM", "scanf without length limit — overflow risk"),
        (r"\bmalloc\s*\(", "LOW", "malloc() — check return value is not NULL"),
        (r"\bfree\s*\(", "LOW", "free() — verify no double-free or use-after-free"),
        (r"\bsystem\s*\(", "CRITICAL", "system() — command injection risk"),
    ],
    "sql": [
        (r"['\"]\s*\+\s*\w+\s*\+\s*['\"]", "CRITICAL", "String concatenation in SQL — injection risk"),
        (r"(?i)select\s+\*", "MEDIUM", "SELECT * — specify columns explicitly"),
        (r"(?i)--\s*$", "LOW", "SQL comment at end of line — verify not from user input"),
    ],
}

QUALITY_PATTERNS = [
    (r"def .+\((?!self)[^)]{80,}\)", "MEDIUM", "Function with many parameters — consider refactoring"),
    (r"^.{120,}$", "LOW", "Line exceeds 120 characters"),
    (r"except:\s*$", "MEDIUM", "Bare except clause — catch specific exceptions"),
    (r"except Exception:\s*$", "LOW", "Catching all exceptions — be more specific"),
    (r"pass\s*$", "LOW", "Empty pass block — intentional?"),
]


def detect_language(filename: str, code: str) -> str:
    """Detect language from filename or code content."""
    if filename:
        ext = filename.rsplit(".", 1)[-1].lower()
        mapping = {"py": "python", "js": "javascript", "ts": "javascript",
                   "c": "c", "cpp": "c", "h": "c", "sql": "sql", "php": "php"}
        if ext in mapping:
            return mapping[ext]
    # Fallback: content heuristics
    if "def " in code and "import " in code:
        return "python"
    if "function " in code or "const " in code or "var " in code:
        return "javascript"
    if "#include" in code:
        return "c"
    return "unknown"


class CodeReviewer:
    def review(self, code: str, filename: str = "") -> str:
        """Review code for security issues and quality problems."""
        if not code or not code.strip():
            return "❌ No code provided for review."

        language = detect_language(filename, code)
        lines = code.splitlines()

        findings = []
        findings.extend(self._scan_patterns(lines, SECURITY_PATTERNS.get("all", []), "security"))
        findings.extend(self._scan_patterns(lines, SECURITY_PATTERNS.get(language, []), "security"))
        findings.extend(self._scan_patterns(lines, QUALITY_PATTERNS, "quality"))

        return self._build_report(filename or "code", language, lines, findings)

    def _scan_patterns(self, lines: List[str], patterns: List, category: str) -> List[Dict]:
        results = []
        for lineno, line in enumerate(lines, 1):
            for pattern, severity, message in patterns:
                if re.search(pattern, line):
                    results.append({
                        "line": lineno,
                        "code": line.strip()[:100],
                        "severity": severity,
                        "message": message,
                        "category": category,
                    })
                    break  # One finding per line per scan
        return results

    def _build_report(self, filename: str, language: str, lines: List[str], findings: List[Dict]) -> str:
        security_findings = [f for f in findings if f["category"] == "security"]
        quality_findings = [f for f in findings if f["category"] == "quality"]

        # Sort by severity
        sev_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
        security_findings.sort(key=lambda f: sev_order.get(f["severity"], 4))

        report = [
            "=" * 60,
            "🔍 CODE REVIEW REPORT",
            "=" * 60,
            f"📄 File     : {filename}",
            f"🔤 Language : {language.capitalize()}",
            f"📋 Lines    : {len(lines)}",
            f"🕐 Reviewed : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            f"📊 SUMMARY: {len(security_findings)} security issue(s), {len(quality_findings)} quality note(s)",
            "",
        ]

        if not security_findings:
            report.append("✅ No security vulnerabilities detected by static analysis.")
        else:
            report.append("🚨 SECURITY ISSUES:")
            report.append("-" * 50)
            for f in security_findings:
                icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(f["severity"], "⚪")
                report.append(f"\n{icon} Line {f['line']} [{f['severity']}]: {f['message']}")
                report.append(f"   Code: {f['code']}")

        if quality_findings:
            report.append("\n\n📝 CODE QUALITY NOTES:")
            report.append("-" * 50)
            for f in quality_findings:
                report.append(f"\n🔵 Line {f['line']} [{f['severity']}]: {f['message']}")
                report.append(f"   Code: {f['code']}")

        report.append("\n\n⚠ DISCLAIMER:")
        report.append("This is static analysis only. Manual review recommended for")
        report.append("complex logic flaws, race conditions, and business logic issues.")
        report.append("=" * 60)
        return "\n".join(report)
