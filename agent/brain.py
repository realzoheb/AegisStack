"""
Agent Brain - Core LLM orchestration and tool routing.
"""

import json
import re
from typing import Optional
from agent.tools import ToolController
from agent.memory import MemoryManager


SYSTEM_PROMPT = """You are a Hybrid DevSecOps AI Assistant — a local, intelligent agent that specializes in:
1. Cybersecurity: analyzing logs, parsing scan results, explaining vulnerabilities, and generating security reports.
2. Software Development: generating code, reviewing code for bugs and security issues, creating unit tests.
3. System Automation: reading files, summarizing outputs, running whitelisted commands safely.

When the user requests an action that matches one of your tools, respond with a JSON tool call in this format:
{"tool": "<tool_name>", "params": {<parameters>}}

Available tools:
- log_analyzer(file_path): Analyze a log file for threats and anomalies
- nmap_parser(raw_output): Parse and summarize nmap scan output
- vulnerability_explainer(cve_or_name): Explain a CVE or vulnerability
- password_checker(password): Check password strength
- code_generator(language, description): Generate code
- code_reviewer(code, filename): Review code for bugs and security issues
- test_generator(code, language): Generate unit tests for code
- project_scaffold(name, type): Create a project folder structure
- file_reader(file_path): Read a file's contents
- command_runner(command): Run a whitelisted system command

For general questions or explanations, respond in plain text.
Always prioritize security. Never execute dangerous commands.
"""


class AgentBrain:
    def __init__(self, model: str = "llama3", use_memory: bool = True, verbose: bool = False):
        self.model = model
        self.verbose = verbose
        self.tools = ToolController()
        self.memory = MemoryManager() if use_memory else None
        self.conversation_history = []
        self._check_ollama()

    def _check_ollama(self):
        """Verify Ollama is running and model is available."""
        try:
            import requests
            resp = requests.get("http://localhost:11434/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                if self.verbose:
                    print(f"[Brain] Available models: {models}")
                if not any(self.model in m for m in models):
                    print(f"⚠  Model '{self.model}' not found. Pull it with: ollama pull {self.model}")
        except Exception:
            print("⚠  Ollama not reachable at http://localhost:11434. Start it with: ollama serve")

    def _call_llm(self, user_message: str) -> str:
        """Send message to Ollama and get a response."""
        try:
            import requests

            # Build messages with history
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]

            # Add recent conversation history (last 10 exchanges)
            for msg in self.conversation_history[-20:]:
                messages.append(msg)

            messages.append({"role": "user", "content": user_message})

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
            }

            resp = requests.post("http://localhost:11434/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            return resp.json()["message"]["content"]

        except Exception as e:
            return f"[LLM Error] {str(e)}"

    def _parse_tool_call(self, response: str) -> Optional[dict]:
        """Extract a JSON tool call from the LLM response."""
        # Try to find JSON block
        match = re.search(r'\{[^{}]*"tool"[^{}]*\}', response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
        return None

    def run_tool(self, tool_name: str, **params) -> str:
        """Directly invoke a tool by name."""
        return self.tools.run(tool_name, **params)

    def chat(self, user_message: str) -> str:
        """Process a user message and return the agent's response."""
        # Save to memory
        if self.memory:
            self.memory.save_message("user", user_message)

        # Get LLM response
        raw_response = self._call_llm(user_message)

        if self.verbose:
            print(f"[Brain Raw] {raw_response}")

        # Check for tool call
        tool_call = self._parse_tool_call(raw_response)
        if tool_call:
            tool_name = tool_call.get("tool")
            params = tool_call.get("params", {})
            tool_result = self.tools.run(tool_name, **params)

            # Send tool result back to LLM for a natural response
            follow_up = f"Tool '{tool_name}' returned:\n\n{tool_result}\n\nPlease summarize this result for the user."
            final_response = self._call_llm(follow_up)

            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": final_response})

            if self.memory:
                self.memory.save_message("assistant", final_response)

            return final_response

        # Plain text response
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": raw_response})

        if self.memory:
            self.memory.save_message("assistant", raw_response)

        return raw_response

    def reset_conversation(self):
        """Clear current conversation context."""
        self.conversation_history = []
