"""Python port of the `bridge-kick` command."""

from __future__ import annotations

import subprocess
import sys

ARCHIVE_NAME = 'bridge-kick'
MODULE_COUNT = 1
SAMPLE_FILES = ('commands/bridge-kick.ts',)
PORTING_NOTE = 'Python port of the bridge-kick command'


def run(argv: list[str] | None = None) -> int:
    """Execute bridge-kick."""
    if argv is None:
        argv = sys.argv[1:]
    try:
        result = subprocess.run(
            ['git', 'bridge-kick'] + argv,
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
        print('Error: bridge-kick command not found', file=sys.stderr)
        return 127


__all__ = ['ARCHIVE_NAME', 'MODULE_COUNT', 'PORTING_NOTE', 'SAMPLE_FILES', 'run']
