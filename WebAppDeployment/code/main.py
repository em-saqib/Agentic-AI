#!/usr/bin/env python3
"""
WordPress Multi-Agent Deployment System
"""
import yaml
import sys
from orchestrator import Orchestrator


def load_config():
    """Load configuration from config.yaml"""
    with open('config.yaml', 'r') as f:
        return yaml.safe_load(f)


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 main.py deploy  - Deploy WordPress")
        print("  python3 main.py stop    - Stop WordPress")
        sys.exit(1)

    command = sys.argv[1]

    # Load configuration
    config = load_config()

    # Create orchestrator
    orchestrator = Orchestrator(config)

    # Execute command
    if command == 'deploy':
        result = orchestrator.deploy()
        sys.exit(0 if result['status'] == 'success' else 1)

    elif command == 'stop':
        orchestrator.stop()
        sys.exit(0)

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
