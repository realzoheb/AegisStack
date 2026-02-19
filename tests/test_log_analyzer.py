"""
Tests for security/log_analyzer.py
"""

import pytest
import os
import tempfile
from security.log_analyzer import LogAnalyzer


@pytest.fixture
def analyzer():
    return LogAnalyzer()


@pytest.fixture
def ssh_brute_log():
    return """Jan 15 14:01:22 server sshd[1234]: Failed password for root from 192.168.1.100 port 22 ssh2
Jan 15 14:01:23 server sshd[1234]: Failed password for admin from 192.168.1.100 port 22 ssh2
Jan 15 14:01:24 server sshd[1234]: Invalid user test from 10.0.0.1 port 22 ssh2
Jan 15 14:01:25 server sshd[1234]: Accepted password for ubuntu from 192.168.1.50 port 22 ssh2
"""


@pytest.fixture
def clean_log():
    return """Jan 15 14:00:00 server systemd[1]: Started OpenSSH server daemon.
Jan 15 14:00:01 server sshd[1234]: Accepted publickey for ubuntu from 192.168.1.10 port 22
Jan 15 14:00:02 server sudo[5678]: ubuntu : TTY=pts/0 ; PWD=/home/ubuntu ; USER=root ; COMMAND=/bin/ls
"""


def test_analyze_ssh_brute_force(analyzer, ssh_brute_log):
    result = analyzer.analyze_text(ssh_brute_log)
    assert "SSH Brute Force" in result
    assert "192.168.1.100" in result


def test_analyze_clean_log_no_threats(analyzer, clean_log):
    result = analyzer.analyze_text(clean_log)
    assert "No known threat patterns detected" in result


def test_analyze_file_not_found(analyzer):
    result = analyzer.analyze(file_path="/nonexistent/path/file.log")
    assert "not found" in result.lower() or "❌" in result


def test_analyze_real_file(analyzer, tmp_path):
    log_file = tmp_path / "test.log"
    log_file.write_text("SELECT * FROM users WHERE id=1 OR 1=1\n")
    result = analyzer.analyze(str(log_file))
    assert "Web Attack" in result or "REPORT" in result


def test_ip_extraction(analyzer):
    log = "192.168.1.1 - - [15/Jan/2025] GET / HTTP/1.1 200\n" * 5
    result = analyzer.analyze_text(log)
    assert "192.168.1.1" in result


def test_xss_detection(analyzer):
    log = "GET /search?q=<script>alert(1)</script> HTTP/1.1"
    result = analyzer.analyze_text(log)
    assert "XSS" in result


def test_empty_log(analyzer):
    result = analyzer.analyze_text("")
    assert "empty" in result.lower() or "❌" in result or "⚠" in result
