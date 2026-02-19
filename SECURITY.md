# Security Policy

## ⚠ Ethical Use

This tool is designed for **authorized** security testing only.

- ✅ Testing your own systems
- ✅ Authorized penetration testing engagements
- ✅ CTF (Capture the Flag) competitions
- ❌ Unauthorized access to systems you do not own
- ❌ Illegal activity of any kind

## 🔐 Reporting a Vulnerability

If you discover a security vulnerability in this project, please **do not** open a public issue.

Instead:
1. Use GitHub's **Private Vulnerability Reporting** feature, or
2. Email the maintainer directly

Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Any suggested fixes

We aim to respond within **48 hours** and patch within **7 days** for critical issues.

## 🛡 Security Architecture

### What the agent can do
- Read files from your filesystem (with path validation)
- Run a strict whitelist of system commands
- Call local Ollama API

### What the agent cannot do
- Execute arbitrary shell commands
- Access the network (except local Ollama)
- Write files (unless explicitly added)
- Escalate privileges

### Data Privacy
- All conversations are stored locally in SQLite (`data/memory.db`)
- No data is transmitted to external servers
- The LLM runs entirely on your machine via Ollama
