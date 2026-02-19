# 🧠 Hybrid AI Agent

> A **local, private** DevSecOps AI assistant for cybersecurity analysis and software development — powered by Ollama and local LLMs.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Ollama](https://img.shields.io/badge/Powered%20by-Ollama-orange)

---

## 🎯 What Is This?

The Hybrid AI Agent is a local command-line AI assistant that combines:

- 🛡 **Cybersecurity intelligence** — log analysis, nmap parsing, CVE explanations, password checking
- 💻 **Software development assistance** — code generation, code review, test generation, project scaffolding
- ⚙ **System automation** — safe file reading, whitelisted command execution

Everything runs **100% locally**. No data leaves your machine.

---

## 🖥 Demo

```
🤖 You: analyze /var/log/auth.log

🛡 Agent:
============================================================
🔍 SECURITY LOG ANALYSIS REPORT
============================================================
📂 Source : /var/log/auth.log
📋 Lines  : 2,847
🕐 Time   : 2025-01-15 14:22:31

🚨 THREATS FOUND (2 categories):
----------------------------------------
🔴 SSH Brute Force [HIGH] — 134 occurrence(s)
   Line 412: Jan 15 14:01:22 sshd[1234]: Failed password for root from 192.168.1.100
   ...
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com) installed and running
- At least one model pulled (e.g., `ollama pull llama3`)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/divyanshakya966/DevSecOps-AI-Agent.git
cd hybrid-ai-agent

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start Ollama (in another terminal)
ollama serve

# 5. Pull a model
ollama pull llama3

# 6. Run the agent
python main.py
```

---

## 📋 Usage

### Interactive Mode

```bash
python main.py                    # Default (llama3)
python main.py --model codellama  # Use codellama for better code tasks
python main.py --no-memory        # Disable persistent memory
python main.py --verbose          # Debug mode
```

### One-Shot Commands

```bash
# Analyze a log file directly
python main.py --analyze-log /var/log/auth.log

# Review a code file
python main.py --review-code myapp.py
```

### CLI Commands

| Command | Description |
|---------|-------------|
| `help` | Show all commands |
| `tools` | List available tools |
| `analyze <file>` | Analyze a log file for threats |
| `nmap <file>` | Parse nmap scan output |
| `vuln <cve/name>` | Explain a CVE or vulnerability |
| `passcheck <pass>` | Check password strength |
| `review <file>` | Review code for security issues |
| `generate <lang>` | Generate code template |
| `tests <file>` | Generate unit tests |
| `scaffold <name> [type]` | Create a project structure |
| `read <file>` | Read a file |
| `run <command>` | Run a whitelisted command |
| `reset` | Clear conversation context |
| `memory` | Show memory statistics |
| `exit` | Exit the agent |

### Natural Language

You can also just chat naturally:

```
🤖 You: Can you explain what Log4Shell is and how to fix it?
🤖 You: Review this Python file for SQL injection vulnerabilities
🤖 You: Generate a Flask REST API template
🤖 You: What are the risks of leaving port 445 open?
```

---

## 🏗 Architecture

```
[CLI Interface]
      │
      ▼
[Agent Brain (LLM via Ollama)]
      │
      ▼
[Tool Controller]
 ┌────┴────┬────────────┐
[Security] [Dev]    [System]
   │         │         │
 logs      code     files/
 nmap     review   commands
 CVEs     tests
```

### Project Structure

```
hybrid-ai-agent/
├── main.py                    # Entry point
├── requirements.txt
├── README.md
│
├── agent/
│   ├── brain.py               # LLM orchestration
│   ├── tools.py               # Tool router
│   ├── memory.py              # SQLite persistence
│   └── system_tools.py        # File & command execution
│
├── security/
│   ├── log_analyzer.py        # Log threat detection
│   ├── nmap_parser.py         # Nmap output parsing
│   ├── vulnerability.py       # CVE/vuln explainer
│   └── password_checker.py    # Password strength
│
├── dev/
│   ├── code_review.py         # Static security analysis
│   ├── code_generator.py      # Code template generation
│   ├── test_generator.py      # Unit test generation
│   └── project_scaffold.py    # Project structure creation
│
├── ui/
│   └── cli.py                 # Interactive CLI
│
├── data/
│   └── memory.db              # SQLite memory (auto-created)
│
└── tests/
    └── ...
```

---

## 🛡 Security Design

The agent is built with security-first principles:

- ❌ **No raw shell execution** — commands are strictly whitelisted
- ✅ **Confirmation prompts** for destructive or sensitive actions
- ✅ **Local-only** — no data sent to external APIs
- ✅ **Sandboxed** — no arbitrary code execution from LLM output
- ✅ **Every action logged** to SQLite memory

### Whitelisted Commands

```python
ALLOWED_COMMANDS = {
    "ls", "pwd", "whoami", "id", "uname", "uptime", "df", "du",
    "free", "top", "ps", "netstat", "ss", "ifconfig", "ip", "ping",
    "date", "hostname", "env", "echo", "cat", "head", "tail", "wc",
    "find", "grep", "which", "whereis", "file", "stat"
}
```

---

## ⚙ Configuration

### Choosing Your Model

| Model | Best For | RAM Required |
|-------|----------|-------------|
| `llama3` | General purpose | ~8 GB |
| `codellama` | Code generation & review | ~8 GB |
| `mistral` | Fast, general purpose | ~4 GB |
| `llama3:70b` | Best quality | ~40 GB |

```bash
# Pull models
ollama pull llama3
ollama pull codellama
ollama pull mistral

# Use a specific model
python main.py --model codellama
```

### Environment Variables

```bash
# Optional .env configuration
OLLAMA_HOST=http://localhost:11434
LOG_LEVEL=INFO
```

---

## 🔌 Extending the Agent

### Add a New Tool

1. Create your tool module:

```python
# security/my_tool.py
class MyTool:
    def analyze(self, input: str) -> str:
        return f"Result: {input}"
```

2. Register it in `agent/tools.py`:

```python
from security.my_tool import MyTool

# In __init__:
self.tools["my_tool"] = MyTool()
self._dispatch["my_tool"] = ("my_tool", "analyze")
```

3. Update the system prompt in `agent/brain.py` to describe the new tool.

### Add Vector Memory

Install optional dependencies:

```bash
pip install faiss-cpu sentence-transformers
```

Then configure in `agent/memory.py` to use FAISS for semantic search over past interactions.

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run a specific test file
pytest tests/test_log_analyzer.py -v
```

---

## 🗺 Roadmap

See [ROADMAP.md](ROADMAP.md) for the full development roadmap.

- [x] Phase 1: Core agent + LLM integration
- [x] Phase 2: Tool system (security + dev + system)
- [x] Phase 3: Cybersecurity intelligence modules
- [x] Phase 4: Software development intelligence
- [x] Phase 5: Memory + persistence
- [ ] Phase 6: Web dashboard (FastAPI + React)
- [ ] Vector memory (FAISS/ChromaDB)
- [ ] Live CVE API integration
- [ ] Voice interface

---

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) first.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -m 'Add my feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## ⚠ Legal & Ethical Notice

This tool is intended for:
- Security professionals performing **authorized** penetration testing
- Developers reviewing their **own** code
- System administrators managing **their own** infrastructure

**Never use this tool against systems you do not own or have explicit permission to test.**

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.com) — local LLM runtime
- [Meta LLaMA](https://llama.meta.com) — language model
- [Rich](https://github.com/Textualize/rich) — terminal formatting
