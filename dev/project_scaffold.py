"""
Project Scaffold - Create project folder structures and boilerplate files.
"""

import os
from datetime import datetime


PROJECT_TEMPLATES = {
    "python-cli": {
        "desc": "Python CLI application",
        "structure": {
            "src/__init__.py": "",
            "src/main.py": "#!/usr/bin/env python3\n\ndef main():\n    pass\n\nif __name__ == '__main__':\n    main()\n",
            "tests/__init__.py": "",
            "tests/test_main.py": "import pytest\n\ndef test_placeholder():\n    assert True\n",
            "README.md": "# {name}\n\n{desc}\n\n## Installation\n\n```bash\npip install -r requirements.txt\n```\n\n## Usage\n\n```bash\npython src/main.py\n```\n",
            "requirements.txt": "# Add your dependencies here\n",
            ".gitignore": "__pycache__/\n*.pyc\n*.pyo\n.env\nvenv/\n.venv/\n*.egg-info/\ndist/\nbuild/\n",
            ".env.example": "# Environment variables\n# Copy to .env and fill in values\nDEBUG=false\n",
            "Makefile": "test:\n\tpytest tests/ -v\n\nlint:\n\tflake8 src/\n\nrun:\n\tpython src/main.py\n",
        }
    },
    "python-api": {
        "desc": "Python Flask/FastAPI REST API",
        "structure": {
            "app/__init__.py": "from flask import Flask\n\ndef create_app():\n    app = Flask(__name__)\n    return app\n",
            "app/routes.py": "from flask import Blueprint, jsonify\n\nbp = Blueprint('api', __name__)\n\n@bp.route('/health')\ndef health():\n    return jsonify({'status': 'ok'})\n",
            "app/models.py": "# Define your data models here\n",
            "app/config.py": "import os\n\nclass Config:\n    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-change-this')\n    DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'\n",
            "tests/__init__.py": "",
            "tests/test_routes.py": "import pytest\n\ndef test_health(client):\n    response = client.get('/health')\n    assert response.status_code == 200\n",
            "main.py": "from app import create_app\n\napp = create_app()\n\nif __name__ == '__main__':\n    app.run(debug=False)\n",
            "requirements.txt": "flask>=2.0\npython-dotenv\nrequests\npytest\n",
            ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\n*.db\n",
            "README.md": "# {name} API\n\n## Setup\n\n```bash\npip install -r requirements.txt\ncp .env.example .env\npython main.py\n```\n",
            ".env.example": "SECRET_KEY=change-this-in-production\nDEBUG=false\n",
        }
    },
    "security-tool": {
        "desc": "Python security/pentest tool",
        "structure": {
            "src/__init__.py": "",
            "src/scanner.py": "\"\"\"Core scanner module.\"\"\"\n\nclass Scanner:\n    def scan(self, target: str) -> dict:\n        \"\"\"Scan a target and return findings.\"\"\"\n        raise NotImplementedError\n",
            "src/reporter.py": "\"\"\"Report generation.\"\"\"\n\ndef generate_report(findings: dict) -> str:\n    \"\"\"Generate a human-readable report.\"\"\"\n    return str(findings)\n",
            "src/utils.py": "\"\"\"Utility functions.\"\"\"\nimport re\n\ndef validate_ip(ip: str) -> bool:\n    pattern = r'^(?:\\d{1,3}\\.){3}\\d{1,3}$'\n    return bool(re.match(pattern, ip))\n",
            "tests/__init__.py": "",
            "tests/test_scanner.py": "import pytest\nfrom src.scanner import Scanner\n\ndef test_scanner_exists():\n    assert Scanner\n",
            "main.py": "#!/usr/bin/env python3\nimport argparse\nfrom src.scanner import Scanner\nfrom src.reporter import generate_report\n\ndef main():\n    parser = argparse.ArgumentParser()\n    parser.add_argument('target', help='Target to scan')\n    args = parser.parse_args()\n    scanner = Scanner()\n    findings = scanner.scan(args.target)\n    print(generate_report(findings))\n\nif __name__ == '__main__':\n    main()\n",
            "requirements.txt": "requests\nscapy\nrich\npytest\n",
            ".gitignore": "__pycache__/\n*.pyc\n.env\nvenv/\nlogs/\n*.log\n",
            "README.md": "# {name}\n\n⚠ **For authorized testing only.**\n\n## Usage\n\n```bash\npip install -r requirements.txt\npython main.py <target>\n```\n",
        }
    },
    "node-api": {
        "desc": "Node.js Express REST API",
        "structure": {
            "src/index.js": "const express = require('express');\nconst helmet = require('helmet');\n\nconst app = express();\napp.use(helmet());\napp.use(express.json());\n\napp.get('/health', (req, res) => res.json({ status: 'ok' }));\n\nconst PORT = process.env.PORT || 3000;\napp.listen(PORT, () => console.log(`Running on port ${PORT}`));\n",
            "src/routes/index.js": "const express = require('express');\nconst router = express.Router();\n\nrouter.get('/', (req, res) => res.json({ message: 'API v1' }));\n\nmodule.exports = router;\n",
            "tests/index.test.js": "const request = require('supertest');\nconst app = require('../src/index');\n\ndescribe('Health', () => {\n    test('GET /health returns ok', async () => {\n        const res = await request(app).get('/health');\n        expect(res.statusCode).toBe(200);\n    });\n});\n",
            "package.json": '{\n  "name": "{name}",\n  "version": "1.0.0",\n  "scripts": {\n    "start": "node src/index.js",\n    "test": "jest",\n    "dev": "nodemon src/index.js"\n  },\n  "dependencies": {\n    "express": "^4.18.0",\n    "helmet": "^7.0.0"\n  },\n  "devDependencies": {\n    "jest": "^29.0.0",\n    "supertest": "^6.0.0"\n  }\n}\n',
            ".gitignore": "node_modules/\n.env\n*.log\ndist/\n",
            "README.md": "# {name}\n\n## Setup\n\n```bash\nnpm install\nnpm start\n```\n",
            ".env.example": "PORT=3000\nNODE_ENV=development\n",
        }
    },
}


