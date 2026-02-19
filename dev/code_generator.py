"""
Code Generator - Generate code templates and boilerplate for common patterns.
"""

from datetime import datetime

TEMPLATES = {
    "python": {
        "cli": '''#!/usr/bin/env python3
"""
{description}
"""

import argparse
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="{description}")
    parser.add_argument("input", help="Input value")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    return parser.parse_args()


def main():
    args = parse_args()
    if args.verbose:
        print(f"[*] Processing: {{args.input}}")
    # TODO: implement main logic
    print(f"Result: {{args.input}}")


if __name__ == "__main__":
    main()
''',
        "flask_api": '''#!/usr/bin/env python3
"""
{description}
"""

from flask import Flask, request, jsonify
from functools import wraps
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)


def require_api_key(f):
    """Simple API key authentication decorator."""
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-Key")
        if key != "your-secret-key":  # TODO: load from env
            return jsonify({{"error": "Unauthorized"}}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/health", methods=["GET"])
def health():
    return jsonify({{"status": "ok"}})


@app.route("/api/v1/example", methods=["POST"])
@require_api_key
def example():
    data = request.get_json()
    if not data:
        return jsonify({{"error": "No JSON payload"}}), 400
    # TODO: process data
    return jsonify({{"result": data}}), 200


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
''',
        "class": '''#!/usr/bin/env python3
"""
{description}
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class {classname}:
    """
    {description}
    """

    def __init__(self, config: Optional[dict] = None):
        self.config = config or {{}}
        self._initialized = False
        self._setup()

    def _setup(self):
        """Initialize internal state."""
        # TODO: setup logic
        self._initialized = True
        logger.info(f"{{self.__class__.__name__}} initialized")

    def process(self, data):
        """Main processing method.
        
        Args:
            data: Input data to process
            
        Returns:
            Processed result
            
        Raises:
            ValueError: If data is invalid
        """
        if not self._initialized:
            raise RuntimeError("Not initialized")
        if data is None:
            raise ValueError("Data cannot be None")
        # TODO: implement
        return data

    def __repr__(self):
        return f"{{self.__class__.__name__}}(config={{self.config}})"
''',
        "scanner": '''#!/usr/bin/env python3
"""
{description}
"""

import socket
import concurrent.futures
from typing import List


def scan_port(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is open."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (socket.timeout, ConnectionRefusedError, OSError):
        return False


def scan_ports(host: str, ports: List[int], max_workers: int = 100) -> dict:
    """Scan multiple ports concurrently."""
    results = {{}}
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_port = {{executor.submit(scan_port, host, p): p for p in ports}}
        for future in concurrent.futures.as_completed(future_to_port):
            port = future_to_port[future]
            results[port] = future.result()
    return results


if __name__ == "__main__":
    host = "127.0.0.1"
    common_ports = [21, 22, 23, 25, 53, 80, 443, 3306, 5432, 8080]
    print(f"Scanning {{host}}...")
    open_ports = [p for p, is_open in scan_ports(host, common_ports).items() if is_open]
    print(f"Open ports: {{open_ports}}")
''',
    },
    "javascript": {
        "express_api": '''/**
 * {description}
 * Express.js REST API
 */

const express = require('express');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 3000;

// Security middleware
app.use(helmet());
app.use(express.json({{ limit: '10kb' }}));

// Rate limiting
const limiter = rateLimit({{
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100
}});
app.use('/api/', limiter);

// Health check
app.get('/health', (req, res) => {{
    res.json({{ status: 'ok', timestamp: new Date().toISOString() }});
}});

// Example route
app.post('/api/v1/process', (req, res) => {{
    const {{ data }} = req.body;
    if (!data) return res.status(400).json({{ error: 'data is required' }});
    // TODO: implement logic
    res.json({{ result: data }});
}});

// Error handler
app.use((err, req, res, next) => {{
    console.error(err.stack);
    res.status(500).json({{ error: 'Internal server error' }});
}});

app.listen(PORT, '127.0.0.1', () => {{
    console.log(`Server running on http://127.0.0.1:${{PORT}}`);
}});
''',
    },
    "c": {
        "basic": '''/**
 * {description}
 * Generated: {date}
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define BUFFER_SIZE 1024
#define MAX_INPUT   512

/**
 * Process input safely
 */
int process_input(const char *input, char *output, size_t out_size) {{
    if (!input || !output || out_size == 0) {{
        return -1;
    }}
    // TODO: implement processing
    strncpy(output, input, out_size - 1);
    output[out_size - 1] = '\\0';
    return 0;
}}

int main(int argc, char *argv[]) {{
    if (argc < 2) {{
        fprintf(stderr, "Usage: %s <input>\\n", argv[0]);
        return EXIT_FAILURE;
    }}

    char output[BUFFER_SIZE];
    if (process_input(argv[1], output, sizeof(output)) != 0) {{
        fprintf(stderr, "Error processing input\\n");
        return EXIT_FAILURE;
    }}

    printf("Result: %s\\n", output);
    return EXIT_SUCCESS;
}}
''',
    },
}


class CodeGenerator:
    def generate(self, language: str, description: str = "", template_type: str = "basic") -> str:
        """Generate code for a given language and template type."""
        lang = language.lower()
        lang_templates = TEMPLATES.get(lang)

        if not lang_templates:
            available = list(TEMPLATES.keys())
            return f"❌ Language '{language}' not supported.\nAvailable: {', '.join(available)}"

        # Auto-select template
        template_key = template_type.lower()
        if template_key not in lang_templates:
            template_key = list(lang_templates.keys())[0]

        template = lang_templates[template_key]

        # Fill in template variables
        classname = "".join(w.capitalize() for w in description.split()[:3]) or "MyClass"
        code = template.format(
            description=description or f"{lang.capitalize()} {template_key} template",
            classname=classname,
            date=datetime.now().strftime("%Y-%m-%d"),
        )

        return (
            f"```{lang}\n{code}\n```\n\n"
            f"💡 Template: {lang.capitalize()} / {template_key}\n"
            f"🗒 Description: {description or '(none)'}\n"
            f"📝 Remember to replace TODO sections with your logic."
        )

    def list_templates(self) -> str:
        lines = ["📋 Available Code Templates:\n"]
        for lang, templates in TEMPLATES.items():
            lines.append(f"  {lang.capitalize()}:")
            for name in templates:
                lines.append(f"    • {name}")
        return "\n".join(lines)
