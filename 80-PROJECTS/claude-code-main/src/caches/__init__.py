"""Python port of the `caches` command — clear caches subcommand."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ARCHIVE_NAME = 'caches'
MODULE_COUNT = 1
SAMPLE_FILES = ('commands/clear/caches.ts',)
PORTING_NOTE = 'Python port of the caches command'


def run(argv: list[str] | None = None) -> int:
    """Clear caches."""
    if argv is None:
        argv = sys.argv[1:]
    cache_dirs = [
        '.cache',
        '__pycache__',
        '.pytest_cache',
        '.mypy_cache',
        'node_modules/.cache',
    ]
    removed = 0
    for d in cache_dirs:
        p = Path(d)
        if p.exists():
            shutil.rmtree(p)
            removed += 1
            print(f'Removed: {d}')
    print(f'Done. Removed {removed} cache directories.')
    return 0


__all__ = ['ARCHIVE_NAME', 'MODULE_COUNT', 'PORTING_NOTE', 'SAMPLE_FILES', 'run']
