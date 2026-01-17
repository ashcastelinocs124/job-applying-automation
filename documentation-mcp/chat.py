#!/usr/bin/env python3
"""Entry point for the Documentation Chat CLI."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.cli import run_cli

if __name__ == "__main__":
    config_path = sys.argv[1] if len(sys.argv) > 1 else None
    run_cli(config_path)
