#!/usr/bin/env python3
"""
Hybrid AI Agent - Main Entry Point
A local DevSecOps AI assistant for cybersecurity and software development.
"""

import argparse
import sys
from agent.brain import AgentBrain
from ui.cli import CLI


def parse_args():
    parser = argparse.ArgumentParser(
        description="Hybrid AI Agent - Local DevSecOps Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                        # Start interactive CLI
  python main.py --model codellama      # Use a specific model
  python main.py --analyze-log /var/log/auth.log
  python main.py --review-code myfile.py
        """
    )
    parser.add_argument("--model", default="llama3", help="Ollama model to use (default: llama3)")
    parser.add_argument("--analyze-log", metavar="FILE", help="Analyze a log file directly")
    parser.add_argument("--review-code", metavar="FILE", help="Review a code file directly")
    parser.add_argument("--no-memory", action="store_true", help="Disable persistent memory")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    return parser.parse_args()


def main():
    args = parse_args()

    brain = AgentBrain(model=args.model, use_memory=not args.no_memory, verbose=args.verbose)

    # Quick one-shot commands
    if args.analyze_log:
        result = brain.run_tool("log_analyzer", file_path=args.analyze_log)
        print(result)
        sys.exit(0)

    if args.review_code:
        with open(args.review_code, "r") as f:
            code = f.read()
        result = brain.run_tool("code_reviewer", code=code, filename=args.review_code)
        print(result)
        sys.exit(0)

    # Start interactive CLI
    cli = CLI(brain)
    cli.run()


if __name__ == "__main__":
    main()
