.PHONY: install run test lint clean setup help

help:  ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

setup:  ## Create venv and install dependencies
	python -m venv venv
	./venv/bin/pip install --upgrade pip
	./venv/bin/pip install -r requirements.txt
	@echo "✅ Setup complete. Run: source venv/bin/activate"

install:  ## Install dependencies
	pip install -r requirements.txt

run:  ## Start the interactive agent
	python main.py

run-code:  ## Start with codellama model
	python main.py --model codellama

test:  ## Run all tests
	pytest tests/ -v

test-cov:  ## Run tests with coverage report
	pytest tests/ -v --cov=. --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

lint:  ## Run flake8 linter
	flake8 . --max-line-length=120 --extend-ignore=E203,W503

format:  ## Format code with black
	black . --line-length=120

clean:  ## Remove cache and temp files
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache htmlcov .coverage 2>/dev/null || true
	@echo "✅ Cleaned"

analyze:  ## Analyze a log file (usage: make analyze LOG=/path/to/log)
	python main.py --analyze-log $(LOG)

review:  ## Review a code file (usage: make review FILE=myfile.py)
	python main.py --review-code $(FILE)
