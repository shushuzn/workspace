"""Python port of security-review subcommand."""

from __future__ import annotations

import sys


def run(argv: list[str] | None = None) -> int:
    """Run a security-focused review."""
    if argv is None:
        argv = sys.argv[1:]
    print(f'security-review: (stub)')
    return 0


__all__ = ['run']
