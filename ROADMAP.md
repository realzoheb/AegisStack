# 🗺 Hybrid AI Agent — Development Roadmap

This document tracks the full development roadmap from beginner to advanced implementation.

---

## ✅ Phase 1 — Foundations (Weeks 1–3)

**Goal:** Build a working local chatbot with file reading capability.

### Skills
- Python (advanced)
- Linux commands
- Git/GitHub
- Networking basics
- Cybersecurity fundamentals
- REST APIs

### Tasks
- [x] Install Ollama and pull local LLM
- [x] Build simple chatbot loop
- [x] Learn prompt engineering
- [x] Implement tool/function calling pattern
- [x] Build CLI interface

### Outputs
- [x] Local chatbot (`ui/cli.py`)
- [x] LLM brain (`agent/brain.py`)

---

## ✅ Phase 2 — Tool System (Week 4–5)

**Goal:** Build the Tool Controller with security, dev, and system tools.

### Security Tools
- [x] `log_analyzer()` — Parse auth/syslog/web logs
- [x] `nmap_parser()` — Parse and analyze nmap output
- [x] `vulnerability_explainer()` — CVE & vuln explanations
- [x] `password_checker()` — Password strength analysis

### Dev Tools
- [x] `code_generator()` — Code template generation
- [x] `code_reviewer()` — Static security analysis
- [x] `test_generator()` — Unit test generation
- [x] `project_scaffold()` — Project structure creation

### System Tools
- [x] `file_reader()` — Safe file reading
- [x] `command_runner()` — Whitelisted command execution

---

## ✅ Phase 3 — Cybersecurity Intelligence (Weeks 6–8)

**Goal:** Deep security analysis capabilities.

- [x] Log file threat detection (SSH brute force, SQLi, XSS, escalation)
- [x] IP frequency analysis
- [x] Nmap port risk assessment
- [x] CVE knowledge base
- [ ] **TODO:** Live CVE API integration (NVD/CIRCL API)
- [ ] **TODO:** Wireshark PCAP text export parsing
- [ ] **TODO:** PDF report generation

---

## ✅ Phase 4 — Software Development Intelligence (Weeks 9–11)

**Goal:** Powerful code assistance tools.

- [x] Multi-language static security analysis (Python, JS, C, SQL)
- [x] Code template generation
- [x] Unit test scaffolding
- [x] Project structure creation
- [ ] **TODO:** Refactoring suggestions (via LLM)
- [ ] **TODO:** Dependency vulnerability scanning (pip-audit, npm audit)
- [ ] **TODO:** SAST integration (Bandit, Semgrep)

---

## ✅ Phase 5 — Memory + Reasoning (Weeks 12–13)

**Goal:** Persistent agent memory.

- [x] Short-term memory (conversation context window)
- [x] Long-term memory (SQLite — messages, reports, notes)
- [ ] **TODO:** Vector memory (FAISS/ChromaDB for semantic search)
- [ ] **TODO:** Project knowledge base indexing
- [ ] **TODO:** Auto-summarization of long conversations

---

## 🔄 Phase 6 — Interface + Automation (Weeks 14–16)

**Goal:** Polish and expand interface options.

- [x] CLI with rich formatting
- [ ] **TODO:** Web dashboard (FastAPI + React/HTMX)
- [ ] **TODO:** File upload via web UI
- [ ] **TODO:** Report export (PDF, Markdown)
- [ ] **TODO:** Scheduled/automated log monitoring
- [ ] **TODO:** Alerting & notifications
- [ ] **TODO:** Voice interface (Whisper STT + TTS)

---

## 🔮 Future Ideas

- Docker containerization
- Multi-agent coordination
- Integration with threat intelligence feeds (Shodan, VirusTotal)
- Git repository security scanning
- Kubernetes/cloud security checks
- Real-time log tailing with streaming analysis

---

## 📊 Milestones (Portfolio Checkpoints)

| Milestone | Status | Description |
|-----------|--------|-------------|
| M1: Local chatbot | ✅ | LLM + CLI interface |
| M2: Security log analyzer | ✅ | Threat detection in logs |
| M3: Code review assistant | ✅ | Static security analysis |
| M4: Hybrid agent with tools | ✅ | Full tool routing |
| M5: Web UI + reports | 🔄 | In progress |
