"""Python port of UltrareviewOverageDialog subcommand."""

from __future__ import annotations

import sys


def run(argv: list[str] | None = None) -> int:
    """Handle ultrareview overage dialog."""
    if argv is None:
        argv = sys.argv[1:]
    print(f'UltrareviewOverageDialog: (stub)')
    return 0


__all__ = ['run']
