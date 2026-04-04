"""Python port of the `brief` command."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ARCHIVE_NAME = 'brief'
MODULE_COUNT = 1
SAMPLE_FILES = ('commands/brief.ts',)
PORTING_NOTE = 'Python port of the brief command'


def run(argv: list[str] | None = None) -> int:
    """Execute brief command."""
    if argv is None:
        argv = sys.argv[1:]
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '-5'] + argv,
            check=True,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
        )
        print(result.stdout, end='')
        return 0
    except subprocess.CalledProcessError as e:
        print(e.stdout, end='')
        print(e.stderr, end='', file=sys.stderr)
        return e.returncode


__all__ = ['ARCHIVE_NAME', 'MODULE_COUNT', 'PORTING_NOTE', 'SAMPLE_FILES', 'run']
