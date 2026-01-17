"""Entry point for running the Documentation MCP server."""
from __future__ import annotations

import argparse
from pathlib import Path

from .server import run_sync


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Documentation MCP server")
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to configuration YAML (defaults to config/config.yaml)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config_path = Path(args.config).as_posix() if args.config else None
    run_sync(config_path)


if __name__ == "__main__":
    main()
