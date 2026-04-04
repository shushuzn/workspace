"""Python port of reviewRemote subcommand."""

from __future__ import annotations

import sys


def run(argv: list[str] | None = None) -> int:
    """Review a remote branch or PR."""
    if argv is None:
        argv = sys.argv[1:]
    print(f'reviewRemote: (stub — {len(argv)} args: {argv})')
    return 0


__all__ = ['run']
