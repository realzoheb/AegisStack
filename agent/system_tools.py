"""
System Tools - Safe file reading and whitelisted command execution.
Fully compatible with unit test suite assertions.
"""

import os
import shlex
import subprocess
from typing import Set


# Security whitelist - only these commands can be run
ALLOWED_COMMANDS: Set[str] = {
    "ls", "pwd", "whoami", "id", "uname", "uptime", "df", "du",
    "free", "top", "ps", "netstat", "ss", "ifconfig", "ip", "ping",
    "date", "hostname", "env", "echo", "cat", "head", "tail", "wc",
    "find", "grep", "which", "whereis", "file", "stat"
}

FORBIDDEN_OPERATORS: Set[str] = {";", "&&", "||", "|", "`", "$(", ">", "<"}
MAX_FILE_SIZE_MB = 10


class SystemTools:
    def read_file(self, file_path: str) -> str:
        """Safely read a file and return its contents."""
        if not file_path or not file_path.strip():
            return "❌ File path is empty."

        path = os.path.abspath(os.path.expanduser(file_path))

        if not os.path.exists(path):
            return f"❌ File not found: {path}"

        if not os.path.isfile(path):
            return f"❌ Path is not a file: {path}"

        size_mb = os.path.getsize(path) / (1024 * 1024)
        if size_mb > MAX_FILE_SIZE_MB:
            return f"❌ File too large ({size_mb:.1f} MB). Max allowed: {MAX_FILE_SIZE_MB} MB."

        try:
            with open(path, "r", errors="replace") as f:
                content = f.read()
            lines = content.splitlines()
            preview = "\n".join(lines[:200])
            total_str = f"\n\n[... Truncated, showing first 200 lines of {len(lines)} total lines]" if len(lines) > 200 else ""
            return f"📄 File Contents ({path}):\n\n{preview}{total_str}"
        except Exception as e:
            return f"❌ Error reading file: {e}"

    def run_command(self, command: str) -> str:
        """Safely run a whitelisted system command without shell expansion."""
        if not command or not command.strip():
            return "❌ Command string is empty."

        # Check explicit shell injection operators
        for op in FORBIDDEN_OPERATORS:
            if op in command:
                return f"❌ Security restriction: Operator '{op}' is disallowed."

        try:
            tokens = shlex.split(command)
        except Exception as e:
            return f"❌ Command parsing error: {e}"

        if not tokens:
            return "❌ Command string is empty."

        base_cmd = tokens[0]
        if base_cmd not in ALLOWED_COMMANDS:
            return f"❌ Command '{base_cmd}' is not in the allowed whitelist."

        try:
            res = subprocess.run(
                tokens,
                capture_output=True,
                text=True,
                timeout=10,
                shell=False
            )
            output = res.stdout if res.returncode == 0 else f"STDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
            return f"✅ Command Result (`{' '.join(tokens)}`):\n\n{output[:3000]}"
        except subprocess.TimeoutExpired:
            return "⏱ Command timed out (10s limit)."
        except Exception as e:
            return f"❌ Error executing command: {e}"

    def list_allowed_commands(self) -> str:
        """List all whitelisted commands."""
        cmds = ", ".join(sorted(ALLOWED_COMMANDS))
        return f"Allowed commands ({len(ALLOWED_COMMANDS)}): {cmds}"
