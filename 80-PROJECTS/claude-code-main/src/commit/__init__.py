"""Python port of the `commit` command — git commit workflow."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ARCHIVE_NAME = 'commit'
MODULE_COUNT = 1
SAMPLE_FILES = ('commands/commit.ts',)
PORTING_NOTE = 'Python port of the git commit command'


def run(argv: list[str] | None = None) -> int:
    """Execute git commit with optional message."""
    if argv is None:
        argv = sys.argv[1:]

    try:
        result = subprocess.run(
            ['git', 'commit'] + argv,
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
    except FileNotFoundError:
        print('Error: git is not installed or not in PATH', file=sys.stderr)
        return 127


__all__ = ['ARCHIVE_NAME', 'MODULE_COUNT', 'PORTING_NOTE', 'SAMPLE_FILES', 'run']
