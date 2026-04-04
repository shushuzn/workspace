"""Python port of ultrareviewEnabled subcommand."""

from __future__ import annotations

import sys


def run(argv: list[str] | None = None) -> int:
    """Check if ultra review is enabled."""
    if argv is None:
        argv = sys.argv[1:]
    print(f'ultrareviewEnabled: (stub)')
    return 0


__all__ = ['run']