class ProjectScaffold:
    def create(self, name: str, project_type: str = "python-cli", output_dir: str = ".") -> str:
        """Create a project scaffold in the given output directory."""
        if not name or not name.strip():
            return "❌ Project name is required."

        ptype = project_type.lower()
        template = PROJECT_TEMPLATES.get(ptype)
        if not template:
            available = list(PROJECT_TEMPLATES.keys())
            return f"❌ Unknown project type '{ptype}'.\nAvailable: {', '.join(available)}"

        project_dir = os.path.join(os.path.abspath(output_dir), name)

        if os.path.exists(project_dir):
            return f"❌ Directory already exists: {project_dir}"

        created_files = []
        try:
            os.makedirs(project_dir)
            for file_path, content in template["structure"].items():
                full_path = os.path.join(project_dir, file_path)
                os.makedirs(os.path.dirname(full_path), exist_ok=True)
                filled = content.format(
                    name=name,
                    desc=template["desc"],
                    date=datetime.now().strftime("%Y-%m-%d"),
                )
                with open(full_path, "w") as f:
                    f.write(filled)
                created_files.append(file_path)
        except Exception as e:
            return f"❌ Error creating project: {e}"

        lines = [
            f"✅ Project '{name}' created at: {project_dir}",
            f"📁 Type: {template['desc']}",
            "",
            "📂 Files created:",
        ]
        for fp in created_files:
            lines.append(f"   {fp}")

        lines.append(f"\n🚀 Next steps:")
        lines.append(f"   cd {project_dir}")
        if "python" in ptype:
            lines.append(f"   pip install -r requirements.txt")
        elif "node" in ptype:
            lines.append(f"   npm install")

        return "\n".join(lines)

    def list_types(self) -> str:
        lines = ["📋 Available project types:\n"]
        for ptype, data in PROJECT_TEMPLATES.items():
            lines.append(f"  • {ptype}: {data['desc']}")
        return "\n".join(lines)
