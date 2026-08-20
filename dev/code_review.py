"""
Code Reviewer - Reviews code for security vulnerabilities, bugs, and performance issues.
Enhanced for open-source PR submission:
- Preserves exact class interface: review_file(file_path) and review_code(code, filename).
- Adds AST-level Python code analysis (CWE-78, CWE-798, CWE-95) alongside pattern checks.
"""

import ast
import os
from typing import Dict, List, Any


class CodeReviewer:
    def review_file(self, file_path: str) -> str:
        """Review a code file for security vulnerabilities."""
        path = os.path.abspath(os.path.expanduser(file_path))

        if not os.path.exists(path):
            return f"❌ File not found: {path}"

        try:
            with open(path, "r", errors="replace") as f:
                code = f.read()
            return self.review_code(code, os.path.basename(path))
        except Exception as e:
            return f"❌ Error reading code file: {e}"

    def review_code(self, code: str, filename: str = "code_snippet") -> str:
        """Review raw code string for vulnerabilities."""
        findings = []

        # 1. AST Analysis for Python files
        if filename.endswith(".py") or "def " in code or "import " in code:
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                            findings.append(f"🔴 [CRITICAL] Line {node.lineno}: Dangerous dynamic code execution `{node.func.id}()` (CWE-95)")
                        elif isinstance(node.func, ast.Attribute) and node.func.attr in ("Popen", "run", "call"):
                            for kw in node.keywords:
                                if kw.arg == "shell" and getattr(kw.value, "value", None) is True:
                                    findings.append(f"🔴 [CRITICAL] Line {node.lineno}: OS Command Injection risk (`shell=True`) (CWE-78)")
                    elif isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name) and any(sk in target.id.lower() for sk in ("password", "api_key", "secret_key", "token")):
                                if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str) and len(node.value.value) > 4:
                                    findings.append(f"🟠 [HIGH] Line {node.lineno}: Potential hardcoded credential in variable `{target.id}` (CWE-798)")
            except SyntaxError:
                findings.append("⚠️ Syntax Warning: Code could not be fully parsed via AST.")

        # 2. Pattern Matching Heuristics
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            if "SELECT " in line.upper() and (" + " in line or " % " in line or ".format(" in line or f'f"' in line or f"f'" in line):
                findings.append(f"🔴 [CRITICAL] Line {idx}: Potential SQL Injection via string formatting")
            if "chmod 777" in line:
                findings.append(f"🟡 [MEDIUM] Line {idx}: Insecure overly permissive permissions `chmod 777`")

        # Build Report
        report = []
        report.append("============================================================")
        report.append(f"💻 CODE SECURITY REVIEW REPORT [{filename}]")
        report.append("============================================================")
        report.append(f"📋 Total Lines Reviewed: {len(lines)}")
        report.append("")

        if findings:
            report.append("🚨 SECURITY FINDINGS DETECTED:")
            report.append("------------------------------------------------------------")
            for finding in findings:
                report.append(f"  └─ {finding}")
            report.append("")
        else:
            report.append("✅ No security anti-patterns detected in source code.")
            report.append("")

        report.append("============================================================")
        return "\n".join(report)
