"""
Tests for dev/code_review.py
"""

import pytest
from dev.code_review import CodeReviewer, detect_language


@pytest.fixture
def reviewer():
    return CodeReviewer()


def test_detect_python_by_extension():
    assert detect_language("script.py", "") == "python"


def test_detect_js_by_extension():
    assert detect_language("app.js", "") == "javascript"


def test_detect_c_by_extension():
    assert detect_language("main.c", "") == "c"


def test_detect_python_by_content():
    code = "import os\ndef main():\n    pass"
    assert detect_language("", code) == "python"


def test_detects_hardcoded_password(reviewer):
    code = 'password = "super_secret_123"'
    result = reviewer.review(code, "test.py")
    assert "Hardcoded password" in result or "CRITICAL" in result


def test_detects_eval(reviewer):
    code = "eval(user_input)"
    result = reviewer.review(code, "test.py")
    assert "eval" in result.lower()


def test_detects_os_system(reviewer):
    code = "os.system(user_cmd)"
    result = reviewer.review(code, "test.py")
    assert "os.system" in result or "HIGH" in result


def test_detects_js_inner_html(reviewer):
    code = "element.innerHTML = userInput;"
    result = reviewer.review(code, "app.js")
    assert "innerHTML" in result or "XSS" in result


def test_detects_c_gets(reviewer):
    code = "#include <stdio.h>\ngets(buffer);"
    result = reviewer.review(code, "main.c")
    assert "gets" in result or "CRITICAL" in result


def test_clean_code_no_critical(reviewer):
    code = """
def greet(name: str) -> str:
    if not isinstance(name, str):
        raise ValueError("name must be a string")
    return f"Hello, {name}!"
"""
    result = reviewer.review(code, "greet.py")
    assert "REPORT" in result


def test_empty_code(reviewer):
    result = reviewer.review("", "test.py")
    assert "❌" in result


def test_hardcoded_api_key(reviewer):
    code = 'api_key = "sk-1234567890abcdef"'
    result = reviewer.review(code, "config.py")
    assert "API key" in result or "HIGH" in result
