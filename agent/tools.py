"""
Tool Controller - Routes tool calls to the appropriate modules.
"""

from security.log_analyzer import LogAnalyzer
from security.nmap_parser import NmapParser
from security.vulnerability import VulnerabilityExplainer
from security.password_checker import PasswordChecker
from dev.code_review import CodeReviewer
from dev.code_generator import CodeGenerator
from dev.test_generator import TestGenerator
from dev.project_scaffold import ProjectScaffold
from agent.system_tools import SystemTools


class ToolController:
    def __init__(self):
        self.tools = {
            "log_analyzer": LogAnalyzer(),
            "nmap_parser": NmapParser(),
            "vulnerability_explainer": VulnerabilityExplainer(),
            "password_checker": PasswordChecker(),
            "code_reviewer": CodeReviewer(),
            "code_generator": CodeGenerator(),
            "test_generator": TestGenerator(),
            "project_scaffold": ProjectScaffold(),
            "system": SystemTools(),
        }

        # Flat dispatch map
        self._dispatch = {
            "log_analyzer": ("log_analyzer", "analyze"),
            "nmap_parser": ("nmap_parser", "parse"),
            "vulnerability_explainer": ("vulnerability_explainer", "explain"),
            "password_checker": ("password_checker", "check"),
            "code_reviewer": ("code_reviewer", "review"),
            "code_generator": ("code_generator", "generate"),
            "test_generator": ("test_generator", "generate"),
            "project_scaffold": ("project_scaffold", "create"),
            "file_reader": ("system", "read_file"),
            "command_runner": ("system", "run_command"),
        }

    def run(self, tool_name: str, **params) -> str:
        """Execute a tool by name with given parameters."""
        if tool_name not in self._dispatch:
            return f"❌ Unknown tool: '{tool_name}'. Available: {list(self._dispatch.keys())}"

        obj_key, method_name = self._dispatch[tool_name]
        obj = self.tools[obj_key]
        method = getattr(obj, method_name, None)

        if not method:
            return f"❌ Tool '{tool_name}' has no method '{method_name}'."

        try:
            return method(**params)
        except TypeError as e:
            return f"❌ Tool '{tool_name}' parameter error: {e}"
        except Exception as e:
            return f"❌ Tool '{tool_name}' failed: {e}"

    def list_tools(self) -> str:
        """Return a human-readable list of available tools."""
        lines = ["🔧 Available Tools:\n"]
        for name in self._dispatch:
            lines.append(f"  • {name}")
        return "\n".join(lines)
