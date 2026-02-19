# Contributing to Hybrid AI Agent

Thank you for your interest in contributing! This document outlines how to get started.

---

## 🚀 Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/hybrid-ai-agent.git
   cd hybrid-ai-agent
   ```
3. **Set up** your development environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
4. **Create a branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

---

## 🧪 Running Tests

Before submitting a PR, ensure all tests pass:

```bash
pytest tests/ -v
```

Check code style:

```bash
flake8 . --max-line-length=120
```

---

## 📋 Contribution Guidelines

### Code Style
- Follow PEP 8 with a max line length of 120 characters
- Use type hints for all function signatures
- Write docstrings for all public classes and methods
- Use descriptive variable names

### Security Rules
- **Never** add raw shell execution or `eval()`
- All new tools must be added to the whitelist/dispatch system
- Validate all user inputs before processing
- Add unit tests for security-sensitive code

### Adding a New Tool

1. Create a new module in `security/` or `dev/`
2. Write a class with a clear public method
3. Register it in `agent/tools.py`
4. Add documentation to the system prompt in `agent/brain.py`
5. Add a CLI shortcut in `ui/cli.py`
6. Write unit tests in `tests/`
7. Update `README.md`

### Commit Messages

Use conventional commit format:

```
feat: add CVE live API lookup
fix: handle empty log files gracefully
docs: update README with new commands
test: add tests for nmap parser
refactor: simplify tool dispatch logic
```

---

## 🐛 Reporting Bugs

Open an issue with:
- A clear description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Your OS, Python version, and Ollama model

---

## 💡 Suggesting Features

Open an issue labeled `enhancement` with:
- A clear description of the feature
- Use case / motivation
- Any implementation ideas

---

## 🔐 Reporting Security Issues

Please **do not** open public issues for security vulnerabilities.

Email: `security@yourproject.com` (or use GitHub private vulnerability reporting)

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.
