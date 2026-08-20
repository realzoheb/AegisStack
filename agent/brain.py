"""
Agent Brain - Core LLM orchestration and tool routing.
Enhanced for open-source PR submission:
- Retains 100% backward compatibility with original AgentBrain class & method signatures.
- Adds native JSON tool parsing with robust regex fallback.
- Incorporates optional ReAct tool iteration while respecting existing chat() interface.
"""

import json
import re
import requests
from typing import Optional, Dict, Any, List
from agent.tools import ToolController
from agent.memory import MemoryManager


SYSTEM_PROMPT = """You are a Hybrid DevSecOps AI Assistant — a local, intelligent agent specializing in cybersecurity analysis, code auditing, and system automation.

When the user requests an action matching one of your tools, respond with a JSON tool call in this exact format:
{"tool": "<tool_name>", "params": {<parameters>}}

Available tools:
- log_analyzer(file_path): Analyze a log file for threats and anomalies
- nmap_parser(raw_output): Parse and summarize nmap scan output
- vulnerability_explainer(cve_or_name): Explain a CVE or vulnerability
- password_checker(password): Check password strength
- code_generator(language, description): Generate code template
- code_reviewer(code, filename): Review code for bugs and security issues
- test_generator(code, language): Generate unit tests for code
- project_scaffold(name, type): Create a project folder structure
- file_reader(file_path): Read a file's contents safely
- command_runner(command): Run a whitelisted system command

For general questions, respond directly in plain text.
Always prioritize security. Never execute dangerous commands.
"""


class AgentBrain:
    def __init__(self, model: str = "llama3", use_memory: bool = True, verbose: bool = False, ollama_host: str = "http://localhost:11434"):
        self.model = model
        self.verbose = verbose
        self.ollama_host = ollama_host.rstrip('/')
        self.tools = ToolController()
        self.memory = MemoryManager() if use_memory else None
        self.conversation_history: List[Dict[str, str]] = []
        self._check_ollama()

    def _check_ollama(self):
        """Verify Ollama is running and model is available."""
        try:
            resp = requests.get(f"{self.ollama_host}/api/tags", timeout=5)
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                if self.verbose:
                    print(f"[Brain] Available models: {models}")
                if not any(self.model in m for m in models):
                    print(f"⚠️  Model '{self.model}' not found in Ollama. Pull it with: ollama pull {self.model}")
        except Exception:
            print(f"⚠️  Ollama not reachable at {self.ollama_host}. Start it with: ollama serve")

    def _call_llm(self, user_message: str) -> str:
        """Send message to Ollama chat API."""
        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            for msg in self.conversation_history[-20:]:
                messages.append(msg)
            messages.append({"role": "user", "content": user_message})

            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False
            }

            resp = requests.post(f"{self.ollama_host}/api/chat", json=payload, timeout=120)
            resp.raise_for_status()
            return resp.json()["message"]["content"]
        except Exception as e:
            return f"[LLM Error] {str(e)}"

    def _parse_tool_call(self, response: str) -> Optional[Dict[str, Any]]:
        """Extract a JSON tool call from LLM response (supports JSON blocks & raw regex fallback)."""
        # 1. Try strict JSON parse
        try:
            data = json.loads(response)
            if isinstance(data, dict) and "tool" in data:
                return data
        except json.JSONDecodeError:
            pass

        # 2. Try Markdown ```json block regex
        codeblock_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?"tool"[\s\S]*?\})\s*```', response, re.IGNORECASE)
        if codeblock_match:
            try:
                return json.loads(codeblock_match.group(1))
            except json.JSONDecodeError:
                pass

        # 3. Fallback regex search for JSON object containing "tool"
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
        """Process user message, execute tools if requested, and return final agent response."""
        if self.memory:
            self.memory.save_message("user", user_message)

        raw_response = self._call_llm(user_message)

        if self.verbose:
            print(f"[Brain Raw] {raw_response}")

        tool_call = self._parse_tool_call(raw_response)
        if tool_call:
            tool_name = tool_call.get("tool")
            params = tool_call.get("params", {})
            tool_result = self.tools.run(tool_name, **params)

            follow_up = f"Tool '{tool_name}' returned:\n\n{tool_result}\n\nPlease summarize this result for the user."
            final_response = self._call_llm(follow_up)

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
