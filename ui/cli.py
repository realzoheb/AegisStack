"""
CLI Interface - Interactive command-line interface for the Hybrid AI Agent.
"""

import os
import sys
import readline  # enables arrow keys and history

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


BANNER = r"""
  _   _       _          _     _       _    ___                     _
 | | | |_   _| |__  _ __(_) __| |     / \  |_ _|     /\   __ _  __| |
 | |_| | | | | '_ \| '__| |/ _` |    / _ \  | |     /  \ / _` |/ _` |
 |  _  | |_| | |_) | |  | | (_| |   / ___ \ | |    / /\ \ (_| | (_| |
 |_| |_|\__, |_.__/|_|  |_|\__,_|  /_/   \_\___|  /_/  \_\__, |\__,_|
         |___/                                              |___/

  🛡  Cybersecurity + 💻 Dev + ⚙ Automation — Local & Private
"""

HELP_TEXT = """
╔══════════════════════════════════════════════════════╗
║              HYBRID AI AGENT — COMMANDS              ║
╠══════════════════════════════════════════════════════╣
║ General                                              ║
║   help         Show this help                        ║
║   tools        List all available tools              ║
║   clear        Clear the screen                      ║
║   reset        Reset conversation context            ║
║   memory       Show memory statistics                ║
║   exit / quit  Exit the agent                        ║
╠══════════════════════════════════════════════════════╣
║ Security Commands                                    ║
║   analyze <file>      Analyze a log file             ║
║   nmap <file|paste>   Parse nmap scan output         ║
║   vuln <name/cve>     Explain a vulnerability        ║
║   passcheck <pass>    Check password strength        ║
╠══════════════════════════════════════════════════════╣
║ Development Commands                                 ║
║   review <file>       Review code for issues         ║
║   generate <lang>     Generate code template         ║
║   tests <file>        Generate unit tests            ║
║   scaffold <name>     Create project structure       ║
╠══════════════════════════════════════════════════════╣
║ System Commands                                      ║
║   read <file>         Read a file                    ║
║   run <command>       Run whitelisted command        ║
╚══════════════════════════════════════════════════════╝

Or just chat naturally — the AI will route your request!
"""


class CLI:
    def __init__(self, brain):
        self.brain = brain
        self.console = Console() if HAS_RICH else None
        self.running = False

    def _print(self, text: str, style: str = ""):
        if HAS_RICH and self.console and style:
            self.console.print(text, style=style)
        else:
            print(text)

    def _print_banner(self):
        if HAS_RICH:
            self.console.print(BANNER, style="bold cyan")
            self.console.print(
                Panel(
                    f"Model: [bold]{self.brain.model}[/bold] | Memory: {'✅ ON' if self.brain.memory else '❌ OFF'}",
                    style="dim"
                )
            )
        else:
            print(BANNER)
            print(f"  Model: {self.brain.model} | Memory: {'ON' if self.brain.memory else 'OFF'}\n")

    def _handle_builtin(self, user_input: str) -> bool:
        """Handle built-in commands. Returns True if handled."""
        parts = user_input.strip().split(None, 1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in ("exit", "quit", "q"):
            self._print("\n👋 Goodbye!", "bold green")
            self.running = False
            return True

        if cmd == "help":
            print(HELP_TEXT)
            return True

        if cmd == "tools":
            print(self.brain.tools.list_tools())
            return True

        if cmd == "clear":
            os.system("clear" if os.name != "nt" else "cls")
            self._print_banner()
            return True

        if cmd == "reset":
            self.brain.reset_conversation()
            self._print("✅ Conversation context cleared.", "green")
            return True

        if cmd == "memory":
            if self.brain.memory:
                stats = self.brain.memory.stats()
                print(f"📊 Memory Stats:\n  Messages: {stats['messages']}\n  Reports: {stats['reports']}\n  Notes: {stats['notes']}\n  DB: {stats['db_path']}")
            else:
                self._print("⚠ Memory is disabled.", "yellow")
            return True

        # Direct security shortcuts
        if cmd == "analyze" and arg:
            print(self.brain.run_tool("log_analyzer", file_path=arg))
            return True

        if cmd == "vuln" and arg:
            print(self.brain.run_tool("vulnerability_explainer", cve_or_name=arg))
            return True

        if cmd == "passcheck" and arg:
            print(self.brain.run_tool("password_checker", password=arg))
            return True

        if cmd == "review" and arg:
            try:
                with open(arg, "r") as f:
                    code = f.read()
                print(self.brain.run_tool("code_reviewer", code=code, filename=arg))
            except FileNotFoundError:
                self._print(f"❌ File not found: {arg}", "red")
            return True

        if cmd == "read" and arg:
            print(self.brain.run_tool("file_reader", file_path=arg))
            return True

        if cmd == "run" and arg:
            print(self.brain.run_tool("command_runner", command=arg))
            return True

        if cmd == "scaffold":
            parts2 = arg.split() if arg else []
            name = parts2[0] if parts2 else ""
            ptype = parts2[1] if len(parts2) > 1 else "python-cli"
            if name:
                print(self.brain.run_tool("project_scaffold", name=name, project_type=ptype))
            else:
                self._print("Usage: scaffold <project-name> [type]", "yellow")
                print(self.brain.tools.tools["project_scaffold"].list_types())
            return True

        if cmd == "generate":
            parts2 = arg.split(None, 1) if arg else []
            lang = parts2[0] if parts2 else "python"
            desc = parts2[1] if len(parts2) > 1 else ""
            print(self.brain.run_tool("code_generator", language=lang, description=desc))
            return True

        if cmd == "tests" and arg:
            try:
                with open(arg, "r") as f:
                    code = f.read()
                print(self.brain.run_tool("test_generator", code=code, filename=arg))
            except FileNotFoundError:
                self._print(f"❌ File not found: {arg}", "red")
            return True

        if cmd == "nmap":
            if arg and os.path.exists(arg):
                print(self.brain.run_tool("nmap_parser", file_path=arg))
            elif arg:
                print(self.brain.run_tool("nmap_parser", raw_output=arg))
            else:
                self._print("Usage: nmap <file_or_paste_output>", "yellow")
            return True

        return False

    def run(self):
        """Start the interactive CLI loop."""
        self._print_banner()
        print("  Type 'help' for commands or just chat naturally.\n")
        self.running = True

        while self.running:
            try:
                user_input = input("🤖 You: ").strip()
            except (KeyboardInterrupt, EOFError):
                self._print("\n👋 Goodbye!", "bold green")
                break

            if not user_input:
                continue

            # Try built-in commands first
            if self._handle_builtin(user_input):
                continue

            # Route to LLM
            print()
            if HAS_RICH:
                with self.console.status("[bold cyan]Thinking...[/bold cyan]"):
                    response = self.brain.chat(user_input)
            else:
                print("⏳ Thinking...")
                response = self.brain.chat(user_input)

            print(f"\n🛡  Agent: {response}\n")
            print("-" * 60)
