"""
Tests for security modules: password_checker.py and vulnerability.py
"""

import pytest
from security.password_checker import PasswordChecker
from security.vulnerability import VulnerabilityExplainer


# ─── Password Checker ─────────────────────────────────────────────────────────

@pytest.fixture
def checker():
    return PasswordChecker()


def test_weak_common_password(checker):
    result = checker.check("password")
    assert "WEAK" in result or "VERY WEAK" in result


def test_strong_password(checker):
    result = checker.check("T!r3$&k9mP@xQ2")
    assert "STRONG" in result or "VERY STRONG" in result


def test_short_password_flagged(checker):
    result = checker.check("abc")
    assert "short" in result.lower() or "WEAK" in result


def test_missing_uppercase_flagged(checker):
    result = checker.check("alllowercase1!")
    assert "uppercase" in result.lower()


def test_missing_special_flagged(checker):
    result = checker.check("NoSpecial123")
    assert "special" in result.lower()


def test_common_password_flagged(checker):
    result = checker.check("123456")
    assert "commonly" in result.lower() or "VERY WEAK" in result


def test_empty_password(checker):
    result = checker.check("")
    assert "❌" in result


def test_entropy_shown(checker):
    result = checker.check("MyPassw0rd!")
    assert "bits" in result


# ─── Vulnerability Explainer ──────────────────────────────────────────────────

@pytest.fixture
def explainer():
    return VulnerabilityExplainer()


def test_known_cve_log4shell(explainer):
    result = explainer.explain("CVE-2021-44228")
    assert "Log4Shell" in result
    assert "CRITICAL" in result


def test_known_cve_eternalblue(explainer):
    result = explainer.explain("CVE-2017-0144")
    assert "EternalBlue" in result


def test_vuln_type_sqli(explainer):
    result = explainer.explain("sqli")
    assert "SQL Injection" in result


def test_vuln_type_xss(explainer):
    result = explainer.explain("xss")
    assert "Cross-Site" in result


def test_vuln_type_buffer_overflow(explainer):
    result = explainer.explain("buffer overflow")
    assert "Buffer Overflow" in result


def test_unknown_cve_links(explainer):
    result = explainer.explain("CVE-1999-0001")
    assert "nvd.nist.gov" in result or "not in the local" in result


def test_unknown_term(explainer):
    result = explainer.explain("randomgarbage")
    assert "Could not find" in result or "Try" in result
