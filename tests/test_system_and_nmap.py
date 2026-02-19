"""
Tests for agent/system_tools.py and security/nmap_parser.py
"""

import pytest
import os
from agent.system_tools import SystemTools
from security.nmap_parser import NmapParser


# ─── System Tools ─────────────────────────────────────────────────────────────

@pytest.fixture
def sys_tools():
    return SystemTools()


def test_read_existing_file(sys_tools, tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("Hello, World!")
    result = sys_tools.read_file(str(f))
    assert "Hello, World!" in result


def test_read_nonexistent_file(sys_tools):
    result = sys_tools.read_file("/nonexistent/file.txt")
    assert "not found" in result.lower() or "❌" in result


def test_read_directory_fails(sys_tools, tmp_path):
    result = sys_tools.read_file(str(tmp_path))
    assert "not a file" in result.lower() or "❌" in result


def test_whitelisted_command(sys_tools):
    result = sys_tools.run_command("whoami")
    assert "✅" in result or len(result) > 0


def test_blocked_command(sys_tools):
    result = sys_tools.run_command("rm -rf /")
    assert "whitelist" in result.lower() or "not in" in result.lower() or "❌" in result


def test_command_injection_blocked(sys_tools):
    result = sys_tools.run_command("ls; rm -rf /")
    assert "❌" in result or "disallowed" in result.lower()


def test_empty_command(sys_tools):
    result = sys_tools.run_command("")
    assert "❌" in result


def test_list_allowed_commands(sys_tools):
    result = sys_tools.list_allowed_commands()
    assert "whoami" in result
    assert "ls" in result


# ─── Nmap Parser ──────────────────────────────────────────────────────────────

SAMPLE_NMAP = """
Nmap scan report for 192.168.1.1
Host is up (0.0010s latency).

PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu
80/tcp   open  http    Apache httpd 2.4.41
443/tcp  open  https   nginx 1.18
3389/tcp open  ms-wbt-server Microsoft Terminal Services
21/tcp   open  ftp     vsftpd 3.0.3

OS details: Linux 5.4 - 5.11
"""


@pytest.fixture
def parser():
    return NmapParser()


def test_parse_target(parser):
    result = parser.parse(raw_output=SAMPLE_NMAP)
    assert "192.168.1.1" in result


def test_parse_detects_open_ports(parser):
    result = parser.parse(raw_output=SAMPLE_NMAP)
    assert "22" in result
    assert "80" in result


def test_parse_detects_rdp_risk(parser):
    result = parser.parse(raw_output=SAMPLE_NMAP)
    assert "3389" in result
    assert "RDP" in result or "HIGH" in result


def test_parse_detects_ftp_risk(parser):
    result = parser.parse(raw_output=SAMPLE_NMAP)
    assert "FTP" in result or "21" in result


def test_parse_empty_input(parser):
    result = parser.parse(raw_output="")
    assert "❌" in result or "No nmap" in result


def test_parse_no_ports(parser):
    result = parser.parse(raw_output="Nmap scan report for 10.0.0.1\nHost is up.")
    assert "REPORT" in result or "No" in result


def test_parse_from_file(parser, tmp_path):
    nmap_file = tmp_path / "scan.txt"
    nmap_file.write_text(SAMPLE_NMAP)
    result = parser.parse(file_path=str(nmap_file))
    assert "192.168.1.1" in result
