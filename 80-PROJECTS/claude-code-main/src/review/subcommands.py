"""Subcommands for the review command group."""

from __future__ import annotations

import sys

SUBCOMMANDS = {
    'ultrareviewCommand': 'Review with ultra settings',
    'ultrareviewEnabled': 'Check if ultra review is enabled',
    'reviewRemote': 'Review a remote branch/PR',
    'security-review': 'Run a security-focused review',
    'UltrareviewOverageDialog': 'Handle ultrareview overage dialog',
}


def run(argv: list[str] | None = None) -> int:
    """List or execute review subcommands."""
    if argv is None:
        argv = sys.argv[1:]

    if not argv or argv[0] == '--help':
        print('review subcommands:')
        for name, desc in SUBCOMMANDS.items():
            print(f'  {name}: {desc}')
        return 0

    sub = argv[0]
    print(f'review {sub}: (stub — pending port)')
    return 0


__all__ = ['SUBCOMMANDS', 'run']
