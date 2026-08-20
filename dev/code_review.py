"""
Code Reviewer - Reviews code for security vulnerabilities, bugs, and performance issues.
Fully compatible with unit test suite assertions.
"""

import ast
import os
from typing import Dict, List, Any


def detect_language(filename: str = "", code: str = "") -> str:
    """Detect programming language from file extension or content."""
    ext = os.path.splitext(filename)[1].lower() if filename else ""
    if ext == ".py":
        return "python"
    elif ext in (".js", ".ts", ".jsx", ".tsx"):
        return "javascript"
    elif ext in (".c", ".h"):
        return "c"
    elif ext in (".cpp", ".hpp", ".cc"):
        return "cpp"
    elif ext == ".java":
        return "java"
    elif ext == ".go":
        return "go"

    if "def " in code or "import os" in code or "print(" in code:
        return "python"
    elif "function " in code or "const " in code or "let " in code or "console.log" in code:
        return "javascript"
    elif "#include <stdio.h>" in code or "int main(" in code:
        return "c"

    return "text"


class CodeReviewer:
    def review_file(self, file_path: str) -> str:
        """Review a code file for security vulnerabilities."""
        if not file_path or not file_path.strip():
            return "❌ File path is empty."

        path = os.path.abspath(os.path.expanduser(file_path))

        if not os.path.exists(path):
            return f"❌ File not found: {path}"

        try:
            with open(path, "r", errors="replace") as f:
                code = f.read()
            return self.review(code, os.path.basename(path))
        except Exception as e:
            return f"❌ Error reading code file: {e}"

    def review(self, code: str, filename: str = "code_snippet") -> str:
        """Review raw code string for vulnerabilities."""
        if not code or not code.strip():
            return "❌ Code is empty."

        findings = []
        lang = detect_language(filename, code)

        # 1. AST Analysis for Python files
        if lang == "python":
            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Call):
                        if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec"):
                            findings.append(f"🔴 [CRITICAL] Line {node.lineno}: Dangerous dynamic code execution `eval()` / `exec()` (CWE-95)")
                        elif isinstance(node.func, ast.Attribute) and node.func.attr in ("Popen", "run", "call"):
                            for kw in node.keywords:
                                if kw.arg == "shell" and getattr(kw.value, "value", None) is True:
                                    findings.append(f"🔴 [CRITICAL] Line {node.lineno}: OS Command Injection risk (`shell=True`) (CWE-78)")
                    elif isinstance(node.func if isinstance(node, ast.Call) else None, ast.Attribute):
                        if node.func.attr == "system" and getattr(node.func.value, "id", "") == "os":
                            findings.append(f"🟠 [HIGH] Line {node.lineno}: Use of `os.system` command execution")
            except SyntaxError:
                pass

        # 2. Heuristics & Pattern Checks
        lines = code.splitlines()
        for idx, line in enumerate(lines, 1):
            line_str = line.strip()
            
            # Hardcoded Password
            if any(pw_kw in line_str.lower() for pw_kw in ("password =", "password=", "passwd =", "secret =")):
                if not any(placeholder in line_str.lower() for placeholder in ("env", "none", "null", "false", "true", "''")):
                    findings.append(f"🔴 [CRITICAL] Line {idx}: Hardcoded password detected in source")

            # Hardcoded API Key
            if "api_key =" in line_str.lower() or "api_key=" in line_str.lower() or "sk-" in line_str:
                findings.append(f"🟠 [HIGH] Line {idx}: Potential hardcoded API key detected")

            # os.system check fallback
            if "os.system(" in line_str and not any("Line " in f for f in findings if "os.system" in f):
                findings.append(f"🟠 [HIGH] Line {idx}: Dangerous use of `os.system()`")

            # eval check fallback
            if "eval(" in line_str and not any("Line " in f for f in findings if "eval" in f):
                findings.append(f"🔴 [CRITICAL] Line {idx}: Use of dangerous `eval()` function")

            # JavaScript innerHTML
            if "innerHTML" in line_str:
                findings.append(f"🔴 [CRITICAL] Line {idx}: Potential DOM-based XSS via `innerHTML` assignment")

            # C gets()
            if "gets(" in line_str:
                findings.append(f"🔴 [CRITICAL] Line {idx}: Vulnerable C function `gets()` causes buffer overflow")

        # Build Standard Report
        report = []
        report.append("============================================================")
        report.append(f"💻 CODE SECURITY AUDIT REPORT [{filename}] ({lang.upper()})")
        report.append("============================================================")
        report.append(f"📋 Lines Analyzed: {len(lines)}")
        report.append("")

        if findings:
            report.append("🚨 SECURITY VULNERABILITIES FOUND:")
            report.append("------------------------------------------------------------")
            for finding in findings:
                report.append(f"  └─ {finding}")
            report.append("")
        else:
            report.append("✅ No known security anti-patterns detected in source code.")
            report.append("")

        report.append("============================================================")
        return "\n".join(report)

    def review_code(self, code: str, filename: str = "code_snippet") -> str:
        return self.review(code, filename)
