"""
System Tools - Safe file reading and whitelisted command execution.
"""

import os
import subprocess
from typing import Optional


# Security whitelist - only these commands can be run
ALLOWED_COMMANDS = {
    "ls", "pwd", "whoami", "id", "uname", "uptime", "df", "du",
    "free", "top", "ps", "netstat", "ss", "ifconfig", "ip", "ping",
    "date", "hostname", "env", "echo", "cat", "head", "tail", "wc",
    "find", "grep", "which", "whereis", "file", "stat"
}

MAX_FILE_SIZE_MB = 10


class SystemTools:
    def read_file(self, file_path: str) -> str:
        """Safely read a file and return its contents."""
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
            suffix = f"\n\n[... {len(lines) - 200} more lines not shown ...]" if len(lines) > 200 else ""
            return f"📄 File: {path}\n\n{preview}{suffix}"
        except Exception as e:
            return f"❌ Error reading file: {e}"

    def run_command(self, command: str) -> str:
        """Run a whitelisted system command safely."""
        if not command or not command.strip():
            return "❌ No command provided."

        # Extract base command
        base_cmd = command.strip().split()[0]

        if base_cmd not in ALLOWED_COMMANDS:
            return (
                f"❌ Command '{base_cmd}' is not in the whitelist.\n"
                f"Allowed commands: {', '.join(sorted(ALLOWED_COMMANDS))}"
            )

        # Block dangerous characters
        dangerous = ["|", ";", "&", ">", "<", "`", "$", "(", ")", "{", "}", "\\"]
        for char in dangerous:
            if char in command:
                return f"❌ Command contains disallowed character: '{char}'"

        try:
            result = subprocess.run(
                command.split(),
                capture_output=True,
                text=True,
                timeout=15
            )
            output = result.stdout.strip()
            error = result.stderr.strip()
            if error:
                return f"⚠ Command completed with warnings:\n{error}\n\nOutput:\n{output}"
            return f"✅ $ {command}\n\n{output}" if output else f"✅ $ {command}\n(no output)"
        except subprocess.TimeoutExpired:
            return "❌ Command timed out (15s limit)."
        except Exception as e:
            return f"❌ Failed to run command: {e}"

    def list_allowed_commands(self) -> str:
        return f"🔒 Whitelisted commands ({len(ALLOWED_COMMANDS)}):\n" + ", ".join(sorted(ALLOWED_COMMANDS))
